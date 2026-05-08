from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class VesselRow(Base):
    __tablename__ = "vessels"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    flag: Mapped[str] = mapped_column(String, nullable=False)
    management_company: Mapped[str] = mapped_column(String, nullable=False)
    edge_server_id: Mapped[str] = mapped_column(String, nullable=False)
    last_psc_inspection: Mapped[str | None] = mapped_column(String, nullable=True)
    detention_history: Mapped[list] = mapped_column(JSON, default=list)
    subscription_tier: Mapped[str] = mapped_column(String, default="STANDARD")
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    longitude: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String, default="SAILING")


class InspectionRow(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    vessel_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    inspector_id: Mapped[str] = mapped_column(String, nullable=False)
    port_of_inspection: Mapped[str] = mapped_column(String, nullable=False)
    mou_region: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    critical_defects: Mapped[int] = mapped_column(Integer, default=0)
    synced: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DetectionRow(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    inspection_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    defect_type: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    psc_code: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    bbox: Mapped[dict] = mapped_column(JSON, nullable=False)
    zone: Mapped[str] = mapped_column(String, nullable=False, server_default="midship", index=True)
    model_version: Mapped[str] = mapped_column(String, default="0.1.0")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class SyncEventRow(Base):
    __tablename__ = "sync_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    vessel_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    edge_server_id: Mapped[str] = mapped_column(String, nullable=False)
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String, default="SUCCESS")
