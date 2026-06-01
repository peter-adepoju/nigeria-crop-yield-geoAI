# Project Design

## Objective

Predict Nigerian crop yield across states, seasons, crops, and coarse agroecological zones using a fusion of agricultural survey data, climate covariates, and Sentinel-2 vegetation indices.

## Why this is a strong ML engineering project

This project is not just a Kaggle-style notebook. It demonstrates a professional workflow:

1. **Data acquisition**: downloads public NBS tables and supports climate/satellite APIs.
2. **Data parsing**: converts complex Excel survey tables into tidy modeling data.
3. **Feature engineering**: creates survey, agroecological, climate, and vegetation-index predictors.
4. **Leakage control**: excludes production and harvested-area variables that define the target.
5. **Model comparison**: trains interpretable and nonlinear baselines.
6. **Evaluation**: reports error by crop and zone, not just one global metric.
7. **Reproducibility**: config-driven scripts, tests, Makefile, and documented data sources.

## Target

The target is:

```text
yield_kg_ha
```

This is the reported crop yield in kg/ha from the NASS report tables.

## Features

### Survey features

- crop
- season
- state
- geopolitical zone
- planted area
- number of households reporting crop

### Agroecological features

- coarse state-level agroecological zone
- latitude and longitude of state centroid

### Climate features

- total rainfall
- mean/min/max temperature
- relative humidity
- growing degree days
- heat-stress days

### Sentinel-2 features

- NDVI mean and variability
- EVI mean
- NDWI mean
- SAVI mean
- cloud-cover statistics

## Validation strategy

The default split is a **grouped split by state**. This gives a more realistic estimate of how well the model generalizes to unseen states, although a single-year state-level aggregate dataset remains small.

## Expected limitations

- A true operational system needs plot-level crop labels and crop calendars.
- State-level aggregation hides within-state variation.
- Satellite features should be computed over actual crop areas, not state centroids.
- A small number of rows limits neural-network usefulness.

## High-impact extension

The best upgrade is to obtain authorized plot-level NBS/LSMS microdata with coordinates and join each plot to Sentinel-2 time-series features over the actual growing period. That would turn this into a much stronger GeoAI project suitable for publication or a serious job portfolio.
