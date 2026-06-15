from __future__ import annotations

import argparse
from typing import Any

from backend.app.models import AISuggestion, Image
from backend.app.services import annotate_ai_errors
from experiments.common import add_config_arg, bbox_from_xyxy, open_session, parse_config, read_jsonl


def _bbox(row: dict[str, Any]) -> tuple[float, float, float, float]:
    if "box2d" in row:
        return bbox_from_xyxy(row["box2d"])
    if "bbox" in row:
        x, y, width, height = row["bbox"]
        return float(x), float(y), float(width), float(height)
    return float(row["x"]), float(row["y"]), float(row["width"]), float(row["height"])


def import_suggestions(db, rows: list[dict[str, Any]], *, model_name: str = "yolo11") -> int:
    count = 0
    for row in rows:
        external_id = row.get("image_external_id") or row.get("image") or row.get("file_name")
        image_id = row.get("image_id")
        image = db.get(Image, int(image_id)) if image_id else None
        if image is None and external_id:
            image = db.query(Image).filter(Image.external_id == external_id).first()
        if image is None:
            continue
        x, y, width, height = _bbox(row)
        suggestion = AISuggestion(
            image_id=image.id,
            model_name=row.get("model_name") or model_name,
            category=row["category"],
            confidence=row.get("confidence"),
            x=x,
            y=y,
            width=width,
            height=height,
            disagreement=row.get("disagreement") or {},
            raw=row,
        )
        db.add(suggestion)
        count += 1
    db.commit()
    for image_id, in db.query(Image.id).all():
        annotate_ai_errors(db, image_id)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Import AI suggestions from JSONL")
    add_config_arg(parser)
    parser.add_argument("--input", required=True, help="JSONL with image id/name, category, bbox, confidence")
    parser.add_argument("--model-name", default="yolo11")
    args = parser.parse_args()
    config = parse_config(args)
    rows = read_jsonl(args.input)
    db = open_session(config)
    try:
        count = import_suggestions(db, rows, model_name=args.model_name)
    finally:
        db.close()
    print(f"Imported {count} suggestions")


if __name__ == "__main__":
    main()

