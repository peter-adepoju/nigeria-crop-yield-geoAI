# Crop Yield Prediction Across Nigerian Agroecological Zones

**A portfolio-grade machine-learning project that combines Nigerian agricultural survey tables, climate covariates, and Sentinel-2 remote-sensing features to predict crop yield at state × crop × season level.**

This repository is designed like a junior machine-learning engineer project: it has a reproducible data pipeline, clean project structure, modular Python package, model training, evaluation, explainability hooks, documentation, tests, and a small dashboard scaffold.

> **Important data note**: The repository includes a real public Nigerian dataset: the National Bureau of Statistics (NBS) National Agricultural Sample Survey (NASS) 2022/2023 report tables. The NASS household-level microdata and NiMet historical station observations may require portal access, login, or formal data request. This project therefore includes adapters for user-supplied NBS/NiMet files and public API downloaders for NASA POWER climate data and Sentinel-2 L2A imagery.

---

## 1. Problem Statement

Nigeria's crop yields vary strongly across agroecological zones because of differences in rainfall, temperature, soil-moisture stress, crop choice, planting season, and management intensity. The goal is to build a reproducible machine-learning pipeline that predicts crop yield, measured in **kg/ha**, from:

1. **NBS agricultural survey data**: state-level NASS 2022/2023 crop production tables.
2. **Agroecological metadata**: state centroid and coarse agroecological-zone labels.
3. **Climate variables**: rainfall, temperature, humidity, heat stress, and growing-degree proxies from either NiMet CSV files or NASA POWER API fallback.
4. **Sentinel-2 satellite features**: NDVI, EVI, NDWI, SAVI and cloud-filtered monthly summaries from Microsoft Planetary Computer Sentinel-2 L2A.

The project can run in two modes:

- **Quickstart mode**: uses the included NBS dataset and state metadata only.
- **Full geospatial mode**: downloads climate and Sentinel-2 features, then joins them to the NBS crop-yield table.

---

## 2. Repository Structure

```text
crop-yield-nigeria-geoai/
├── app/                         # Streamlit dashboard scaffold
├── configs/                     # YAML configuration
├── data/
│   ├── raw/nbs/                 # Included real NBS NASS XLSX
│   ├── raw/climate/             # Downloaded NiMet/NASA climate files
│   ├── raw/sentinel2/           # Downloaded Sentinel-2/STAC outputs
│   ├── interim/                 # Intermediate feature tables
│   └── processed/               # Clean modeling-ready tables
├── docs/                        # Design notes, data sources, model-card template
├── notebooks/                   # Progressive implementation notebooks
├── reports/                     # Tables, figures, model metrics
├── scripts/                     # Executable pipeline scripts
├── src/nigeria_crop_yield/      # Python package
├── tests/                       # Lightweight tests
├── Makefile
├── pyproject.toml
└── requirements.txt
```

---


## 3. Notebook-First Workflow

The main implementation path is in `notebooks/`. These notebooks are intentionally not pre-executed; run them yourself to generate the processed files, figures, metrics, and model artifacts.

Recommended order:

1. `01_data_audit_and_nbs_parsing.ipynb`
2. `02_crop_yield_eda_by_zone_and_season.ipynb`
3. `03_climate_data_download_and_feature_engineering.ipynb`
4. `04_sentinel2_feature_engineering.ipynb`
5. `05_modeling_dataset_and_leakage_control.ipynb`
6. `06_baseline_and_machine_learning_models.ipynb`
7. `07_hyperparameter_tuning_and_model_selection.ipynb`
8. `08_error_analysis_explainability_and_reporting.ipynb`

Outputs are written under `data/interim/`, `data/processed/`, `reports/`, and `models/` only when you execute the notebooks or scripts.

Every notebook saves each Matplotlib plot to `reports/figures/` before displaying it, using notebook-specific filenames such as `02_crop_yield_eda_by_zone_and_season_01_figure_01.png`.

## 4. Quickstart

### 4.1 Create an environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
pip install -e .
```

### 4.2 Run the quick pipeline

```bash
make quickstart
```

This will:

1. Rebuild the processed NBS crop-yield table from the included XLSX.
2. Build the quick modeling table.
3. Train several regression models.
4. Save metrics, predictions, model artifact, and figures under `reports/` and `models/`.

Equivalent Python commands:

```bash
python scripts/00_download_nbs_tables.py --skip-if-exists
python scripts/03_build_features.py --mode quickstart
python scripts/04_train_models.py --config configs/config.yaml
python scripts/05_evaluate_and_explain.py --config configs/config.yaml
```

---

## 5. Full Pipeline With Climate and Sentinel-2

```bash
make full
```

The full pipeline adds:

- NASA POWER daily climate variables at state centroids.
- Sentinel-2 L2A STAC queries and vegetation-index extraction.

For a stronger research-grade version, request NiMet station data and place it here:

```text
data/raw/climate/nimet_daily_station_observations.csv
```

Expected NiMet-compatible schema:

```text
station_id,state,date,rainfall_mm,tmin_c,tmax_c,tmean_c,rh_percent,solar_radiation_mj_m2,wind_speed_m_s
```

Then run:

```bash
python scripts/03_build_features.py --mode full --climate-source nimet
python scripts/04_train_models.py --config configs/config.yaml
```

---

## 6. Modeling Approach

The project treats yield prediction as a supervised regression problem:

\[
y_{s,c,t} = f(X_{s,c,t}) + \epsilon,
\]

where:

- \(s\) = state or agroecological zone,
- \(c\) = crop,
- \(t\) = agricultural season,
- \(y\) = yield in kg/ha,
- \(X\) = survey, climate, and remote-sensing features.

Models included:

- Dummy mean baseline
- Ridge regression
- Random Forest
- Extra Trees
- Gradient Boosting
- MLP regressor

Evaluation metrics:

- MAE
- RMSE
- \(R^2\)
- MAPE
- Grouped validation by state where possible
- Crop-wise and agroecological-zone-wise residual analysis

Leakage prevention:

- The default model **does not use harvested quantity** or **harvested area** as predictors because reported yield is derived from production divided by harvested area.
- Yield target is kept separate from feature engineering.
- Aggregate rows are excluded from model training by default.

---

## 7. Data Sources

### Included in this repository

- `data/raw/nbs/nass_report_tables_2022_2023.xlsx`
- `data/processed/nbs_crop_yield_state_zone_2022_2023.csv`
- `data/processed/state_metadata.csv`

### Optional/reproducible sources

- NBS NASS 2022/2023 report tables: `scripts/00_download_nbs_tables.py`
- NASA POWER climate API: `scripts/01_download_climate_nasa_power.py`
- Sentinel-2 L2A via Microsoft Planetary Computer STAC: `scripts/02_download_sentinel2_planetary_computer.py`
- User-supplied NiMet historical station CSV: `data/raw/climate/nimet_daily_station_observations.csv`

---

## 8. Suggested GitHub Project Story

**Title:** Crop Yield Prediction Across Nigerian Agroecological Zones Using Survey Data, Climate Covariates, and Sentinel-2 Remote Sensing

**One-sentence pitch:** I built an end-to-end GeoAI/ML pipeline that predicts Nigerian crop yields across states and agroecological zones by combining NBS NASS agricultural survey data with climate and Sentinel-2 vegetation-index features.

**What this demonstrates to employers:**

- Real-world data sourcing and documentation
- Geospatial and tabular feature engineering
- Leakage-aware supervised learning
- Robust evaluation by crop, state, and agroecological zone
- Clean repository structure, tests, config-driven scripts, and reproducibility
- Practical understanding of agricultural ML and remote sensing

---

## 9. Limitations

1. The included NASS tables are state-level aggregates, not household/plot-level microdata.
2. The agroecological labels in `state_metadata.csv` are coarse state-level approximations, not pixel-level AEZ maps.
3. NiMet station observations are supported but not bundled because historical data access may require a formal request.
4. Sentinel-2 files are not bundled because imagery is too large for GitHub; the project includes download/extraction scripts instead.

---

## 9. Next Improvements

- Replace state centroids with true plot coordinates from authorized NBS/LSMS microdata.
- Use crop calendars to align Sentinel-2 observations with crop-specific growth stages.
- Add spatial cross-validation by agroecological zone.
- Add uncertainty quantification using conformal prediction or quantile regression.
- Deploy an interactive dashboard for policy-facing yield-risk visualization.
