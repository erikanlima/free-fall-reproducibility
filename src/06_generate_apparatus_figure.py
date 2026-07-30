#!/usr/bin/env python3
"""Generate the apparatus schematic used as Figure 1.

The diagram is intentionally not to scale. The nominal h0 arrow marks the
approximately 1 mm gap from the lower surface of the sphere to the beam level
of photogate 1. Because timing starts at the onset of beam interruption, the
6.35 mm sphere diameter is not added to h0.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from data_utils import output_path


def save(fig, stem: str) -> None:
    for extension in ("pdf", "png"):
        fig.savefig(output_path("figures", f"{stem}.{extension}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    fig, ax = plt.subplots(figsize=(8.7, 6.1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Support and electromagnet.
    ax.add_patch(Rectangle((0.65, 0.35), 8.6, 0.28, facecolor="#D0D0D0",
                           edgecolor="#555555", linewidth=1.0))
    ax.add_patch(Rectangle((1.35, 0.62), 0.48, 6.1, facecolor="#E1E1E1",
                           edgecolor="#444444", linewidth=1.0))
    ax.add_patch(Rectangle((1.72, 6.7), 2.35, 0.42, facecolor="#E6E6E6",
                           edgecolor="#333333", linewidth=1.0))
    ax.add_patch(Rectangle((2.93, 6.51), 0.55, 0.20, facecolor="#8EC6D9",
                           edgecolor="#777777", linewidth=0.8))
    ax.annotate("Electromagnet", xy=(4.08, 6.91), xytext=(5.05, 6.91),
                arrowprops=dict(arrowstyle="-|>", lw=1.2), va="center", fontsize=11)

    # Sphere and release geometry.
    sphere_x = 3.2
    sphere_r = 0.25
    beam1_y = 4.8
    gap_draw = 0.36  # enlarged for readability; not to scale
    sphere_cy = beam1_y + gap_draw + sphere_r
    ax.add_patch(Circle((sphere_x, sphere_cy), sphere_r, facecolor="#D8D8D8",
                        edgecolor="#333333", linewidth=1.0))
    ax.text(3.55, sphere_cy, "Steel sphere", va="center", fontsize=11)

    # Diameter annotation.
    ax.annotate("", xy=(sphere_x - sphere_r, sphere_cy + 0.46),
                xytext=(sphere_x + sphere_r, sphere_cy + 0.46),
                arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax.text(sphere_x, sphere_cy + 0.60, "diameter 6.35 mm", ha="center", fontsize=9)

    # Photogates and beams.
    beam2_y = 1.95
    for y, color, label in [(beam1_y, "#7C79C8", "Photogate 1"),
                            (beam2_y, "#62B66A", "Photogate 2")]:
        ax.add_patch(FancyBboxPatch((1.70, y - 0.09), 0.65, 0.18,
                                    boxstyle="round,pad=0.02,rounding_size=0.07",
                                    facecolor=color, edgecolor="#333333", linewidth=0.9))
        ax.add_patch(FancyBboxPatch((4.05, y - 0.09), 0.65, 0.18,
                                    boxstyle="round,pad=0.02,rounding_size=0.07",
                                    facecolor=color, edgecolor="#333333", linewidth=0.9))
        ax.plot([2.35, 4.05], [y, y], color="#333333", linewidth=1.0)
        ax.annotate(label, xy=(4.55, y + 0.03), xytext=(5.35, y + 0.55 if y==beam1_y else y-0.65),
                    arrowprops=dict(arrowstyle="-|>", lw=1.0), fontsize=11,
                    va="center")

    # Falling path and gravity.
    ax.plot([sphere_x, sphere_x], [sphere_cy - sphere_r, 1.3], linestyle=(0, (4, 4)),
            color="#666666", linewidth=1.0)
    ax.annotate("", xy=(3.75, 2.45), xytext=(3.75, 3.55),
                arrowprops=dict(arrowstyle="-|>", lw=1.7))
    ax.text(3.92, 3.0, "$g$", fontsize=13, va="center")

    # Correct h0: lower sphere surface to beam 1.
    lower_surface_y = sphere_cy - sphere_r
    ax.annotate("", xy=(2.78, lower_surface_y), xytext=(2.78, beam1_y),
                arrowprops=dict(arrowstyle="<->", lw=1.3))
    ax.text(2.60, (lower_surface_y + beam1_y)/2,
            "$h_0\\approx1$ mm", ha="right", va="center", fontsize=11)
    ax.text(2.60, beam1_y - 0.32, "onset trigger", ha="right", fontsize=8.5)

    # H is beam-to-beam separation.
    ax.annotate("", xy=(2.78, beam1_y), xytext=(2.78, beam2_y),
                arrowprops=dict(arrowstyle="<->", lw=1.3))
    ax.text(2.60, (beam1_y + beam2_y)/2, "$H$", ha="right", va="center", fontsize=13)

    # Timer and cables.
    timer = FancyBboxPatch((6.75, 0.72), 2.05, 0.95,
                           boxstyle="round,pad=0.08,rounding_size=0.14",
                           facecolor="#E2E2E2", edgecolor="#333333", linewidth=1.2)
    ax.add_patch(timer)
    ax.add_patch(FancyBboxPatch((7.15, 1.02), 1.25, 0.35,
                                boxstyle="round,pad=0.03,rounding_size=0.06",
                                facecolor="#111111", edgecolor="#111111"))
    ax.text(7.78, 1.20, "0.050 s", color="white", ha="center", va="center",
            family="monospace", fontsize=12)
    ax.text(7.78, 1.82, "Digital timer", ha="center", fontsize=11)
    ax.plot([4.70, 6.76], [beam1_y, 1.45], color="#B5B5B5", linewidth=1.2)
    ax.plot([4.70, 6.76], [beam2_y, 1.00], color="#B5B5B5", linewidth=1.2)

    # Explicit timing logic.
    ax.text(5.20, 4.25, "START: lower surface first interrupts photogate 1 beam",
            fontsize=9.2, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#777777"))
    ax.text(5.20, 2.55, "STOP: lower surface first interrupts photogate 2 beam",
            fontsize=9.2, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#777777"))
    ax.text(5.20, 3.45, "one release $\\rightarrow$ one transit time $t$",
            fontsize=9.5, fontweight="bold")

    ax.text(0.72, 0.10, "Schematic not to scale", fontsize=8.5, style="italic")
    fig.tight_layout()
    save(fig, "figure1_apparatus")
    print("Saved Figure 1 as PDF and PNG.")


if __name__ == "__main__":
    main()
