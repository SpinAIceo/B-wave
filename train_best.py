"""B-Wave YOLO26s full training with best config from Karpathy Loop.

Winner: SGD + no mosaic + no augmentation
30-epoch result: mAP50-95=0.2830, mAP50=0.4787
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
        lr0=0.01,
        optimizer="SGD",
        weight_decay=0.0005,
        warmup_epochs=3,
        patience=20,
        project="runs/train",
        name="bwave-yolo26s-best",
        exist_ok=True,
        workers=4,
        # Winner config: no mosaic, no augmentation
        fliplr=0.5,
        flipud=0.0,
        degrees=0.0,
        scale=0.0,
        mosaic=0.0,
        copy_paste=0.0,
        mixup=0.0,
        cls=1.0,
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
