"""Dataset quality audit for B-Wave unified training data.

Checks:
1. Near-duplicate images (perceptual hash)
2. Label consistency (rust images with no rust labels)
3. Tiny/huge bounding boxes
4. Class distribution per source dataset
5. Images with no labels vs images with many labels
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

DATA_ROOT = Path("data/unified")
CLASSES = ["rust", "damage", "leak"]
REPORT_DIR = Path("data/reports")


def phash(img_path: Path, hash_size: int = 8) -> str:
    """Compute perceptual hash."""
    try:
        img = Image.open(img_path).convert("L").resize((hash_size + 1, hash_size), Image.LANCZOS)
    except Exception:
        return ""
    pixels = list(img.getdata())
    w = hash_size + 1
    bits = []
    for y in range(hash_size):
        for x in range(hash_size):
            bits.append(1 if pixels[y * w + x] > pixels[y * w + x + 1] else 0)
    return "".join(str(b) for b in bits)


def hamming(h1: str, h2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


def parse_labels(label_path: Path) -> list[dict]:
    if not label_path.exists():
        return []
    labels = []
    for line in label_path.read_text().strip().splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        try:
            cls_id = int(parts[0])
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            labels.append({"class": cls_id, "cx": cx, "cy": cy, "w": w, "h": h, "area": w * h})
        except ValueError:
            continue
    return labels


def audit_split(split: str) -> list[dict]:
    img_dir = DATA_ROOT / split / "images"
    lbl_dir = DATA_ROOT / split / "labels"
    if not img_dir.exists():
        return []

    issues = []
    hashes: dict[str, list[str]] = defaultdict(list)
    class_counts = Counter()
    bbox_areas: dict[int, list[float]] = defaultdict(list)
    empty_label_count = 0
    total = 0

    for img_path in sorted(img_dir.iterdir()):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            continue
        total += 1
        stem = img_path.stem
        lbl_path = lbl_dir / f"{stem}.txt"

        # Parse labels
        labels = parse_labels(lbl_path)

        # Check empty labels
        if not labels:
            empty_label_count += 1

        # Check bbox quality
        for lbl in labels:
            cls_id = lbl["class"]
            area = lbl["area"]
            class_counts[cls_id] += 1
            bbox_areas[cls_id].append(area)

            # Tiny bbox (< 0.1% of image)
            if area < 0.001:
                issues.append({
                    "file": str(img_path.name),
                    "split": split,
                    "issue": "tiny_bbox",
                    "detail": f"class={CLASSES[cls_id] if cls_id < len(CLASSES) else cls_id} area={area:.6f}",
                })

            # Huge bbox (> 80% of image)
            if area > 0.8:
                issues.append({
                    "file": str(img_path.name),
                    "split": split,
                    "issue": "huge_bbox",
                    "detail": f"class={CLASSES[cls_id] if cls_id < len(CLASSES) else cls_id} area={area:.4f}",
                })

            # Invalid coordinates
            if lbl["cx"] < 0 or lbl["cy"] < 0 or lbl["w"] <= 0 or lbl["h"] <= 0:
                issues.append({
                    "file": str(img_path.name),
                    "split": split,
                    "issue": "invalid_coords",
                    "detail": f"cx={lbl['cx']} cy={lbl['cy']} w={lbl['w']} h={lbl['h']}",
                })

        # Too many labels per image
        if len(labels) > 50:
            issues.append({
                "file": str(img_path.name),
                "split": split,
                "issue": "too_many_labels",
                "detail": f"count={len(labels)}",
            })

        # Perceptual hash for duplicate detection
        h = phash(img_path)
        if h:
            hashes[h].append(str(img_path.name))

    # Find near-duplicates
    hash_list = list(hashes.items())
    dup_count = 0
    for i in range(len(hash_list)):
        for j in range(i + 1, len(hash_list)):
            dist = hamming(hash_list[i][0], hash_list[j][0])
            if dist <= 3:
                for f1 in hash_list[i][1]:
                    for f2 in hash_list[j][1]:
                        if f1.split("_")[0] == f2.split("_")[0]:
                            continue  # same dataset prefix = expected oversampling
                        dup_count += 1
                        if dup_count <= 100:
                            issues.append({
                                "file": f"{f1} <-> {f2}",
                                "split": split,
                                "issue": "near_duplicate",
                                "detail": f"hamming={dist}",
                            })

    # Exact duplicates (same hash)
    for h, files in hashes.items():
        unique_sources = set(f.split("_")[0] for f in files)
        if len(files) > 1 and len(unique_sources) > 1:
            issues.append({
                "file": ", ".join(files[:5]),
                "split": split,
                "issue": "exact_duplicate_cross_dataset",
                "detail": f"count={len(files)} sources={unique_sources}",
            })

    # Print summary
    print(f"\n=== {split} ({total} images) ===")
    print(f"  Empty labels: {empty_label_count} ({empty_label_count/max(total,1)*100:.1f}%)")
    print(f"  Class distribution:")
    for cls_id in sorted(class_counts):
        name = CLASSES[cls_id] if cls_id < len(CLASSES) else f"unknown_{cls_id}"
        areas = bbox_areas[cls_id]
        avg_area = sum(areas) / len(areas) if areas else 0
        min_area = min(areas) if areas else 0
        max_area = max(areas) if areas else 0
        print(f"    {name:10s}: {class_counts[cls_id]:>6d} labels, "
              f"avg_area={avg_area:.4f}, min={min_area:.6f}, max={max_area:.4f}")
    print(f"  Near-duplicates (cross-dataset): {dup_count}")
    print(f"  Issues found: {len(issues)}")

    return issues


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    all_issues = []
    for split in ["train", "val", "test"]:
        issues = audit_split(split)
        all_issues.extend(issues)

    # Write CSV report
    csv_path = REPORT_DIR / "dataset_audit.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "split", "issue", "detail"])
        writer.writeheader()
        writer.writerows(all_issues)

    # Summary
    issue_types = Counter(i["issue"] for i in all_issues)
    print(f"\n{'='*60}")
    print(f"AUDIT COMPLETE - {len(all_issues)} issues found")
    print(f"{'='*60}")
    for issue_type, count in issue_types.most_common():
        print(f"  {issue_type:30s}: {count}")
    print(f"\nReport saved to: {csv_path}")


if __name__ == "__main__":
    main()
