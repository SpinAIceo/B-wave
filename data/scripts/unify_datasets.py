"""Unify 6 raw datasets into a single YOLO-format dataset for B-Wave training.

Datasets handled:
  1. NEU-DET       — VOC XML, 6 steel surface defect classes
  2. GC10-DET      — VOC XML, 10 steel surface defect classes (Chinese names)
  3. CODEBRIM      — VOC XML with multi-label defect flags
  4. SDNET2018     — Classification only (Cracked/Non-cracked), no bboxes
  5. Roboflow RAM Corrosion — YOLO segmentation polygon, 1 class
  6. Roboflow Pipe Defect   — YOLO segmentation polygon, 3 classes

Output: YOLO detection format compatible with ultralytics training.
"""

from __future__ import annotations

import argparse
import logging
import random
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

DEFECT_CLASSES = ["rust", "damage", "leak", "missing_label", "cargo_lashing"]

NEUDET_CLASS_MAP = {
    "pitted_surface": 0,
    "rolled-in_scale": 0,
    "crazing": 1,
    "inclusion": 1,
    "patches": 1,
    "scratches": 1,
}

GC10_CLASS_MAP = {
    "1_chongkong": 1,
    "2_hanfeng": 1,
    "3_yueyawan": 1,
    "4_shuiban": 2,
    "5_youban": 2,
    "6_siban": 1,
    "7_yiwu": 1,
    "8_yahen": 1,
    "9_zhehen": 1,
    "10_yaozhe": 1,
    "10_yaozhed": 1,
    "d": 1,
}

CODEBRIM_CLASS_MAP = {
    "CorrosionStain": 0,
    "Crack": 1,
    "Spallation": 1,
    "Efflorescence": 1,
    "ExposedBars": 1,
}

ROBOFLOW_PIPE_CLASS_MAP = {
    0: 1,  # Crack -> damage
    1: 0,  # corrosion -> rust
    2: 1,  # weld-defect -> damage
}

SDNET_MAX_NEGATIVES = 2000
TRAIN_RATIO = 0.80
VAL_RATIO = 0.15
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
OVERSAMPLE_TARGET_RATIO = 0.15

log = logging.getLogger("unify")


@dataclass
class DataEntry:
    src_image_path: Path
    dest_image_name: str
    yolo_lines: list[str]
    dataset_name: str
    split: str | None = None


@dataclass
class UnifyStats:
    per_dataset: Counter = field(default_factory=Counter)
    per_class: Counter = field(default_factory=Counter)
    per_split: Counter = field(default_factory=Counter)
    per_dataset_split: dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    corrupt: list[str] = field(default_factory=list)

    def record(self, entry: DataEntry) -> None:
        self.per_dataset[entry.dataset_name] += 1
        self.per_split[entry.split] += 1
        self.per_dataset_split[entry.dataset_name][entry.split] += 1
        for line in entry.yolo_lines:
            cls_id = int(line.split()[0])
            self.per_class[DEFECT_CLASSES[cls_id]] += 1

    def report(self) -> str:
        lines = [
            "",
            "=" * 72,
            f"{'Dataset':<22} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}",
            "-" * 72,
        ]
        for ds in sorted(self.per_dataset_split):
            s = self.per_dataset_split[ds]
            total = s["train"] + s["val"] + s["test"]
            lines.append(f"{ds:<22} {s['train']:>7} {s['val']:>7} {s['test']:>7} {total:>7}")
        lines.append("-" * 72)
        lines.append(
            f"{'TOTAL':<22} {self.per_split['train']:>7} "
            f"{self.per_split['val']:>7} {self.per_split['test']:>7} "
            f"{sum(self.per_split.values()):>7}"
        )
        lines.append("")
        lines.append("Class distribution (label lines):")
        for cls_name in DEFECT_CLASSES:
            count = self.per_class.get(cls_name, 0)
            lines.append(f"  {cls_name:<20} {count:>7}")
        if self.corrupt:
            lines.append(f"\nCorrupt/unreadable images skipped: {len(self.corrupt)}")
        missing = [c for c in DEFECT_CLASSES if self.per_class.get(c, 0) == 0]
        if missing:
            lines.append(f"\nWARNING: No training samples for classes: {missing}")
        lines.append("=" * 72)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# VOC XML helpers
# ---------------------------------------------------------------------------

def voc_bbox_to_yolo(xmin: float, ymin: float, xmax: float, ymax: float,
                     img_w: int, img_h: int) -> tuple[float, float, float, float]:
    cx = (xmin + xmax) / 2.0 / img_w
    cy = (ymin + ymax) / 2.0 / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h
    return (
        max(0.0, min(1.0, cx)),
        max(0.0, min(1.0, cy)),
        max(0.0, min(1.0, w)),
        max(0.0, min(1.0, h)),
    )


def parse_voc_size(root: ET.Element) -> tuple[int, int]:
    size = root.find("size")
    if size is None:
        return 0, 0
    w = int(size.findtext("width", "0"))
    h = int(size.findtext("height", "0"))
    return w, h


def parse_voc_bbox(obj: ET.Element) -> tuple[float, float, float, float] | None:
    bb = obj.find("bndbox")
    if bb is None:
        return None
    try:
        return (
            float(bb.findtext("xmin", "0")),
            float(bb.findtext("ymin", "0")),
            float(bb.findtext("xmax", "0")),
            float(bb.findtext("ymax", "0")),
        )
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Polygon -> bbox helper (for Roboflow segmentation labels)
# ---------------------------------------------------------------------------

def polygon_to_yolo_bbox(coords: list[float]) -> tuple[float, float, float, float] | None:
    if len(coords) < 4 or len(coords) % 2 != 0:
        return None
    xs = coords[0::2]
    ys = coords[1::2]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    w = max_x - min_x
    h = max_y - min_y
    if w <= 0 or h <= 0:
        return None
    return (
        max(0.0, min(1.0, cx)),
        max(0.0, min(1.0, cy)),
        max(0.0, min(1.0, w)),
        max(0.0, min(1.0, h)),
    )


def fmt_yolo(cls_id: int, cx: float, cy: float, w: float, h: float) -> str:
    return f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


# ---------------------------------------------------------------------------
# Dataset converters
# ---------------------------------------------------------------------------

def convert_neudet(raw_root: Path) -> list[DataEntry]:
    base = raw_root / "neu-det" / "NEU-DET"
    entries: list[DataEntry] = []

    for split_name, split_dir in [("train", "train"), ("val", "validation")]:
        ann_dir = base / split_dir / "annotations"
        img_base = base / split_dir / "images"
        if not ann_dir.exists():
            log.warning("NEU-DET %s annotations not found at %s", split_name, ann_dir)
            continue
        for xml_path in sorted(ann_dir.glob("*.xml")):
            try:
                tree = ET.parse(xml_path)
            except ET.ParseError:
                log.warning("NEU-DET: failed to parse %s", xml_path)
                continue
            root = tree.getroot()
            img_w, img_h = parse_voc_size(root)
            if img_w == 0 or img_h == 0:
                continue
            filename = root.findtext("filename", "")
            if not filename:
                continue

            img_path = None
            for cls_folder in img_base.iterdir():
                candidate = cls_folder / filename
                if candidate.exists():
                    img_path = candidate
                    break
            if img_path is None:
                flat = img_base / filename
                if flat.exists():
                    img_path = flat
            if img_path is None:
                log.warning("NEU-DET: image not found for %s", filename)
                continue

            yolo_lines = []
            for obj in root.iter("object"):
                name = obj.findtext("name", "").strip()
                cls_id = NEUDET_CLASS_MAP.get(name)
                if cls_id is None:
                    log.warning("NEU-DET: unknown class '%s'", name)
                    continue
                bbox = parse_voc_bbox(obj)
                if bbox is None:
                    continue
                cx, cy, w, h = voc_bbox_to_yolo(*bbox, img_w, img_h)
                yolo_lines.append(fmt_yolo(cls_id, cx, cy, w, h))

            dest_name = f"neudet_{img_path.stem}{img_path.suffix}"
            entries.append(DataEntry(img_path, dest_name, yolo_lines, "NEU-DET", split_name))

    return entries


def convert_gc10det(raw_root: Path) -> list[DataEntry]:
    base = raw_root / "gc10-det"
    entries: list[DataEntry] = []

    img_index: dict[str, list[Path]] = defaultdict(list)
    for folder_num in range(1, 11):
        folder = base / str(folder_num)
        if not folder.exists():
            continue
        for img_path in folder.iterdir():
            if img_path.suffix.lower() in IMAGE_EXTS:
                img_index[img_path.name].append(img_path)

    label_dir = base / "lable"
    if not label_dir.exists():
        log.warning("GC10-DET: label directory not found")
        return entries

    for xml_path in sorted(label_dir.glob("*.xml")):
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            log.warning("GC10-DET: failed to parse %s", xml_path)
            continue
        root = tree.getroot()
        img_w, img_h = parse_voc_size(root)
        if img_w == 0 or img_h == 0:
            continue
        filename = root.findtext("filename", "")
        if not filename:
            continue

        candidates = img_index.get(filename, [])
        if not candidates:
            log.warning("GC10-DET: image not found for %s", filename)
            continue
        img_path = candidates[0]

        yolo_lines = []
        for obj in root.iter("object"):
            name = obj.findtext("name", "").strip()
            cls_id = GC10_CLASS_MAP.get(name)
            if cls_id is None:
                log.warning("GC10-DET: unknown class '%s'", name)
                continue
            bbox = parse_voc_bbox(obj)
            if bbox is None:
                continue
            cx, cy, w, h = voc_bbox_to_yolo(*bbox, img_w, img_h)
            yolo_lines.append(fmt_yolo(cls_id, cx, cy, w, h))

        folder_name = img_path.parent.name
        dest_name = f"gc10_{folder_name}_{img_path.stem}{img_path.suffix}"
        entries.append(DataEntry(img_path, dest_name, yolo_lines, "GC10-DET"))

    return entries


def convert_codebrim(raw_root: Path) -> list[DataEntry]:
    base = raw_root / "codebrim" / "original_dataset"
    entries: list[DataEntry] = []
    ann_dir = base / "annotations"
    img_dir = base / "images"

    if not ann_dir.exists():
        log.warning("CODEBRIM: annotations not found at %s", ann_dir)
        return entries

    annotated_stems: set[str] = set()

    for xml_path in sorted(ann_dir.glob("*.xml")):
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            log.warning("CODEBRIM: failed to parse %s", xml_path)
            continue
        root = tree.getroot()
        img_w, img_h = parse_voc_size(root)
        if img_w == 0 or img_h == 0:
            continue
        filename = root.findtext("filename", "")
        if not filename:
            continue

        img_path = img_dir / filename
        if not img_path.exists():
            log.warning("CODEBRIM: image not found: %s", img_path)
            continue
        annotated_stems.add(img_path.stem)

        yolo_lines = []
        for obj in root.iter("object"):
            bbox = parse_voc_bbox(obj)
            if bbox is None:
                continue
            cx, cy, w, h = voc_bbox_to_yolo(*bbox, img_w, img_h)

            defect_el = obj.find("Defect")
            if defect_el is None:
                continue

            classes_for_bbox: set[int] = set()
            for defect_name, bwave_cls in CODEBRIM_CLASS_MAP.items():
                val = defect_el.findtext(defect_name, "0").strip()
                if val == "1":
                    classes_for_bbox.add(bwave_cls)

            for cls_id in sorted(classes_for_bbox):
                yolo_lines.append(fmt_yolo(cls_id, cx, cy, w, h))

        dest_name = f"codebrim_{img_path.stem}{img_path.suffix}"
        entries.append(DataEntry(img_path, dest_name, yolo_lines, "CODEBRIM"))

    if img_dir.exists():
        for img_path in sorted(img_dir.iterdir()):
            if img_path.suffix.lower() in IMAGE_EXTS and img_path.stem not in annotated_stems:
                dest_name = f"codebrim_{img_path.stem}{img_path.suffix}"
                entries.append(DataEntry(img_path, dest_name, [], "CODEBRIM"))

    return entries


def convert_sdnet2018(raw_root: Path, rng: random.Random) -> list[DataEntry]:
    base = raw_root / "sdnet2018"
    entries: list[DataEntry] = []

    surface_types = ["Decks", "Pavements", "Walls"]

    for surface in surface_types:
        cracked_dir = base / surface / "Cracked"
        if cracked_dir.exists():
            for img_path in sorted(cracked_dir.iterdir()):
                if img_path.suffix.lower() in IMAGE_EXTS:
                    dest_name = f"sdnet_{surface.lower()}_{img_path.stem}{img_path.suffix}"
                    yolo_lines = [fmt_yolo(1, 0.5, 0.5, 1.0, 1.0)]
                    entries.append(DataEntry(img_path, dest_name, yolo_lines, "SDNET2018"))

    neg_pools: dict[str, list[Path]] = {}
    total_neg = 0
    for surface in surface_types:
        noncracked_dir = base / surface / "Non-cracked"
        if noncracked_dir.exists():
            imgs = sorted(
                p for p in noncracked_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS
            )
            neg_pools[surface] = imgs
            total_neg += len(imgs)

    if total_neg > 0:
        for surface, imgs in neg_pools.items():
            quota = int(SDNET_MAX_NEGATIVES * len(imgs) / total_neg)
            sampled = rng.sample(imgs, min(quota, len(imgs)))
            for img_path in sampled:
                dest_name = f"sdnet_{surface.lower()}_{img_path.stem}{img_path.suffix}"
                entries.append(DataEntry(img_path, dest_name, [], "SDNET2018"))

    return entries


def _convert_roboflow_yolo(raw_root: Path, dataset_dir: str, dataset_name: str,
                           class_map: dict[int, int], prefix: str) -> list[DataEntry]:
    base = raw_root / dataset_dir
    entries: list[DataEntry] = []

    split_map = {"train": "train", "valid": "val", "test": "test"}

    for rf_split, bwave_split in split_map.items():
        img_dir = base / rf_split / "images"
        lbl_dir = base / rf_split / "labels"
        if not img_dir.exists():
            continue

        for img_path in sorted(img_dir.iterdir()):
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue

            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            yolo_lines: list[str] = []

            if lbl_path.exists():
                for line in lbl_path.read_text().strip().splitlines():
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    try:
                        orig_cls = int(parts[0])
                    except ValueError:
                        continue

                    new_cls = class_map.get(orig_cls)
                    if new_cls is None:
                        continue

                    coords = [float(x) for x in parts[1:]]

                    if len(coords) == 4:
                        cx, cy, w, h = coords
                    else:
                        result = polygon_to_yolo_bbox(coords)
                        if result is None:
                            continue
                        cx, cy, w, h = result

                    yolo_lines.append(fmt_yolo(new_cls, cx, cy, w, h))

            dest_name = f"{prefix}_{img_path.stem}{img_path.suffix}"
            entries.append(DataEntry(img_path, dest_name, yolo_lines, dataset_name, bwave_split))

    return entries


def convert_roboflow_corrosion(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-corrosion", "RBF-Corrosion", {0: 0}, "rbfcorr"
    )


def convert_roboflow_pipe_defect(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-pipe-defect", "RBF-PipeDefect", ROBOFLOW_PIPE_CLASS_MAP, "rbfpipe"
    )


def convert_roboflow_oil_spill(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-oil-spill", "RBF-OilSpill", {0: 2}, "rbfoil1"
    )


def convert_roboflow_oil_spill2(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-oil-spill2", "RBF-OilSpill2", {0: 2}, "rbfoil2"
    )


def convert_roboflow_pipe_leak(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-pipe-leak", "RBF-PipeLeak",
        {0: 1, 1: 2, 2: 2},  # crack->damage, gas->leak, water->leak
        "rbfleak"
    )


def convert_roboflow_wire_rope(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-wire-rope", "RBF-WireRope",
        {0: 4, 1: 4, 2: 4},  # break/thunderbolt/wear -> cargo_lashing
        "rbfwire"
    )


def convert_roboflow_fastener(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-fastener", "RBF-Fastener",
        {2: 4, 3: 4, 4: 4},  # fastener2_broken/fastener_broken/missing -> cargo_lashing
        "rbffast"
    )


def convert_roboflow_fire_safety(raw_root: Path) -> list[DataEntry]:
    return _convert_roboflow_yolo(
        raw_root, "roboflow-fire-safety", "RBF-FireSafety",
        {0: 3},  # extinguisher -> missing_label (sign/equipment presence)
        "rbffire"
    )


def convert_hazmat13(raw_root: Path) -> list[DataEntry]:
    """Convert HAZMAT-13 VOC XML dataset. All 13 hazmat classes -> missing_label."""
    base = raw_root / "hazmat13" / "original_full"
    if not base.exists():
        base = raw_root / "hazmat13" / "original"
    entries: list[DataEntry] = []

    img_dir = base / "JPEGImages"
    ann_dir = base / "bboxes" / "annotations"
    if not img_dir.exists() or not ann_dir.exists():
        log.warning("HAZMAT-13: directories not found at %s", base)
        return entries

    for xml_path in sorted(ann_dir.glob("*.xml")):
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            continue
        root = tree.getroot()
        img_w, img_h = parse_voc_size(root)
        if img_w == 0 or img_h == 0:
            continue
        filename = root.findtext("filename", "")
        if not filename:
            continue

        img_path = img_dir / filename
        if not img_path.exists():
            for ext in [".jpg", ".png", ".jpeg"]:
                candidate = img_dir / (xml_path.stem + ext)
                if candidate.exists():
                    img_path = candidate
                    break
        if not img_path.exists():
            continue

        yolo_lines = []
        for obj in root.iter("object"):
            bbox = parse_voc_bbox(obj)
            if bbox is None:
                continue
            cx, cy, w, h = voc_bbox_to_yolo(*bbox, img_w, img_h)
            yolo_lines.append(fmt_yolo(3, cx, cy, w, h))  # all -> missing_label(3)

        dest_name = f"hazmat_{img_path.stem}{img_path.suffix}"
        entries.append(DataEntry(img_path, dest_name, yolo_lines, "HAZMAT-13"))

    return entries


# ---------------------------------------------------------------------------
# Split assignment
# ---------------------------------------------------------------------------

def oversample_minority(entries: list[DataEntry], rng: random.Random) -> list[DataEntry]:
    """Oversample images containing minority classes to reduce imbalance."""
    class_counts: Counter = Counter()
    for e in entries:
        for line in e.yolo_lines:
            cls_id = int(line.split()[0])
            class_counts[cls_id] += 1

    if not class_counts:
        return entries

    max_count = max(class_counts.values())
    target_count = int(max_count * OVERSAMPLE_TARGET_RATIO)

    entries_by_class: dict[int, list[DataEntry]] = defaultdict(list)
    for e in entries:
        classes_in_entry = {int(line.split()[0]) for line in e.yolo_lines}
        for cls_id in classes_in_entry:
            entries_by_class[cls_id].append(e)

    extra: list[DataEntry] = []
    for cls_id, count in class_counts.items():
        if count >= target_count:
            continue
        pool = entries_by_class.get(cls_id, [])
        if not pool:
            continue
        needed = target_count - count
        num_copies = needed // len(pool) + 1
        sampled = pool * num_copies
        rng.shuffle(sampled)
        for i, entry in enumerate(sampled[:needed]):
            extra.append(DataEntry(
                src_image_path=entry.src_image_path,
                dest_image_name=f"os{i}_{entry.dest_image_name}",
                yolo_lines=list(entry.yolo_lines),
                dataset_name=entry.dataset_name,
                split=entry.split,
            ))

    if extra:
        new_counts: Counter = Counter()
        for e in extra:
            for line in e.yolo_lines:
                new_counts[int(line.split()[0])] += 1
        for cls_id in sorted(new_counts):
            log.info("  Oversampled class %d (%s): +%d labels",
                     cls_id, DEFECT_CLASSES[cls_id], new_counts[cls_id])

    return entries + extra


def assign_splits(entries: list[DataEntry], rng: random.Random) -> None:
    by_dataset: dict[str, list[DataEntry]] = defaultdict(list)
    for e in entries:
        if e.split is None:
            by_dataset[e.dataset_name].append(e)

    for ds_entries in by_dataset.values():
        rng.shuffle(ds_entries)
        n = len(ds_entries)
        train_end = int(n * TRAIN_RATIO)
        val_end = int(n * (TRAIN_RATIO + VAL_RATIO))
        for e in ds_entries[:train_end]:
            e.split = "train"
        for e in ds_entries[train_end:val_end]:
            e.split = "val"
        for e in ds_entries[val_end:]:
            e.split = "test"


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_output(entries: list[DataEntry], output_root: Path,
                 stats: UnifyStats, skip_validation: bool) -> None:
    for split in ("train", "val", "test"):
        (output_root / split / "images").mkdir(parents=True, exist_ok=True)
        (output_root / split / "labels").mkdir(parents=True, exist_ok=True)

    for entry in entries:
        if not skip_validation:
            try:
                img = Image.open(entry.src_image_path)
                img.verify()
            except Exception:
                stats.corrupt.append(str(entry.src_image_path))
                log.warning("Corrupt image skipped: %s", entry.src_image_path)
                continue

        split = entry.split or "train"
        dest_img = output_root / split / "images" / entry.dest_image_name
        dest_lbl = output_root / split / "labels" / (Path(entry.dest_image_name).stem + ".txt")

        shutil.copy2(entry.src_image_path, dest_img)

        label_text = "\n".join(entry.yolo_lines)
        if label_text:
            label_text += "\n"
        dest_lbl.write_text(label_text)

        stats.record(entry)


def write_data_yaml(output_root: Path) -> Path:
    yaml_path = output_root / "data.yaml"
    path_str = output_root.resolve().as_posix()
    names_block = "\n".join(f"  {i}: {name}" for i, name in enumerate(DEFECT_CLASSES))
    content = (
        f"path: {path_str}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"test: test/images\n"
        f"\n"
        f"nc: {len(DEFECT_CLASSES)}\n"
        f"names:\n"
        f"{names_block}\n"
    )
    yaml_path.write_text(content)
    return yaml_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Unify B-Wave training datasets")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-root", type=Path, default=Path("data/unified"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--datasets", type=str, default="all",
                        help="Comma-separated list: neudet,gc10,codebrim,sdnet,corrosion,pipe")
    parser.add_argument("--oversample", action="store_true",
                        help="Oversample minority classes to reduce imbalance")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    rng = random.Random(args.seed)

    enabled = set(args.datasets.split(",")) if args.datasets != "all" else {
        "neudet", "gc10", "codebrim", "sdnet", "corrosion", "pipe"
    }

    all_entries: list[DataEntry] = []

    converters = {
        "neudet": lambda: convert_neudet(args.raw_root),
        "gc10": lambda: convert_gc10det(args.raw_root),
        "codebrim": lambda: convert_codebrim(args.raw_root),
        "sdnet": lambda: convert_sdnet2018(args.raw_root, rng),
        "corrosion": lambda: convert_roboflow_corrosion(args.raw_root),
        "pipe": lambda: convert_roboflow_pipe_defect(args.raw_root),
        "oilspill": lambda: convert_roboflow_oil_spill(args.raw_root),
        "oilspill2": lambda: convert_roboflow_oil_spill2(args.raw_root),
        "pipeleak": lambda: convert_roboflow_pipe_leak(args.raw_root),
        "wirerope": lambda: convert_roboflow_wire_rope(args.raw_root),
        "fastener": lambda: convert_roboflow_fastener(args.raw_root),
        "firesafety": lambda: convert_roboflow_fire_safety(args.raw_root),
        "hazmat": lambda: convert_hazmat13(args.raw_root),
    }

    for name, converter in converters.items():
        if name not in enabled:
            continue
        log.info("Converting %s...", name)
        entries = converter()
        log.info("  -> %d entries", len(entries))
        all_entries.extend(entries)

    if args.oversample:
        log.info("Oversampling minority classes...")
        all_entries = oversample_minority(all_entries, rng)

    log.info("Assigning splits for datasets without pre-existing splits...")
    assign_splits(all_entries, rng)

    log.info("Total entries: %d", len(all_entries))

    if args.dry_run:
        stats = UnifyStats()
        for e in all_entries:
            stats.record(e)
        print(stats.report())
        return

    log.info("Writing output to %s...", args.output_root)
    stats = UnifyStats()
    write_output(all_entries, args.output_root, stats, args.skip_validation)

    yaml_path = write_data_yaml(args.output_root)
    log.info("data.yaml written to %s", yaml_path)

    print(stats.report())


if __name__ == "__main__":
    main()
