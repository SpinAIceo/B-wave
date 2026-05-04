from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from ai_engine.labeling.config import ALConfig  # noqa: E402
from ai_engine.labeling.pre_labeler import PseudoLabel  # noqa: E402


@pytest.fixture()
def tmp_image_dir(tmp_path: Path) -> str:
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    for i in range(20):
        img = Image.new("RGB", (640, 480), color=(i * 10, 50, 100))
        img.save(img_dir / f"img_{i:03d}.jpg")
    return str(img_dir)


@pytest.fixture()
def tmp_output_dir(tmp_path: Path) -> str:
    out = tmp_path / "output"
    out.mkdir()
    return str(out)


@pytest.fixture()
def al_config(tmp_image_dir: str, tmp_output_dir: str) -> ALConfig:
    return ALConfig(
        image_dir=tmp_image_dir,
        output_dir=tmp_output_dir,
        num_clusters=4,
        initial_batch_size=5,
        batch_size=3,
        max_rounds=3,
        target_accuracy=0.85,
    )


@pytest.fixture()
def random_embeddings() -> np.ndarray:
    rng = np.random.RandomState(42)
    emb = rng.randn(20, 128).astype(np.float32)
    norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8
    return emb / norms


@pytest.fixture()
def sample_labels() -> dict[str, list[PseudoLabel]]:
    return {
        f"img_{i:03d}.jpg": [
            PseudoLabel(
                x_center=0.5,
                y_center=0.5,
                width=0.3,
                height=0.3,
                class_id=i % 5,
                class_name=["rust", "damage", "leak", "missing_label", "cargo_lashing"][
                    i % 5
                ],
                confidence=0.5 + (i % 5) * 0.1,
                source="mock",
            )
        ]
        for i in range(10)
    }
