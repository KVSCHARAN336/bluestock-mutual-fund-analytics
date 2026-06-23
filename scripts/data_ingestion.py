"""
Bluestock Mutual Fund Analytics - Data Ingestion Module
========================================================
Day-1 Deliverable: Load, profile, validate, and report on all 10 CSV datasets.

Author : Bluestock Fintech Analytics Team
Created: 2026-06-23
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_ingestion.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("data_ingestion")

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT.parent  # where CSVs live (e:\xyz\BLUE STOCKS)
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

for d in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Dataset Manifest
# ──────────────────────────────────────────────────────────────────────────────
DATASETS: Dict[str, str] = {
    "fund_master":           "01_fund_master.csv",
    "nav_history":           "02_nav_history.csv",
    "aum_by_fund_house":     "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":   "04_monthly_sip_inflows.csv",
    "category_inflows":      "05_category_inflows.csv",
    "industry_folio_count":  "06_industry_folio_count.csv",
    "scheme_performance":    "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings":    "09_portfolio_holdings - 09_portfolio_holdings.csv",
    "benchmark_indices":     "10_benchmark_indices - 10_benchmark_indices.csv",
}


# ──────────────────────────────────────────────────────────────────────────────
# Core Functions
# ──────────────────────────────────────────────────────────────────────────────
def load_dataset(name: str, filename: str) -> Optional[pd.DataFrame]:
    """Load a single CSV dataset from the source directory."""
    filepath = SOURCE_DIR / filename
    if not filepath.exists():
        logger.error(f"[{name}] File not found: {filepath}")
        return None

    try:
        df = pd.read_csv(filepath)
        logger.info(f"[{name}] Loaded successfully — {df.shape[0]:,} rows × {df.shape[1]} cols")
        return df
    except Exception as e:
        logger.error(f"[{name}] Failed to load: {e}")
        return None


def profile_dataset(name: str, df: pd.DataFrame) -> Dict:
    """Generate a profiling report for a single dataset."""
    profile = {
        "name": name,
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "head": df.head().to_string(),
        "missing_values": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "missing_pct": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "summary_stats": df.describe(include="all").to_string(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1_048_576, 2),
    }

    logger.info(f"[{name}] Shape: {profile['shape']}")
    logger.info(f"[{name}] Missing values: {profile['total_missing']} ({profile['missing_pct']}%)")
    logger.info(f"[{name}] Duplicate rows: {profile['duplicate_rows']}")
    logger.info(f"[{name}] Memory: {profile['memory_mb']} MB")

    return profile


def validate_data_quality(name: str, df: pd.DataFrame) -> Dict:
    """Run data quality validation checks on a dataset."""
    issues = []

    # Check missing values
    missing = df.isnull().sum()
    cols_with_missing = missing[missing > 0]
    if len(cols_with_missing) > 0:
        for col, count in cols_with_missing.items():
            pct = round(count / len(df) * 100, 2)
            issues.append({
                "check": "missing_values",
                "column": col,
                "count": int(count),
                "pct": pct,
                "severity": "HIGH" if pct > 20 else "MEDIUM" if pct > 5 else "LOW",
            })

    # Check duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        issues.append({
            "check": "duplicate_rows",
            "column": "ALL",
            "count": int(dup_count),
            "pct": round(dup_count / len(df) * 100, 2),
            "severity": "MEDIUM",
        })

    # Dataset-specific validations
    if name == "fund_master":
        issues.extend(_validate_fund_master(df))
    elif name == "nav_history":
        issues.extend(_validate_nav_history(df))
    elif name == "scheme_performance":
        issues.extend(_validate_scheme_performance(df))
    elif name == "investor_transactions":
        issues.extend(_validate_transactions(df))

    return {"dataset": name, "total_issues": len(issues), "issues": issues}


def _validate_fund_master(df: pd.DataFrame) -> list:
    """Fund master specific validations."""
    issues = []

    # Check AMFI code validity (should be positive integers)
    if "amfi_code" in df.columns:
        invalid_amfi = df[df["amfi_code"].apply(lambda x: not str(x).isdigit() or int(x) <= 0)]
        if len(invalid_amfi) > 0:
            issues.append({
                "check": "invalid_amfi_code",
                "column": "amfi_code",
                "count": len(invalid_amfi),
                "pct": round(len(invalid_amfi) / len(df) * 100, 2),
                "severity": "HIGH",
            })

    # Check launch_date validity
    if "launch_date" in df.columns:
        try:
            dates = pd.to_datetime(df["launch_date"], errors="coerce")
            invalid_dates = dates.isna().sum() - df["launch_date"].isna().sum()
            if invalid_dates > 0:
                issues.append({
                    "check": "invalid_launch_date",
                    "column": "launch_date",
                    "count": int(invalid_dates),
                    "pct": round(invalid_dates / len(df) * 100, 2),
                    "severity": "HIGH",
                })
        except Exception:
            pass

    # Check risk category consistency
    valid_risks = {"Low", "Moderate", "Moderately High", "High", "Very High"}
    if "risk_category" in df.columns:
        invalid_risk = df[~df["risk_category"].isin(valid_risks)]
        if len(invalid_risk) > 0:
            issues.append({
                "check": "invalid_risk_category",
                "column": "risk_category",
                "count": len(invalid_risk),
                "pct": round(len(invalid_risk) / len(df) * 100, 2),
                "severity": "MEDIUM",
            })

    # Check category consistency
    valid_categories = {"Equity", "Debt", "Hybrid", "Solution Oriented", "Other"}
    if "category" in df.columns:
        unique_cats = set(df["category"].dropna().unique())
        unexpected = unique_cats - valid_categories
        if unexpected:
            issues.append({
                "check": "unexpected_category_values",
                "column": "category",
                "count": len(unexpected),
                "pct": 0,
                "severity": "INFO",
                "detail": f"Found categories: {unexpected}",
            })

    return issues


def _validate_nav_history(df: pd.DataFrame) -> list:
    """NAV history specific validations."""
    issues = []

    # Check for negative or zero NAV
    if "nav" in df.columns:
        invalid_nav = df[df["nav"] <= 0]
        if len(invalid_nav) > 0:
            issues.append({
                "check": "invalid_nav_values",
                "column": "nav",
                "count": len(invalid_nav),
                "pct": round(len(invalid_nav) / len(df) * 100, 2),
                "severity": "HIGH",
            })

    # Check date validity
    if "date" in df.columns:
        try:
            dates = pd.to_datetime(df["date"], errors="coerce")
            invalid_dates = dates.isna().sum() - df["date"].isna().sum()
            if invalid_dates > 0:
                issues.append({
                    "check": "invalid_dates",
                    "column": "date",
                    "count": int(invalid_dates),
                    "pct": round(invalid_dates / len(df) * 100, 2),
                    "severity": "HIGH",
                })
        except Exception:
            pass

    return issues


def _validate_scheme_performance(df: pd.DataFrame) -> list:
    """Scheme performance specific validations."""
    issues = []

    # Check risk grade consistency
    valid_grades = {"Low", "Moderate", "Moderately High", "High", "Very High"}
    if "risk_grade" in df.columns:
        invalid = df[~df["risk_grade"].isin(valid_grades)]
        if len(invalid) > 0:
            issues.append({
                "check": "invalid_risk_grade",
                "column": "risk_grade",
                "count": len(invalid),
                "pct": round(len(invalid) / len(df) * 100, 2),
                "severity": "MEDIUM",
            })

    return issues


def _validate_transactions(df: pd.DataFrame) -> list:
    """Investor transactions specific validations."""
    issues = []

    # Check for negative amounts
    if "amount_inr" in df.columns:
        negative = df[df["amount_inr"] < 0]
        if len(negative) > 0:
            issues.append({
                "check": "negative_transaction_amount",
                "column": "amount_inr",
                "count": len(negative),
                "pct": round(len(negative) / len(df) * 100, 2),
                "severity": "HIGH",
            })

    # Check KYC status
    valid_kyc = {"Verified", "Pending", "Rejected"}
    if "kyc_status" in df.columns:
        invalid = df[~df["kyc_status"].isin(valid_kyc)]
        if len(invalid) > 0:
            issues.append({
                "check": "invalid_kyc_status",
                "column": "kyc_status",
                "count": len(invalid),
                "pct": round(len(invalid) / len(df) * 100, 2),
                "severity": "MEDIUM",
            })

    return issues


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> Dict:
    """Validate that all AMFI codes in fund_master exist in nav_history."""
    master_codes = set(fund_master["amfi_code"].unique())
    nav_codes = set(nav_history["amfi_code"].unique())

    missing = master_codes - nav_codes
    extra = nav_codes - master_codes
    matched = master_codes & nav_codes

    report = {
        "total_master_schemes": len(master_codes),
        "total_nav_schemes": len(nav_codes),
        "matched_schemes": len(matched),
        "missing_from_nav": sorted(missing),
        "extra_in_nav": sorted(extra),
        "coverage_pct": round(len(matched) / len(master_codes) * 100, 2) if master_codes else 0,
    }

    logger.info(f"AMFI Validation: {report['matched_schemes']}/{report['total_master_schemes']} "
                f"schemes matched ({report['coverage_pct']}%)")
    if missing:
        logger.warning(f"AMFI codes in fund_master but NOT in nav_history: {sorted(missing)}")
    if extra:
        logger.info(f"AMFI codes in nav_history but NOT in fund_master: {sorted(extra)}")

    return report


def explore_fund_master(df: pd.DataFrame) -> Dict:
    """Analyze fund master for unique dimensions."""
    exploration = {
        "unique_fund_houses": sorted(df["fund_house"].unique().tolist()),
        "num_fund_houses": df["fund_house"].nunique(),
        "categories": sorted(df["category"].unique().tolist()),
        "num_categories": df["category"].nunique(),
        "sub_categories": sorted(df["sub_category"].unique().tolist()),
        "num_sub_categories": df["sub_category"].nunique(),
        "risk_grades": sorted(df["risk_category"].unique().tolist()),
        "num_risk_grades": df["risk_category"].nunique(),
        "benchmarks": sorted(df["benchmark"].unique().tolist()),
        "num_benchmarks": df["benchmark"].nunique(),
        "plan_types": sorted(df["plan"].unique().tolist()),
        "num_plan_types": df["plan"].nunique(),
        "total_schemes": len(df),
        "fund_house_distribution": df["fund_house"].value_counts().to_dict(),
        "category_distribution": df["category"].value_counts().to_dict(),
        "risk_distribution": df["risk_category"].value_counts().to_dict(),
    }

    logger.info(f"Fund Master Exploration:")
    logger.info(f"  Fund Houses: {exploration['num_fund_houses']}")
    logger.info(f"  Categories: {exploration['num_categories']}")
    logger.info(f"  Sub-Categories: {exploration['num_sub_categories']}")
    logger.info(f"  Risk Grades: {exploration['num_risk_grades']}")
    logger.info(f"  Benchmarks: {exploration['num_benchmarks']}")
    logger.info(f"  Plan Types: {exploration['num_plan_types']}")

    return exploration


# ──────────────────────────────────────────────────────────────────────────────
# Report Generation
# ──────────────────────────────────────────────────────────────────────────────
def generate_data_quality_report(all_validations: list, all_profiles: list) -> str:
    """Generate a comprehensive Day-1 data quality report in Markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Day-1 Data Quality Report",
        f"",
        f"**Generated:** {timestamp}",
        f"**Platform:** Bluestock Mutual Fund Analytics",
        f"**Datasets Analyzed:** {len(all_profiles)}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]

    total_issues = sum(v["total_issues"] for v in all_validations)
    total_rows = sum(p["shape"][0] for p in all_profiles)
    total_cols = sum(p["shape"][1] for p in all_profiles)
    total_missing = sum(p["total_missing"] for p in all_profiles)
    total_dups = sum(p["duplicate_rows"] for p in all_profiles)

    lines.extend([
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Datasets | {len(all_profiles)} |",
        f"| Total Rows | {total_rows:,} |",
        f"| Total Columns | {total_cols} |",
        f"| Total Missing Values | {total_missing:,} |",
        f"| Total Duplicate Rows | {total_dups:,} |",
        f"| Total Quality Issues | {total_issues} |",
        "",
        "---",
        "",
        "## Dataset Profiles",
        "",
    ])

    for p in all_profiles:
        lines.extend([
            f"### {p['name']}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Rows | {p['shape'][0]:,} |",
            f"| Columns | {p['shape'][1]} |",
            f"| Missing Values | {p['total_missing']:,} ({p['missing_pct']}%) |",
            f"| Duplicate Rows | {p['duplicate_rows']:,} |",
            f"| Memory | {p['memory_mb']} MB |",
            "",
            "**Data Types:**",
            "",
            "| Column | Type |",
            "|--------|------|",
        ])
        for col, dtype in p["dtypes"].items():
            lines.append(f"| {col} | {dtype} |")

        # Missing values detail
        missing_cols = {k: v for k, v in p["missing_values"].items() if v > 0}
        if missing_cols:
            lines.extend(["", "**Missing Values by Column:**", "",
                          "| Column | Count | % |", "|--------|-------|---|"])
            for col, count in missing_cols.items():
                pct = round(count / p["shape"][0] * 100, 2)
                lines.append(f"| {col} | {count} | {pct}% |")

        lines.extend(["", "**First 5 Rows:**", "", "```", p["head"], "```", "", "---", ""])

    # Validation Issues
    lines.extend(["## Data Quality Issues", ""])

    for v in all_validations:
        lines.extend([f"### {v['dataset']} — {v['total_issues']} issue(s)", ""])
        if v["total_issues"] == 0:
            lines.append("✅ No quality issues detected.")
        else:
            lines.extend(["| Check | Column | Count | % | Severity |",
                          "|-------|--------|-------|---|----------|"])
            for issue in v["issues"]:
                detail = issue.get("detail", "")
                detail_str = f" ({detail})" if detail else ""
                lines.append(
                    f"| {issue['check']}{detail_str} | {issue['column']} | "
                    f"{issue['count']} | {issue['pct']}% | {issue['severity']} |"
                )
        lines.extend(["", "---", ""])

    # Recommendations
    lines.extend([
        "## Recommendations",
        "",
        "1. **Missing Values:** Handle missing `yoy_growth_pct` in SIP inflows (expected for first year).",
        "2. **Data Types:** Convert date columns to datetime for time-series analysis.",
        "3. **Duplicates:** Investigate any duplicate rows in transaction data.",
        "4. **NAV Validation:** Ensure all NAV values are positive and within reasonable range.",
        "5. **AMFI Consistency:** Cross-validate AMFI codes across all datasets.",
        "",
        "---",
        "",
        f"*Report generated by Bluestock MF Analytics Pipeline — {timestamp}*",
    ])

    return "\n".join(lines)


def generate_amfi_validation_report(amfi_report: Dict, exploration: Dict) -> str:
    """Generate the AMFI validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# AMFI Code Validation Report",
        "",
        f"**Generated:** {timestamp}",
        f"**Platform:** Bluestock Mutual Fund Analytics",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Schemes (Fund Master) | {amfi_report['total_master_schemes']} |",
        f"| Total Schemes (NAV History) | {amfi_report['total_nav_schemes']} |",
        f"| Matched Schemes | {amfi_report['matched_schemes']} |",
        f"| Missing from NAV History | {len(amfi_report['missing_from_nav'])} |",
        f"| Extra in NAV History | {len(amfi_report['extra_in_nav'])} |",
        f"| Coverage | {amfi_report['coverage_pct']}% |",
        "",
        "---",
        "",
    ]

    if amfi_report["missing_from_nav"]:
        lines.extend([
            "## Missing Schemes (in Fund Master but NOT in NAV History)",
            "",
            "| AMFI Code |",
            "|-----------|",
        ])
        for code in amfi_report["missing_from_nav"]:
            lines.append(f"| {code} |")
        lines.extend(["", "---", ""])

    if amfi_report["extra_in_nav"]:
        lines.extend([
            "## Extra Schemes (in NAV History but NOT in Fund Master)",
            "",
            "| AMFI Code |",
            "|-----------|",
        ])
        for code in amfi_report["extra_in_nav"]:
            lines.append(f"| {code} |")
        lines.extend(["", "---", ""])

    # Fund Master Summary
    lines.extend([
        "## Fund Master Exploration Summary",
        "",
        f"| Dimension | Count |",
        f"|-----------|-------|",
        f"| Fund Houses | {exploration['num_fund_houses']} |",
        f"| Categories | {exploration['num_categories']} |",
        f"| Sub-Categories | {exploration['num_sub_categories']} |",
        f"| Risk Grades | {exploration['num_risk_grades']} |",
        f"| Benchmark Indices | {exploration['num_benchmarks']} |",
        f"| Plan Types | {exploration['num_plan_types']} |",
        f"| Total Schemes | {exploration['total_schemes']} |",
        "",
        "### Fund Houses",
        "",
    ])
    for fh in exploration["unique_fund_houses"]:
        count = exploration["fund_house_distribution"].get(fh, 0)
        lines.append(f"- **{fh}** — {count} scheme(s)")

    lines.extend(["", "### Categories", ""])
    for cat, count in exploration["category_distribution"].items():
        lines.append(f"- **{cat}** — {count} scheme(s)")

    lines.extend(["", "### Risk Distribution", ""])
    for risk, count in exploration["risk_distribution"].items():
        lines.append(f"- **{risk}** — {count} scheme(s)")

    lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
        "1. **Full Coverage:** All fund master schemes have corresponding NAV history data."
        if amfi_report["coverage_pct"] == 100
        else "1. **Gap Remediation:** Fetch NAV history for missing schemes via MFAPI.",
        "2. **Regular Sync:** Set up automated daily sync to keep NAV data current.",
        "3. **Cross-Validation:** Validate AMFI codes against AMFI India official list.",
        "4. **Schema Alignment:** Ensure scheme names are consistent across datasets.",
        "",
        "---",
        "",
        f"*Report generated by Bluestock MF Analytics Pipeline — {timestamp}*",
    ])

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────────────────────────────────────
def main():
    """Execute the full Day-1 data ingestion pipeline."""
    logger.info("=" * 80)
    logger.info("BLUESTOCK MUTUAL FUND ANALYTICS — DAY-1 DATA INGESTION")
    logger.info("=" * 80)

    start_time = datetime.now()

    # Phase 1: Load all datasets
    logger.info("\n" + "=" * 40 + " PHASE 1: DATA LOADING " + "=" * 40)
    dataframes: Dict[str, pd.DataFrame] = {}
    for name, filename in DATASETS.items():
        df = load_dataset(name, filename)
        if df is not None:
            dataframes[name] = df

    logger.info(f"\nLoaded {len(dataframes)}/{len(DATASETS)} datasets successfully.")

    if not dataframes:
        logger.error("No datasets loaded. Exiting.")
        sys.exit(1)

    # Phase 2: Profile all datasets
    logger.info("\n" + "=" * 40 + " PHASE 2: DATA PROFILING " + "=" * 40)
    all_profiles = []
    for name, df in dataframes.items():
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Profiling: {name}")
        logger.info(f"{'─' * 60}")
        profile = profile_dataset(name, df)
        all_profiles.append(profile)

        # Print dtypes
        logger.info(f"\n[{name}] Data Types:")
        for col, dtype in profile["dtypes"].items():
            logger.info(f"  {col}: {dtype}")

        # Print head
        logger.info(f"\n[{name}] First 5 rows:")
        logger.info(f"\n{profile['head']}")

        # Print missing values
        missing = {k: v for k, v in profile["missing_values"].items() if v > 0}
        if missing:
            logger.info(f"\n[{name}] Missing values:")
            for col, count in missing.items():
                logger.info(f"  {col}: {count}")
        else:
            logger.info(f"\n[{name}] No missing values.")

    # Phase 3: Data Quality Validation
    logger.info("\n" + "=" * 40 + " PHASE 3: DATA QUALITY VALIDATION " + "=" * 40)
    all_validations = []
    for name, df in dataframes.items():
        logger.info(f"\nValidating: {name}")
        validation = validate_data_quality(name, df)
        all_validations.append(validation)
        if validation["total_issues"] == 0:
            logger.info(f"  ✅ No issues found.")
        else:
            for issue in validation["issues"]:
                logger.warning(
                    f"  ⚠ [{issue['severity']}] {issue['check']} in '{issue['column']}': "
                    f"{issue['count']} ({issue['pct']}%)"
                )

    # Phase 4: AMFI Validation
    logger.info("\n" + "=" * 40 + " PHASE 4: AMFI CODE VALIDATION " + "=" * 40)
    amfi_report = {}
    exploration = {}
    if "fund_master" in dataframes and "nav_history" in dataframes:
        amfi_report = validate_amfi_codes(dataframes["fund_master"], dataframes["nav_history"])
        exploration = explore_fund_master(dataframes["fund_master"])
    else:
        logger.warning("Cannot perform AMFI validation — fund_master or nav_history missing.")

    # Phase 5: Generate Reports
    logger.info("\n" + "=" * 40 + " PHASE 5: REPORT GENERATION " + "=" * 40)

    # Data Quality Report
    quality_report = generate_data_quality_report(all_validations, all_profiles)
    quality_report_path = REPORTS_DIR / "day1_data_quality_report.md"
    quality_report_path.write_text(quality_report, encoding="utf-8")
    logger.info(f"✅ Data Quality Report saved: {quality_report_path}")

    # AMFI Validation Report
    if amfi_report and exploration:
        amfi_report_md = generate_amfi_validation_report(amfi_report, exploration)
        amfi_report_path = REPORTS_DIR / "amfi_validation_report.md"
        amfi_report_path.write_text(amfi_report_md, encoding="utf-8")
        logger.info(f"✅ AMFI Validation Report saved: {amfi_report_path}")

    # Phase 6: Copy raw data to project structure
    logger.info("\n" + "=" * 40 + " PHASE 6: RAW DATA ARCHIVAL " + "=" * 40)
    for name, filename in DATASETS.items():
        src = SOURCE_DIR / filename
        dst = RAW_DIR / filename
        if src.exists() and not dst.exists():
            try:
                import shutil
                shutil.copy2(src, dst)
                logger.info(f"  Copied: {filename} -> data/raw/")
            except Exception as e:
                logger.warning(f"  Could not copy {filename}: {e}")

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("\n" + "=" * 80)
    logger.info("DAY-1 DATA INGESTION - COMPLETE")
    logger.info(f"  Datasets loaded:   {len(dataframes)}/{len(DATASETS)}")
    logger.info(f"  Total rows:        {sum(p['shape'][0] for p in all_profiles):,}")
    logger.info(f"  Quality issues:    {sum(v['total_issues'] for v in all_validations)}")
    logger.info(f"  AMFI coverage:     {amfi_report.get('coverage_pct', 'N/A')}%")
    logger.info(f"  Elapsed time:      {elapsed:.1f}s")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
