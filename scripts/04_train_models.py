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

from nigeria_crop_yield.models.train import train_and_select
from nigeria_crop_yield.settings import load_config, resolve_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Train crop yield prediction models.")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    df = pd.read_csv(resolve_path(cfg["paths"]["modeling_dataset"]))
    result = train_and_select(df, cfg, output_dir=resolve_path(cfg["paths"]["model_dir"]))

    report_dir = resolve_path(cfg["paths"]["report_dir"])
    (report_dir / "tables").mkdir(parents=True, exist_ok=True)
    result.metrics.to_csv(report_dir / "tables/model_metrics.csv", index=False)
    result.predictions.to_csv(report_dir / "tables/model_predictions.csv", index=False)

    print("Model metrics:")
    print(result.metrics.to_string(index=False))
    print(f"Best model: {result.best_model_name}")


if __name__ == "__main__":
    main()
