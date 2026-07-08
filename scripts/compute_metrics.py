"""
BlueStock MF Capstone — Compute Performance Metrics
====================================================
Computes: Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR, CVaR, CAGR
Exports:  reports/fund_scorecard.csv, reports/alpha_beta.csv, reports/var_cvar_report.csv

Usage:
    python scripts/compute_metrics.py

Note: Annualisation uses 252 TRADING DAYS (not calendar days).
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from pathlib import Path
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR      = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR  = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.065 / TRADING_DAYS_PER_YEAR  # ~6.5% annual (Indian 10yr yield)

print("=" * 60)
print("  BlueStock MF — Performance Metrics Calculator")
print("=" * 60)

# ──────────────────────────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────────────────────────
fund_master = pd.read_csv(RAW_DIR / "01_fund_master.csv")
nav_df      = pd.read_csv(RAW_DIR / "02_nav_history.csv")
perf_df     = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
bench_df    = pd.read_csv(RAW_DIR / "10_benchmark_indices - 10_benchmark_indices.csv")

nav_df['date'] = pd.to_datetime(nav_df['date'])

amfi_to_name  = fund_master.set_index('amfi_code')['scheme_name'].to_dict()
amfi_to_house = fund_master.set_index('amfi_code')['fund_house'].to_dict()
amfi_to_cat   = fund_master.set_index('amfi_code')['category'].to_dict()

# Pivot NAV -> daily returns
nav_pivot = nav_df.pivot(index='date', columns='amfi_code', values='nav').sort_index()
daily_returns = nav_pivot.pct_change().dropna(how='all')

# Benchmark returns (Nifty 50)
if 'date' in bench_df.columns and 'nifty_50' in bench_df.columns:
    bench_df['date'] = pd.to_datetime(bench_df['date'])
    bench_df = bench_df.sort_values('date').set_index('date')
    bench_returns = bench_df['nifty_50'].pct_change().dropna()
else:
    bench_returns = None

print(f"\n  Loaded {len(fund_master)} schemes, {len(nav_df):,} NAV records")
print(f"  Daily returns shape: {daily_returns.shape}")

# ──────────────────────────────────────────────────────────────────────────────
# Compute metrics for each fund
# ──────────────────────────────────────────────────────────────────────────────
print("\n  Computing metrics for all schemes...\n")

results = []
alpha_beta_results = []

for amfi in daily_returns.columns:
    rets = daily_returns[amfi].dropna()
    if len(rets) < 30:
        continue

    n_days = len(rets)
    excess = rets - RISK_FREE_RATE

    # --- Sharpe Ratio (annualised) ---
    sharpe = (excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS_PER_YEAR) if excess.std() > 0 else 0

    # --- Sortino Ratio (annualised) ---
    downside = excess[excess < 0]
    downside_std = downside.std() if len(downside) > 0 else 0
    sortino = (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS_PER_YEAR) if downside_std > 0 else 0

    # --- Max Drawdown ---
    cum_returns = (1 + rets).cumprod()
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100  # as percentage

    # --- VaR (95%) & CVaR ---
    var_95 = rets.quantile(0.05)
    cvar = rets[rets <= var_95].mean()

    # --- CAGR (annualised with trading days, NOT calendar days) ---
    total_return = cum_returns.iloc[-1] / cum_returns.iloc[0]
    cagr = (total_return ** (TRADING_DAYS_PER_YEAR / n_days) - 1) * 100

    # --- Alpha & Beta (vs benchmark) ---
    alpha, beta = np.nan, np.nan
    if bench_returns is not None:
        common_idx = rets.index.intersection(bench_returns.index)
        if len(common_idx) > 30:
            fund_r = rets.loc[common_idx]
            bench_r = bench_returns.loc[common_idx]
            cov_matrix = np.cov(fund_r, bench_r)
            beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] != 0 else 0
            alpha = (fund_r.mean() - RISK_FREE_RATE - beta * (bench_r.mean() - RISK_FREE_RATE)) * TRADING_DAYS_PER_YEAR * 100

    # Risk grade from performance data
    risk_map = perf_df.set_index('amfi_code')['risk_grade'].to_dict() if 'risk_grade' in perf_df.columns else {}

    results.append({
        'amfi_code':       amfi,
        'scheme_name':     amfi_to_name.get(amfi, str(amfi)),
        'fund_house':      amfi_to_house.get(amfi, 'Unknown'),
        'category':        amfi_to_cat.get(amfi, 'Unknown'),
        'risk_grade':      risk_map.get(amfi, 'Unknown'),
        'sharpe_ratio':    round(sharpe, 4),
        'sortino_ratio':   round(sortino, 4),
        'max_drawdown_pct': round(max_drawdown, 2),
        'VaR_95_pct':      round(var_95 * 100, 4),
        'CVaR_pct':        round(cvar * 100, 4),
        'CAGR_pct':        round(cagr, 2),
        'observations':    n_days,
    })

    alpha_beta_results.append({
        'amfi_code':    amfi,
        'scheme_name':  amfi_to_name.get(amfi, str(amfi)),
        'alpha':        round(alpha, 4) if not np.isnan(alpha) else None,
        'beta':         round(beta, 4) if not np.isnan(beta) else None,
    })

# ──────────────────────────────────────────────────────────────────────────────
# Export CSVs
# ──────────────────────────────────────────────────────────────────────────────
scorecard = pd.DataFrame(results).sort_values('sharpe_ratio', ascending=False)
scorecard.to_csv(REPORTS_DIR / "fund_scorecard.csv", index=False)
print(f"  Saved: reports/fund_scorecard.csv  ({len(scorecard)} schemes)")

alpha_beta = pd.DataFrame(alpha_beta_results)
alpha_beta.to_csv(REPORTS_DIR / "alpha_beta.csv", index=False)
print(f"  Saved: reports/alpha_beta.csv  ({len(alpha_beta)} schemes)")

var_cvar = scorecard[['amfi_code', 'scheme_name', 'fund_house', 'category',
                       'VaR_95_pct', 'CVaR_pct', 'observations', 'risk_grade']]
var_cvar = var_cvar.sort_values('VaR_95_pct')
var_cvar.to_csv(REPORTS_DIR / "var_cvar_report.csv", index=False)
print(f"  Saved: reports/var_cvar_report.csv  ({len(var_cvar)} schemes)")

# ──────────────────────────────────────────────────────────────────────────────
# Print summary
# ──────────────────────────────────────────────────────────────────────────────
print("\n  Top 5 Funds by Sharpe Ratio:")
for _, r in scorecard.head(5).iterrows():
    print(f"    Sharpe {r['sharpe_ratio']:>6.2f} | CAGR {r['CAGR_pct']:>6.1f}% | "
          f"MaxDD {r['max_drawdown_pct']:>6.1f}% | {r['scheme_name'][:45]}")

print(f"\n  Top 5 Riskiest (VaR):")
for _, r in var_cvar.head(5).iterrows():
    print(f"    VaR {r['VaR_95_pct']:>7.3f}% | CVaR {r['CVaR_pct']:>7.3f}% | {r['scheme_name'][:45]}")

print("\n" + "=" * 60)
print("  All metrics computed successfully!")
print("=" * 60)
