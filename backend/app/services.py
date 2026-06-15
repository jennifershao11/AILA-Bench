from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy import and_, exists, select
from sqlalchemy.orm import Session, aliased

from backend.app.config import get_config
from backend.app.metrics import Box, confidence_bucket, match_predictions, summarize_errors
from backend.app.models import (
    AISuggestion,
    AnnotationEvent,
    AnnotationTask,
    Condition,
    FinalLabel,
    GoldLabel,
    Image,
    SCLNFeature,
    TaskStatus,
)
from backend.app.schemas import AnnotationEventIn, FinalLabelIn


def box_from_orm(row: GoldLabel | AISuggestion | FinalLabel) -> Box:
    return Box(
        id=row.id,
        category=row.category,
        x=row.x,
        y=row.y,
        width=row.width,
        height=row.height,
        confidence=getattr(row, "confidence", None),
    )


def allowed_suggestions_for_condition(task: AnnotationTask) -> bool:
    return task.condition in {Condition.ai_assisted, Condition.ai_assisted_confidence}


def claim_task(
    db: Session,
    *,
    annotator_id: str,
    condition: Condition | None = None,
) -> AnnotationTask | None:
    active_task = (
        db.query(AnnotationTask)
        .filter(
            AnnotationTask.annotator_id == annotator_id,
            AnnotationTask.status == TaskStatus.in_progress,
        )
        .order_by(AnnotationTask.assigned_at.desc().nullslast(), AnnotationTask.id.desc())
        .first()
    )
    if active_task is not None:
        db.refresh(active_task)
        return active_task

    candidate = aliased(AnnotationTask)
    claimed = aliased(AnnotationTask)
    conflict = exists().where(
        and_(
            claimed.image_id == candidate.image_id,
            claimed.annotator_id == annotator_id,
            claimed.status.in_([TaskStatus.in_progress, TaskStatus.submitted]),
        )
    )
    query = (
        select(candidate)
        .where(candidate.status == TaskStatus.pending)
        .where(~conflict)
        .order_by(candidate.id.asc())
        .limit(1)
    )
    if condition:
        query = query.where(candidate.condition == condition)
    task = db.execute(query).scalars().first()
    if task is None:
        return None
    task.status = TaskStatus.in_progress
    task.annotator_id = annotator_id
    task.assigned_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_for_annotator(db: Session, task_id: int, annotator_id: str | None = None) -> AnnotationTask:
    task = db.get(AnnotationTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if annotator_id is not None and task.annotator_id != annotator_id:
        raise HTTPException(status_code=403, detail="Task is assigned to another annotator")
    return task


def submit_task(
    db: Session,
    *,
    task: AnnotationTask,
    labels: list[FinalLabelIn],
    events: list[AnnotationEventIn],
    review_time_ms: int,
    started_at_client_ms: int | None,
) -> tuple[list[FinalLabel], dict[str, int]]:
    db.query(FinalLabel).filter(FinalLabel.task_id == task.id).delete()

    final_rows: list[FinalLabel] = []
    for label in labels:
        final_rows.append(
            FinalLabel(
                task_id=task.id,
                category=label.category,
                x=label.x,
                y=label.y,
                width=label.width,
                height=label.height,
                confidence=label.confidence,
                source_suggestion_id=label.source_suggestion_id,
            )
        )
    db.add_all(final_rows)
    db.flush()

    for event in events:
        db.add(
            AnnotationEvent(
                task_id=task.id,
                client_event_id=event.client_event_id,
                timestamp_ms=event.timestamp_ms,
                action_type=event.action_type,
                label_temp_id=event.label_temp_id,
                before=event.before,
                after=event.after,
                details=event.details,
            )
        )

    golds = [box_from_orm(gold) for gold in task.image.gold_labels]
    matches = match_predictions(
        [box_from_orm(row) for row in final_rows],
        golds,
        iou_threshold=get_config().matching.iou_threshold,
        duplicate_iou_threshold=get_config().matching.duplicate_iou_threshold,
    )
    by_pred = {match.pred_id: match for match in matches if match.pred_id is not None}
    for row in final_rows:
        match = by_pred.get(row.id)
        if match:
            row.matched_gold_id = match.gold_id
            row.error_type = match.error_type

    task.status = TaskStatus.submitted
    task.submitted_at = datetime.utcnow()
    task.review_time_ms = review_time_ms
    task.started_at_client_ms = started_at_client_ms
    db.add(task)
    db.commit()
    for row in final_rows:
        db.refresh(row)
    db.refresh(task)
    return final_rows, summarize_errors(matches)


def append_events(db: Session, *, task: AnnotationTask, events: list[AnnotationEventIn]) -> list[AnnotationEvent]:
    rows = [
        AnnotationEvent(
            task_id=task.id,
            client_event_id=event.client_event_id,
            timestamp_ms=event.timestamp_ms,
            action_type=event.action_type,
            label_temp_id=event.label_temp_id,
            before=event.before,
            after=event.after,
            details=event.details,
        )
        for event in events
    ]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def annotate_ai_errors(db: Session, image_id: int) -> None:
    image = db.get(Image, image_id)
    if image is None:
        return
    golds = [box_from_orm(gold) for gold in image.gold_labels]
    suggestions = [box_from_orm(suggestion) for suggestion in image.ai_suggestions]
    matches = match_predictions(
        suggestions,
        golds,
        iou_threshold=get_config().matching.iou_threshold,
        duplicate_iou_threshold=get_config().matching.duplicate_iou_threshold,
    )
    by_pred = {match.pred_id: match for match in matches if match.pred_id is not None}
    for suggestion in image.ai_suggestions:
        match = by_pred.get(suggestion.id)
        if match:
            suggestion.ai_error_type = match.error_type
            db.add(suggestion)
    db.commit()


def export_rows(db: Session) -> list[dict[str, Any]]:
    tasks = (
        db.query(AnnotationTask)
        .filter(AnnotationTask.status == TaskStatus.submitted)
        .order_by(AnnotationTask.id.asc())
        .all()
    )
    rows: list[dict[str, Any]] = []
    for task in tasks:
        events = list(task.events)
        event_counts = Counter(event.action_type for event in events)
        suggestions = list(task.image.ai_suggestions)
        gold_count = len(task.image.gold_labels)
        ai_error_count = sum(1 for suggestion in suggestions if suggestion.ai_error_type != "correct")
        mean_ai_conf = (
            sum(float(s.confidence or 0.0) for s in suggestions) / len(suggestions)
            if suggestions
            else 0.0
        )
        for label in task.final_labels:
            source = next((s for s in suggestions if s.id == label.source_suggestion_id), None)
            has_error = label.error_type != "correct"
            rows.append(
                {
                    "task_id": task.id,
                    "image_id": task.image_id,
                    "label_id": label.id,
                    "condition": task.condition.value,
                    "category": label.category,
                    "error_type": label.error_type or "unknown",
                    "target_error": int(has_error),
                    "review_time_ms": task.review_time_ms or 0,
                    "event_count": len(events),
                    "box_create_count": event_counts.get("box_create", 0),
                    "box_edit_count": event_counts.get("box_edit", 0),
                    "box_delete_count": event_counts.get("box_delete", 0),
                    "class_change_count": event_counts.get("class_change", 0),
                    "confirm_count": event_counts.get("confirm", 0),
                    "final_area": label.width * label.height,
                    "source_ai_confidence": source.confidence if source else None,
                    "source_ai_conf_bucket": confidence_bucket(source.confidence if source else None),
                    "source_ai_error_type": source.ai_error_type if source else "none",
                    "ai_suggestion_count": len(suggestions),
                    "ai_error_count": ai_error_count,
                    "mean_ai_confidence": mean_ai_conf,
                    "gold_count": gold_count,
                    "image_width": task.image.width or 0,
                    "image_height": task.image.height or 0,
                    "scene_dataset": task.image.dataset,
                    "scene_split": task.image.split,
                }
            )
        if not task.final_labels:
            rows.append(
                {
                    "task_id": task.id,
                    "image_id": task.image_id,
                    "label_id": None,
                    "condition": task.condition.value,
                    "category": "none",
                    "error_type": "miss" if gold_count else "correct",
                    "target_error": int(gold_count > 0),
                    "review_time_ms": task.review_time_ms or 0,
                    "event_count": len(events),
                    "box_create_count": event_counts.get("box_create", 0),
                    "box_edit_count": event_counts.get("box_edit", 0),
                    "box_delete_count": event_counts.get("box_delete", 0),
                    "class_change_count": event_counts.get("class_change", 0),
                    "confirm_count": event_counts.get("confirm", 0),
                    "final_area": 0,
                    "source_ai_confidence": None,
                    "source_ai_conf_bucket": "unknown",
                    "source_ai_error_type": "none",
                    "ai_suggestion_count": len(suggestions),
                    "ai_error_count": ai_error_count,
                    "mean_ai_confidence": mean_ai_conf,
                    "gold_count": gold_count,
                    "image_width": task.image.width or 0,
                    "image_height": task.image.height or 0,
                    "scene_dataset": task.image.dataset,
                    "scene_split": task.image.split,
                }
            )
    return rows


def refresh_scln_features(db: Session) -> int:
    db.query(SCLNFeature).delete()
    count = 0
    for row in export_rows(db):
        feature_json = dict(row)
        task_id = int(feature_json.pop("task_id"))
        label_id = feature_json.pop("label_id")
        target_error = bool(feature_json.get("target_error"))
        db.add(SCLNFeature(task_id=task_id, label_id=label_id, feature_json=feature_json, target_error=target_error))
        count += 1
    db.commit()
    return count


def resolve_image_path(file_name: str) -> Path:
    path = Path(file_name)
    if path.is_absolute():
        return path
    if path.exists():
        return path.resolve()
    return Path(get_config().paths.image_root) / path
