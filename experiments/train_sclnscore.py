from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DROP_COLUMNS = {"target_error", "error_type", "task_id", "image_id", "label_id"}


def _feature_columns(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = []
    categorical = []
    for column in frame.columns:
        if column in DROP_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(frame[column]):
            numeric.append(column)
        else:
            categorical.append(column)
    return numeric, categorical


def _pipeline(frame: pd.DataFrame, classifier: LogisticRegression | DummyClassifier | None = None) -> Pipeline:
    numeric, categorical = _feature_columns(frame)
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocessor),
            ("model", classifier or LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def _probability(model: Pipeline, frame: pd.DataFrame) -> np.ndarray:
    if len(getattr(model.named_steps["model"], "classes_", [])) == 1:
        only_class = int(model.named_steps["model"].classes_[0])
        return np.ones(len(frame)) if only_class == 1 else np.zeros(len(frame))
    return model.predict_proba(frame)[:, 1]


def train_sclnscore(features: Path, output_dir: Path) -> pd.DataFrame:
    frame = pd.read_csv(features)
    if frame.empty:
        raise ValueError("Feature file is empty")
    frame["target_error"] = frame["target_error"].astype(int)
    ai_mask = frame["condition"].isin(["ai_assisted", "ai_assisted_confidence"])
    human_mask = frame["condition"].eq("human_only")
    if ai_mask.sum() == 0 or human_mask.sum() == 0:
        raise ValueError("Need both AI-assisted and human_only rows to train SCLNScore")

    ai_y = frame.loc[ai_mask, "target_error"]
    human_y = frame.loc[human_mask, "target_error"]
    model_ai = _pipeline(
        frame[ai_mask],
        DummyClassifier(strategy="prior") if ai_y.nunique() < 2 else None,
    )
    model_human = _pipeline(
        frame[human_mask],
        DummyClassifier(strategy="prior") if human_y.nunique() < 2 else None,
    )
    model_ai.fit(frame[ai_mask].drop(columns=["target_error"]), ai_y)
    model_human.fit(frame[human_mask].drop(columns=["target_error"]), human_y)

    scored = frame.copy()
    model_input = scored.drop(columns=["target_error"])
    scored["p1_error_ai_trace"] = _probability(model_ai, model_input)
    scored["p0_error_human_sample"] = _probability(model_human, model_input)
    scored["SCLNScore"] = scored["p1_error_ai_trace"] - scored["p0_error_human_sample"]

    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_ai, output_dir / "p1_ai_trace_logreg.joblib")
    joblib.dump(model_human, output_dir / "p0_human_sample_logreg.joblib")
    scored.to_csv(output_dir / "features_scored.csv", index=False)

    metrics = {}
    y = scored["target_error"].to_numpy()
    if len(set(y)) > 1:
        metrics["auroc_scln"] = float(roc_auc_score(y, scored["SCLNScore"]))
        metrics["auprc_scln"] = float(average_precision_score(y, scored["SCLNScore"]))
    else:
        metrics["auroc_scln"] = None
        metrics["auprc_scln"] = None
    pd.DataFrame([metrics]).to_csv(output_dir / "metrics.csv", index=False)
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Train p1/p0 logistic baselines and compute SCLNScore")
    parser.add_argument("--features", required=True)
    parser.add_argument("--output-dir", default="outputs/scln")
    args = parser.parse_args()
    scored = train_sclnscore(Path(args.features), Path(args.output_dir))
    print(f"Scored {len(scored)} rows under {args.output_dir}")


if __name__ == "__main__":
    main()
