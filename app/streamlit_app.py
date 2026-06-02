# -*- coding: utf-8 -*-
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
    html, body, [class*="css"] {font-family: "Segoe UI", "Inter", "Arial", sans-serif;}
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


story_tabs = st.tabs(
    [
        "Project Story",
        "Background",
        "Data",
        "Feature Engineering",
        "Modeling",
        "Evaluation",
        "Explainability",
        "Figures",
        "Explorer",
        "Limitations",
        "Future Work",
    ]
)

with story_tabs[0]:
    st.markdown("### Project Story")
    st.markdown(
        """
        This project is a GeoAI study of crop yield prediction across Nigerian states and
        agroecological zones. The central idea is simple but important: yield is shaped by
        geography, crop type, seasonality, climate, and vegetation condition, so any serious
        forecasting model should reflect those forces rather than rely on a single aggregate
        number.

        The repository is organized like a full research pipeline. It begins with raw NBS
        survey tables, adds state metadata, then enriches the table with climate and
        Sentinel-2 summaries where available. After that, several regression models are
        compared, the best model is tuned and explained, and the residuals are analyzed by
        crop, state, season, and zone.

        The website is intentionally paper-like. It tells the story in the same order a
        researcher would write it: problem, background, data, methods, results, interpretation,
        limitations, and future work. The goal is not merely to show output, but to help a
        reader understand why the output matters.
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("States covered", "37")
    c2.metric("Crops tracked", "22")
    c3.metric("State-level yield rows", "490")
    c4.metric("Total processed rows", "1,053")
    st.info(
        "The project uses state-level agricultural reporting, so it is best read as a high-quality "
        "predictive and explanatory study rather than a plot-level operational system."
    )

with story_tabs[1]:
    st.markdown("### Background")
    st.markdown(
        """
        Nigeria's agriculture is spatially diverse. Rainfall, heat, humidity, crop mix, and
        seasonal timing vary across the country, which means that a national average hides a
        great deal of local structure. That is why crop yield modeling is not just a machine
        learning exercise: it is a spatial reasoning problem.

        Machine learning is used here as a function-approximation tool. The model learns a
        mapping from features such as crop, state, climate, and vegetation indices to the
        continuous target yield in kg/ha. Because the target is numeric, this is a regression
        problem rather than a classification problem.

        Several background ideas are essential:
        - supervised learning uses labeled examples,
        - regression predicts continuous values,
        - leakage occurs when target information enters the feature set,
        - interpretability tells us what the model learned,
        - geospatial context matters because location is not neutral.
        """
    )
    st.warning(
        "If you are new to ML, think of this project as learning from examples of state-crop-season "
        "rows, then checking whether the learned pattern generalizes to new data and new regions."
    )

with story_tabs[2]:
    st.markdown("### Data")
    st.markdown(
        """
        The core source is the NBS National Agricultural Sample Survey 2022/2023 report tables.
        These tables supply the target yield and the main agricultural context. The processed
        table in the repo summarizes 1,053 rows, of which 490 are state-level rows with yield
        values.

        The data sources in the pipeline are:
        1. NBS survey tables, which define the target and the row structure.
        2. State metadata, which attaches centroid and zone information.
        3. Climate data, either from NiMet or NASA POWER fallback summaries.
        4. Sentinel-2 remote sensing, which supplies vegetation-condition features.

        The project deliberately supports both a quickstart mode and a fuller geospatial mode.
        That means the reader can reproduce the main project using only the included public data,
        and then optionally extend it with richer climate and satellite inputs.
        """
    )
    ds_cols = st.columns(3)
    ds_cols[0].markdown(
        """
        **Included data**

        - NBS workbook
        - processed yield table
        - state metadata
        - modeling dataset
        """
    )
    ds_cols[1].markdown(
        """
        **Optional data**

        - NiMet station climate data
        - NASA POWER fallback climate data
        - Sentinel-2 extraction outputs
        """
    )
    ds_cols[2].markdown(
        """
        **Important constraint**

        Not all ideal data are open or lightweight. The project therefore keeps the
        code flexible enough to degrade gracefully when only the public source tables
        are available.
        """
    )

with story_tabs[3]:
    st.markdown("### Feature Engineering")
    st.markdown(
        """
        Feature engineering turns raw public tables into a modeling dataset. This is one of
        the most important stages in the project because the model can only learn from the
        variables it receives. The final table is designed to answer the question: what can
        we safely know about a state-crop-season observation before we try to predict yield?

        The feature set combines:
        - survey variables such as crop and season,
        - spatial variables such as state and zone,
        - climate summaries such as rainfall and temperature,
        - Sentinel-2 vegetation indices such as NDVI, EVI, NDWI, and SAVI.

        The crucial design rule is leakage control. Variables that are algebraically or
        operationally tied to yield, such as harvested area or production, are excluded from
        the predictors because they would make the task unrealistically easy.
        """
    )
    feat_cols = st.columns(2)
    feat_cols[0].markdown(
        """
        **Remote sensing logic**

        Sentinel-2 bands are not used raw in the dashboard. Instead, they are transformed
        into vegetation indices because those summarize canopy vigor, moisture, and soil
        background effects in a more interpretable way.
        """
    )
    feat_cols[1].markdown(
        """
        **Temporal aggregation**

        Daily climate or satellite observations are reduced to seasonal summaries so that the
        machine learning models can work with a single row per state-crop-season example.
        """
    )

with story_tabs[4]:
    st.markdown("### Modeling")
    st.markdown(
        """
        The project compares a set of regression models that range from simple to flexible.
        The purpose of this comparison is not just to maximize performance but to understand
        whether nonlinear models add meaningful value beyond a simple baseline.

        The candidate family includes:
        - mean or dummy baseline,
        - ridge regression,
        - random forest,
        - extra trees,
        - gradient boosting,
        - multi-layer perceptron regressor.

        The tuned results stored in the repository show that the tree-based models are the
        strongest performers. This suggests that the yield problem contains nonlinearities
        and interactions that simple linear models cannot capture as well.
        """
    )
    if "model" in metrics.columns:
        model_summary = metrics.copy()
        cols = [c for c in ["model", "rmse", "mae", "r2", "mape_percent"] if c in model_summary.columns]
        st.dataframe(model_summary[cols], use_container_width=True)
    st.markdown(
        """
        **Best tuned results from the stored outputs**

        - Random Forest: RMSE 1433.59, MAE 808.71, R2 0.535
        - Extra Trees: RMSE 1442.53, MAE 831.85, R2 0.529
        - Gradient Boosting: RMSE 1538.65, MAE 901.20, R2 0.465
        """
    )

with story_tabs[5]:
    st.markdown("### Evaluation")
    st.markdown(
        """
        Evaluation is where we ask whether the model actually generalizes. The project uses
        several metrics because no single number is enough.

        MAE measures the average absolute error in kg/ha. RMSE penalizes large errors more
        strongly. R2 measures how much variance is explained relative to a mean baseline.
        MAPE expresses error as a percentage, though it should be interpreted carefully when
        yield values are small.

        The project also evaluates residuals by crop, zone, state, and season. This subgroup
        analysis is important because a model with a strong overall score may still fail badly
        for one crop or one region.
        """
    )
    if "model" in metrics.columns:
        leader = metrics.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Best model", str(leader["model"]))
        m2.metric("RMSE", f'{leader.get("rmse", float("nan")):,.2f}')
        m3.metric("MAE", f'{leader.get("mae", float("nan")):,.2f}')
        m4.metric("R2", f'{leader.get("r2", float("nan")):.3f}')
    st.caption("The evaluation story is not complete without residual analysis and subgroup checks.")

with story_tabs[6]:
    st.markdown("### Explainability")
    st.markdown(
        """
        Explainability answers the question: what is the model using to make its predictions?
        In this project, feature importance, permutation importance, partial dependence, and
        subgroup residual tables are used to open up the model.

        Explainability is not the same as causality. If a feature is important, that means the
        model uses it well, not that changing the feature will necessarily change the real-world
        yield. This is an important distinction in any serious applied machine learning project.
        """
    )
    ex_cols = st.columns(2)
    ex_cols[0].markdown(
        """
        **What the plots can show**

        - which features matter most,
        - which crops are harder to predict,
        - where the model underpredicts or overpredicts,
        - whether climate variables carry meaningful signal.
        """
    )
    ex_cols[1].markdown(
        """
        **What they cannot prove**

        - direct causality,
        - operational intervention effects,
        - exact field-level conditions,
        - perfect understanding of every row.
        """
    )

with story_tabs[7]:
    st.markdown("### Figures")
    st.markdown(
        """
        The figures below are the project?s visual evidence. They are not decoration. They are
        the graphical form of the story told in the textbook.
        """
    )
    if image_paths:
        figure_names = [path.name for path in image_paths]
        figure_map = {path.name: path for path in image_paths}
        selected_fig = st.selectbox("Choose a figure to inspect", figure_names)
        fig_path = figure_map[selected_fig]
        st.image(Image.open(fig_path), caption=selected_fig, use_container_width=True)
        st.markdown(
            f"""
            **Selected figure:** `{selected_fig}`  
            Use this figure in the textbook where the corresponding concept is discussed. The
            dashboard keeps the full set of notebook-generated plots available so that no key
            result is hidden.
            """
        )
    else:
        st.info("No figures were found in `reports/figures/`.")

with story_tabs[8]:
    st.markdown("### Explorer")
    st.markdown(
        """
        The explorer lets the reader inspect the modeling dataset directly. This helps connect
        the high-level story to the actual rows used in training. It is particularly useful for
        verifying that the dataset is structured as expected and for seeing how features vary.
        """
    )
    if not modeling.empty:
        explorer_cols = st.columns([1, 1, 2])
        with explorer_cols[0]:
            sample_size = st.slider(
                "Rows to preview",
                25,
                min(500, len(modeling)),
                min(100, len(modeling)),
            )
        with explorer_cols[1]:
            column_choice = st.selectbox("Highlight column", modeling.columns.tolist())
        with explorer_cols[2]:
            st.caption("Quick glance at the feature table used for training.")
        st.dataframe(modeling.head(sample_size), use_container_width=True)
        if pd.api.types.is_numeric_dtype(modeling[column_choice]):
            st.bar_chart(modeling[column_choice].dropna().head(30), use_container_width=True)
    else:
        st.info("Modeling dataset is unavailable.")

with story_tabs[9]:
    st.markdown("### Limitations")
    st.markdown(
        """
        The project is strong as an educational and exploratory GeoAI study, but it still has
        real limitations. The data are state-level, not plot-level. The satellite summaries are
        coarse approximations. Some climate inputs are optional or fallback-based. And the model
        is predictive rather than causal.

        These limitations do not weaken the project?s value. They define the boundary of what the
        analysis can honestly claim. A good scientific project is not one that hides its limits,
        but one that states them clearly.
        """
    )
    st.markdown(
        """
        **Main threats to validity**

        - aggregation hides local variation,
        - seasonal summaries may not align perfectly with crop calendars,
        - measurement noise may remain in survey tables,
        - some crops are sparse,
        - grouped validation is important because random splits can overstate performance.
        """
    )

with story_tabs[10]:
    st.markdown("### Future Work")
    st.markdown(
        """
        The most important future improvement is to move from coarse state-level summaries to
        plot-level or farm-level geospatial data. That would allow more accurate climate and
        satellite alignment and would make the analysis much more operational.

        Other strong future directions include:
        - stronger temporal models,
        - uncertainty quantification,
        - more robust spatial validation,
        - causal inference extensions,
        - policy-facing risk dashboards.

        These future directions build directly on the current pipeline. The present project is
        already a complete story, but it is also a foundation for a more advanced research or
        production-grade system.
        """
    )

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




