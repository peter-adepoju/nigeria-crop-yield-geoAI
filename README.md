# Nigeria Crop Yield GeoAI

An interactive GeoAI and machine-learning project for explaining and predicting crop yield across Nigerian agroecological zones.

This repository combines:

- NBS agricultural survey tables
- state metadata and agroecological labels
- climate covariates
- Sentinel-2 vegetation features
- leakage-aware regression models
- a paper-style Streamlit dashboard for storytelling and exploration

The goal is not just to predict yield. The goal is to show how a real end-to-end data science project can be structured: from raw public data, through feature engineering and model selection, to interpretable results and visual reporting.

## Project Story

Nigeria's crop yield varies by geography, rainfall, temperature, seasonality, and crop type. This project asks a simple question with a practical answer:

**Can we combine survey data, climate signals, and remote sensing to model crop yield across Nigerian states and agroecological zones?**

To answer it, the project:

1. Audits and parses NBS survey tables.
2. Builds a modeling table with yield, state, crop, and season information.
3. Adds climate and Sentinel-2 features where available.
4. Trains baseline and tree-based regression models.
5. Evaluates error patterns by crop, zone, and state.
6. Presents the results in an interactive report.

## Live Dashboard

The Streamlit app is designed like a research report:

- abstract
- methods
- results
- figure gallery
- interactive data explorer

Run it locally with:

```bash
streamlit run streamlit_app.py
```

## Repository Highlights

- reproducible scripts and notebook workflow
- clean Python package under `src/`
- lightweight tests
- model outputs and figures stored under `reports/`
- deployable Streamlit app at the repository root

## Key Results

The best tuned model in the included outputs is a tree-based regressor, with the following summary from `reports/tables/tuned_model_metrics_notebook07.csv`:

- Random Forest: RMSE 1433.59, MAE 808.71, R2 0.535
- Extra Trees: RMSE 1442.53, MAE 831.85, R2 0.529
- Gradient Boosting: RMSE 1538.65, MAE 901.20, R2 0.465

These results are explored further in the dashboard, including actual-vs-predicted plots and error breakdowns by crop and zone.

## Repository Structure

```text
crop-yield-nigeria-geoai/
|-- app/                      # Streamlit dashboard implementation
|-- configs/                  # YAML configuration
|-- data/                     # Raw, interim, and processed datasets
|-- docs/                     # Project design and data source notes
|-- notebooks/                # Notebook-driven workflow
|-- reports/                  # Figures, metrics, and analysis tables
|-- scripts/                  # Pipeline entrypoints
|-- src/nigeria_crop_yield/   # Python package
|-- tests/                    # Lightweight tests
`-- streamlit_app.py          # Streamlit Cloud entrypoint
```

## Reproduce Locally

### 1. Create an environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2. Run the pipeline

```bash
make quickstart
```

Or run the core scripts directly:

```bash
python scripts/00_download_nbs_tables.py --skip-if-exists
python scripts/03_build_features.py --mode quickstart
python scripts/04_train_models.py --config configs/config.yaml
python scripts/05_evaluate_and_explain.py --config configs/config.yaml
```

### 3. Launch the dashboard

```bash
streamlit run streamlit_app.py
```

## Data Notes

Included in the repository:

- `data/raw/nbs/nass_report_tables_2022_2023.xlsx`
- `data/processed/nbs_crop_yield_state_zone_2022_2023.csv`
- `data/processed/state_metadata.csv`

Optional reproducible sources:

- NASA POWER climate API
- Sentinel-2 imagery from Microsoft Planetary Computer
- user-supplied NiMet station observations

## What This Project Demonstrates

- geospatial feature engineering
- data cleaning and validation
- leakage-aware supervised learning
- model comparison and error analysis
- explainability-oriented reporting
- a polished, stakeholder-friendly dashboard

## Deployment

This repo is ready for Streamlit Community Cloud with `streamlit_app.py` at the repository root.

See `.streamlit/config.toml` and `.streamlit/secrets.toml.example` for deployment settings.

## GitHub Pages Website

A static, browser-first website lives in `docs/` and is ready for GitHub Pages.

To publish it:

1. Go to the repository settings on GitHub.
2. Open **Pages**.
3. Set the source to **Deploy from a branch**.
4. Select branch `main` and folder `/docs`.
5. Save the settings.

The homepage is `docs/index.html`, and the site includes an interactive metrics chart, a filterable prediction scatter plot, and a figure gallery.

## License

MIT License
