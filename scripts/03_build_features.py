from __future__ import annotations

from pathlib import Path

# Allow scripts to run directly from the repository root without requiring pip install -e . first.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import argparse

from nigeria_crop_yield.features.build_features import build_modeling_dataset
from nigeria_crop_yield.settings import load_config, resolve_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build modeling dataset from NBS, climate, and Sentinel-2 features.")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--mode", choices=["quickstart", "full"], default="quickstart")
    parser.add_argument("--climate-source", choices=["nasa_power", "nimet"], default="nasa_power")
    args = parser.parse_args()

    cfg = load_config(args.config)
    climate_path = resolve_path(cfg["paths"]["climate_daily"]) if args.mode == "full" else None
    sentinel_path = resolve_path(cfg["paths"]["sentinel_features"]) if args.mode == "full" else None

    df = build_modeling_dataset(
        nbs_path=resolve_path(cfg["paths"]["nbs_processed"]),
        state_metadata_path=resolve_path(cfg["paths"]["state_metadata"]),
        output_path=resolve_path(cfg["paths"]["modeling_dataset"]),
        climate_path=climate_path,
        sentinel_path=sentinel_path,
        climate_source=args.climate_source,
        exclude_aggregates=cfg["nbs"].get("exclude_aggregate_rows", True),
    )
    print(f"Saved modeling dataset: {cfg['paths']['modeling_dataset']} shape={df.shape}")


if __name__ == "__main__":
    main()
