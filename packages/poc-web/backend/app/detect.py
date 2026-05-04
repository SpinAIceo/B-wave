from __future__ import annotations

import io
import os
import time
from pathlib import Path

from PIL import Image

from app.models import BBox, DetectResponse

# PSC mapping (mirrors psc_mapper.py)
_PSC_CODE: dict[str, str] = {
    "rust": "0615",
    "damage": "0630",
    "leak": "0950",
}
_PSC_DESC: dict[str, str] = {
    "0615": "Hull corrosion / wastage",
    "0630": "Structural deficiency",
    "0950": "Oil / water leakage",
}


def _severity(conf: float) -> str:
    if conf >= 0.8:
        return "CRITICAL"
    if conf >= 0.6:
        return "HIGH"
    if conf >= 0.4:
        return "MEDIUM"
    return "LOW"


def _find_model() -> Path | None:
    candidates: list[Path] = []
    env_path = os.environ.get("MODEL_PATH", "")
    if env_path:
        candidates.append(Path(env_path))
    # Prefer .pt on local dev (no onnxruntime conflicts); prefer .onnx in Docker
    candidates += [
        Path(__file__).parent.parent / "model" / "best.pt",
        Path(__file__).parent.parent / "model" / "best.onnx",
        Path("runs/detect/runs/train/bwave-yolo26s-v1/weights/best.pt"),
        Path("runs/detect/runs/train/bwave-yolo26s-v1/weights/best.onnx"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


_model = None
_model_loaded = False


def _load_model():
    global _model, _model_loaded
    if _model_loaded:
        return
    model_path = _find_model()
    if model_path is None:
        _model_loaded = True
        return
    try:
        from ultralytics import YOLO
        _model = YOLO(str(model_path))
        _model_loaded = True
    except Exception:
        _model_loaded = True


def run_inference(image_bytes: bytes) -> DetectResponse:
    _load_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = image.size

    if _model is None:
        # Return demo detections if model not found
        return _demo_response(img_w, img_h)

    t0 = time.perf_counter()
    results = _model.predict(image, conf=0.25, verbose=False)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    detections: list[BBox] = []
    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].cpu().numpy()
            names = result.names
            cls_name = names.get(cls_id, "unknown")

            psc_code = _PSC_CODE.get(cls_name, "9999")
            psc_desc = _PSC_DESC.get(psc_code, "Unknown deficiency")

            detections.append(BBox(
                x_min=float(xyxy[0]),
                y_min=float(xyxy[1]),
                x_max=float(xyxy[2]),
                y_max=float(xyxy[3]),
                class_name=cls_name,
                confidence=round(conf, 4),
                psc_code=psc_code,
                psc_description=psc_desc,
                severity=_severity(conf),
            ))

    return DetectResponse(
        detections=detections,
        image_width=img_w,
        image_height=img_h,
        inference_ms=round(elapsed_ms, 1),
    )


def _demo_response(img_w: int, img_h: int) -> DetectResponse:
    """Fallback demo detections when no model is loaded."""
    demo: list[BBox] = [
        BBox(
            x_min=img_w * 0.1,
            y_min=img_h * 0.15,
            x_max=img_w * 0.4,
            y_max=img_h * 0.45,
            class_name="rust",
            confidence=0.78,
            psc_code="0615",
            psc_description="Hull corrosion / wastage",
            severity="HIGH",
        ),
        BBox(
            x_min=img_w * 0.55,
            y_min=img_h * 0.3,
            x_max=img_w * 0.85,
            y_max=img_h * 0.7,
            class_name="damage",
            confidence=0.62,
            psc_code="0630",
            psc_description="Structural deficiency",
            severity="HIGH",
        ),
    ]
    return DetectResponse(
        detections=demo,
        image_width=img_w,
        image_height=img_h,
        inference_ms=0.0,
        model_version="YOLO26s-v1 (demo)",
    )
