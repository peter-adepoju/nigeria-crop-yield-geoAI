# Data Sources

## 1. NBS National Agricultural Sample Survey 2022/2023

Included file:

```text
data/raw/nbs/nass_report_tables_2022_2023.xlsx
```

Processed file:

```text
data/processed/nbs_crop_yield_state_zone_2022_2023.csv
```

The included XLSX is the public **NASS Report Tables** file from the NBS microdata catalog for the National Agricultural Sample Survey 2023. It contains crop production tables with state/zone-level planted area, harvested area, harvested quantity, and yield for major and minor seasons.

The processing script is:

```bash
python scripts/00_download_nbs_tables.py --skip-if-exists
```

## 2. NiMet Climate Variables

NiMet historical station observations are not bundled. Place authorized data at:

```text
data/raw/climate/nimet_daily_station_observations.csv
```

Expected schema:

```text
station_id,state,date,rainfall_mm,tmin_c,tmax_c,tmean_c,rh_percent,solar_radiation_mj_m2,wind_speed_m_s
```

The project then aggregates daily station data to state-level growing-season features.

## 3. NASA POWER Climate Fallback

Because NiMet historical station data may require formal request/access, this project includes a public NASA POWER fallback downloader:

```bash
python scripts/01_download_climate_nasa_power.py
```

The script downloads daily agroclimatology variables at Nigerian state centroids and saves:

```text
data/raw/climate/nasa_power_daily_state_centroids_2022_2023.csv
```

## 4. Sentinel-2 L2A Remote Sensing

The project includes a Sentinel-2 STAC query script:

```bash
python scripts/02_download_sentinel2_planetary_computer.py --dry-run
```

A real research-grade workflow should use crop masks or plot polygons instead of state centroids. The script is intentionally conservative because downloading rasters for all states and months can become large.

Recommended feature table schema:

```text
state,crop,season,ndvi_mean,ndvi_std,evi_mean,ndwi_mean,savi_mean,cloud_cover_mean,n_observations
```

Save it as:

```text
data/interim/sentinel2_monthly_indices_state_crop_2022_2023.csv
```
