from __future__ import annotations

import uuid
from datetime import datetime

from .models import AuditReport, ReportFormat
from .store import DataStore

SUPPORTED_REPORT_TYPES = {"psc_readiness", "class_survey", "security_audit", "cic_compliance"}


class ReportEngine:
    def __init__(self, store: DataStore) -> None:
        self.store = store
        self.reports: dict[str, AuditReport] = {}

    def generate_audit_report(
        self,
        vessel_id: str,
        report_type: str = "psc_readiness",
        fmt: ReportFormat = ReportFormat.PDF,
    ) -> AuditReport:
        vessel = self.store.get_vessel(vessel_id)
        if vessel is None:
            raise ValueError(f"Vessel {vessel_id} not found")
        if report_type not in SUPPORTED_REPORT_TYPES:
            raise ValueError(f"Unsupported report type: {report_type}")

        report_id = f"RPT-{uuid.uuid4().hex[:8]}"
        report = AuditReport(
            id=report_id,
            vessel_id=vessel_id,
            generated_at=datetime.now(),
            report_type=report_type,
            format=fmt,
            file_path=f"/reports/{vessel_id}/{report_id}.{fmt.value.lower()}",
            status="generated",
        )
        self.reports[report_id] = report
        return report

    def get_report(self, report_id: str) -> AuditReport | None:
        return self.reports.get(report_id)

    def generate_fleet_summary(self) -> dict:
        vessels = self.store.get_vessels()
        all_detections = self.store.get_all_detections()
        overview = self.store.get_dashboard_overview()

        vessel_summaries = []
        for v in vessels:
            inspections = self.store.get_inspections(v.id)
            total_defects = 0
            for ins in inspections:
                total_defects += len(self.store.get_detections(ins.id))
            vessel_summaries.append({
                "vessel_id": v.id,
                "vessel_name": v.name,
                "flag": v.flag,
                "inspection_count": len(inspections),
                "total_defects": total_defects,
                "status": v.status.value,
            })

        return {
            "generated_at": datetime.now().isoformat(),
            "fleet_overview": overview.model_dump(),
            "vessel_summaries": vessel_summaries,
            "total_detections": len(all_detections),
        }

    def generate_report_data(self, vessel_id: str, report_type: str) -> dict:
        vessel = self.store.get_vessel(vessel_id)
        if vessel is None:
            return {}

        inspections = self.store.get_inspections(vessel_id)
        detections = []
        for ins in inspections:
            detections.extend(self.store.get_detections(ins.id))

        base = {
            "vessel": vessel.model_dump(),
            "inspections": [i.model_dump() for i in inspections],
            "detections": [d.model_dump() for d in detections],
        }

        if report_type == "psc_readiness":
            base["readiness_score"] = _compute_readiness(inspections)
            base["recommendation"] = (
                "Address all CRITICAL and HIGH severity items before port call."
            )
        elif report_type == "class_survey":
            base["survey_standard"] = "DNV GL Rules for Classification"
            base["compliance_status"] = "CONDITIONAL" if detections else "COMPLIANT"
        elif report_type == "security_audit":
            base["standard"] = "IACS UR E26/E27"
            base["audit_areas"] = [
                "Network segmentation (OT/IT separation)",
                "Access control (RBAC)",
                "Audit logging",
                "Encryption at rest and in transit",
            ]
            base["compliance_status"] = "COMPLIANT"
        elif report_type == "cic_compliance":
            cargo_defects = [d for d in detections if d.defect_type == "CARGO_LASHING"]
            base["cic_year"] = 2026
            base["focus_area"] = "Cargo Securing"
            base["cargo_defects_found"] = len(cargo_defects)
            base["compliance_status"] = "NON_COMPLIANT" if cargo_defects else "COMPLIANT"

        return base


def _compute_readiness(inspections: list) -> float:
    if not inspections:
        return 100.0
    total = sum(i.total_items for i in inspections)
    passed = sum(i.passed for i in inspections)
    return round(passed / total * 100, 1) if total > 0 else 100.0
