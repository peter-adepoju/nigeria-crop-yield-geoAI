# Model Card: Nigerian Crop Yield Predictor

## Model Details

- Project: Crop Yield Prediction Across Nigerian Agroecological Zones
- Target: `yield_kg_ha`
- Model type: Regression
- Best model: To be filled after training
- Training data: NBS NASS 2022/2023 state-level crop production tables plus optional climate/satellite features

## Intended Use

This model is intended for educational, portfolio, and exploratory policy-analysis purposes. It should not be used as the sole basis for food-security decisions, insurance pricing, or farmer-level interventions.

## Training Data

The quickstart model uses NASS report-table aggregates at state × crop × season level. Optional full-mode features can include climate covariates and Sentinel-2 vegetation indices.

## Evaluation

Primary metrics:

- RMSE
- MAE
- R²
- MAPE

Secondary diagnostics:

- Crop-wise error
- Zone-wise residual bias
- Actual-vs-predicted plots

## Ethical and Practical Considerations

- State-level predictions can mask local crop failure or localized high productivity.
- Climate and satellite features should be aligned with crop calendars before operational use.
- Predictions should be communicated with uncertainty intervals.
- Data gaps and missing values should be reported transparently.
