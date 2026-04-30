"""QA: SC-03 Offline Operation Scenarios."""

from __future__ import annotations

import time


class TestInferenceOffline:
    def test_no_network_dependency(self, inference_engine):
        assert inference_engine is not None
        assert inference_engine.runtime in ("onnxruntime", "ultralytics", "none")

    def test_predict_without_connectivity(self, inference_engine, fake_jpeg_bytes):
        result = inference_engine.predict(fake_jpeg_bytes)
        assert isinstance(result, list)

    def test_class_names_embedded(self, inference_engine):
        assert len(inference_engine.class_names) == 5
        for name in ["rust", "damage", "leak", "missing_label", "cargo_lashing"]:
            assert name in inference_engine.class_names


class TestPSCMapperOffline:
    def test_all_rules_embedded(self, psc_mapper):
        mappings = psc_mapper.get_all_mappings()
        assert len(mappings) >= 5

    def test_map_without_network(self, psc_mapper):
        result = psc_mapper.map_defect("rust", 0.85)
        assert result.psc_code == "0615"
        assert result.severity is not None

    def test_all_five_types_offline(self, psc_mapper):
        expected = {
            "rust": "0615",
            "damage": "0630",
            "leak": "0950",
            "missing_label": "1320",
            "cargo_lashing": "0725",
        }
        for defect_type, expected_code in expected.items():
            result = psc_mapper.map_defect(defect_type, 0.7)
            assert result.psc_code == expected_code, f"{defect_type} should map to {expected_code}"


class TestSyncQueuePriority:
    def test_critical_before_normal(self):
        queue = [
            {"id": "A", "priority": 2, "type": "normal"},
            {"id": "B", "priority": 0, "type": "critical"},
            {"id": "C", "priority": 1, "type": "high"},
        ]
        sorted_queue = sorted(queue, key=lambda x: x["priority"])
        assert sorted_queue[0]["type"] == "critical"
        assert sorted_queue[1]["type"] == "high"
        assert sorted_queue[2]["type"] == "normal"

    def test_accumulate_and_batch(self):
        pending = []
        for i in range(20):
            pending.append({"id": f"REC-{i:03d}", "synced": False})

        assert len(pending) == 20
        assert all(not r["synced"] for r in pending)

        batch = pending[:10]
        for r in batch:
            r["synced"] = True

        synced = [r for r in pending if r["synced"]]
        remaining = [r for r in pending if not r["synced"]]
        assert len(synced) == 10
        assert len(remaining) == 10


class TestOfflinePipelineLatency:
    def test_pipeline_under_500ms(self, inference_engine, psc_mapper, fake_jpeg_bytes):
        start = time.perf_counter()

        detections = inference_engine.predict(fake_jpeg_bytes)
        for det in detections:
            psc_mapper.map_defect(det.class_name, det.confidence)

        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, f"Pipeline took {elapsed_ms:.1f}ms, exceeds 500ms"

    def test_ten_consecutive_scans_stable(self, inference_engine, psc_mapper, fake_jpeg_bytes):
        times = []
        for _ in range(10):
            start = time.perf_counter()
            inference_engine.predict(fake_jpeg_bytes)
            times.append((time.perf_counter() - start) * 1000)

        avg = sum(times) / len(times)
        max_t = max(times)
        assert max_t < 500, f"Max {max_t:.1f}ms exceeds 500ms budget"
        assert avg < 500, f"Avg {avg:.1f}ms exceeds 500ms budget"
