"""Ablation and redundant-feature permutation diagnostics for Model B."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from data_utils import G_REF, add_classical_estimate, load_data, mae, output_path, split_blocks
from ml_utils import RANDOM_STATE, build_features, select_best_model

N_PERMUTATIONS = 1000


def main() -> None:
    df = add_classical_estimate(load_data())
    block1, block2 = split_blocks(df)

    X_train_A, y_train = build_features(block1, include_mechanism_feature=False)
    X_train_B, _ = build_features(block1, include_mechanism_feature=True)
    X_test_A, _ = build_features(block2, include_mechanism_feature=False)
    X_test_B, _ = build_features(block2, include_mechanism_feature=True)

    selected_A = select_best_model(X_train_A, y_train)
    selected_B = select_best_model(X_train_B, y_train)

    g_classical_test = block2["g_classical"].to_numpy(dtype=float)
    g_hat_A = g_classical_test - selected_A.estimator.predict(X_test_A)
    g_hat_B = g_classical_test - selected_B.estimator.predict(X_test_B)
    mae_A = mae(G_REF, g_hat_A)
    mae_B = mae(G_REF, g_hat_B)

    rng = np.random.default_rng(RANDOM_STATE)
    H_test = block2["h(m)"].to_numpy(dtype=float)
    t_test = block2["t(s)"].to_numpy(dtype=float)
    inv_sqrt_H = 1.0 / np.sqrt(H_test)

    permuted_mae = np.empty(N_PERMUTATIONS, dtype=float)
    for index in range(N_PERMUTATIONS):
        X_permuted = np.column_stack(
            [H_test, t_test, rng.permutation(inv_sqrt_H)]
        )
        g_hat = g_classical_test - selected_B.estimator.predict(X_permuted)
        permuted_mae[index] = mae(G_REF, g_hat)

    fraction_worse = float(np.mean(permuted_mae > mae_B))
    # One-sided empirical p-value for an unusually small original MAE.
    empirical_p = float((1 + np.sum(permuted_mae <= mae_B)) / (N_PERMUTATIONS + 1))

    print("=== Ablation ===")
    print(
        f"Model A: {selected_A.algorithm}, {selected_A.hyperparameters}, "
        f"MAE={mae_A:.6f}"
    )
    print(
        f"Model B: {selected_B.algorithm}, {selected_B.hyperparameters}, "
        f"MAE={mae_B:.6f}"
    )
    print(f"B - A = {mae_B - mae_A:+.6f} m/s^2\n")

    print("=== Redundant-feature permutation ===")
    print(f"Original Model B MAE={mae_B:.6f}")
    print(
        f"Permuted MAE={permuted_mae.mean():.6f} +/- "
        f"{permuted_mae.std(ddof=1):.6f}"
    )
    print(f"Fraction of permutations with worse MAE={fraction_worse:.6f}")
    print(f"One-sided empirical p-value={empirical_p:.6f}")
    print(
        "Interpretation caution: permutation breaks the deterministic relation "
        "between H and 1/sqrt(H), creating internally inconsistent inputs."
    )

    rows = [
        {"quantity": "model_A_algorithm", "value": selected_A.algorithm},
        {
            "quantity": "model_A_hyperparameters",
            "value": json.dumps(selected_A.hyperparameters, sort_keys=True),
        },
        {"quantity": "model_A_loo_rmse", "value": selected_A.loo_rmse},
        {"quantity": "model_A_test_mae", "value": mae_A},
        {"quantity": "model_B_algorithm", "value": selected_B.algorithm},
        {
            "quantity": "model_B_hyperparameters",
            "value": json.dumps(selected_B.hyperparameters, sort_keys=True),
        },
        {"quantity": "model_B_loo_rmse", "value": selected_B.loo_rmse},
        {"quantity": "model_B_test_mae", "value": mae_B},
        {"quantity": "permutation_n", "value": N_PERMUTATIONS},
        {"quantity": "permutation_mean_mae", "value": permuted_mae.mean()},
        {"quantity": "permutation_sd_mae", "value": permuted_mae.std(ddof=1)},
        {"quantity": "permutation_fraction_worse", "value": fraction_worse},
        {"quantity": "permutation_empirical_p", "value": empirical_p},
    ]
    path = output_path("results", "diagnostics_results.csv")
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
