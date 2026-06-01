# Reports

This directory is intentionally empty in the packaged project except for `.gitkeep` files.

Run the notebooks or scripts to generate:

- figures under `reports/figures/`
- metrics/prediction tables under `reports/tables/`
- model-card drafts under `reports/`

## Figure outputs

The notebooks automatically save each Matplotlib plot before displaying it. The output filenames use this convention:

```text
<notebook_name>_<figure_counter>_<figure_label>.png
```

For example, plots from `02_crop_yield_eda_by_zone_and_season.ipynb` will be saved in `reports/figures/` with filenames beginning with `02_crop_yield_eda_by_zone_and_season_`.

The goal is for you to generate the plots and result tables yourself, rather than receiving pre-computed outputs.
