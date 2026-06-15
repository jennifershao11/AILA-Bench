from __future__ import annotations

from pathlib import Path

import pandas as pd

from experiments.evaluate_review import evaluate_review_policies
from experiments.train_sclnscore import train_sclnscore


def test_train_sclnscore_and_review_outputs(tmp_path: Path) -> None:
    rows = []
    for idx in range(24):
        condition = "human_only" if idx % 3 == 0 else "ai_assisted"
        target = 1 if idx % 4 == 0 else 0
        rows.append(
            {
                "task_id": idx,
                "image_id": idx // 3,
                "label_id": idx,
                "condition": condition,
                "category": "car" if idx % 2 else "bus",
                "error_type": "bbox_error" if target else "correct",
                "target_error": target,
                "review_time_ms": 1000 + idx,
                "event_count": idx % 5,
                "box_create_count": 1,
                "box_edit_count": idx % 2,
                "box_delete_count": 0,
                "class_change_count": idx % 3,
                "confirm_count": 1,
                "final_area": 900 + idx,
                "source_ai_confidence": 0.2 + (idx % 7) / 10,
                "source_ai_conf_bucket": "0.50-0.75",
                "source_ai_error_type": "correct",
                "ai_suggestion_count": 2,
                "ai_error_count": idx % 2,
                "mean_ai_confidence": 0.6,
                "gold_count": 2,
                "image_width": 100,
                "image_height": 100,
                "scene_dataset": "bdd100k",
                "scene_split": "pilot",
            }
        )
    features = tmp_path / "features.csv"
    pd.DataFrame(rows).to_csv(features, index=False)

    scored = train_sclnscore(features, tmp_path / "scln")
    assert "SCLNScore" in scored.columns
    assert (tmp_path / "scln" / "features_scored.csv").exists()

    report = evaluate_review_policies(tmp_path / "scln" / "features_scored.csv", tmp_path / "review", [0.1, 0.2])
    assert set(report["policy"]).issuperset({"Random", "SCLNScore"})
    assert (tmp_path / "review" / "review_policy_metrics.csv").exists()

