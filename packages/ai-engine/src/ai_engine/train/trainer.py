from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import TrainConfig


@dataclass
class TrainResult:
    best_model_path: str
    metrics: dict[str, float]
    epochs_completed: int


@dataclass
class EvalResult:
    map50: float
    map50_95: float
    precision: float
    recall: float
    per_class: dict[str, dict[str, float]]


def train(config: TrainConfig, data_yaml: str | Path) -> TrainResult:
    """Run YOLOv8 training with the given config."""
    from ultralytics import YOLO

    model = YOLO(config.model_name)

    results: Any = model.train(
        data=str(data_yaml),
        epochs=config.epochs,
        imgsz=config.image_size,
        batch=config.batch_size,
        lr0=config.lr,
        optimizer=config.optimizer,
        weight_decay=config.weight_decay,
        warmup_epochs=config.warmup_epochs,
        patience=config.patience,
        device=config.device,
        project=config.project,
        name=config.name,
        exist_ok=True,
        flipud=config.augmentation.vertical_flip_prob,
        fliplr=config.augmentation.horizontal_flip_prob,
        degrees=config.augmentation.rotation_degrees,
        scale=config.augmentation.scale_range[1] - 1.0,
    )

    best_path = Path(config.project) / config.name / "weights" / "best.pt"
    metrics = {}
    if results and hasattr(results, "results_dict"):
        metrics = dict(results.results_dict)

    return TrainResult(
        best_model_path=str(best_path),
        metrics=metrics,
        epochs_completed=config.epochs,
    )


def evaluate(model_path: str | Path, data_yaml: str | Path) -> EvalResult:
    """Evaluate a trained model and return mAP metrics."""
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    results: Any = model.val(data=str(data_yaml))

    per_class: dict[str, dict[str, float]] = {}
    if hasattr(results, "names") and hasattr(results, "maps"):
        for i, name in results.names.items():
            per_class[name] = {"map50_95": float(results.maps[i])}

    return EvalResult(
        map50=float(getattr(results, "map50", 0.0)),
        map50_95=float(getattr(results, "map", 0.0)),
        precision=float(getattr(results, "mp", 0.0)),
        recall=float(getattr(results, "mr", 0.0)),
        per_class=per_class,
    )
