# QuantifiableCracks — Phase 1

**Version:** v0.1.0  
**Release series:** Phase 1 is the first batch of an expanding dataset.

QuantifiableCracks provides surface-crack images and pixel-level annotations for structural-inspection research. **This is Phase 1, the initial data batch. The dataset will continue to be expanded in subsequent releases.** The file manifest defines the contents of this version.

## Contents

Phase 1 contains **158 samples**, with one image, one binary mask, and one JSON annotation per sample:

- 158 PNG crack images, each 512 × 512 pixels;
- 158 binary PNG masks, each paired with an image;
- 158 JSON annotation files derived from those masks.

The image files are **processed regions of interest (ROIs)**, not the original full-frame photographs. Images are stored once and paired with their masks and JSON annotations through stable sample identifiers.

## Directory layout

```text
data/
  phase1/
    images/<id>.png
    masks/<id>mask.png
    annotations/<id>mask.json
metadata/
tools/
  validate_dataset.py
```

Here, `<id>` is the sample identifier taken from the image filename. The same identifier links the three files. Filename prefixes are not verified specimen identifiers; no specimen grouping should be inferred from them. Release metadata and file manifests are maintained under `metadata/`.

## Annotation format

Each JSON file uses a Labelme-style polygon structure and additionally stores an exact COCO-style **uncompressed run-length encoding (RLE)** of its source mask. The polygons are converted representations of the PNG mask. Use the PNG mask or the included RLE when exact pixel-level agreement is needed.

`imageData` is `null`, so images are supplied as separate files. `imagePath` and `sourceMask` are relative to the JSON file's directory:

- `../images/<id>.png`
- `../masks/<id>mask.png`

These portable path references do not change the underlying image or mask content. The JSON files are mask-derived annotations, not a separately acquired source of crack geometry.

## Read a sample

The following example uses Python, Pillow, and NumPy. Run it from the package root.

```python
from pathlib import Path
import json

import numpy as np
from PIL import Image

base = Path("data/phase1")
image_path = sorted((base / "images").glob("*.png"))[0]
sample_id = image_path.stem
mask_path = base / "masks" / f"{sample_id}mask.png"
annotation_path = base / "annotations" / f"{sample_id}mask.json"

with Image.open(image_path) as image:
    image_array = np.asarray(image.convert("RGB"))
with Image.open(mask_path) as mask:
    foreground = np.asarray(mask.convert("L")) > 0
with annotation_path.open(encoding="utf-8") as stream:
    annotation = json.load(stream)

assert image_array.shape[:2] == foreground.shape == (512, 512)
print(sample_id, image_array.shape, foreground.sum())
```

Install the loading and validation dependencies, then check every file:

```bash
python -m pip install -r requirements.txt
python tools/validate_dataset.py
```

Validation checks file pairing, dimensions, mask values, JSON paths, exact RLE agreement, and SHA-256 checksums. See `metadata/manifest.csv`, `metadata/annotation_fidelity.csv`, and `metadata/release_metadata.json` for sample-level and release-level records.

## Scope and limitations

This batch does **not** include full-frame acquisition photographs, camera intrinsics, ArUco corner coordinates, per-image calibration metadata, official training/validation/test assignments, or geometric measurement results. The image dimensions alone do not establish a physical pixel scale.

Users should document any partitions or additional processing they create. Specimen-level evaluation requires independently verified grouping information. The supplied ROI files support pixel-level analysis; reproducing physical measurements additionally requires the corresponding scale and calibration information.

## Versions and future additions

Sample identifiers will remain stable. New samples will receive distinct identifiers; corrections to an existing sample will be recorded against its identifier in a new version. Published release snapshots should remain unchanged.

Subsequent releases will distinguish additions, annotation corrections, and metadata changes in `CHANGELOG.md`. Record the exact release tag and sample identifiers used in an experiment. Phase 1 identifies a batch, while v0.1.0 identifies this snapshot. No DOI has been assigned to this snapshot. Cite the version tag or exact commit used; see `CITATION.md`.

## License and related tool

License: **MIT**; see `LICENSE`.

Related annotation tool: [Semi-auto-Annotating-tool](https://github.com/levyw3847-arch/Semi-auto-Annotating-tool).

Dataset repository: [QuantifiableCracks](https://github.com/levyw3847-arch/QuantifiableCracks).

See [annotation-format details](docs/ANNOTATION_FORMAT.md) for exact RLE decoding and polygon limitations.
