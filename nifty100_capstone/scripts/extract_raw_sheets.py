"""
Nifty100 Capstone — Raw Dataset Extractor
==========================================
Extracts sheets from DATASET.xlsx and SUPPORTING_DATASETS.xlsx
and saves them as individual Excel/CSV files in data/raw/.
"""

import os
from pathlib import Path
import pandas as pd

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATASET_PATH = RAW_DIR / "DATASET.xlsx"
SUPPORTING_PATH = RAW_DIR / "SUPPORTING_DATASETS.xlsx"

print("=" * 60)
print("  Extracting raw data sheets to individual files...")
print("=" * 60)

# Core datasets in DATASET.xlsx (metadata header at index 0, actual header at index 1)
core_sheets = {
    "COMPANIES":     "companies.xlsx",
    "PROFITANDLOSS": "profit_loss.xlsx",
    "BANCESHEET":    "balance_sheet.xlsx",
    "CASHFLOW":      "cash_flow.xlsx",
    "ANALYSIS":      "analysis.xlsx",
    "DOCUMENTS":     "documents.xlsx",
    "PROSANDCONS":   "prosandcons.xlsx"
}

print("\n--- Core Datasets (DATASET.xlsx) ---")
for sheet_name, dest_file in core_sheets.items():
    try:
        # Load the sheet. Index 0 is metadata, so header is at index 1
        df = pd.read_excel(DATASET_PATH, sheet_name=sheet_name, header=1)
        
        # Strip string values and column names
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
        dest_path = RAW_DIR / dest_file
        df.to_excel(dest_path, index=False)
        print(f"  Extracted '{sheet_name}' -> {dest_file} (Rows: {len(df)}, Columns: {df.shape[1]})")
    except Exception as e:
        print(f"  Error extracting '{sheet_name}': {e}")

# Supplementary datasets in SUPPORTING_DATASETS.xlsx (header at index 0)
supp_sheets = {
    "SECTORS":          ("sectors.xlsx", "excel"),
    "FINANCIAL_RATIOS": ("financial_ratios.xlsx", "excel"),
    "MARKET_CAP":       ("market_cap.xlsx", "excel"),
    "PEER_PRICES":      ("peer_groups.xlsx", "excel"),
    "SOCK_PRICES":      ("stock_prices.csv", "csv")
}

print("\n--- Supplementary Datasets (SUPPORTING_DATASETS.xlsx) ---")
for sheet_name, (dest_file, file_type) in supp_sheets.items():
    try:
        df = pd.read_excel(SUPPORTING_PATH, sheet_name=sheet_name, header=0)
        
        # Strip string values and column names
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
        dest_path = RAW_DIR / dest_file
        if file_type == "excel":
            df.to_excel(dest_path, index=False)
        else:
            df.to_csv(dest_path, index=False)
        print(f"  Extracted '{sheet_name}' -> {dest_file} (Rows: {len(df)}, Columns: {df.shape[1]})")
    except Exception as e:
        print(f"  Error extracting '{sheet_name}': {e}")

# Create empty additional_details.xlsx if it doesn't exist
# (since our previous synthetic generator had it for extra details)
additional_details_path = RAW_DIR / "additional_details.xlsx"
if not additional_details_path.exists():
    pd.DataFrame(columns=["company_id", "is_nifty50", "market_cap_category"]).to_excel(additional_details_path, index=False)
    print("\n  Created placeholder additional_details.xlsx")

print("=" * 60)
print("  Extraction complete!")
print("=" * 60)
