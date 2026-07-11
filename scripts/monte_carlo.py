"""
BlueStock MF Capstone — Monte Carlo NAV Projection
===================================================
Fulfills Bonus Challenge B3.
Projects NAV growth over 5 years (1260 trading days) using Geometric Brownian Motion (GBM).
Runs 1000 simulations and plots median path with 10th-90th percentile uncertainty bands.

Usage:
    python scripts/monte_carlo.py
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
print("  Bonus B3: Monte Carlo NAV Growth Simulation (5 Years)")
print("=" * 60)

# Load NAV history
nav_df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
nav_df['date'] = pd.to_datetime(nav_df['date'])

# Select a key representative fund (Mirae Asset Large Cap Fund - Regular - Growth, amfi_code = 148566 or similar)
# Let's find a fund with complete history
fund_counts = nav_df['amfi_code'].value_counts()
target_amfi = fund_counts.index[0] # The one with the most records

# Get scheme name
fund_master = pd.read_csv(RAW_DIR / "01_fund_master.csv")
scheme_name = fund_master[fund_master['amfi_code'] == target_amfi]['scheme_name'].values[0]
print(f"Running simulation for: {scheme_name} (AMFI: {target_amfi})")

fund_nav = nav_df[nav_df['amfi_code'] == target_amfi].sort_values('date').copy()
fund_nav['returns'] = fund_nav['nav'].pct_change()
returns = fund_nav['returns'].dropna()

# Calculate parameters
mu = returns.mean()  # Daily mean return
sigma = returns.std()  # Daily volatility
last_nav = fund_nav['nav'].iloc[-1]

print(f"  Historical Daily Mean Return: {mu:.6f} ({mu*252*100:.2f}% annualized)")
print(f"  Historical Daily Volatility:  {sigma:.6f} ({sigma*np.sqrt(252)*100:.2f}% annualized)")
print(f"  Latest NAV (Initial Value):  ₹{last_nav:.2f}")

# Simulation parameters
T = 5  # Years
N_DAYS = 5 * 252  # Trading days
N_SIMS = 1000

# Geometric Brownian Motion simulation
# dS = mu * S * dt + sigma * S * dW
dt = 1
sim_nav = np.zeros((N_DAYS + 1, N_SIMS))
sim_nav[0] = last_nav

for t in range(1, N_DAYS + 1):
    # Standard normal random variables
    Z = np.random.normal(0, 1, N_SIMS)
    sim_nav[t] = sim_nav[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)

# Compute percentiles
median_path = np.percentile(sim_nav, 50, axis=1)
upper_band = np.percentile(sim_nav, 90, axis=1)
lower_band = np.percentile(sim_nav, 10, axis=1)
worst_path = np.percentile(sim_nav, 5, axis=1)
best_path = np.percentile(sim_nav, 95, axis=1)

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
sns.set_theme(style="whitegrid")

days = np.arange(N_DAYS + 1)
years = days / 252

# Plot some individual paths for illustration
for i in range(15):
    ax.plot(years, sim_nav[:, i], color='lightblue', alpha=0.3, linewidth=0.8)

# Plot statistical bands
ax.plot(years, median_path, color='#1e3a8a', linewidth=2.5, label='Median Projection (50th percentile)')
ax.fill_between(years, lower_band, upper_band, color='#3b82f6', alpha=0.3, label='Uncertainty Band (10th - 90th percentile)')
ax.fill_between(years, worst_path, best_path, color='#3b82f6', alpha=0.1, label='Outer Band (5th - 95th percentile)')

ax.set_title(f"5-Year Monte Carlo NAV Growth Simulation\n{scheme_name}", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Years", fontsize=12)
ax.set_ylabel("NAV (₹)", fontsize=12)
ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
ax.set_xlim(0, T)
ax.grid(True, linestyle='--', alpha=0.5)

# Formatting y-axis with Currency Symbol
ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('₹%.0f'))

# Save plot
chart_path = CHARTS_DIR / "monte_carlo_simulation.png"
fig.savefig(chart_path, dpi=200, bbox_inches='tight')
plt.close(fig)

print(f"\n  Simulation complete! Saved chart to: {chart_path}")
print(f"  Projected NAV in 5 years:")
print(f"    Optimistic (90th percentile):  ₹{upper_band[-1]:.2f}")
print(f"    Expected (Median / 50th):      ₹{median_path[-1]:.2f}")
print(f"    Pessimistic (10th percentile):  ₹{lower_band[-1]:.2f}")
print("=" * 60)
