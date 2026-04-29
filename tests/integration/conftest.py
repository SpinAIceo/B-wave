from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure proto stubs and ai_engine are importable
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "shared" / "gen" / "python"))
sys.path.insert(0, str(_root / "packages" / "ai-engine" / "src"))

from ai_engine.cargo.detector import CargoSecuringDetector
from ai_engine.inference.engine import InferenceEngine
from ai_engine.inference.psc_mapper import PSCCodeMapper
from ai_engine.inference.server import EdgeInferenceServiceServicer


def _make_jpeg(width: int = 640, height: int = 480) -> bytes:
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def fake_jpeg_bytes() -> bytes:
    return _make_jpeg()


@pytest.fixture()
def inference_engine() -> InferenceEngine:
    return InferenceEngine("nonexistent_model.onnx")


@pytest.fixture()
def psc_mapper() -> PSCCodeMapper:
    return PSCCodeMapper()


@pytest.fixture()
def cargo_detector(inference_engine: InferenceEngine) -> CargoSecuringDetector:
    return CargoSecuringDetector(inference_engine)


@pytest.fixture()
def grpc_servicer(inference_engine: InferenceEngine, psc_mapper: PSCCodeMapper):
    return EdgeInferenceServiceServicer(inference_engine, psc_mapper)
