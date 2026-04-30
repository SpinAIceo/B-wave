"""Pre-labeling Model (Paper Figure 5, steps e-f).

Provides approximate labels using a foundation model (Grounding DINO + SAM)
so that human reviewers correct rather than create labels from scratch.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .config import ALConfig


@dataclass
class PseudoLabel:
    x_center: float
    y_center: float
    width: float
    height: float
    class_id: int
    class_name: str
    confidence: float
    source: str  # "grounding_dino", "sam_refined", "al_model", "human"


@dataclass
class ConfidenceFilterResult:
    auto_approved: dict[str, list[PseudoLabel]]
    needs_review: dict[str, list[PseudoLabel]]
    discarded: dict[str, list[PseudoLabel]]
    stats: dict[str, int] = field(default_factory=dict)


class PreLabeler:
    def __init__(self, config: ALConfig):
        self._config = config
        self._gdino_model = None
        self._sam_model = None
        self._use_mock = True

    def load_models(self) -> None:
        try:
            self._load_grounding_dino()
            self._load_sam()
            self._use_mock = False
        except ImportError as e:
            raise RuntimeError(
                "Pre-labeling requires groundingdino and segment_anything. "
                "Install them or disable pre-labeling. "
                "Mock predictions are not allowed in production."
            ) from e

    def _load_grounding_dino(self) -> None:
        from groundingdino.util.inference import Model  # noqa: F401

        raise ImportError("Real Grounding DINO loading not yet wired")

    def _load_sam(self) -> None:
        from segment_anything import sam_model_registry  # noqa: F401

        raise ImportError("Real SAM loading not yet wired")

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_single(self, image_path: str) -> list[PseudoLabel]:
        if self._use_mock:
            return self._mock_predict(image_path)
        return self._real_predict(image_path)

    def predict_batch(
        self,
        image_paths: list[str],
        progress_callback=None,
    ) -> dict[str, list[PseudoLabel]]:
        results: dict[str, list[PseudoLabel]] = {}
        for i, path in enumerate(image_paths):
            results[path] = self.predict_single(path)
            if progress_callback:
                progress_callback(i + 1, len(image_paths))
        return results

    # ------------------------------------------------------------------
    # Confidence filtering
    # ------------------------------------------------------------------

    def filter_by_confidence(
        self, labels: dict[str, list[PseudoLabel]]
    ) -> ConfidenceFilterResult:
        approved: dict[str, list[PseudoLabel]] = {}
        review: dict[str, list[PseudoLabel]] = {}
        discarded: dict[str, list[PseudoLabel]] = {}
        counts = {"auto_approved": 0, "needs_review": 0, "discarded": 0}

        hi = self._config.confidence_threshold_auto
        lo = self._config.confidence_threshold_discard

        for path, pls in labels.items():
            for pl in pls:
                if pl.confidence >= hi:
                    approved.setdefault(path, []).append(pl)
                    counts["auto_approved"] += 1
                elif pl.confidence >= lo:
                    review.setdefault(path, []).append(pl)
                    counts["needs_review"] += 1
                else:
                    discarded.setdefault(path, []).append(pl)
                    counts["discarded"] += 1

        return ConfidenceFilterResult(
            auto_approved=approved,
            needs_review=review,
            discarded=discarded,
            stats=counts,
        )

    # ------------------------------------------------------------------
    # Real / mock implementations
    # ------------------------------------------------------------------

    def _real_predict(self, image_path: str) -> list[PseudoLabel]:
        raise NotImplementedError("Wire Grounding DINO + SAM here")

    def _mock_predict(self, image_path: str) -> list[PseudoLabel]:
        rng = random.Random(hash(image_path))
        n = rng.randint(0, 4)
        labels: list[PseudoLabel] = []
        for _ in range(n):
            cls_id = rng.randint(0, len(self._config.class_names) - 1)
            cx = rng.uniform(0.15, 0.85)
            cy = rng.uniform(0.15, 0.85)
            w = rng.uniform(0.05, 0.35)
            h = rng.uniform(0.05, 0.35)
            labels.append(
                PseudoLabel(
                    x_center=cx,
                    y_center=cy,
                    width=w,
                    height=h,
                    class_id=cls_id,
                    class_name=self._config.class_names[cls_id],
                    confidence=rng.uniform(0.15, 0.95),
                    source="grounding_dino_mock",
                )
            )
        return labels
