from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, ImageFilter

if TYPE_CHECKING:
    from .config import AugmentationConfig


class MaritimeAugmentation:
    """Data augmentation pipeline simulating maritime conditions."""

    def __init__(self, config: AugmentationConfig):
        self.config = config
        self._rng = np.random.default_rng()

    def __call__(self, image: Image.Image) -> Image.Image:
        image = self._apply_motion_blur(image)
        image = self._apply_salt_noise(image)
        image = self._apply_brightness(image)
        image = self._apply_fog(image)
        return image

    def _apply_motion_blur(self, image: Image.Image) -> Image.Image:
        if self._rng.random() > self.config.motion_blur_prob:
            return image
        k = self.config.motion_blur_kernel
        kernel_size = max(3, k if k % 2 == 1 else k + 1)
        return image.filter(ImageFilter.BoxBlur(kernel_size // 3))

    def _apply_salt_noise(self, image: Image.Image) -> Image.Image:
        if self._rng.random() > self.config.salt_noise_prob:
            return image
        arr = np.array(image)
        amount = self.config.salt_noise_amount
        mask = self._rng.random(arr.shape[:2])
        arr[mask < amount / 2] = 255
        arr[mask > 1 - amount / 2] = 0
        return Image.fromarray(arr)

    def _apply_brightness(self, image: Image.Image) -> Image.Image:
        lo, hi = self.config.brightness_range
        factor = self._rng.uniform(lo, hi)
        arr = np.array(image, dtype=np.float32)
        arr = np.clip(arr * factor, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    def _apply_fog(self, image: Image.Image) -> Image.Image:
        if self._rng.random() > self.config.fog_prob:
            return image
        lo, hi = self.config.fog_alpha_range
        alpha = self._rng.uniform(lo, hi)
        arr = np.array(image, dtype=np.float32)
        fog = np.full_like(arr, 200.0)
        blended = arr * (1 - alpha) + fog * alpha
        return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))


class ShipDefectDataset:
    """YOLO-format dataset loader for ship defect images.

    Expected directory structure:
        data_dir/
        ├── images/
        │   ├── img001.jpg
        │   └── ...
        └── labels/
            ├── img001.txt   (YOLO format: class x_center y_center width height)
            └── ...
    """

    def __init__(
        self,
        data_dir: str | Path,
        image_size: int = 640,
        augmentation: MaritimeAugmentation | None = None,
    ):
        self.data_dir = Path(data_dir)
        self.image_size = image_size
        self.augmentation = augmentation
        self.image_dir = self.data_dir / "images"
        self.label_dir = self.data_dir / "labels"
        self.image_paths = self._discover_images()

    def _discover_images(self) -> list[Path]:
        if not self.image_dir.exists():
            return []
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        return sorted(p for p in self.image_dir.iterdir() if p.suffix.lower() in exts)

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> tuple[Image.Image, list[list[float]]]:
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")

        label_path = self.label_dir / f"{img_path.stem}.txt"
        labels = self._load_labels(label_path)

        if self.augmentation:
            image = self.augmentation(image)

        image = image.resize((self.image_size, self.image_size))
        return image, labels

    @staticmethod
    def _load_labels(label_path: Path) -> list[list[float]]:
        if not label_path.exists():
            return []
        labels = []
        for line in label_path.read_text().strip().splitlines():
            parts = line.strip().split()
            if len(parts) == 5:
                labels.append([float(x) for x in parts])
        return labels

    def generate_yolo_yaml(self, output_path: str | Path) -> Path:
        """Generate a YOLO data.yaml config for ultralytics training."""
        from .config import DEFECT_CLASSES

        output_path = Path(output_path)
        content = (
            f"path: {self.data_dir.resolve()}\n"
            f"train: images\n"
            f"val: images\n"
            f"nc: {len(DEFECT_CLASSES)}\n"
            f"names: {DEFECT_CLASSES}\n"
        )
        output_path.write_text(content)
        return output_path
