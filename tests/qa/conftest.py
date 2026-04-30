"""Shared fixtures for QA tests."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT / "packages" / "ai-engine" / "src"))
sys.path.insert(0, str(ROOT / "shared" / "gen" / "python"))
sys.path.insert(0, str(ROOT / "packages" / "fleet-view" / "backend" / "src"))


@pytest.fixture()
def fake_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (640, 480), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def fleet_client():
    from fastapi.testclient import TestClient

    from fleet_backend.main import app

    return TestClient(app)


@pytest.fixture()
def inference_engine():
    from ai_engine.inference.engine import InferenceEngine

    return InferenceEngine("nonexistent_model.onnx")


@pytest.fixture()
def psc_mapper():
    from ai_engine.inference.psc_mapper import PSCCodeMapper

    return PSCCodeMapper()


@pytest.fixture()
def cargo_detector(inference_engine):
    from ai_engine.cargo.detector import CargoSecuringDetector

    return CargoSecuringDetector(inference_engine)


class _MockContext:
    """Mock gRPC context for testing servicer methods."""

    def __init__(self):
        self.code = None
        self.details = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details


@pytest.fixture()
def mock_grpc_context():
    return _MockContext()


@pytest.fixture()
def grpc_servicer():
    from ai_engine.inference.engine import InferenceEngine
    from ai_engine.inference.psc_mapper import PSCCodeMapper
    from ai_engine.inference.server import EdgeInferenceServiceServicer

    engine = InferenceEngine("nonexistent.onnx")
    mapper = PSCCodeMapper()
    return EdgeInferenceServiceServicer(engine, mapper)
