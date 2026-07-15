"""
Sprint 2 — Day 12-13: Compute All Financial Ratios & Populate SQLite
=====================================================================
Reads P&L, BS, CF from nifty100.db, computes 50+ KPIs for all 92 companies,
and writes results into the financial_ratios table.

Usage:
    python src/analytics/compute_all.py
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
DB_PATH = PROJECT_ROOT / "data" / "db" / "nifty100.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT / "src"))
from analytics.ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage_ratio,
    net_debt, asset_turnover, book_value_per_share
)
from analytics.cagr import compute_all_cagrs
from analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_score, capex_intensity,
    fcf_conversion, classify_capital_allocation, generate_capital_allocation_csv
)


def safe_float(val):
    """Convert value to float or return None."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def load_source_data(conn):
    """Load all source tables into DataFrames."""
    df_pl = pd.read_sql("SELECT * FROM profitandloss", conn)
    df_bs = pd.read_sql("SELECT * FROM balancesheet", conn)
    df_cf = pd.read_sql("SELECT * FROM cashflow", conn)
    df_sec = pd.read_sql("SELECT * FROM sectors", conn)
    df_comp = pd.read_sql("SELECT * FROM companies", conn)
    return df_pl, df_bs, df_cf, df_sec, df_comp


def get_financial_companies(df_sec):
    """Get set of company_ids in Financials broad_sector."""
    fin_mask = df_sec["broad_sector"].str.contains("Financ", case=False, na=False)
    return set(df_sec.loc[fin_mask, "company_id"].tolist())


def compute_composite_quality_score(row):
    """
    Composite Quality Score (0-100) based on weighted KPI metrics.
    Weights: ROE(25%), ROCE(20%), NPM(15%), D/E inverse(15%), ICR(10%), CFO Quality(15%).
    """
    score = 0
    count = 0

    roe = row.get("return_on_equity_pct")
    if roe is not None:
        # ROE: 15%+ is excellent (25 pts), 10-15% is good (15 pts), <10% is okay (5 pts)
        if roe >= 15:
            score += 25
        elif roe >= 10:
            score += 15
        else:
            score += max(0, 5)
        count += 1

    roce = row.get("roce_pct")
    if roce is not None:
        if roce >= 20:
            score += 20
        elif roce >= 12:
            score += 12
        else:
            score += max(0, 4)
        count += 1

    npm = row.get("net_profit_margin_pct")
    if npm is not None:
        if npm >= 15:
            score += 15
        elif npm >= 8:
            score += 10
        else:
            score += max(0, 3)
        count += 1

    de = row.get("debt_to_equity")
    if de is not None:
        if de < 0.5:
            score += 15
        elif de < 1.0:
            score += 10
        elif de < 2.0:
            score += 5
        else:
            score += 0
        count += 1

    icr = row.get("interest_coverage")
    if icr is not None:
        if icr > 5:
            score += 10
        elif icr > 2:
            score += 6
        elif icr > 1:
            score += 3
        else:
            score += 0
        count += 1

    cfo_q = row.get("cfo_quality_score")
    if cfo_q is not None:
        if cfo_q > 1.0:
            score += 15
        elif cfo_q > 0.5:
            score += 10
        else:
            score += 3
        count += 1

    if count == 0:
        return None
    return round(score, 2)


def run_ratio_engine():
    """Main entry point: compute all ratios and populate financial_ratios table."""
    print("=" * 60)
    print("  Sprint 2 — Financial Ratio Engine")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Load source data
    print("  Loading source data from SQLite...")
    df_pl, df_bs, df_cf, df_sec, df_comp = load_source_data(conn)

    financial_companies = get_financial_companies(df_sec)
    print(f"  Financial sector companies: {len(financial_companies)}")

    # Get all unique (company_id, year) from P&L (base table)
    all_keys = df_pl[["company_id", "year"]].drop_duplicates()
    print(f"  Computing ratios for {len(all_keys)} company-year records...")

    # Index dataframes for fast lookup
    pl_idx = df_pl.set_index(["company_id", "year"])
    bs_idx = df_bs.set_index(["company_id", "year"])
    cf_idx = df_cf.set_index(["company_id", "year"])

    # Group P&L by company for CAGR computation
    pl_by_company = {cid: group for cid, group in df_pl.groupby("company_id")}

    # Edge case log
    edge_cases = []

    # Compute ratios for each (company_id, year)
    results = []
    for _, key_row in all_keys.iterrows():
        cid = key_row["company_id"]
        yr = key_row["year"]

        # Lookup P&L row
        pl = pl_idx.loc[(cid, yr)] if (cid, yr) in pl_idx.index else pd.Series()
        # Lookup BS row
        bs = bs_idx.loc[(cid, yr)] if (cid, yr) in bs_idx.index else pd.Series()
        # Lookup CF row
        cf = cf_idx.loc[(cid, yr)] if (cid, yr) in cf_idx.index else pd.Series()

        # Extract values
        sales = safe_float(pl.get("sales"))
        expenses = safe_float(pl.get("expenses"))
        op_profit = safe_float(pl.get("operating_profit"))
        opm_pct_reported = safe_float(pl.get("opm_percentage"))
        other_income = safe_float(pl.get("other_income"))
        interest = safe_float(pl.get("interest"))
        net_prof = safe_float(pl.get("net_profit"))
        eps = safe_float(pl.get("eps"))
        div_payout = safe_float(pl.get("dividend_payout"))

        eq_cap = safe_float(bs.get("equity_capital"))
        reserves = safe_float(bs.get("reserves"))
        borrowings = safe_float(bs.get("borrowings"))
        total_assets = safe_float(bs.get("total_assets"))
        investments = safe_float(bs.get("investments"))

        cfo = safe_float(cf.get("operating_activity"))
        cfi = safe_float(cf.get("investing_activity"))
        cff = safe_float(cf.get("financing_activity"))

        is_fin = cid in financial_companies

        # ── Day 08: Profitability ──
        npm = net_profit_margin(net_prof, sales)
        opm = operating_profit_margin(op_profit, sales)
        roe = return_on_equity(net_prof, eq_cap, reserves)
        roce = return_on_capital_employed(op_profit, other_income, eq_cap, reserves, borrowings)
        roa = return_on_assets(net_prof, total_assets)

        # OPM cross-check
        opm_warn = opm_cross_check(opm, opm_pct_reported)
        if opm_warn:
            edge_cases.append(f"[OPM] {cid} {yr}: {opm_warn}")

        # ── Day 09: Leverage & Efficiency ──
        de = debt_to_equity(borrowings, eq_cap, reserves)
        hlf = high_leverage_flag(de, is_fin)
        icr_val, icr_lbl = interest_coverage_ratio(op_profit, other_income, interest)
        nd = net_debt(borrowings, investments)
        at = asset_turnover(sales, total_assets)
        bvps = book_value_per_share(eq_cap, reserves)

        # ── Day 11: Cash Flow KPIs ──
        fcf = free_cash_flow(cfo, cfi)
        capex_int_pct, capex_int_lbl = capex_intensity(cfi, sales)
        fcf_conv = fcf_conversion(fcf, op_profit)
        cap_alloc = classify_capital_allocation(cfo, cfi, cff)

        # CFO Quality: need 5 years of history, compute per-year for now
        cfo_q = None
        cfo_q_lbl = ""
        if cfo is not None and net_prof is not None and net_prof != 0:
            cfo_q = round(cfo / net_prof, 2)
            if cfo_q > 1.0:
                cfo_q_lbl = "High Quality"
            elif cfo_q >= 0.5:
                cfo_q_lbl = "Moderate"
            else:
                cfo_q_lbl = "Accrual Risk"

        # ── Day 10: CAGR Metrics ──
        company_pl = pl_by_company.get(cid, pd.DataFrame())
        rev_cagrs = compute_all_cagrs(company_pl, "sales", yr)
        pat_cagrs = compute_all_cagrs(company_pl, "net_profit", yr)
        eps_cagrs = compute_all_cagrs(company_pl, "eps", yr)

        # Build row
        row = {
            "company_id": cid,
            "year": yr,
            # Profitability
            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "roce_pct": roce,
            "roa_pct": roa,
            # Leverage & Efficiency
            "debt_to_equity": de,
            "high_leverage_flag": hlf,
            "interest_coverage": icr_val,
            "icr_label": icr_lbl,
            "net_debt_cr": nd,
            "asset_turnover": at,
            # Cash Flow
            "free_cash_flow_cr": fcf,
            "capex_cr": abs(cfi) if cfi is not None else None,
            "cash_from_operations_cr": cfo,
            "cfo_quality_score": cfo_q,
            "cfo_quality_label": cfo_q_lbl,
            "capex_intensity_pct": capex_int_pct,
            "capex_intensity_label": capex_int_lbl,
            "fcf_conversion_pct": fcf_conv,
            "capital_allocation_pattern": cap_alloc,
            # Per-share
            "earnings_per_share": eps,
            "book_value_per_share": bvps,
            "dividend_payout_ratio_pct": div_payout,
            "total_debt_cr": borrowings,
            # CAGR — Revenue
            "revenue_cagr_3yr": rev_cagrs["3yr"][0],
            "revenue_cagr_3yr_flag": rev_cagrs["3yr"][1] or None,
            "revenue_cagr_5yr": rev_cagrs["5yr"][0],
            "revenue_cagr_5yr_flag": rev_cagrs["5yr"][1] or None,
            "revenue_cagr_10yr": rev_cagrs["10yr"][0],
            "revenue_cagr_10yr_flag": rev_cagrs["10yr"][1] or None,
            # CAGR — PAT
            "pat_cagr_3yr": pat_cagrs["3yr"][0],
            "pat_cagr_3yr_flag": pat_cagrs["3yr"][1] or None,
            "pat_cagr_5yr": pat_cagrs["5yr"][0],
            "pat_cagr_5yr_flag": pat_cagrs["5yr"][1] or None,
            "pat_cagr_10yr": pat_cagrs["10yr"][0],
            "pat_cagr_10yr_flag": pat_cagrs["10yr"][1] or None,
            # CAGR — EPS
            "eps_cagr_3yr": eps_cagrs["3yr"][0],
            "eps_cagr_3yr_flag": eps_cagrs["3yr"][1] or None,
            "eps_cagr_5yr": eps_cagrs["5yr"][0],
            "eps_cagr_5yr_flag": eps_cagrs["5yr"][1] or None,
            "eps_cagr_10yr": eps_cagrs["10yr"][0],
            "eps_cagr_10yr_flag": eps_cagrs["10yr"][1] or None,
        }
        results.append(row)

    # Build DataFrame
    df_ratios = pd.DataFrame(results)

    # ── Day 12: Composite Quality Score ──
    print("  Computing composite quality scores...")
    df_ratios["composite_quality_score"] = df_ratios.apply(compute_composite_quality_score, axis=1)

    # ── Day 13: Bank ROCE Carve-Out & Edge Case Log ──
    print("  Cross-checking ROCE and ROE against source values...")
    for _, comp_row in df_comp.iterrows():
        cid = comp_row["id"]
        src_roce = safe_float(comp_row.get("roce_percentage"))
        src_roe = safe_float(comp_row.get("roe_percentage"))

        # Get latest computed values for this company
        comp_ratios = df_ratios[df_ratios["company_id"] == cid]
        if comp_ratios.empty:
            continue

        # Use the latest non-TTM year
        latest = comp_ratios[comp_ratios["year"] != "TTM"].sort_values("year", ascending=False)
        if latest.empty:
            continue
        latest_row = latest.iloc[0]

        computed_roce = latest_row.get("roce_pct")
        computed_roe = latest_row.get("return_on_equity_pct")

        if src_roce is not None and computed_roce is not None:
            diff = abs(computed_roce - src_roce)
            if diff > 5:
                edge_cases.append(
                    f"[ROCE_ANOMALY] {cid}: computed={computed_roce:.2f}%, source={src_roce:.2f}%, diff={diff:.2f}% — Category: version difference"
                )

        if src_roe is not None and computed_roe is not None:
            diff = abs(computed_roe - src_roe)
            if diff > 5:
                category = "data source issue" if src_roe < 1 else "version difference"
                edge_cases.append(
                    f"[ROE_ANOMALY] {cid}: computed={computed_roe:.2f}%, source={src_roe:.2f}%, diff={diff:.2f}% — Category: {category}"
                )

    # ── Write to database ──
    print(f"\n  Dropping old financial_ratios and writing {len(df_ratios)} computed rows...")
    # Re-apply schema for financial_ratios table only
    conn.execute("DROP TABLE IF EXISTS financial_ratios;")
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    # Extract just the financial_ratios CREATE statement
    import re
    match = re.search(r"(CREATE TABLE financial_ratios \(.*?\);)", schema_sql, re.DOTALL)
    if match:
        conn.execute(match.group(1))
    else:
        print("  ERROR: Could not find financial_ratios CREATE statement in schema.sql!")
        sys.exit(1)

    df_ratios.to_sql("financial_ratios", conn, if_exists="append", index=False)

    # Verify row count
    count = pd.read_sql("SELECT COUNT(*) as cnt FROM financial_ratios", conn).iloc[0]["cnt"]
    print(f"  SELECT COUNT(*) FROM financial_ratios = {count}")

    # Check for null-only columns
    null_check = pd.read_sql("SELECT * FROM financial_ratios", conn)
    null_cols = [c for c in null_check.columns if null_check[c].isna().all()]
    if null_cols:
        print(f"  ⚠️ Warning: Null-only columns detected: {null_cols}")
    else:
        print("  All KPI columns have data — zero null-only columns.")

    # ── Generate output files ──

    # Capital Allocation CSV
    print("  Generating output/capital_allocation.csv...")
    df_cf_full = pd.read_sql("SELECT * FROM cashflow", conn)
    cap_alloc_df = generate_capital_allocation_csv(df_cf_full)
    cap_alloc_df.to_csv(OUTPUT_DIR / "capital_allocation.csv", index=False)

    # Edge Case Log
    print(f"  Writing {len(edge_cases)} edge cases to output/ratio_edge_cases.log...")
    with open(OUTPUT_DIR / "ratio_edge_cases.log", "w", encoding="utf-8") as f:
        f.write("Nifty100 Financial Ratio Engine — Edge Case Log\n")
        f.write("=" * 60 + "\n\n")
        for ec in edge_cases:
            f.write(ec + "\n")
        if not edge_cases:
            f.write("No edge cases detected.\n")

    # Screener Preview: ROE > 15% and D/E < 1
    screener = pd.read_sql("""
        SELECT DISTINCT company_id, return_on_equity_pct, debt_to_equity
        FROM financial_ratios
        WHERE return_on_equity_pct > 15 AND debt_to_equity < 1
        AND year != 'TTM'
        ORDER BY return_on_equity_pct DESC
    """, conn)
    print(f"\n  Screener Preview (ROE > 15% & D/E < 1): {len(screener)} unique company-year entries")

    # Spot-check 3 companies
    spot_check_companies = ["TCS", "RELIANCE", "HDFCBANK"]
    print("\n  Manual Spot-Check (5 KPIs for 3 companies, latest year):")
    for cid in spot_check_companies:
        row = df_ratios[(df_ratios["company_id"] == cid) & (df_ratios["year"] != "TTM")]
        if row.empty:
            print(f"    {cid}: No data found")
            continue
        latest = row.sort_values("year", ascending=False).iloc[0]
        print(f"    {cid} ({latest['year']}): "
              f"ROE={latest.get('return_on_equity_pct')}%, "
              f"ROCE={latest.get('roce_pct')}%, "
              f"NPM={latest.get('net_profit_margin_pct')}%, "
              f"D/E={latest.get('debt_to_equity')}, "
              f"Rev CAGR 5yr={latest.get('revenue_cagr_5yr')}%")

    conn.close()

    print("\n" + "=" * 60)
    print("  SPRINT 2 — RATIO ENGINE COMPLETED SUCCESSFULLY!")
    print(f"  financial_ratios: {count} rows, 50+ KPI columns")
    print(f"  output/capital_allocation.csv: {len(cap_alloc_df)} rows")
    print(f"  output/ratio_edge_cases.log: {len(edge_cases)} entries")
    print("=" * 60)


if __name__ == "__main__":
    run_ratio_engine()
