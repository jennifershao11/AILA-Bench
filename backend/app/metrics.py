from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float
    category: str | None = None
    id: int | None = None
    confidence: float | None = None

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.height

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)


@dataclass(frozen=True)
class MatchResult:
    pred_id: int | None
    gold_id: int | None
    iou: float
    error_type: str


def bbox_iou(a: Box, b: Box) -> float:
    ix1 = max(a.x, b.x)
    iy1 = max(a.y, b.y)
    ix2 = min(a.x2, b.x2)
    iy2 = min(a.y2, b.y2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection = iw * ih
    union = a.area + b.area - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def _best_pairs(preds: list[Box], golds: list[Box]) -> list[tuple[int, int, float]]:
    pairs: list[tuple[int, int, float]] = []
    for pred_idx, pred in enumerate(preds):
        for gold_idx, gold in enumerate(golds):
            pairs.append((pred_idx, gold_idx, bbox_iou(pred, gold)))
    pairs.sort(key=lambda item: item[2], reverse=True)
    return pairs


def match_predictions(
    predictions: Iterable[Box],
    golds: Iterable[Box],
    *,
    iou_threshold: float = 0.5,
    duplicate_iou_threshold: float = 0.75,
) -> list[MatchResult]:
    preds = list(predictions)
    gold_list = list(golds)
    matched_preds: set[int] = set()
    matched_golds: set[int] = set()
    results: dict[int, MatchResult] = {}

    for pred_idx, gold_idx, iou in _best_pairs(preds, gold_list):
        if iou < iou_threshold or pred_idx in matched_preds or gold_idx in matched_golds:
            continue
        pred = preds[pred_idx]
        gold = gold_list[gold_idx]
        error_type = "correct" if pred.category == gold.category else "class_error"
        results[pred_idx] = MatchResult(pred.id, gold.id, iou, error_type)
        matched_preds.add(pred_idx)
        matched_golds.add(gold_idx)

    for pred_idx, pred in enumerate(preds):
        if pred_idx in results:
            continue
        duplicate_gold_id: int | None = None
        duplicate_iou = 0.0
        for gold_idx in matched_golds:
            iou = bbox_iou(pred, gold_list[gold_idx])
            if iou >= duplicate_iou_threshold and iou > duplicate_iou:
                duplicate_gold_id = gold_list[gold_idx].id
                duplicate_iou = iou
        if duplicate_gold_id is not None:
            results[pred_idx] = MatchResult(pred.id, duplicate_gold_id, duplicate_iou, "duplicate")
            continue

        best_gold_id: int | None = None
        best_iou = 0.0
        for gold in gold_list:
            iou = bbox_iou(pred, gold)
            if iou > best_iou:
                best_iou = iou
                best_gold_id = gold.id
        if best_iou > 0:
            error_type = "bbox_error" if best_iou >= 0.1 else "wrong_object"
            results[pred_idx] = MatchResult(pred.id, best_gold_id, best_iou, error_type)
        else:
            results[pred_idx] = MatchResult(pred.id, None, 0.0, "false_positive")

    output = [results[idx] for idx in range(len(preds))]
    for gold_idx, gold in enumerate(gold_list):
        if gold_idx not in matched_golds:
            output.append(MatchResult(None, gold.id, 0.0, "miss"))
    return output


def summarize_errors(matches: Iterable[MatchResult]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for match in matches:
        summary[match.error_type] = summary.get(match.error_type, 0) + 1
    return summary


def confidence_bucket(confidence: float | None) -> str:
    if confidence is None:
        return "unknown"
    if confidence < 0.25:
        return "0.00-0.25"
    if confidence < 0.50:
        return "0.25-0.50"
    if confidence < 0.75:
        return "0.50-0.75"
    return "0.75-1.00"


def scln_score(p1_error_given_ai_trace: float, p0_error_human_only_sample: float) -> float:
    return p1_error_given_ai_trace - p0_error_human_only_sample

