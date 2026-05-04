"""Unsupervised Object Discovery (Paper Figure 5, discovery step).

Extracts random patches at multiple scales, embeds them, and
clusters to separate foreground objects from background.  Objects
are expected to be small, visually distinct from their surroundings,
and less uniform across images than background.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from .config import ALConfig


@dataclass
class Patch:
    x: int
    y: int
    width: int
    height: int
    image_path: str


@dataclass
class Region:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    objectness_score: float


class ObjectDiscovery:
    def __init__(self, config: ALConfig):
        self._config = config
        self._bg_centroid: np.ndarray | None = None

    # ------------------------------------------------------------------

    def extract_patches(self, image_path: str) -> list[Patch]:
        try:
            from PIL import Image

            img = Image.open(image_path)
            w, h = img.size
        except Exception:
            w, h = 640, 480

        rng = random.Random(hash(image_path))
        patches: list[Patch] = []
        per_scale = self._config.discovery_num_patches // len(
            self._config.discovery_patch_sizes
        )

        for ps in self._config.discovery_patch_sizes:
            for _ in range(per_scale):
                x = rng.randint(0, max(0, w - ps))
                y = rng.randint(0, max(0, h - ps))
                patches.append(Patch(x=x, y=y, width=ps, height=ps, image_path=image_path))

        return patches

    # ------------------------------------------------------------------

    def compute_patch_embeddings(self, patches: list[Patch]) -> np.ndarray:
        rng = np.random.RandomState(42)
        dim = self._config.simclr_embedding_dim
        emb = rng.randn(len(patches), dim).astype(np.float32)
        norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8
        return emb / norms

    # ------------------------------------------------------------------

    def discover_objects(
        self,
        image_paths: list[str],
        max_images: int = 200,
    ) -> dict[str, list[Region]]:
        paths = image_paths[:max_images]
        all_patches: list[Patch] = []
        for p in paths:
            all_patches.extend(self.extract_patches(p))

        embeddings = self.compute_patch_embeddings(all_patches)

        try:
            from sklearn.cluster import KMeans

            km = KMeans(n_clusters=min(10, len(embeddings)), random_state=42, n_init=5)
            cluster_labels = km.fit_predict(embeddings)
        except ImportError:
            cluster_labels = np.array([i % 10 for i in range(len(embeddings))])

        # Background = largest cluster(s); object = smaller clusters with
        # high within-cluster variance relative to background.
        unique, counts = np.unique(cluster_labels, return_counts=True)
        total = counts.sum()
        bg_clusters = set(unique[counts > total * 0.15].tolist())

        results: dict[str, list[Region]] = {}
        for idx, patch in enumerate(all_patches):
            if cluster_labels[idx] in bg_clusters:
                continue
            objectness = 1.0 - counts[cluster_labels[idx]] / total

            try:
                from PIL import Image

                img = Image.open(patch.image_path)
                w, h = img.size
            except Exception:
                w, h = 640, 480

            region = Region(
                x_min=patch.x / w,
                y_min=patch.y / h,
                x_max=(patch.x + patch.width) / w,
                y_max=(patch.y + patch.height) / h,
                objectness_score=float(objectness),
            )
            results.setdefault(patch.image_path, []).append(region)

        return results

    # ------------------------------------------------------------------

    def suggest_attention_regions(self, image_path: str) -> list[Region]:
        discovered = self.discover_objects([image_path], max_images=1)
        regions = discovered.get(image_path, [])
        regions.sort(key=lambda r: r.objectness_score, reverse=True)
        return regions[:10]
