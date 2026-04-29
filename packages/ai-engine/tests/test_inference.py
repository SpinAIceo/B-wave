import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared" / "gen" / "python"))

from ai_engine.inference.server import EdgeInferenceServiceServicer


def test_servicer_loads():
    servicer = EdgeInferenceServiceServicer()
    assert servicer is not None
