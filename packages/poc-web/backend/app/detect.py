from __future__ import annotations

import io
import os
import time
from pathlib import Path

from PIL import Image

from app.harness import (
    DROP_BELOW_THRESHOLD,
    HarnessContext,
    HarnessTrace,
    InferenceHarness,
)
from app.logger import get_logger
from app.models import BBox, DetectResponse

# Loaded once at import; safe to share across requests (stateless).
_HARNESS = InferenceHarness.load_default()
_HARNESS_INFO = _HARNESS.describe()

# Sub-logger so operators can filter `bwave.detect.harness` separately
# from the rest of the inference pipeline noise.
log = get_logger("bwave.detect")
harness_log = get_logger("bwave.detect.harness")

# Startup banner — emitted once at import. Lets operators verify which
# config is live without grepping the YAML.
harness_log.info(
    "Harness loaded | T=%.3f default_thr=%.2f zones_thr=%s zones_allow=%s vessel_types=%s penalty=%.2f",
    _HARNESS_INFO["calibration_T"],
    _HARNESS_INFO["default_threshold"],
    _HARNESS_INFO["zones_with_thresholds"],
    _HARNESS_INFO["zones_with_allowlist"],
    _HARNESS_INFO["vessel_types"],
    _HARNESS_INFO["disallowed_penalty"],
)
if _HARNESS_INFO["calibration_T"] == 1.0:
    harness_log.warning(
        "Calibration T=1.0 (no-op). Run scripts/fit_calibration.py on a "
        "labeled validation set to fit a real T — without it, severity "
        "buckets reflect raw YOLO confidence, not calibrated probability."
    )

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


def _harness_trace_log(idx: int, total: int, cls_name: str,
                        trace: HarnessTrace) -> None:
    """Bilingual one-line trace: shows raw → calibrated → context-adjusted →
    final, plus the threshold and the keep/drop decision. Useful when an
    operator wonders 'why was that detection dropped?' or 'where did the
    confidence number come from?'"""
    ko_cls = _CLASS_KO.get(cls_name, cls_name)
    decision_en = "KEEP" if trace.kept else f"DROP({trace.drop_reason or 'unknown'})"
    decision_ko = "유지" if trace.kept else f"제거({trace.drop_reason or '알수없음'})"
    allow_marker = "" if trace.allowed_in_zone else "  ❌zone-disallowed"

    harness_log.info(
        f"  [{idx}/{total}] {cls_name} ({ko_cls})  "
        f"raw={trace.raw_confidence*100:.1f}% → "
        f"cal={trace.calibrated_confidence*100:.1f}%  "
        f"× allow={trace.allowlist_factor:.2f} "
        f"× prior={trace.zone_prior_factor:.2f} "
        f"× vt={trace.vessel_type_factor:.2f}  "
        f"= final={trace.final_confidence*100:.1f}%  "
        f"thr[{trace.threshold_zone_key}]={trace.threshold_applied*100:.1f}%  "
        f"→ {decision_en} / {decision_ko}{allow_marker}"
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


def run_inference(
    image_bytes: bytes,
    zone: str | None = None,
    vessel_type: str | None = None,
) -> DetectResponse:
    # ── STEP 1/8: 이미지 수신 (Image received) ────────────────────────────────
    log.info(f"[STEP 1/8] 이미지 수신 | image received — {len(image_bytes)/1024:.1f} KB")

    # ── STEP 2/8: 모델 준비 확인 (Model readiness check) ─────────────────────
    log.info("[STEP 2/8] 모델 준비 확인 | model readiness check")
    _load_model()
    mode = "REAL" if _model is not None else "DEMO"
    log.info(f"           └─ mode={mode} ({'실제 YOLO 모델' if mode=='REAL' else '데모 응답 (모델 없음)'})")

    # ── STEP 3/8: 이미지 디코딩 (Image decode) ───────────────────────────────
    log.info("[STEP 3/8] 이미지 디코딩 | image decode")
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_w, img_h = image.size
    log.info(f"           └─ size={img_w}×{img_h}px  channels=RGB")

    # ── STEP 4/8: Harness 컨텍스트 (Harness context) ──────────────────────────
    harness_ctx = HarnessContext(zone=zone, vessel_type=vessel_type)
    log.info(
        f"[STEP 4/8] Harness 컨텍스트 | harness ctx — "
        f"zone={zone or '-'}  vessel_type={vessel_type or '-'}  "
        f"T={_HARNESS_INFO['calibration_T']:.2f}"
    )
    if zone and zone not in _HARNESS_INFO["zones_with_thresholds"]:
        harness_log.warning(
            f"  zone='{zone}' has no per-zone thresholds — falling back to 'default' "
            f"(known zones: {_HARNESS_INFO['zones_with_thresholds']})"
        )

    if _model is None:
        log.info("[STEP 5/8] 모델 추론 SKIP | inference skipped → 데모 결과 반환")
        demo = _demo_response(img_w, img_h)
        log.info("[STEP 6/8] Harness SKIP | demo mode bypasses harness")
        log.info("[STEP 7/8] PSC 매핑 | PSC mapping (demo 고정값)")
        total = len(demo.detections)
        for i, d in enumerate(demo.detections, 1):
            _bilingual_detection_log(i, total, d.class_name, d.confidence,
                                     d.psc_code, d.severity,
                                     (d.x_min, d.y_min, d.x_max, d.y_max))
        log.info(f"[STEP 8/8] 응답 생성 완료 | response built — 탐지={total}건 (demo mode)")
        return demo

    # ── STEP 5/8: 모델 추론 (Model inference) ────────────────────────────────
    import torch
    device = 0 if torch.cuda.is_available() else "cpu"
    device_label = f"GPU(cuda:{device})" if device == 0 else "CPU"
    # Lower conf=0.05 since the harness applies its own (calibrated, per-zone)
    # thresholds afterward. This lets the harness see candidates the model
    # would otherwise drop.
    log.info(f"[STEP 5/8] 모델 추론 시작 | inference start — device={device_label} model_conf=0.05")
    t0 = time.perf_counter()
    results = _model.predict(image, conf=0.05, verbose=False, device=device)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    raw_count = sum(len(r.boxes) for r in results if r.boxes is not None)
    log.info(
        f"           └─ 완료 {elapsed_ms:.1f}ms | done in {elapsed_ms:.1f}ms — raw boxes={raw_count}"
    )

    # ── STEP 6/8: Harness 후처리 (calibration → context → threshold) ─────────
    log.info(
        f"[STEP 6/8] Harness 후처리 시작 | post-processing — "
        f"calibration → context filter → zone threshold"
    )
    detections: list[BBox] = []
    drop_reasons: dict[str, int] = {}
    raw_boxes: list[tuple[str, int, float, list]] = []  # (cls_name, cls_id, raw_conf, xyxy)

    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id   = int(box.cls[0].item())
            raw_conf = float(box.conf[0].item())
            xyxy     = box.xyxy[0].cpu().numpy()
            cls_name = result.names.get(cls_id, "unknown")
            raw_boxes.append((cls_name, cls_id, raw_conf, xyxy))

    if not raw_boxes:
        harness_log.info("  no raw boxes to process")

    for idx, (cls_name, cls_id, raw_conf, xyxy) in enumerate(raw_boxes, 1):
        # Harness adjusts confidence (calibration + context priors) and
        # decides whether the detection meets the per-(zone,class) threshold.
        adj_conf, kept, trace = _HARNESS.adjust_with_trace(cls_name, raw_conf, harness_ctx)
        _harness_trace_log(idx, len(raw_boxes), cls_name, trace)

        if not kept:
            reason = trace.drop_reason or "unknown"
            drop_reasons[reason] = drop_reasons.get(reason, 0) + 1
            continue

        conf = adj_conf
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

    dropped_by_harness = sum(drop_reasons.values())
    drop_summary = ", ".join(f"{k}={v}" for k, v in drop_reasons.items()) or "(none)"
    harness_log.info(
        f"  Harness summary | raw={raw_count}  kept={len(detections)}  "
        f"dropped={dropped_by_harness} ({drop_summary})"
    )

    # Operator anomalies — surface unusual harness behavior so it's not silent.
    if raw_count > 0 and len(detections) == 0:
        harness_log.warning(
            "  All raw detections dropped by harness — verify thresholds for "
            f"zone='{zone}' aren't too strict (config: {_HARNESS_INFO['calibration_T']=}, "
            f"default_thr={_HARNESS_INFO['default_threshold']})"
        )
    elif raw_count >= 5 and dropped_by_harness / raw_count >= 0.8:
        harness_log.warning(
            f"  High drop ratio: {dropped_by_harness}/{raw_count} "
            f"({dropped_by_harness/raw_count*100:.0f}%) — review zone='{zone}' thresholds"
        )

    # ── STEP 7/8: PSC 매핑 + 심각도 (이미 위에서 적용됨; 결과 출력) ───────────
    log.info(f"[STEP 7/8] PSC 매핑 + 심각도 분류 | PSC mapping + severity classification")
    for i, d in enumerate(detections, 1):
        _bilingual_detection_log(i, len(detections),
                                  d.class_name, d.confidence,
                                  d.psc_code, d.severity,
                                  (d.x_min, d.y_min, d.x_max, d.y_max))

    # ── STEP 8/8: 응답 생성 (Response build) ─────────────────────────────────
    severity_summary = {s: sum(1 for d in detections if d.severity == s)
                        for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW") if
                        any(d.severity == s for d in detections)}
    ko_summary = {_SEVERITY_KO[s]: c for s, c in severity_summary.items()}
    log.info(
        f"[STEP 8/8] 응답 생성 완료 | response built — "
        f"총 탐지={len(detections)}건 / total={len(detections)} detections  "
        f"harness dropped={dropped_by_harness} (raw={raw_count})  "
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
