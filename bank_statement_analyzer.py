"""
Bank Statement Analyzer
=======================
Reads multiple bank statement files (CSV, XLSX, XLS, PDF),
auto-detects the balance column regardless of name or position,
and reports the max and min balance for each file.

Usage:
    python bank_statement_analyzer.py file1.csv file2.xlsx file3.pdf
    python bank_statement_analyzer.py /path/to/statements/   # process entire folder
"""

import sys
import os
import glob
import warnings
warnings.filterwarnings("ignore")

from analyzer import analyze_statement
from reporter import print_report


def collect_paths(args: list[str]) -> list[str]:
    """
    Collect file paths from command-line arguments.
    Handles individual files, directories, and glob patterns.
    """
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            for ext in ("*.csv", "*.xlsx", "*.xls", "*.pdf"):
                paths.extend(glob.glob(os.path.join(arg, ext)))
        elif os.path.isfile(arg):
            paths.append(arg)
        else:
            # Glob pattern
            matches = glob.glob(arg)
            paths.extend(matches)
    return sorted(set(paths))


def main():
    """Main entry point."""
    args = sys.argv[1:]
    if not args:
        print("Usage: python bank_statement_analyzer.py file1.csv file2.xlsx ...")
        print("       python bank_statement_analyzer.py /path/to/folder/")
        sys.exit(1)

    paths = collect_paths(args)
    if not paths:
        print("No matching files found.")
        sys.exit(1)

    print(f"\nFound {len(paths)} file(s) to process...")
    results = [analyze_statement(p) for p in paths]
    print_report(results)


if __name__ == "__main__":
    main()
