"""
Configuration and constants for the Bank Statement Analyzer.
"""

# Keywords likely found in balance column headers (case-insensitive)
BALANCE_KEYWORDS = [
    "balance", "bal", "closing", "running balance", "running bal",
    "available", "ledger", "net balance", "end balance", "book balance",
    "current balance", "total balance", "avl bal", "avl. bal",
]

# Keywords that disqualify a column even if "balance" appears
# (these are debit/credit columns, not running balance)
EXCLUDE_KEYWORDS = [
    "debit", "credit", "dr", "cr", "deposit", "withdrawal",
    "transaction", "amount", "narration", "description", "date",
    "particulars", "remarks", "cheque", "ref", "mode",
]
