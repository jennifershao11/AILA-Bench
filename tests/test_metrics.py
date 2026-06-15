from __future__ import annotations

from backend.app.metrics import Box, bbox_iou, confidence_bucket, match_predictions, scln_score, summarize_errors


def test_bbox_iou() -> None:
    assert bbox_iou(Box(0, 0, 10, 10), Box(0, 0, 10, 10)) == 1.0
    assert bbox_iou(Box(0, 0, 10, 10), Box(20, 20, 10, 10)) == 0.0
    assert round(bbox_iou(Box(0, 0, 10, 10), Box(5, 5, 10, 10)), 4) == 0.1429


def test_match_predictions_error_types() -> None:
    golds = [
        Box(0, 0, 10, 10, "car", id=1),
        Box(40, 40, 10, 10, "bus", id=2),
    ]
    predictions = [
        Box(0, 0, 10, 10, "car", id=11),
        Box(40, 40, 10, 10, "truck", id=12),
        Box(0, 0, 10, 10, "car", id=13),
        Box(90, 90, 5, 5, "car", id=14),
    ]
    matches = match_predictions(predictions, golds)
    summary = summarize_errors(matches)
    assert summary["correct"] == 1
    assert summary["class_error"] == 1
    assert summary["duplicate"] == 1
    assert summary["false_positive"] == 1


def test_confidence_bucket_and_scln_score() -> None:
    assert confidence_bucket(None) == "unknown"
    assert confidence_bucket(0.2) == "0.00-0.25"
    assert confidence_bucket(0.5) == "0.50-0.75"
    assert confidence_bucket(0.99) == "0.75-1.00"
    assert scln_score(0.8, 0.3) == 0.5

