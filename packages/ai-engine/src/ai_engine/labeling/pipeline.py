"""Advanced Active Learning Pipeline orchestrator (Paper Figure 5).

Ties together all five techniques into a single run-loop:

    pipeline = AdvancedALPipeline(config)
    pipeline.initialize()
    pipeline.run_pre_labeling()

    for round in range(max_rounds):
        batch = pipeline.select_batch()
        pipeline.submit_human_labels(batch, human_labels)
        pipeline.train_al_model()
        if pipeline.should_stop():
            break

    pipeline.auto_label_remaining()
    pipeline.export_dataset()
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from .acquisition import BABAAcquisition
from .al_model import GPALModel
from .config import ALConfig
from .export import YOLOExporter
from .object_discovery import ObjectDiscovery
from .pre_labeler import PreLabeler, PseudoLabel
from .simclr_init import SimCLRInitializer


@dataclass
class RoundResult:
    round_number: int = 0
    batch_size: int = 0
    al_model_accuracy: float = 0.0
    total_labeled: int = 0
    total_images: int = 0
    auto_approved: int = 0
    needs_review: int = 0
    discarded: int = 0
    label_distribution: dict[str, int] = field(default_factory=dict)


@dataclass
class PipelineStatus:
    current_round: int = 0
    total_images: int = 0
    labeled_count: int = 0
    labeled_percent: float = 0.0
    al_model_accuracy: float = 0.0
    target_accuracy: float = 0.90
    estimated_rounds_remaining: int = 0
    class_distribution: dict[str, int] = field(default_factory=dict)
    history: list[RoundResult] = field(default_factory=list)


class AdvancedALPipeline:
    def __init__(self, config: ALConfig):
        self.config = config
        self.initializer = SimCLRInitializer(config)
        self.pre_labeler = PreLabeler(config)
        self.al_model = GPALModel(config)
        self.acquisition = BABAAcquisition(config)
        self.discovery = ObjectDiscovery(config)
        self.exporter = YOLOExporter(config)

        self._image_paths: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._cluster_labels: list[int] = []
        self._labels: dict[str, list[PseudoLabel]] = {}
        self._labeled_indices: set[int] = set()
        self._round: int = 0
        self._history: list[RoundResult] = []
        self._al_accuracy: float = 0.0

    # ------------------------------------------------------------------
    # Step 1: Initialize
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        img_dir = Path(self.config.image_dir)
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        self._image_paths = sorted(
            str(p) for p in img_dir.rglob("*") if p.suffix.lower() in exts
        )

        self._embeddings = self.initializer.compute_embeddings(self._image_paths)
        self._cluster_labels = self.initializer.cluster_images(self._embeddings)

    # ------------------------------------------------------------------
    # Step 2: Pre-label
    # ------------------------------------------------------------------

    def run_pre_labeling(self) -> None:
        self.pre_labeler.load_models()
        raw_labels = self.pre_labeler.predict_batch(self._image_paths)
        filtered = self.pre_labeler.filter_by_confidence(raw_labels)

        for path, pls in filtered.auto_approved.items():
            self._labels[path] = pls
            idx = self._image_paths.index(path)
            self._labeled_indices.add(idx)

        for path, pls in filtered.needs_review.items():
            self._labels.setdefault(path, []).extend(pls)

    # ------------------------------------------------------------------
    # Step 3: Select batch
    # ------------------------------------------------------------------

    def select_initial_batch(self) -> list[str]:
        return self.initializer.select_initial_batch(
            self._image_paths,
            self._embeddings,
            self._cluster_labels,
            self.config.initial_batch_size,
        )

    def select_batch(self) -> list[str]:
        if self._round == 0:
            return self.select_initial_batch()

        unlabeled = [
            i for i in range(len(self._image_paths)) if i not in self._labeled_indices
        ]
        if not unlabeled:
            return []

        emb_unlabeled = self._embeddings[unlabeled]
        preds, unc = self.al_model.predict(emb_unlabeled)

        batch_indices = self.acquisition.select_batch(
            preds,
            unc,
            emb_unlabeled,
            self.config.batch_size,
        )
        return [self._image_paths[unlabeled[i]] for i in batch_indices]

    # ------------------------------------------------------------------
    # Step 4: Receive human labels
    # ------------------------------------------------------------------

    def submit_human_labels(
        self,
        image_paths: list[str],
        labels: dict[str, list[PseudoLabel]],
    ) -> None:
        for path, pls in labels.items():
            self._labels[path] = pls
            if path in self._image_paths:
                idx = self._image_paths.index(path)
                self._labeled_indices.add(idx)

    # ------------------------------------------------------------------
    # Step 5: Train AL model
    # ------------------------------------------------------------------

    def train_al_model(self) -> float:
        labeled_idx = sorted(self._labeled_indices)
        if len(labeled_idx) < 5:
            return 0.0

        embs = self._embeddings[labeled_idx]
        y = np.array([
            self._primary_class(self._image_paths[i]) for i in labeled_idx
        ])

        split = max(1, int(len(labeled_idx) * 0.8))
        self.al_model.fit(embs[:split], y[:split])
        self._al_accuracy = self.al_model.get_accuracy(embs[split:], y[split:])
        self._round += 1

        self._history.append(
            RoundResult(
                round_number=self._round,
                batch_size=self.config.batch_size,
                al_model_accuracy=self._al_accuracy,
                total_labeled=len(self._labeled_indices),
                total_images=len(self._image_paths),
                label_distribution=self._class_distribution(),
            )
        )
        return self._al_accuracy

    # ------------------------------------------------------------------
    # Step 6: Stop check
    # ------------------------------------------------------------------

    def should_stop(self) -> bool:
        if self._round >= self.config.max_rounds:
            return True
        if self._al_accuracy >= self.config.target_accuracy:
            return True
        if len(self._labeled_indices) >= len(self._image_paths):
            return True
        return False

    # ------------------------------------------------------------------
    # Step 7: Auto-label remaining
    # ------------------------------------------------------------------

    def auto_label_remaining(self) -> int:
        unlabeled = [
            i for i in range(len(self._image_paths)) if i not in self._labeled_indices
        ]
        if not unlabeled:
            return 0

        emb = self._embeddings[unlabeled]
        result = self.al_model.auto_label(emb, threshold=self.config.target_accuracy)

        count = 0
        for rel_idx, cls_id in zip(result.labeled_indices, result.predicted_labels):
            abs_idx = unlabeled[rel_idx]
            path = self._image_paths[abs_idx]
            if path not in self._labels:
                self._labels[path] = []
            self._labels[path].append(
                PseudoLabel(
                    x_center=0.5,
                    y_center=0.5,
                    width=0.3,
                    height=0.3,
                    class_id=cls_id,
                    class_name=self.config.class_names[cls_id],
                    confidence=result.confidences[result.labeled_indices.index(rel_idx)],
                    source="al_model",
                )
            )
            self._labeled_indices.add(abs_idx)
            count += 1

        return count

    # ------------------------------------------------------------------
    # Step 8: Export
    # ------------------------------------------------------------------

    def export_dataset(self, output_dir: str | None = None) -> str:
        out = output_dir or self.config.output_dir
        return self.exporter.export(self._labels, out)

    # ------------------------------------------------------------------
    # Status / persistence
    # ------------------------------------------------------------------

    def get_status(self) -> PipelineStatus:
        total = len(self._image_paths)
        labeled = len(self._labeled_indices)
        return PipelineStatus(
            current_round=self._round,
            total_images=total,
            labeled_count=labeled,
            labeled_percent=labeled / max(total, 1) * 100,
            al_model_accuracy=self._al_accuracy,
            target_accuracy=self.config.target_accuracy,
            estimated_rounds_remaining=max(0, self.config.max_rounds - self._round),
            class_distribution=self._class_distribution(),
            history=list(self._history),
        )

    def save_state(self, path: str) -> None:
        state = {
            "round": self._round,
            "labeled_indices": sorted(self._labeled_indices),
            "al_accuracy": self._al_accuracy,
            "history": [asdict(r) for r in self._history],
            "labels": {
                p: [asdict(pl) for pl in pls] for p, pls in self._labels.items()
            },
        }
        Path(path).write_text(json.dumps(state, indent=2))

    def load_state(self, path: str) -> None:
        state = json.loads(Path(path).read_text())
        self._round = state["round"]
        self._labeled_indices = set(state["labeled_indices"])
        self._al_accuracy = state["al_accuracy"]
        self._history = [RoundResult(**r) for r in state["history"]]
        self._labels = {
            p: [PseudoLabel(**pl) for pl in pls]
            for p, pls in state["labels"].items()
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _primary_class(self, image_path: str) -> int:
        pls = self._labels.get(image_path, [])
        if not pls:
            return 0
        best = max(pls, key=lambda p: p.confidence)
        return best.class_id

    def _class_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for pls in self._labels.values():
            for pl in pls:
                dist[pl.class_name] = dist.get(pl.class_name, 0) + 1
        return dist
