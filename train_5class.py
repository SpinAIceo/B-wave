"""B-Wave 5-class training — YOLO26m on 21k images.

5 classes: rust, damage, leak, missing_label, cargo_lashing
Larger model (21.9M) justified by larger dataset (21k vs 11k).
Config A settings (best proven) with 200 epochs for deeper convergence.
"""

from ultralytics import YOLO


def main():
    model = YOLO("yolo26m.pt")

    model.train(
        data="data/unified-5class/data.yaml",
        epochs=200,
        imgsz=640,
        batch=16,
        device="cuda",
        lr0=0.01,
        optimizer="AdamW",
        weight_decay=0.0005,
        warmup_epochs=5,
        patience=30,
        project="runs/train",
        name="bwave-yolo26m-5class",
        exist_ok=True,
        workers=4,
        fliplr=0.5,
        flipud=0.0,
        degrees=10.0,
        scale=0.2,
        mosaic=1.0,
        close_mosaic=10,
        copy_paste=0.3,
        mixup=0.15,
        cls=1.0,
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
