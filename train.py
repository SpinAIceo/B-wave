"""B-Wave YOLO26s training script."""

from ultralytics import YOLO


def main():
    model = YOLO("yolo26s.pt")

    model.train(
        data="data/unified/data.yaml",
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
        name="bwave-yolo26s-v1",
        exist_ok=True,
        workers=4,
        # augmentation
        fliplr=0.5,
        flipud=0.0,
        degrees=10.0,
        scale=0.2,
        mosaic=1.0,
        copy_paste=0.3,
        mixup=0.15,
        # imbalance mitigation
        cls=1.0,
        # logging
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
