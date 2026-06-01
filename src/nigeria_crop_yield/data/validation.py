from __future__ import annotations

import pandas as pd

REQUIRED_NBS_COLUMNS = {
    "season",
    "zone",
    "state",
    "crop",
    "planted_area_ha",
    "yield_kg_ha",
    "is_aggregate",
}


def validate_nbs_table(df: pd.DataFrame) -> None:
    missing = REQUIRED_NBS_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"NBS table is missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("NBS table is empty.")
    if df["yield_kg_ha"].notna().sum() == 0:
        raise ValueError("No usable yield values found in the NBS table.")


def validate_modeling_table(df: pd.DataFrame, target: str = "yield_kg_ha") -> None:
    if target not in df.columns:
        raise ValueError(f"Target column {target!r} was not found.")
    if df[target].notna().sum() < 20:
        raise ValueError("Modeling table has too few non-missing target values for training.")
