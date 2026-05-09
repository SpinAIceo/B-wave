"""
Fit confidence calibration temperature T for the inference harness.

Usage:
    python -m ai_engine.scripts.fit_calibration \
        --model runs/exp1/weights/best.pt \
        --val-set data/unified/val \
        --out packages/ai-engine/configs/harness.yaml

What it does:
    1. Run inference on every val image, collecting (predicted_score, true_label)
       pairs per detected box (matched to GT via IoU > 0.5).
    2. Fit a single scalar T that minimises Negative Log-Likelihood:
       calibrated = sigmoid(logit(p) / T)
    3. Update `calibration.temperature` in the harness config in place.

Quick math:
    A model that's 80% confident but only 60% accurate is over-confident.
    Temperature scaling pulls probabilities toward 0.5 (T>1) or extremes (T<1)
    until the predicted distribution matches the empirical one. It does NOT
    change the rank order of predictions, so mAP/AP is unchanged — only
    severity classification downstream improves.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


def _logit(p: float, eps: float = 1e-6) -> float:
    p = max(eps, min(1.0 - eps, p))
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def negative_log_likelihood(T: float, scores: list[float], labels: list[int]) -> float:
    """Binary NLL after temperature scaling. labels in {0, 1}."""
    if T <= 0:
        return float("inf")
    nll = 0.0
    for p, y in zip(scores, labels):
        cal = _sigmoid(_logit(p) / T)
        cal = max(1e-9, min(1.0 - 1e-9, cal))
        nll -= y * math.log(cal) + (1 - y) * math.log(1 - cal)
    return nll / max(1, len(scores))


def fit_temperature(scores: list[float], labels: list[int]) -> float:
    """Golden-section search over T in (0.05, 5.0). No external deps."""
    if not scores:
        return 1.0

    lo, hi = 0.05, 5.0
    phi = (math.sqrt(5) - 1) / 2  # 0.618...
    a = hi - phi * (hi - lo)
    b = lo + phi * (hi - lo)
    fa = negative_log_likelihood(a, scores, labels)
    fb = negative_log_likelihood(b, scores, labels)

    for _ in range(60):  # ~1e-9 precision
        if fa < fb:
            hi = b
            b, fb = a, fa
            a = hi - phi * (hi - lo)
            fa = negative_log_likelihood(a, scores, labels)
        else:
            lo = a
            a, fa = b, fb
            b = lo + phi * (hi - lo)
            fb = negative_log_likelihood(b, scores, labels)

    return round((lo + hi) / 2, 4)


def expected_calibration_error(
    scores: list[float], labels: list[int], n_bins: int = 10
) -> float:
    """ECE for a quick sanity check before/after."""
    if not scores:
        return 0.0
    bins = [(i / n_bins, (i + 1) / n_bins) for i in range(n_bins)]
    total = len(scores)
    ece = 0.0
    for lo, hi in bins:
        in_bin = [(s, y) for s, y in zip(scores, labels) if lo <= s < hi or (hi == 1.0 and s == 1.0)]
        if not in_bin:
            continue
        avg_conf = sum(s for s, _ in in_bin) / len(in_bin)
        accuracy = sum(y for _, y in in_bin) / len(in_bin)
        ece += (len(in_bin) / total) * abs(avg_conf - accuracy)
    return ece


def collect_predictions(model_path: Path, val_dir: Path, iou_match: float = 0.5):
    """Run inference on val_dir, match each prediction to GT, return (scores, labels).
    label=1 if matched to GT of same class, label=0 if false positive."""
    try:
        from ai_engine.inference.engine import InferenceEngine
    except ImportError:
        print("ERROR: ai_engine.inference.engine import failed. "
              "Install the package with `pip install -e packages/ai-engine`.")
        sys.exit(2)

    engine = InferenceEngine(str(model_path))
    if not engine.is_loaded:
        print(f"ERROR: model {model_path} failed to load")
        sys.exit(2)

    img_dir = val_dir / "images" if (val_dir / "images").exists() else val_dir
    label_dir = val_dir / "labels" if (val_dir / "labels").exists() else val_dir

    scores: list[float] = []
    labels: list[int] = []
    n_images = 0
    n_gt = 0
    n_pred = 0

    for img_path in sorted(img_dir.glob("*.jpg")) + sorted(img_dir.glob("*.png")):
        gt_path = label_dir / f"{img_path.stem}.txt"
        gts = _load_yolo_labels(gt_path) if gt_path.exists() else []
        n_gt += len(gts)
        n_images += 1

        with open(img_path, "rb") as f:
            preds = engine.predict(f.read(), conf_threshold=0.05)
        n_pred += len(preds)

        used = set()
        for p in preds:
            best_iou, best_gt = 0.0, None
            for gi, g in enumerate(gts):
                if gi in used or g["class_id"] != p.class_id:
                    continue
                iou = _box_iou(
                    (p.x_min, p.y_min, p.x_max, p.y_max),
                    (g["x_min"], g["y_min"], g["x_max"], g["y_max"]),
                )
                if iou > best_iou:
                    best_iou, best_gt = iou, gi
            scores.append(p.confidence)
            if best_gt is not None and best_iou >= iou_match:
                labels.append(1)
                used.add(best_gt)
            else:
                labels.append(0)

    print(f"Processed {n_images} images: {n_gt} GT boxes, {n_pred} predictions, "
          f"{sum(labels)} TP, {len(labels) - sum(labels)} FP")
    return scores, labels


def _load_yolo_labels(path: Path) -> list[dict]:
    out = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cls, cx, cy, w, h = int(parts[0]), *map(float, parts[1:5])
        out.append({
            "class_id": cls,
            "x_min": cx - w / 2, "y_min": cy - h / 2,
            "x_max": cx + w / 2, "y_max": cy + h / 2,
        })
    return out


def _box_iou(a: tuple, b: tuple) -> float:
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def update_yaml_temperature(yaml_path: Path, T: float) -> None:
    import yaml

    data = {}
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    data.setdefault("calibration", {})["temperature"] = T
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, type=Path)
    ap.add_argument("--val-set", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    if not args.model.exists():
        print(f"Model not found: {args.model}")
        return 1
    if not args.val_set.exists():
        print(f"Val set not found: {args.val_set}")
        return 1

    print(f"Running inference on {args.val_set}...")
    scores, labels = collect_predictions(args.model, args.val_set)
    if not scores:
        print("No predictions collected — cannot fit T.")
        return 1

    ece_before = expected_calibration_error(scores, labels)
    T = fit_temperature(scores, labels)
    cal_scores = [_sigmoid(_logit(s) / T) for s in scores]
    ece_after = expected_calibration_error(cal_scores, labels)

    print(f"Fitted T = {T}")
    print(f"ECE: {ece_before:.4f} → {ece_after:.4f}  (lower is better)")
    print(f"Updating {args.out} ...")
    update_yaml_temperature(args.out, T)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
