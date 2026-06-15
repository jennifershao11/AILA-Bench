from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def _find_files(root: Path) -> dict[str, list[Path]]:
    jsons = list(root.rglob("*.json"))
    zips = list(root.rglob("*.zip"))
    images = list(root.rglob("*.jpg")) + list(root.rglob("*.png"))
    return {"json": jsons, "zip": zips, "image": images}


def _candidate_label_path(root: Path, paths: list[Path]) -> Path | None:
    preferred_dirs = [
        root / "bdd100k_labels" / "100k" / "train",
        root / "bdd100k_labels" / "100k" / "val",
        root / "labels" / "100k" / "train",
        root / "100k" / "train",
    ]
    for directory in preferred_dirs:
        if directory.exists() and any(directory.glob("*.json")):
            return directory
    for path in paths:
        name = path.name.lower()
        if "det" in name and ("train" in name or "val" in name):
            return path
    for path in paths:
        if "label" in path.name.lower():
            return path
    return paths[0] if paths else None


def prepare_bdd100k(source_dir: Path, output_dir: Path, *, extract: bool = False) -> dict:
    source_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if extract:
        for archive in source_dir.rglob("*.zip"):
            target = output_dir / archive.stem
            if target.exists():
                continue
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(target)

    files = _find_files(output_dir if extract else source_dir)
    scan_root = output_dir if extract else source_dir
    label_json = _candidate_label_path(scan_root, files["json"])
    image_roots = sorted({path.parent for path in files["image"]})
    likely_image_root = None
    preferred_image_roots = [
        scan_root / "bdd100k_images_100k" / "100k" / "train",
        scan_root / "bdd100k_images_100k" / "100k" / "val",
        scan_root / "100k" / "train",
        scan_root / "images" / "100k" / "train",
    ]
    for root in preferred_image_roots:
        if root.exists() and len(list(root.glob("*.jpg"))) + len(list(root.glob("*.png"))) >= 10:
            likely_image_root = root
            break
    for root in image_roots:
        if likely_image_root is not None:
            break
        if len(list(root.glob("*.jpg"))) + len(list(root.glob("*.png"))) >= 10:
            likely_image_root = root
            break
    if likely_image_root is None and image_roots:
        likely_image_root = image_roots[0]

    status = {
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "zip_count": len(files["zip"]),
        "json_count": len(files["json"]),
        "image_count": len(files["image"]),
        "label_path": str(label_json) if label_json else None,
        "image_root": str(likely_image_root) if likely_image_root else None,
        "ready": bool(label_json and likely_image_root),
    }
    if status["ready"]:
        status["import_command"] = (
            "python -m experiments.import_bdd100k "
            f"--config configs/default.yaml --bdd-labels {status['label_path']} "
            f"--image-root {status['image_root']} --limit 300 --reset-db"
        )
    else:
        status["next_step"] = (
            "Place official BDD100K detection label JSON and 100k image files under "
            f"{source_dir}, or pass --extract if you placed official zip files there."
        )
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare authorized BDD100K files for import")
    parser.add_argument("--source-dir", default="data/bdd100k_official")
    parser.add_argument("--output-dir", default="data/bdd100k_prepared")
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--status-json", default="outputs/bdd100k_prepare_status.json")
    args = parser.parse_args()
    status = prepare_bdd100k(Path(args.source_dir), Path(args.output_dir), extract=args.extract)
    output = Path(args.status_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
