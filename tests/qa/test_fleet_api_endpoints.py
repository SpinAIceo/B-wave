"""SC-06: Fleet View API endpoint tests."""

from __future__ import annotations

import pytest

VESSEL_IDS = ["V-001", "V-002", "V-003", "V-004", "V-005"]
REPORT_TYPES = ["psc_readiness", "class_survey", "security_audit", "cic_compliance"]


class TestHealthEndpoint:
    def test_health_returns_ok(self, fleet_client):
        resp = fleet_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_health_response_time(self, fleet_client):
        import time

        start = time.perf_counter()
        fleet_client.get("/health")
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0


class TestVesselsEndpoint:
    def test_vessels_list_count(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels")
        assert resp.status_code == 200
        assert len(resp.json()) == 5

    def test_vessels_list_has_required_fields(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels")
        required = {"id", "name", "type", "flag", "status", "latitude", "longitude"}
        for vessel in resp.json():
            assert required.issubset(vessel.keys()), f"Missing fields in {vessel.get('id')}"

    @pytest.mark.parametrize("vessel_id", VESSEL_IDS)
    def test_vessel_detail_by_id(self, fleet_client, vessel_id):
        resp = fleet_client.get(f"/api/v1/vessels/{vessel_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == vessel_id
        assert len(data["name"]) > 0

    def test_vessel_detail_not_found(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/INVALID-999")
        assert resp.status_code == 404

    def test_vessel_names_are_unique(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels")
        names = [v["name"] for v in resp.json()]
        assert len(names) == len(set(names))

    def test_vessel_coordinates_reasonable(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels")
        for v in resp.json():
            assert -90 <= v["latitude"] <= 90
            assert -180 <= v["longitude"] <= 180


class TestInspectionsEndpoint:
    def test_vessel_inspections_returns_list(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_vessel_inspections_not_found(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/INVALID/inspections")
        assert resp.status_code == 404

    def test_inspection_has_required_fields(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections")
        required = {"id", "vessel_id", "inspector_id", "port_of_inspection", "total_items"}
        for ins in resp.json():
            assert required.issubset(ins.keys())

    def test_inspection_items_consistent(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections")
        for ins in resp.json():
            assert ins["passed"] + ins["failed"] <= ins["total_items"]


class TestDetectionsEndpoint:
    def test_detections_returns_list(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections/INS-001/detections")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_detections_not_found(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections/INVALID/detections")
        assert resp.status_code == 404

    def test_detection_has_psc_code(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections/INS-001/detections")
        for det in resp.json():
            assert "psc_code" in det
            assert len(det["psc_code"]) == 4

    def test_detection_bbox_normalized(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/V-001/inspections/INS-001/detections")
        for det in resp.json():
            bbox = det["bbox"]
            assert 0 <= bbox["x_min"] <= 1
            assert 0 <= bbox["y_min"] <= 1
            assert 0 <= bbox["x_max"] <= 1
            assert 0 <= bbox["y_max"] <= 1
            assert bbox["x_max"] >= bbox["x_min"]
            assert bbox["y_max"] >= bbox["y_min"]


class TestDashboardEndpoint:
    def test_dashboard_overview_structure(self, fleet_client):
        resp = fleet_client.get("/api/v1/dashboard/overview")
        assert resp.status_code == 200
        data = resp.json()
        required = {
            "total_vessels",
            "active_inspections",
            "critical_defects",
            "detention_risk_score",
            "vessels_by_status",
            "defect_type_distribution",
        }
        assert required.issubset(data.keys())

    def test_dashboard_values_reasonable(self, fleet_client):
        resp = fleet_client.get("/api/v1/dashboard/overview")
        data = resp.json()
        assert data["total_vessels"] == 5
        assert data["active_inspections"] >= 0
        assert data["critical_defects"] >= 0
        assert 0 <= data["detention_risk_score"] <= 100

    def test_dashboard_vessel_status_sum(self, fleet_client):
        resp = fleet_client.get("/api/v1/dashboard/overview")
        data = resp.json()
        total_by_status = sum(data["vessels_by_status"].values())
        assert total_by_status == data["total_vessels"]

    def test_dashboard_defect_distribution_types(self, fleet_client):
        resp = fleet_client.get("/api/v1/dashboard/overview")
        valid_types = {"RUST", "DAMAGE", "LEAK", "MISSING_LABEL", "CARGO_LASHING"}
        for defect_type in resp.json()["defect_type_distribution"]:
            assert defect_type in valid_types


class TestSyncEndpoint:
    def test_sync_receive_valid(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={
            "vessel_id": "V-001",
            "edge_server_id": "EDGE-001",
            "inspection_id": "INS-NEW-001",
            "inspector_id": "CREW-101",
            "port_of_inspection": "Busan",
            "mou_region": "TOKYO",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SUCCESS"
        assert data["records_received"] >= 1

    def test_sync_receive_with_detections(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={
            "vessel_id": "V-002",
            "edge_server_id": "EDGE-002",
            "inspection_id": "INS-NEW-002",
            "detections": [
                {
                    "defect_type": "RUST",
                    "confidence": 0.85,
                    "psc_code": "0615",
                    "severity": "HIGH",
                    "bbox": {"x_min": 0.1, "y_min": 0.2, "x_max": 0.4, "y_max": 0.5},
                }
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["records_received"] >= 2

    def test_sync_receive_minimal(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={
            "vessel_id": "V-003",
            "edge_server_id": "EDGE-003",
        })
        assert resp.status_code == 200


class TestReportsEndpoint:
    @pytest.mark.parametrize("report_type", REPORT_TYPES)
    def test_report_generate_by_type(self, fleet_client, report_type):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "V-001",
            "report_type": report_type,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["report_type"] == report_type
        assert data["vessel_id"] == "V-001"
        assert data["status"] == "generated"

    def test_report_generate_invalid_type(self, fleet_client):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "V-001",
            "report_type": "invalid_report",
        })
        assert resp.status_code == 400

    def test_report_generate_invalid_vessel(self, fleet_client):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "INVALID",
            "report_type": "psc_readiness",
        })
        assert resp.status_code == 400

    def test_report_get_by_id(self, fleet_client):
        create_resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "V-001",
            "report_type": "psc_readiness",
        })
        report_id = create_resp.json()["id"]

        get_resp = fleet_client.get(f"/api/v1/reports/{report_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == report_id

    def test_report_get_not_found(self, fleet_client):
        resp = fleet_client.get("/api/v1/reports/RPT-nonexistent")
        assert resp.status_code == 404

    def test_report_has_file_path(self, fleet_client):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "V-001",
            "report_type": "class_survey",
        })
        data = resp.json()
        assert data["file_path"] is not None
        assert "V-001" in data["file_path"]


class TestWebhooksEndpoint:
    def test_webhook_configure_valid(self, fleet_client):
        resp = fleet_client.post("/api/v1/webhooks/configure", json={
            "url": "https://example.com/webhook",
            "events": ["defect.critical", "sync.received"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "webhook_id" in data
        assert data["status"] == "configured"

    def test_webhook_configure_invalid_event(self, fleet_client):
        resp = fleet_client.post("/api/v1/webhooks/configure", json={
            "url": "https://example.com/webhook",
            "events": ["invalid.event"],
        })
        assert resp.status_code == 400

    def test_webhook_test_delivery(self, fleet_client):
        config_resp = fleet_client.post("/api/v1/webhooks/configure", json={
            "url": "https://example.com/hook",
            "events": ["defect.critical"],
        })
        wh_id = config_resp.json()["webhook_id"]

        test_resp = fleet_client.post("/api/v1/webhooks/test", json={
            "webhook_id": wh_id,
        })
        assert test_resp.status_code == 200
        assert test_resp.json()["status"] == "delivered"

    def test_webhook_test_not_found(self, fleet_client):
        resp = fleet_client.post("/api/v1/webhooks/test", json={
            "webhook_id": "WH-nonexistent",
        })
        assert resp.status_code == 404
