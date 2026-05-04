"""B-Wave YOLO26s training on cleaned dataset.

Config A (best mAP50-95=0.323) + cleaned data (tiny/huge bbox, duplicates removed).
"""

from ultralytics import YOLO


def main():
    model = YOLO("yolo26s.pt")

    model.train(
        data="data/unified-clean/data.yaml",
        epochs=100,
        imgsz=640,
        batch=32,
        device="cuda",
        lr0=0.01,
        optimizer="AdamW",
        weight_decay=0.0005,
        warmup_epochs=3,
        patience=20,
        project="runs/train",
        name="bwave-yolo26s-clean",
        exist_ok=True,
        workers=4,
        fliplr=0.5,
        flipud=0.0,
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
