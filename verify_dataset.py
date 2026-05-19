#!/usr/bin/env python3
"""Verify a local TomatoPlantfactoryDataset extraction."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
CLASS_NAMES = {0: "green", 1: "red"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check image, Pascal VOC XML and YOLO TXT files."
    )
    parser.add_argument(
        "--root",
        default="TomatoPlantfactoryDataset",
        type=Path,
        help="Dataset root containing Images/, Annotations/ and labels/.",
    )
    return parser.parse_args()


def list_images(images_dir: Path) -> list[Path]:
    return sorted(path for path in images_dir.iterdir() if path.suffix in IMAGE_EXTENSIONS)


def count_xml_objects(xml_files: list[Path]) -> tuple[Counter[str], Counter[str]]:
    class_counts: Counter[str] = Counter()
    difficult_counts: Counter[str] = Counter()

    for xml_file in xml_files:
        root = ElementTree.parse(xml_file).getroot()
        for obj in root.findall("object"):
            name = (obj.findtext("name") or "unknown").strip()
            class_counts[name] += 1
            if (obj.findtext("difficult") or "0").strip() == "1":
                difficult_counts[name] += 1

    return class_counts, difficult_counts


def count_yolo_objects(label_files: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()

    for label_file in label_files:
        for line_number, line in enumerate(label_file.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 5:
                raise ValueError(f"{label_file}:{line_number} should have 5 columns")
            class_id = int(parts[0])
            for value in parts[1:]:
                number = float(value)
                if number < 0 or number > 1:
                    raise ValueError(
                        f"{label_file}:{line_number} has non-normalized value {value}"
                    )
            counts[CLASS_NAMES.get(class_id, f"class_{class_id}")] += 1

    return counts


def main() -> int:
    args = parse_args()
    dataset_root = args.root.resolve()
    images_dir = dataset_root / "Images"
    annotations_dir = dataset_root / "Annotations"
    labels_dir = dataset_root / "labels"

    missing_dirs = [
        directory for directory in (images_dir, annotations_dir, labels_dir) if not directory.is_dir()
    ]
    if missing_dirs:
        print("Missing required directories:", file=sys.stderr)
        for directory in missing_dirs:
            print(f"  - {directory}", file=sys.stderr)
        return 1

    images = list_images(images_dir)
    xml_files = sorted(annotations_dir.glob("*.xml"))
    label_files = sorted(labels_dir.glob("*.txt"))

    image_stems = {path.stem for path in images}
    xml_stems = {path.stem for path in xml_files}
    label_stems = {path.stem for path in label_files}

    missing_xml = sorted(image_stems - xml_stems)
    missing_labels = sorted(image_stems - label_stems)
    extra_xml = sorted(xml_stems - image_stems)
    extra_labels = sorted(label_stems - image_stems)

    xml_counts, xml_difficult = count_xml_objects(xml_files)
    yolo_counts = count_yolo_objects(label_files)

    print(f"Dataset root: {dataset_root}")
    print(f"Images: {len(images)}")
    print(f"Pascal VOC XML files: {len(xml_files)}")
    print(f"YOLO label files: {len(label_files)}")
    print()
    print("Pascal VOC object counts:")
    for name, count in sorted(xml_counts.items()):
        difficult = xml_difficult.get(name, 0)
        print(f"  {name}: {count} ({difficult} marked difficult)")
    print(f"  total: {sum(xml_counts.values())}")
    print()
    print("YOLO object counts:")
    for name, count in sorted(yolo_counts.items()):
        print(f"  {name}: {count}")
    print(f"  total: {sum(yolo_counts.values())}")

    problems = {
        "missing XML for images": missing_xml,
        "missing YOLO labels for images": missing_labels,
        "XML without images": extra_xml,
        "YOLO labels without images": extra_labels,
    }

    failed = False
    for label, stems in problems.items():
        if stems:
            failed = True
            preview = ", ".join(stems[:10])
            suffix = " ..." if len(stems) > 10 else ""
            print(f"\n{label}: {len(stems)}")
            print(f"  {preview}{suffix}")

    if failed:
        return 1

    print("\nOK: image, XML and YOLO file stems are aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
