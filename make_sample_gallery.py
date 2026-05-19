#!/usr/bin/env python3
"""Build a dense image mosaic from local dataset samples."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a dense preview mosaic for the GitHub README."
    )
    parser.add_argument(
        "--root",
        default=Path("TomatoPlantfactoryDataset"),
        type=Path,
        help="Dataset root containing Images/.",
    )
    parser.add_argument(
        "--out",
        default=Path("assets/sample-gallery-dense.jpg"),
        type=Path,
        help="Output image path.",
    )
    parser.add_argument("--cols", default=20, type=int, help="Number of columns.")
    parser.add_argument(
        "--rows",
        default=0,
        type=int,
        help="Number of rows. Use 0 to fit all selected images.",
    )
    parser.add_argument("--tile-width", default=96, type=int, help="Tile width in pixels.")
    parser.add_argument("--tile-height", default=72, type=int, help="Tile height in pixels.")
    parser.add_argument(
        "--max-images",
        default=0,
        type=int,
        help="Maximum number of images. Use 0 to include all images.",
    )
    parser.add_argument("--quality", default=84, type=int, help="JPEG quality.")
    return parser.parse_args()


def list_images(images_dir: Path) -> list[Path]:
    return sorted(path for path in images_dir.iterdir() if path.suffix in IMAGE_EXTENSIONS)


def evenly_sample(items: list[Path], count: int) -> list[Path]:
    if count <= 0 or count >= len(items):
        return items
    if count == 1:
        return [items[0]]

    step = (len(items) - 1) / (count - 1)
    return [items[round(index * step)] for index in range(count)]


def main() -> int:
    args = parse_args()
    images_dir = args.root / "Images"
    images = list_images(images_dir)

    if not images:
        raise SystemExit(f"No images found in {images_dir}")
    if args.cols <= 0 or args.tile_width <= 0 or args.tile_height <= 0:
        raise SystemExit("--cols, --tile-width and --tile-height must be positive")

    images = evenly_sample(images, args.max_images)
    rows = args.rows or math.ceil(len(images) / args.cols)
    capacity = args.cols * rows
    images = evenly_sample(images, capacity)

    canvas = Image.new("RGB", (args.cols * args.tile_width, rows * args.tile_height), "white")

    for index, image_path in enumerate(images):
        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            tile = ImageOps.fit(
                image,
                (args.tile_width, args.tile_height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
        x = (index % args.cols) * args.tile_width
        y = (index // args.cols) * args.tile_height
        canvas.paste(tile, (x, y))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, quality=args.quality, optimize=True, progressive=True)

    print(f"Wrote {args.out} ({len(images)} images, {args.cols}x{rows})")
    print(f"Canvas: {canvas.width}x{canvas.height}px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
