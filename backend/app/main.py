from __future__ import annotations

from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.config import get_config
from backend.app.database import get_db, init_db
from backend.app.models import AISuggestion, AnnotationTask, TaskStatus
from backend.app.models import AnnotationEvent, FinalLabel, Image
from backend.app.schemas import (
    AISuggestionOut,
    ClaimTaskRequest,
    ExportOut,
    EventLogRequest,
    ReportOut,
    ArtifactOut,
    PublicTaskBundleOut,
    PublicTaskOut,
    StatsOut,
    SubmitTaskRequest,
    SubmitTaskResponse,
    TaskDraftRequest,
    TaskBundleOut,
    TaskOut,
)
from backend.app import services


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AILA-Bench SCLN-Det MVP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def config() -> dict[str, object]:
    cfg = get_config()
    return {"classes": cfg.classes, "conditions": cfg.conditions, "budgets": cfg.budgets}


@app.get("/stats/summary", response_model=StatsOut)
def stats_summary(db: Session = Depends(get_db)) -> StatsOut:
    tasks = db.query(AnnotationTask).all()
    return StatsOut(
        images=db.query(Image).count(),
        tasks_total=len(tasks),
        tasks_pending=sum(1 for task in tasks if task.status == TaskStatus.pending),
        tasks_in_progress=sum(1 for task in tasks if task.status == TaskStatus.in_progress),
        tasks_submitted=sum(1 for task in tasks if task.status == TaskStatus.submitted),
        final_labels=db.query(FinalLabel).count(),
        annotation_events=db.query(AnnotationEvent).count(),
        ai_suggestions=db.query(AISuggestion).count(),
        conditions={
            condition: sum(1 for task in tasks if task.condition.value == condition)
            for condition in get_config().conditions
        },
    )


@app.get("/reports/latest", response_model=ReportOut)
def latest_report() -> ReportOut:
    yolo_path = Path("outputs/bdd100k/yolo11_predictions.jsonl")
    if not yolo_path.exists():
        yolo_path = Path("outputs/yolo11_nuimages_predictions.jsonl")
    artifact_paths = {
        "features": Path("outputs/features.csv"),
        "scored_features": Path("outputs/scln/features_scored.csv"),
        "review_metrics": Path("outputs/review/review_policy_metrics.csv"),
        "report_markdown": Path("outputs/report/report.md"),
        "report_summary": Path("outputs/report/summary.json"),
        "yolo_predictions": yolo_path,
    }
    artifacts = [
        ArtifactOut(
            name=name,
            path=str(path),
            exists=path.exists(),
            size_bytes=path.stat().st_size if path.exists() else None,
        )
        for name, path in artifact_paths.items()
    ]
    summary_path = artifact_paths["report_summary"]
    summary = None
    if summary_path.exists():
        with summary_path.open("r", encoding="utf-8") as handle:
            summary = json.load(handle)
    return ReportOut(summary=summary, artifacts=artifacts)


@app.get("/reports/artifacts/{artifact_name}")
def download_artifact(artifact_name: str) -> FileResponse:
    yolo_path = Path("outputs/bdd100k/yolo11_predictions.jsonl")
    if not yolo_path.exists():
        yolo_path = Path("outputs/yolo11_nuimages_predictions.jsonl")
    allowed = {
        "features": Path("outputs/features.csv"),
        "scored_features": Path("outputs/scln/features_scored.csv"),
        "review_metrics": Path("outputs/review/review_policy_metrics.csv"),
        "report_markdown": Path("outputs/report/report.md"),
        "report_summary": Path("outputs/report/summary.json"),
        "yolo_predictions": yolo_path,
    }
    path = allowed.get(artifact_name)
    if path is None:
        raise HTTPException(status_code=404, detail="Unknown artifact")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Artifact not found: {path}")
    return FileResponse(path)


@app.post("/tasks/claim", response_model=PublicTaskBundleOut)
def claim_task(payload: ClaimTaskRequest, db: Session = Depends(get_db)) -> PublicTaskBundleOut:
    task = services.claim_task(db, annotator_id=payload.annotator_id, condition=payload.condition)
    if task is None:
        raise HTTPException(status_code=404, detail="No eligible tasks available")
    return _public_task_bundle(db, task)


@app.get("/tasks/{task_id}", response_model=PublicTaskBundleOut)
def get_task(task_id: int, annotator_id: str | None = None, db: Session = Depends(get_db)) -> PublicTaskBundleOut:
    task = services.get_task_for_annotator(db, task_id, annotator_id=annotator_id)
    return _public_task_bundle(db, task)


@app.post("/tasks/{task_id}/draft")
def save_task_draft(task_id: int, payload: TaskDraftRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    task = services.get_task_for_annotator(db, task_id, annotator_id=payload.annotator_id)
    task.metadata_json = {**(task.metadata_json or {}), "draft": payload.draft}
    db.add(task)
    db.commit()
    return {"status": "ok"}


@app.post("/tasks/{task_id}/events")
def log_events(task_id: int, payload: EventLogRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    task = services.get_task_for_annotator(db, task_id, annotator_id=payload.annotator_id)
    rows = services.append_events(db, task=task, events=payload.events)
    return {"inserted": len(rows)}


@app.post("/tasks/{task_id}/submit", response_model=SubmitTaskResponse)
def submit_task(
    task_id: int,
    payload: SubmitTaskRequest,
    db: Session = Depends(get_db),
) -> SubmitTaskResponse:
    task = services.get_task_for_annotator(db, task_id, annotator_id=payload.annotator_id)
    if task.status not in {TaskStatus.in_progress, TaskStatus.pending}:
        raise HTTPException(status_code=409, detail=f"Task is already {task.status.value}")
    final_labels, errors = services.submit_task(
        db,
        task=task,
        labels=payload.labels,
        events=payload.events,
        review_time_ms=payload.review_time_ms,
        started_at_client_ms=payload.started_at_client_ms,
    )
    return SubmitTaskResponse(task=TaskOut.model_validate(task), final_labels=final_labels, errors=errors)


@app.get("/images/{image_id}/file")
def image_file(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    from backend.app.models import Image

    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    path = services.resolve_image_path(image.file_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Image file not found: {path}")
    return FileResponse(path)


@app.get("/export/features", response_model=ExportOut)
def export_features(db: Session = Depends(get_db)) -> ExportOut:
    return ExportOut(rows=services.export_rows(db))


@app.post("/export/refresh-scln-features")
def refresh_features(db: Session = Depends(get_db)) -> dict[str, int]:
    return {"inserted": services.refresh_scln_features(db)}


def _task_bundle(db: Session, task: AnnotationTask) -> TaskBundleOut:
    db.refresh(task)
    suggestions = []
    if services.allowed_suggestions_for_condition(task):
        suggestions = (
            db.query(AISuggestion)
            .filter(AISuggestion.image_id == task.image_id)
            .order_by(AISuggestion.id.asc())
            .all()
        )
    suggestion_outputs = [AISuggestionOut.model_validate(suggestion) for suggestion in suggestions]
    if task.condition.value == "ai_assisted":
        suggestion_outputs = [suggestion.model_copy(update={"confidence": None}) for suggestion in suggestion_outputs]
    display_condition = "standard"
    if task.condition.value in {"ai_assisted", "ai_assisted_confidence"}:
        display_condition = "reference"
    return TaskBundleOut(
        task=task,
        image=task.image,
        suggestions=suggestion_outputs,
        classes=get_config().classes,
        display_condition=display_condition,
        show_confidence=task.condition.value == "ai_assisted_confidence",
    )


def _public_task_bundle(db: Session, task: AnnotationTask) -> PublicTaskBundleOut:
    bundle = _task_bundle(db, task)
    return PublicTaskBundleOut(
        task=PublicTaskOut(
            id=task.id,
            image_id=task.image_id,
            status=task.status,
            annotator_id=task.annotator_id,
            review_time_ms=task.review_time_ms,
            metadata_json=task.metadata_json or {},
        ),
        image=bundle.image,
        suggestions=bundle.suggestions,
        classes=bundle.classes,
        display_condition=bundle.display_condition,
        show_confidence=bundle.show_confidence,
    )
