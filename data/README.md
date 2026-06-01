# Data Directory

This project includes one real public Nigerian agricultural dataset:

```text
raw/nbs/nass_report_tables_2022_2023.xlsx
```

It is converted into:

```text
processed/nbs_crop_yield_state_zone_2022_2023.csv
```

Large optional downloads are not committed by default:

- `raw/climate/`: NiMet or NASA POWER daily climate data
- `raw/sentinel2/`: Sentinel-2 STAC metadata/raster outputs
- `interim/`: generated feature tables

Run `make quickstart` to reproduce the included processed table and train models.
