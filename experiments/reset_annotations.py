from __future__ import annotations

import argparse

from backend.app.models import AnnotationEvent, AnnotationTask, FinalLabel, ReviewScore, SCLNFeature, TaskStatus
from experiments.common import add_config_arg, open_session, parse_config


def reset_annotations(db) -> dict[str, int]:
    counts = {
        "review_scores": db.query(ReviewScore).delete(),
        "scln_features": db.query(SCLNFeature).delete(),
        "annotation_events": db.query(AnnotationEvent).delete(),
        "final_labels": db.query(FinalLabel).delete(),
    }
    tasks = db.query(AnnotationTask).all()
    for task in tasks:
        task.status = TaskStatus.pending
        task.annotator_id = None
        task.assigned_at = None
        task.submitted_at = None
        task.review_time_ms = None
        task.started_at_client_ms = None
        db.add(task)
    counts["tasks_reset"] = len(tasks)
    db.commit()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Clear submitted annotations and reopen all tasks")
    add_config_arg(parser)
    args = parser.parse_args()
    config = parse_config(args)
    db = open_session(config)
    try:
        counts = reset_annotations(db)
    finally:
        db.close()
    print(counts)


if __name__ == "__main__":
    main()

