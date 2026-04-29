from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure proto stubs and src are importable
_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_root / "shared" / "gen" / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def fake_jpeg_bytes() -> bytes:
    """Generate a random 640x480 JPEG image as bytes."""
    arr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def fake_small_jpeg_bytes() -> bytes:
    """Generate a small 64x64 JPEG for fast tests."""
    arr = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
