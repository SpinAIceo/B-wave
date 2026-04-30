from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    DashboardOverview,
    ReportGenerateRequest,
    SyncReceiveRequest,
    WebhookConfigRequest,
    WebhookTestRequest,
)
from .report_engine import ReportEngine
from .store import DataStore
from .sync_receiver import SyncReceiver
from .webhooks import WebhookManager

app = FastAPI(title="B-Wave Fleet View", version="0.1.0")

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

store = DataStore()
sync_receiver = SyncReceiver(store)
report_engine = ReportEngine(store)
webhook_manager = WebhookManager()

_API_KEY = os.environ.get("BWAVE_API_KEY", "")


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if _API_KEY and x_api_key != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/vessels")
async def list_vessels():
    return [v.model_dump() for v in store.get_vessels()]


@app.get("/api/v1/vessels/{vessel_id}")
async def get_vessel(vessel_id: str):
    vessel = store.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    return vessel.model_dump()


@app.get("/api/v1/vessels/{vessel_id}/inspections")
async def get_vessel_inspections(vessel_id: str):
    vessel = store.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    inspections = store.get_inspections(vessel_id)
    return [i.model_dump() for i in inspections]


@app.get("/api/v1/vessels/{vessel_id}/inspections/{inspection_id}/detections")
async def get_inspection_detections(vessel_id: str, inspection_id: str):
    inspection = store.get_inspection(inspection_id)
    if inspection is None or inspection.vessel_id != vessel_id:
        raise HTTPException(status_code=404, detail="Inspection not found")
    detections = store.get_detections(inspection_id)
    return [d.model_dump() for d in detections]


@app.get("/api/v1/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview():
    return store.get_dashboard_overview()


@app.post("/api/v1/sync/receive")
async def receive_sync(
    data: SyncReceiveRequest, _: None = Depends(verify_api_key)
):
    event = sync_receiver.receive_inspection(data)
    webhook_manager.trigger("sync.received", {
        "vessel_id": data.vessel_id,
        "records": event.records_received,
    })
    return event.model_dump()


@app.post("/api/v1/reports/generate")
async def generate_report(
    request: ReportGenerateRequest, _: None = Depends(verify_api_key)
):
    try:
        report = report_engine.generate_audit_report(
            request.vessel_id, request.report_type, request.format,
        )
        return report.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/v1/reports/{report_id}")
async def get_report(report_id: str):
    report = report_engine.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()


@app.post("/api/v1/webhooks/configure")
async def configure_webhook(
    request: WebhookConfigRequest, _: None = Depends(verify_api_key)
):
    try:
        webhook_id = webhook_manager.configure(request.url, request.events)
        return {"webhook_id": webhook_id, "status": "configured"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/v1/webhooks/test")
async def test_webhook(
    request: WebhookTestRequest, _: None = Depends(verify_api_key)
):
    success = webhook_manager.test(request.webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "delivered", "webhook_id": request.webhook_id}
