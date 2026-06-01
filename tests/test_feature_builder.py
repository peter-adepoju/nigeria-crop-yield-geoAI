import pandas as pd

from nigeria_crop_yield.features.build_features import load_base_nbs


def test_load_base_nbs_excludes_aggregates():
    df = load_base_nbs(
        "data/processed/nbs_crop_yield_state_zone_2022_2023.csv",
        "data/processed/state_metadata.csv",
        exclude_aggregates=True,
    )
    assert not df.empty
    assert not df["is_aggregate"].any()
    assert "agroecological_zone" in df.columns
    assert df["yield_kg_ha"].notna().all()
