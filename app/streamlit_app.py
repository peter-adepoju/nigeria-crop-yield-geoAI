from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from PIL import Image


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATA_PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_TABLES_DIR = ROOT / "reports" / "tables"
REPORTS_FIGURES_DIR = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"


# ---------------------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Nigeria Crop Yield GeoAI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .hero {
        background: linear-gradient(135deg, #102a43 0%, #1d4ed8 45%, #0f766e 100%);
        color: white;
        border-radius: 24px;
        padding: 28px 28px 22px 28px;
        box-shadow: 0 18px 50px rgba(0,0,0,0.18);
        margin-bottom: 1.25rem;
    }
    .hero h1 {font-size: 2.4rem; margin-bottom: 0.15rem;}
    .hero p {font-size: 1.02rem; line-height: 1.6; max-width: 980px;}
    .pill {
        display: inline-block;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        margin: 0.2rem 0.35rem 0 0;
        font-size: 0.84rem;
    }
    .section-card {
        background: white;
        border: 1px solid rgba(15,23,42,0.08);
        border-radius: 18px;
        padding: 1rem 1rem 0.75rem 1rem;
        box-shadow: 0 6px 18px rgba(15,23,42,0.04);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Crop Yield Prediction Across Nigerian Agroecological Zones</h1>
      <p>
        A data-science story in paper format: from Nigerian agricultural survey tables,
        through geospatial feature engineering, to model comparison and error analysis.
        The site is designed to be interactive enough for a project showcase, yet structured
        like a concise research report.
      </p>
      <div>
        <span class="pill">NBS NASS 2022/2023</span>
        <span class="pill">Climate covariates</span>
        <span class="pill">Sentinel-2 GeoAI</span>
        <span class="pill">Leakage-aware ML</span>
        <span class="pill">Explainability</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
    <p>
    This dashboard surfaces the model leaderboard, prediction results, residual
    errors, and the final modeling table. It also walks through the project
    narrative so a visitor can understand the problem, the data, the design
    choices, and the outcome without opening the notebooks.
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def first_existing_path(paths: list[Path]) -> Optional[Path]:
    """
    Return the first existing file path from a list of candidate paths.
    """
    for path in paths:
        if path.exists():
            return path
    return None


def load_csv(path: Path, label: str) -> pd.DataFrame:
    """
    Load a CSV file with a clear Streamlit error message if loading fails.
    """
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not load {label}: `{path}`")
        st.exception(exc)
        st.stop()


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to make the dashboard more robust.

    This does not change the meaning of columns. It only makes names easier
    to work with by removing spaces and making them lowercase.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """
    Find the first matching column in a dataframe from a list of candidates.
    """
    for col in candidates:
        if col in df.columns:
            return col
    return None


def show_file_status(label: str, path: Optional[Path]) -> None:
    """
    Display whether a required or optional file was found.
    """
    if path is None:
        st.error(f"{label}: not found")
    else:
        st.success(f"{label}: found")
        st.code(str(path.relative_to(ROOT)))


# ---------------------------------------------------------------------
# Candidate result files
# ---------------------------------------------------------------------

metrics_candidates = [
    REPORTS_TABLES_DIR / "tuned_model_metrics_notebook07.csv",
    REPORTS_TABLES_DIR / "model_metrics_notebook06.csv",
    REPORTS_TABLES_DIR / "model_metrics.csv",
]

predictions_candidates = [
    REPORTS_TABLES_DIR / "tuned_model_predictions_notebook07.csv",
    REPORTS_TABLES_DIR / "model_predictions_notebook06.csv",
    REPORTS_TABLES_DIR / "model_predictions.csv",
]

modeling_candidates = [
    DATA_PROCESSED_DIR / "modeling_dataset.csv",
    DATA_PROCESSED_DIR / "modeling_dataset_notebook05.csv",
]

metrics_path = first_existing_path(metrics_candidates)
preds_path = first_existing_path(predictions_candidates)
modeling_path = first_existing_path(modeling_candidates)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------

st.sidebar.title("Project dashboard")
st.sidebar.caption("Interact with the report like a guided notebook.")

st.sidebar.markdown("### Detected files")

if metrics_path is not None:
    st.sidebar.success(f"Metrics: {metrics_path.name}")
else:
    st.sidebar.error("Metrics: not found")

if preds_path is not None:
    st.sidebar.success(f"Predictions: {preds_path.name}")
else:
    st.sidebar.error("Predictions: not found")

if modeling_path is not None:
    st.sidebar.success(f"Modeling data: {modeling_path.name}")
else:
    st.sidebar.warning("Modeling data: not found")

st.sidebar.markdown("---")

show_debug = st.sidebar.checkbox("Show debug information", value=False)

image_paths = sorted(REPORTS_FIGURES_DIR.glob("*.png"))
figure_map = {path.stem: path for path in image_paths}


# ---------------------------------------------------------------------
# Required file check
# ---------------------------------------------------------------------

if metrics_path is None or preds_path is None:
    st.warning(
        "The dashboard cannot run yet because the required model output files "
        "were not found using the expected filenames."
    )

    st.markdown("### Expected metrics files")

    for path in metrics_candidates:
        status = "FOUND" if path.exists() else "missing"
        st.code(f"{status}: {path.relative_to(ROOT)}")

    st.markdown("### Expected prediction files")

    for path in predictions_candidates:
        status = "FOUND" if path.exists() else "missing"
        st.code(f"{status}: {path.relative_to(ROOT)}")

    st.markdown(
        """
        To fix this, run the modeling notebooks first, especially:

        1. `06_baseline_and_machine_learning_models.ipynb`
        2. `07_hyperparameter_tuning_and_model_selection.ipynb`

        Alternatively, rename or copy your result files to one of the expected names.
        For example, from the VS Code terminal:

        ```powershell
        Copy-Item "reports\\tables\\tuned_model_metrics_notebook07.csv" "reports\\tables\\model_metrics.csv" -Force
        Copy-Item "reports\\tables\\tuned_model_predictions_notebook07.csv" "reports\\tables\\model_predictions.csv" -Force
        ```
        """
    )

    st.stop()


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

metrics = load_csv(metrics_path, "model metrics")
preds = load_csv(preds_path, "model predictions")

metrics = normalize_column_names(metrics)
preds = normalize_column_names(preds)

if modeling_path is not None:
    modeling = load_csv(modeling_path, "modeling dataset")
    modeling = normalize_column_names(modeling)
else:
    modeling = pd.DataFrame()


# ---------------------------------------------------------------------
# Debug information
# ---------------------------------------------------------------------

if show_debug:
    st.subheader("Debug information")

    st.markdown("#### Project root")
    st.code(str(ROOT))

    st.markdown("#### Files being used")
    st.code(f"Metrics: {metrics_path.relative_to(ROOT)}")
    st.code(f"Predictions: {preds_path.relative_to(ROOT)}")

    if modeling_path is not None:
        st.code(f"Modeling dataset: {modeling_path.relative_to(ROOT)}")
    else:
        st.code("Modeling dataset: not found")

    st.markdown("#### Metrics columns")
    st.write(metrics.columns.tolist())

    st.markdown("#### Predictions columns")
    st.write(preds.columns.tolist())

    if not modeling.empty:
        st.markdown("#### Modeling dataset columns")
        st.write(modeling.columns.tolist())


story_tabs = st.tabs(["Abstract", "Methods", "Results", "Figures", "Explorer"])

with story_tabs[0]:
    st.markdown("### Abstract")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(
            """
            This project predicts crop yield at the state × crop × season level in Nigeria
            by joining NBS agricultural survey tables with geospatial and climate covariates.
            The core value is not just the prediction itself, but the full pipeline: data audit,
            feature construction, leakage control, model selection, and explainability.
            """
        )
        st.markdown(
            """
            **Research question**: can state-level survey tables, climate summaries, and
            satellite vegetation indices jointly explain yield variation across crops and zones?
            """
        )
    with right:
        st.metric("States covered", "37")
        st.metric("Crops tracked", "22")
        st.metric("State-level yield rows", "490")
        st.metric("Total rows in processed table", "1,053")

with story_tabs[1]:
    st.markdown("### Methods")
    method_cols = st.columns(3)
    method_cols[0].markdown(
        """
        **1. Data audit**

        Validate the NBS workbook, standardize crop labels, and remove non-modelable
        aggregate rows before training.
        """
    )
    method_cols[1].markdown(
        """
        **2. Feature engineering**

        Join state metadata, climate summaries, and optional Sentinel-2 vegetation metrics
        to create a modeling-ready table.
        """
    )
    method_cols[2].markdown(
        """
        **3. Modeling**

        Compare a baseline against tree-based regressors, then inspect residuals, crop
        bias, and permutation importance.
        """
    )
    st.info(
        "Leakage control matters here: reported yield is not reconstructed from harvested area "
        "or production, and aggregate rows are excluded from the training set."
    )

with story_tabs[2]:
    st.markdown("### Results snapshot")
    if "model" in metrics.columns:
        leader = metrics.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Best model", str(leader["model"]))
        c2.metric("RMSE", f'{leader.get("rmse", float("nan")):,.2f}')
        c3.metric("MAE", f'{leader.get("mae", float("nan")):,.2f}')
        c4.metric("R²", f'{leader.get("r2", float("nan")):.3f}')
    st.dataframe(metrics, use_container_width=True)

with story_tabs[3]:
    st.markdown("### Figure gallery")
    if image_paths:
        selected_fig = st.selectbox("Choose a figure", [path.name for path in image_paths])
        fig_path = REPORTS_FIGURES_DIR / selected_fig
        st.image(Image.open(fig_path), caption=selected_fig, use_container_width=True)
    else:
        st.info("No figures were found in `reports/figures/`.")

with story_tabs[4]:
    st.markdown("### Data explorer")
    if not modeling.empty:
        explorer_cols = st.columns([1, 1, 2])
        with explorer_cols[0]:
            sample_size = st.slider("Rows to preview", 25, min(500, len(modeling)), min(100, len(modeling)))
        with explorer_cols[1]:
            column_choice = st.selectbox("Highlight column", modeling.columns.tolist())
        with explorer_cols[2]:
            st.caption("Quick glance at the feature table used for training.")
        st.dataframe(modeling.head(sample_size), use_container_width=True)
        if pd.api.types.is_numeric_dtype(modeling[column_choice]):
            st.bar_chart(modeling[column_choice].dropna().head(30))
    else:
        st.info("Modeling dataset is unavailable.")


# ---------------------------------------------------------------------
# Validate key columns
# ---------------------------------------------------------------------

model_col = find_column(metrics, ["model", "model_name", "estimator"])
pred_model_col = find_column(preds, ["model", "model_name", "estimator"])

if model_col is None:
    st.error(
        "The metrics file must contain a model column. Expected one of: "
        "`model`, `model_name`, or `estimator`."
    )
    st.stop()

if pred_model_col is None:
    st.error(
        "The predictions file must contain a model column. Expected one of: "
        "`model`, `model_name`, or `estimator`."
    )
    st.stop()

if metrics.empty:
    st.error("The metrics file is empty. Re-run the modeling notebook.")
    st.stop()

if preds.empty:
    st.error("The predictions file is empty. Re-run the prediction notebook.")
    st.stop()


# ---------------------------------------------------------------------
# Model leaderboard
# ---------------------------------------------------------------------

st.subheader("Model leaderboard")

st.markdown(
    """
    The table below compares the trained models using the evaluation metrics
    saved from the project notebooks.
    """
)

st.dataframe(metrics, use_container_width=True)

available_models = metrics[model_col].dropna().astype(str).tolist()

default_model = available_models[0]

selected_model = st.selectbox(
    "Select model to inspect",
    available_models,
    index=0,
)

view = preds[preds[pred_model_col].astype(str) == selected_model].copy()

if view.empty:
    st.warning(f"No prediction rows were found for model: `{selected_model}`")
    st.stop()


# ---------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------

st.subheader(f"Predictions from model: {selected_model}")

crop_col = find_column(view, ["crop", "commodity", "crop_name"])
zone_col = find_column(
    view,
    [
        "zone",
        "agroecological_zone",
        "agro_ecological_zone",
        "geopolitical_zone",
    ],
)
state_col = find_column(view, ["state", "state_name"])
season_col = find_column(view, ["season", "production_season"])

filter_cols = st.columns(4)

with filter_cols[0]:
    if crop_col is not None:
        crop_options = ["All"] + sorted(view[crop_col].dropna().astype(str).unique())
        selected_crop = st.selectbox("Crop", crop_options)

        if selected_crop != "All":
            view = view[view[crop_col].astype(str) == selected_crop]

with filter_cols[1]:
    if zone_col is not None:
        zone_options = ["All"] + sorted(view[zone_col].dropna().astype(str).unique())
        selected_zone = st.selectbox("Zone", zone_options)

        if selected_zone != "All":
            view = view[view[zone_col].astype(str) == selected_zone]

with filter_cols[2]:
    if state_col is not None:
        state_options = ["All"] + sorted(view[state_col].dropna().astype(str).unique())
        selected_state = st.selectbox("State", state_options)

        if selected_state != "All":
            view = view[view[state_col].astype(str) == selected_state]

with filter_cols[3]:
    if season_col is not None:
        season_options = ["All"] + sorted(view[season_col].dropna().astype(str).unique())
        selected_season = st.selectbox("Season", season_options)

        if selected_season != "All":
            view = view[view[season_col].astype(str) == selected_season]


# ---------------------------------------------------------------------
# Key columns for plots
# ---------------------------------------------------------------------

actual_col = find_column(
    view,
    [
        "yield_kg_ha",
        "actual",
        "actual_yield",
        "y_true",
        "target",
    ],
)

prediction_col = find_column(
    view,
    [
        "prediction",
        "predicted",
        "predicted_yield",
        "y_pred",
    ],
)

residual_col = find_column(
    view,
    [
        "residual",
        "error",
        "prediction_error",
    ],
)


# ---------------------------------------------------------------------
# Summary cards
# ---------------------------------------------------------------------

st.subheader("Prediction summary")

summary_cols = st.columns(4)

with summary_cols[0]:
    st.metric("Rows displayed", f"{len(view):,}")

with summary_cols[1]:
    if actual_col is not None:
        st.metric("Mean actual yield", f"{view[actual_col].mean():,.2f}")
    else:
        st.metric("Mean actual yield", "N/A")

with summary_cols[2]:
    if prediction_col is not None:
        st.metric("Mean predicted yield", f"{view[prediction_col].mean():,.2f}")
    else:
        st.metric("Mean predicted yield", "N/A")

with summary_cols[3]:
    if residual_col is not None:
        st.metric("Mean absolute residual", f"{view[residual_col].abs().mean():,.2f}")
    elif actual_col is not None and prediction_col is not None:
        temp_residual = view[prediction_col] - view[actual_col]
        st.metric("Mean absolute residual", f"{temp_residual.abs().mean():,.2f}")
    else:
        st.metric("Mean absolute residual", "N/A")


# ---------------------------------------------------------------------
# Actual vs predicted plot
# ---------------------------------------------------------------------

if actual_col is not None and prediction_col is not None:
    st.subheader("Actual vs predicted yield")

    plot_data = view.copy()

    if zone_col is not None:
        st.scatter_chart(
            plot_data,
            x=actual_col,
            y=prediction_col,
            color=zone_col,
            use_container_width=True,
        )
    else:
        st.scatter_chart(
            plot_data,
            x=actual_col,
            y=prediction_col,
            use_container_width=True,
        )
else:
    st.warning(
        """
        Could not create the actual-vs-predicted scatter plot because the
        required actual and prediction columns were not found.

        Expected actual column names include:
        `yield_kg_ha`, `actual`, `actual_yield`, `y_true`, `target`.

        Expected prediction column names include:
        `prediction`, `predicted`, `predicted_yield`, `y_pred`.
        """
    )


# ---------------------------------------------------------------------
# Residual/error table
# ---------------------------------------------------------------------

st.subheader("Prediction error table")

error_view = view.copy()

if residual_col is None and actual_col is not None and prediction_col is not None:
    error_view["residual"] = error_view[prediction_col] - error_view[actual_col]
    residual_col = "residual"

if residual_col is not None:
    error_view = error_view.sort_values(
        residual_col,
        key=lambda x: x.abs(),
        ascending=False,
    )

st.dataframe(error_view, use_container_width=True)


# ---------------------------------------------------------------------
# Grouped error analysis
# ---------------------------------------------------------------------

if residual_col is not None:
    st.subheader("Grouped error analysis")

    group_tabs = st.tabs(["By crop", "By zone", "By state", "By season"])

    with group_tabs[0]:
        if crop_col is not None:
            crop_error = (
                error_view
                .groupby(crop_col, as_index=False)
                .agg(
                    n_rows=(residual_col, "size"),
                    mean_residual=(residual_col, "mean"),
                    mean_abs_residual=(residual_col, lambda x: x.abs().mean()),
                )
                .sort_values("mean_abs_residual", ascending=False)
            )
            st.dataframe(crop_error, use_container_width=True)
        else:
            st.info("No crop column found.")

    with group_tabs[1]:
        if zone_col is not None:
            zone_error = (
                error_view
                .groupby(zone_col, as_index=False)
                .agg(
                    n_rows=(residual_col, "size"),
                    mean_residual=(residual_col, "mean"),
                    mean_abs_residual=(residual_col, lambda x: x.abs().mean()),
                )
                .sort_values("mean_abs_residual", ascending=False)
            )
            st.dataframe(zone_error, use_container_width=True)
        else:
            st.info("No zone column found.")

    with group_tabs[2]:
        if state_col is not None:
            state_error = (
                error_view
                .groupby(state_col, as_index=False)
                .agg(
                    n_rows=(residual_col, "size"),
                    mean_residual=(residual_col, "mean"),
                    mean_abs_residual=(residual_col, lambda x: x.abs().mean()),
                )
                .sort_values("mean_abs_residual", ascending=False)
            )
            st.dataframe(state_error, use_container_width=True)
        else:
            st.info("No state column found.")

    with group_tabs[3]:
        if season_col is not None:
            season_error = (
                error_view
                .groupby(season_col, as_index=False)
                .agg(
                    n_rows=(residual_col, "size"),
                    mean_residual=(residual_col, "mean"),
                    mean_abs_residual=(residual_col, lambda x: x.abs().mean()),
                )
                .sort_values("mean_abs_residual", ascending=False)
            )
            st.dataframe(season_error, use_container_width=True)
        else:
            st.info("No season column found.")


# ---------------------------------------------------------------------
# Modeling dataset sample
# ---------------------------------------------------------------------

if not modeling.empty:
    st.subheader("Modeling dataset sample")

    st.markdown(
        """
        This is a sample of the final machine-learning table used for training
        and evaluation.
        """
    )

    n_rows = st.slider(
        "Number of modeling rows to display",
        min_value=10,
        max_value=min(500, len(modeling)),
        value=min(100, len(modeling)),
        step=10,
    )

    st.dataframe(modeling.head(n_rows), use_container_width=True)
else:
    st.info(
        "`data/processed/modeling_dataset.csv` was not found, so the modeling "
        "dataset sample is not displayed."
    )


# ---------------------------------------------------------------------
# Available report tables
# ---------------------------------------------------------------------

st.subheader("Available report tables")

table_files = sorted(REPORTS_TABLES_DIR.glob("*.csv"))

if table_files:
    table_names = [path.name for path in table_files]
    selected_table_name = st.selectbox("Select a table to preview", table_names)

    selected_table_path = REPORTS_TABLES_DIR / selected_table_name
    selected_table = load_csv(selected_table_path, selected_table_name)

    st.dataframe(selected_table, use_container_width=True)
else:
    st.info("No CSV tables were found in `reports/tables/`.")


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.markdown("---")

st.caption(
    "Nigeria Crop Yield GeoAI dashboard. "
    "Run the notebooks in order to regenerate datasets, metrics, predictions, and reports."
)
