#!/usr/bin/env python3
"""Generate figures 1-3 of the manuscript from data and results/.

Figure 1: apparatus schematic. Figure 2: kinematic fits (data from
data/free_fall_measurements.csv; parameters from results/h1_fit_results.csv).
Figure 3: target circularity (data; MAEs from results/ml_pipeline_results.csv).
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

from data_utils import G_REF, H0_NOMINAL_M, H0_READING_UNCERTAINTY_M, load_data, output_path

OUT = str(output_path("figures", "placeholder").parent)
H0 = H0_NOMINAL_M
C1, C2, CR, CP, CF = "#3a70a1", "#5c8c59", "#b33a47", "#5c4a8a", "#222222"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "xtick.direction": "out", "ytick.direction": "out", "legend.frameon": False,
    "mathtext.default": "it", "pdf.fonttype": 42, "savefig.dpi": 600,
})
U_ACC = r"m s$^{-2}$"
U_VEL = r"m s$^{-1}$"
GREF = r"$g_{\mathrm{ref}}$"


def panel_label(ax, s):
    ax.text(-0.13, 1.04, s, transform=ax.transAxes, fontsize=13, fontweight="bold", va="bottom")


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- figure 1
fig, ax = plt.subplots(figsize=(7.2, 4.9))
ax.set_xlim(0, 10.4); ax.set_ylim(0, 6.4); ax.set_aspect("equal"); ax.axis("off")
gray, edge = "#e3e3e3", "#3a3a3a"
ax.add_patch(Rectangle((0.2, 0.55), 9.6, 0.22, fc="#d0d0d0", ec=edge, lw=1))          # base
ax.add_patch(Rectangle((0.6, 0.77), 0.42, 5.3, fc=gray, ec=edge, lw=1))              # rod
ax.add_patch(Rectangle((0.95, 5.8), 2.85, 0.36, fc=gray, ec=edge, lw=1))                # arm
ax.add_patch(Rectangle((2.75, 5.62), 0.5, 0.18, fc="#8fc5d9", ec=edge, lw=0.8))       # magnet pole
ax.annotate("Electromagnet", xy=(3.85, 5.98), xytext=(4.6, 5.98), va="center", fontsize=11,
            arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2))
xc, ysph, rs = 3.0, 4.95, 0.25
ax.add_patch(Circle((xc, ysph), rs, fc="#d9d9d9", ec=edge, lw=1.2))
ax.text(xc + 0.4, ysph, "Steel sphere\n(diameter 6.35 mm)", va="center", fontsize=10.5)
yg1, yg2 = 4.0, 1.55
ax.plot([xc, xc], [ysph - rs, 1.0], ls=(0, (3, 3)), color="#666", lw=0.9)
for yg, col, lab in [(yg1, "#7e78c7", "Photogate 1"), (yg2, "#62b66a", "Photogate 2")]:
    for x0 in (1.75, 3.85):
        ax.add_patch(FancyBboxPatch((x0, yg - 0.09), 0.62, 0.18, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=col, ec=edge, lw=1))
    ax.plot([2.37, 3.85], [yg, yg], color=edge, lw=1)
    ax.add_patch(Rectangle((1.02, yg - 0.035), 0.73, 0.07, fc="#bdbdbd", ec=edge, lw=0.6))
    ax.text(4.6, yg, lab, va="center", fontsize=11)
# h0 and H dimension arrows (left of the axis of fall)
xa = 2.6
ax.annotate("", xy=(xa, ysph - rs), xytext=(xa, yg1), arrowprops=dict(arrowstyle="<->", lw=1.3))
ax.text(xa - 0.12, (ysph - rs + yg1) / 2, r"$h_0 = 7\ \mathrm{mm}$", ha="right", va="center", fontsize=11)
ax.annotate("", xy=(xa, yg1), xytext=(xa, yg2), arrowprops=dict(arrowstyle="<->", lw=1.3))
ax.text(xa - 0.12, (yg1 + yg2) / 2, r"$H$", ha="right", va="center", fontsize=14)
ax.annotate("", xy=(3.55, 2.3), xytext=(3.55, 3.3), arrowprops=dict(arrowstyle="-|>", lw=1.6))
ax.text(3.68, 2.8, r"$g$", va="center", fontsize=14)
ax.plot([ysph * 0 + 3.0 - 0.25, 3.25], [ysph + 0.42] * 2, alpha=0)  # spacer
# timer and wiring
ax.add_patch(FancyBboxPatch((7.6, 0.95), 2.0, 1.0, boxstyle="round,pad=0,rounding_size=0.12",
                            fc=gray, ec=edge, lw=1.3))
ax.add_patch(FancyBboxPatch((7.9, 1.25), 1.4, 0.4, boxstyle="round,pad=0,rounding_size=0.05", fc="#111", ec="#111"))
ax.text(8.6, 1.45, "t (s)", color="w", ha="center", va="center", family="DejaVu Sans Mono", fontsize=11)
ax.text(8.6, 2.08, "Digital timer", ha="center", fontsize=11)
ax.plot([4.47, 7.6], [yg1, 1.75], color="#b5b5b5", lw=1.1)
ax.plot([4.47, 7.6], [yg2, 1.25], color="#b5b5b5", lw=1.1)
box = dict(boxstyle="round,pad=0.35", fc="w", ec="#777", lw=1)
ax.text(6.4, 4.75, "START: lower surface of the sphere\nfirst interrupts the photogate 1 beam", fontsize=9.5, bbox=box)
ax.text(6.4, 2.55, "STOP: lower surface of the sphere\nfirst interrupts the photogate 2 beam", fontsize=9.5, bbox=box)
ax.text(6.4, 3.65, r"one release $\rightarrow$ one recorded transit time $t$", fontsize=10.5, fontweight="bold")
ax.text(0.25, 0.25, "Schematic not to scale", fontsize=9, style="italic")
save(fig, "figure1_apparatus")

# ---------------------------------------------------------------- figure 2
df = load_data()
blk = df["block"].astype(str).str.extract(r"(\d)")[0].astype(int).to_numpy()
H, t = df["h(m)"].to_numpy(float), df["t(s)"].to_numpy(float)
h1 = pd.read_csv(output_path("results", "h1_fit_results.csv")).set_index("sample")
key = {"B1": "Block 1", "B2": "Block 2", "P": "Pooled"}
free = {k: (h1.loc[v, "v_effective_m_s"], h1.loc[v, "v_effective_se_m_s"],
            h1.loc[v, "g_effective_fit_m_s2"], h1.loc[v, "g_effective_fit_se_m_s2"]) for k, v in key.items()}
fixed = {k: (h1.loc[v, "g_nominal_geometry_fit_m_s2"], h1.loc[v, "g_nominal_geometry_fit_se_m_s2"])
         for k, v in key.items()}

fig, axs = plt.subplots(1, 3, figsize=(14.5, 4.3), gridspec_kw=dict(width_ratios=[1.25, 1, 1], wspace=0.32))
ax = axs[0]
ax.scatter(t[blk == 1], H[blk == 1], s=16, color=C1, alpha=0.75, lw=0, label="Block 1 ($n$ = 75)")
ax.scatter(t[blk == 2], H[blk == 2], s=18, marker="^", color=C2, alpha=0.8, lw=0, label="Block 2 ($n$ = 44)")
tt = np.linspace(0, 0.37, 300)
v, _, g, _ = free["P"]
ax.plot(tt, v * tt + 0.5 * g * tt**2, ls="--", color=CR, lw=1.4, label=f"Free-$v_1$ fit: $g$ = {g:.3f} {U_ACC}")
gf = fixed["P"][0]
ax.plot(tt, np.sqrt(2 * gf * H0) * tt + 0.5 * gf * tt**2, ls=":", color=CP, lw=1.8,
        label=f"Fixed-$h_0$ fit: $g$ = {gf:.3f} {U_ACC}")
ax.scatter([0], [0], marker="x", color="k", s=30, zorder=5, label="Model constraint $H(0) = 0$")
ax.set_xlabel("Recorded transit time, $t$ (s)"); ax.set_ylabel("Photogate separation, $H$ (m)")
ax.set_xlim(-0.01, 0.38); ax.set_ylim(-0.02, 0.80)
ax.legend(loc="upper left", fontsize=9.5, handletextpad=0.4)
panel_label(ax, "a")

ax = axs[1]
xs = np.arange(3); keys = ["B1", "B2", "P"]
ax.axhline(G_REF, color="k", ls="--", lw=1, label=f"{GREF} = {G_REF:.5f} {U_ACC}")
ax.errorbar(xs - 0.12, [free[k][2] for k in keys], [free[k][3] for k in keys], fmt="o", color=CR, ms=6,
            capsize=3.5, lw=1.4, label="Free $v_1$")
ax.errorbar(xs + 0.12, [fixed[k][0] for k in keys], [fixed[k][1] for k in keys], fmt="s", color=CP, ms=6,
            capsize=3.5, lw=1.4, label="Fixed $h_0$ = 7 mm")
ax.set_xticks(xs, ["Block 1", "Block 2", "Pooled"]); ax.set_xlim(-0.5, 2.5)
ax.set_ylim(9.42, 10.30); ax.set_ylabel(f"Fitted $g$ ({U_ACC})")
ax.legend(loc="upper left", fontsize=9.5, handletextpad=0.4)
panel_label(ax, "b")

ax = axs[2]
vg = np.sqrt(2 * G_REF * H0)
dvg = 0.5 * vg * H0_READING_UNCERTAINTY_M / H0
ax.axhspan(vg - dvg, vg + dvg, color=CP, alpha=0.10, lw=0,
           label=r"$\pm$" + f"{dvg:.4f} " + U_VEL + r" ($\Delta h_0$ = 0.5 mm)")
ax.axhline(vg, color=CP, ls="--", lw=1.2,
           label=r"$\sqrt{2g_{\mathrm{ref}}h_0}$ = " + f"{vg:.4f} {U_VEL}")
for x, k, c in zip(xs, keys, [C1, C2, CR]):
    ax.errorbar(x, free[k][0], free[k][1], fmt="o", color=c, ms=6, capsize=3.5, lw=1.4)
    ax.annotate(f"{free[k][0]:.4f}", (x, free[k][0]), xytext=(9, 9), textcoords="offset points",
                va="bottom", fontsize=9.5)
ax.set_xticks(xs, ["Block 1", "Block 2", "Pooled"]); ax.set_xlim(-0.4, 2.7)
ax.set_ylim(0.31, 0.405); ax.set_ylabel(f"Free-fit entry velocity, $v_1$ ({U_VEL})")
ax.legend(loc="lower right", fontsize=9, handletextpad=0.4)
panel_label(ax, "c")
save(fig, "figure2_kinematic_fit")

# ---------------------------------------------------------------- figure 3
y = 2 * H / t**2 - G_REF
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.3), gridspec_kw=dict(wspace=0.3))
ax = axs[0]
lim = (1.0, 17.0)
ax.plot(lim, lim, color=CR, lw=1.4, label="Identity", zorder=1)
ax.scatter(y[blk == 1], y[blk == 1], s=16, color=C1, alpha=0.75, lw=0, label="Block 1", zorder=2)
ax.scatter(y[blk == 2], y[blk == 2], s=18, marker="^", color=C2, alpha=0.8, lw=0, label="Block 2", zorder=2)
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel(r"Closed form, $2H_m/t_m^2 - g_{\mathrm{ref}}$ (" + U_ACC + ")")
ax.set_ylabel(r"Learning target, $y_i$ (" + U_ACC + ")")
ax.legend(loc="upper left", fontsize=9.5)
panel_label(ax, "a")

ax = axs[1]
ml = pd.read_csv(output_path("results", "ml_pipeline_results.csv")).set_index("configuration")
mae = {m: tuple(ml.loc[f"Model {m}: Block {a} -> Block {b}", "test_mae_g_m_s2"] for a, b in ((1, 2), (2, 1)))
       for m in "AB"}
xs = np.arange(2); w = 0.36
for off, k, c, lab in [(-w / 2, "A", C1, r"Model A: $(H_m, t_m)$"),
                       (w / 2, "B", C2, r"Model B: $(H_m, t_m, 1/\sqrt{H_m})$")]:
    bars = ax.bar(xs + off, mae[k], w, color=c, label=lab)
    for b, v in zip(bars, mae[k]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f}", ha="center", va="bottom", fontsize=9.5)
ax.set_xticks(xs, [r"Block 1 $\rightarrow$ Block 2", r"Block 2 $\rightarrow$ Block 1"])
ax.set_ylim(0, 0.56); ax.set_ylabel(f"Test MAE of reconstructed $g$ ({U_ACC})")
ax.plot([], [], ls="none", label="Exact analytical expression: MAE = 0")
ax.legend(loc="upper left", fontsize=9.5)
panel_label(ax, "b")
save(fig, "figure3_circularity")
print(f"Saved figures 1-3 to {OUT}")
