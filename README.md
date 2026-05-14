# Bank Statement Analyzer

A modular Python tool for reading multiple bank statement files (CSV, XLSX, XLS, PDF), automatically detecting balance columns, and reporting maximum and minimum balances.

## Project Structure

```
backend/
├── __init__.py                    # Package initialization
├── config.py                      # Configuration and constants
├── detectors.py                   # Balance column detection logic
├── cleaners.py                    # Numeric data cleaning utilities
├── readers.py                     # File reading functions (CSV, Excel, PDF)
├── analyzer.py                    # Core analysis logic
├── reporter.py                    # Report formatting and display
├── bank_statement_analyzer.py     # Main entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Module Descriptions

### `config.py`
Stores configuration constants:
- `BALANCE_KEYWORDS`: Keywords used to identify balance columns
- `EXCLUDE_KEYWORDS`: Keywords that disqualify columns from being balance columns

### `detectors.py`
Contains balance column detection logic:
- `score_column()`: Scores column names based on balance-related keywords
- `detect_balance_column()`: Identifies the balance column in a DataFrame using scoring and heuristics

### `cleaners.py`
Handles numeric data cleaning:
- `clean_numeric()`: Converts various text formats (with currency symbols, Cr/Dr suffixes, etc.) to numeric values

### `readers.py`
File reading functions for multiple formats:
- `read_csv()`: Reads CSV files with encoding detection
- `read_excel()`: Reads Excel files, selecting the sheet with most rows
- `read_pdf()`: Extracts tables from PDF files using pdfplumber or tabula
- `load_file()`: Dispatcher function that selects the appropriate reader based on file extension

### `analyzer.py`
Core analysis logic:
- `analyze_statement()`: Analyzes a single bank statement file and returns results

### `reporter.py`
Report generation and formatting:
- `print_report()`: Displays formatted analysis results with balance information and statistics

### `bank_statement_analyzer.py`
Main entry point:
- `collect_paths()`: Processes command-line arguments to gather file paths
- `main()`: Orchestrates the analysis workflow

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Analyze specific files:
```bash
python bank_statement_analyzer.py file1.csv file2.xlsx file3.pdf
```

### Process all statements in a folder:
```bash
python bank_statement_analyzer.py /path/to/statements/
```

### Use glob patterns:
```bash
python bank_statement_analyzer.py ./statements/*.csv
```

## Features

- **Auto-detects balance columns** regardless of their name or position
- **Supports multiple formats**: CSV, XLSX, XLS, ODS, and PDF
- **Handles various formats**: Currency symbols (₹, $, €, etc.), Cr/Dr suffixes, comma-separated thousands
- **Robust encoding detection** for CSV files
- **Graceful error handling** with detailed error messages
- **Smart fallback heuristics** for difficult files

## Output

The tool generates a formatted report showing:
- File name
- Detected balance column name
- Number of rows analyzed
- Maximum balance
- Minimum balance
- Status (success or error with details)

## Dependencies

- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file support
- **xlrd**: Legacy XLS file support
- **pdfplumber**: PDF table extraction (preferred)
- **tabula-py**: Alternative PDF table extraction

## Error Handling

The analyzer gracefully handles:
- Missing or unreadable files
- Unsupported file formats
- Files without detectable balance columns
- Encoding issues in CSV files
- Missing dependencies for specific file types
