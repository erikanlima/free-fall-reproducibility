# Free-fall model misspecification and algebraic target circularity

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21694213.svg)](https://doi.org/10.5281/zenodo.21694213)

Version 1.0.0 reproducibility package for the study:

**Kinematic model misspecification and algebraic target circularity in a machine-learning analysis of free-fall measurements**

## Archived release

Version 1.0.0 is archived on Zenodo:

**DOI:** [10.5281/zenodo.21694213](https://doi.org/10.5281/zenodo.21694213)

## Contents

This archive contains the experimental data, Python source code, numerical outputs, acquisition protocol, and PNG previews required to reproduce the reported analyses. The manuscript itself is intentionally not included.

```text
.
├── ACQUISITION_PROTOCOL.md
├── CITATION.cff
├── LICENSE_CODE.txt
├── LICENSE_DATA.txt
├── README.md
├── ZENODO_METADATA.md
├── requirements.txt
├── environment_versions.txt
├── run_all.sh
├── data/
│   └── free_fall_measurements.csv
├── src/
│   ├── data_utils.py
│   ├── ml_utils.py
│   ├── 00_fit_configurations.py
│   ├── 01_h1_constrained_fit.py
│   ├── 02_h2_mechanism_test.py
│   ├── 03_ml_pipeline_and_circularity.py
│   ├── 04_diagnostics.py
│   ├── 05_generate_figures.py
│   └── 06_generate_apparatus_figure.py
├── results/
└── figures/
```

## Data

`data/free_fall_measurements.csv` contains 119 individual releases. Its columns are:

- `run_index`: acquisition order;
- `block`: sequential acquisition block;
- `h(m)`: photogate beam-to-beam separation in metres;
- `t(s)`: measured transit time in seconds.

Block 1 contains 75 releases. After the photogate separation was reset to a lower value, Block 2 contains 44 releases. The same sphere, photogates, timing unit, support, and release apparatus were used throughout the campaign.

## Reproduce the analysis

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
./run_all.sh
```

The scripts write numerical outputs to `results/` and regenerate the figures in `figures/` as PDF and PNG files. SVG output is not generated.

## Scope of the analysis

The package reproduces:

- classical estimates based on `g = 2H/t^2`;
- effective-linear and nominal-geometry kinematic sensitivity fits;
- residual regressions and cross-block checks;
- timing-offset fits and parameter-correlation diagnostics;
- diagnostic machine-learning models and exact algebraic-target baseline;
- ablation and redundant-feature permutation diagnostics;
- all data-derived figures.

The machine-learning target is exactly reconstructible from the input variables and the fixed reference value. The reported ML scores therefore quantify approximation of a known algebraic identity rather than an independently learned physical correction.

## Citation

Please cite the archived software package as:

> Brito, A., Amorim, M. X., & Lima, E. N. (2026). *Free-fall model misspecification and algebraic target circularity: reproducibility package* (Version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.21694213

A machine-readable citation is also provided in `CITATION.cff`.

## Authorship

Auri Brito and Matheus Xavier Amorim contributed equally to this work. Erika N. Lima is the corresponding author.

## Licenses

- Source code in `src/` and `run_all.sh`: MIT License, see `LICENSE_CODE.txt`.
- Data, results, figures, and documentation: Creative Commons Attribution 4.0 International, see `LICENSE_DATA.txt`.
