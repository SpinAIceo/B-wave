"""SC-01 + SC-07: AI inference pipeline and Cargo Securing tests."""

from __future__ import annotations

import pytest

from ai_engine.cargo.detector import CargoSecuringDetector, CargoSubtype
from ai_engine.inference.engine import Detection, InferenceEngine, _iou, _nms
from ai_engine.inference.psc_mapper import PSCCodeMapper, Severity
from bwave.v1 import common_pb2, inference_pb2


class TestInferenceEngine:
    def test_loads_without_model(self, inference_engine):
        assert not inference_engine.is_loaded
        assert inference_engine.runtime == "none"

    def test_predict_returns_list(self, inference_engine, fake_jpeg_bytes):
        result = inference_engine.predict(fake_jpeg_bytes)
        assert isinstance(result, list)
        assert result == []

    def test_class_names_count(self, inference_engine):
        assert len(inference_engine.class_names) == 5

    def test_class_names_content(self, inference_engine):
        expected = {"rust", "damage", "leak", "missing_label", "cargo_lashing"}
        assert set(inference_engine.class_names) == expected


class TestPSCMapper:
    @pytest.mark.parametrize(
        "defect_type,expected_code",
        [
            ("rust", "0615"),
            ("damage", "0630"),
            ("leak", "0950"),
            ("missing_label", "1320"),
            ("cargo_lashing", "0725"),
        ],
    )
    def test_all_five_type_mappings(self, psc_mapper, defect_type, expected_code):
        result = psc_mapper.map_defect(defect_type, 0.5)
        assert result.psc_code == expected_code

    def test_unknown_type_returns_9999(self, psc_mapper):
        result = psc_mapper.map_defect("unknown", 0.5)
        assert result.psc_code == "9999"

    def test_severity_critical_boundary(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.80)
        assert result.severity == Severity.CRITICAL

    def test_severity_high_boundary(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.60)
        assert result.severity == Severity.HIGH

    def test_severity_medium_boundary(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.40)
        assert result.severity == Severity.MEDIUM

    def test_severity_low_boundary(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.39)
        assert result.severity == Severity.LOW

    def test_severity_just_below_critical(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.799)
        assert result.severity == Severity.HIGH

    def test_get_all_mappings_count(self, psc_mapper):
        assert len(psc_mapper.get_all_mappings()) == 5


class TestNMS:
    def test_empty_input(self):
        assert _nms([]) == []

    def test_removes_duplicate_same_class(self):
        dets = [
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.7),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 1
        assert result[0].confidence == 0.9

    def test_preserves_different_classes(self):
        dets = [
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.0, 0.0, 0.5, 0.5, 1, "damage", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 2

    def test_preserves_non_overlapping(self):
        dets = [
            Detection(0.0, 0.0, 0.1, 0.1, 0, "rust", 0.9),
            Detection(0.8, 0.8, 0.9, 0.9, 0, "rust", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 2


class TestIoU:
    def test_identical_boxes_equals_one(self):
        a = Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.9)
        b = Detection(0.1, 0.1, 0.5, 0.5, 0, "rust", 0.8)
        assert abs(_iou(a, b) - 1.0) < 1e-6

    def test_no_overlap_equals_zero(self):
        a = Detection(0.0, 0.0, 0.1, 0.1, 0, "rust", 0.9)
        b = Detection(0.5, 0.5, 0.6, 0.6, 0, "rust", 0.8)
        assert _iou(a, b) == 0.0

    def test_partial_overlap_between_0_and_1(self):
        a = Detection(0.0, 0.0, 0.4, 0.4, 0, "rust", 0.9)
        b = Detection(0.2, 0.2, 0.6, 0.6, 0, "rust", 0.8)
        iou = _iou(a, b)
        assert 0.0 < iou < 1.0


class TestGRPCServicer:
    def test_detect_defects_returns_proto(self, grpc_servicer, mock_grpc_context):
        request = inference_pb2.DetectRequest(
            image_data=b"\xff\xd8\xff\xe0",
            image_width=640,
            image_height=480,
            inspection_id="test-001",
        )
        response = grpc_servicer.DetectDefects(request, mock_grpc_context)
        assert isinstance(response, inference_pb2.DetectResponse)

    def test_model_info_returns_defect_types(self, grpc_servicer, mock_grpc_context):
        request = common_pb2.Empty()
        response = grpc_servicer.GetModelInfo(request, mock_grpc_context)
        assert isinstance(response, inference_pb2.ModelInfo)
        assert len(response.supported_defect_types) == 5
        assert "rust" in response.supported_defect_types
        assert "cargo_lashing" in response.supported_defect_types

    def test_health_check_returns_status(self, grpc_servicer, mock_grpc_context):
        request = common_pb2.Empty()
        response = grpc_servicer.HealthCheck(request, mock_grpc_context)
        assert isinstance(response, common_pb2.HealthStatus)
        assert response.uptime_seconds >= 0


class TestCargoDetector:
    def test_init(self, cargo_detector):
        assert cargo_detector is not None
        assert cargo_detector.CARGO_CLASS_NAME == "cargo_lashing"

    def test_psc_code_is_0725(self):
        from ai_engine.cargo.detector import CargoDefect

        defect = CargoDefect(0.1, 0.2, 0.3, 0.4, CargoSubtype.LASHING_LOOSE, 0.8)
        assert defect.psc_code == "0725"

    @pytest.mark.parametrize(
        "width,height,confidence,expected_subtype",
        [
            (0.1, 0.4, 0.5, CargoSubtype.LASHING_LOOSE),
            (0.1, 0.4, 0.8, CargoSubtype.TURNBUCKLE_BROKEN),
            (0.6, 0.1, 0.5, CargoSubtype.WIRE_CUT),
            (0.4, 0.4, 0.5, CargoSubtype.SECURING_MISSING),
        ],
    )
    def test_subtype_classification(self, width, height, confidence, expected_subtype):
        det = Detection(
            x_min=0.0, y_min=0.0, x_max=width, y_max=height,
            class_id=4, class_name="cargo_lashing", confidence=confidence,
        )
        result = CargoSecuringDetector._infer_subtype(det)
        assert result == expected_subtype

    def test_all_four_subtypes_exist(self):
        assert len(CargoSubtype) == 4
        assert CargoSubtype.LASHING_LOOSE in CargoSubtype
        assert CargoSubtype.TURNBUCKLE_BROKEN in CargoSubtype
        assert CargoSubtype.WIRE_CUT in CargoSubtype
        assert CargoSubtype.SECURING_MISSING in CargoSubtype


class TestFullPipeline:
    def test_image_to_psc_codes(self, inference_engine, psc_mapper):
        """End-to-end: engine predict → mapper → PSC codes."""
        for defect_type in inference_engine.class_names:
            mapping = psc_mapper.map_defect(defect_type, 0.75)
            assert mapping.psc_code != "9999"
            assert mapping.severity in (Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL)
            assert len(mapping.description) > 0
