from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


POLICIES = {
    "Random": None,
    "Low-confidence": "low_confidence_score",
    "High-confidence": "high_confidence_score",
    "High-loss": "target_error",
    "Ensemble disagreement": "disagreement_score",
    "Confident learning": "confident_learning_score",
    "SCLNScore": "SCLNScore",
}


def _prepare_scores(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    scored = frame.copy()
    confidence = pd.to_numeric(scored.get("source_ai_confidence"), errors="coerce").fillna(0.0)
    scored["low_confidence_score"] = 1.0 - confidence
    scored["high_confidence_score"] = confidence
    scored["disagreement_score"] = pd.to_numeric(scored.get("ai_error_count"), errors="coerce").fillna(0.0)
    scored["confident_learning_score"] = confidence * pd.to_numeric(scored.get("target_error"), errors="coerce").fillna(0.0)
    scored["random_score"] = rng.random(len(scored))
    if "SCLNScore" not in scored:
        scored["SCLNScore"] = scored["low_confidence_score"]
    return scored


def evaluate_review_policies(features: Path, output_dir: Path, budgets: list[float], seed: int = 42) -> pd.DataFrame:
    frame = pd.read_csv(features)
    if frame.empty:
        raise ValueError("Feature file is empty")
    frame["target_error"] = frame["target_error"].astype(int)
    scored = _prepare_scores(frame, seed)
    total_errors = max(1, int(scored["target_error"].sum()))
    rows = []

    for policy, score_column in POLICIES.items():
        column = score_column or "random_score"
        ranked = scored.sort_values(column, ascending=False).reset_index(drop=True)
        for budget in budgets:
            k = max(1, int(np.ceil(len(ranked) * budget)))
            selected = ranked.head(k)
            caught = int(selected["target_error"].sum())
            precision = caught / k
            recall = caught / total_errors
            rows.append(
                {
                    "policy": policy,
                    "budget": budget,
                    "k": k,
                    "errors_caught": caught,
                    "precision_at_k": precision,
                    "recall_at_budget": recall,
                    "cost_normalized_gain": recall / budget if budget > 0 else 0.0,
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    report = pd.DataFrame(rows)
    report.to_csv(output_dir / "review_policy_metrics.csv", index=False)
    for budget in budgets:
        k = max(1, int(np.ceil(len(scored) * budget)))
        scored.sort_values("SCLNScore", ascending=False).head(k).to_csv(
            output_dir / f"scln_candidates_budget_{int(budget * 100)}.csv",
            index=False,
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate review candidate ranking policies")
    parser.add_argument("--features", required=True, help="CSV from train_sclnscore or export_features")
    parser.add_argument("--output-dir", default="outputs/review")
    parser.add_argument("--budgets", default="0.01,0.05,0.10,0.20")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    budgets = [float(item) for item in args.budgets.split(",") if item]
    report = evaluate_review_policies(Path(args.features), Path(args.output_dir), budgets, seed=args.seed)
    print(f"Wrote {len(report)} policy rows under {args.output_dir}")


if __name__ == "__main__":
    main()

