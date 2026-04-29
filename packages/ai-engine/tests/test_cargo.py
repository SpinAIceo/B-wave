from ai_engine.cargo.detector import CargoDefect, CargoSecuringDetector, CargoSubtype
from ai_engine.inference.engine import Detection, InferenceEngine


class TestCargoSubtypeClassification:
    def setup_method(self):
        self.detector = CargoSecuringDetector(InferenceEngine("nonexistent.onnx"))

    def test_tall_narrow_high_confidence_is_turnbuckle(self):
        det = Detection(0.1, 0.1, 0.13, 0.5, 4, "cargo_lashing", 0.85)
        result = self.detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.TURNBUCKLE_BROKEN

    def test_tall_narrow_low_confidence_is_lashing(self):
        det = Detection(0.1, 0.1, 0.13, 0.5, 4, "cargo_lashing", 0.5)
        result = self.detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.LASHING_LOOSE

    def test_wide_short_is_wire_cut(self):
        det = Detection(0.1, 0.1, 0.8, 0.15, 4, "cargo_lashing", 0.7)
        result = self.detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.WIRE_CUT

    def test_large_square_is_securing_missing(self):
        det = Detection(0.1, 0.1, 0.5, 0.5, 4, "cargo_lashing", 0.6)
        result = self.detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.SECURING_MISSING

    def test_tiny_bbox_is_securing_missing(self):
        det = Detection(0.5, 0.5, 0.5, 0.5, 4, "cargo_lashing", 0.9)
        result = self.detector._classify_subtype(det)
        assert result.defect_subtype == CargoSubtype.SECURING_MISSING

    def test_psc_code_always_0725(self):
        det = Detection(0.1, 0.1, 0.8, 0.15, 4, "cargo_lashing", 0.7)
        result = self.detector._classify_subtype(det)
        assert result.psc_code == "0725"

    def test_cargo_defect_fields(self):
        det = Detection(0.1, 0.2, 0.3, 0.4, 4, "cargo_lashing", 0.75)
        result = self.detector._classify_subtype(det)
        assert isinstance(result, CargoDefect)
        assert result.x_min == 0.1
        assert result.y_min == 0.2
        assert result.confidence == 0.75


class TestCargoDetectorInit:
    def test_init_with_unloaded_engine(self):
        engine = InferenceEngine("nonexistent.onnx")
        detector = CargoSecuringDetector(engine)
        assert detector.CARGO_CLASS_NAME == "cargo_lashing"

    def test_detect_returns_empty_without_model(self, fake_jpeg_bytes):
        engine = InferenceEngine("nonexistent.onnx")
        detector = CargoSecuringDetector(engine)
        result = detector.detect(fake_jpeg_bytes)
        assert result == []
