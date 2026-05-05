from __future__ import annotations

import io
import os
import time
from pathlib import Path

from PIL import Image

from app.logger import get_logger
from app.models import BBox, DetectResponse

log = get_logger("bwave.detect")

# ── Bilingual label tables ────────────────────────────────────────────────────

_PSC_CODE: dict[str, str] = {
    "rust":   "0615",
    "damage": "0630",
    "leak":   "0950",
}

# English PSC descriptions
_PSC_DESC_EN: dict[str, str] = {
    "0615": "Hull corrosion / wastage",
    "0630": "Structural deficiency",
    "0950": "Oil / water leakage",
}

# Korean PSC descriptions
_PSC_DESC_KO: dict[str, str] = {
    "0615": "선체 부식/낭비",
    "0630": "구조적 결함",
    "0950": "오일/수분 누출",
}

# Keep backward-compat alias
_PSC_DESC = _PSC_DESC_EN

# English class names (used as-is from model)
_CLASS_EN: dict[str, str] = {
    "rust":   "Rust / Corrosion",
    "damage": "Structural Damage",
    "leak":   "Oil / Water Leak",
}

# Korean class names
_CLASS_KO: dict[str, str] = {
    "rust":   "부식",
    "damage": "손상",
    "leak":   "누수",
}

# English severity labels
_SEVERITY_EN: dict[str, str] = {
    "CRITICAL": "Critical",
    "HIGH":     "High",
    "MEDIUM":   "Medium",
    "LOW":      "Low",
}

# Korean severity labels
_SEVERITY_KO: dict[str, str] = {
    "CRITICAL": "심각",
    "HIGH":     "높음",
    "MEDIUM":   "중간",
    "LOW":      "낮음",
}


def _severity(conf: float) -> str:
    if conf >= 0.8:
        return "CRITICAL"
    if conf >= 0.6:
        return "HIGH"
    if conf >= 0.4:
        return "MEDIUM"
    return "LOW"


def _bilingual_detection_log(idx: int, total: int, cls_name: str, conf: float,
                              psc_code: str, severity: str, xyxy: tuple) -> None:
    """Log one detection result in both Korean and English."""
    en_cls  = _CLASS_EN.get(cls_name, cls_name)
    ko_cls  = _CLASS_KO.get(cls_name, cls_name)
    en_desc = _PSC_DESC_EN.get(psc_code, "Unknown deficiency")
    ko_desc = _PSC_DESC_KO.get(psc_code, "알 수 없는 결함")
    en_sev  = _SEVERITY_EN.get(severity, severity)
    ko_sev  = _SEVERITY_KO.get(severity, severity)
    x1, y1, x2, y2 = (round(v) for v in xyxy)
    log.info(
        f"  [탐지 {idx}/{total}] "
        f"EN: {en_cls} | KO: {ko_cls}  "
        f"conf={conf*100:.1f}%  "
        f"severity: {en_sev}({ko_sev})  "
        f"PSC-{psc_code}: \"{en_desc}\" / \"{ko_desc}\"  "
        f"bbox=[{x1},{y1} → {x2},{y2}]"
    )


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
    log.debug(f"model search candidates={[str(c) for c in candidates]}")
    for p in candidates:
        if p.exists() and p.is_file():
            log.info(f"model found: {p}")
            return p
    log.warning("no model file found — will use demo response")
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
    log.info(f"loading model from {model_path} …")
    try:
        import torch
        from ultralytics import YOLO
        _model = YOLO(str(model_path))
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            _model.to("cuda")
        _model_loaded = True
        log.info(f"model loaded OK device={device}")
    except Exception as exc:
        log.error(f"model load FAILED: {exc!r} — falling back to demo mode")
        _model_loaded = True


def run_inference(image_bytes: bytes) -> DetectResponse:
    # ── STEP 1/6: 이미지 수신 (Image received) ────────────────────────────────
    log.info(f"[STEP 1/6] 이미지 수신 | image received — {len(image_bytes)/1024:.1f} KB")

    # ── STEP 2/6: 모델 준비 확인 (Model readiness check) ─────────────────────
    log.info("[STEP 2/6] 모델 준비 확인 | model readiness check")
    _load_model()
    mode = "REAL" if _model is not None else "DEMO"
    log.info(f"           └─ mode={mode} ({'실제 YOLO 모델' if mode=='REAL' else '데모 응답 (모델 없음)'})")

    # ── STEP 3/6: 이미지 디코딩 (Image decode) ───────────────────────────────
    log.info("[STEP 3/6] 이미지 디코딩 | image decode")
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = image.size
    log.info(f"           └─ size={img_w}×{img_h}px  channels=RGB")

    if _model is None:
        log.info("[STEP 4/6] 모델 추론 SKIP | inference skipped → 데모 결과 반환")
        demo = _demo_response(img_w, img_h)
        log.info("[STEP 5/6] PSC 매핑 | PSC mapping (demo 고정값)")
        total = len(demo.detections)
        for i, d in enumerate(demo.detections, 1):
            _bilingual_detection_log(i, total, d.class_name, d.confidence,
                                     d.psc_code, d.severity,
                                     (d.x_min, d.y_min, d.x_max, d.y_max))
        log.info(f"[STEP 6/6] 응답 생성 완료 | response built — 탐지={total}건 (demo mode)")
        return demo

    # ── STEP 4/6: 모델 추론 (Model inference) ────────────────────────────────
    import torch
    device = 0 if torch.cuda.is_available() else "cpu"
    device_label = f"GPU(cuda:{device})" if device == 0 else "CPU"
    log.info(f"[STEP 4/6] 모델 추론 시작 | inference start — device={device_label} conf_threshold=0.25")
    t0 = time.perf_counter()
    results = _model.predict(image, conf=0.25, verbose=False, device=device)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    raw_count = sum(len(r.boxes) for r in results if r.boxes is not None)
    log.info(f"           └─ 완료 {elapsed_ms:.1f}ms | done in {elapsed_ms:.1f}ms — raw boxes={raw_count}")

    # ── STEP 5/6: PSC 코드 매핑 + 심각도 분류 (PSC mapping + severity) ────────
    log.info(f"[STEP 5/6] PSC 매핑 + 심각도 분류 | PSC mapping + severity classification")
    detections: list[BBox] = []
    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id   = int(box.cls[0].item())
            conf     = float(box.conf[0].item())
            xyxy     = box.xyxy[0].cpu().numpy()
            cls_name = result.names.get(cls_id, "unknown")
            psc_code = _PSC_CODE.get(cls_name, "9999")
            psc_desc = _PSC_DESC_EN.get(psc_code, "Unknown deficiency")
            severity = _severity(conf)

            # ── 도메인 검증 (Domain validation warnings) ──────────────────
            if not (0.0 < conf <= 1.0):
                log.warning(f"  [WARN] 비정상 confidence | unusual conf={conf:.4f} cls={cls_name}")
            if cls_name == "unknown":
                log.warning(f"  [WARN] 미분류 클래스 | unknown class cls_id={cls_id}")
            if psc_code == "9999":
                log.warning(f"  [WARN] PSC 미매핑 | unmapped PSC cls={cls_name} → psc_code=9999")
            x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
            if x1 < 0 or y1 < 0 or x2 > img_w or y2 > img_h:
                log.warning(
                    f"  [WARN] bbox 이미지 범위 초과 | bbox out of bounds "
                    f"[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}] img={img_w}×{img_h}"
                )
            if x2 <= x1 or y2 <= y1:
                log.warning(f"  [WARN] bbox 넓이 0 이하 | degenerate bbox [{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]")

            detections.append(BBox(
                x_min=float(xyxy[0]),
                y_min=float(xyxy[1]),
                x_max=float(xyxy[2]),
                y_max=float(xyxy[3]),
                class_name=cls_name,
                confidence=round(conf, 4),
                psc_code=psc_code,
                psc_description=psc_desc,
                severity=severity,
            ))
            _bilingual_detection_log(len(detections), raw_count,
                                     cls_name, conf, psc_code, severity, tuple(xyxy))

    # ── STEP 6/6: 응답 생성 (Response build) ─────────────────────────────────
    severity_summary = {s: sum(1 for d in detections if d.severity == s)
                        for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW") if
                        any(d.severity == s for d in detections)}
    ko_summary = {_SEVERITY_KO[s]: c for s, c in severity_summary.items()}
    log.info(
        f"[STEP 6/6] 응답 생성 완료 | response built — "
        f"총 탐지={len(detections)}건 / total={len(detections)} detections  "
        f"심각도: {ko_summary} / severity: {severity_summary}  "
        f"추론시간={elapsed_ms:.1f}ms"
    )
    return DetectResponse(
        detections=detections,
        image_width=img_w,
        image_height=img_h,
        inference_ms=round(elapsed_ms, 1),
    )


def _demo_response(img_w: int, img_h: int) -> DetectResponse:
    """Fallback: fixed demo detections when no model is loaded."""
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
