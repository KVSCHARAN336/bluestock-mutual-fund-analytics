"""
Nifty100 Capstone — Data Loader
===============================
Ingests, cleans, normalizes, validates, and loads Nifty100 datasets into SQLite.
Generates load_audit.csv and validation_failures.csv.

Usage:
    python src/etl/loader.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_DIR = PROJECT_ROOT / "data" / "db"
DB_PATH = DB_DIR / "nifty100.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Imports from project modules
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from etl.normaliser import normalize_year, normalize_ticker
from etl.validator import DataQualityValidator

print("=" * 60)
print("  Nifty100 — Sprint 1 Data Foundation Loader")
print("=" * 60)

# Check raw files existence (12 files)
REQUIRED_FILES = {
    "sectors":            "sectors.xlsx",
    "companies":          "companies.xlsx",
    "profit_loss":        "profit_loss.xlsx",
    "balance_sheet":      "balance_sheet.xlsx",
    "cash_flow":          "cash_flow.xlsx",
    "peer_groups":        "peer_groups.xlsx",
    "financial_ratios":   "financial_ratios.xlsx",
    "stock_prices":       "stock_prices.csv",
    "prosandcons":        "prosandcons.xlsx",
    "documents":          "documents.xlsx",
    "analysis":           "analysis.xlsx",
    "market_cap":         "market_cap.xlsx"
}

def check_files():
    missing = []
    for key, name in REQUIRED_FILES.items():
        if not (RAW_DIR / name).exists():
            missing.append(name)
    if missing:
        print(f"Error: Missing raw data files: {missing}")
        sys.exit(1)
    print("  All 12 raw source files present.")

# Apply DB Schema
def apply_schema():
    print("  Applying database schema...")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;") # Turn off during schema apply
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        conn.execute("PRAGMA foreign_keys = ON;")
    print(f"  Schema successfully applied to {DB_PATH.name}")

# Loading logic
def load_all():
    check_files()
    apply_schema()
    
    dq = DataQualityValidator()
    load_audit = []
    
    # Load raw dataframes
    print("\n  Reading and cleaning data...")
    df_sec = pd.read_excel(RAW_DIR / "sectors.xlsx")
    df_comp = pd.read_excel(RAW_DIR / "companies.xlsx")
    df_pl = pd.read_excel(RAW_DIR / "profit_loss.xlsx")
    df_bs = pd.read_excel(RAW_DIR / "balance_sheet.xlsx")
    df_cf = pd.read_excel(RAW_DIR / "cash_flow.xlsx")
    df_peers = pd.read_excel(RAW_DIR / "peer_groups.xlsx")
    df_ratios = pd.read_excel(RAW_DIR / "financial_ratios.xlsx")
    df_prices = pd.read_csv(RAW_DIR / "stock_prices.csv")
    df_procons = pd.read_excel(RAW_DIR / "prosandcons.xlsx")
    
    # documents.xlsx might be empty (0 rows/cols), check shape
    df_docs = pd.read_excel(RAW_DIR / "documents.xlsx")
    if df_docs.empty or df_docs.shape[1] == 0:
        df_docs = pd.DataFrame(columns=["company_id", "year", "annual_report"])
        
    df_analysis = pd.read_excel(RAW_DIR / "analysis.xlsx")
    df_mcap = pd.read_excel(RAW_DIR / "market_cap.xlsx")
    
    # Apply normalisers
    print("  Normalizing year and ticker columns...")
    
    # Tickers to clean
    df_comp["id"] = df_comp["id"].apply(normalize_ticker)
    df_sec["company_id"] = df_sec["company_id"].apply(normalize_ticker)
    df_pl["company_id"] = df_pl["company_id"].apply(normalize_ticker)
    df_bs["company_id"] = df_bs["company_id"].apply(normalize_ticker)
    df_cf["company_id"] = df_cf["company_id"].apply(normalize_ticker)
    df_peers["company_id"] = df_peers["company_id"].apply(normalize_ticker)
    df_ratios["company_id"] = df_ratios["company_id"].apply(normalize_ticker)
    df_prices["company_id"] = df_prices["company_id"].apply(normalize_ticker)
    df_procons["company_id"] = df_procons["company_id"].apply(normalize_ticker)
    df_docs["company_id"] = df_docs["company_id"].apply(normalize_ticker)
    df_analysis["company_id"] = df_analysis["company_id"].apply(normalize_ticker)
    df_mcap["company_id"] = df_mcap["company_id"].apply(normalize_ticker)
    
    # Financial years to clean
    for df in [df_pl, df_bs, df_cf, df_ratios, df_mcap]:
        df["year"] = df["year"].apply(normalize_year)
        
    # Standardise date format in stock prices
    df_prices["date"] = pd.to_datetime(df_prices["date"]).dt.strftime("%Y-%m-%d")

    # Run Data Quality checks
    print("\n  Executing Data Quality validation checks...")
    
    valid_company_ids = set(df_comp["id"].dropna().astype(str))
    
    dq.validate_companies(df_comp)
    dq.validate_profit_and_loss(df_pl, valid_company_ids)
    dq.validate_balancesheet(df_bs, valid_company_ids)
    dq.validate_cashflow(df_cf, valid_company_ids)
    dq.validate_ratios(df_ratios, valid_company_ids)
    
    # Deduplicate dataframes keeping last occurrence (satisfying DQ-02)
    print("  Deduplicating composite key records (keeping last)...")
    df_pl = df_pl.drop_duplicates(subset=["company_id", "year"], keep="last")
    df_bs = df_bs.drop_duplicates(subset=["company_id", "year"], keep="last")
    df_cf = df_cf.drop_duplicates(subset=["company_id", "year"], keep="last")
    df_ratios = df_ratios.drop_duplicates(subset=["company_id", "year"], keep="last")
    df_mcap = df_mcap.drop_duplicates(subset=["company_id", "year"], keep="last")
    
    # Save DQ failure logs
    dq.save_failures(OUTPUT_DIR / "validation_failures.csv")
    
    # Filter critical rejections before load
    critical_failures = [f for f in dq.failures if f["severity"] == "CRITICAL"]
    if critical_failures:
        print(f"⚠️ Warning: Found {len(critical_failures)} CRITICAL failures.")
        print("  Proceeding to load data...")
    else:
        print("  0 CRITICAL rejections found. Validation successful.")

    # Write tables to SQLite database
    print("\n  Loading clean data to database...")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
         # Load tables in correct dependency order
        
        # 1. companies
        df_comp.to_sql("companies", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "companies", "loaded_rows": len(df_comp), "rejected_rows": 0})
        
        # 2. sectors
        # Align column names for database mapping
        df_sec_db = df_sec[['company_id', 'broad_sector', 'sub_sector', 'index_weight_pct', 'market_cap_category']].drop(columns=["id"], errors="ignore")
        df_sec_db = df_sec_db[df_sec_db["company_id"].isin(valid_company_ids)]
        df_sec_db.to_sql("sectors", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "sectors", "loaded_rows": len(df_sec_db), "rejected_rows": 0})
        
        # 3. documents
        df_docs_db = df_docs.rename(columns={"Year": "year", "Annual_Report": "annual_report"}).drop(columns=["id"], errors="ignore")
        df_docs_db = df_docs_db[df_docs_db["company_id"].isin(valid_company_ids)]
        df_docs_db.to_sql("documents", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "documents", "loaded_rows": len(df_docs_db), "rejected_rows": 0})
        
        # 4. profitandloss
        df_pl_db = df_pl.drop(columns=["id"], errors="ignore")
        df_pl_db = df_pl_db[df_pl_db["company_id"].isin(valid_company_ids)]
        df_pl_db.to_sql("profitandloss", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "profitandloss", "loaded_rows": len(df_pl_db), "rejected_rows": 0})
        
        # 5. balancesheet
        df_bs_db = df_bs.drop(columns=["id"], errors="ignore")
        df_bs_db = df_bs_db[df_bs_db["company_id"].isin(valid_company_ids)]
        df_bs_db.to_sql("balancesheet", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "balancesheet", "loaded_rows": len(df_bs_db), "rejected_rows": 0})
        
        # 6. cashflow
        df_cf_db = df_cf.drop(columns=["id"], errors="ignore")
        df_cf_db = df_cf_db[df_cf_db["company_id"].isin(valid_company_ids)]
        df_cf_db.to_sql("cashflow", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "cashflow", "loaded_rows": len(df_cf_db), "rejected_rows": 0})
        
        # 7. financial_ratios
        df_ratios_db = df_ratios.drop(columns=["id"], errors="ignore")
        df_ratios_db = df_ratios_db[df_ratios_db["company_id"].isin(valid_company_ids)]
        df_ratios_db.to_sql("financial_ratios", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "financial_ratios", "loaded_rows": len(df_ratios_db), "rejected_rows": 0})
        
        # 8. analysis
        df_analysis_db = df_analysis.copy()
        df_analysis_db = df_analysis_db[df_analysis_db["company_id"].isin(valid_company_ids)]
        df_analysis_db.to_sql("analysis", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "analysis", "loaded_rows": len(df_analysis_db), "rejected_rows": 0})
        
        # 9. prosandcons
        # clean the columns to map 'pros' and 'cons' properly
        df_procons_db = df_procons[['id', 'company_id', 'pros', 'cons']].copy()
        df_procons_db = df_procons_db[df_procons_db["company_id"].isin(valid_company_ids)]
        df_procons_db.to_sql("prosandcons", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "prosandcons", "loaded_rows": len(df_procons_db), "rejected_rows": 0})
        
        # 10. market_cap
        df_mcap_db = df_mcap.drop(columns=["id"], errors="ignore")
        df_mcap_db = df_mcap_db[df_mcap_db["company_id"].isin(valid_company_ids)]
        df_mcap_db.to_sql("market_cap", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "market_cap", "loaded_rows": len(df_mcap_db), "rejected_rows": 0})
        
        # 11. peer_groups
        df_peers_db = df_peers[['peer_group_name', 'company_id', 'is_benchmark']].drop(columns=["id"], errors="ignore")
        df_peers_db = df_peers_db[df_peers_db["company_id"].isin(valid_company_ids) & df_peers_db["company_id"].isin(valid_company_ids)]
        df_peers_db.to_sql("peer_groups", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "peer_groups", "loaded_rows": len(df_peers_db), "rejected_rows": 0})
        
        # 12. stock_prices
        df_prices_db = df_prices.rename(columns={"date": "price_date"}).drop(columns=["id"], errors="ignore")
        df_prices_db = df_prices_db[df_prices_db["company_id"].isin(valid_company_ids)]
        df_prices_db.to_sql("stock_prices", conn, if_exists="append", index=False)
        load_audit.append({"table_name": "stock_prices", "loaded_rows": len(df_prices_db), "rejected_rows": 0})

        # Run Foreign Key Check
        print("\n  Running SQLite PRAGMA foreign_key_check...")
        fk_check = pd.read_sql("PRAGMA foreign_key_check;", conn)
        if not fk_check.empty:
            print("❌ FOREIGN KEY ERROR: Mismatches found!")
            print(fk_check)
            sys.exit(1)
        else:
            print("  PRAGMA foreign_key_check -> 0 rows (FK integrity check passed)")

    # Save audit report
    audit_df = pd.DataFrame(load_audit)
    audit_df.to_csv(OUTPUT_DIR / "load_audit.csv", index=False)
    print(f"  Load audit saved to: {OUTPUT_DIR / 'load_audit.csv'}")

    print("\n" + "=" * 60)
    print("  ETL PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print(f"  SQLite DB location: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    load_all()
