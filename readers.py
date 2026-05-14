"""
File reader functions for various file formats.
"""

import os
import pandas as pd


def read_csv(path: str) -> pd.DataFrame:
    """Read CSV file with multiple encoding attempts."""
    # Try common encodings
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=enc, thousands=",")
            if len(df.columns) > 1:
                return df
        except Exception:
            continue
    raise ValueError(f"Could not read CSV: {path}")


def read_excel(path: str) -> pd.DataFrame:
    """Read Excel file and return the sheet with most rows."""
    ext = os.path.splitext(path)[1].lower()
    engine = "xlrd" if ext == ".xls" else "openpyxl"
    # Try each sheet; pick the one with most rows
    xl = pd.ExcelFile(path, engine=engine)
    best = pd.DataFrame()
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, thousands=",")
        if len(df) > len(best):
            best = df
    return best


def read_pdf(path: str) -> pd.DataFrame:
    """Extract tables from PDF using pdfplumber (preferred) or tabula."""
    try:
        import pdfplumber
        tables = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for tbl in page.extract_tables():
                    if tbl and len(tbl) > 1:
                        headers = [str(h).strip() if h else f"col_{i}"
                                   for i, h in enumerate(tbl[0])]
                        rows = tbl[1:]
                        tables.append(pd.DataFrame(rows, columns=headers))
        if tables:
            df = pd.concat(tables, ignore_index=True)
            return df
    except ImportError:
        pass

    try:
        import tabula
        dfs = tabula.read_pdf(path, pages="all", multiple_tables=True,
                              silent=True)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
    except ImportError:
        pass

    raise ImportError(
        "PDF reading requires 'pdfplumber' or 'tabula-py'.\n"
        "Install with:  pip install pdfplumber"
    )


def load_file(path: str) -> pd.DataFrame:
    """Load a file based on its extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return read_csv(path)
    elif ext in (".xlsx", ".xls", ".xlsm", ".ods"):
        return read_excel(path)
    elif ext == ".pdf":
        return read_pdf(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
