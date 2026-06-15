from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image as PILImage
from sqlalchemy.orm import Session

from backend.app.models import GoldLabel, Image
from experiments.common import add_config_arg, bbox_from_xyxy, load_class_mapping, open_session, parse_config


def _image_size(path: Path) -> tuple[int | None, int | None]:
    if not path.exists():
        return None, None
    try:
        with PILImage.open(path) as image:
            return image.size
    except Exception:
        return None, None


def _records_from_path(label_path: Path) -> list[dict[str, Any]]:
    if label_path.is_dir():
        records = []
        for path in sorted(label_path.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                records.append(json.load(handle))
        return records
    with label_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else [data]


def _labels_from_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    if "labels" in record:
        return record.get("labels", [])
    frames = record.get("frames") or []
    if frames:
        return frames[0].get("objects", [])
    return []


def _record_file_name(record: dict[str, Any]) -> str | None:
    name = record.get("name")
    if not name:
        return None
    return name if Path(name).suffix else f"{name}.jpg"


def import_bdd100k(
    db: Session,
    *,
    label_path: Path,
    image_root: Path,
    classes: list[str],
    limit: int | None,
    split: str,
    dataset: str = "bdd100k",
) -> int:
    mapping = load_class_mapping(dataset="bdd100k")
    records = _records_from_path(label_path)
    imported = 0
    allowed = set(classes)

    for record in records:
        if limit is not None and imported >= limit:
            break
        file_name = _record_file_name(record)
        if not file_name:
            continue
        labels = []
        for source_label in _labels_from_record(record):
            category = mapping.get(source_label.get("category"), source_label.get("category"))
            box2d = source_label.get("box2d")
            if category not in allowed or not box2d:
                continue
            x, y, width, height = bbox_from_xyxy(box2d)
            if width <= 0 or height <= 0:
                continue
            labels.append((category, x, y, width, height, source_label.get("attributes") or {}))
        if not labels:
            continue
        width, height = _image_size(image_root / file_name)
        image_path = image_root / file_name
        image = Image(
            dataset=dataset,
            split=split,
            external_id=Path(file_name).stem,
            file_name=str(image_path),
            width=width,
            height=height,
            scene_attributes=record.get("attributes") or {},
        )
        db.add(image)
        db.flush()
        for category, x, y, box_width, box_height, attributes in labels:
            db.add(
                GoldLabel(
                    image_id=image.id,
                    category=category,
                    x=x,
                    y=y,
                    width=box_width,
                    height=box_height,
                    attributes=attributes,
                )
            )
        imported += 1
    db.commit()
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description="Import BDD100K detection labels as gold labels")
    add_config_arg(parser)
    parser.add_argument("--bdd-labels", help="BDD100K detection JSON or directory of per-image JSON labels")
    parser.add_argument("--image-root", help="BDD100K image directory")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--split", default="pilot")
    parser.add_argument("--reset-db", action="store_true")
    args = parser.parse_args()
    config = parse_config(args)
    if not args.bdd_labels or not args.image_root:
        raise SystemExit("Provide --bdd-labels and --image-root")
    label_path = Path(args.bdd_labels)
    image_root = Path(args.image_root)
    if not label_path.exists():
        raise SystemExit(f"Label file not found: {label_path}")
    db = open_session(config, reset_db=args.reset_db)
    try:
        imported = import_bdd100k(
            db,
            label_path=label_path,
            image_root=image_root,
            classes=config.classes,
            limit=args.limit if args.limit is not None else config.pilot_size,
            split=args.split,
        )
    finally:
        db.close()
    print(f"Imported {imported} images from {label_path}")


if __name__ == "__main__":
    main()
