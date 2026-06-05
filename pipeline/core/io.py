"""Result persistence for the pipeline.

Saves a study's output tables to disk as CSV and reads them back. Each study
writes to a single "latest" folder that is overwritten on each run:

    results/<study_name>/latest/<output_name>.csv

This module is generic core plumbing: it does not know or care which study
produced the data, only that outputs are named DataFrames.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Project root is two levels up from this file: pipeline/core/io.py -> project/
RESULTS_ROOT = Path(__file__).resolve().parents[2] / "results"


def _run_dir(study_name: str, results_root: Path | None = None) -> Path:
    """Return the 'latest' output directory for a study, creating it if needed."""
    root = results_root if results_root is not None else RESULTS_ROOT
    path = root / study_name / "latest"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_results(
    study_name: str,
    outputs: dict[str, pd.DataFrame],
    results_root: Path | None = None,
) -> Path:
    """Save a study's named output tables to results/<study_name>/latest/.

    Overwrites any existing files in that folder for the given output names.

    Args:
        study_name: identifier for the study (used as the folder name).
        outputs: mapping of output name -> DataFrame. Each is written to
            <output_name>.csv.
        results_root: optional override for the results directory (useful in
            tests). Defaults to the project-level results/ folder.

    Returns:
        The directory the files were written to.
    """
    out_dir = _run_dir(study_name, results_root)
    for name, df in outputs.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)
    return out_dir


def load_results(
    study_name: str,
    results_root: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Load a study's saved output tables from results/<study_name>/latest/.

    Args:
        study_name: identifier for the study (the folder name used when saving).
        results_root: optional override for the results directory.

    Returns:
        A mapping of output name -> DataFrame for every CSV found. Returns an
        empty dict if the study has no saved results yet.
    """
    root = results_root if results_root is not None else RESULTS_ROOT
    out_dir = root / study_name / "latest"
    if not out_dir.exists():
        return {}
    return {
        csv_path.stem: pd.read_csv(csv_path)
        for csv_path in sorted(out_dir.glob("*.csv"))
    }