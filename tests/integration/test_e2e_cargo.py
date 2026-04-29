"""E2E-04: Cargo Securing Module (CIC 2026).

Validates the specialized cargo securing detection pipeline:
  - CargoSecuringDetector initialization and filtering
  - PSC code 0725 mapping
  - All 4 subtypes: LASHING_LOOSE, TURNBUCKLE_BROKEN, WIRE_CUT, SECURING_MISSING
  - Severity prioritization for cargo defects
  - CIC 2026 target flag in the Rust rule engine
"""
from __future__ import annotations

import re
from pathlib import Path

from ai_engine.cargo.detector import CargoDefect, CargoSecuringDetector, CargoSubtype
from ai_engine.inference.engine import Detection, InferenceEngine
from ai_engine.inference.psc_mapper import PSCCodeMapper, Severity


class TestCargoDetectorInit:
    def test_creates_with_engine(self, inference_engine):
        detector = CargoSecuringDetector(inference_engine)
        assert detector is not None
        assert detector.CARGO_CLASS_NAME == "cargo_lashing"

    def test_detect_returns_empty_without_model(self, cargo_detector, fake_jpeg_bytes):
        results = cargo_detector.detect(fake_jpeg_bytes)
        assert results == []


class TestCargoSubtypeClassification:
    """Verifies heuristic-based subtype classification via bbox geometry."""

    def _make_detection(self, x_min, y_min, x_max, y_max, confidence=0.8):
        return Detection(
            x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max,
            class_id=4, class_name="cargo_lashing", confidence=confidence,
        )

    def test_tall_narrow_high_conf_is_turnbuckle(self, cargo_detector):
        det = self._make_detection(0.1, 0.1, 0.15, 0.6, confidence=0.8)
        result = cargo_detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.TURNBUCKLE_BROKEN

    def test_tall_narrow_low_conf_is_lashing_loose(self, cargo_detector):
        det = self._make_detection(0.1, 0.1, 0.15, 0.6, confidence=0.5)
        result = cargo_detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.LASHING_LOOSE

    def test_wide_short_is_wire_cut(self, cargo_detector):
        det = self._make_detection(0.1, 0.4, 0.8, 0.45, confidence=0.8)
        result = cargo_detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.WIRE_CUT

    def test_large_area_is_securing_missing(self, cargo_detector):
        det = self._make_detection(0.1, 0.1, 0.5, 0.5, confidence=0.8)
        result = cargo_detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.SECURING_MISSING

    def test_tiny_bbox_is_securing_missing(self, cargo_detector):
        det = self._make_detection(0.5, 0.5, 0.5005, 0.5005, confidence=0.9)
        result = cargo_detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.SECURING_MISSING

    def test_all_subtypes_have_psc_0725(self, cargo_detector):
        bboxes = [
            (0.1, 0.1, 0.15, 0.6, 0.8),   # TURNBUCKLE_BROKEN
            (0.1, 0.1, 0.15, 0.6, 0.5),   # LASHING_LOOSE
            (0.1, 0.4, 0.8, 0.45, 0.8),   # WIRE_CUT
            (0.1, 0.1, 0.5, 0.5, 0.8),    # SECURING_MISSING
        ]
        for x1, y1, x2, y2, conf in bboxes:
            det = self._make_detection(x1, y1, x2, y2, conf)
            result = cargo_detector._classify_subtype(det)
            assert result.psc_code == "0725"


class TestCargoPSCMapping:
    def test_cargo_lashing_maps_to_0725(self, psc_mapper):
        mapping = psc_mapper.map_defect("cargo_lashing", 0.85)
        assert mapping.psc_code == "0725"
        assert mapping.description == "Cargo securing deficiency"

    def test_high_confidence_cargo_is_critical(self, psc_mapper):
        mapping = psc_mapper.map_defect("cargo_lashing", 0.9)
        assert mapping.severity == Severity.CRITICAL

    def test_medium_confidence_cargo_is_high(self, psc_mapper):
        mapping = psc_mapper.map_defect("cargo_lashing", 0.7)
        assert mapping.severity == Severity.HIGH


class TestCargoCIC2026Rust:
    """Verify CIC 2026 target flags in the Rust rule engine source."""

    def _read_rules(self):
        path = Path(__file__).resolve().parents[2] / "packages" / "edge-platform" / "src" / "rule_engine.rs"
        return path.read_text(encoding="utf-8")

    def test_cic_rules_exist(self):
        source = self._read_rules()
        assert "cic_target_2026: true" in source

    def test_code_0725_is_cic_target(self):
        source = self._read_rules()
        block_0725 = source[source.index('"0725"'):source.index('"0725"') + 500]
        assert "cic_target_2026: true" in block_0725

    def test_code_0726_is_cic_target(self):
        source = self._read_rules()
        block_0726 = source[source.index('"0726"'):source.index('"0726"') + 500]
        assert "cic_target_2026: true" in block_0726

    def test_code_0728_is_cic_target(self):
        source = self._read_rules()
        block_0728 = source[source.index('"0728"'):source.index('"0728"') + 500]
        assert "cic_target_2026: true" in block_0728

    def test_cargo_lashing_in_related_types(self):
        source = self._read_rules()
        cargo_blocks = [i for i in range(len(source)) if source[i:].startswith('"CARGO_LASHING"')]
        assert len(cargo_blocks) >= 2
