from __future__ import annotations

import os
import time
import uuid

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import defect_stats, get_detections, get_scans, init_db, save_scan, vessel_stats
from app.detect import run_inference
from app.fleet import generate_fleet
from app.logger import get_logger
from app.models import FleetResponse, LeadRequest, RiskRequest, RiskResponse, RoiRequest, RoiResponse
from app.risk import calculate_risk
from app.roi import calculate_roi

log = get_logger("bwave.api")

app = FastAPI(title="B-Wave Virtual PoC API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8].upper()
    t0 = time.perf_counter()
    log.info(f"→ {req_id} {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        ms = (time.perf_counter() - t0) * 1000
        log.info(f"← {req_id} {response.status_code} [{ms:.1f}ms]")
        return response
    except Exception as exc:
        ms = (time.perf_counter() - t0) * 1000
        log.error(f"← {req_id} UNHANDLED [{ms:.1f}ms] {exc!r}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

_VESSEL_IDS = ["V001", "V002", "V003", "V004", "V005"]

_MOCK_VESSELS = [
    {"id": "V001", "name": "MV Pacific Star",   "type": "Bulk Carrier", "flag": "KR", "managementCompany": "Spinai Maritime", "lat": 35.1,  "lng": 129.0,  "status": "sailing",     "lastInspection": "2026-04-25", "criticalDefects": 0, "detentionRisk": 35},
    {"id": "V002", "name": "MV Ocean Harmony",  "type": "Container",    "flag": "PA", "managementCompany": "Spinai Maritime", "lat": 1.26,  "lng": 103.8,  "status": "port",        "lastInspection": "2026-04-20", "criticalDefects": 0, "detentionRisk": 12},
    {"id": "V003", "name": "MV Blue Horizon",   "type": "Tanker",       "flag": "LR", "managementCompany": "Spinai Maritime", "lat": 51.9,  "lng": 4.5,    "status": "anchor",      "lastInspection": "2026-04-15", "criticalDefects": 0, "detentionRisk": 78},
    {"id": "V004", "name": "MV Northern Wind",  "type": "Bulk Carrier", "flag": "MH", "managementCompany": "Spinai Maritime", "lat": 31.2,  "lng": 121.5,  "status": "sailing",     "lastInspection": "2026-04-22", "criticalDefects": 0, "detentionRisk": 8},
    {"id": "V005", "name": "MV Coral Venture",  "type": "Container",    "flag": "SG", "managementCompany": "Spinai Maritime", "lat": 22.3,  "lng": 114.2,  "status": "maintenance", "lastInspection": "2026-04-10", "criticalDefects": 0, "detentionRisk": 62},
]


@app.on_event("startup")
def startup():
    log.info("Starting B-Wave PoC API …")
    init_db()
    log.info("DB ready. Server online.")


@app.get("/health")
def health() -> dict:
    log.debug("health check")
    return {"status": "ok", "service": "bwave-poc-api"}


# ── Core endpoints ────────────────────────────────────────────────────────────

@app.post("/api/detect")
async def detect(file: UploadFile = File(...), vessel_id: str = "V001"):
    if not file.content_type or not file.content_type.startswith("image/"):
        log.warning(f"Rejected non-image upload: content_type={file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")
    contents = await file.read()
    size_kb = len(contents) / 1024
    if len(contents) > 20 * 1024 * 1024:
        log.warning(f"Rejected oversized file: {size_kb:.0f}KB vessel={vessel_id}")
        raise HTTPException(status_code=413, detail="Image too large (max 20MB)")
    log.info(f"detect start vessel={vessel_id} file={file.filename} size={size_kb:.0f}KB")
    try:
        result = run_inference(contents)
        scan_id = save_scan(vessel_id, file.filename or "upload.jpg", result)
        log.info(
            f"detect done vessel={vessel_id} scan={scan_id} "
            f"defects={len(result.detections)} model={result.model_version} "
            f"inference={result.inference_ms}ms"
        )
        return result
    except Exception as exc:
        log.error(f"detect failed vessel={vessel_id}: {exc!r}")
        raise HTTPException(status_code=500, detail="Inference failed") from exc


@app.post("/api/risk", response_model=RiskResponse)
def risk(req: RiskRequest):
    log.info(f"risk port={req.port_code} defects={req.defects} age={req.vessel_age_years}yr")
    try:
        result = calculate_risk(req.port_code, req.defects, req.vessel_age_years)
        log.info(f"risk result level={result.risk_level} rate={result.adjusted_detention_rate}%")
        return result
    except Exception as exc:
        log.error(f"risk calc failed: {exc!r}")
        raise HTTPException(status_code=500, detail="Risk calculation failed") from exc


@app.post("/api/roi", response_model=RoiResponse)
def roi(req: RoiRequest):
    log.info(f"roi port={req.port_code} type={req.vessel_type} dwt={req.vessel_dwt}")
    try:
        result = calculate_roi(req.defects, req.port_code, req.vessel_type, req.vessel_dwt)
        log.info(f"roi result cost={result.total_cost_usd:,.0f} USD")
        return result
    except Exception as exc:
        log.error(f"roi calc failed: {exc!r}")
        raise HTTPException(status_code=500, detail="ROI calculation failed") from exc


@app.get("/api/fleet", response_model=FleetResponse)
def fleet():
    log.info("fleet data requested")
    try:
        result = generate_fleet()
        log.info(f"fleet generated vessels={len(result.vessels)}")
        return result
    except Exception as exc:
        log.error(f"fleet generation failed: {exc!r}")
        raise HTTPException(status_code=500, detail="Fleet generation failed") from exc


@app.get("/api/ports")
def ports():
    from app.risk import PORT_DB
    log.debug(f"ports list requested count={len(PORT_DB)}")
    return [{"code": k, "name": v[0], "region": v[1]} for k, v in sorted(PORT_DB.items(), key=lambda x: x[1][0])]


@app.post("/api/leads")
def leads(req: LeadRequest):
    log.info(f"LEAD email={req.email} company={req.company} fleet_size={req.fleet_size}")
    return {"status": "received", "message": "Thank you! Our team will contact you shortly."}


# ── /api/v1/ endpoints for fleet-view ────────────────────────────────────────

@app.get("/api/v1/vessels")
def v1_vessels():
    log.debug("v1 vessels list")
    vstats = vessel_stats()
    vessels = []
    for v in _MOCK_VESSELS:
        s = vstats.get(v["id"], {})
        entry = dict(v)
        entry["criticalDefects"] = s.get("critical_defects") or 0
        if s.get("last_inspection"):
            entry["lastInspection"] = s["last_inspection"][:10]
        vessels.append(entry)
    log.debug(f"v1 vessels returned count={len(vessels)}")
    return vessels


@app.get("/api/v1/vessels/{vessel_id}")
def v1_vessel(vessel_id: str):
    log.debug(f"v1 vessel detail id={vessel_id}")
    vstats = vessel_stats()
    for v in _MOCK_VESSELS:
        if v["id"] == vessel_id:
            s = vstats.get(vessel_id, {})
            entry = dict(v)
            entry["criticalDefects"] = s.get("critical_defects") or 0
            if s.get("last_inspection"):
                entry["lastInspection"] = s["last_inspection"][:10]
            return entry
    log.warning(f"v1 vessel not found id={vessel_id}")
    raise HTTPException(status_code=404, detail="Vessel not found")


@app.get("/api/v1/dashboard/overview")
def v1_overview():
    log.debug("v1 dashboard overview")
    scans = get_scans()
    dstats = defect_stats()
    vstats = vessel_stats()
    critical = sum((s.get("critical_defects") or 0) for s in vstats.values())
    total_risk = sum(v["detentionRisk"] for v in _MOCK_VESSELS) // len(_MOCK_VESSELS)
    log.info(f"overview scans={len(scans)} critical={critical} risk={total_risk}%")
    return {
        "totalVessels": len(_MOCK_VESSELS),
        "activeInspections": len(scans),
        "criticalDefects": int(critical),
        "detentionRiskScore": total_risk,
        "vesselsByStatus": {"sailing": 2, "port": 1, "anchor": 1, "maintenance": 1},
        "defectDistribution": {
            "rust":          dstats.get("rust", 0),
            "damage":        dstats.get("damage", 0),
            "leak":          dstats.get("leak", 0),
            "missing_label": dstats.get("missing_label", 0),
            "cargo_lashing": dstats.get("cargo_lashing", 0),
        },
    }


@app.get("/api/v1/vessels/{vessel_id}/inspections")
def v1_vessel_inspections(vessel_id: str):
    target = vessel_id if vessel_id != "all" else None
    log.debug(f"v1 inspections vessel={vessel_id}")
    rows = _scans_as_inspections(target)
    log.debug(f"v1 inspections returned count={len(rows)}")
    return rows


@app.get("/api/v1/inspections/{scan_id}/detections")
def v1_detections(scan_id: str):
    log.debug(f"v1 detections scan={scan_id}")
    rows = get_detections(scan_id)
    log.debug(f"v1 detections returned count={len(rows)}")
    return [
        {
            "id": r["id"],
            "defectType": r["class_name"],
            "confidence": r["confidence"],
            "pscCode": r["psc_code"],
            "severity": r["severity"].lower(),
            "bbox": {
                "xMin": r["x_min"], "yMin": r["y_min"],
                "xMax": r["x_max"], "yMax": r["y_max"],
            },
        }
        for r in rows
    ]


def _scans_as_inspections(vessel_id: str | None):
    vessel_map = {v["id"]: v["name"] for v in _MOCK_VESSELS}
    results = []
    for s in get_scans(vessel_id):
        dets = get_detections(s["id"])
        failed = len(dets)
        critical = sum(1 for d in dets if d["severity"] in ("HIGH", "CRITICAL"))
        results.append({
            "id": s["id"],
            "vesselId": s["vessel_id"],
            "vesselName": vessel_map.get(s["vessel_id"], s["vessel_id"]),
            "port": "On Board",
            "mouRegion": "Tokyo",
            "startedAt": s["scanned_at"],
            "completedAt": s["scanned_at"],
            "totalItems": max(failed, 1),
            "passed": max(0, 1 - failed) if failed == 0 else 0,
            "failed": failed,
            "criticalDefects": critical,
        })
    return results
