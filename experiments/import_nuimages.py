from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from backend.app.models import GoldLabel, Image
from experiments.common import add_config_arg, load_class_mapping, open_session, parse_config


def _load_table(root: Path, version: str, name: str) -> list[dict]:
    path = root / version / f"{name}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def import_nuimages(
    db,
    *,
    nuimages_root: Path,
    version: str,
    classes: list[str],
    limit: int | None,
    split: str,
) -> int:
    categories = {row["token"]: row["name"] for row in _load_table(nuimages_root, version, "category")}
    sample_data = {row["token"]: row for row in _load_table(nuimages_root, version, "sample_data")}
    annotations = _load_table(nuimages_root, version, "object_ann")
    mapping = load_class_mapping(dataset="nuimages")
    allowed = set(classes)

    grouped: dict[str, list[tuple[str, float, float, float, float, dict]]] = {}
    for ann in annotations:
        category = mapping.get(categories.get(ann["category_token"], ""))
        if category not in allowed:
            continue
        x1, y1, x2, y2 = [float(value) for value in ann["bbox"]]
        width = max(0.0, x2 - x1)
        height = max(0.0, y2 - y1)
        if width <= 0 or height <= 0:
            continue
        grouped.setdefault(ann["sample_data_token"], []).append(
            (
                category,
                x1,
                y1,
                width,
                height,
                {"nuimages_token": ann["token"], "attribute_tokens": ann.get("attribute_tokens", [])},
            )
        )

    imported = 0
    for sample_data_token, labels in grouped.items():
        if limit is not None and imported >= limit:
            break
        sample = sample_data.get(sample_data_token)
        if not sample:
            continue
        file_name = sample["filename"]
        image = Image(
            dataset="nuimages",
            split=split,
            external_id=sample_data_token,
            file_name=str(nuimages_root / file_name),
            width=sample.get("width"),
            height=sample.get("height"),
            scene_attributes={
                "is_key_frame": sample.get("is_key_frame"),
                "timestamp": sample.get("timestamp"),
                "channel": Path(file_name).parts[1] if len(Path(file_name).parts) > 1 else "",
            },
        )
        db.add(image)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            continue
        for category, x, y, width, height, attributes in labels:
            db.add(
                GoldLabel(
                    image_id=image.id,
                    category=category,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    attributes=attributes,
                    source="nuimages_official",
                )
            )
        imported += 1
    db.commit()
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description="Import nuImages 2D object annotations as gold labels")
    add_config_arg(parser)
    parser.add_argument("--nuimages-root", default="data/nuimages")
    parser.add_argument("--version", default="v1.0-mini")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--split", default="nuimages-mini")
    parser.add_argument("--reset-db", action="store_true")
    args = parser.parse_args()
    config = parse_config(args)
    db = open_session(config, reset_db=args.reset_db)
    try:
        imported = import_nuimages(
            db,
            nuimages_root=Path(args.nuimages_root),
            version=args.version,
            classes=config.classes,
            limit=args.limit,
            split=args.split,
        )
    finally:
        db.close()
    print(f"Imported {imported} nuImages images from {args.nuimages_root}/{args.version}")


if __name__ == "__main__":
    main()
