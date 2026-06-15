from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


DEFAULT_CONFIG_PATH = Path(os.getenv("AILA_CONFIG", "configs/default.yaml"))


class PathsConfig(BaseModel):
    image_root: str = "data/bdd100k_prepared/bdd100k_images_100k/100k/train"
    artifact_dir: str = "outputs"


class MatchingConfig(BaseModel):
    iou_threshold: float = 0.5
    duplicate_iou_threshold: float = 0.75


class AppConfig(BaseModel):
    database_url: str = "sqlite:///./aila_bench.db"
    pilot_size: int = 300
    random_seed: int = 42
    paths: PathsConfig = Field(default_factory=PathsConfig)
    classes: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    budgets: list[float] = Field(default_factory=lambda: [0.01, 0.05, 0.10, 0.20])
    matching: MatchingConfig = Field(default_factory=MatchingConfig)
    model: dict[str, Any] = Field(default_factory=dict)
    external_models: dict[str, Any] = Field(default_factory=dict)


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    data: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    return AppConfig(**data)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return load_config()
