"""
BlueStock MF Capstone — Unified ETL Pipeline
=============================================
Runs the ENTIRE data pipeline end-to-end without manual steps:
  1. Ingest raw CSVs from data/raw/
  2. Clean, validate, standardise
  3. Export cleaned CSVs to data/processed/
  4. Create SQLite DB at data/db/bluestock_mf.db
  5. Load all tables using sql/schema.sql

Usage:
    python scripts/etl_pipeline.py

Author : BlueStock Fintech Analytics Team
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR      = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_DIR       = PROJECT_ROOT / "data" / "db"
DB_PATH      = DB_DIR / "bluestock_mf.db"
SCHEMA_PATH  = PROJECT_ROOT / "sql" / "schema.sql"
LOG_DIR      = PROJECT_ROOT / "logs"

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("etl_pipeline")

# ──────────────────────────────────────────────────────────────────────────────
# RAW FILE MAPPING
# ──────────────────────────────────────────────────────────────────────────────
RAW_FILES = {
    "fund_master":        "01_fund_master.csv",
    "nav_history":        "02_nav_history.csv",
    "aum_by_fund_house":  "03_aum_by_fund_house.csv",
    "monthly_sip":        "04_monthly_sip_inflows.csv",
    "category_inflows":   "05_category_inflows.csv",
    "industry_folio":     "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "transactions":       "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings - 09_portfolio_holdings.csv",
    "benchmark_indices":  "10_benchmark_indices - 10_benchmark_indices.csv",
}


# ======================================================================
# STEP 1 — INGEST: Load & Validate Raw CSVs
# ======================================================================

def ingest_raw_data() -> dict[str, pd.DataFrame]:
    """Load all 10 raw CSV files and perform basic validation."""
    logger.info("=" * 60)
    logger.info("STEP 1: Ingesting raw data from %s", RAW_DIR)
    logger.info("=" * 60)

    datasets = {}
    for key, filename in RAW_FILES.items():
        filepath = RAW_DIR / filename
        if not filepath.exists():
            logger.error("  MISSING: %s", filepath)
            raise FileNotFoundError(f"Raw file not found: {filepath}")

        df = pd.read_csv(filepath)
        logger.info("  Loaded %-22s  %6d rows x %2d cols", key, len(df), len(df.columns))
        datasets[key] = df

    logger.info("  Total datasets loaded: %d", len(datasets))
    return datasets


# ======================================================================
# STEP 2 — CLEAN: Validate, Fix Types, Handle Nulls
# ======================================================================

def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    """Clean fund master: ensure amfi_code uniqueness, fill missing categories."""
    df = df.drop_duplicates(subset=["amfi_code"], keep="first")
    df["amfi_code"] = df["amfi_code"].astype(int)
    return df


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    """Clean NAV history: parse dates, sort, ffill missing NAVs for weekends/holidays."""
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"]).drop_duplicates()
    # Forward-fill NAV gaps (weekends, holidays) within each fund
    df["nav"] = df.groupby("amfi_code")["nav"].ffill()
    invalid = df[df["nav"] <= 0]
    if len(invalid) > 0:
        logger.warning("  NAV: %d rows with NAV <= 0 (will be dropped)", len(invalid))
        df = df[df["nav"] > 0]
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transactions: parse dates, standardise transaction types, filter invalid."""
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    type_map = {
        "sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption",
    }
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().map(type_map)
    before = len(df)
    df = df[df["amount_inr"] > 0]
    df = df.dropna(subset=["transaction_type"])
    logger.info("  Transactions: %d -> %d rows after cleaning", before, len(df))
    return df


def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Clean performance: coerce numerics, validate ranges."""
    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "expense_ratio_pct", "max_drawdown_pct",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_benchmark_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Clean benchmark indices: parse dates."""
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df.drop_duplicates()


def clean_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply specialised cleaning to each dataset."""
    logger.info("=" * 60)
    logger.info("STEP 2: Cleaning & validating data")
    logger.info("=" * 60)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Specialised cleaning
    datasets["fund_master"]        = clean_fund_master(datasets["fund_master"])
    datasets["nav_history"]        = clean_nav_history(datasets["nav_history"])
    datasets["transactions"]       = clean_transactions(datasets["transactions"])
    datasets["scheme_performance"] = clean_scheme_performance(datasets["scheme_performance"])
    datasets["benchmark_indices"]  = clean_benchmark_indices(datasets["benchmark_indices"])

    # Generic cleaning for remaining datasets
    for key in ["aum_by_fund_house", "monthly_sip", "category_inflows",
                "industry_folio", "portfolio_holdings"]:
        datasets[key] = datasets[key].drop_duplicates()

    # Export all to processed/
    CLEAN_NAMES = {
        "fund_master":        "clean_fund_master.csv",
        "nav_history":        "clean_nav_history.csv",
        "aum_by_fund_house":  "clean_aum_by_fund_house.csv",
        "monthly_sip":        "clean_monthly_sip_inflows.csv",
        "category_inflows":   "clean_category_inflows.csv",
        "industry_folio":     "clean_industry_folio_count.csv",
        "scheme_performance": "clean_scheme_performance.csv",
        "transactions":       "clean_transactions.csv",
        "portfolio_holdings": "clean_portfolio_holdings.csv",
        "benchmark_indices":  "clean_benchmark_indices.csv",
    }

    for key, filename in CLEAN_NAMES.items():
        out = PROCESSED_DIR / filename
        datasets[key].to_csv(out, index=False)
        logger.info("  Saved %-35s  %6d rows", filename, len(datasets[key]))

    return datasets


# ======================================================================
# STEP 3 — LOAD: Create SQLite DB & Load Tables
# ======================================================================

def load_to_sqlite(datasets: dict[str, pd.DataFrame]) -> None:
    """Create SQLite DB from schema.sql and load all tables."""
    logger.info("=" * 60)
    logger.info("STEP 3: Loading data into SQLite at %s", DB_PATH)
    logger.info("=" * 60)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Apply schema
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        logger.info("  Schema applied from %s", SCHEMA_PATH)

        # dim_fund
        df = datasets["fund_master"]
        cols = ["amfi_code", "fund_house", "scheme_name", "category",
                "sub_category", "expense_ratio_pct", "risk_category"]
        cols = [c for c in cols if c in df.columns]
        df[cols].to_sql("dim_fund", conn, if_exists="replace", index=False)
        logger.info("  dim_fund:           %d rows", len(df))

        # fact_nav
        df = datasets["nav_history"].rename(columns={"date": "nav_date"})
        df[["amfi_code", "nav_date", "nav"]].to_sql(
            "fact_nav", conn, if_exists="replace", index=False)
        logger.info("  fact_nav:           %d rows", len(df))

        # fact_transactions
        df = datasets["transactions"]
        df.to_sql("fact_transactions", conn, if_exists="replace", index=False)
        logger.info("  fact_transactions:  %d rows", len(df))

        # fact_performance
        df = datasets["scheme_performance"]
        perf_cols = ["amfi_code", "return_1yr_pct", "return_3yr_pct",
                     "return_5yr_pct", "alpha", "beta", "sharpe_ratio",
                     "sortino_ratio", "max_drawdown_pct"]
        perf_cols = [c for c in perf_cols if c in df.columns]
        df[perf_cols].to_sql("fact_performance", conn, if_exists="replace", index=False)
        logger.info("  fact_performance:   %d rows", len(df))

        # fact_aum
        df = datasets["aum_by_fund_house"]
        if "date" in df.columns:
            df["quarter"] = pd.to_datetime(df["date"]).dt.to_period("Q").astype(str)
            df[["fund_house", "quarter", "aum_crore"]].to_sql(
                "fact_aum", conn, if_exists="replace", index=False)
        logger.info("  fact_aum:           %d rows", len(df))

        # sip_inflows
        df = datasets["monthly_sip"]
        df.to_sql("sip_inflows", conn, if_exists="replace", index=False)
        logger.info("  sip_inflows:        %d rows", len(df))

    # Verify
    with sqlite3.connect(DB_PATH) as conn:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        logger.info("  Tables in DB: %s", list(tables["name"]))

    logger.info("  Database size: %.1f MB", DB_PATH.stat().st_size / 1e6)


# ======================================================================
# MAIN
# ======================================================================

def main():
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("  BlueStock MF — ETL Pipeline Started")
    logger.info("  Timestamp: %s", start.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 60)

    try:
        # Step 1: Ingest
        datasets = ingest_raw_data()

        # Step 2: Clean
        datasets = clean_all(datasets)

        # Step 3: Load to SQLite
        load_to_sqlite(datasets)

        elapsed = (datetime.now() - start).total_seconds()
        logger.info("=" * 60)
        logger.info("  ETL COMPLETE in %.1f seconds", elapsed)
        logger.info("  Processed CSVs: %s", PROCESSED_DIR)
        logger.info("  SQLite DB:      %s", DB_PATH)
        logger.info("=" * 60)

    except Exception as e:
        logger.error("ETL FAILED: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
