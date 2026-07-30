#!/usr/bin/env python3
"""Shared data loading, validation, acquisition-block handling, and metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

G_REF = 9.78326  # m s^-2, theoretical geodetic estimate
SPHERE_DIAMETER_M = 0.00635
H0_NOMINAL_M = 0.001  # lower sphere surface to photogate-1 beam
TRIGGER_EDGE = "onset of beam interruption"
V1_GEOMETRIC_REF_M_S = float(np.sqrt(2.0 * G_REF * H0_NOMINAL_M))
BLOCK_BOUNDARY = 75
EXPECTED_ROWS = 119

SRC_DIR = Path(__file__).resolve().parent
REPO_ROOT = SRC_DIR.parent
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "free_fall_measurements.csv"

REQUIRED_COLUMNS = ("h(m)", "t(s)")


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load and validate the raw free-fall measurements.

    Required columns are ``h(m)`` and ``t(s)``. An optional ``block``
    column may contain ``Block 1`` and ``Block 2``. When absent, the
    documented row boundary at index 75 is used by :func:`split_blocks`.
    """
    data_path = Path(path) if path is not None else DEFAULT_DATA_PATH
    if not data_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {data_path}. Place the 119-row CSV at "
            "data/free_fall_measurements.csv or pass an explicit path."
        )

    df = pd.read_csv(data_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required data columns: {missing}")

    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    invalid = ~np.isfinite(df[list(REQUIRED_COLUMNS)]).all(axis=1)
    nonpositive = (df[list(REQUIRED_COLUMNS)] <= 0).any(axis=1)
    if invalid.any() or nonpositive.any():
        bad_rows = df.index[invalid | nonpositive].tolist()
        raise ValueError(
            "The dataset contains missing, non-numerical, infinite, or "
            f"non-positive H/t values at rows: {bad_rows}"
        )

    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} retained measurements, found {len(df)}."
        )

    return df.reset_index(drop=True)


def add_classical_estimate(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``g_classical = 2H/t^2``, which imposes zero entry velocity."""
    out = df.copy()
    out["g_classical"] = 2.0 * out["h(m)"] / out["t(s)"] ** 2
    return out


def split_blocks(
    df: pd.DataFrame, boundary: int = BLOCK_BOUNDARY
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return Block 1 and Block 2 dataframes.

    A supplied ``block`` column takes precedence. Otherwise, the documented
    acquisition boundary is used: rows 0--74 for Block 1 and rows 75--118
    for Block 2. Both blocks were acquired sequentially with the same
    apparatus during one experimental campaign.
    """
    if "block" in df.columns:
        normalized = df["block"].astype(str).str.strip().str.lower()
        block1 = df.loc[normalized.isin({"block 1", "block1", "1"})].copy()
        block2 = df.loc[normalized.isin({"block 2", "block2", "2"})].copy()
        if len(block1) != 75 or len(block2) != 44:
            raise ValueError(
                "The block column must identify 75 Block 1 and 44 Block 2 rows."
            )
        return block1.reset_index(drop=True), block2.reset_index(drop=True)

    if not 0 < boundary < len(df):
        raise ValueError(f"Invalid block boundary {boundary} for {len(df)} rows.")
    block1 = df.iloc[:boundary].reset_index(drop=True)
    block2 = df.iloc[boundary:].reset_index(drop=True)
    return block1, block2


def mae(reference: float, estimates) -> float:
    """Mean absolute error against a scalar reference value."""
    values = np.asarray(estimates, dtype=float)
    return float(np.mean(np.abs(values - reference)))


def rmse(reference: float, estimates) -> float:
    """Root-mean-square error against a scalar reference value."""
    values = np.asarray(estimates, dtype=float)
    return float(np.sqrt(np.mean((values - reference) ** 2)))


def output_path(*parts: str) -> Path:
    """Resolve an output path relative to the repository root."""
    path = REPO_ROOT.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
