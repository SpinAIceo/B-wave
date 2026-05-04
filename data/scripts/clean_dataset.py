"""Clean the unified dataset based on audit findings.

Removes:
1. Labels with tiny bboxes (area < 0.001)
2. Labels with huge bboxes (area > 0.8)
3. Labels with invalid coordinates
4. Cross-dataset near-duplicate images (keeps first occurrence)
5. Images with too many labels (>50)
"""

from __future__ import annotations

import shutil
from collections import Counter
from pathlib import Path

from PIL import Image

SRC = Path("data/unified")
DST = Path("data/unified-clean")
CLASSES = ["rust", "damage", "leak"]

MIN_AREA = 0.001
MAX_AREA = 0.80
MAX_LABELS = 50
HASH_SIZE = 8


def phash(img_path: Path) -> str:
    try:
        img = Image.open(img_path).convert("L").resize((HASH_SIZE + 1, HASH_SIZE), Image.LANCZOS)
    except Exception:
        return ""
    pixels = list(img.getdata())
    w = HASH_SIZE + 1
    bits = []
    for y in range(HASH_SIZE):
        for x in range(HASH_SIZE):
            bits.append(1 if pixels[y * w + x] > pixels[y * w + x + 1] else 0)
    return "".join(str(b) for b in bits)


def hamming(h1: str, h2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


def clean_labels(label_text: str) -> tuple[str, dict]:
    """Filter label lines, return cleaned text and stats."""
    stats = {"kept": 0, "tiny_removed": 0, "huge_removed": 0, "invalid_removed": 0}
    kept_lines = []
    for line in label_text.strip().splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            stats["invalid_removed"] += 1
            continue
        try:
            cls_id = int(parts[0])
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        except ValueError:
            stats["invalid_removed"] += 1
            continue

        if w <= 0 or h <= 0 or cx < 0 or cy < 0:
            stats["invalid_removed"] += 1
            continue

        area = w * h
        if area < MIN_AREA:
            stats["tiny_removed"] += 1
            continue
        if area > MAX_AREA:
            stats["huge_removed"] += 1
            continue

        kept_lines.append(line.strip())
        stats["kept"] += 1

    return "\n".join(kept_lines) + ("\n" if kept_lines else ""), stats


def process_split(split: str, seen_hashes: dict[str, str]) -> dict:
    src_img = SRC / split / "images"
    src_lbl = SRC / split / "labels"
    dst_img = DST / split / "images"
    dst_lbl = DST / split / "labels"
    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)

    totals = {
        "images_in": 0, "images_out": 0,
        "labels_kept": 0, "tiny_removed": 0, "huge_removed": 0,
        "invalid_removed": 0, "dup_removed": 0, "too_many_removed": 0,
    }
    class_before = Counter()
    class_after = Counter()

    for img_path in sorted(src_img.iterdir()):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            continue
        totals["images_in"] += 1
        stem = img_path.stem
        lbl_path = src_lbl / f"{stem}.txt"

        # Duplicate check (skip oversampled copies — they start with "os")
        if not stem.startswith("os"):
            h = phash(img_path)
            if h:
                source = stem.split("_")[0]
                matched = False
                for existing_h, existing_source in seen_hashes.items():
                    if hamming(h, existing_h) <= 3 and source != existing_source:
                        matched = True
                        break
                if matched:
                    totals["dup_removed"] += 1
                    continue
                seen_hashes[h] = source

        # Parse and count before
        raw_text = lbl_path.read_text() if lbl_path.exists() else ""
        for line in raw_text.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    class_before[int(parts[0])] += 1
                except ValueError:
                    pass

        # Clean labels
        cleaned, stats = clean_labels(raw_text)
        totals["labels_kept"] += stats["kept"]
        totals["tiny_removed"] += stats["tiny_removed"]
        totals["huge_removed"] += stats["huge_removed"]
        totals["invalid_removed"] += stats["invalid_removed"]

        # Too many labels check
        label_count = len(cleaned.strip().splitlines()) if cleaned.strip() else 0
        if label_count > MAX_LABELS:
            totals["too_many_removed"] += 1
            continue

        # Count after
        for line in cleaned.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    class_after[int(parts[0])] += 1
                except ValueError:
                    pass

        # Copy image and write cleaned labels
        shutil.copy2(img_path, dst_img / img_path.name)
        (dst_lbl / f"{stem}.txt").write_text(cleaned)
        totals["images_out"] += 1

    print(f"\n=== {split} ===")
    print(f"  Images: {totals['images_in']} -> {totals['images_out']} "
          f"(-{totals['images_in'] - totals['images_out']})")
    print(f"  Labels kept: {totals['labels_kept']}")
    print(f"  Tiny bbox removed: {totals['tiny_removed']}")
    print(f"  Huge bbox removed: {totals['huge_removed']}")
    print(f"  Invalid removed: {totals['invalid_removed']}")
    print(f"  Duplicates removed: {totals['dup_removed']}")
    print(f"  Too-many-labels removed: {totals['too_many_removed']}")
    print(f"  Class before: {dict(class_before)}")
    print(f"  Class after:  {dict(class_after)}")

    return totals


def main():
    if DST.exists():
        shutil.rmtree(DST)

    seen_hashes: dict[str, str] = {}
    grand = Counter()

    for split in ["train", "val", "test"]:
        totals = process_split(split, seen_hashes)
        for k, v in totals.items():
            grand[k] += v

    # Copy data.yaml with updated path
    yaml_path = DST / "data.yaml"
    path_str = DST.resolve().as_posix()
    yaml_path.write_text(
        f"path: {path_str}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"test: test/images\n"
        f"\n"
        f"nc: {len(CLASSES)}\n"
        f"names:\n"
        + "\n".join(f"  {i}: {n}" for i, n in enumerate(CLASSES))
        + "\n"
    )

    print(f"\n{'='*60}")
    print(f"CLEANING COMPLETE")
    print(f"{'='*60}")
    print(f"  Images: {grand['images_in']} -> {grand['images_out']} "
          f"(-{grand['images_in'] - grand['images_out']})")
    print(f"  Total labels kept: {grand['labels_kept']}")
    print(f"  Removed: tiny={grand['tiny_removed']} huge={grand['huge_removed']} "
          f"invalid={grand['invalid_removed']} dup={grand['dup_removed']} "
          f"too_many={grand['too_many_removed']}")
    print(f"\nClean dataset at: {DST}")
    print(f"data.yaml at: {yaml_path}")


if __name__ == "__main__":
    main()
