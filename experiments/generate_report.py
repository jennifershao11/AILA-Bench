from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _safe_rate(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _write_table(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def _markdown_table(frame: pd.DataFrame, *, max_rows: int = 20) -> str:
    if frame.empty:
        return "No rows."
    view = frame.head(max_rows).copy()
    columns = [str(column) for column in view.columns]
    rows = [[str(value) for value in row] for row in view.to_numpy().tolist()]
    widths = [
        max(len(columns[index]), *(len(row[index]) for row in rows))
        for index in range(len(columns))
    ]
    header = "| " + " | ".join(columns[index].ljust(widths[index]) for index in range(len(columns))) + " |"
    divider = "| " + " | ".join("-" * widths[index] for index in range(len(columns))) + " |"
    body = [
        "| " + " | ".join(row[index].ljust(widths[index]) for index in range(len(columns))) + " |"
        for row in rows
    ]
    suffix = [f"\nShowing {len(view)} of {len(frame)} rows."] if len(frame) > len(view) else []
    return "\n".join([header, divider, *body, *suffix])


def generate_report(
    *,
    features_path: Path,
    review_metrics_path: Path,
    output_dir: Path,
) -> dict:
    features = pd.read_csv(features_path)
    review = pd.read_csv(review_metrics_path) if review_metrics_path.exists() else pd.DataFrame()
    if features.empty:
        raise ValueError("features file is empty")

    features["target_error"] = features["target_error"].astype(int)
    total_rows = len(features)
    total_errors = int(features["target_error"].sum())

    rq1 = (
        features.groupby("condition", dropna=False)
        .agg(
            labels=("target_error", "size"),
            errors=("target_error", "sum"),
            mean_review_time_ms=("review_time_ms", "mean"),
        )
        .reset_index()
    )
    rq1["fder"] = rq1.apply(lambda row: _safe_rate(row["errors"], row["labels"]), axis=1)

    error_distribution = (
        features.groupby(["condition", "error_type"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["condition", "count"], ascending=[True, False])
    )

    ai_rows = features[features["condition"].isin(["ai_assisted", "ai_assisted_confidence"])].copy()
    if not ai_rows.empty:
        ai_rows["human_changed_ai"] = (
            (ai_rows["box_edit_count"].fillna(0) > 0)
            | (ai_rows["class_change_count"].fillna(0) > 0)
            | (ai_rows["box_delete_count"].fillna(0) > 0)
        ).astype(int)
        rq2 = (
            ai_rows.groupby(["source_ai_conf_bucket", "category"], dropna=False)
            .agg(
                labels=("target_error", "size"),
                errors=("target_error", "sum"),
                human_changes=("human_changed_ai", "sum"),
                mean_ai_confidence=("source_ai_confidence", "mean"),
            )
            .reset_index()
        )
        rq2["hcear"] = rq2.apply(lambda row: _safe_rate(row["human_changes"], row["errors"]), axis=1)
        rq2["hcr"] = rq2.apply(lambda row: _safe_rate(row["human_changes"], row["labels"]), axis=1)
        rq2["fcwr"] = rq2.apply(lambda row: _safe_rate(row["errors"], row["human_changes"]), axis=1)
    else:
        rq2 = pd.DataFrame(columns=["source_ai_conf_bucket", "category", "labels", "errors", "human_changes", "hcear", "hcr", "fcwr"])

    if not review.empty:
        rq3 = review.sort_values(["budget", "recall_at_budget"], ascending=[True, False])
    else:
        rq3 = pd.DataFrame()

    ablation_rows = []
    feature_groups = {
        "AI": ["source_ai_confidence", "ai_suggestion_count", "ai_error_count", "mean_ai_confidence"],
        "Trace": ["event_count", "box_create_count", "box_edit_count", "box_delete_count", "class_change_count", "confirm_count"],
        "Object": ["category", "final_area"],
        "Scene": ["image_width", "image_height", "gold_count", "scene_dataset", "scene_split"],
        "Interface": ["condition", "review_time_ms"],
    }
    scored_column = "SCLNScore" if "SCLNScore" in features.columns else None
    for group_name, columns in feature_groups.items():
        present = [column for column in columns if column in features.columns]
        coverage = sum(features[column].notna().mean() for column in present) / len(present) if present else 0.0
        ablation_rows.append(
            {
                "feature_group": group_name,
                "available_features": len(present),
                "coverage": coverage,
                "score_column_present": bool(scored_column),
            }
        )
    rq4 = pd.DataFrame(ablation_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_table(output_dir / "rq1_condition_fder.csv", rq1)
    _write_table(output_dir / "rq1_error_distribution.csv", error_distribution)
    _write_table(output_dir / "rq2_human_ai_interaction.csv", rq2)
    if not rq3.empty:
        _write_table(output_dir / "rq3_review_policies.csv", rq3)
    _write_table(output_dir / "rq4_feature_group_coverage.csv", rq4)

    best_policy = None
    if not rq3.empty:
        row = rq3.sort_values(["budget", "recall_at_budget"], ascending=[True, False]).iloc[0]
        best_policy = {
            "policy": row["policy"],
            "budget": float(row["budget"]),
            "recall_at_budget": float(row["recall_at_budget"]),
            "precision_at_k": float(row["precision_at_k"]),
        }

    summary = {
        "features_path": str(features_path),
        "review_metrics_path": str(review_metrics_path),
        "total_rows": total_rows,
        "total_errors": total_errors,
        "overall_error_rate": _safe_rate(total_errors, total_rows),
        "conditions": rq1.to_dict(orient="records"),
        "best_low_budget_policy": best_policy,
        "outputs": {
            "rq1_condition_fder": str(output_dir / "rq1_condition_fder.csv"),
            "rq1_error_distribution": str(output_dir / "rq1_error_distribution.csv"),
            "rq2_human_ai_interaction": str(output_dir / "rq2_human_ai_interaction.csv"),
            "rq3_review_policies": str(output_dir / "rq3_review_policies.csv"),
            "rq4_feature_group_coverage": str(output_dir / "rq4_feature_group_coverage.csv"),
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    markdown = [
        "# AILA-Bench Experiment Report",
        "",
        f"- Rows: {total_rows}",
        f"- Errors: {total_errors}",
        f"- Overall error rate: {summary['overall_error_rate']:.4f}",
        "",
        "## RQ1 Condition FDER",
        _markdown_table(rq1),
        "",
        "## RQ3 Review Policies",
        _markdown_table(rq3) if not rq3.empty else "No review policy table available.",
        "",
        "## RQ4 Feature Group Coverage",
        _markdown_table(rq4),
        "",
    ]
    (output_dir / "report.md").write_text("\n".join(markdown), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RQ summary tables and Markdown report")
    parser.add_argument("--features", default="outputs/scln/features_scored.csv")
    parser.add_argument("--review-metrics", default="outputs/review/review_policy_metrics.csv")
    parser.add_argument("--output-dir", default="outputs/report")
    args = parser.parse_args()
    summary = generate_report(
        features_path=Path(args.features),
        review_metrics_path=Path(args.review_metrics),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
