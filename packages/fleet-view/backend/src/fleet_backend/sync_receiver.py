from __future__ import annotations

import uuid
from datetime import datetime

from .models import (
    BBox,
    DetectionRecord,
    Inspection,
    MoURegion,
    Severity,
    SyncEvent,
    SyncReceiveRequest,
    SyncStatus,
)
from .store import DataStore

REQUIRED_FIELDS = {"vessel_id", "edge_server_id"}


class SyncReceiver:
    def __init__(self, store: DataStore) -> None:
        self.store = store

    def validate_sync_data(self, data: SyncReceiveRequest) -> bool:
        return bool(data.vessel_id and data.edge_server_id)

    def receive_inspection(self, data: SyncReceiveRequest) -> SyncEvent:
        if not self.validate_sync_data(data):
            return SyncEvent(
                id=f"SYNC-{uuid.uuid4().hex[:8]}",
                vessel_id=data.vessel_id or "unknown",
                edge_server_id=data.edge_server_id or "unknown",
                records_received=0,
                status=SyncStatus.FAILED,
            )

        records_received = 0

        if data.inspection_id:
            existing = self.store.get_inspection(data.inspection_id)
            if existing:
                resolved = self.resolve_conflicts(existing, data)
                self.store.inspections[resolved.id] = resolved
            else:
                inspection = Inspection(
                    id=data.inspection_id,
                    vessel_id=data.vessel_id,
                    inspector_id=data.inspector_id or "unknown",
                    port_of_inspection=data.port_of_inspection or "unknown",
                    mou_region=MoURegion(data.mou_region) if data.mou_region else MoURegion.TOKYO,
                    started_at=datetime.now(),
                    synced=True,
                    synced_at=datetime.now(),
                )
                self.store.add_inspection(inspection)
            records_received += 1

        for det_data in data.detections:
            det = DetectionRecord(
                id=det_data.get("id", f"DET-{uuid.uuid4().hex[:8]}"),
                inspection_id=data.inspection_id or "unknown",
                defect_type=det_data.get("defect_type", "UNKNOWN"),
                confidence=det_data.get("confidence", 0.0),
                psc_code=det_data.get("psc_code", "0000"),
                severity=Severity(det_data.get("severity", "LOW")),
                bbox=BBox(**det_data["bbox"]) if "bbox" in det_data else BBox(
                    x_min=0, y_min=0, x_max=0, y_max=0
                ),
                model_version=det_data.get("model_version", "0.1.0"),
            )
            self.store.add_detection(det)
            records_received += 1

        sync_event = SyncEvent(
            id=f"SYNC-{uuid.uuid4().hex[:8]}",
            vessel_id=data.vessel_id,
            edge_server_id=data.edge_server_id,
            records_received=records_received,
            status=SyncStatus.SUCCESS,
        )
        self.store.add_sync_event(sync_event)
        return sync_event

    def resolve_conflicts(self, existing: Inspection, incoming: SyncReceiveRequest) -> Inspection:
        incoming_ts = incoming.timestamp or datetime.now().isoformat()
        existing_ts = existing.synced_at.isoformat() if existing.synced_at else "1970-01-01"

        if incoming_ts >= existing_ts:
            existing.synced = True
            existing.synced_at = datetime.now()
            if incoming.port_of_inspection:
                existing.port_of_inspection = incoming.port_of_inspection
        return existing

    def get_sync_history(self, vessel_id: str) -> list[SyncEvent]:
        return self.store.get_sync_history(vessel_id)
