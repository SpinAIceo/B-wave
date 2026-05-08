from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import RequireAdmin, RequireOperator, RequireViewer, Token, login_for_access_token
from .database import AsyncSessionLocal, get_db, init_db
from .models import (
    DashboardOverview,
    ReportGenerateRequest,
    SyncReceiveRequest,
    WebhookConfigRequest,
    WebhookTestRequest,
)
from .report_engine import ReportEngine
from .store import DataStore, seed_initial_data
from .sync_receiver import SyncReceiver
from .webhooks import WebhookManager

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)
    yield


app = FastAPI(title="B-Wave Fleet View", version="0.1.0", lifespan=lifespan)

_cors_origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials="*" not in _cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory singleton (no DB)
_webhook_manager = WebhookManager()
_report_engine = ReportEngine()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/auth/token", response_model=Token, tags=["auth"])
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/vessels")
async def list_vessels(
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    store = DataStore(db)
    return [v.model_dump() for v in await store.get_vessels()]


@app.get("/api/v1/vessels/{vessel_id}")
async def get_vessel(
    vessel_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    store = DataStore(db)
    vessel = await store.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    return vessel.model_dump()


@app.get("/api/v1/vessels/{vessel_id}/inspections")
async def get_vessel_inspections(
    vessel_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    store = DataStore(db)
    vessel = await store.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    return [i.model_dump() for i in await store.get_inspections(vessel_id)]


@app.get("/api/v1/vessels/{vessel_id}/inspections/{inspection_id}/detections")
async def get_inspection_detections(
    vessel_id: str,
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    store = DataStore(db)
    inspection = await store.get_inspection(inspection_id)
    if inspection is None or inspection.vessel_id != vessel_id:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return [d.model_dump() for d in await store.get_detections(inspection_id)]


@app.get("/api/v1/vessels/{vessel_id}/zone-summary")
async def get_vessel_zone_summary(
    vessel_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    """Returns detection counts per zone for a vessel.

    Response shape: {"bow": int, "midship": int, "stern": int,
                     "deck": int, "hull": int, "engine_room": int}
    """
    store = DataStore(db)
    vessel = await store.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    return await store.get_zone_summary(vessel_id)


@app.get("/api/v1/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview(
    db: AsyncSession = Depends(get_db),
    _: None = RequireViewer,
):
    store = DataStore(db)
    return await store.get_dashboard_overview()


@app.post("/api/v1/sync/receive")
async def receive_sync(
    data: SyncReceiveRequest,
    db: AsyncSession = Depends(get_db),
    _: None = RequireOperator,
):
    store = DataStore(db)
    receiver = SyncReceiver(store)
    event = await receiver.receive_inspection(data)
    _webhook_manager.trigger("sync.received", {
        "vessel_id": data.vessel_id,
        "records": event.records_received,
    })
    return event.model_dump()


@app.post("/api/v1/reports/generate")
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = RequireOperator,
):
    store = DataStore(db)
    try:
        report = await _report_engine.generate_audit_report(
            store, request.vessel_id, request.report_type, request.format,
        )
        return report.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/v1/reports/{report_id}")
async def get_report(
    report_id: str,
    _: None = RequireViewer,
):
    report = _report_engine.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()


@app.post("/api/v1/webhooks/configure")
async def configure_webhook(
    request: WebhookConfigRequest,
    _: None = RequireAdmin,
):
    try:
        webhook_id = _webhook_manager.configure(request.url, request.events)
        return {"webhook_id": webhook_id, "status": "configured"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/v1/webhooks/test")
async def test_webhook(
    request: WebhookTestRequest,
    _: None = RequireAdmin,
):
    success = _webhook_manager.test(request.webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "delivered", "webhook_id": request.webhook_id}
