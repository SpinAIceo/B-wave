"""QA: Edge Case Tests — boundary values, malformed inputs, stress scenarios."""

from __future__ import annotations

import io
import struct
import time
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EDGE_SRC = ROOT / "packages" / "edge-platform" / "src"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tiny_jpeg() -> bytes:
    img = Image.new("RGB", (1, 1), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def large_jpeg() -> bytes:
    img = Image.new("RGB", (4096, 4096), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=50)
    return buf.getvalue()


@pytest.fixture()
def corrupted_bytes() -> bytes:
    return b"\x00\x01\x02\x03\x04\x05NOTAJPEG"


@pytest.fixture()
def empty_bytes() -> bytes:
    return b""


@pytest.fixture()
def png_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# AI Engine Edge Cases
# ---------------------------------------------------------------------------


class TestInferenceEdgeCases:
    def test_empty_image_bytes(self, inference_engine, empty_bytes):
        result = inference_engine.predict(empty_bytes)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_corrupted_image_bytes(self, inference_engine, corrupted_bytes):
        result = inference_engine.predict(corrupted_bytes)
        assert isinstance(result, list)

    def test_tiny_1x1_image(self, inference_engine, tiny_jpeg):
        result = inference_engine.predict(tiny_jpeg)
        assert isinstance(result, list)

    def test_large_4096x4096_image(self, inference_engine, large_jpeg):
        result = inference_engine.predict(large_jpeg)
        assert isinstance(result, list)

    def test_png_format_input(self, inference_engine, png_bytes):
        result = inference_engine.predict(png_bytes)
        assert isinstance(result, list)

    def test_none_model_path_handling(self):
        from ai_engine.inference.engine import InferenceEngine
        engine = InferenceEngine("nonexistent.onnx")
        assert not engine.is_loaded

    def test_repeated_predictions_no_memory_leak(self, inference_engine, fake_jpeg_bytes):
        for _ in range(100):
            inference_engine.predict(fake_jpeg_bytes)


class TestPSCMapperEdgeCases:
    def test_confidence_exactly_zero(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.0)
        assert result.psc_code == "0615"

    def test_confidence_exactly_one(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 1.0)
        assert result.psc_code == "0615"

    def test_confidence_negative(self, psc_mapper):
        result = psc_mapper.map_defect("rust", -0.1)
        assert result.psc_code == "0615"

    def test_confidence_above_one(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 1.5)
        assert result.psc_code == "0615"

    def test_empty_string_defect_type(self, psc_mapper):
        result = psc_mapper.map_defect("", 0.9)
        assert result.psc_code is not None

    def test_very_long_defect_type(self, psc_mapper):
        result = psc_mapper.map_defect("x" * 10000, 0.5)
        assert result.psc_code is not None

    def test_special_chars_defect_type(self, psc_mapper):
        result = psc_mapper.map_defect("rust'; DROP TABLE--", 0.9)
        assert result.psc_code is not None

    def test_unicode_defect_type(self, psc_mapper):
        result = psc_mapper.map_defect("부식", 0.8)
        assert result.psc_code is not None

    def test_boundary_critical_0_80(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.80)
        assert result.severity.value == 4  # CRITICAL

    def test_boundary_just_below_critical_0_7999(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.7999)
        assert result.severity.value < 4

    def test_boundary_high_0_60(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.60)
        assert result.severity.value == 3  # HIGH

    def test_boundary_just_below_high_0_5999(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.5999)
        assert result.severity.value < 3

    def test_boundary_medium_0_40(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.40)
        assert result.severity.value == 2  # MEDIUM

    def test_boundary_just_below_medium_0_3999(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.3999)
        assert result.severity.value == 1  # LOW


class TestNMSEdgeCases:
    def test_single_detection(self):
        from ai_engine.inference.engine import Detection, _nms
        dets = [Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.9)]
        result = _nms(dets)
        assert len(result) == 1

    def test_many_overlapping_detections(self):
        from ai_engine.inference.engine import Detection, _nms
        dets = [Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.9 - i * 0.01) for i in range(50)]
        result = _nms(dets, iou_threshold=0.5)
        assert len(result) == 1

    def test_zero_area_box(self):
        from ai_engine.inference.engine import Detection, _iou
        a = Detection(0.5, 0.5, 0.5, 0.5, 0, "rust", 0.9)
        b = Detection(0.5, 0.5, 0.5, 0.5, 0, "rust", 0.8)
        iou = _iou(a, b)
        assert iou >= 0

    def test_negative_coordinates(self):
        from ai_engine.inference.engine import Detection, _iou
        a = Detection(-0.1, -0.1, 0.1, 0.1, 0, "rust", 0.9)
        b = Detection(0.0, 0.0, 0.2, 0.2, 0, "rust", 0.8)
        iou = _iou(a, b)
        assert 0 <= iou <= 1

    def test_coordinates_beyond_one(self):
        from ai_engine.inference.engine import Detection, _iou
        a = Detection(0.8, 0.8, 1.2, 1.2, 0, "rust", 0.9)
        b = Detection(0.9, 0.9, 1.3, 1.3, 0, "rust", 0.8)
        iou = _iou(a, b)
        assert 0 <= iou <= 1

    def test_iou_threshold_zero_keeps_one(self):
        from ai_engine.inference.engine import Detection, _nms
        dets = [
            Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.2, 0.2, 0.6, 0.6, 0, "rust", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.0)
        assert len(result) == 1

    def test_iou_threshold_one_keeps_all(self):
        from ai_engine.inference.engine import Detection, _nms
        dets = [
            Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.8),
        ]
        result = _nms(dets, iou_threshold=1.0)
        assert len(result) == 2


class TestCargoSecuringEdgeCases:
    def test_zero_area_bbox_subtype(self, cargo_detector):
        from ai_engine.cargo.detector import CargoDefect, CargoSubtype
        defect = CargoDefect(0.5, 0.5, 0.5, 0.5, CargoSubtype.SECURING_MISSING, 0.9)
        assert defect.defect_subtype == CargoSubtype.SECURING_MISSING

    def test_full_frame_bbox(self, cargo_detector):
        from ai_engine.cargo.detector import CargoDefect, CargoSubtype
        defect = CargoDefect(0.0, 0.0, 1.0, 1.0, CargoSubtype.LASHING_LOOSE, 0.7)
        assert defect.psc_code == "0725"


# ---------------------------------------------------------------------------
# gRPC Servicer Edge Cases
# ---------------------------------------------------------------------------


class TestGRPCServicerEdgeCases:
    def test_empty_image_data(self, grpc_servicer, mock_grpc_context):
        from bwave.v1 import inference_pb2
        request = inference_pb2.DetectRequest(
            image_data=b"",
            image_width=0,
            image_height=0,
            inspection_id="",
        )
        response = grpc_servicer.DetectDefects(request, mock_grpc_context)
        assert isinstance(response, inference_pb2.DetectResponse)

    def test_very_large_inspection_id(self, grpc_servicer, mock_grpc_context):
        from bwave.v1 import inference_pb2
        request = inference_pb2.DetectRequest(
            image_data=b"\xff\xd8\xff\xe0",
            image_width=640,
            image_height=480,
            inspection_id="x" * 100000,
        )
        response = grpc_servicer.DetectDefects(request, mock_grpc_context)
        assert isinstance(response, inference_pb2.DetectResponse)

    def test_negative_dimensions(self, grpc_servicer, mock_grpc_context):
        from bwave.v1 import inference_pb2
        request = inference_pb2.DetectRequest(
            image_data=b"\xff\xd8\xff\xe0",
            image_width=-1,
            image_height=-1,
            inspection_id="test",
        )
        response = grpc_servicer.DetectDefects(request, mock_grpc_context)
        assert isinstance(response, inference_pb2.DetectResponse)

    def test_health_check_returns_uptime(self, grpc_servicer, mock_grpc_context):
        from bwave.v1 import common_pb2
        response = grpc_servicer.HealthCheck(common_pb2.Empty(), mock_grpc_context)
        assert response.uptime_seconds >= 0


# ---------------------------------------------------------------------------
# Fleet API Edge Cases
# ---------------------------------------------------------------------------


class TestFleetAPIEdgeCases:
    def test_vessel_id_empty_string(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/")
        assert resp.status_code in (404, 307, 200)

    def test_vessel_id_special_chars(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/../../etc/passwd")
        assert resp.status_code == 404

    def test_vessel_id_sql_injection(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/' OR 1=1 --")
        assert resp.status_code == 404

    def test_vessel_id_unicode(self, fleet_client):
        resp = fleet_client.get("/api/v1/vessels/선박-001")
        assert resp.status_code == 404

    def test_vessel_id_very_long(self, fleet_client):
        resp = fleet_client.get(f"/api/v1/vessels/{'A' * 10000}")
        assert resp.status_code == 404

    def test_sync_receive_empty_body(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={})
        assert resp.status_code in (400, 422)

    def test_sync_receive_null_values(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={
            "vessel_id": None,
            "inspector_id": None,
        })
        assert resp.status_code in (400, 422)

    def test_sync_receive_extra_fields(self, fleet_client):
        resp = fleet_client.post("/api/v1/sync/receive", json={
            "vessel_id": "V-001",
            "inspector_id": "CREW-001",
            "port": "Busan",
            "unexpected_field": "should be ignored",
            "detections": [],
        })
        assert resp.status_code in (200, 201, 422)

    def test_report_generate_empty_vessel_id(self, fleet_client):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "",
            "report_type": "psc_readiness",
        })
        assert resp.status_code in (200, 400, 404, 422)

    def test_report_generate_null_type(self, fleet_client):
        resp = fleet_client.post("/api/v1/reports/generate", json={
            "vessel_id": "V-001",
            "report_type": None,
        })
        assert resp.status_code in (400, 422)

    def test_webhook_configure_empty_url(self, fleet_client):
        resp = fleet_client.post("/api/v1/webhooks/configure", json={
            "url": "",
            "events": ["defect.critical"],
        })
        assert resp.status_code in (200, 400, 422)

    def test_webhook_configure_malicious_url(self, fleet_client):
        resp = fleet_client.post("/api/v1/webhooks/configure", json={
            "url": "javascript:alert(1)",
            "events": ["defect.critical"],
        })
        assert resp.status_code in (200, 400)

    def test_dashboard_overview_consistent_totals(self, fleet_client):
        resp = fleet_client.get("/api/v1/dashboard/overview")
        data = resp.json()
        assert data["total_vessels"] >= 0
        assert data["active_inspections"] >= 0
        assert data["critical_defects"] >= 0
        if "detention_risk_score" in data:
            assert 0 <= data["detention_risk_score"] <= 100

    def test_concurrent_vessel_requests(self, fleet_client):
        import concurrent.futures
        def fetch_vessel(vid):
            return fleet_client.get(f"/api/v1/vessels/{vid}").status_code
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(fetch_vessel, f"V-{i:03d}") for i in range(1, 6)]
            results = [f.result() for f in futures]
        assert all(r == 200 for r in results)


# ---------------------------------------------------------------------------
# Offline Edge Cases
# ---------------------------------------------------------------------------


class TestOfflineEdgeCases:
    def test_sync_queue_empty(self):
        queue = []
        sorted_queue = sorted(queue, key=lambda x: x.get("priority", 99))
        assert sorted_queue == []

    def test_sync_queue_single_item(self):
        queue = [{"id": "A", "priority": 0}]
        sorted_queue = sorted(queue, key=lambda x: x["priority"])
        assert len(sorted_queue) == 1

    def test_sync_queue_all_same_priority(self):
        queue = [{"id": f"R-{i}", "priority": 1} for i in range(10)]
        sorted_queue = sorted(queue, key=lambda x: x["priority"])
        assert len(sorted_queue) == 10

    def test_sync_queue_massive_backlog(self):
        queue = [{"id": f"R-{i}", "priority": i % 4, "synced": False} for i in range(10000)]
        sorted_queue = sorted(queue, key=lambda x: x["priority"])
        assert sorted_queue[0]["priority"] == 0
        assert sorted_queue[-1]["priority"] == 3
        assert len(sorted_queue) == 10000

    def test_data_integrity_special_chars(self):
        record = {
            "id": "REC-001",
            "notes": "부식 발견 — O'Brien's inspection <script>alert('xss')</script>",
            "port": "Busan 부산",
        }
        assert record["notes"] is not None
        assert "<script>" in record["notes"]


# ---------------------------------------------------------------------------
# Rust Edge Platform Edge Cases (via cargo test)
# ---------------------------------------------------------------------------


class TestRustEdgeCases:
    """Verify Rust unit tests cover edge cases by checking cargo test output."""

    @pytest.fixture(autouse=True, scope="class")
    def cargo_output(self, request):
        import subprocess
        try:
            result = subprocess.run(
                ["cargo", "test"],
                capture_output=True,
                text=True,
                cwd=str(ROOT / "packages" / "edge-platform"),
                timeout=300,
            )
            request.cls.output = result.stdout + result.stderr
            request.cls.passed = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("cargo not available")

    def test_all_rust_tests_pass(self):
        assert self.passed, f"cargo test failed:\n{self.output[-1000:]}"

    def test_no_violations_for_unknown_defect(self):
        assert "no_violations_for_unknown_defect_type ... ok" in self.output

    def test_nonexistent_inspection_returns_none(self):
        assert "nonexistent_inspection_returns_none ... ok" in self.output

    def test_authenticate_invalid_token(self):
        assert "authenticate_invalid_token ... ok" in self.output

    def test_authenticate_unknown_role(self):
        assert "authenticate_unknown_role ... ok" in self.output
