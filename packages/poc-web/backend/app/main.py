from __future__ import annotations

import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.detect import run_inference
from app.fleet import generate_fleet
from app.models import FleetResponse, LeadRequest, RiskRequest, RiskResponse, RoiRequest, RoiResponse
from app.risk import calculate_risk
from app.roi import calculate_roi

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://*.vercel.app",
).split(",")

app = FastAPI(title="B-Wave Virtual PoC API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production with ALLOWED_ORIGINS
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "bwave-poc-api"}


@app.post("/api/detect")
async def detect(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 20MB)")
    return run_inference(contents)


@app.post("/api/risk", response_model=RiskResponse)
def risk(req: RiskRequest):
    return calculate_risk(req.port_code, req.defects, req.vessel_age_years)


@app.post("/api/roi", response_model=RoiResponse)
def roi(req: RoiRequest):
    return calculate_roi(req.defects, req.port_code, req.vessel_type, req.vessel_dwt)


@app.get("/api/fleet", response_model=FleetResponse)
def fleet():
    return generate_fleet()


@app.get("/api/ports")
def ports():
    from app.risk import PORT_DB
    return [{"code": k, "name": v[0], "region": v[1]} for k, v in sorted(PORT_DB.items(), key=lambda x: x[1][0])]


@app.post("/api/leads")
def leads(req: LeadRequest):
    # In production: save to DB or send to CRM
    print(f"[LEAD] {req.email} | {req.company} | fleet={req.fleet_size}")
    return {"status": "received", "message": "Thank you! Our team will contact you shortly."}
