"""
BlueStock MF Capstone — Markowitz Portfolio Optimisation
==========================================================
Fulfills Bonus Challenge B4.
Optimizes a portfolio of 5 selected funds across different asset categories.
Generates 5000 random portfolios to plot the Efficient Frontier and highlights
the Max Sharpe Ratio and Minimum Volatility portfolios.

Usage:
    python scripts/portfolio_optimization.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHARTS_DIR = PROJECT_ROOT / "reports" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  Bonus B4: Markowitz Efficient Frontier Portfolio Optimization")
print("=" * 60)

# Load NAV and master data
nav_df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
nav_df['date'] = pd.to_datetime(nav_df['date'])
fund_master = pd.read_csv(RAW_DIR / "01_fund_master.csv")

# Select 5 representative funds from different categories:
# 1. Gilt (Debt/Low Risk): 119120 (SBI Magnum Gilt Fund)
# 2. Large Cap (Moderate Risk): 100016 (HDFC Top 100 Fund)
# 3. Mid Cap (High Risk): 100033 (HDFC Mid-Cap Opportunities Fund)
# 4. Small Cap (Very High Risk): 118634 (Nippon India Small Cap Fund)
# 5. Liquid (Very Low Risk/Cash): 120503 (ICICI Prudential Liquid Fund)
selected_amfis = [119120, 100016, 100033, 118634, 120503]

# Pivot NAV to get daily returns for these funds
nav_pivot = nav_df[nav_df['amfi_code'].isin(selected_amfis)].pivot(index='date', columns='amfi_code', values='nav').sort_index()
daily_returns = nav_pivot.pct_change().dropna()

# Rename columns to scheme names
name_map = fund_master.set_index('amfi_code')['scheme_name'].to_dict()
daily_returns = daily_returns.rename(columns=name_map)
scheme_names = list(daily_returns.columns)

print("Selected Funds for Portfolio Optimization:")
for idx, name in enumerate(scheme_names):
    print(f"  {idx+1}. {name}")

# Compute annualized mean returns and covariance matrix
TRADING_DAYS = 252
mean_returns = daily_returns.mean() * TRADING_DAYS
cov_matrix = daily_returns.cov() * TRADING_DAYS
risk_free_rate = 0.065 # 6.5% Indian risk-free rate

# Simulate random portfolios
num_portfolios = 5000
results = np.zeros((3, num_portfolios))
weights_record = []

np.random.seed(42)
for i in range(num_portfolios):
    weights = np.random.random(len(selected_amfis))
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    # Portfolio expected return
    p_return = np.sum(weights * mean_returns)
    # Portfolio volatility
    p_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    # Portfolio Sharpe ratio
    p_sharpe = (p_return - risk_free_rate) / p_volatility
    
    results[0,i] = p_volatility
    results[1,i] = p_return
    results[2,i] = p_sharpe

# Find key portfolios
max_sharpe_idx = np.argmax(results[2])
sd_max_sharpe, rp_max_sharpe = results[0, max_sharpe_idx], results[1, max_sharpe_idx]
max_sharpe_weights = weights_record[max_sharpe_idx]

min_vol_idx = np.argmin(results[0])
sd_min_vol, rp_min_vol = results[0, min_vol_idx], results[1, min_vol_idx]
min_vol_weights = weights_record[min_vol_idx]

# Plotting the Efficient Frontier
fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(results[0]*100, results[1]*100, c=results[2], cmap='viridis', marker='o', s=10, alpha=0.3)
plt.colorbar(sc, label='Sharpe Ratio')

# Highlight Max Sharpe and Min Vol
ax.scatter(sd_max_sharpe*100, rp_max_sharpe*100, color='red', marker='*', s=200, label='Max Sharpe Ratio Portfolio')
ax.scatter(sd_min_vol*100, rp_min_vol*100, color='blue', marker='D', s=100, label='Minimum Volatility Portfolio')

ax.set_title('Markowitz Efficient Frontier - Selected 5 BlueStock Funds', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Annualized Volatility (Risk) (%)', fontsize=12)
ax.set_ylabel('Annualized Expected Return (%)', fontsize=12)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.5)

# Save chart
chart_path = CHARTS_DIR / "portfolio_efficient_frontier.png"
fig.savefig(chart_path, dpi=200, bbox_inches='tight')
plt.close(fig)

print(f"\n  Optimization complete! Saved chart to: {chart_path}")
print("\n🔥 Optimal Portfolios Allocation:")
print("-" * 60)
print(f"{'Fund Name':<45} | {'Max Sharpe %':<12} | {'Min Vol %':<10}")
print("-" * 60)
for idx, name in enumerate(scheme_names):
    short_name = name[:42] + "..." if len(name) > 45 else name
    print(f"{short_name:<45} | {max_sharpe_weights[idx]*100:>10.2f}% | {min_vol_weights[idx]*100:>8.2f}%")
print("-" * 60)
print(f"Expected Annualized Return:             | {rp_max_sharpe*100:>10.2f}% | {rp_min_vol*100:>8.2f}%")
print(f"Annualized Risk (Volatility):            | {sd_max_sharpe*100:>10.2f}% | {sd_min_vol*100:>8.2f}%")
print(f"Sharpe Ratio (Rf = 6.5%):               | {results[2, max_sharpe_idx]:>11.2f} | {results[2, min_vol_idx]:>9.2f}")
print("=" * 60)
