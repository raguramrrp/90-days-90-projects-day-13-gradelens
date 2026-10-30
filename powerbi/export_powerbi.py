"""
GradeLens Standalone Power BI Data Export Pipeline.
Usage:
    python powerbi/export_powerbi.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.exports.powerbi_exporter import export_powerbi_datasets

if __name__ == "__main__":
    print("=" * 65)
    print(" GradeLens: Exporting Analytical Views for Power BI Desktop")
    print("=" * 65)
    results = export_powerbi_datasets()
    for filename, info in results.items():
        if info.get("status") == "Success":
            print(f" [OK] {filename:<30} | {info['rows']:>4} rows | {info['size_kb']:>6.2f} KB")
        else:
            print(f" [FAILED] {filename:<30} | Error: {info.get('error')}")
    print("=" * 65)
    print(f" Datasets written to: {BASE_DIR / 'powerbi' / 'data'}")
    print(" Open Power BI Desktop and select 'Get Data -> Folder' or 'Get Data -> Text/CSV'.")
    print("=" * 65)
