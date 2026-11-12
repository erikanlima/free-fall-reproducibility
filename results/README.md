# Numerical outputs

The CSV and JSON files in this directory were generated from `data/free_fall_measurements.csv` by scripts 00--04 and 07.

- `fit_configurations.json`: physical-fit and machine-learning configuration
- `h1_fit_results.csv`: classical errors, effective-linear fits, and nominal-geometry sensitivity fits
- `h2_mechanism_results.csv`: residual regressions and cross-block sensitivity
- `h2_delta_stability.csv`: geometry-constrained timing-offset fits (g, delta) for Block 1, Block 2, and pooled data
- `h2_delta_parameter_correlations.csv`: g-delta correlation matrices
- `ml_pipeline_results.csv`: selected models, hyperparameters, and cross-block metrics
- `diagnostics_results.csv`: ablation and redundant-feature permutation diagnostics
- `drag_buoyancy_bound.csv`: bias in the fixed-geometry g caused by quadratic drag and buoyancy

The H1 results report the measured trigger geometry (`h0_nominal_m = 0.007`), the corresponding geometric entry velocity and its reading uncertainty, the fitted-to-geometric velocity ratio, the effective pre-trigger distance v_eff^2/(2g) with its covariance-propagated uncertainty, and the one-parameter fixed-geometry result for `g`.

`ml_pipeline_results.csv` includes mean-residual baselines in both cross-block directions and the exact zero-error analytical baseline.
