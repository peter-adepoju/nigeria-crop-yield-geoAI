from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests


@dataclass(frozen=True)
class PowerRequest:
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    parameters: tuple[str, ...]


def fetch_nasa_power_daily(req: PowerRequest) -> pd.DataFrame:
    """Fetch daily NASA POWER agroclimatology variables for one point.

    Dates should be YYYY-MM-DD strings. NASA POWER expects YYYYMMDD in the URL.
    """
    start = req.start_date.replace("-", "")
    end = req.end_date.replace("-", "")
    params = ",".join(req.parameters)
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={params}&community=AG&longitude={req.longitude:.4f}"
        f"&latitude={req.latitude:.4f}&start={start}&end={end}&format=JSON"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.json()
    data = payload["properties"]["parameter"]
    frame = pd.DataFrame(data)
    frame.index = pd.to_datetime(frame.index, format="%Y%m%d")
    frame.index.name = "date"
    frame = frame.reset_index()
    return frame


def download_power_for_states(
    state_metadata: pd.DataFrame,
    start_date: str,
    end_date: str,
    parameters: list[str],
    output_path: str | Path,
) -> pd.DataFrame:
    frames = []
    for row in state_metadata.itertuples(index=False):
        req = PowerRequest(
            latitude=float(row.latitude),
            longitude=float(row.longitude),
            start_date=start_date,
            end_date=end_date,
            parameters=tuple(parameters),
        )
        df = fetch_nasa_power_daily(req)
        df.insert(0, "state", row.state)
        df.insert(1, "latitude", row.latitude)
        df.insert(2, "longitude", row.longitude)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return out


def summarize_daily_climate(daily: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily climate to state-level growing-season features."""
    df = daily.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Rename common NASA POWER parameters to project names.
    rename = {
        "PRECTOTCORR": "rainfall_mm",
        "T2M": "tmean_c",
        "T2M_MAX": "tmax_c",
        "T2M_MIN": "tmin_c",
        "RH2M": "rh_percent",
        "WS2M": "wind_speed_m_s",
        "ALLSKY_SFC_SW_DWN": "solar_radiation_kwh_m2_day",
    }
    df = df.rename(columns=rename)
    for col in rename.values():
        if col not in df.columns:
            df[col] = pd.NA

    df["gdd"] = (df["tmean_c"] - 10.0).clip(lower=0)
    df["heat_stress_day"] = (df["tmax_c"] >= 35.0).astype(float)

    agg = (
        df.groupby("state", as_index=False)
        .agg(
            total_rainfall_mm=("rainfall_mm", "sum"),
            mean_tmean_c=("tmean_c", "mean"),
            mean_tmax_c=("tmax_c", "mean"),
            mean_tmin_c=("tmin_c", "mean"),
            mean_rh_percent=("rh_percent", "mean"),
            mean_wind_speed_m_s=("wind_speed_m_s", "mean"),
            growing_degree_days=("gdd", "sum"),
            heat_stress_days=("heat_stress_day", "sum"),
            mean_solar_radiation_kwh_m2_day=("solar_radiation_kwh_m2_day", "mean"),
            total_solar_radiation_kwh_m2=("solar_radiation_kwh_m2_day", "sum"),
        )
        .reset_index(drop=True)
    )
    return agg


def load_nimet_csv(path: str | Path) -> pd.DataFrame:
    """Load user-supplied NiMet daily station observations.

    Expected columns:
    station_id,state,date,rainfall_mm,tmin_c,tmax_c,tmean_c,rh_percent,solar_radiation_mj_m2,wind_speed_m_s
    """
    df = pd.read_csv(path)
    required = {"state", "date", "rainfall_mm", "tmean_c"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"NiMet CSV missing required columns: {sorted(missing)}")
    return df
