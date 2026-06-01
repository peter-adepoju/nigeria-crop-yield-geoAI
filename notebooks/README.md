# Notebook Workflow

These notebooks are the main progressive implementation path for the project. They are intentionally **not pre-executed**: run them yourself to generate the processed files, metrics, plots, model artifacts, and report tables.

Recommended order:

1. `01_data_audit_and_nbs_parsing.ipynb` — inspect and parse the raw NBS/NASS Excel workbook.
2. `02_crop_yield_eda_by_zone_and_season.ipynb` — explore yield variation by crop, season, state, and zone.
3. `03_climate_data_download_and_feature_engineering.ipynb` — download or load climate data and create climate features.
4. `04_sentinel2_feature_engineering.ipynb` — compute vegetation-index features and prepare the Sentinel-2 feature table.
5. `05_modeling_dataset_and_leakage_control.ipynb` — build the final ML table and define honest features/splits.
6. `06_baseline_and_machine_learning_models.ipynb` — train baseline and classical ML models.
7. `07_hyperparameter_tuning_and_model_selection.ipynb` — tune tree-based models and save the best model.
8. `08_error_analysis_explainability_and_reporting.ipynb` — analyze errors, feature importance, spatial residuals, and generate report assets.

The notebooks generate outputs under `data/interim/`, `data/processed/`, `reports/`, and `models/` when executed.


## Plot-saving convention

Each notebook defines a small `save_figure(...)` helper in its setup cell. Before every `plt.show()` call, the notebook saves the active Matplotlib figure to `reports/figures/` using the pattern:

```text
<notebook_name>_<figure_counter>_<figure_label>.png
```

This means that when you run the notebooks progressively, the figures you see in the notebook are also written automatically to the project-level figures folder.
