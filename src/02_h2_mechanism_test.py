"""Residual-pattern and timing-offset analyses.

The timing-offset model is geometry constrained: the entry velocity is fixed
by the measured release distance, v1 = sqrt(2*g*h0) with h0 = 7 mm, and only
g and the additive offset delta are fitted. Block-to-block stability and the
local g-delta correlation are reported as practical identifiability diagnostics.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit

from data_utils import G_REF, H0_NOMINAL_M, add_classical_estimate, load_data, output_path, split_blocks


def h1_model(t, v1, g):
    return v1 * t + 0.5 * g * t**2


def delta_model(t_measured, g, delta):
    """Geometry-constrained offset model with t_measured = t_true + delta.

    H = sqrt(2*g*h0)*(t_m - delta) + 0.5*g*(t_m - delta)^2, so that H = 0 at
    t_true = 0, i.e. at t_m = delta.
    """
    t_true = t_measured - delta
    return np.sqrt(2.0 * g * H0_NOMINAL_M) * t_true + 0.5 * g * t_true**2


def fit_h1(df):
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    popt, pcov = curve_fit(h1_model, t, H, p0=[0.4, 9.8])
    return popt, pcov


def corrected_residual(df, v1, g):
    t = df["t(s)"].to_numpy(dtype=float)
    g_classical = df["g_classical"].to_numpy(dtype=float)
    return (g_classical - 2.0 * v1 / t) - g


def covariance_to_correlation(pcov):
    scale = np.sqrt(np.diag(pcov))
    return pcov / np.outer(scale, scale)


def main() -> None:
    df = add_classical_estimate(load_data())
    block1, block2 = split_blocks(df)

    v1_pool, g_pool = fit_h1(df)[0]
    x_full = 1.0 / np.sqrt(df["h(m)"].to_numpy(dtype=float))

    y_raw = df["g_classical"].to_numpy(dtype=float) - G_REF
    raw = stats.linregress(x_full, y_raw)

    y_corr = corrected_residual(df, v1_pool, g_pool)
    corr = stats.linregress(x_full, y_corr)

    print("=== Pooled raw error vs 1/sqrt(H) ===")
    print(f"slope={raw.slope:.6f}, intercept={raw.intercept:.6f}, "
          f"R2={raw.rvalue**2:.6f}, p={raw.pvalue:.3e}\n")
    print("=== Pooled H1-corrected residual vs 1/sqrt(H) ===")
    print(f"slope={corr.slope:.6f}, intercept={corr.intercept:.6f}, "
          f"R2={corr.rvalue**2:.6f}, p={corr.pvalue:.3e}\n")

    # Cross-block functional-form check. The H1 and linear relation are
    # estimated on Block 1 only, then applied without refitting to Block 2.
    (v1_d1, g_d1), _ = fit_h1(block1)
    x_d1 = 1.0 / np.sqrt(block1["h(m)"].to_numpy(dtype=float))
    y_d1 = corrected_residual(block1, v1_d1, g_d1)
    block1_relation = stats.linregress(x_d1, y_d1)

    x_d2 = 1.0 / np.sqrt(block2["h(m)"].to_numpy(dtype=float))
    y_d2 = corrected_residual(block2, v1_d1, g_d1)
    y_d2_pred = block1_relation.slope * x_d2 + block1_relation.intercept
    ss_res = float(np.sum((y_d2 - y_d2_pred) ** 2))
    ss_tot = float(np.sum((y_d2 - y_d2.mean()) ** 2))
    r2_oos = np.nan if ss_tot == 0 else 1.0 - ss_res / ss_tot

    print("=== Block 1 relation applied to Block 2 corrected residual ===")
    print(f"Block 1 slope={block1_relation.slope:.6f}, "
          f"Block 1 R2={block1_relation.rvalue**2:.6f}")
    print(f"Block 2 out-of-sample R2={r2_oos:.6f}\n")

    mechanism_rows = [
        {
            "analysis": "pooled_raw_error_vs_inv_sqrt_H",
            "slope": raw.slope,
            "intercept": raw.intercept,
            "R2": raw.rvalue**2,
            "p_value": raw.pvalue,
        },
        {
            "analysis": "pooled_corrected_residual_vs_inv_sqrt_H",
            "slope": corr.slope,
            "intercept": corr.intercept,
            "R2": corr.rvalue**2,
            "p_value": corr.pvalue,
        },
        {
            "analysis": "block1_fit_block2_out_of_sample",
            "slope": block1_relation.slope,
            "intercept": block1_relation.intercept,
            "R2": r2_oos,
            "p_value": np.nan,
        },
    ]
    pd.DataFrame(mechanism_rows).to_csv(
        output_path("results", "h2_mechanism_results.csv"), index=False
    )

    delta_rows = []
    correlation_rows = []
    for sample, subset in (("Block 1", block1), ("Block 2", block2), ("Pooled", df)):
        H = subset["h(m)"].to_numpy(dtype=float)
        t = subset["t(s)"].to_numpy(dtype=float)
        popt, pcov = curve_fit(delta_model, t, H, p0=[9.6, 0.0])
        perr = np.sqrt(np.diag(pcov))
        pcorr = covariance_to_correlation(pcov)
        g_fit, delta_fit = popt
        g_se, delta_se = perr

        delta_rows.append(
            {
                "sample": sample,
                "n": len(subset),
                "h0_fixed_m": H0_NOMINAL_M,
                "g_m_s2": g_fit,
                "g_se_m_s2": g_se,
                "delta_ms": 1000.0 * delta_fit,
                "delta_se_ms": 1000.0 * delta_se,
                "corr_g_delta": pcorr[0, 1],
            }
        )

        names = ("g", "delta")
        for i, first in enumerate(names):
            for j, second in enumerate(names):
                correlation_rows.append(
                    {
                        "sample": sample,
                        "parameter_1": first,
                        "parameter_2": second,
                        "correlation": pcorr[i, j],
                    }
                )

        print(f"=== {sample}: geometry-constrained g, delta fit (h0 = {1000*H0_NOMINAL_M:.0f} mm) ===")
        print(f"g={g_fit:.6f} +/- {g_se:.6f} m/s^2")
        print(f"delta={1000*delta_fit:.3f} +/- {1000*delta_se:.3f} ms")
        print(f"corr(g,delta)={pcorr[0,1]:.6f}\n")

    pd.DataFrame(delta_rows).to_csv(
        output_path("results", "h2_delta_stability.csv"), index=False
    )
    pd.DataFrame(correlation_rows).to_csv(
        output_path("results", "h2_delta_parameter_correlations.csv"), index=False
    )
    print("Saved H2 mechanism, delta, and parameter-correlation results.")


if __name__ == "__main__":
    main()
