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

from nigeria_crop_yield.models.evaluate import crop_level_metrics, residual_summary
from nigeria_crop_yield.settings import load_config, resolve_path
from nigeria_crop_yield.visualization.plots import plot_actual_vs_predicted, plot_residuals_by_zone


def main() -> None:
    parser = argparse.ArgumentParser(description="Create evaluation tables and plots.")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    report_dir = resolve_path(cfg["paths"]["report_dir"])
    pred_path = report_dir / "tables/model_predictions.csv"
    predictions = pd.read_csv(pred_path)

    # Keep only the best model for plots. The best model is first in the metrics table.
    metrics = pd.read_csv(report_dir / "tables/model_metrics.csv")
    best_model = metrics.iloc[0]["model"]
    best_predictions = predictions[predictions["model"] == best_model].copy()

    residual_summary(best_predictions).to_csv(report_dir / "tables/residual_summary_by_zone_crop.csv", index=False)
    crop_level_metrics(predictions).to_csv(report_dir / "tables/crop_level_metrics.csv", index=False)
    plot_actual_vs_predicted(best_predictions, report_dir / "figures/actual_vs_predicted.png")
    plot_residuals_by_zone(best_predictions, report_dir / "figures/residuals_by_zone.png")
    print(f"Saved evaluation artifacts under {report_dir}")


if __name__ == "__main__":
    main()
