#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" - <<'CHECK'
import sys
if sys.version_info < (3,10):
    raise SystemExit(f"Python 3.10+ required; found {sys.version.split()[0]}")
print(f"Using Python {sys.version.split()[0]}")
CHECK
cd "$REPO_DIR/src"
"$PYTHON_BIN" 00_fit_configurations.py
"$PYTHON_BIN" 01_h1_constrained_fit.py
"$PYTHON_BIN" 02_h2_mechanism_test.py
"$PYTHON_BIN" 03_ml_pipeline_and_circularity.py
"$PYTHON_BIN" 04_diagnostics.py
"$PYTHON_BIN" 06_generate_apparatus_figure.py
"$PYTHON_BIN" 05_generate_figures.py
echo "Completed. Results: $REPO_DIR/results; figures: $REPO_DIR/figures"
