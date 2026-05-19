# Dataset Card: TomatoPlantfactoryDataset

## Summary

TomatoPlantfactoryDataset is an object-detection dataset for tomato fruit images
captured in an artificial-light plant factory. It covers complex supplemental
lighting, color shifts, occlusion, small targets, blur and changing viewpoints.

The official dataset is hosted on Mendeley Data:
<https://data.mendeley.com/datasets/8h3s6jkyff/2>.

## Intended Uses

- Tomato fruit detection in plant factories.
- Green/red tomato maturity detection and counting.
- Benchmarking object detectors under complex lighting.
- YOLO, Pascal VOC and object-detection teaching examples.
- Transfer learning for related agricultural detection scenarios.

## Data Description

| Field | Value |
| --- | --- |
| Number of images | 520 |
| Image format | JPG |
| Resolutions | 6000 x 4000 and 4032 x 3024 |
| Annotation formats | Pascal VOC XML and YOLO TXT |
| Classes | `green`, `red` |
| Published object counts | 5996 green, 3116 red, 9112 total |
| Crop variety | Micro tomato |
| Collection period | December 2021 to February 2022 |
| Collection location | Artificial Light Plant Factory Laboratory, Henan Institute of Science and Technology, Xinxiang, China |

## Collection Method

Images were captured with a Canon 80D DSLR camera and an iPhone 11 wide-angle
camera across growth stages and supplemental-lighting states.

Unrelated or out-of-focus images were removed. Filenames were normalized, and
Exif metadata was removed during preprocessing.

## Annotation

All visible red and green tomato fruits were manually annotated with LabelImg.
Pascal VOC XML files contain bounding-box coordinates and class names. YOLO TXT
files contain normalized class and bounding-box coordinates.

The class names are:

```text
0: green
1: red
```

Use `verify_dataset.py` after extraction to check file alignment and summarize
annotation counts.

Annotation note: Pascal VOC XML contains 9112 objects. YOLO TXT contains 8223
rows; the difference matches 889 green-fruit objects marked as `difficult`.

## Notes

- The dataset is specialized for artificial-light plant factories.
- This mirror does not define an official train/validation/test split.
- Use `prepare_yolo_split.py` for reproducible splits.
- Report annotation format, split, seed, image size and training settings.

## Ethical Considerations

The data article reports no experiments involving humans or animals.

## Citation

Please cite the data article:

Wu, Z.-W., Liu, M.-H., Sun, C.-X. and Wang, X.-F. A dataset of tomato fruits
images for object detection in the complex lighting environment of plant
factories. Data in Brief 48, 109291 (2023).
<https://doi.org/10.1016/j.dib.2023.109291>
