#!/usr/bin/env python3
"""Create a reproducible Ultralytics-style split for TomatoPlantfactoryDataset."""

from __future__ import annotations

import argparse
import csv
import os
import random
import shutil
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
CLASS_NAMES = ["green", "red"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create train/val/test folders for Ultralytics YOLO."
    )
    parser.add_argument(
        "--root",
        default="TomatoPlantfactoryDataset",
        type=Path,
        help="Dataset root containing Images/ and labels/.",
    )
    parser.add_argument(
        "--out",
        default="yolo_dataset",
        type=Path,
        help="Output directory for the YOLO split.",
    )
    parser.add_argument("--train", default=0.8, type=float, help="Train split ratio.")
    parser.add_argument("--val", default=0.1, type=float, help="Validation split ratio.")
    parser.add_argument("--seed", default=42, type=int, help="Random seed.")
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of creating symlinks.",
    )
    return parser.parse_args()


def list_images(images_dir: Path) -> list[Path]:
    return sorted(path for path in images_dir.iterdir() if path.suffix in IMAGE_EXTENSIONS)


def link_or_copy(source: Path, destination: Path, copy: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        destination.unlink()

    if copy:
        shutil.copy2(source, destination)
        return

    relative_source = os.path.relpath(source.resolve(), start=destination.parent.resolve())
    try:
        destination.symlink_to(relative_source)
    except OSError:
        shutil.copy2(source, destination)


def split_items(items: list[Path], train_ratio: float, val_ratio: float) -> dict[str, list[Path]]:
    if train_ratio <= 0 or val_ratio < 0 or train_ratio + val_ratio >= 1:
        raise ValueError("--train must be > 0, --val must be >= 0, and train + val must be < 1")

    train_count = round(len(items) * train_ratio)
    val_count = round(len(items) * val_ratio)

    return {
        "train": items[:train_count],
        "val": items[train_count : train_count + val_count],
        "test": items[train_count + val_count :],
    }


def write_data_yaml(output_dir: Path) -> None:
    names = "\n".join(f"  {index}: {name}" for index, name in enumerate(CLASS_NAMES))
    content = f"""path: {output_dir.resolve()}
train: images/train
val: images/val
test: images/test

names:
{names}
"""
    (output_dir / "data.yaml").write_text(content)


def write_manifest(output_dir: Path, splits: dict[str, list[Path]]) -> None:
    with (output_dir / "split_manifest.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["split", "image"])
        for split_name, images in splits.items():
            for image in images:
                writer.writerow([split_name, image.name])


def main() -> int:
    args = parse_args()
    dataset_root = args.root.resolve()
    output_dir = args.out.resolve()
    images_dir = dataset_root / "Images"
    labels_dir = dataset_root / "labels"

    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise SystemExit("Expected Images/ and labels/ under --root.")

    images = list_images(images_dir)
    missing_labels = [image.name for image in images if not (labels_dir / f"{image.stem}.txt").is_file()]
    if missing_labels:
        preview = ", ".join(missing_labels[:10])
        suffix = " ..." if len(missing_labels) > 10 else ""
        raise SystemExit(f"Missing labels for {len(missing_labels)} images: {preview}{suffix}")

    random.Random(args.seed).shuffle(images)
    splits = split_items(images, args.train, args.val)

    for split_name, split_images in splits.items():
        for image in split_images:
            label = labels_dir / f"{image.stem}.txt"
            link_or_copy(
                image,
                output_dir / "images" / split_name / image.name,
                copy=args.copy,
            )
            link_or_copy(
                label,
                output_dir / "labels" / split_name / label.name,
                copy=args.copy,
            )

    write_data_yaml(output_dir)
    write_manifest(output_dir, splits)

    print(f"Wrote split to {output_dir}")
    for split_name, split_images in splits.items():
        print(f"  {split_name}: {len(split_images)} images")
    print(f"Data config: {output_dir / 'data.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
