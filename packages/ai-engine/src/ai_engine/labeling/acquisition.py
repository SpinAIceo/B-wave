"""BABA Acquisition Function (Paper Figure 5, acquisition step).

Beta Approximation for Bayesian Active Learning.  Models prediction
uncertainty with a Beta distribution and selects samples that
maximise expected information gain (KL divergence).  Combined with
diversity-aware greedy selection to avoid redundant batches.
"""

from __future__ import annotations

import numpy as np
from scipy import special as sp

from .config import ALConfig


class BABAAcquisition:
    def __init__(self, config: ALConfig):
        self.alpha_prior = config.baba_alpha_prior
        self.beta_prior = config.baba_beta_prior

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score(
        self,
        predictions: np.ndarray,
        uncertainties: np.ndarray,
    ) -> np.ndarray:
        """Compute per-sample BABA information-gain score.

        Higher score → more informative → label first.
        """
        n = len(predictions)
        scores = np.zeros(n)

        for i in range(n):
            p = 1.0 - uncertainties[i]
            p = np.clip(p, 0.01, 0.99)

            alpha = self.alpha_prior + p * 10
            beta = self.beta_prior + (1 - p) * 10

            # Expected information gain = entropy of Beta posterior
            entropy = (
                sp.betaln(alpha, beta)
                - (alpha - 1) * sp.digamma(alpha)
                - (beta - 1) * sp.digamma(beta)
                + (alpha + beta - 2) * sp.digamma(alpha + beta)
            )
            scores[i] = entropy + uncertainties[i]

        return scores

    # ------------------------------------------------------------------
    # Batch selection (BABA + diversity)
    # ------------------------------------------------------------------

    def select_batch(
        self,
        predictions: np.ndarray,
        uncertainties: np.ndarray,
        embeddings: np.ndarray,
        batch_size: int,
        already_labeled: set[int] | None = None,
    ) -> list[int]:
        if already_labeled is None:
            already_labeled = set()

        scores = self.score(predictions, uncertainties)
        candidates = [i for i in range(len(scores)) if i not in already_labeled]

        if not candidates:
            return []

        selected: list[int] = []
        remaining = set(candidates)
        min_dist_threshold = 0.1

        while len(selected) < batch_size and remaining:
            best_idx = max(remaining, key=lambda i: scores[i])
            selected.append(best_idx)
            remaining.discard(best_idx)

            # Remove candidates that are too similar (diversity enforcement)
            too_close = set()
            for idx in remaining:
                dist = float(
                    np.linalg.norm(
                        embeddings[best_idx] - embeddings[idx]
                    )
                )
                if dist < min_dist_threshold:
                    too_close.add(idx)
            remaining -= too_close

        return selected

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @staticmethod
    def compare_with_random(
        scores: np.ndarray, batch_size: int
    ) -> dict[str, float]:
        rng = np.random.RandomState(42)
        sorted_indices = np.argsort(-scores)
        baba_top = sorted_indices[:batch_size]
        random_top = rng.choice(len(scores), size=batch_size, replace=False)

        return {
            "baba_mean_score": float(scores[baba_top].mean()),
            "random_mean_score": float(scores[random_top].mean()),
            "improvement_ratio": float(
                scores[baba_top].mean() / (scores[random_top].mean() + 1e-8)
            ),
        }
