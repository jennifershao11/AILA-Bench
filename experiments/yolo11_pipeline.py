from __future__ import annotations

import argparse
from pathlib import Path

from backend.app.models import Image
from experiments.common import add_config_arg, open_session, parse_config, write_jsonl


COCO_TO_TARGET = {
    "person": "pedestrian",
    "bicycle": "rider",
    "car": "car",
    "motorcycle": "motorcycle",
    "bus": "bus",
    "truck": "truck",
    "traffic light": "traffic light",
    "stop sign": "traffic sign",
}


def predict_from_db(
    *,
    config_path: str,
    weights: Path,
    output: Path,
    dataset: str | None,
    split: str | None,
    limit: int | None,
    conf: float,
) -> int:
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise SystemExit("ultralytics is required. Install it with: pip install ultralytics") from exc

    config = parse_config(argparse.Namespace(config=config_path))
    db = open_session(config)
    try:
        query = db.query(Image).order_by(Image.id.asc())
        if dataset:
            query = query.filter(Image.dataset == dataset)
        if split:
            query = query.filter(Image.split == split)
        images = query.limit(limit).all() if limit else query.all()
    finally:
        db.close()

    model = YOLO(str(weights))
    rows = []
    for image in images:
        path = Path(image.file_name)
        if not path.is_absolute() and not path.exists():
            path = Path(config.paths.image_root) / path
        if not path.exists():
            continue
        results = model.predict(str(path), conf=conf, verbose=False)
        result = results[0]
        names = result.names
        for box in result.boxes:
            class_name = names[int(box.cls.item())]
            category = COCO_TO_TARGET.get(class_name)
            if not category:
                continue
            x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
            rows.append(
                {
                    "image_id": image.id,
                    "image_external_id": image.external_id,
                    "file_name": image.file_name,
                    "model_name": "yolo11",
                    "category": category,
                    "confidence": float(box.conf.item()),
                    "bbox": [x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)],
                    "raw": {"coco_class": class_name},
                }
            )
    write_jsonl(output, rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YOLO11 inference for imported images")
    add_config_arg(parser)
    parser.add_argument("--mode", choices=["predict"], default="predict")
    parser.add_argument("--weights", default="models/yolo11n.pt")
    parser.add_argument("--output", default="outputs/yolo11_predictions.jsonl")
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--split", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    count = predict_from_db(
        config_path=args.config,
        weights=Path(args.weights),
        output=Path(args.output),
        dataset=args.dataset,
        split=args.split,
        limit=args.limit,
        conf=args.conf,
    )
    print(f"Wrote {count} YOLO11 predictions to {args.output}")


if __name__ == "__main__":
    main()
