from __future__ import annotations

import json
from pathlib import Path

from backend.app.models import AnnotationTask, Condition, TaskStatus
from backend.app.services import resolve_image_path
from backend.app.services import claim_task


def test_same_annotator_cannot_claim_same_image_across_conditions(db_session, seeded_db) -> None:
    first = claim_task(db_session, annotator_id="ann-1", condition=Condition.human_only)
    assert first is not None
    second = claim_task(db_session, annotator_id="ann-1")
    assert second is not None
    assert second.id == first.id

    other = claim_task(db_session, annotator_id="ann-2", condition=Condition.ai_assisted)
    assert other is not None
    assert other.image_id == seeded_db.id


def test_condition_suggestions_visibility(client, seeded_db) -> None:
    human = client.post("/tasks/claim", json={"annotator_id": "human", "condition": "human_only"})
    assert human.status_code == 200
    assert human.json()["suggestions"] == []
    assert "condition" not in human.json()["task"]

    ai = client.post("/tasks/claim", json={"annotator_id": "ai", "condition": "ai_assisted"})
    assert ai.status_code == 200
    ai_suggestions = ai.json()["suggestions"]
    assert len(ai_suggestions) == 1
    assert ai_suggestions[0]["confidence"] is None

    ai_conf = client.post(
        "/tasks/claim",
        json={"annotator_id": "ai-conf", "condition": "ai_assisted_confidence"},
    )
    assert ai_conf.status_code == 200
    conf_suggestions = ai_conf.json()["suggestions"]
    assert len(conf_suggestions) == 1
    assert conf_suggestions[0]["confidence"] == 0.91


def test_task_draft_is_saved_and_recovered(client, seeded_db) -> None:
    response = client.post("/tasks/claim", json={"annotator_id": "ann-draft", "condition": "ai_assisted"})
    assert response.status_code == 200
    task_id = response.json()["task"]["id"]
    draft = {
        "paused": True,
        "elapsedMs": 2400,
        "mode": "select",
        "activeClass": "truck",
        "selectedId": "manual-1",
        "labels": [
            {
                "temp_id": "manual-1",
                "category": "truck",
                "x": 12,
                "y": 14,
                "width": 18,
                "height": 20,
                "confidence": None,
                "source_suggestion_id": None,
            }
        ],
        "events": [
            {
                "client_event_id": "draft-event-1",
                "timestamp_ms": 1100,
                "action_type": "box_create",
            }
        ],
    }
    saved = client.post(
        f"/tasks/{task_id}/draft",
        json={"annotator_id": "ann-draft", "draft": draft},
    )
    assert saved.status_code == 200

    recovered = client.post("/tasks/claim", json={"annotator_id": "ann-draft"})
    assert recovered.status_code == 200
    payload = recovered.json()
    assert payload["task"]["id"] == task_id
    assert payload["task"]["metadata_json"]["draft"]["paused"] is True
    assert payload["task"]["metadata_json"]["draft"]["labels"][0]["category"] == "truck"


def test_submit_task_matches_gold_and_exports_features(client, db_session, seeded_db) -> None:
    response = client.post("/tasks/claim", json={"annotator_id": "ann-submit", "condition": "human_only"})
    task_id = response.json()["task"]["id"]
    submit = client.post(
        f"/tasks/{task_id}/submit",
        json={
            "annotator_id": "ann-submit",
            "review_time_ms": 1200,
            "labels": [{"category": "car", "x": 10, "y": 10, "width": 30, "height": 30}],
            "events": [
                {
                    "client_event_id": "e1",
                    "timestamp_ms": 100,
                    "action_type": "box_create",
                    "details": {},
                }
            ],
        },
    )
    assert submit.status_code == 200
    assert submit.json()["errors"]["correct"] == 1
    task = db_session.get(AnnotationTask, task_id)
    assert task.status == TaskStatus.submitted

    exported = client.get("/export/features")
    assert exported.status_code == 200
    rows = exported.json()["rows"]
    assert len(rows) == 1
    assert rows[0]["condition"] == "human_only"
    assert rows[0]["target_error"] == 0

    stats = client.get("/stats/summary")
    assert stats.status_code == 200
    assert stats.json()["tasks_submitted"] == 1


def test_resolve_image_path_prefers_existing_relative_path(tmp_path, monkeypatch) -> None:
    path = tmp_path / "existing.jpg"
    path.write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    assert resolve_image_path("existing.jpg") == path


def test_latest_report_api(client, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    report_dir = Path("outputs/report")
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text(json.dumps({"total_rows": 1, "total_errors": 0}), encoding="utf-8")
    (report_dir / "report.md").write_text("# Report", encoding="utf-8")

    response = client.get("/reports/latest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["total_rows"] == 1
    assert any(item["name"] == "report_markdown" and item["exists"] for item in payload["artifacts"])
