from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_actual_vs_predicted(predictions: pd.DataFrame, output_path: str | Path, target_col: str = "yield_kg_ha") -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best = predictions["model"].iloc[0]
    df = predictions[predictions["model"] == best]
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df[target_col], df["prediction"], alpha=0.75)
    lo = min(df[target_col].min(), df["prediction"].min())
    hi = max(df[target_col].max(), df["prediction"].max())
    ax.plot([lo, hi], [lo, hi], linestyle="--")
    ax.set_xlabel("Actual yield (kg/ha)")
    ax.set_ylabel("Predicted yield (kg/ha)")
    ax.set_title(f"Actual vs predicted yield: {best}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_residuals_by_zone(predictions: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best = predictions["model"].iloc[0]
    df = predictions[predictions["model"] == best].copy()
    summary = df.groupby("zone")["residual"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    summary.plot(kind="barh", ax=ax)
    ax.axvline(0, linestyle="--")
    ax.set_xlabel("Mean residual (actual - predicted, kg/ha)")
    ax.set_ylabel("Zone")
    ax.set_title(f"Mean residual by zone: {best}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
