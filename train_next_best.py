"""B-Wave YOLO26s — Codex-recommended optimal config.

Strategy: SGD + mosaic=0.5 + close_mosaic=90
- Mosaic at half-strength for 90 epochs (leak diversity)
- Mosaic off for last 10 epochs (bbox tightness for rust/damage)
- Low lr=0.005 (sgd-low-lr was 2nd best in 30ep grid)
- Light augmentation (copy_paste=0.15, mixup=0.05)
"""

from ultralytics import YOLO


def main():
    model = YOLO("yolo26s.pt")

    model.train(
        data="data/unified/data.yaml",
        epochs=100,
        imgsz=640,
        batch=32,
        device="cuda",
        lr0=0.005,
        optimizer="SGD",
        weight_decay=0.0005,
        warmup_epochs=3,
        patience=30,
        project="runs/train",
        name="bwave-yolo26s-codex-optimal",
        exist_ok=True,
        workers=4,
        # Codex optimal: half mosaic + close at epoch 90
        mosaic=0.5,
        close_mosaic=90,
        copy_paste=0.15,
        mixup=0.05,
        # Light geometric aug
        fliplr=0.5,
        flipud=0.0,
        degrees=5.0,
        scale=0.1,
        cls=1.0,
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
