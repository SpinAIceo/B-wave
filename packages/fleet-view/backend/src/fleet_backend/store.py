from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    BBox,
    DashboardOverview,
    DEFAULT_ZONE,
    DetectionRecord,
    Inspection,
    MoURegion,
    Severity,
    SubscriptionTier,
    SyncEvent,
    SyncStatus,
    Vessel,
    VesselStatus,
    VesselType,
    Zone,
)
from .orm import DetectionRow, InspectionRow, SyncEventRow, VesselRow


# ── ORM → Pydantic converters ─────────────────────────────────────────────────

def _to_vessel(r: VesselRow) -> Vessel:
    return Vessel(
        id=r.id, name=r.name, type=VesselType(r.type), flag=r.flag,
        management_company=r.management_company, edge_server_id=r.edge_server_id,
        last_psc_inspection=r.last_psc_inspection, detention_history=r.detention_history or [],
        subscription_tier=SubscriptionTier(r.subscription_tier),
        latitude=r.latitude, longitude=r.longitude, status=VesselStatus(r.status),
    )


def _to_inspection(r: InspectionRow) -> Inspection:
    return Inspection(
        id=r.id, vessel_id=r.vessel_id, inspector_id=r.inspector_id,
        port_of_inspection=r.port_of_inspection, mou_region=MoURegion(r.mou_region),
        started_at=r.started_at, completed_at=r.completed_at,
        total_items=r.total_items, passed=r.passed, failed=r.failed,
        critical_defects=r.critical_defects, synced=r.synced, synced_at=r.synced_at,
    )


def _to_detection(r: DetectionRow) -> DetectionRecord:
    bbox_data = r.bbox or {}
    try:
        zone = Zone(r.zone) if r.zone else DEFAULT_ZONE
    except ValueError:
        zone = DEFAULT_ZONE
    return DetectionRecord(
        id=r.id, inspection_id=r.inspection_id, defect_type=r.defect_type,
        confidence=r.confidence, psc_code=r.psc_code, severity=Severity(r.severity),
        bbox=BBox(**bbox_data),
        zone=zone,
        model_version=r.model_version, timestamp=r.timestamp,
    )


def _to_sync_event(r: SyncEventRow) -> SyncEvent:
    return SyncEvent(
        id=r.id, vessel_id=r.vessel_id, edge_server_id=r.edge_server_id,
        records_received=r.records_received, synced_at=r.synced_at,
        status=SyncStatus(r.status),
    )


# ── DataStore ─────────────────────────────────────────────────────────────────

class DataStore:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_vessels(self) -> list[Vessel]:
        rows = (await self.session.execute(select(VesselRow))).scalars().all()
        return [_to_vessel(r) for r in rows]

    async def get_vessel(self, vessel_id: str) -> Vessel | None:
        row = await self.session.get(VesselRow, vessel_id)
        return _to_vessel(row) if row else None

    async def get_inspections(self, vessel_id: str) -> list[Inspection]:
        rows = (await self.session.execute(
            select(InspectionRow).where(InspectionRow.vessel_id == vessel_id)
        )).scalars().all()
        return [_to_inspection(r) for r in rows]

    async def get_all_inspections(self) -> list[Inspection]:
        rows = (await self.session.execute(
            select(InspectionRow).order_by(InspectionRow.started_at.desc())
        )).scalars().all()
        return [_to_inspection(r) for r in rows]

    async def get_inspection(self, inspection_id: str) -> Inspection | None:
        row = await self.session.get(InspectionRow, inspection_id)
        return _to_inspection(row) if row else None

    async def get_detections(self, inspection_id: str) -> list[DetectionRecord]:
        rows = (await self.session.execute(
            select(DetectionRow).where(DetectionRow.inspection_id == inspection_id)
        )).scalars().all()
        return [_to_detection(r) for r in rows]

    async def get_all_detections(self) -> list[DetectionRecord]:
        rows = (await self.session.execute(select(DetectionRow))).scalars().all()
        return [_to_detection(r) for r in rows]

    async def get_zone_summary(self, vessel_id: str) -> dict[str, int]:
        """Aggregate detection counts grouped by zone for a vessel.

        Returns a dict with one entry per Zone enum value (zero-filled for
        zones with no detections).
        """
        # Inner subquery: inspection_ids of this vessel
        inspection_ids = select(InspectionRow.id).where(
            InspectionRow.vessel_id == vessel_id
        )
        rows = (await self.session.execute(
            select(DetectionRow.zone, func.count(DetectionRow.id))
            .where(DetectionRow.inspection_id.in_(inspection_ids))
            .group_by(DetectionRow.zone)
        )).all()
        summary: dict[str, int] = {z.value: 0 for z in Zone}
        for zone_value, count in rows:
            if zone_value in summary:
                summary[zone_value] = count
        return summary

    async def add_inspection(self, inspection: Inspection) -> None:
        row = await self.session.get(InspectionRow, inspection.id)
        if row:
            row.vessel_id = inspection.vessel_id
            row.inspector_id = inspection.inspector_id
            row.port_of_inspection = inspection.port_of_inspection
            row.mou_region = str(inspection.mou_region)
            row.started_at = inspection.started_at
            row.completed_at = inspection.completed_at
            row.total_items = inspection.total_items
            row.passed = inspection.passed
            row.failed = inspection.failed
            row.critical_defects = inspection.critical_defects
            row.synced = inspection.synced
            row.synced_at = inspection.synced_at
        else:
            self.session.add(InspectionRow(
                id=inspection.id, vessel_id=inspection.vessel_id,
                inspector_id=inspection.inspector_id,
                port_of_inspection=inspection.port_of_inspection,
                mou_region=str(inspection.mou_region),
                started_at=inspection.started_at, completed_at=inspection.completed_at,
                total_items=inspection.total_items, passed=inspection.passed,
                failed=inspection.failed, critical_defects=inspection.critical_defects,
                synced=inspection.synced, synced_at=inspection.synced_at,
            ))
        await self.session.commit()

    async def add_detection(self, detection: DetectionRecord) -> None:
        self.session.add(DetectionRow(
            id=detection.id, inspection_id=detection.inspection_id,
            defect_type=detection.defect_type, confidence=detection.confidence,
            psc_code=detection.psc_code, severity=str(detection.severity),
            bbox=detection.bbox.model_dump(),
            zone=str(detection.zone),
            model_version=detection.model_version, timestamp=detection.timestamp,
        ))
        await self.session.commit()

    async def add_sync_event(self, event: SyncEvent) -> None:
        self.session.add(SyncEventRow(
            id=event.id, vessel_id=event.vessel_id,
            edge_server_id=event.edge_server_id,
            records_received=event.records_received,
            synced_at=event.synced_at, status=str(event.status),
        ))
        await self.session.commit()

    async def get_sync_history(self, vessel_id: str) -> list[SyncEvent]:
        rows = (await self.session.execute(
            select(SyncEventRow).where(SyncEventRow.vessel_id == vessel_id)
        )).scalars().all()
        return [_to_sync_event(r) for r in rows]

    async def get_dashboard_overview(self) -> DashboardOverview:
        total_vessels = (await self.session.execute(
            select(func.count()).select_from(VesselRow)
        )).scalar() or 0

        active_inspections = (await self.session.execute(
            select(func.count()).select_from(InspectionRow)
            .where(InspectionRow.completed_at.is_(None))
        )).scalar() or 0

        critical_defects = (await self.session.execute(
            select(func.count()).select_from(DetectionRow)
            .where(DetectionRow.severity == "CRITICAL")
        )).scalar() or 0

        status_rows = (await self.session.execute(
            select(VesselRow.status, func.count()).group_by(VesselRow.status)
        )).all()
        vessels_by_status = {row[0]: row[1] for row in status_rows}

        defect_rows = (await self.session.execute(
            select(DetectionRow.defect_type, func.count()).group_by(DetectionRow.defect_type)
        )).all()
        defect_dist = {row[0]: row[1] for row in defect_rows}

        risk_row = (await self.session.execute(
            select(func.sum(InspectionRow.failed), func.sum(InspectionRow.total_items))
        )).one()
        total_failed = risk_row[0] or 0
        total_items_sum = risk_row[1] or 0
        risk = (total_failed / total_items_sum * 100) if total_items_sum > 0 else 0.0

        return DashboardOverview(
            total_vessels=total_vessels,
            active_inspections=active_inspections,
            critical_defects=critical_defects,
            detention_risk_score=round(risk, 1),
            vessels_by_status=vessels_by_status,
            defect_type_distribution=defect_dist,
        )


# ── Seed data (called once at startup if vessels table is empty) ───────────────

async def seed_initial_data(session: AsyncSession) -> None:
    count = (await session.execute(select(func.count()).select_from(VesselRow))).scalar()
    if count and count > 0:
        return  # already seeded

    now = datetime.now()

    vessels = [
        VesselRow(id="V-001", name="MV Pacific Star", type="BULK", flag="KR",
                  management_company="Korea Maritime Co.", edge_server_id="EDGE-001",
                  last_psc_inspection="2026-04-15", subscription_tier="ENTERPRISE",
                  latitude=35.1, longitude=129.0, status="PORT"),
        VesselRow(id="V-002", name="MV Atlantic Glory", type="CONTAINER", flag="NL",
                  management_company="EuroShip Management", edge_server_id="EDGE-002",
                  last_psc_inspection="2026-04-10", subscription_tier="ENTERPRISE",
                  latitude=51.9, longitude=4.5, status="SAILING"),
        VesselRow(id="V-003", name="MV Indian Voyager", type="TANKER", flag="SG",
                  management_company="Asia Pacific Shipping", edge_server_id="EDGE-003",
                  last_psc_inspection="2026-03-28", subscription_tier="STANDARD",
                  latitude=1.3, longitude=103.8, status="ANCHOR"),
        VesselRow(id="V-004", name="MV Arctic Pioneer", type="BULK", flag="CN",
                  management_company="China Ocean Shipping", edge_server_id="EDGE-004",
                  last_psc_inspection="2026-04-20", subscription_tier="STANDARD",
                  latitude=31.2, longitude=121.5, status="PORT"),
        VesselRow(id="V-005", name="MV Mediterranean Spirit", type="RORO", flag="GR",
                  management_company="Hellenic Carriers", edge_server_id="EDGE-005",
                  last_psc_inspection="2026-04-01", subscription_tier="BASIC",
                  latitude=37.9, longitude=23.7, status="SAILING"),
    ]
    session.add_all(vessels)

    inspections = [
        InspectionRow(id="INS-001", vessel_id="V-001", inspector_id="CREW-101",
                      port_of_inspection="Busan", mou_region="TOKYO",
                      started_at=now - timedelta(days=14),
                      completed_at=now - timedelta(days=14, hours=-2),
                      total_items=15, passed=12, failed=3, critical_defects=1,
                      synced=True, synced_at=now - timedelta(days=13)),
        InspectionRow(id="INS-002", vessel_id="V-001", inspector_id="CREW-101",
                      port_of_inspection="Busan", mou_region="TOKYO",
                      started_at=now - timedelta(days=2),
                      completed_at=now - timedelta(days=2, hours=-1),
                      total_items=15, passed=14, failed=1, critical_defects=0,
                      synced=True, synced_at=now - timedelta(days=1)),
        InspectionRow(id="INS-003", vessel_id="V-002", inspector_id="CREW-201",
                      port_of_inspection="Rotterdam", mou_region="PARIS",
                      started_at=now - timedelta(days=5),
                      completed_at=now - timedelta(days=5, hours=-3),
                      total_items=15, passed=10, failed=5, critical_defects=2,
                      synced=True, synced_at=now - timedelta(days=4)),
        InspectionRow(id="INS-004", vessel_id="V-003", inspector_id="CREW-301",
                      port_of_inspection="Singapore", mou_region="TOKYO",
                      started_at=now - timedelta(days=7),
                      completed_at=now - timedelta(days=7, hours=-2),
                      total_items=15, passed=13, failed=2, critical_defects=1,
                      synced=False),
        InspectionRow(id="INS-005", vessel_id="V-004", inspector_id="CREW-401",
                      port_of_inspection="Shanghai", mou_region="TOKYO",
                      started_at=now - timedelta(days=3),
                      total_items=15, passed=8, failed=4, critical_defects=2,
                      synced=True, synced_at=now - timedelta(days=2)),
        InspectionRow(id="INS-006", vessel_id="V-005", inspector_id="CREW-501",
                      port_of_inspection="Piraeus", mou_region="PARIS",
                      started_at=now - timedelta(days=10),
                      completed_at=now - timedelta(days=10, hours=-1),
                      total_items=15, passed=14, failed=1, critical_defects=0,
                      synced=True, synced_at=now - timedelta(days=9)),
    ]
    session.add_all(inspections)

    detections = [
        DetectionRow(id="DET-001", inspection_id="INS-001", defect_type="RUST",
                     confidence=0.87, psc_code="0615", severity="HIGH",
                     bbox={"x_min": 0.1, "y_min": 0.2, "x_max": 0.4, "y_max": 0.5},
                     zone="hull"),
        DetectionRow(id="DET-002", inspection_id="INS-001", defect_type="DAMAGE",
                     confidence=0.92, psc_code="0630", severity="CRITICAL",
                     bbox={"x_min": 0.5, "y_min": 0.1, "x_max": 0.8, "y_max": 0.35},
                     zone="bow"),
        DetectionRow(id="DET-003", inspection_id="INS-003", defect_type="CARGO_LASHING",
                     confidence=0.81, psc_code="0725", severity="HIGH",
                     bbox={"x_min": 0.3, "y_min": 0.6, "x_max": 0.6, "y_max": 0.85},
                     zone="deck"),
        DetectionRow(id="DET-004", inspection_id="INS-003", defect_type="LEAK",
                     confidence=0.75, psc_code="0950", severity="MEDIUM",
                     bbox={"x_min": 0.2, "y_min": 0.3, "x_max": 0.5, "y_max": 0.6},
                     zone="engine_room"),
        DetectionRow(id="DET-005", inspection_id="INS-004", defect_type="MISSING_LABEL",
                     confidence=0.68, psc_code="1320", severity="LOW",
                     bbox={"x_min": 0.6, "y_min": 0.7, "x_max": 0.9, "y_max": 0.95},
                     zone="deck"),
        DetectionRow(id="DET-006", inspection_id="INS-005", defect_type="CARGO_LASHING",
                     confidence=0.89, psc_code="0725", severity="CRITICAL",
                     bbox={"x_min": 0.1, "y_min": 0.4, "x_max": 0.45, "y_max": 0.7},
                     zone="deck"),
        DetectionRow(id="DET-007", inspection_id="INS-005", defect_type="RUST",
                     confidence=0.72, psc_code="0615", severity="MEDIUM",
                     bbox={"x_min": 0.5, "y_min": 0.2, "x_max": 0.7, "y_max": 0.4},
                     zone="stern"),
    ]
    session.add_all(detections)

    sync_events = [
        SyncEventRow(id="SYNC-001", vessel_id="V-001", edge_server_id="EDGE-001",
                     records_received=3, synced_at=now - timedelta(days=1)),
        SyncEventRow(id="SYNC-002", vessel_id="V-002", edge_server_id="EDGE-002",
                     records_received=5, synced_at=now - timedelta(days=4)),
        SyncEventRow(id="SYNC-003", vessel_id="V-004", edge_server_id="EDGE-004",
                     records_received=4, synced_at=now - timedelta(days=2)),
        SyncEventRow(id="SYNC-004", vessel_id="V-005", edge_server_id="EDGE-005",
                     records_received=1, synced_at=now - timedelta(days=9), status="PARTIAL"),
    ]
    session.add_all(sync_events)

    await session.commit()
