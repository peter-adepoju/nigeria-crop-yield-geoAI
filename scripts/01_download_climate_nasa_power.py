from __future__ import annotations

from pathlib import Path

# Allow scripts to run directly from the repository root without requiring pip install -e . first.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import argparse

import pandas as pd

from nigeria_crop_yield.data.climate import download_power_for_states
from nigeria_crop_yield.settings import load_config, resolve_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download NASA POWER daily climate variables for Nigerian state centroids.")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    state_meta = pd.read_csv(resolve_path(cfg["paths"]["state_metadata"]))
    out = download_power_for_states(
        state_metadata=state_meta,
        start_date=cfg["climate"]["start_date"],
        end_date=cfg["climate"]["end_date"],
        parameters=cfg["climate"]["parameters"],
        output_path=resolve_path(cfg["paths"]["climate_daily"]),
    )
    print(f"Saved climate table with shape {out.shape} to {cfg['paths']['climate_daily']}")


if __name__ == "__main__":
    main()
