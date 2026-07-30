#!/usr/bin/env python3
"""Kinematic fits for Block 1, Block 2, and pooled data.

Two models are reported:

1. Effective-linear-term model
       H = v_eff*t + 0.5*g*t^2
   where v_eff and g are fitted jointly. The fitted linear coefficient is
   intentionally named v_eff because the independently observed release
   geometry shows that it cannot be interpreted as the physical entry
   velocity alone.

2. Nominal-geometry sensitivity model
       H = sqrt(2*g*h0)*t + 0.5*g*t^2
   where h0 = 1 mm is fixed from the approximate lower-surface-to-beam
   clearance and only g is fitted. This is a sensitivity analysis, not the
   primary estimator, because h0 and the photogate trigger threshold were not
   calibrated with a quantified uncertainty.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from data_utils import (
    G_REF,
    H0_NOMINAL_M,
    V1_GEOMETRIC_REF_M_S,
    add_classical_estimate,
    load_data,
    mae,
    output_path,
    rmse,
    split_blocks,
)


def effective_linear_model(t, v_eff, g):
    """H = v_eff*t + 0.5*g*t^2, with H(0)=0 by construction."""
    return v_eff * t + 0.5 * g * t**2


def nominal_geometry_model(t, g):
    """Kinematic model with h0 fixed and v1=sqrt(2*g*h0)."""
    if np.any(np.asarray(g) <= 0):
        return np.full_like(np.asarray(t, dtype=float), np.nan, dtype=float)
    v_geometry = np.sqrt(2.0 * g * H0_NOMINAL_M)
    return v_geometry * t + 0.5 * g * t**2


def fit_effective_linear(df):
    """Return parameters, covariance errors, covariance, and H-space RMSE."""
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    popt, pcov = curve_fit(effective_linear_model, t, H, p0=[0.4, 9.8])
    perr = np.sqrt(np.diag(pcov))
    residual = H - effective_linear_model(t, *popt)
    rmse_h = float(np.sqrt(np.mean(residual**2)))
    return popt, perr, pcov, rmse_h


def fit_nominal_geometry(df):
    """Fit g with h0 fixed; return g, covariance error, and H-space RMSE."""
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    popt, pcov = curve_fit(
        nominal_geometry_model,
        t,
        H,
        p0=[9.8],
        bounds=(1.0e-12, np.inf),
    )
    g_fit = float(popt[0])
    g_err = float(np.sqrt(pcov[0, 0]))
    residual = H - nominal_geometry_model(t, g_fit)
    rmse_h = float(np.sqrt(np.mean(residual**2)))
    return g_fit, g_err, rmse_h


def main() -> None:
    df = add_classical_estimate(load_data())
    block1, block2 = split_blocks(df)

    rows = []
    for sample, subset in (("Block 1", block1), ("Block 2", block2), ("Pooled", df)):
        popt, perr, pcov, rmse_h_eff = fit_effective_linear(subset)
        v_eff, g_eff = popt
        v_eff_err, g_eff_err = perr
        corr_v_g = pcov[0, 1] / np.sqrt(pcov[0, 0] * pcov[1, 1])
        g_geom, g_geom_err, rmse_h_geom = fit_nominal_geometry(subset)

        result = {
            "sample": sample,
            "n": len(subset),
            "classical_mae_m_s2": mae(G_REF, subset["g_classical"]),
            "classical_rmse_m_s2": rmse(G_REF, subset["g_classical"]),
            "v_effective_m_s": v_eff,
            "v_effective_se_m_s": v_eff_err,
            "g_effective_fit_m_s2": g_eff,
            "g_effective_fit_se_m_s2": g_eff_err,
            "g_effective_abs_deviation_m_s2": abs(g_eff - G_REF),
            "corr_v_effective_g": corr_v_g,
            "effective_fit_rmse_H_m": rmse_h_eff,
            "h0_nominal_m": H0_NOMINAL_M,
            "v1_geometry_ref_m_s": V1_GEOMETRIC_REF_M_S,
            "v_effective_to_geometry_ratio": v_eff / V1_GEOMETRIC_REF_M_S,
            "h0_effective_from_v_m": v_eff**2 / (2.0 * G_REF),
            "g_nominal_geometry_fit_m_s2": g_geom,
            "g_nominal_geometry_fit_se_m_s2": g_geom_err,
            "g_nominal_geometry_abs_deviation_m_s2": abs(g_geom - G_REF),
            "nominal_geometry_fit_rmse_H_m": rmse_h_geom,
        }
        rows.append(result)

        print(f"--- {sample} (n={len(subset)}) ---")
        print(
            f"Classical: MAE={result['classical_mae_m_s2']:.4f}, "
            f"RMSE={result['classical_rmse_m_s2']:.4f} m/s^2"
        )
        print(
            f"Effective-linear fit: v_eff={v_eff:.6f} +/- {v_eff_err:.6f} m/s, "
            f"g={g_eff:.6f} +/- {g_eff_err:.6f} m/s^2, "
            f"|g-g_ref|={abs(g_eff-G_REF):.6f} m/s^2, "
            f"RMSE_H={rmse_h_eff:.6f} m"
        )
        print(f"corr(v_eff,g)={corr_v_g:.6f}")
        print(
            f"Geometry check: h0={H0_NOMINAL_M*1000:.3f} mm, "
            f"v1_geom={V1_GEOMETRIC_REF_M_S:.6f} m/s, "
            f"v_eff/v1_geom={v_eff/V1_GEOMETRIC_REF_M_S:.3f}, "
            f"h0_eff={v_eff**2/(2.0*G_REF)*1000:.3f} mm"
        )
        print(
            f"Nominal-geometry sensitivity fit: g={g_geom:.6f} +/- "
            f"{g_geom_err:.6f} m/s^2, |g-g_ref|={abs(g_geom-G_REF):.6f} m/s^2, "
            f"RMSE_H={rmse_h_geom:.6f} m\n"
        )

    out = pd.DataFrame(rows)
    path = output_path("results", "h1_fit_results.csv")
    out.to_csv(path, index=False)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
