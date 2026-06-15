from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import AppConfig, load_config
from backend.app.database import Base, create_engine_for_url


def add_config_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config")


def open_session(config: AppConfig, *, reset_db: bool = False) -> Session:
    engine = create_engine_for_url(config.database_url)
    from backend.app import models  # noqa: F401

    if reset_db:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return session_factory()


def load_class_mapping(path: str | Path = "configs/class_mapping.yaml", dataset: str = "bdd100k") -> dict[str, str]:
    mapping_path = Path(path)
    if not mapping_path.exists():
        return {}
    with mapping_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data.get(dataset, {})


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    if input_path.suffix.lower() == ".jsonl":
        return read_jsonl(input_path)
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_config(args: argparse.Namespace) -> AppConfig:
    return load_config(args.config)


def bbox_from_xyxy(box2d: dict[str, Any]) -> tuple[float, float, float, float]:
    x1 = float(box2d["x1"])
    y1 = float(box2d["y1"])
    x2 = float(box2d["x2"])
    y2 = float(box2d["y2"])
    return x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)


def bbox_to_xyxy(x: float, y: float, width: float, height: float) -> dict[str, float]:
    return {"x1": x, "y1": y, "x2": x + width, "y2": y + height}

