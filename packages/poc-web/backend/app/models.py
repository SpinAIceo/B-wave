from __future__ import annotations

from typing import Any
from pydantic import BaseModel, field_validator


class BBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    class_name: str
    confidence: float
    psc_code: str
    psc_description: str
    severity: str


class DetectResponse(BaseModel):
    detections: list[BBox]
    image_width: int
    image_height: int
    inference_ms: float
    model_version: str = "YOLO26s-v1"


class RiskRequest(BaseModel):
    port_code: str
    defects: list[str] = []
    vessel_age_years: int = 10

    @field_validator("port_code")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.upper()


class RiskFactor(BaseModel):
    label: str
    contribution: float


class RiskResponse(BaseModel):
    port_code: str
    port_name: str
    mou_region: str
    base_detention_rate: float
    adjusted_detention_rate: float
    risk_level: str
    risk_factors: list[RiskFactor]
    historical_average_days: float
    recommendation: str


class RoiRequest(BaseModel):
    defects: list[str]
    port_code: str
    vessel_type: str = "bulk_carrier"
    vessel_dwt: int = 50000


class RoiResponse(BaseModel):
    expected_detention_days: float
    detention_cost_usd: float
    cargo_delay_cost_usd: float
    reputational_cost_usd: float
    total_risk_usd: float
    bwave_annual_cost_usd: float
    roi_ratio: float
    payback_months: float
    breakdown: dict[str, Any]


class Vessel(BaseModel):
    id: str
    name: str
    flag: str
    type: str
    imo: str
    lat: float
    lon: float
    status: str
    risk_level: str
    defects: list[str]
    last_inspection: str
    next_port: str


class FleetResponse(BaseModel):
    vessels: list[Vessel]
    summary: dict[str, int]


class LeadRequest(BaseModel):
    email: str
    company: str = ""
    fleet_size: int = 0
