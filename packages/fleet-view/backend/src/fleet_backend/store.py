from __future__ import annotations

from datetime import datetime, timedelta

from .models import (
    BBox,
    DashboardOverview,
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
)


class DataStore:
    def __init__(self) -> None:
        self.vessels: dict[str, Vessel] = {}
        self.inspections: dict[str, Inspection] = {}
        self.detections: dict[str, DetectionRecord] = {}
        self.sync_events: list[SyncEvent] = []
        self._seed()

    def _seed(self) -> None:
        now = datetime.now()

        vessels_data = [
            Vessel(
                id="V-001", name="MV Pacific Star", type=VesselType.BULK,
                flag="KR", management_company="Korea Maritime Co.",
                edge_server_id="EDGE-001", last_psc_inspection="2026-04-15",
                subscription_tier=SubscriptionTier.ENTERPRISE,
                latitude=35.1, longitude=129.0, status=VesselStatus.PORT,
            ),
            Vessel(
                id="V-002", name="MV Atlantic Glory", type=VesselType.CONTAINER,
                flag="NL", management_company="EuroShip Management",
                edge_server_id="EDGE-002", last_psc_inspection="2026-04-10",
                subscription_tier=SubscriptionTier.ENTERPRISE,
                latitude=51.9, longitude=4.5, status=VesselStatus.SAILING,
            ),
            Vessel(
                id="V-003", name="MV Indian Voyager", type=VesselType.TANKER,
                flag="SG", management_company="Asia Pacific Shipping",
                edge_server_id="EDGE-003", last_psc_inspection="2026-03-28",
                subscription_tier=SubscriptionTier.STANDARD,
                latitude=1.3, longitude=103.8, status=VesselStatus.ANCHOR,
            ),
            Vessel(
                id="V-004", name="MV Arctic Pioneer", type=VesselType.BULK,
                flag="CN", management_company="China Ocean Shipping",
                edge_server_id="EDGE-004", last_psc_inspection="2026-04-20",
                subscription_tier=SubscriptionTier.STANDARD,
                latitude=31.2, longitude=121.5, status=VesselStatus.PORT,
            ),
            Vessel(
                id="V-005", name="MV Mediterranean Spirit", type=VesselType.RORO,
                flag="GR", management_company="Hellenic Carriers",
                edge_server_id="EDGE-005", last_psc_inspection="2026-04-01",
                subscription_tier=SubscriptionTier.BASIC,
                latitude=37.9, longitude=23.7, status=VesselStatus.SAILING,
            ),
        ]
        for v in vessels_data:
            self.vessels[v.id] = v

        inspections_data = [
            Inspection(
                id="INS-001", vessel_id="V-001", inspector_id="CREW-101",
                port_of_inspection="Busan", mou_region=MoURegion.TOKYO,
                started_at=now - timedelta(days=14),
                completed_at=now - timedelta(days=14, hours=-2),
                total_items=15, passed=12, failed=3, critical_defects=1, synced=True,
                synced_at=now - timedelta(days=13),
            ),
            Inspection(
                id="INS-002", vessel_id="V-001", inspector_id="CREW-101",
                port_of_inspection="Busan", mou_region=MoURegion.TOKYO,
                started_at=now - timedelta(days=2), completed_at=now - timedelta(days=2, hours=-1),
                total_items=15, passed=14, failed=1, critical_defects=0, synced=True,
                synced_at=now - timedelta(days=1),
            ),
            Inspection(
                id="INS-003", vessel_id="V-002", inspector_id="CREW-201",
                port_of_inspection="Rotterdam", mou_region=MoURegion.PARIS,
                started_at=now - timedelta(days=5), completed_at=now - timedelta(days=5, hours=-3),
                total_items=15, passed=10, failed=5, critical_defects=2, synced=True,
                synced_at=now - timedelta(days=4),
            ),
            Inspection(
                id="INS-004", vessel_id="V-003", inspector_id="CREW-301",
                port_of_inspection="Singapore", mou_region=MoURegion.TOKYO,
                started_at=now - timedelta(days=7), completed_at=now - timedelta(days=7, hours=-2),
                total_items=15, passed=13, failed=2, critical_defects=1, synced=False,
            ),
            Inspection(
                id="INS-005", vessel_id="V-004", inspector_id="CREW-401",
                port_of_inspection="Shanghai", mou_region=MoURegion.TOKYO,
                started_at=now - timedelta(days=3),
                total_items=15, passed=8, failed=4, critical_defects=2, synced=True,
                synced_at=now - timedelta(days=2),
            ),
            Inspection(
                id="INS-006", vessel_id="V-005", inspector_id="CREW-501",
                port_of_inspection="Piraeus", mou_region=MoURegion.PARIS,
                started_at=now - timedelta(days=10),
                completed_at=now - timedelta(days=10, hours=-1),
                total_items=15, passed=14, failed=1, critical_defects=0, synced=True,
                synced_at=now - timedelta(days=9),
            ),
        ]
        for ins in inspections_data:
            self.inspections[ins.id] = ins

        detections_data = [
            DetectionRecord(
                id="DET-001", inspection_id="INS-001", defect_type="RUST",
                confidence=0.87, psc_code="0615", severity=Severity.HIGH,
                bbox=BBox(x_min=0.1, y_min=0.2, x_max=0.4, y_max=0.5),
            ),
            DetectionRecord(
                id="DET-002", inspection_id="INS-001", defect_type="DAMAGE",
                confidence=0.92, psc_code="0630", severity=Severity.CRITICAL,
                bbox=BBox(x_min=0.5, y_min=0.1, x_max=0.8, y_max=0.35),
            ),
            DetectionRecord(
                id="DET-003", inspection_id="INS-003", defect_type="CARGO_LASHING",
                confidence=0.81, psc_code="0725", severity=Severity.HIGH,
                bbox=BBox(x_min=0.3, y_min=0.6, x_max=0.6, y_max=0.85),
            ),
            DetectionRecord(
                id="DET-004", inspection_id="INS-003", defect_type="LEAK",
                confidence=0.75, psc_code="0950", severity=Severity.MEDIUM,
                bbox=BBox(x_min=0.2, y_min=0.3, x_max=0.5, y_max=0.6),
            ),
            DetectionRecord(
                id="DET-005", inspection_id="INS-004", defect_type="MISSING_LABEL",
                confidence=0.68, psc_code="1320", severity=Severity.LOW,
                bbox=BBox(x_min=0.6, y_min=0.7, x_max=0.9, y_max=0.95),
            ),
            DetectionRecord(
                id="DET-006", inspection_id="INS-005", defect_type="CARGO_LASHING",
                confidence=0.89, psc_code="0725", severity=Severity.CRITICAL,
                bbox=BBox(x_min=0.1, y_min=0.4, x_max=0.45, y_max=0.7),
            ),
            DetectionRecord(
                id="DET-007", inspection_id="INS-005", defect_type="RUST",
                confidence=0.72, psc_code="0615", severity=Severity.MEDIUM,
                bbox=BBox(x_min=0.5, y_min=0.2, x_max=0.7, y_max=0.4),
            ),
        ]
        for det in detections_data:
            self.detections[det.id] = det

        self.sync_events = [
            SyncEvent(
                id="SYNC-001", vessel_id="V-001", edge_server_id="EDGE-001",
                records_received=3, synced_at=now - timedelta(days=1),
            ),
            SyncEvent(
                id="SYNC-002", vessel_id="V-002", edge_server_id="EDGE-002",
                records_received=5, synced_at=now - timedelta(days=4),
            ),
            SyncEvent(
                id="SYNC-003", vessel_id="V-004", edge_server_id="EDGE-004",
                records_received=4, synced_at=now - timedelta(days=2),
            ),
            SyncEvent(
                id="SYNC-004", vessel_id="V-005", edge_server_id="EDGE-005",
                records_received=1, synced_at=now - timedelta(days=9),
                status=SyncStatus.PARTIAL,
            ),
        ]

    def get_vessels(self) -> list[Vessel]:
        return list(self.vessels.values())

    def get_vessel(self, vessel_id: str) -> Vessel | None:
        return self.vessels.get(vessel_id)

    def get_inspections(self, vessel_id: str) -> list[Inspection]:
        return [i for i in self.inspections.values() if i.vessel_id == vessel_id]

    def get_inspection(self, inspection_id: str) -> Inspection | None:
        return self.inspections.get(inspection_id)

    def get_detections(self, inspection_id: str) -> list[DetectionRecord]:
        return [d for d in self.detections.values() if d.inspection_id == inspection_id]

    def get_all_detections(self) -> list[DetectionRecord]:
        return list(self.detections.values())

    def add_inspection(self, inspection: Inspection) -> None:
        self.inspections[inspection.id] = inspection

    def add_detection(self, detection: DetectionRecord) -> None:
        self.detections[detection.id] = detection

    def add_sync_event(self, event: SyncEvent) -> None:
        self.sync_events.append(event)

    def get_sync_history(self, vessel_id: str) -> list[SyncEvent]:
        return [e for e in self.sync_events if e.vessel_id == vessel_id]

    def get_dashboard_overview(self) -> DashboardOverview:
        all_inspections = list(self.inspections.values())
        all_detections = list(self.detections.values())

        active = [i for i in all_inspections if i.completed_at is None]
        critical = sum(1 for d in all_detections if d.severity == Severity.CRITICAL)

        status_counts: dict[str, int] = {}
        for v in self.vessels.values():
            status_counts[v.status.value] = status_counts.get(v.status.value, 0) + 1

        defect_dist: dict[str, int] = {}
        for d in all_detections:
            defect_dist[d.defect_type] = defect_dist.get(d.defect_type, 0) + 1

        total_failed = sum(i.failed for i in all_inspections)
        total_items = sum(i.total_items for i in all_inspections)
        risk = (total_failed / total_items * 100) if total_items > 0 else 0.0

        return DashboardOverview(
            total_vessels=len(self.vessels),
            active_inspections=len(active),
            critical_defects=critical,
            detention_risk_score=round(risk, 1),
            vessels_by_status=status_counts,
            defect_type_distribution=defect_dist,
        )
