"""YOLO-format dataset exporter."""

from __future__ import annotations

import random
import shutil
from pathlib import Path

import yaml

from .config import ALConfig
from .pre_labeler import PseudoLabel


class YOLOExporter:
    def __init__(self, config: ALConfig):
        self._config = config

    # ------------------------------------------------------------------

    def export(
        self,
        labels: dict[str, list[PseudoLabel]],
        output_dir: str,
    ) -> str:
        out = Path(output_dir)
        for sub in ("images/train", "images/val", "labels/train", "labels/val"):
            (out / sub).mkdir(parents=True, exist_ok=True)

        paths = list(labels.keys())
        train_paths, val_paths = self.split_train_val(paths)

        for p in train_paths:
            self._copy_and_write(p, labels[p], out, "train")
        for p in val_paths:
            self._copy_and_write(p, labels[p], out, "val")

        yaml_path = self.generate_data_yaml(str(out))
        return yaml_path

    # ------------------------------------------------------------------

    def _copy_and_write(
        self,
        image_path: str,
        pls: list[PseudoLabel],
        out: Path,
        split: str,
    ) -> None:
        src = Path(image_path)
        if src.exists():
            shutil.copy2(src, out / "images" / split / src.name)
        label_path = out / "labels" / split / (src.stem + ".txt")
        self.write_label_file(image_path, pls, str(label_path))

    # ------------------------------------------------------------------

    def write_label_file(
        self,
        image_path: str,
        labels: list[PseudoLabel],
        output_path: str,
    ) -> None:
        lines: list[str] = []
        for pl in labels:
            coords = f"{pl.x_center:.6f} {pl.y_center:.6f} {pl.width:.6f} {pl.height:.6f}"
            line = f"{pl.class_id} {coords}"
            if self._config.export_confidence_scores:
                line += f" {pl.confidence:.4f}"
            lines.append(line)
        Path(output_path).write_text("\n".join(lines) + ("\n" if lines else ""))

    # ------------------------------------------------------------------

    def generate_data_yaml(self, output_dir: str) -> str:
        out = Path(output_dir)
        data = {
            "path": str(out.resolve()),
            "train": "images/train",
            "val": "images/val",
            "names": {i: n for i, n in enumerate(self._config.class_names)},
            "nc": len(self._config.class_names),
        }
        yaml_path = out / "data.yaml"
        yaml_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        return str(yaml_path)

    # ------------------------------------------------------------------

    def split_train_val(
        self, image_paths: list[str], val_ratio: float = 0.2
    ) -> tuple[list[str], list[str]]:
        paths = list(image_paths)
        random.Random(42).shuffle(paths)
        split = int(len(paths) * (1 - val_ratio))
        return paths[:split], paths[split:]

    # ------------------------------------------------------------------

    def export_statistics(self, labels: dict[str, list[PseudoLabel]]) -> dict:
        total_images = len(labels)
        total_labels = sum(len(v) for v in labels.values())
        class_counts: dict[str, int] = {}
        for pls in labels.values():
            for pl in pls:
                class_counts[pl.class_name] = class_counts.get(pl.class_name, 0) + 1

        return {
            "total_images": total_images,
            "total_labels": total_labels,
            "avg_labels_per_image": total_labels / max(total_images, 1),
            "class_distribution": class_counts,
        }
