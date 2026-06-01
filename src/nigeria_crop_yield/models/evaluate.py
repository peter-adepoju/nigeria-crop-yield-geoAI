from __future__ import annotations

import pandas as pd


def residual_summary(predictions: pd.DataFrame, target_col: str = "yield_kg_ha") -> pd.DataFrame:
    best_model = predictions["model"].iloc[0] if predictions["model"].nunique() == 1 else None
    df = predictions if best_model is None else predictions[predictions["model"] == best_model]
    return (
        df.groupby(["zone", "crop"], dropna=False)
        .agg(
            n=(target_col, "size"),
            mean_actual=(target_col, "mean"),
            mean_prediction=("prediction", "mean"),
            mean_residual=("residual", "mean"),
            mean_abs_residual=("residual", lambda x: x.abs().mean()),
        )
        .reset_index()
        .sort_values("mean_abs_residual", ascending=False)
    )


def crop_level_metrics(predictions: pd.DataFrame, target_col: str = "yield_kg_ha") -> pd.DataFrame:
    rows = []
    for (model, crop), g in predictions.groupby(["model", "crop"]):
        if len(g) < 2:
            continue
        err = g[target_col] - g["prediction"]
        rows.append(
            {
                "model": model,
                "crop": crop,
                "n": len(g),
                "mae": err.abs().mean(),
                "bias": err.mean(),
                "rmse": (err.pow(2).mean()) ** 0.5,
            }
        )
    return pd.DataFrame(rows).sort_values(["model", "mae"])
