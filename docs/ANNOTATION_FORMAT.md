# Annotation format

Each sample has an RGB PNG image, a grayscale PNG mask, and one JSON file. All have a 512 x 512 pixel grid. The PNG mask uses 0 for background and 255 for crack pixels; the JSON RLE represents the same values as 0 and 1.

## JSON fields

- `version`: the Labelme-style format version, 5.5.0.
- `imageWidth`, `imageHeight`: image width and height in pixels.
- `imageData`: null; images are provided as separate PNG files.
- `imagePath`: the image path relative to the annotation file, `../images/<id>.png`.
- `sourceMask`: the source PNG mask path relative to the annotation file, `../masks/<id>mask.png`.
- `shapes`: polygons labelled `crack`; coordinates are `[x, y]` in pixel coordinates.
- `mask_rle`: a custom exact-mask field with `format`, `label`, `size`, and `counts`. It is an uncompressed COCO-style RLE, not a complete COCO dataset JSON.

`mask_rle.size` is `[height, width]`. The nonnegative run lengths alternate between background and foreground, starting with a background run (which can be zero). Runs traverse the flattened mask in column-major / Fortran order.

```python
import json
from pathlib import Path
import numpy as np

path = sorted(Path("data/phase1/annotations").glob("*.json"))[0]
annotation = json.loads(path.read_text(encoding="utf-8"))
rle = annotation["mask_rle"]
counts = np.asarray(rle["counts"], dtype=np.int64)
assert counts.sum() == np.prod(rle["size"])
mask = np.repeat(np.arange(len(counts)) % 2, counts)
mask = mask.reshape(tuple(rle["size"]), order="F").astype(np.uint8)
# mask[y, x]: 0 = background, 1 = crack
```

## Exact masks and editable polygons

The JSON annotations were derived from the source PNG masks. They are alternative encodings, not independently drawn annotations. All 158 RLE masks match their PNG references exactly. Labelme-style polygons support visualization and editing, but polygon rasterization can fill internal holes or alter boundaries. Use the PNG masks or decoded `mask_rle` for pixel-level evaluation and geometric measurement.

In this snapshot, polygon rasterization matches 107 masks exactly; 51 differ. The sample-level audit in `metadata/annotation_fidelity.csv` uses Pillow polygon filling. Its mean IoU is approximately 0.997861, and the minimum is approximately 0.900292. Polygon counts must not be interpreted as counts of independent physical cracks.

## Portable-path preparation

The PNG images and masks were copied without changing their bytes. Only the JSON `imagePath` and `sourceMask` values were normalized to the package layout. Polygon coordinates, RLE counts, and the other annotation values were preserved. JSON whitespace was normalized to UTF-8 indented text.
