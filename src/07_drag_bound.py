#!/usr/bin/env python3
"""Upper bound on the bias in g from quadratic air drag and buoyancy.

The steel sphere is released from rest h0 above photogate 1. Its trajectory
is integrated with quadratic drag and buoyancy, H(t) is evaluated at the
recorded transit times, and the drag-free geometry-constrained model
H = sqrt(2*g*h0)*t + 0.5*g*t^2 is fitted to the simulated values. The
difference between the fitted g and G_REF is the bias introduced by drag
and buoyancy alone.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit

from data_utils import G_REF, H0_NOMINAL_M, SPHERE_DIAMETER_M, load_data, output_path

RHO_STEEL = 7850.0  # kg m^-3
C_D_VALUES = (0.40, 0.50)
RHO_AIR_VALUES = (1.10, 1.20)  # kg m^-3


def fixed_geometry_model(t, g):
    return np.sqrt(2.0 * g * H0_NOMINAL_M) * t + 0.5 * g * t**2


def simulated_separation(t_recorded, c_d, rho_air):
    radius = 0.5 * SPHERE_DIAMETER_M
    mass = RHO_STEEL * 4.0 / 3.0 * np.pi * radius**3
    area = np.pi * radius**2
    k = 0.5 * rho_air * c_d * area / mass
    g_eff = G_REF * (1.0 - rho_air / RHO_STEEL)

    def rhs(_, state):
        return [state[1], g_eff - k * state[1] ** 2]

    def reach_gate(_, state):
        return state[0] - H0_NOMINAL_M

    sol = solve_ivp(rhs, [0.0, 1.0], [0.0, 0.0], events=reach_gate,
                    rtol=1e-12, atol=1e-14, dense_output=True)
    t_gate1 = sol.t_events[0][0]
    return np.array([sol.sol(t_gate1 + ti)[0] - H0_NOMINAL_M for ti in t_recorded])


def main() -> None:
    df = load_data()
    t = df["t(s)"].to_numpy(dtype=float)
    rows = []
    for c_d in C_D_VALUES:
        for rho_air in RHO_AIR_VALUES:
            H_sim = simulated_separation(t, c_d, rho_air)
            (g_fit,), _ = curve_fit(fixed_geometry_model, t, H_sim, p0=[9.7])
            rows.append({"C_D": c_d, "rho_air_kg_m3": rho_air,
                         "g_fit_m_s2": g_fit, "bias_g_m_s2": g_fit - G_REF})
            print(f"C_D={c_d:.2f}, rho_air={rho_air:.2f}: bias in g = {g_fit - G_REF:+.4f} m/s^2")
    path = output_path("results", "drag_buoyancy_bound.csv")
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
