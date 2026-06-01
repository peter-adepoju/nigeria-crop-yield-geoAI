from pathlib import Path

from nigeria_crop_yield.data.nbs_parser import build_nbs_crop_yield_table


def test_nbs_parser_finds_crop_rows():
    path = Path("data/raw/nbs/nass_report_tables_2022_2023.xlsx")
    df = build_nbs_crop_yield_table(path)
    assert not df.empty
    assert {"state", "crop", "yield_kg_ha", "season"}.issubset(df.columns)
    assert df["crop"].nunique() >= 10
    assert df["yield_kg_ha"].notna().sum() > 100
