from __future__ import annotations

from dataclasses import dataclass, field

DEFECT_CLASSES = ["rust", "damage", "leak", "missing_label", "cargo_lashing"]


@dataclass
class AugmentationConfig:
    motion_blur_prob: float = 0.3
    motion_blur_kernel: int = 15
    salt_noise_prob: float = 0.2
    salt_noise_amount: float = 0.02
    brightness_range: tuple[float, float] = (0.5, 1.5)
    fog_prob: float = 0.15
    fog_alpha_range: tuple[float, float] = (0.1, 0.4)
    horizontal_flip_prob: float = 0.5
    vertical_flip_prob: float = 0.0
    rotation_degrees: float = 10.0
    scale_range: tuple[float, float] = (0.8, 1.2)


@dataclass
class TrainConfig:
    model_name: str = "yolov8n.pt"
    num_classes: int = 5
    class_names: list[str] = field(default_factory=lambda: list(DEFECT_CLASSES))
    image_size: int = 640
    batch_size: int = 16
    epochs: int = 100
    lr: float = 0.01
    optimizer: str = "AdamW"
    weight_decay: float = 0.0005
    warmup_epochs: int = 3
    patience: int = 20
    device: str = "cpu"
    project: str = "runs/train"
    name: str = "bwave-defect"
    augmentation: AugmentationConfig = field(default_factory=AugmentationConfig)
