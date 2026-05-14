"""
Balance column detection logic.
"""

import pandas as pd
from config import BALANCE_KEYWORDS, EXCLUDE_KEYWORDS


def score_column(col_name: str) -> int:
    """
    Return a relevance score for a column name.
    Higher = more likely to be the balance column.
    """
    name = col_name.strip().lower()

    # Hard exclusion: if any exclusion keyword is a significant part of the name
    for kw in EXCLUDE_KEYWORDS:
        if kw == name or (kw in name and "balance" not in name):
            return -1

    score = 0
    for kw in BALANCE_KEYWORDS:
        if kw == name:
            score += 10          # exact match
        elif name.startswith(kw):
            score += 7
        elif kw in name:
            score += 4
    return score


def detect_balance_column(df: pd.DataFrame) -> str | None:
    """
    Returns the most likely balance column name, or None if not found.
    Also tries heuristics on numeric columns (last numeric column often
    holds running balance in many bank formats).
    """
    scores = {col: score_column(str(col)) for col in df.columns}
    best_col = max(scores, key=scores.get)

    if scores[best_col] > 0:
        return best_col

    # Fallback heuristic: last numeric column that has no negatives
    # (running balance is almost always non-negative)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in reversed(numeric_cols):          # rightmost first
        series = df[col].dropna()
        if len(series) > 0 and (series >= 0).mean() > 0.9:
            return col

    # Last resort: just the last numeric column
    if numeric_cols:
        return numeric_cols[-1]

    return None
