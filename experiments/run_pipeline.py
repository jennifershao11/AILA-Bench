from __future__ import annotations

import argparse
import subprocess
import sys


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run official-data setup or post-annotation experiment outputs")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--dataset", choices=["bdd100k", "nuimages-mini"], default="bdd100k")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--skip-yolo", action="store_true")
    parser.add_argument("--skip-import", action="store_true")
    parser.add_argument("--labels", default="data/bdd100k_prepared/bdd100k_labels/100k/train")
    parser.add_argument("--image-root", default="data/bdd100k_prepared/bdd100k_images_100k/100k/train")
    parser.add_argument("--weights", default="models/yolo11n.pt")
    parser.add_argument("--post-annotation", action="store_true", help="Export features, train SCLNScore, and generate reports")
    args = parser.parse_args()

    py = sys.executable
    if not args.skip_import:
        if args.dataset == "bdd100k":
            run(
                [
                    py,
                    "-m",
                    "experiments.import_bdd100k",
                    "--config",
                    args.config,
                    "--bdd-labels",
                    args.labels,
                    "--image-root",
                    args.image_root,
                    "--limit",
                    str(args.limit),
                    "--reset-db",
                ]
            )
        else:
            run([py, "-m", "experiments.download_assets"])
            run(
                [
                    py,
                    "-m",
                    "experiments.import_nuimages",
                    "--config",
                    args.config,
                    "--nuimages-root",
                    "data/nuimages",
                    "--limit",
                    str(args.limit),
                    "--reset-db",
                ]
            )

        run([py, "-m", "experiments.create_tasks", "--config", args.config])

    if args.dataset == "bdd100k" and not args.skip_yolo:
        run(
            [
                py,
                "-m",
                "experiments.yolo11_pipeline",
                "--config",
                args.config,
                "--dataset",
                "bdd100k",
                "--split",
                "pilot",
                "--limit",
                str(args.limit),
                "--weights",
                args.weights,
                "--output",
                "outputs/bdd100k/yolo11_predictions.jsonl",
            ]
        )
        run(
            [
                py,
                "-m",
                "experiments.import_suggestions",
                "--config",
                args.config,
                "--input",
                "outputs/bdd100k/yolo11_predictions.jsonl",
            ]
        )

    if not args.post_annotation:
        return

    run(
        [
            py,
            "-m",
            "experiments.export_features",
            "--config",
            args.config,
            "--output",
            "outputs/features.csv",
            "--refresh-db",
        ]
    )
    run([py, "-m", "experiments.train_sclnscore", "--features", "outputs/features.csv", "--output-dir", "outputs/scln"])
    run(
        [
            py,
            "-m",
            "experiments.evaluate_review",
            "--features",
            "outputs/scln/features_scored.csv",
            "--output-dir",
            "outputs/review",
        ]
    )
    run(
        [
            py,
            "-m",
            "experiments.generate_report",
            "--features",
            "outputs/scln/features_scored.csv",
            "--review-metrics",
            "outputs/review/review_policy_metrics.csv",
            "--output-dir",
            "outputs/report",
        ]
    )


if __name__ == "__main__":
    main()
