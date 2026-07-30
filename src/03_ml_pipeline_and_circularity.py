"""Diagnostic residual-ML pipeline and algebraic-circularity demonstration."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from data_utils import G_REF, add_classical_estimate, load_data, mae, output_path, rmse, split_blocks
from ml_utils import build_features, select_best_model


def evaluate_direction(train_df, test_df, include_mechanism_feature: bool, label: str):
    X_train, y_train = build_features(train_df, include_mechanism_feature)
    X_test, _ = build_features(test_df, include_mechanism_feature)

    selected = select_best_model(X_train, y_train)
    y_pred = selected.estimator.predict(X_test)
    g_hat = test_df["g_classical"].to_numpy(dtype=float) - y_pred

    result = {
        "configuration": label,
        "algorithm": selected.algorithm,
        "hyperparameters": json.dumps(selected.hyperparameters, sort_keys=True),
        "loo_cv_rmse_target": selected.loo_rmse,
        "n_train": len(train_df),
        "n_test": len(test_df),
        "test_mae_g_m_s2": mae(G_REF, g_hat),
        "test_rmse_g_m_s2": rmse(G_REF, g_hat),
    }
    print(
        f"[{label}] algorithm={selected.algorithm}; "
        f"params={selected.hyperparameters}; LOO-RMSE={selected.loo_rmse:.6f}; "
        f"test MAE={result['test_mae_g_m_s2']:.6f}; "
        f"test RMSE={result['test_rmse_g_m_s2']:.6f}"
    )
    return result


def main() -> None:
    df = add_classical_estimate(load_data())
    block1, block2 = split_blocks(df)

    print("=" * 78)
    print("CAUTION: y = 2H/t^2 - g_ref is an exact function of the inputs H and t.")
    print("The following scores describe numerical approximation of that identity,")
    print("not an independently learned physical correction.")
    print("=" * 78)

    rows = []
    for include_feature, model_name in ((False, "Model A"), (True, "Model B")):
        rows.append(
            evaluate_direction(
                block1,
                block2,
                include_feature,
                f"{model_name}: Block 1 -> Block 2",
            )
        )
        rows.append(
            evaluate_direction(
                block2,
                block1,
                include_feature,
                f"{model_name}: Block 2 -> Block 1",
            )
        )

    for train_block, test_block, label in (
        (block1, block2, "Block 1 -> Block 2"),
        (block2, block1, "Block 2 -> Block 1"),
    ):
        mean_residual = float((train_block["g_classical"] - G_REF).mean())
        g_hat_baseline = (
            test_block["g_classical"].to_numpy(dtype=float) - mean_residual
        )
        rows.append(
            {
                "configuration": f"Mean-residual baseline: {label}",
                "algorithm": "constant_mean_residual",
                "hyperparameters": "{}",
                "loo_cv_rmse_target": np.nan,
                "n_train": len(train_block),
                "n_test": len(test_block),
                "test_mae_g_m_s2": mae(G_REF, g_hat_baseline),
                "test_rmse_g_m_s2": rmse(G_REF, g_hat_baseline),
            }
        )

    # The exact baseline is not fitted. It reconstructs the target from the
    # inputs by definition and therefore has exactly zero target error.
    rows.append(
        {
            "configuration": "Exact algebraic target baseline",
            "algorithm": "y = 2H/t^2 - g_ref",
            "hyperparameters": "{}",
            "loo_cv_rmse_target": 0.0,
            "n_train": np.nan,
            "n_test": len(df),
            "test_mae_g_m_s2": 0.0,
            "test_rmse_g_m_s2": 0.0,
        }
    )

    path = output_path("results", "ml_pipeline_results.csv")
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
