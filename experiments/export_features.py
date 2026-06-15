from __future__ import annotations

import argparse

from backend.app.services import export_rows, refresh_scln_features
from experiments.common import add_config_arg, open_session, parse_config, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Export submitted annotation features")
    add_config_arg(parser)
    parser.add_argument("--output", default="outputs/features.csv")
    parser.add_argument("--refresh-db", action="store_true", help="Also refresh scln_features table")
    args = parser.parse_args()
    config = parse_config(args)
    db = open_session(config)
    try:
        rows = export_rows(db)
        if args.refresh_db:
            refresh_scln_features(db)
    finally:
        db.close()
    write_csv(args.output, rows)
    print(f"Exported {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()

