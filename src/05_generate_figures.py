#!/usr/bin/env python3
"""Regenerate the three data-derived manuscript figures (Figures 2--4)."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit

from data_utils import (
    G_REF,
    H0_NOMINAL_M,
    V1_GEOMETRIC_REF_M_S,
    add_classical_estimate,
    load_data,
    mae,
    output_path,
    split_blocks,
)
from ml_utils import build_features, select_best_model

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 12.2,
    "axes.labelsize": 13.2,
    "xtick.labelsize": 11.8,
    "ytick.labelsize": 11.8,
    "legend.fontsize": 11.2,
    "axes.linewidth": 0.8,
    "figure.dpi": 300,
})

BLOCK1_COLOR = "#3B6FA0"
BLOCK2_COLOR = "#5B8C5A"
POOLED_COLOR = "#B23A48"
GEOMETRY_COLOR = "#5C4B8A"
RAW_COLOR = "#A6A6A6"


def effective_linear_model(t, v_eff, g):
    return v_eff * t + 0.5 * g * t**2


def nominal_geometry_model(t, g):
    return np.sqrt(2.0 * g * H0_NOMINAL_M) * t + 0.5 * g * t**2


def fit_effective_linear(df):
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    popt, pcov = curve_fit(effective_linear_model, t, H, p0=[0.4, 9.8])
    return popt, np.sqrt(np.diag(pcov))


def fit_nominal_geometry(df):
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    popt, pcov = curve_fit(
        nominal_geometry_model,
        t,
        H,
        p0=[9.8],
        bounds=(1.0e-12, np.inf),
    )
    return float(popt[0]), float(np.sqrt(pcov[0, 0]))


def save_figure(fig, stem: str) -> None:
    for extension in ("pdf", "png"):
        fig.savefig(
            output_path("figures", f"{stem}.{extension}"),
            dpi=300,
            bbox_inches="tight",
        )
    plt.close(fig)


def figure_kinematic_fit(df, block1, block2):
    effective_fits = {
        "Block 1": fit_effective_linear(block1),
        "Block 2": fit_effective_linear(block2),
        "Pooled": fit_effective_linear(df),
    }
    geometry_fits = {
        "Block 1": fit_nominal_geometry(block1),
        "Block 2": fit_nominal_geometry(block2),
        "Pooled": fit_nominal_geometry(df),
    }
    (v_pool, g_pool), _ = effective_fits["Pooled"]
    g_geom_pool, _ = geometry_fits["Pooled"]

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15.8, 5.2),
        gridspec_kw={"width_ratios": [1.45, 0.95, 0.90]},
    )

    # Panel a: data and pooled curves.
    ax = axes[0]
    ax.scatter(
        block1["t(s)"], block1["h(m)"], s=17, alpha=0.67,
        color=BLOCK1_COLOR, label=f"Block 1 (n={len(block1)})"
    )
    ax.scatter(
        block2["t(s)"], block2["h(m)"], s=20, alpha=0.72,
        color=BLOCK2_COLOR, marker="^", label=f"Block 2 (n={len(block2)})"
    )
    t_line = np.linspace(0.0, df["t(s)"].max(), 350)
    ax.plot(
        t_line,
        effective_linear_model(t_line, v_pool, g_pool),
        "--",
        linewidth=1.55,
        color=POOLED_COLOR,
        label=fr"Pooled free-$v_{{\rm eff}}$ fit: $g={g_pool:.3f}$",
    )
    ax.plot(
        t_line,
        nominal_geometry_model(t_line, g_geom_pool),
        ":",
        linewidth=1.75,
        color=GEOMETRY_COLOR,
        label=fr"Pooled fixed-$h_0$ fit: $g={g_geom_pool:.3f}$",
    )
    ax.scatter([0], [0], marker="x", s=32, color="black", label=r"$H(0)=0$")
    ax.set_xlabel(r"$t$ (s)")
    ax.set_ylabel(r"$H$ (m)")
    ax.set_title(r"$\mathbf{a}$  Pooled model comparison", loc="left", fontsize=14.2)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    # Panel b: g values from both kinematic formulations.
    ax = axes[1]
    labels = ["Block 1", "Block 2", "Pooled"]
    x = np.arange(len(labels), dtype=float)
    offset = 0.11
    eff_g = [effective_fits[label][0][1] for label in labels]
    eff_ge = [effective_fits[label][1][1] for label in labels]
    geom_g = [geometry_fits[label][0] for label in labels]
    geom_ge = [geometry_fits[label][1] for label in labels]
    ax.errorbar(
        x - offset, eff_g, yerr=eff_ge, fmt="o", markersize=5,
        color=POOLED_COLOR, ecolor=POOLED_COLOR, capsize=3,
        label=r"Free $v_{\rm eff}$"
    )
    ax.errorbar(
        x + offset, geom_g, yerr=geom_ge, fmt="s", markersize=4.8,
        color=GEOMETRY_COLOR, ecolor=GEOMETRY_COLOR, capsize=3,
        label=r"Fixed $h_0=1$ mm"
    )
    ax.axhline(G_REF, color="black", linestyle="--", linewidth=1.0,
               label=fr"$g_{{ref}}={G_REF:.5f}$")
    ax.set_xticks(x, labels, rotation=12)
    ax.set_ylabel(r"Fitted $g$ (m/s$^2$)")
    ax.set_title(r"$\mathbf{b}$  Model and block sensitivity", loc="left", fontsize=14.2)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    # Panel c: fitted linear coefficient against geometric expectation.
    ax = axes[2]
    vvals = [effective_fits[label][0][0] for label in labels]
    verrs = [effective_fits[label][1][0] for label in labels]
    colors = [BLOCK1_COLOR, BLOCK2_COLOR, POOLED_COLOR]
    for xi, value, err, color in zip(x, vvals, verrs, colors):
        ax.errorbar([xi], [value], yerr=[err], fmt="o", color=color,
                    ecolor=color, capsize=3, markersize=5)
        ax.text(xi, value + 0.014, f"{value:.3f}", ha="center", fontsize=10.8)
    ax.axhline(
        V1_GEOMETRIC_REF_M_S,
        color=GEOMETRY_COLOR,
        linestyle="--",
        linewidth=1.25,
        label=fr"Geometric expectation: {V1_GEOMETRIC_REF_M_S:.3f} m/s",
    )
    ax.set_xticks(x, labels, rotation=12)
    ax.set_ylabel(r"Linear coefficient $v_{\rm eff}$ (m/s)")
    ax.set_title(r"$\mathbf{c}$  Effective coefficient vs geometric expectation", loc="left", fontsize=14.2)
    ax.set_ylim(0.10, max(vvals) + 0.075)
    ax.legend(frameon=False, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save_figure(fig, "figure2_kinematic_fit")
    return v_pool, g_pool


def effective_fit_residual(d, v_eff, g):
    H = d["h(m)"].to_numpy(dtype=float)
    t = d["t(s)"].to_numpy(dtype=float)
    g_classical = 2.0 * H / t**2
    return (g_classical - 2.0 * v_eff / t) - g


def figure_residuals(df, block1, block2, v_pool, g_pool):
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    x = 1.0 / np.sqrt(H)
    raw_error = 2.0 * H / t**2 - G_REF
    residual_pool = effective_fit_residual(df, v_pool, g_pool)
    raw_fit = stats.linregress(x, raw_error)
    pool_fit = stats.linregress(x, residual_pool)

    (v_b1, g_b1), _ = fit_effective_linear(block1)
    x_b1 = 1.0 / np.sqrt(block1["h(m)"].to_numpy(dtype=float))
    x_b2 = 1.0 / np.sqrt(block2["h(m)"].to_numpy(dtype=float))
    r_b1 = effective_fit_residual(block1, v_b1, g_b1)
    r_b2 = effective_fit_residual(block2, v_b1, g_b1)
    b1_fit = stats.linregress(x_b1, r_b1)
    pred_b2 = b1_fit.slope * x_b2 + b1_fit.intercept
    ss_res = np.sum((r_b2 - pred_b2) ** 2)
    ss_tot = np.sum((r_b2 - np.mean(r_b2)) ** 2)
    r2_oos = 1.0 - ss_res / ss_tot

    fig, axes = plt.subplots(1, 3, figsize=(15.4, 5.0))
    x_line = np.linspace(x.min(), x.max(), 300)

    axes[0].scatter(x_b1, raw_error[:len(block1)], s=14, alpha=0.66,
                    color=BLOCK1_COLOR, label="Block 1")
    axes[0].scatter(x_b2, raw_error[len(block1):], s=17, alpha=0.70,
                    color=BLOCK2_COLOR, marker="^", label="Block 2")
    axes[0].plot(x_line, raw_fit.slope*x_line + raw_fit.intercept,
                 "--", linewidth=1.4, color=POOLED_COLOR, label="Pooled OLS")
    axes[0].set_title(fr"$\mathbf{{a}}$  Raw error ($R^2={raw_fit.rvalue**2:.2f}$)",
                      loc="left", fontsize=14.2)
    axes[0].set_xlabel(r"$1/\sqrt{H}$ (m$^{-1/2}$)")
    axes[0].set_ylabel(r"$g_{\rm classical}-g_{\rm ref}$ (m/s$^2$)")
    axes[0].legend(frameon=False, loc="upper left")

    axes[1].scatter(x_b1, residual_pool[:len(block1)], s=14, alpha=0.66,
                    color=BLOCK1_COLOR)
    axes[1].scatter(x_b2, residual_pool[len(block1):], s=17, alpha=0.70,
                    color=BLOCK2_COLOR, marker="^")
    axes[1].plot(x_line, pool_fit.slope*x_line + pool_fit.intercept,
                 "--", linewidth=1.4, color=POOLED_COLOR)
    axes[1].set_title(
        fr"$\mathbf{{b}}$  Pooled effective-fit residual ($R^2={pool_fit.rvalue**2:.2f}$)",
        loc="left", fontsize=12.2
    )
    axes[1].set_xlabel(r"$1/\sqrt{H}$ (m$^{-1/2}$)")
    axes[1].set_ylabel(r"Residual (m/s$^2$)")

    axes[2].scatter(x_b1, r_b1, s=14, alpha=0.66, color=BLOCK1_COLOR,
                    label="Block 1 fit data")
    axes[2].scatter(x_b2, r_b2, s=17, alpha=0.70, color=BLOCK2_COLOR,
                    marker="^", label="Block 2 test data")
    axes[2].plot(x_line, b1_fit.slope*x_line + b1_fit.intercept,
                 "--", linewidth=1.4, color=BLOCK1_COLOR,
                 label="Block 1 relation")
    axes[2].set_title(
        fr"$\mathbf{{c}}$  Block 1 fit evaluated on Block 2 ($R^2_{{\rm OOS}}={r2_oos:.2f}$)",
        loc="left", fontsize=12.2
    )
    axes[2].set_xlabel(r"$1/\sqrt{H}$ (m$^{-1/2}$)")
    axes[2].set_ylabel(r"Residual computed with Block 1 fit (m/s$^2$)")
    axes[2].legend(frameon=False, loc="upper right")

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_figure(fig, "figure3_residuals")


def cross_block_mae(train_df, test_df, include_mechanism_feature: bool) -> float:
    X_train, y_train = build_features(train_df, include_mechanism_feature)
    X_test, _ = build_features(test_df, include_mechanism_feature)
    selected = select_best_model(X_train, y_train)
    y_pred = selected.estimator.predict(X_test)
    g_hat = test_df["g_classical"].to_numpy(dtype=float) - y_pred
    return mae(G_REF, g_hat)


def figure_circularity(df, block1, block2):
    H = df["h(m)"].to_numpy(dtype=float)
    t = df["t(s)"].to_numpy(dtype=float)
    g_classical = 2.0 * H / t**2
    target = g_classical - G_REF
    closed_form = 2.0 * H / t**2 - G_REF

    mae_a_12 = cross_block_mae(block1, block2, False)
    mae_b_12 = cross_block_mae(block1, block2, True)
    mae_a_21 = cross_block_mae(block2, block1, False)
    mae_b_21 = cross_block_mae(block2, block1, True)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.9))
    axes[0].scatter(closed_form, target, s=14, alpha=0.60, color=BLOCK1_COLOR)
    limits = [min(closed_form.min(), target.min()), max(closed_form.max(), target.max())]
    axes[0].plot(limits, limits, linewidth=1.2, color=POOLED_COLOR, label="Identity")
    axes[0].set_xlabel(r"$2H_m/t_m^2-g_{\rm ref}$ (m/s$^2$; closed form)")
    axes[0].set_ylabel(r"$y_i$ (m/s$^2$; training target)")
    axes[0].set_title(r"$\mathbf{a}$  Exact target reconstruction", loc="left", fontsize=14.2)
    axes[0].legend(frameon=False, loc="upper left")

    directions = [r"Block 1$\to$Block 2", r"Block 2$\to$Block 1"]
    xpos = np.arange(len(directions), dtype=float)
    width = 0.34
    values_a = [mae_a_12, mae_a_21]
    values_b = [mae_b_12, mae_b_21]
    bars_a = axes[1].bar(xpos - width/2, values_a, width, color=BLOCK1_COLOR,
                         alpha=0.85, label=r"Model A: $(H,t)$")
    bars_b = axes[1].bar(xpos + width/2, values_b, width, color=BLOCK2_COLOR,
                         alpha=0.85, label=r"Model B: $(H,t,1/\sqrt{H})$")
    axes[1].set_xticks(xpos, directions)
    axes[1].set_ylabel(r"Test MAE of reconstructed $g$ (m/s$^2$)")
    axes[1].set_title(r"$\mathbf{b}$  Diagnostic cross-block errors", loc="left", fontsize=14.2)
    axes[1].legend(frameon=False, loc="upper left")
    axes[1].set_ylim(0.0, max(values_a + values_b) * 1.30)
    for bars in (bars_a, bars_b):
        for bar in bars:
            value = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2, value + 0.012,
                         f"{value:.3f}", ha="center", va="bottom", fontsize=10.8)
    axes[1].text(
        0.98, 0.97, "Exact closed-form baseline: MAE = 0",
        transform=axes[1].transAxes, ha="right", va="top", fontsize=10.4,
    )

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_figure(fig, "figure4_circularity")


def main() -> None:
    df = add_classical_estimate(load_data())
    block1, block2 = split_blocks(df)
    v_pool, g_pool = figure_kinematic_fit(df, block1, block2)
    figure_residuals(df, block1, block2, v_pool, g_pool)
    figure_circularity(df, block1, block2)
    print("Saved manuscript Figures 2--4 as PDF and PNG.")


if __name__ == "__main__":
    main()
