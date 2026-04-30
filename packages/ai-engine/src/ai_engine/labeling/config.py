from __future__ import annotations

from dataclasses import dataclass, field


def default_class_prompts() -> dict[str, list[str]]:
    return {
        "rust": [
            "rust on metal surface",
            "corrosion on steel",
            "oxidation on hull",
            "rust stain",
        ],
        "damage": [
            "structural damage",
            "crack on metal",
            "dent on hull",
            "broken weld",
        ],
        "leak": [
            "oil leak",
            "water leak dripping",
            "fluid leak stain on surface",
        ],
        "missing_label": [
            "location where safety sign should be",
            "empty mounting point for label",
        ],
        "cargo_lashing": [
            "loose lashing rod",
            "broken turnbuckle",
            "damaged cargo wire",
            "missing securing equipment",
        ],
    }


@dataclass
class ALConfig:
    image_dir: str
    output_dir: str
    model_cache_dir: str = "models/al_cache"

    class_names: list[str] = field(
        default_factory=lambda: [
            "rust",
            "damage",
            "leak",
            "missing_label",
            "cargo_lashing",
        ]
    )
    class_prompts: dict[str, list[str]] = field(default_factory=default_class_prompts)

    # SimCLR
    simclr_embedding_dim: int = 128
    simclr_backbone: str = "resnet50"
    num_clusters: int = 20

    # Active Learning
    initial_batch_size: int = 50
    batch_size: int = 30
    max_rounds: int = 10
    target_accuracy: float = 0.90

    # Pre-labeling
    confidence_threshold_auto: float = 0.7
    confidence_threshold_discard: float = 0.3
    grounding_dino_model: str = "IDEA-Research/grounding-dino-tiny"
    sam_model: str = "facebook/sam-vit-base"

    # BABA
    baba_alpha_prior: float = 1.0
    baba_beta_prior: float = 1.0

    # GP
    gp_kernel: str = "rbf"
    gp_length_scale: float = 1.0

    # Object Discovery
    discovery_num_patches: int = 1000
    discovery_patch_sizes: list[int] = field(default_factory=lambda: [32, 64, 128])

    # Output
    yolo_format: bool = True
    export_confidence_scores: bool = False
