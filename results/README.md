# Numerical outputs

The CSV and JSON files in this directory were generated from `data/free_fall_measurements.csv` by scripts 00--04.

- `fit_configurations.json`: physical-fit and machine-learning configuration
- `h1_fit_results.csv`: classical errors, effective-linear fits, and nominal-geometry sensitivity fits
- `h2_mechanism_results.csv`: residual regressions and cross-block sensitivity
- `h2_delta_stability.csv`: timing-offset fit parameters and uncertainties
- `h2_delta_parameter_correlations.csv`: full parameter-correlation outputs
- `ml_pipeline_results.csv`: selected models, hyperparameters, and cross-block metrics
- `diagnostics_results.csv`: ablation and redundant-feature permutation diagnostics

The H1 results report the nominal trigger geometry (`h0_nominal_m = 0.001`), the corresponding geometric entry velocity, the fitted-to-geometric velocity ratio, the effective height implied by each fitted linear coefficient, and the one-parameter nominal-geometry sensitivity result for `g`.

`ml_pipeline_results.csv` includes mean-residual baselines in both cross-block directions and the exact zero-error analytical baseline.
