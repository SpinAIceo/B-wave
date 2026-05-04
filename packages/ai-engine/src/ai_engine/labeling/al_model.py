"""Gaussian Process Active Learning Model (Paper Figure 5, AL model step).

Trains a GP classifier on SimCLR embeddings of labeled images and uses
the calibrated posterior to (a) estimate uncertainty for acquisition and
(b) auto-label high-confidence predictions.  GP handles class imbalance
better than most discriminative models.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import ALConfig


@dataclass
class AutoLabelResult:
    labeled_indices: list[int] = field(default_factory=list)
    predicted_labels: list[int] = field(default_factory=list)
    confidences: list[float] = field(default_factory=list)
    unlabeled_indices: list[int] = field(default_factory=list)


class GPALModel:
    def __init__(self, config: ALConfig):
        self._config = config
        self._model = None
        self._fitted = False

    # ------------------------------------------------------------------

    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> None:
        try:
            from sklearn.gaussian_process import GaussianProcessClassifier
            from sklearn.gaussian_process.kernels import RBF
        except ImportError:
            self._fit_fallback(embeddings, labels)
            return

        kernel = RBF(length_scale=self._config.gp_length_scale)
        self._model = GaussianProcessClassifier(
            kernel=kernel, random_state=42, max_iter_predict=50
        )
        self._model.fit(embeddings, labels)
        self._fitted = True

    def _fit_fallback(self, embeddings: np.ndarray, labels: np.ndarray) -> None:
        self._fallback_centroids: dict[int, np.ndarray] = {}
        for c in np.unique(labels):
            self._fallback_centroids[int(c)] = embeddings[labels == c].mean(axis=0)
        self._fitted = True

    # ------------------------------------------------------------------

    def predict(
        self, embeddings: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        if not self._fitted:
            return (
                np.zeros(len(embeddings), dtype=int),
                np.ones(len(embeddings)),
            )

        if self._model is not None:
            preds = self._model.predict(embeddings)
            probs = self._model.predict_proba(embeddings)
            uncertainty = 1.0 - probs.max(axis=1)
            return preds, uncertainty

        return self._predict_fallback(embeddings)

    def _predict_fallback(
        self, embeddings: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        preds = []
        uncertainties = []
        for emb in embeddings:
            dists = {
                c: float(np.linalg.norm(emb - cent))
                for c, cent in self._fallback_centroids.items()
            }
            best = min(dists, key=dists.get)  # type: ignore[arg-type]
            min_dist = dists[best]
            uncertainty = 1.0 - np.exp(-min_dist)
            preds.append(best)
            uncertainties.append(float(uncertainty))
        return np.array(preds), np.array(uncertainties)

    # ------------------------------------------------------------------

    def get_accuracy(
        self, test_embeddings: np.ndarray, test_labels: np.ndarray
    ) -> float:
        preds, _ = self.predict(test_embeddings)
        return float((preds == test_labels).mean())

    # ------------------------------------------------------------------

    def auto_label(
        self, embeddings: np.ndarray, threshold: float = 0.9
    ) -> AutoLabelResult:
        preds, uncertainty = self.predict(embeddings)
        confidence = 1.0 - uncertainty

        labeled_idx = []
        labeled_preds = []
        labeled_conf = []
        unlabeled_idx = []

        for i in range(len(embeddings)):
            if confidence[i] >= threshold:
                labeled_idx.append(i)
                labeled_preds.append(int(preds[i]))
                labeled_conf.append(float(confidence[i]))
            else:
                unlabeled_idx.append(i)

        return AutoLabelResult(
            labeled_indices=labeled_idx,
            predicted_labels=labeled_preds,
            confidences=labeled_conf,
            unlabeled_indices=unlabeled_idx,
        )
