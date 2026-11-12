"""Write a machine-readable record of every analysis configuration."""

from __future__ import annotations

import json

from data_utils import (
    G_REF,
    BLOCK_BOUNDARY,
    H0_NOMINAL_M,
    H0_READING_UNCERTAINTY_M,
    SPHERE_DIAMETER_M,
    TRIGGER_EDGE,
    V1_GEOMETRIC_REF_M_S,
    output_path,
)
from ml_utils import RANDOM_STATE

CONFIGURATIONS = {
    "constants": {
        "g_ref_m_s2": G_REF,
        "g_ref_source": (
            "WGS84 Somigliana formula with free-air correction; theoretical "
            "geodetic estimate, not an independent gravimetric measurement"
        ),
        "block_boundary_row_index": BLOCK_BOUNDARY,
        "sphere_diameter_m": SPHERE_DIAMETER_M,
        "h0_nominal_m": H0_NOMINAL_M,
        "h0_reading_uncertainty_m": H0_READING_UNCERTAINTY_M,
        "photogate_trigger_definition": TRIGGER_EDGE,
        "v1_geometry_ref_m_s": V1_GEOMETRIC_REF_M_S,
        "block1_n": 75,
        "block2_n": 44,
        "acquisition_structure": (
            "One experimental campaign with the same apparatus, organized "
            "as two sequential blocks. Block 1 contains 75 releases; H was "
            "then reset to a lower value and Block 2 contains 44 releases."
        ),
        "random_state": RANDOM_STATE,
    },
    "H1_effective_linear_fit": {
        "script": "01_h1_constrained_fit.py",
        "model": "H = v_effective*t + 0.5*g*t^2",
        "boundary_condition": "H=0 at the beginning of the physical interval",
        "method": "scipy.optimize.curve_fit; Levenberg-Marquardt; unbounded",
        "initial_guess_p0": {"v_effective_m_s": 0.4, "g_m_s2": 9.8},
        "sigma": "not supplied",
        "absolute_sigma": False,
        "uncertainty_estimation": "sqrt(diag(pcov))",
        "fits": ["Block 1", "Block 2", "Pooled"],
        "primary_reported_fit": "Pooled; block fits assess acquisition-block sensitivity",
        "interpretation": (
            "The fitted linear coefficient is reported as v_effective, not as a "
            "direct measurement of entry velocity. The measured 7 mm geometry predicts "
            "v1=sqrt(2*g_ref*h0), which is used as an independent physical check."
        ),
    },
    "H1_nominal_geometry_sensitivity_fit": {
        "script": "01_h1_constrained_fit.py",
        "model": "H = sqrt(2*g*h0)*t + 0.5*g*t^2 with h0 fixed at 0.007 m",
        "free_parameter": "g",
        "method": "scipy.optimize.curve_fit; bounded to g>0",
        "initial_guess_p0": {"g_m_s2": 9.8},
        "uncertainty_estimation": "sqrt(diag(pcov))",
        "fits": ["Block 1", "Block 2", "Pooled"],
        "interpretation": (
            "The 7 mm clearance was set with a ruler graduated in 1 mm; a 0.5 mm "
            "half-division reading uncertainty is adopted. Parallax, alignment, beam "
            "position, and trigger threshold were not independently characterized. The fit "
            "tests whether the measured geometry alone can explain the observations."
        ),
    },
    "H2_delta_model": {
        "script": "02_h2_mechanism_test.py",
        "measurement_relation": "t_m = t_true + delta",
        "model": "H = sqrt(2*g*h0)*(t_m-delta) + 0.5*g*(t_m-delta)^2 with h0 = 0.007 m",
        "free_parameters": ["g", "delta"],
        "boundary_condition": "H=0 at t_true=0, corresponding to t_m=delta",
        "method": "scipy.optimize.curve_fit; Levenberg-Marquardt; unbounded",
        "initial_guess_p0": {"g_m_s2": 9.6, "delta_s": 0.0},
        "sigma": "not supplied",
        "absolute_sigma": False,
        "uncertainty_estimation": "sqrt(diag(pcov)); full correlation matrix saved",
        "fits": ["Block 1", "Block 2", "Pooled"],
        "identifiability_note": (
            "Block-to-block stability and the local g-delta correlation are used as "
            "practical identifiability diagnostics. Strong correlation is not, by "
            "itself, evidence of structural non-identifiability."
        ),
    },
    "drag_buoyancy_bound": {
        "script": "07_drag_bound.py",
        "model": "dv/dt = g_ref*(1 - rho_air/rho_steel) - k*v^2, k = rho_air*C_D*A/(2m)",
        "sphere": {"diameter_m": 0.00635, "density_kg_m3": 7850.0},
        "C_D": [0.40, 0.50],
        "rho_air_kg_m3": [1.10, 1.20],
        "procedure": (
            "Integrate from rest h0 above photogate 1, evaluate H at the recorded "
            "transit times, and fit the drag-free fixed-h0 model to obtain the bias in g"
        ),
    },
    "H2_mechanism_regression": {
        "script": "02_h2_mechanism_test.py",
        "model": "OLS regression of raw error or H1-corrected residual vs 1/sqrt(H)",
        "method": "scipy.stats.linregress",
        "analyses": [
            "Pooled raw error",
            "Pooled H1-corrected residual",
            "Block 1 fit applied out of sample to Block 2 corrected residual",
        ],
    },
    "ML_model_selection": {
        "scripts": ["03_ml_pipeline_and_circularity.py", "04_diagnostics.py"],
        "cross_validation": "LeaveOneOut within the training acquisition block",
        "selection_metric": "aggregate RMSE of all out-of-fold predictions",
        "selection_implementation": "ParameterGrid + cross_val_predict",
        "candidates": {
            "ridge": {
                "estimator": "StandardScaler -> Ridge",
                "grid": {"alpha": [0.1, 1.0, 10.0]},
            },
            "random_forest": {
                "estimator": "RandomForestRegressor",
                "grid": {
                    "n_estimators": [50, 100],
                    "max_depth": [2, 3, 4],
                },
                "fixed": {"random_state": RANDOM_STATE},
            },
            "gradient_boosting": {
                "estimator": "GradientBoostingRegressor",
                "grid": {
                    "n_estimators": [50, 100],
                    "max_depth": [2, 3],
                    "learning_rate": [0.05, 0.1],
                },
                "fixed": {"random_state": RANDOM_STATE},
            },
        },
        "directions": [
            "Model A: Block 1 -> Block 2",
            "Model A: Block 2 -> Block 1",
            "Model B: Block 1 -> Block 2",
            "Model B: Block 2 -> Block 1",
        ],
        "output": "results/ml_pipeline_results.csv",
    },
    "permutation_test": {
        "script": "04_diagnostics.py",
        "n_permutations": 1000,
        "random_state": RANDOM_STATE,
        "procedure": (
            "Permute 1/sqrt(H) across the Block 2 test block, retain H and t, "
            "and evaluate the already fitted Model B without retraining"
        ),
        "reported_statistics": [
            "original MAE",
            "mean and standard deviation of permuted MAE",
            "fraction of permutations with worse MAE",
            "one-sided empirical p-value",
        ],
    },
}


def main() -> None:
    path = output_path("results", "fit_configurations.json")
    path.write_text(json.dumps(CONFIGURATIONS, indent=2), encoding="utf-8")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
