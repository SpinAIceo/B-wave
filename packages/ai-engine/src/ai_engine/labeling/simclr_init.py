"""SimCLR-based Unsupervised Initialization (Paper Figure 5, steps b-c).

Embeds images into a latent space via a pretrained ResNet backbone,
clusters them with K-Means, and selects a maximally diverse initial
batch so the first round of human labeling covers as many visual
modes as possible.
"""

from __future__ import annotations

import math
import random

import numpy as np

from .config import ALConfig


class SimCLRInitializer:
    def __init__(self, config: ALConfig):
        self._config = config
        self._cluster_labels: np.ndarray | None = None
        self._cluster_counts: dict[int, int] = {}

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def compute_embeddings(self, image_paths: list[str]) -> np.ndarray:
        """Extract embeddings using a pretrained ResNet backbone.

        Falls back to random embeddings when torch/torchvision are absent
        so that the rest of the pipeline can still be tested.
        """
        try:
            return self._compute_embeddings_torch(image_paths)
        except ImportError:
            return self._compute_embeddings_fallback(image_paths)

    def _compute_embeddings_torch(self, image_paths: list[str]) -> np.ndarray:
        import torch
        from torchvision import models, transforms

        weights_attr = f"resnet{self._config.simclr_backbone.replace('resnet', '')}"
        backbone = getattr(models, weights_attr)(weights="DEFAULT")
        backbone.fc = torch.nn.Identity()
        backbone.eval()

        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

        from PIL import Image

        embeddings = []
        with torch.no_grad():
            for p in image_paths:
                img = Image.open(p).convert("RGB")
                tensor = transform(img).unsqueeze(0)
                emb = backbone(tensor).squeeze(0).numpy()
                emb = emb / (np.linalg.norm(emb) + 1e-8)
                embeddings.append(emb)

        out = np.stack(embeddings)
        if out.shape[1] != self._config.simclr_embedding_dim:
            proj = np.random.RandomState(42).randn(
                out.shape[1], self._config.simclr_embedding_dim
            )
            out = out @ proj
            norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-8
            out = out / norms
        return out

    def _compute_embeddings_fallback(self, image_paths: list[str]) -> np.ndarray:
        rng = np.random.RandomState(42)
        emb = rng.randn(len(image_paths), self._config.simclr_embedding_dim)
        norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8
        return emb / norms

    # ------------------------------------------------------------------
    # Clustering
    # ------------------------------------------------------------------

    def cluster_images(self, embeddings: np.ndarray) -> list[int]:
        try:
            from sklearn.cluster import KMeans
        except ImportError:
            return self._cluster_fallback(embeddings)

        k = min(self._config.num_clusters, len(embeddings))
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(embeddings)
        self._cluster_labels = labels
        self._cluster_counts = {
            int(c): int((labels == c).sum()) for c in range(k)
        }
        return labels.tolist()

    def _cluster_fallback(self, embeddings: np.ndarray) -> list[int]:
        k = min(self._config.num_clusters, len(embeddings))
        labels = np.array([i % k for i in range(len(embeddings))])
        self._cluster_labels = labels
        self._cluster_counts = {
            int(c): int((labels == c).sum()) for c in range(k)
        }
        return labels.tolist()

    # ------------------------------------------------------------------
    # Diverse batch selection
    # ------------------------------------------------------------------

    def select_initial_batch(
        self,
        image_paths: list[str],
        embeddings: np.ndarray,
        cluster_labels: list[int],
        batch_size: int,
    ) -> list[str]:
        labels_arr = np.asarray(cluster_labels)
        unique_clusters = sorted(set(cluster_labels))
        per_cluster = max(1, math.ceil(batch_size / len(unique_clusters)))

        selected: list[int] = []
        rng = random.Random(42)

        for c in unique_clusters:
            indices = np.where(labels_arr == c)[0].tolist()
            rng.shuffle(indices)
            selected.extend(indices[:per_cluster])

        rng.shuffle(selected)
        selected = selected[:batch_size]
        return [image_paths[i] for i in selected]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_cluster_distribution(self) -> dict[int, int]:
        return dict(self._cluster_counts)
