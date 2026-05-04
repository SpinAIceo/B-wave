"""Fine-tune best 3-class model on original + auto-labeled marine corrosion data.

Strategy: Start from best.pt (not pretrained), lower lr for fine-tuning.
Merge original unified data with auto-labeled marine corrosion.
"""

from pathlib import Path
from ultralytics import YOLO
import shutil


def merge_datasets():
    """Merge original unified + auto-labeled into a combined dataset."""
    combined = Path("data/combined-finetune")
    if combined.exists():
        shutil.rmtree(combined)

    for split in ["train", "val"]:
        (combined / split / "images").mkdir(parents=True, exist_ok=True)
        (combined / split / "labels").mkdir(parents=True, exist_ok=True)

    count = 0
    # Copy original unified data
    orig = Path("data/unified")
    for split_map in [("train", "train"), ("val", "val"), ("test", "val")]:
        src_split, dst_split = split_map
        src_img = orig / src_split / "images"
        src_lbl = orig / src_split / "labels"
        if not src_img.exists():
            continue
        for img in src_img.iterdir():
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                shutil.copy2(img, combined / dst_split / "images" / img.name)
                lbl = src_lbl / (img.stem + ".txt")
                if lbl.exists():
                    shutil.copy2(lbl, combined / dst_split / "labels" / lbl.name)
                else:
                    (combined / dst_split / "labels" / (img.stem + ".txt")).write_text("")
                count += 1

    # Copy auto-labeled marine corrosion
    auto = Path("data/auto-labeled/marine-corrosion")
    for split in ["train", "val"]:
        src_img = auto / split / "images"
        src_lbl = auto / split / "labels"
        if not src_img.exists():
            continue
        for img in src_img.iterdir():
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                shutil.copy2(img, combined / split / "images" / img.name)
                lbl = src_lbl / (img.stem + ".txt")
                if lbl.exists():
                    shutil.copy2(lbl, combined / split / "labels" / lbl.name)
                count += 1

    # Write data.yaml
    yaml_path = combined / "data.yaml"
    yaml_path.write_text(
        f"path: {combined.resolve().as_posix()}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"\n"
        f"nc: 3\n"
        f"names:\n"
        f"  0: rust\n"
        f"  1: damage\n"
        f"  2: leak\n"
    )
    print(f"Combined dataset: {count} images at {combined}")
    return str(yaml_path)


def main():
    yaml_path = merge_datasets()

    # Fine-tune from best weights, not from scratch
    model = YOLO("runs/detect/runs/train/bwave-yolo26s-v1/weights/best.pt")

    model.train(
        data=yaml_path,
        epochs=50,
        imgsz=640,
        batch=32,
        device="cuda",
        lr0=0.001,  # lower lr for fine-tuning
        lrf=0.01,
        optimizer="AdamW",
        weight_decay=0.0005,
        warmup_epochs=2,
        patience=15,
        project="runs/train",
        name="bwave-yolo26s-finetune",
        exist_ok=True,
        workers=4,
        fliplr=0.5,
        degrees=10.0,
        scale=0.2,
        mosaic=1.0,
        copy_paste=0.3,
        mixup=0.15,
        cls=1.0,
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
