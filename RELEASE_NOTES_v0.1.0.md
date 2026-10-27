# QuantifiableCracks v0.1.0 — Phase 1 Release Notes

**Release designation:** Phase 1, the initial data batch of QuantifiableCracks.

## Included in this batch

| Item | Count | Description |
|---|---:|---|
| Images | 158 | Processed PNG ROIs, each 512 × 512 pixels |
| Masks | 158 | Paired binary PNG masks |
| JSON annotations | 158 | Mask-derived Labelme-style polygons and exact COCO-style uncompressed RLE |

Samples use the paths `data/phase1/images/<id>.png`, `data/phase1/masks/<id>mask.png`, and `data/phase1/annotations/<id>mask.json`. Matching copies in the second source image directory are not duplicated.

JSON files contain no embedded image payload (`imageData: null`). Their image and mask references are portable relative paths. The PNG image and mask pixels are preserved.

## Scope

This release does not include original full-frame photographs, camera intrinsics, ArUco corner coordinates, per-image calibration metadata, official training/validation/test splits, or geometric measurement results. Sample identifiers and filename prefixes are not verified specimen identifiers.

The 158 samples describe the scope of this batch only. They should not be equated with the full image collection or all experimental materials described in the paper. The package alone does not establish full reproduction of the paper's calibrated geometric measurements.

## Using and checking the package

See `README.md` or `README_zh-CN.md` for the directory layout and a Python loading example. The validation tool is `tools/validate_dataset.py`; file manifests and release metadata are maintained under `metadata/`.

License: MIT; see `LICENSE`.

Related annotation tool: [Semi-auto-Annotating-tool](https://github.com/levyw3847-arch/Semi-auto-Annotating-tool).

## Future updates

Additional batches are planned. Sample identifiers will remain stable, and corrections or additions will be documented in a new version and in `CHANGELOG.md`. Users should record the exact release tag and samples used.

