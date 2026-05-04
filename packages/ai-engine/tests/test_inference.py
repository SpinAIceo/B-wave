from ai_engine.inference.engine import Detection, InferenceEngine, _iou, _nms


class TestInferenceEngineInit:
    def test_init_with_nonexistent_model(self):
        engine = InferenceEngine("nonexistent_model.onnx")
        assert not engine.is_loaded
        assert engine.runtime == "none"

    def test_init_model_version_default(self):
        engine = InferenceEngine("nonexistent.onnx")
        assert engine.model_version == "unknown"

    def test_predict_without_model(self, fake_jpeg_bytes):
        engine = InferenceEngine("nonexistent.onnx")
        result = engine.predict(fake_jpeg_bytes)
        assert result == []

    def test_class_names(self):
        engine = InferenceEngine("nonexistent.onnx")
        assert len(engine.class_names) == 3
        assert "rust" in engine.class_names
        assert "damage" in engine.class_names
        assert "leak" in engine.class_names


class TestNMS:
    def test_empty_detections(self):
        assert _nms([]) == []

    def test_no_overlap(self):
        dets = [
            Detection(0.0, 0.0, 0.1, 0.1, 0, "rust", 0.9),
            Detection(0.5, 0.5, 0.6, 0.6, 0, "rust", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 2

    def test_overlapping_same_class(self):
        dets = [
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 1
        assert result[0].confidence == 0.9

    def test_overlapping_different_class(self):
        dets = [
            Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.9),
            Detection(0.0, 0.0, 0.5, 0.5, 1, "damage", 0.8),
        ]
        result = _nms(dets, iou_threshold=0.45)
        assert len(result) == 2


class TestIoU:
    def test_no_overlap(self):
        a = Detection(0.0, 0.0, 0.1, 0.1, 0, "rust", 0.9)
        b = Detection(0.5, 0.5, 0.6, 0.6, 0, "rust", 0.8)
        assert _iou(a, b) == 0.0

    def test_perfect_overlap(self):
        a = Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.9)
        b = Detection(0.0, 0.0, 0.5, 0.5, 0, "rust", 0.8)
        assert abs(_iou(a, b) - 1.0) < 1e-6

    def test_partial_overlap(self):
        a = Detection(0.0, 0.0, 0.4, 0.4, 0, "rust", 0.9)
        b = Detection(0.2, 0.2, 0.6, 0.6, 0, "rust", 0.8)
        iou = _iou(a, b)
        assert 0.0 < iou < 1.0
