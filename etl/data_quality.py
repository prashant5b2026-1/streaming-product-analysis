"""Data quality checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a simple data-quality report for a dataframe."""

    report: Dict[str, Any] = {}

    report["total_rows"] = int(df.shape[0])
    report["total_columns"] = int(df.shape[1])

    # Duplicate rows
    report["duplicate_rows"] = int(df.duplicated().sum())

    # Missing value summary
    missing = df.isnull().sum()
    report["missing_values"] = {
        col: int(count) for col, count in missing.items() if count > 0
    }

    # Unique counts for key columns (useful for data validation)
    for col in ["show_id", "title", "primary_genre", "primary_country"]:
        if col in df.columns:
            report.setdefault("unique_counts", {})[col] = int(df[col].nunique(dropna=True))

    # Basic type summary
    report["data_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    return report


def save_report(report: Dict[str, Any], out_path: Path) -> None:
    """Save the data quality report as JSON."""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
