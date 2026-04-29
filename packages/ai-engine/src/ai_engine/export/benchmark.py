from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class BenchmarkResult:
    avg_inference_ms: float
    min_inference_ms: float
    max_inference_ms: float
    throughput_fps: float
    memory_mb: float
    model_size_mb: float
    runtime: str


def benchmark_model(
    model_path: str | Path,
    num_iterations: int = 100,
    image_size: int = 640,
    warmup: int = 5,
) -> BenchmarkResult:
    """Measure inference performance for ONNX or PyTorch models."""
    model_path = Path(model_path)
    model_size_mb = model_path.stat().st_size / (1024 * 1024)

    if model_path.suffix == ".onnx":
        return _benchmark_onnx(model_path, num_iterations, image_size, warmup, model_size_mb)
    return _benchmark_pytorch(model_path, num_iterations, image_size, warmup, model_size_mb)


def _benchmark_onnx(
    model_path: Path,
    num_iterations: int,
    image_size: int,
    warmup: int,
    model_size_mb: float,
) -> BenchmarkResult:
    import onnxruntime as ort
    import psutil

    session = ort.InferenceSession(
        str(model_path),
        providers=["CPUExecutionProvider"],
    )
    input_name = session.get_inputs()[0].name
    dummy = np.random.rand(1, 3, image_size, image_size).astype(np.float32)

    for _ in range(warmup):
        session.run(None, {input_name: dummy})

    process = psutil.Process()
    mem_before = process.memory_info().rss

    times: list[float] = []
    for _ in range(num_iterations):
        start = time.perf_counter()
        session.run(None, {input_name: dummy})
        times.append((time.perf_counter() - start) * 1000)

    mem_after = process.memory_info().rss
    memory_mb = (mem_after - mem_before) / (1024 * 1024)

    return BenchmarkResult(
        avg_inference_ms=float(np.mean(times)),
        min_inference_ms=float(np.min(times)),
        max_inference_ms=float(np.max(times)),
        throughput_fps=1000.0 / float(np.mean(times)),
        memory_mb=max(0.0, memory_mb),
        model_size_mb=model_size_mb,
        runtime="onnxruntime",
    )


def _benchmark_pytorch(
    model_path: Path,
    num_iterations: int,
    image_size: int,
    warmup: int,
    model_size_mb: float,
) -> BenchmarkResult:
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    dummy = np.random.randint(0, 255, (image_size, image_size, 3), dtype=np.uint8)

    for _ in range(warmup):
        model.predict(dummy, verbose=False)

    times: list[float] = []
    for _ in range(num_iterations):
        start = time.perf_counter()
        model.predict(dummy, verbose=False)
        times.append((time.perf_counter() - start) * 1000)

    return BenchmarkResult(
        avg_inference_ms=float(np.mean(times)),
        min_inference_ms=float(np.min(times)),
        max_inference_ms=float(np.max(times)),
        throughput_fps=1000.0 / float(np.mean(times)),
        memory_mb=0.0,
        model_size_mb=model_size_mb,
        runtime="pytorch",
    )
