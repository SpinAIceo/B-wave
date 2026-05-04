"""Auto-label classification-only datasets using trained YOLO model.

Uses the best 3-class model to generate bbox annotations on
Marine Corrosion images, then outputs YOLO-format labels for fine-tuning.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ultralytics import YOLO

MODEL_PATH = "runs/detect/runs/train/bwave-yolo26s-v1/weights/best.pt"
SRC = Path("data/raw/marine-corrosion/marine_corrosion_dataset")
DST = Path("data/auto-labeled/marine-corrosion")
CONF_THRESHOLD = 0.3

# Map marine corrosion folder names to B-Wave class hints
# If model detects nothing, use folder name as fallback class
FOLDER_CLASS_HINT = {
    "crevice_corrosion": 0,       # rust
    "erosion_corrosion": 1,       # damage
    "galvanic_corrosion": 0,      # rust
    "healthy_structure": None,    # negative sample
    "mic_corrosion": 0,           # rust
    "pitting_corrosion": 0,       # rust
    "stress_corrosion": 1,        # damage (structural)
    "under_insulation_corrosion": 0,  # rust
    "uniform_corrosion": 0,       # rust
}


def main():
    model = YOLO(MODEL_PATH)
    print(f"Model loaded: {MODEL_PATH}")

    for split_dir in ["train", "val"]:
        (DST / split_dir / "images").mkdir(parents=True, exist_ok=True)
        (DST / split_dir / "labels").mkdir(parents=True, exist_ok=True)

    total = 0
    auto_labeled = 0
    hint_labeled = 0
    negative = 0

    folders = sorted(SRC.iterdir())
    for folder in folders:
        if not folder.is_dir():
            continue

        folder_name = folder.name
        hint_cls = FOLDER_CLASS_HINT.get(folder_name)
        images = sorted(folder.glob("*.*"))
        print(f"\n{folder_name}: {len(images)} images (hint_cls={hint_cls})")

        for i, img_path in enumerate(images):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
                continue
            total += 1

            # 80/20 train/val split
            split = "val" if i % 5 == 0 else "train"
            dest_name = f"mc_{folder_name}_{img_path.stem}{img_path.suffix}"

            # Run inference
            results = model.predict(str(img_path), conf=CONF_THRESHOLD, verbose=False)

            yolo_lines = []
            for result in results:
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].cpu().numpy()
                    img_w, img_h = result.orig_shape[1], result.orig_shape[0]

                    cx = ((xyxy[0] + xyxy[2]) / 2) / img_w
                    cy = ((xyxy[1] + xyxy[3]) / 2) / img_h
                    w = (xyxy[2] - xyxy[0]) / img_w
                    h = (xyxy[3] - xyxy[1]) / img_h

                    yolo_lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            if yolo_lines:
                auto_labeled += 1
            elif hint_cls is not None:
                # Model found nothing — use full-image bbox with folder hint
                # Only for corrosion folders, skip for small fraction
                if i % 3 == 0:  # use 1/3 of hint-labeled to avoid noise
                    yolo_lines.append(f"{hint_cls} 0.500000 0.500000 0.900000 0.900000")
                    hint_labeled += 1
            else:
                # healthy_structure — negative sample
                negative += 1

            # Copy image and write label
            shutil.copy2(img_path, DST / split / "images" / dest_name)
            label_text = "\n".join(yolo_lines) + ("\n" if yolo_lines else "")
            (DST / split / "labels" / (Path(dest_name).stem + ".txt")).write_text(label_text)

    # Write data.yaml
    yaml_path = DST / "data.yaml"
    yaml_path.write_text(
        f"path: {DST.resolve().as_posix()}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"\n"
        f"nc: 3\n"
        f"names:\n"
        f"  0: rust\n"
        f"  1: damage\n"
        f"  2: leak\n"
    )

    print(f"\n{'='*60}")
    print(f"AUTO-LABELING COMPLETE")
    print(f"  Total images: {total}")
    print(f"  Model-detected labels: {auto_labeled}")
    print(f"  Hint-based labels: {hint_labeled}")
    print(f"  Negative samples: {negative}")
    print(f"  Output: {DST}")


if __name__ == "__main__":
    main()
