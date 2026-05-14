"""
Reporting utilities for displaying analysis results.
"""


def print_report(results: list[dict]):
    """Print a formatted report of analysis results."""
    print("\n" + "=" * 70)
    print(f"{'BANK STATEMENT BALANCE REPORT':^70}")
    print("=" * 70)

    for r in results:
        print(f"\nFile    : {r['file']}")
        if r["status"] == "error":
            print(f"  ❌  ERROR: {r['error']}")
        else:
            print(f"  Balance Column : {r['balance_column']}")
            print(f"  Rows Analysed  : {r['row_count']}")
            print(f"  ✅ MAX Balance : {r['max_balance']:>15,.2f}")
            print(f"  ✅ MIN Balance : {r['min_balance']:>15,.2f}")
        print("-" * 70)

    ok = [r for r in results if r["status"] == "ok"]
    print(f"\nSummary: {len(ok)}/{len(results)} files processed successfully.")
    print("=" * 70 + "\n")
