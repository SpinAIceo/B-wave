"""
Benchmark inference latency across model variants on a folder of images.

Why this exists:
    After running export_optimized.py you'll have multiple model artifacts
    side-by-side (best.pt, best.onnx, best.engine, best_int8.engine).
    Before promoting one to production you want to know:
      - How much faster is it really?
      - Did precision reduction cost you accuracy (mAP-style metric)?

What this measures:
    - Wall-clock latency per image (median, p95, p99) over N runs.
    - Detection-count agreement between FP32 baseline and the variant
      (a rough proxy for "did INT8 break things?"). NOT a full mAP run.

Usage:
    python -m ai_engine.scripts.bench_latency \
        --models runs/exp1/weights/best.pt runs/exp1/weights/best.engine \
        --images data/unified/val/images \
        --runs 100 --warmup 20 --imgsz 640
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(pct / 100 * len(s))))
    return s[k]


def bench(model_path: Path, images: list[Path], imgsz: int, runs: int, warmup: int):
    from ultralytics import YOLO
    import torch

    print(f"\n=== {model_path.name} ===")
    model = YOLO(str(model_path))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and model_path.suffix == ".pt":
        model.to("cuda")
        try:
            model.model.half()
            print(f"  device={device} (FP16)")
        except Exception:
            print(f"  device={device} (FP32 — half failed)")
    else:
        print(f"  device={device}  format={model_path.suffix}")

    # Warmup — JIT, CUDA stream, TensorRT engine load.
    for img in images[:warmup]:
        model.predict(str(img), conf=0.05, verbose=False, device=device, imgsz=imgsz)
    if device == "cuda":
        torch.cuda.synchronize()

    # Measure
    latencies: list[float] = []
    raw_counts: list[int] = []
    for i in range(runs):
        img = images[i % len(images)]
        t0 = time.perf_counter()
        results = model.predict(
            str(img), conf=0.05, verbose=False, device=device, imgsz=imgsz
        )
        if device == "cuda":
            torch.cuda.synchronize()
        latencies.append((time.perf_counter() - t0) * 1000)
        raw_counts.append(sum(len(r.boxes) for r in results if r.boxes is not None))

    print(f"  runs={runs}  warmup={warmup}  imgsz={imgsz}")
    print(f"  latency: median={statistics.median(latencies):.2f}ms  "
          f"mean={statistics.mean(latencies):.2f}ms  "
          f"p95={_percentile(latencies, 95):.2f}ms  "
          f"p99={_percentile(latencies, 99):.2f}ms  "
          f"min={min(latencies):.2f}ms  max={max(latencies):.2f}ms")
    print(f"  detections: total={sum(raw_counts)}  avg/img={statistics.mean(raw_counts):.2f}")
    return {
        "model": model_path.name,
        "median_ms": statistics.median(latencies),
        "p95_ms": _percentile(latencies, 95),
        "total_detections": sum(raw_counts),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", type=Path, required=True,
                    help="paths to model files to benchmark")
    ap.add_argument("--images", required=True, type=Path,
                    help="directory of test images")
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    if not args.images.exists():
        print(f"ERROR: images dir not found: {args.images}")
        return 1

    images = (sorted(args.images.glob("*.jpg")) +
              sorted(args.images.glob("*.png")))[: args.runs + args.warmup]
    if not images:
        print(f"ERROR: no images in {args.images}")
        return 1
    print(f"Using {len(images)} images for warmup ({args.warmup}) + runs ({args.runs})")

    results = []
    for m in args.models:
        if not m.exists():
            print(f"  SKIP {m} — not found")
            continue
        results.append(bench(m, images, args.imgsz, args.runs, args.warmup))

    # Comparison table
    if len(results) > 1:
        baseline = results[0]
        print("\n=== Comparison (relative to first model) ===")
        print(f"{'Model':<30} {'median (ms)':<15} {'p95 (ms)':<12} {'speedup':<10} {'det count':<10}")
        for r in results:
            speedup = baseline["median_ms"] / r["median_ms"] if r["median_ms"] > 0 else 0
            print(f"{r['model']:<30} {r['median_ms']:<15.2f} {r['p95_ms']:<12.2f} "
                  f"{speedup:<10.2f}x {r['total_detections']:<10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
