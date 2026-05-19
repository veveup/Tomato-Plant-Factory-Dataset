# Quick Start: YOLO Training

This guide prepares the Mendeley Data archive for Ultralytics YOLO.

## 1. Download The Dataset

Download the official archive from:

<https://data.mendeley.com/datasets/8h3s6jkyff/2>

Place `TomatoPlantfactoryDataset.zip` in the repository root and extract it into
the ignored local data folder:

```bash
mkdir -p TomatoPlantfactoryDataset
unzip TomatoPlantfactoryDataset.zip -d TomatoPlantfactoryDataset
```

You should see:

```text
TomatoPlantfactoryDataset/
  Images/
  Annotations/
  labels/
```

## 2. Verify The Local Files

```bash
python verify_dataset.py --root TomatoPlantfactoryDataset
```

The script checks file alignment and prints annotation counts.

The Pascal VOC XML files contain 9112 objects. The YOLO TXT files contain 8223
rows; the difference matches the 889 XML objects marked as `difficult`.

## 3. Create A Reproducible Split

```bash
python prepare_yolo_split.py --root TomatoPlantfactoryDataset --out yolo_dataset --train 0.8 --val 0.1 --seed 42
```

This creates:

```text
yolo_dataset/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  data.yaml
  split_manifest.csv
```

By default, files are symlinked so the 3 GB archive is not duplicated.
Use `--copy` if you need a standalone dataset folder.

## 4. Train With Ultralytics

Install Ultralytics:

```bash
pip install ultralytics
```

Run a small baseline:

```bash
yolo detect train model=yolov8n.pt data=yolo_dataset/data.yaml imgsz=640 epochs=100
```

For small-fruit detection, try a larger image size if GPU memory allows it:

```bash
yolo detect train model=yolov8s.pt data=yolo_dataset/data.yaml imgsz=1280 epochs=100
```

## 5. Evaluate And Report

```bash
yolo detect val model=runs/detect/train/weights/best.pt data=yolo_dataset/data.yaml imgsz=640
```

When reporting results, include:

- Model name and version.
- Input image size.
- Train/validation/test ratio and random seed.
- Number of epochs and batch size.
- Hardware.
- Metrics: mAP50, mAP50-95, precision and recall.

Record comparable results in [BENCHMARKS.md](BENCHMARKS.md).
