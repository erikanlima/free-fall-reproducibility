"""Shared model selection utilities for the diagnostic ML pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneOut, ParameterGrid, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from data_utils import G_REF

RANDOM_STATE = 42


@dataclass
class SelectedModel:
    estimator: Any
    algorithm: str
    hyperparameters: dict[str, Any]
    loo_rmse: float


def build_features(df, include_mechanism_feature: bool):
    """Build Model A/B features and the algebraically circular target."""
    features = df[["h(m)", "t(s)"]].copy()
    if include_mechanism_feature:
        features["inv_sqrt_H"] = 1.0 / np.sqrt(df["h(m)"])
    target = df["g_classical"] - G_REF
    return features.to_numpy(dtype=float), target.to_numpy(dtype=float)


def candidate_models():
    """Return estimators and complete hyperparameter grids.

    Ridge is placed in a scaling pipeline because its regularization penalty
    is scale-sensitive. Tree models use raw features.
    """
    return {
        "ridge": (
            Pipeline([
                ("scale", StandardScaler()),
                ("ridge", Ridge()),
            ]),
            {"ridge__alpha": [0.1, 1.0, 10.0]},
        ),
        "random_forest": (
            RandomForestRegressor(random_state=RANDOM_STATE),
            {"n_estimators": [50, 100], "max_depth": [2, 3, 4]},
        ),
        "gradient_boosting": (
            GradientBoostingRegressor(random_state=RANDOM_STATE),
            {
                "n_estimators": [50, 100],
                "max_depth": [2, 3],
                "learning_rate": [0.05, 0.1],
            },
        ),
    }


def select_best_model(X_train, y_train) -> SelectedModel:
    """Select the model with the lowest aggregate LOO out-of-fold RMSE.

    ``GridSearchCV(scoring='neg_root_mean_squared_error')`` is not used here
    because every leave-one-out test fold contains one observation; averaging
    fold-level RMSE values would then equal MAE, not the RMSE of all out-of-fold
    predictions. This routine explicitly aggregates all LOO predictions before
    computing RMSE.
    """
    loo = LeaveOneOut()
    best: SelectedModel | None = None

    for algorithm, (base_estimator, grid) in candidate_models().items():
        for params in ParameterGrid(grid):
            estimator = clone(base_estimator).set_params(**params)
            predictions = cross_val_predict(
                estimator,
                X_train,
                y_train,
                cv=loo,
                n_jobs=-1,
                method="predict",
            )
            score = float(np.sqrt(mean_squared_error(y_train, predictions)))
            if best is None or score < best.loo_rmse:
                fitted = clone(estimator).fit(X_train, y_train)
                best = SelectedModel(
                    estimator=fitted,
                    algorithm=algorithm,
                    hyperparameters=params,
                    loo_rmse=score,
                )

    if best is None:
        raise RuntimeError("No candidate model was evaluated.")
    return best
