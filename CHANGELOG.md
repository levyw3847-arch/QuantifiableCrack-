# Changelog

This log records the contents and changes of each dataset snapshot. Phase 1 is the first batch, and the dataset will continue to expand in subsequent versions.

## v0.1.0 — Phase 1

### Added

- An initial batch of 158 processed ROI samples.
- 158 PNG images at 512 × 512 pixels, 158 paired binary PNG masks, and 158 mask-derived JSON annotations.
- A consistent relative layout under `data/phase1/images/`, `masks/`, and `annotations/`.
- English and Simplified Chinese dataset descriptions.
- A package validation tool at `tools/validate_dataset.py`, together with release metadata and file manifests.

### Annotation portability

- JSON `imageData` is `null`; image files are stored separately.
- JSON `imagePath` and `sourceMask` refer to sibling image and mask directories using relative paths.
- JSON annotations retain the Labelme-style polygons and exact COCO-style uncompressed RLE derived from the source masks.
- Path updates do not change image or mask pixels.

### Scope

- Full-frame acquisition photographs, camera intrinsics, ArUco corner coordinates, per-image calibration metadata, official dataset splits, and geometric measurement results are not included.
- Duplicate image copies from the second source directory are not repeated in the package.
- This initial batch is not presented as a complete archive of all materials described in the paper.

### Version maintenance

- Keep sample identifiers stable across versions; assign distinct identifiers to new samples.
- Describe additions, corrections, and withdrawals explicitly in subsequent change-log entries.
- Publish corrections as a new version instead of replacing a published snapshot.
- Cite the exact version and record the sample identifiers used for analysis.

Preparation date: 2026-10-27. The actual publication date and any persistent identifier should be recorded when the release is published.
