# Initial velocity and circular targets as pitfalls in the machine-learning analysis of free-fall data

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24180985.svg)](https://doi.org/10.5281/zenodo.24180985)

*Versão em português: [README.pt.md](README.pt.md)*

Version 2.0.0 reproducibility package for the study **Initial velocity and circular targets as pitfalls in the machine-learning analysis of free-fall data** (A. Brito, M. X. Amorim, E. N. Lima).

## Study overview

Free-fall experiments with two photogates are a standard exercise in undergraduate laboratories, and their data are increasingly used as an entry point to machine learning. The study asks what such data can actually tell us about the gravitational acceleration and about the apparatus, first when they are analysed with the simplified kinematic estimator and then when they are used to train a machine-learning model.

Two problems emerge from one dataset recorded in two sequential acquisition blocks:

- **Physical.** The simplified estimator assumes that the sphere starts the timed interval at rest, whereas it crosses the first photogate already moving. Including this entry velocity in the kinematic fit reproduces the value expected from the measured release geometry, but the fitted acceleration remains below the local reference, differs between blocks and is strongly coupled to the entry velocity. The data support the diagnosis, not an instrumental calibration.
- **Methodological.** A residual target defined from the simplified estimate and a fixed reference value can be reconstructed exactly from the inputs and that same reference. Validation scores then measure approximation of a known algebraic identity, not a physical correction learned from the data.

The scripts below reproduce every number and figure behind both diagnoses.

## Archived releases

Version 2.0.0 is archived on Zenodo: [10.5281/zenodo.24180985](https://doi.org/10.5281/zenodo.24180985). Version 1.0.0: [10.5281/zenodo.21694213](https://doi.org/10.5281/zenodo.21694213). Version 2.0.0 corrects the release geometry and the reference value of gravity; see `CHANGELOG.md`.

## Contents

This archive contains the experimental data, Python source code, numerical outputs, acquisition protocol, and PNG previews required to reproduce the reported analyses. The manuscript itself is intentionally not included.

```text
.
├── ACQUISITION_PROTOCOL.md
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE_CODE.txt
├── LICENSE_DATA.txt
├── README.md
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
│   └── 07_drag_bound.py
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

The scripts write numerical outputs to `results/` and regenerate the figures in `figures/` as PDF and PNG files. SVG output is not generated. Figures are produced in English and in Portuguese; the Portuguese versions carry the suffix `_pt` and use a decimal comma (`python3 src/05_generate_figures.py --lang pt` regenerates only these).

## Scope of the analysis

The package reproduces:

- classical estimates based on `g = 2H/t^2`;
- effective-linear and fixed-geometry (h0 = 7 mm) kinematic fits;
- residual regressions and cross-block checks;
- geometry-constrained timing-offset fits and g-delta correlation diagnostics;
- a bound on the drag and buoyancy bias in g;
- diagnostic machine-learning models and exact algebraic-target baseline;
- ablation and redundant-feature permutation diagnostics;
- all data-derived figures.

The machine-learning target is exactly reconstructible from the input variables and the fixed reference value. The reported ML scores therefore quantify approximation of a known algebraic identity rather than an independently learned physical correction.

## Citation

Please cite the archived software package as:

> Brito, A., Amorim, M. X., & Lima, E. N. (2026). *Reproducibility package for Initial velocity and circular targets as pitfalls in the machine-learning analysis of free-fall data* (Version 2.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.24180985

A machine-readable citation is also provided in `CITATION.cff`.

## Authorship

Auiri Brito and Matheus Xavier Amorim contributed equally to this work. Erika N. Lima is the corresponding author.

## Licenses

- Source code in `src/` and `run_all.sh`: MIT License, see `LICENSE_CODE.txt`.
- Data, results, figures, and documentation: Creative Commons Attribution 4.0 International, see `LICENSE_DATA.txt`.
