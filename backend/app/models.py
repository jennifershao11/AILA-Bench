from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.app.database import Base


class Condition(str, Enum):
    human_only = "human_only"
    ai_assisted = "ai_assisted"
    ai_assisted_confidence = "ai_assisted_confidence"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    submitted = "submitted"
    skipped = "skipped"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    dataset = Column(String(64), nullable=False, index=True)
    split = Column(String(64), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, index=True)
    file_name = Column(String(512), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    scene_attributes = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    gold_labels = relationship("GoldLabel", back_populates="image", cascade="all, delete-orphan")
    ai_suggestions = relationship("AISuggestion", back_populates="image", cascade="all, delete-orphan")
    tasks = relationship("AnnotationTask", back_populates="image", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("dataset", "split", "external_id", name="uq_image_external"),)


class GoldLabel(Base):
    __tablename__ = "gold_labels"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    category = Column(String(128), nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    attributes = Column(JSON, nullable=False, default=dict)
    source = Column(String(128), default="bdd100k_official", nullable=False)

    image = relationship("Image", back_populates="gold_labels")


class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    model_name = Column(String(128), nullable=False, default="yolo11")
    category = Column(String(128), nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    ai_error_type = Column(String(64), nullable=True)
    disagreement = Column(JSON, nullable=False, default=dict)
    raw = Column(JSON, nullable=False, default=dict)

    image = relationship("Image", back_populates="ai_suggestions")


class AnnotationTask(Base):
    __tablename__ = "annotation_tasks"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    condition = Column(SAEnum(Condition), nullable=False, index=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.pending, index=True)
    annotator_id = Column(String(128), nullable=True, index=True)
    assigned_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    review_time_ms = Column(Integer, nullable=True)
    started_at_client_ms = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=False, default=dict)

    image = relationship("Image", back_populates="tasks")
    final_labels = relationship("FinalLabel", back_populates="task", cascade="all, delete-orphan")
    events = relationship("AnnotationEvent", back_populates="task", cascade="all, delete-orphan")
    features = relationship("SCLNFeature", back_populates="task", cascade="all, delete-orphan")
    review_scores = relationship("ReviewScore", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("image_id", "condition", name="uq_task_image_condition"),)


class FinalLabel(Base):
    __tablename__ = "final_labels"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("annotation_tasks.id"), nullable=False, index=True)
    category = Column(String(128), nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    source_suggestion_id = Column(Integer, ForeignKey("ai_suggestions.id"), nullable=True)
    matched_gold_id = Column(Integer, ForeignKey("gold_labels.id"), nullable=True)
    error_type = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("AnnotationTask", back_populates="final_labels")


class AnnotationEvent(Base):
    __tablename__ = "annotation_events"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("annotation_tasks.id"), nullable=False, index=True)
    client_event_id = Column(String(128), nullable=True)
    timestamp_ms = Column(Integer, nullable=False)
    action_type = Column(String(64), nullable=False, index=True)
    label_temp_id = Column(String(128), nullable=True)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)
    details = Column(JSON, nullable=False, default=dict)

    task = relationship("AnnotationTask", back_populates="events")


class SCLNFeature(Base):
    __tablename__ = "scln_features"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("annotation_tasks.id"), nullable=False, index=True)
    label_id = Column(Integer, ForeignKey("final_labels.id"), nullable=True)
    feature_json = Column(JSON, nullable=False)
    target_error = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("AnnotationTask", back_populates="features")


class ReviewScore(Base):
    __tablename__ = "review_scores"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("annotation_tasks.id"), nullable=False, index=True)
    score_name = Column(String(128), nullable=False, index=True)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)
    selected_for_budget = Column(JSON, nullable=False, default=dict)
    reviewer_id = Column(String(128), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_outcome = Column(String(64), nullable=True)

    task = relationship("AnnotationTask", back_populates="review_scores")

