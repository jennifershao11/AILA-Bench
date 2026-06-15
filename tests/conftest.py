from __future__ import annotations

from pathlib import Path
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.config import AppConfig
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import AISuggestion, AnnotationTask, Condition, GoldLabel, Image


@pytest.fixture()
def db_session(tmp_path: Path):
    from backend.app import models  # noqa: F401

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}, future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setenv("AILA_CONFIG", "configs/default.yaml")
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_db(db_session):
    image = Image(
        dataset="bdd100k",
        split="pilot",
        external_id="sample.jpg",
        file_name="sample.jpg",
        width=100,
        height=100,
        scene_attributes={},
    )
    db_session.add(image)
    db_session.flush()
    db_session.add(GoldLabel(image_id=image.id, category="car", x=10, y=10, width=30, height=30))
    db_session.add(
        AISuggestion(
            image_id=image.id,
            model_name="yolo11",
            category="car",
            confidence=0.91,
            x=11,
            y=11,
            width=30,
            height=30,
        )
    )
    for condition in Condition:
        db_session.add(AnnotationTask(image_id=image.id, condition=condition))
    db_session.commit()
    return image

