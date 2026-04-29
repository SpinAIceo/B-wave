from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class VesselType(StrEnum):
    BULK = "BULK"
    CONTAINER = "CONTAINER"
    TANKER = "TANKER"
    GENERAL = "GENERAL"
    RORO = "RORO"


class VesselStatus(StrEnum):
    SAILING = "SAILING"
    PORT = "PORT"
    ANCHOR = "ANCHOR"


class SubscriptionTier(StrEnum):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    ENTERPRISE = "ENTERPRISE"


class MoURegion(StrEnum):
    TOKYO = "TOKYO"
    PARIS = "PARIS"
    INDIAN_OCEAN = "INDIAN_OCEAN"
    USCG = "USCG"


class SyncStatus(StrEnum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class ReportFormat(StrEnum):
    PDF = "PDF"
    JSON = "JSON"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetentionRecord(BaseModel):
    date: str
    port: str
    defects: list[str] = []


class Vessel(BaseModel):
    id: str
    name: str
    type: VesselType
    flag: str
    management_company: str
    edge_server_id: str
    last_psc_inspection: str | None = None
    detention_history: list[DetentionRecord] = []
    subscription_tier: SubscriptionTier = SubscriptionTier.STANDARD
    latitude: float = 0.0
    longitude: float = 0.0
    status: VesselStatus = VesselStatus.SAILING


class Inspection(BaseModel):
    id: str
    vessel_id: str
    inspector_id: str
    port_of_inspection: str
    mou_region: MoURegion
    started_at: datetime
    completed_at: datetime | None = None
    total_items: int = 0
    passed: int = 0
    failed: int = 0
    critical_defects: int = 0
    synced: bool = False
    synced_at: datetime | None = None


class BBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class DetectionRecord(BaseModel):
    id: str
    inspection_id: str
    defect_type: str
    confidence: float
    psc_code: str
    severity: Severity
    bbox: BBox
    model_version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.now)


class SyncEvent(BaseModel):
    id: str
    vessel_id: str
    edge_server_id: str
    records_received: int = 0
    synced_at: datetime = Field(default_factory=datetime.now)
    status: SyncStatus = SyncStatus.SUCCESS


class AuditReport(BaseModel):
    id: str
    vessel_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    report_type: str
    format: ReportFormat = ReportFormat.PDF
    file_path: str | None = None
    status: str = "generated"


# --- Response models ---


class DashboardOverview(BaseModel):
    total_vessels: int
    active_inspections: int
    critical_defects: int
    detention_risk_score: float
    vessels_by_status: dict[str, int]
    defect_type_distribution: dict[str, int]


class SyncReceiveRequest(BaseModel):
    vessel_id: str
    edge_server_id: str
    inspection_id: str | None = None
    inspector_id: str | None = None
    port_of_inspection: str | None = None
    mou_region: str | None = None
    detections: list[dict] = []
    timestamp: str | None = None


class ReportGenerateRequest(BaseModel):
    vessel_id: str
    report_type: str = "psc_readiness"
    format: ReportFormat = ReportFormat.PDF


class WebhookConfigRequest(BaseModel):
    url: str
    events: list[str] = ["defect.critical"]


class WebhookTestRequest(BaseModel):
    webhook_id: str
