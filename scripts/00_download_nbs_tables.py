from __future__ import annotations

import argparse
from pathlib import Path

# Allow scripts to run directly from the repository root without requiring pip install -e . first.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import requests

from nigeria_crop_yield.data.nbs_parser import build_nbs_crop_yield_table
from nigeria_crop_yield.settings import load_config, resolve_path


def download_file(url: str, output_path: Path, skip_if_exists: bool = True) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if skip_if_exists and output_path.exists() and output_path.stat().st_size > 0:
        print(f"[skip] {output_path} already exists")
        return
    print(f"Downloading {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    print(f"Saved {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--skip-if-exists", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    xlsx_path = resolve_path(cfg["paths"]["nbs_xlsx"])
    processed_path = resolve_path(cfg["paths"]["nbs_processed"])
    download_file(cfg["nbs"]["download_url"], xlsx_path, skip_if_exists=args.skip_if_exists)

    df = build_nbs_crop_yield_table(xlsx_path)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"Processed NBS crop-yield table: {processed_path} ({df.shape[0]} rows)")


if __name__ == "__main__":
    main()
