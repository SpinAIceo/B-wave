"""
Export a trained YOLO checkpoint to optimized inference formats.

Why this exists:
    YOLO is a CNN — there's no KV cache. The wins for inference latency
    come from precision reduction (FP16 / INT8) and graph compilation
    (TensorRT). On an RTX 4090 we typically see:

        FP32 PT             ~9–12 ms / image  (baseline)
        FP16 ONNX           ~5–7 ms
        FP16 TensorRT       ~3–4 ms          (← edge-server target)
        INT8 TensorRT       ~2–3 ms          (− calibration data)

Usage:
    python -m ai_engine.scripts.export_optimized \
        --model runs/exp1/weights/best.pt \
        --imgsz 640 \
        --formats onnx,engine,int8 \
        --calib-data data/unified/val/images   # only needed for int8

Outputs are written next to the input model with suffixes:
    best.pt              (input)
    best.onnx            (FP16 ONNX, runs anywhere with onnxruntime)
    best.engine          (FP16 TensorRT engine — NVIDIA only)
    best_int8.engine     (INT8 TensorRT engine — needs calib images)

Constraints:
    - TensorRT export requires NVIDIA GPU + the `tensorrt` python package
      (Ultralytics installs lazily). Skips with a clear message otherwise.
    - INT8 export requires ~100–500 representative images (no labels needed).
    - FP16 ONNX runs on CPU too (small speedup) but really shines on GPU.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def export_onnx(model_path: Path, imgsz: int, half: bool = True) -> Path | None:
    """Export to ONNX with optional FP16. Works on any platform."""
    from ultralytics import YOLO

    print(f"[ONNX] exporting {model_path.name} → ONNX (half={half}, imgsz={imgsz})")
    t0 = time.perf_counter()
    model = YOLO(str(model_path))
    out_str = model.export(format="onnx", half=half, imgsz=imgsz, simplify=True)
    out = Path(out_str)
    elapsed = time.perf_counter() - t0
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"       → {out.name}  ({size_mb:.1f} MB, exported in {elapsed:.1f}s)")
    return out


def export_tensorrt(
    model_path: Path,
    imgsz: int,
    half: bool = True,
    int8: bool = False,
    calib_data: Path | None = None,
) -> Path | None:
    """Export to TensorRT engine. NVIDIA GPU + tensorrt package required."""
    try:
        import tensorrt  # noqa: F401
    except ImportError:
        print("[TRT]  SKIP — tensorrt not installed (pip install tensorrt)")
        return None

    try:
        import torch
        if not torch.cuda.is_available():
            print("[TRT]  SKIP — no CUDA-capable GPU detected")
            return None
    except ImportError:
        print("[TRT]  SKIP — torch missing")
        return None

    from ultralytics import YOLO

    mode = "INT8" if int8 else ("FP16" if half else "FP32")
    print(f"[TRT]  exporting {model_path.name} → TensorRT ({mode}, imgsz={imgsz})")

    if int8 and calib_data is None:
        print("       ERROR: --calib-data required for INT8")
        return None

    t0 = time.perf_counter()
    model = YOLO(str(model_path))
    kwargs = {
        "format": "engine",
        "imgsz": imgsz,
        "half": half and not int8,
        "int8": int8,
    }
    if int8:
        # Ultralytics expects a directory of representative images for
        # INT8 calibration — no labels needed.
        kwargs["data"] = str(calib_data)
    out_str = model.export(**kwargs)
    out = Path(out_str)
    elapsed = time.perf_counter() - t0
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"       → {out.name}  ({size_mb:.1f} MB, exported in {elapsed:.1f}s)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, type=Path,
                    help="path to trained .pt checkpoint")
    ap.add_argument("--imgsz", type=int, default=640,
                    help="inference resolution (must match training)")
    ap.add_argument(
        "--formats",
        default="onnx,engine",
        help="comma-separated subset of: onnx,engine,int8 (default: onnx,engine)",
    )
    ap.add_argument(
        "--calib-data",
        type=Path,
        default=None,
        help="directory of images for INT8 calibration (~100-500 images, no labels)",
    )
    args = ap.parse_args()

    if not args.model.exists():
        print(f"ERROR: model not found: {args.model}")
        return 1

    formats = {f.strip().lower() for f in args.formats.split(",")}
    unknown = formats - {"onnx", "engine", "int8"}
    if unknown:
        print(f"ERROR: unknown format(s): {unknown}")
        return 1

    print(f"Source : {args.model}  ({args.model.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"Formats: {sorted(formats)}")
    print()

    if "onnx" in formats:
        export_onnx(args.model, args.imgsz, half=True)
    if "engine" in formats:
        export_tensorrt(args.model, args.imgsz, half=True, int8=False)
    if "int8" in formats:
        if not args.calib_data:
            print("[INT8] ERROR: --calib-data required")
            return 1
        if not args.calib_data.exists():
            print(f"[INT8] ERROR: calib data not found: {args.calib_data}")
            return 1
        export_tensorrt(args.model, args.imgsz, half=False, int8=True,
                        calib_data=args.calib_data)

    print("\nDone. The inference engine auto-detects .engine > .onnx > .pt; just")
    print("place the artifacts next to the original .pt and restart the service.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
