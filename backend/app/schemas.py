from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models import Condition, TaskStatus


class BoxBase(BaseModel):
    category: str
    x: float
    y: float
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset: str
    split: str
    external_id: str
    file_name: str
    width: int | None = None
    height: int | None = None
    scene_attributes: dict[str, Any] = Field(default_factory=dict)


class GoldLabelOut(BoxBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    attributes: dict[str, Any] = Field(default_factory=dict)


class AISuggestionOut(BoxBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    model_name: str
    confidence: float | None = None
    ai_error_type: str | None = None
    disagreement: dict[str, Any] = Field(default_factory=dict)


class FinalLabelIn(BoxBase):
    temp_id: str | None = None
    confidence: float | None = None
    source_suggestion_id: int | None = None


class FinalLabelOut(BoxBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    confidence: float | None = None
    source_suggestion_id: int | None = None
    matched_gold_id: int | None = None
    error_type: str | None = None


class AnnotationEventIn(BaseModel):
    client_event_id: str | None = None
    timestamp_ms: int
    action_type: str
    label_temp_id: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AnnotationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    client_event_id: str | None = None
    timestamp_ms: int
    action_type: str
    label_temp_id: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    condition: Condition
    status: TaskStatus
    annotator_id: str | None = None
    review_time_ms: int | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class TaskBundleOut(BaseModel):
    task: TaskOut
    image: ImageOut
    suggestions: list[AISuggestionOut] = Field(default_factory=list)
    classes: list[str]
    display_condition: str = "standard"
    show_confidence: bool = False


class PublicTaskOut(BaseModel):
    id: int
    image_id: int
    status: TaskStatus
    annotator_id: str | None = None
    review_time_ms: int | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class PublicTaskBundleOut(BaseModel):
    task: PublicTaskOut
    image: ImageOut
    suggestions: list[AISuggestionOut] = Field(default_factory=list)
    classes: list[str]
    display_condition: str = "standard"
    show_confidence: bool = False


class ClaimTaskRequest(BaseModel):
    annotator_id: str
    condition: Condition | None = None


class TaskDraftRequest(BaseModel):
    annotator_id: str
    draft: dict[str, Any] = Field(default_factory=dict)


class SubmitTaskRequest(BaseModel):
    annotator_id: str
    review_time_ms: int = Field(ge=0)
    started_at_client_ms: int | None = None
    labels: list[FinalLabelIn]
    events: list[AnnotationEventIn] = Field(default_factory=list)


class SubmitTaskResponse(BaseModel):
    task: TaskOut
    final_labels: list[FinalLabelOut]
    errors: dict[str, int]


class EventLogRequest(BaseModel):
    annotator_id: str
    events: list[AnnotationEventIn]


class ExportOut(BaseModel):
    rows: list[dict[str, Any]]


class StatsOut(BaseModel):
    images: int
    tasks_total: int
    tasks_pending: int
    tasks_in_progress: int
    tasks_submitted: int
    final_labels: int
    annotation_events: int
    ai_suggestions: int
    conditions: dict[str, int]


class ArtifactOut(BaseModel):
    name: str
    path: str
    exists: bool
    size_bytes: int | None = None


class ReportOut(BaseModel):
    summary: dict[str, Any] | None = None
    artifacts: list[ArtifactOut]
