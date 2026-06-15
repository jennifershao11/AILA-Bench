from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="GroundingDINO disagreement feature interface")
    parser.add_argument("--detections", required=True)
    parser.add_argument("--output", default="outputs/disagreement.jsonl")
    parser.parse_args()
    raise SystemExit(
        "GroundingDINO is optional in the MVP. Produce per-suggestion disagreement JSON and merge it into "
        "the 'disagreement' field accepted by experiments.import_suggestions."
    )


if __name__ == "__main__":
    main()

