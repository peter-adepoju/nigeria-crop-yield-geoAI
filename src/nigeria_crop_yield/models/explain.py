from __future__ import annotations

import pandas as pd


def permutation_importance_table(model, X: pd.DataFrame, y: pd.Series, n_repeats: int = 10, random_state: int = 42) -> pd.DataFrame:
    """Compute permutation importance for any fitted sklearn pipeline."""
    from sklearn.inspection import permutation_importance

    result = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=random_state, n_jobs=-1)
    return (
        pd.DataFrame(
            {
                "feature": X.columns,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
