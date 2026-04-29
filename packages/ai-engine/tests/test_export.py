import inspect

from ai_engine.export.benchmark import BenchmarkResult, benchmark_model
from ai_engine.export.onnx_export import export_to_onnx


class TestExportSignatures:
    def test_export_to_onnx_signature(self):
        sig = inspect.signature(export_to_onnx)
        params = list(sig.parameters.keys())
        assert "model_path" in params
        assert "output_path" in params
        assert "image_size" in params
        assert "opset" in params

    def test_benchmark_model_signature(self):
        sig = inspect.signature(benchmark_model)
        params = list(sig.parameters.keys())
        assert "model_path" in params
        assert "num_iterations" in params
        assert "image_size" in params

    def test_benchmark_result_fields(self):
        result = BenchmarkResult(
            avg_inference_ms=10.0,
            min_inference_ms=8.0,
            max_inference_ms=12.0,
            throughput_fps=100.0,
            memory_mb=50.0,
            model_size_mb=25.0,
            runtime="onnxruntime",
        )
        assert result.avg_inference_ms == 10.0
        assert result.runtime == "onnxruntime"
