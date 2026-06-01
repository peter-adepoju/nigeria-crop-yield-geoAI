from __future__ import annotations

from pathlib import Path

import pandas as pd


def vegetation_indices(red, green, blue, nir, swir=None):
    """Compute common Sentinel-2 vegetation indices from arrays or scalars.

    Sentinel-2 L2A common band mapping:
    - B02: blue
    - B03: green
    - B04: red
    - B08: near infrared
    - B11/B12: short-wave infrared
    """
    ndvi = (nir - red) / (nir + red)
    evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
    ndwi = (green - nir) / (green + nir)
    savi = 1.5 * (nir - red) / (nir + red + 0.5)
    out = {"ndvi": ndvi, "evi": evi, "ndwi": ndwi, "savi": savi}
    if swir is not None:
        out["ndmi"] = (nir - swir) / (nir + swir)
    return out


def sentinel_feature_schema() -> list[str]:
    return [
        "state",
        "crop",
        "season",
        "ndvi_mean",
        "ndvi_std",
        "evi_mean",
        "ndwi_mean",
        "savi_mean",
        "cloud_cover_mean",
        "n_observations",
    ]


def load_sentinel_features(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = set(sentinel_feature_schema()).difference(df.columns)
    if missing:
        raise ValueError(f"Sentinel-2 feature table is missing columns: {sorted(missing)}")
    return df
