"""Validate a QuantifiableCracks release using its manifest and SHA-256 checksums."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_inside(root: Path, value: str, relative_to: Path | None = None) -> Path:
    path = ((relative_to or root) / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes the release: {value}")
    if not path.is_file():
        raise ValueError(f"Missing file: {value}")
    return path


def decode_rle(rle: dict) -> np.ndarray:
    """Decode alternating background/foreground runs in COCO column-major order."""
    height, width = rle["size"]
    counts = rle["counts"]
    if not isinstance(counts, list) or any(type(n) is not int or n < 0 for n in counts):
        raise ValueError("RLE counts must be nonnegative integers")
    if sum(counts) != height * width:
        raise ValueError("RLE length does not match the declared image size")
    values = np.arange(len(counts), dtype=np.uint8) % 2
    return np.repeat(values, counts).reshape((height, width), order="F")


def validate(root: Path) -> dict:
    root = root.resolve()
    with (root / "metadata/manifest.csv").open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    metadata = json.loads((root / "metadata/release_metadata.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    sample_ids: set[str] = set()
    paths_in_manifest: set[str] = set()
    for row in records:
        sample_id = row["sample_id"]
        try:
            if sample_id in sample_ids:
                raise ValueError("Duplicate sample_id")
            sample_ids.add(sample_id)
            image_path = resolve_inside(root, row["image_path"])
            mask_path = resolve_inside(root, row["mask_path"])
            json_path = resolve_inside(root, row["annotation_path"])
            with Image.open(image_path) as image:
                image.load()
                image_size = image.size
            with Image.open(mask_path) as mask_image:
                mask_image.load()
                if mask_image.mode != "L":
                    raise ValueError(f"Expected grayscale L mask, got {mask_image.mode}")
                mask = np.asarray(mask_image)
            width, height = int(row["width"]), int(row["height"])
            if image_size != (width, height) or mask.shape != (height, width):
                raise ValueError("Image, mask, and manifest dimensions disagree")
            if not set(np.unique(mask).tolist()).issubset({0, 255}):
                raise ValueError("Mask must contain only background=0 and crack=255")
            foreground = int(np.count_nonzero(mask))
            if foreground != int(row["foreground_pixels"]) or foreground == 0:
                raise ValueError("Foreground pixel count is inconsistent or zero")
            annotation = json.loads(json_path.read_text(encoding="utf-8"))
            if (annotation["imageWidth"], annotation["imageHeight"]) != (width, height):
                raise ValueError("JSON dimensions do not match the image")
            if resolve_inside(root, annotation["imagePath"], json_path.parent) != image_path:
                raise ValueError("JSON imagePath points to another image")
            if resolve_inside(root, annotation["sourceMask"], json_path.parent) != mask_path:
                raise ValueError("JSON sourceMask points to another mask")
            if annotation.get("imageData") is not None:
                raise ValueError("Unexpected embedded imageData")
            if annotation["mask_rle"].get("format") != "coco_uncompressed":
                raise ValueError("Unexpected RLE format")
            if not np.array_equal(decode_rle(annotation["mask_rle"]), mask > 0):
                raise ValueError("RLE differs from the PNG reference mask")
            for shape in annotation["shapes"]:
                points = np.asarray(shape["points"], dtype=float)
                if shape["label"] != "crack" or shape["shape_type"] != "polygon":
                    raise ValueError("Unexpected polygon label or shape type")
                if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
                    raise ValueError("Invalid polygon point array")
                if not np.isfinite(points).all():
                    raise ValueError("Nonfinite polygon coordinates")
                if not ((points >= 0).all() and (points[:, 0] < width).all() and (points[:, 1] < height).all()):
                    raise ValueError("Polygon coordinates outside the image")
            for kind, path in (("image", image_path), ("mask", mask_path), ("annotation", json_path)):
                relative_path = path.relative_to(root).as_posix()
                paths_in_manifest.add(relative_path)
                if sha256(path) != row[f"{kind}_sha256"]:
                    raise ValueError(f"SHA-256 mismatch for {relative_path}")
        except Exception as exc:
            errors.append(f"{sample_id}: {exc}")

    actual_data_files = {p.relative_to(root).as_posix() for p in (root / "data").rglob("*") if p.is_file()}
    if actual_data_files != paths_in_manifest:
        errors.append("The data directory and manifest do not describe the same files")
    if len(records) != metadata["counts"]["samples"]:
        errors.append("Manifest count differs from release metadata")

    checksums_path = root / "checksums.sha256"
    checksum_paths: set[str] = set()
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        try:
            expected, relative_path = line.split("  ", 1)
            path = resolve_inside(root, relative_path)
            if relative_path in checksum_paths:
                raise ValueError("Duplicate checksum entry")
            checksum_paths.add(relative_path)
            if sha256(path) != expected:
                raise ValueError("Checksum mismatch")
        except Exception as exc:
            errors.append(f"Checksum {line[:100]}: {exc}")
    release_files = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and ".git" not in p.relative_to(root).parts
        and "__pycache__" not in p.relative_to(root).parts
        and p != checksums_path
    }
    if release_files != checksum_paths:
        errors.append("Checksum file does not cover exactly the release files (excluding itself)")

    return {
        "dataset": metadata["dataset_name"],
        "version": metadata["version"],
        "samples_checked": len(records),
        "data_files_checked": len(actual_data_files),
        "files_with_checksums": len(checksum_paths),
        "errors": errors,
        "passed": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = validate(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
