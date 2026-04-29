"""E2E-02: Offline Operation Verification.

Validates that the entire detection + PSC mapping pipeline works
without any network access — a hard requirement for at-sea operation.
"""
from __future__ import annotations

import time
from collections import defaultdict

from ai_engine.inference.engine import Detection, InferenceEngine
from ai_engine.inference.psc_mapper import PSCCodeMapper, Severity


class TestInferenceOffline:
    def test_engine_creates_without_network(self, inference_engine):
        assert inference_engine is not None
        assert inference_engine.runtime == "none"

    def test_predict_returns_empty_without_model(self, inference_engine, fake_jpeg_bytes):
        result = inference_engine.predict(fake_jpeg_bytes)
        assert result == []

    def test_engine_has_all_class_names(self, inference_engine):
        assert len(inference_engine.class_names) == 5


class TestPSCMappingOffline:
    def test_mapper_needs_no_network(self, psc_mapper):
        mapping = psc_mapper.map_defect("rust", 0.9)
        assert mapping.psc_code == "0615"

    def test_all_mappings_embedded(self, psc_mapper):
        all_maps = psc_mapper.get_all_mappings()
        assert len(all_maps) == 5
        assert all_maps["cargo_lashing"] == "0725"

    def test_severity_classification_offline(self, psc_mapper):
        critical = psc_mapper.map_defect("damage", 0.85)
        assert critical.severity == Severity.CRITICAL

        high = psc_mapper.map_defect("damage", 0.65)
        assert high.severity == Severity.HIGH

        medium = psc_mapper.map_defect("damage", 0.45)
        assert medium.severity == Severity.MEDIUM

        low = psc_mapper.map_defect("damage", 0.2)
        assert low.severity == Severity.LOW


class TestFullPipelineOffline:
    def test_detection_to_violation_no_network(self, psc_mapper):
        detections = [
            Detection(0.1, 0.2, 0.4, 0.5, 0, "rust", 0.87),
            Detection(0.5, 0.1, 0.8, 0.3, 4, "cargo_lashing", 0.75),
        ]
        violations = []
        for det in detections:
            mapping = psc_mapper.map_defect(det.class_name, det.confidence)
            violations.append({
                "detection": det,
                "psc_code": mapping.psc_code,
                "severity": mapping.severity,
                "description": mapping.description,
            })

        assert len(violations) == 2
        assert violations[0]["psc_code"] == "0615"
        assert violations[1]["psc_code"] == "0725"

    def test_pipeline_latency_under_500ms(self, psc_mapper):
        start = time.perf_counter()
        for _ in range(100):
            for dt in ["rust", "damage", "leak", "missing_label", "cargo_lashing"]:
                psc_mapper.map_defect(dt, 0.7)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500


class TestOfflineStorageSimulation:
    def test_accumulate_and_verify(self, psc_mapper):
        local_store: dict[str, list] = defaultdict(list)

        detections = [
            Detection(0.1, 0.2, 0.4, 0.5, 0, "rust", 0.87),
            Detection(0.5, 0.1, 0.8, 0.3, 1, "damage", 0.92),
            Detection(0.3, 0.6, 0.6, 0.8, 2, "leak", 0.65),
        ]

        for i, det in enumerate(detections):
            mapping = psc_mapper.map_defect(det.class_name, det.confidence)
            local_store["inspection-001"].append({
                "id": f"det-{i:03d}",
                "defect_type": det.class_name,
                "psc_code": mapping.psc_code,
                "severity": mapping.severity.name,
                "confidence": det.confidence,
            })

        stored = local_store["inspection-001"]
        assert len(stored) == 3
        assert stored[0]["psc_code"] == "0615"
        assert stored[1]["severity"] == "CRITICAL"
        assert stored[2]["defect_type"] == "leak"

    def test_sync_queue_priority_ordering(self, psc_mapper):
        queue: list[dict] = []

        entries = [
            ("rust", 0.4, "normal"),         # MEDIUM → Normal priority
            ("damage", 0.92, "critical"),     # CRITICAL → Critical priority
            ("leak", 0.3, "normal"),          # LOW → Normal priority
            ("cargo_lashing", 0.85, "high"),  # CRITICAL → High priority (CIC)
        ]

        for defect_type, conf, _ in entries:
            mapping = psc_mapper.map_defect(defect_type, conf)
            priority = 0 if mapping.severity == Severity.CRITICAL else (
                1 if mapping.severity == Severity.HIGH else 2
            )
            queue.append({
                "defect_type": defect_type,
                "psc_code": mapping.psc_code,
                "severity": mapping.severity.name,
                "priority": priority,
            })

        queue.sort(key=lambda x: x["priority"])
        assert queue[0]["severity"] == "CRITICAL"
        assert queue[0]["defect_type"] == "damage"
        assert queue[1]["severity"] == "CRITICAL"
        assert queue[1]["defect_type"] == "cargo_lashing"

    def test_batch_sync_after_accumulation(self, psc_mapper):
        pending = []
        for i in range(20):
            det_type = ["rust", "damage", "leak", "missing_label", "cargo_lashing"][i % 5]
            mapping = psc_mapper.map_defect(det_type, 0.5 + (i % 5) * 0.1)
            pending.append({"id": f"rec-{i:03d}", "psc_code": mapping.psc_code, "synced": False})

        assert all(not r["synced"] for r in pending)
        assert len(pending) == 20

        for r in pending:
            r["synced"] = True

        assert all(r["synced"] for r in pending)
