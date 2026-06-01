from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class TrainingResult:
    best_model_name: str
    best_model: Pipeline
    metrics: pd.DataFrame
    predictions: pd.DataFrame


def _available_features(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    return [c for c in candidates if c in df.columns]


def make_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, numeric_features),
            ("cat", categorical, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def make_models(random_state: int = 42) -> dict[str, Any]:
    return {
        "dummy_mean": DummyRegressor(strategy="mean"),
        "ridge": Ridge(alpha=3.0),
        "random_forest": RandomForestRegressor(
            n_estimators=120,
            max_depth=None,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=160,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=180,
            learning_rate=0.04,
            max_depth=3,
            random_state=random_state,
        ),
        "mlp": MLPRegressor(
            hidden_layer_sizes=(64, 32),
            alpha=0.01,
            learning_rate_init=0.001,
            max_iter=350,
            early_stopping=True,
            random_state=random_state,
        ),
    }


def split_data(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.25,
    random_state: int = 42,
    group_col: str | None = "state",
):
    df = df[df[target].notna()].copy()
    if group_col and group_col in df.columns and df[group_col].nunique() > 4:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
        train_idx, test_idx = next(splitter.split(df, df[target], groups=df[group_col]))
        return df.iloc[train_idx].copy(), df.iloc[test_idx].copy()
    train, test = train_test_split(df, test_size=test_size, random_state=random_state)
    return train.copy(), test.copy()


def train_and_select(
    df: pd.DataFrame,
    config: dict[str, Any],
    output_dir: str | Path = "models",
) -> TrainingResult:
    target = config["nbs"].get("target", "yield_kg_ha")
    modeling = config["modeling"]
    random_state = int(config["project"].get("random_state", 42))
    leakage_cols = set(modeling.get("leakage_columns", []))

    numeric_features = _available_features(df, modeling.get("numeric_features", []))
    categorical_features = _available_features(df, modeling.get("categorical_features", []))
    feature_cols = [c for c in numeric_features + categorical_features if c not in leakage_cols]

    train_df, test_df = split_data(
        df,
        target=target,
        test_size=float(modeling.get("test_size", 0.25)),
        random_state=random_state,
        group_col="state" if modeling.get("split_strategy") == "group_by_state" else None,
    )

    X_train, y_train = train_df[feature_cols], train_df[target]
    X_test, y_test = test_df[feature_cols], test_df[target]

    preprocessor = make_preprocessor(numeric_features, categorical_features)
    models = make_models(random_state=random_state)
    selected = modeling.get("include_models") or list(models)

    metric_rows = []
    prediction_frames = []
    fitted_models = {}

    for name in selected:
        if name not in models:
            continue
        pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", models[name])])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        mae = mean_absolute_error(y_test, pred)
        r2 = r2_score(y_test, pred)
        mape = np.mean(np.abs((y_test - pred) / np.maximum(np.abs(y_test), 1))) * 100
        metric_rows.append({"model": name, "rmse": rmse, "mae": mae, "r2": r2, "mape_percent": mape})
        fitted_models[name] = pipe
        pred_df = test_df[["state", "zone", "crop", "season", target]].copy()
        pred_df["prediction"] = pred
        pred_df["residual"] = pred_df[target] - pred_df["prediction"]
        pred_df["model"] = name
        prediction_frames.append(pred_df)

    metrics = pd.DataFrame(metric_rows).sort_values("rmse", ascending=True).reset_index(drop=True)
    best_name = metrics.iloc[0]["model"]
    best_model = fitted_models[best_name]
    predictions = pd.concat(prediction_frames, ignore_index=True)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, output_dir / "best_model.joblib")
    joblib.dump({"feature_cols": feature_cols, "target": target, "best_model": best_name}, output_dir / "training_metadata.joblib")

    return TrainingResult(
        best_model_name=str(best_name), best_model=best_model, metrics=metrics, predictions=predictions
    )
