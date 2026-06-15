from __future__ import annotations

import argparse
import shutil
import subprocess
import tarfile
from pathlib import Path
from urllib.request import urlretrieve


YOLO11N_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
NUIMAGES_MINI_URL = "https://www.nuscenes.org/data/nuimages-v1.0-mini.tgz"


def download(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        return
    tmp = output.with_suffix(output.suffix + ".tmp")
    urlretrieve(url, tmp)
    tmp.replace(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download public MVP assets")
    parser.add_argument("--models-dir", default="models")
    parser.add_argument("--downloads-dir", default="data/downloads")
    parser.add_argument("--nuimages-root", default="data/nuimages")
    parser.add_argument("--skip-nuimages", action="store_true")
    args = parser.parse_args()

    yolo_path = Path(args.models_dir) / "yolo11n.pt"
    download(YOLO11N_URL, yolo_path)
    print(f"YOLO11n: {yolo_path}")

    if not args.skip_nuimages:
        archive = Path(args.downloads_dir) / "nuimages-v1.0-mini.tgz"
        download(NUIMAGES_MINI_URL, archive)
        target = Path(args.nuimages_root)
        target.mkdir(parents=True, exist_ok=True)
        if not (target / "v1.0-mini").exists():
            with tarfile.open(archive, "r:gz") as handle:
                handle.extractall(target)
        print(f"nuImages mini: {target}")


if __name__ == "__main__":
    main()

