"""E2E-01: Basic Defect Detection Flow.

Validates the end-to-end pipeline:
  image bytes → InferenceEngine → PSCCodeMapper → gRPC proto response
"""
from __future__ import annotations

import time
from unittest.mock import MagicMock

from ai_engine.inference.engine import Detection, InferenceEngine
from ai_engine.inference.psc_mapper import PSCCodeMapper, Severity
from ai_engine.inference.server import EdgeInferenceServiceServicer
from bwave.v1 import common_pb2, inference_pb2


class TestGrpcServicerInstantiation:
    def test_servicer_creates(self, grpc_servicer):
        assert grpc_servicer is not None

    def test_servicer_has_engine(self, grpc_servicer):
        assert isinstance(grpc_servicer._engine, InferenceEngine)

    def test_servicer_has_mapper(self, grpc_servicer):
        assert isinstance(grpc_servicer._mapper, PSCCodeMapper)


class TestDetectDefectsRPC:
    def test_returns_detect_response(self, grpc_servicer, fake_jpeg_bytes):
        request = inference_pb2.DetectRequest(
            image_data=fake_jpeg_bytes,
            image_width=640,
            image_height=480,
            inspection_id="test-001",
        )
        ctx = MagicMock()
        response = grpc_servicer.DetectDefects(request, ctx)
        assert isinstance(response, inference_pb2.DetectResponse)

    def test_no_model_sets_unavailable(self, grpc_servicer, fake_jpeg_bytes):
        request = inference_pb2.DetectRequest(
            image_data=fake_jpeg_bytes,
            image_width=640,
            image_height=480,
            inspection_id="test-002",
        )
        ctx = MagicMock()
        grpc_servicer.DetectDefects(request, ctx)
        ctx.set_code.assert_called()

    def test_response_has_model_version(self, grpc_servicer, fake_jpeg_bytes):
        request = inference_pb2.DetectRequest(image_data=fake_jpeg_bytes)
        ctx = MagicMock()
        response = grpc_servicer.DetectDefects(request, ctx)
        assert isinstance(response.model_version, str)


class TestGetModelInfoRPC:
    def test_returns_model_info(self, grpc_servicer):
        ctx = MagicMock()
        response = grpc_servicer.GetModelInfo(common_pb2.Empty(), ctx)
        assert isinstance(response, inference_pb2.ModelInfo)

    def test_lists_all_defect_types(self, grpc_servicer):
        ctx = MagicMock()
        response = grpc_servicer.GetModelInfo(common_pb2.Empty(), ctx)
        types = list(response.supported_defect_types)
        assert len(types) == 5
        for expected in ["rust", "damage", "leak", "missing_label", "cargo_lashing"]:
            assert expected in types

    def test_model_name_present(self, grpc_servicer):
        ctx = MagicMock()
        response = grpc_servicer.GetModelInfo(common_pb2.Empty(), ctx)
        assert response.model_name == "bwave-yolov8-defect"


class TestHealthCheckRPC:
    def test_returns_health_status(self, grpc_servicer):
        ctx = MagicMock()
        response = grpc_servicer.HealthCheck(common_pb2.Empty(), ctx)
        assert isinstance(response, common_pb2.HealthStatus)

    def test_reports_unloaded_model(self, grpc_servicer):
        ctx = MagicMock()
        response = grpc_servicer.HealthCheck(common_pb2.Empty(), ctx)
        assert response.healthy is False

    def test_uptime_is_positive(self, grpc_servicer):
        time.sleep(0.01)
        ctx = MagicMock()
        response = grpc_servicer.HealthCheck(common_pb2.Empty(), ctx)
        assert response.uptime_seconds >= 0


class TestPSCCodeMappingPipeline:
    ALL_DEFECTS = {
        "rust": "0615",
        "damage": "0630",
        "leak": "0950",
        "missing_label": "1320",
        "cargo_lashing": "0725",
    }

    def test_all_defect_types_map(self, psc_mapper):
        for defect_type, expected_code in self.ALL_DEFECTS.items():
            mapping = psc_mapper.map_defect(defect_type, 0.7)
            assert mapping.psc_code == expected_code

    def test_unknown_defect_type(self, psc_mapper):
        mapping = psc_mapper.map_defect("unknown_type", 0.9)
        assert mapping.psc_code == "9999"


class TestE2EPipelineFlow:
    def test_detection_to_proto_roundtrip(self, psc_mapper):
        det = Detection(
            x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6,
            class_id=0, class_name="rust", confidence=0.85,
        )
        mapping = psc_mapper.map_defect(det.class_name, det.confidence)

        proto_defect = common_pb2.Defect(
            bbox=common_pb2.BoundingBox(
                x_min=det.x_min, y_min=det.y_min,
                x_max=det.x_max, y_max=det.y_max,
            ),
            defect_type=common_pb2.DEFECT_TYPE_RUST,
            confidence=det.confidence,
            psc_code=mapping.psc_code,
            severity=int(mapping.severity),
        )

        assert proto_defect.psc_code == "0615"
        assert abs(proto_defect.confidence - 0.85) < 1e-5
        assert proto_defect.severity == int(Severity.CRITICAL)
        assert abs(proto_defect.bbox.x_min - 0.1) < 1e-5

    def test_response_construction(self, psc_mapper):
        detections = [
            Detection(0.1, 0.2, 0.4, 0.5, 0, "rust", 0.87),
            Detection(0.5, 0.1, 0.8, 0.3, 1, "damage", 0.92),
        ]

        defects = []
        for det in detections:
            m = psc_mapper.map_defect(det.class_name, det.confidence)
            defects.append(common_pb2.Defect(
                psc_code=m.psc_code,
                confidence=det.confidence,
                severity=int(m.severity),
            ))

        response = inference_pb2.DetectResponse(
            defects=defects,
            inference_time_ms=123.4,
            model_version="0.1.0",
        )

        assert len(response.defects) == 2
        assert abs(response.inference_time_ms - 123.4) < 0.1
        assert response.defects[0].psc_code == "0615"
        assert response.defects[1].psc_code == "0630"

    def test_response_timing_tracked(self, psc_mapper):
        start = time.perf_counter()
        for dt in ["rust", "damage", "leak", "missing_label", "cargo_lashing"]:
            psc_mapper.map_defect(dt, 0.5)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500
