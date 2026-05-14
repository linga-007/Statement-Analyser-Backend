"""
Numeric data cleaning and conversion utilities.
"""

import pandas as pd


def clean_numeric(series: pd.Series) -> pd.Series:
    """
    Convert a series that may contain strings like '1,23,456.78' or
    '₹ 5000 Cr' into floats. Cr/Dr suffixes are handled.
    """
    if pd.api.types.is_numeric_dtype(series):
        return series

    s = series.astype(str).str.strip()

    # Remove currency symbols and spaces
    s = s.str.replace(r"[₹$€£¥\s]", "", regex=True)

    # Handle Cr/Dr suffixes (credit = positive, debit = negative for balance?)
    # For a running balance column, Cr is positive and Dr could be negative.
    cr_mask = s.str.upper().str.endswith("CR")
    dr_mask = s.str.upper().str.endswith("DR")
    s = s.str.replace(r"(?i)(cr|dr)$", "", regex=True).str.strip()

    # Remove commas (thousands separator)
    s = s.str.replace(",", "", regex=False)

    numeric = pd.to_numeric(s, errors="coerce")

    # Flip sign for Dr-suffixed values (balance went negative)
    numeric[dr_mask] = -numeric[dr_mask].abs()

    return numeric
