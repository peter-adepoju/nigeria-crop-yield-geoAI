from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from nigeria_crop_yield.data.climate import load_nimet_csv, summarize_daily_climate
from nigeria_crop_yield.data.validation import validate_modeling_table, validate_nbs_table


def load_base_nbs(nbs_path: str | Path, state_metadata_path: str | Path, exclude_aggregates: bool = True) -> pd.DataFrame:
    nbs = pd.read_csv(nbs_path)
    validate_nbs_table(nbs)
    if exclude_aggregates and "is_aggregate" in nbs.columns:
        nbs = nbs[~nbs["is_aggregate"].astype(bool)].copy()
    nbs = nbs[nbs["yield_kg_ha"].notna()].copy()
    state_meta = pd.read_csv(state_metadata_path)
    out = nbs.merge(state_meta, on="state", how="left")
    out["log_planted_area_ha"] = np.log(out["planted_area_ha"].clip(lower=0) + 1)
    return out


def add_climate_features(df: pd.DataFrame, climate_path: str | Path, source: str = "nasa_power") -> pd.DataFrame:
    if not Path(climate_path).exists():
        return df
    daily = load_nimet_csv(climate_path) if source == "nimet" else pd.read_csv(climate_path)
    climate = summarize_daily_climate(daily)
    return df.merge(climate, on="state", how="left")


def add_sentinel_features(df: pd.DataFrame, sentinel_path: str | Path) -> pd.DataFrame:
    if not Path(sentinel_path).exists():
        return df
    sentinel = pd.read_csv(sentinel_path)
    join_cols = [c for c in ["state", "crop", "season"] if c in sentinel.columns and c in df.columns]
    if not join_cols:
        raise ValueError("Sentinel feature table must share at least one join key with modeling data.")
    return df.merge(sentinel, on=join_cols, how="left")


def build_modeling_dataset(
    nbs_path: str | Path,
    state_metadata_path: str | Path,
    output_path: str | Path,
    climate_path: str | Path | None = None,
    sentinel_path: str | Path | None = None,
    climate_source: str = "nasa_power",
    exclude_aggregates: bool = True,
) -> pd.DataFrame:
    df = load_base_nbs(nbs_path, state_metadata_path, exclude_aggregates=exclude_aggregates)
    if climate_path is not None:
        df = add_climate_features(df, climate_path, source=climate_source)
    if sentinel_path is not None:
        df = add_sentinel_features(df, sentinel_path)
    validate_modeling_table(df)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
