# Changelog

## 2.0.0 (2026-11-12)

### Corrected
- Release geometry: the lower surface of the sphere was positioned 7 mm above the photogate-1 beam, set with a ruler graduated in 1 mm. Version 1.0.0 incorrectly stated an approximately 1 mm clearance. `H0_NOMINAL_M` is now 0.007 m, with a 0.5 mm reading uncertainty (`H0_READING_UNCERTAINTY_M`).
- Reference gravity: `G_REF` = 9.78355 m s^-2 (WGS84 Somigliana relation with free-air correction for 15.6 S and 165 m). Version 1.0.0 used 9.78326 m s^-2. The machine-learning metrics are unchanged to numerical precision.
- Author name: Auiri Brito.

### Changed
- Timing-offset analysis (`02_h2_mechanism_test.py`): the three-parameter (v1, g, delta) model was replaced by the geometry-constrained model H = sqrt(2 g h0)(t - delta) + g (t - delta)^2 / 2, fitted for Block 1, Block 2, and pooled data.
- `01_h1_constrained_fit.py`: the effective pre-trigger distance is now v_eff^2/(2g), using the fitted g, with a covariance-propagated uncertainty; the geometric entry velocity is reported with its reading uncertainty.
- Figures regenerated as figures 1-3 of the revised manuscript; the apparatus figure is now produced by `05_generate_figures.py` (former `06_generate_apparatus_figure.py` removed).

### Added
- `07_drag_bound.py` and `results/drag_buoyancy_bound.csv`: bias in the fixed-geometry g from quadratic drag and buoyancy (C_D = 0.40-0.50, air density 1.10-1.20 kg m^-3).

## 1.0.0 (2026-07-29)
- Initial reproducibility release.
