from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


MISSING_MARKERS = {"(S)", "-", "", ".."}


def _clean_num(x: object) -> float:
    if pd.isna(x):
        return float("nan")
    if isinstance(x, str):
        s = x.strip().replace(",", "")
        if s in MISSING_MARKERS:
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return float("nan")
    try:
        return float(x)  # type: ignore[arg-type]
    except Exception:
        return float("nan")


def _metric_name(raw: object) -> str:
    s = str(raw).lower().strip()
    if "household" in s:
        return "households_reporting_000"
    if "planted area" in s:
        return "planted_area_ha"
    if "harvested area" in s:
        return "harvested_area_ha"
    if "harvested quantity" in s:
        return "harvested_quantity_kg"
    if "yield" in s:
        return "yield_kg_ha"
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def _crop_name(raw: object) -> str:
    s = str(raw).split(":", 1)[-1]
    s = re.sub(r"\s+", " ", s).strip().upper()
    s = re.sub(r"\s*\([0-9]+\)$", "", s).strip()
    s = s.replace("CHILLIPEPPER", "CHILLI PEPPER")
    s = s.replace("OIL PALM TREE", "OIL PALM")
    return s


def parse_crop_production_sheet(xlsx_path: str | Path, sheet_name: str, season: str) -> pd.DataFrame:
    """Parse the NASS crop production sheet into a tidy long table.

    The NASS report tables use repeated Excel blocks like `CROP 1: MAIZE`,
    followed by the same five metrics. This function detects each header block
    and returns one row per state/zone × crop × season.
    """
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    records: list[dict[str, object]] = []

    header_rows = [
        i
        for i, row in df.iterrows()
        if str(row.iloc[0]).strip() == "Zone" and str(row.iloc[1]).strip() == "State"
    ]

    for header_row in header_rows:
        crop_row = header_row - 1

        table_title = ""
        for j in range(header_row - 1, max(-1, header_row - 12), -1):
            value = df.iloc[j, 0]
            if isinstance(value, str) and value.strip().startswith("Table"):
                table_title = value.strip()
                break

        starts = [
            c
            for c, value in enumerate(df.iloc[crop_row])
            if isinstance(value, str) and "CROP" in value.upper()
        ]
        starts.append(df.shape[1])

        end_row = header_row + 1
        while end_row < len(df):
            value = df.iloc[end_row, 0]
            if isinstance(value, str) and value.strip().startswith("Source:"):
                break
            end_row += 1

        for k in range(len(starts) - 1):
            start_col, end_col = starts[k], starts[k + 1]
            crop = _crop_name(df.iloc[crop_row, start_col])
            metric_cols = [
                (c, _metric_name(df.iloc[header_row, c]))
                for c in range(start_col, end_col)
                if pd.notna(df.iloc[header_row, c])
            ]
            for r in range(header_row + 1, end_row):
                zone, state = df.iloc[r, 0], df.iloc[r, 1]
                if pd.isna(zone) or pd.isna(state):
                    continue
                state_str = str(state).strip().title().replace("Fct", "FCT")
                zone_str = str(zone).strip()
                record: dict[str, object] = {
                    "season": season,
                    "zone": zone_str,
                    "state": state_str,
                    "crop": crop,
                    "source_sheet": sheet_name,
                    "source_table": table_title,
                    "is_aggregate": state_str.lower() in {"zone total", "total"}
                    or zone_str.lower() == "nigeria",
                }
                for col, metric in metric_cols:
                    record[metric] = _clean_num(df.iloc[r, col])
                records.append(record)

    return pd.DataFrame.from_records(records)


def build_nbs_crop_yield_table(xlsx_path: str | Path) -> pd.DataFrame:
    """Build the full NASS crop yield table from major and minor season sheets."""
    frames = [
        parse_crop_production_sheet(xlsx_path, "Crop Production2_major season", "major"),
        parse_crop_production_sheet(xlsx_path, "Crop Production2_minor season", "minor"),
    ]
    out = pd.concat(frames, ignore_index=True)
    # Put core columns first for readability.
    core = [
        "season",
        "zone",
        "state",
        "crop",
        "households_reporting_000",
        "planted_area_ha",
        "harvested_area_ha",
        "harvested_quantity_kg",
        "yield_kg_ha",
        "is_aggregate",
        "source_sheet",
        "source_table",
    ]
    return out[[c for c in core if c in out.columns]]
