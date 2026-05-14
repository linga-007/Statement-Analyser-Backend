"""
Core analysis logic for processing bank statements.
"""

import os
import pandas as pd
from readers import load_file
from detectors import detect_balance_column
from cleaners import clean_numeric


def analyze_statement(path: str) -> dict:
    """
    Analyze a single bank statement file.
    Returns a dictionary with analysis results and any errors.
    Keys use snake_case for API compatibility.
    """
    result = {
        "file": os.path.basename(path),
        "status": "ok",
        "balance_column": None,
        "max_balance": None,
        "min_balance": None,
        "row_count": None,
        "valid_count": None,
        "opening_balance": None,
        "closing_balance": None,
        "columns": [],
        "error": None,
    }

    try:
        df = load_file(path)
        result["row_count"] = int(len(df))

        # Strip whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]
        result["columns"] = list(df.columns)

        # Detect balance column
        bal_col = detect_balance_column(df)
        if bal_col is None:
            result["status"] = "error"
            result["error"] = "Could not detect a balance column."
            return result

        result["balance_column"] = bal_col

        # Clean and parse
        bal_series = clean_numeric(df[bal_col]).dropna()

        if bal_series.empty:
            result["status"] = "error"
            result["error"] = f"Column '{bal_col}' has no numeric data."
            return result

        values = bal_series.tolist()
        result["max_balance"] = float(round(float(bal_series.max()), 2))
        result["min_balance"] = float(round(float(bal_series.min()), 2))
        result["opening_balance"] = float(round(float(values[0]), 2))
        result["closing_balance"] = float(round(float(values[-1]), 2))
        result["valid_count"] = int(len(values))

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result
