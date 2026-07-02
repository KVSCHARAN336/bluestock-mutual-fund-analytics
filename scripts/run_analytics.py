"""
Execute Advanced_Analytics notebook logic as a standalone script.
Generates: var_cvar_report.csv, rolling_sharpe_chart.png
Run with: python run_analytics.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, os

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({
    'figure.figsize': (14, 6),
    'figure.dpi': 120,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})

ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, 'reports', 'charts'), exist_ok=True)

print("=" * 70)
print("  BlueStock MF - Advanced Analytics Runner")
print("=" * 70)

# ======================================================================
# 1. Load Data
# ======================================================================
print("\n[1/7] Loading data...")
fund_master  = pd.read_csv(os.path.join(ROOT, '01_fund_master.csv'))
nav_df       = pd.read_csv(os.path.join(ROOT, '02_nav_history.csv'))
perf_df      = pd.read_csv(os.path.join(ROOT, '07_scheme_performance.csv'))
tx_df        = pd.read_csv(os.path.join(ROOT, '08_investor_transactions.csv'))
holdings_df  = pd.read_csv(os.path.join(ROOT, '09_portfolio_holdings - 09_portfolio_holdings.csv'))

nav_df['date'] = pd.to_datetime(nav_df['date'])
tx_df['transaction_date'] = pd.to_datetime(tx_df['transaction_date'])

amfi_to_name  = fund_master.set_index('amfi_code')['scheme_name'].to_dict()
amfi_to_house = fund_master.set_index('amfi_code')['fund_house'].to_dict()
amfi_to_cat   = fund_master.set_index('amfi_code')['category'].to_dict()

nav_pivot = nav_df.pivot(index='date', columns='amfi_code', values='nav').sort_index()
daily_returns = nav_pivot.pct_change().dropna(how='all')

print(f"  Loaded {len(fund_master)} schemes, {len(nav_df):,} NAV records, {len(tx_df):,} transactions")
print(f"  NAV date range: {nav_df['date'].min().date()} -> {nav_df['date'].max().date()}")

# ======================================================================
# 2. Historical VaR (95%) & CVaR
# ======================================================================
print("\n[2/7] Computing VaR (95%) & CVaR for all schemes...")

var_results = []
for amfi in daily_returns.columns:
    rets = daily_returns[amfi].dropna()
    if len(rets) < 30:
        continue
    var_95 = rets.quantile(0.05)
    cvar = rets[rets <= var_95].mean()
    var_results.append({
        'amfi_code':    amfi,
        'scheme_name':  amfi_to_name.get(amfi, str(amfi)),
        'fund_house':   amfi_to_house.get(amfi, 'Unknown'),
        'category':     amfi_to_cat.get(amfi, 'Unknown'),
        'VaR_95_pct':   round(var_95 * 100, 4),
        'CVaR_pct':     round(cvar * 100, 4),
        'observations': len(rets),
    })

var_cvar_df = pd.DataFrame(var_results)
risk_map = perf_df.set_index('amfi_code')['risk_grade'].to_dict()
var_cvar_df['risk_grade'] = var_cvar_df['amfi_code'].map(risk_map)
var_cvar_df = var_cvar_df.sort_values('VaR_95_pct').reset_index(drop=True)

csv_path = os.path.join(ROOT, 'reports', 'var_cvar_report.csv')
var_cvar_df.to_csv(csv_path, index=False)
print(f"  Saved: {csv_path}  ({len(var_cvar_df)} schemes)")

print("\n  Top 10 Riskiest Funds by VaR(95%):")
for _, row in var_cvar_df.head(10).iterrows():
    print(f"    {row['VaR_95_pct']:>7.3f}%  CVaR: {row['CVaR_pct']:>7.3f}%  {row['scheme_name'][:50]}")

# ======================================================================
# 3. Rolling 90-Day Sharpe Ratio
# ======================================================================
print("\n[3/7] Computing Rolling 90-Day Sharpe...")

KEY_FUNDS = {
    119120: 'SBI Magnum Gilt Fund (Low)',
    100016: 'HDFC Top 100 Fund (Moderate)',
    100033: 'HDFC Mid-Cap Opps (High)',
    120843: 'Kotak Flexicap Fund (Mod-High)',
    119598: 'SBI Small Cap Fund (Very High)',
}

WINDOW = 90
ANNUALIZE = np.sqrt(252)

fig, ax = plt.subplots(figsize=(15, 7))
palette = ['#1565c0', '#2e7d32', '#e65100', '#6a1b9a', '#c62828']

for idx, (amfi, label) in enumerate(KEY_FUNDS.items()):
    rets = daily_returns[amfi].dropna()
    rolling_mean = rets.rolling(WINDOW).mean()
    rolling_std  = rets.rolling(WINDOW).std()
    rolling_sharpe = (rolling_mean / rolling_std) * ANNUALIZE
    rolling_sharpe = rolling_sharpe.dropna()
    ax.plot(rolling_sharpe.index, rolling_sharpe.values,
            label=label, color=palette[idx], linewidth=1.5, alpha=0.85)

ax.axhline(y=0, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)
ax.axhline(y=1, color='green', linestyle=':', linewidth=0.7, alpha=0.5, label='Sharpe = 1')
ax.axhline(y=-1, color='red', linestyle=':', linewidth=0.7, alpha=0.5, label='Sharpe = -1')

ax.set_title('Rolling 90-Day Sharpe Ratio - 5 Key Funds Across Risk Tiers', fontweight='bold', fontsize=14)
ax.set_xlabel('Date')
ax.set_ylabel('Annualized Sharpe Ratio')
ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()

chart_path = os.path.join(ROOT, 'reports', 'charts', 'rolling_sharpe_chart.png')
fig.savefig(chart_path, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f"  Saved: {chart_path}")

# ======================================================================
# 4. Investor Cohort Analysis
# ======================================================================
print("\n[4/7] Running Investor Cohort Analysis...")

first_tx = tx_df.groupby('investor_id')['transaction_date'].min().reset_index()
first_tx.columns = ['investor_id', 'first_tx_date']
first_tx['cohort_year'] = first_tx['first_tx_date'].dt.year

tx_cohort = tx_df.merge(first_tx[['investor_id', 'cohort_year']], on='investor_id')

sip_tx = tx_cohort[tx_cohort['transaction_type'] == 'SIP']
avg_sip = sip_tx.groupby('cohort_year')['amount_inr'].mean().rename('avg_sip_amount')

invest_tx = tx_cohort[tx_cohort['transaction_type'].isin(['SIP', 'Lumpsum'])]
total_invested = invest_tx.groupby('cohort_year')['amount_inr'].sum().rename('total_invested_inr')

top_fund = (tx_cohort.groupby('cohort_year')['amfi_code']
            .agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else np.nan)
            .rename('top_amfi_code'))

cohort_summary = pd.concat([avg_sip, total_invested, top_fund], axis=1).reset_index()
cohort_summary['top_fund_name'] = cohort_summary['top_amfi_code'].map(amfi_to_name)
cohort_summary['investor_count'] = first_tx.groupby('cohort_year').size().values

print("\n  Cohort Summary:")
for _, row in cohort_summary.iterrows():
    print(f"    {int(row['cohort_year'])} | Investors: {int(row['investor_count']):>5} | "
          f"Avg SIP: Rs.{row['avg_sip_amount']:>9,.0f} | "
          f"Total: Rs.{row['total_invested_inr']/1e7:>7.1f} Cr | "
          f"Top Fund: {str(row['top_fund_name'])[:35]}")

# ======================================================================
# 5. SIP Continuity Analysis
# ======================================================================
print("\n[5/7] Running SIP Continuity Analysis...")

sip_all = tx_df[tx_df['transaction_type'] == 'SIP'].sort_values(
    ['investor_id', 'transaction_date'])
sip_counts = sip_all.groupby('investor_id').size().rename('sip_count')
active_investors = sip_counts[sip_counts >= 6].index
sip_filtered = sip_all[sip_all['investor_id'].isin(active_investors)].copy()

def avg_gap_days(group):
    dates = group['transaction_date'].sort_values()
    gaps = dates.diff().dt.days.dropna()
    return gaps.mean() if len(gaps) > 0 else np.nan

investor_gaps = sip_filtered.groupby('investor_id').apply(avg_gap_days).rename('avg_gap_days')
investor_gaps = investor_gaps.dropna()

sip_continuity = pd.DataFrame(investor_gaps)
sip_continuity['sip_count'] = sip_counts.loc[sip_continuity.index]
sip_continuity['status'] = np.where(sip_continuity['avg_gap_days'] > 35, 'At-Risk', 'Regular')

total_sip_investors = len(sip_counts)
qualified_investors = len(sip_continuity)
at_risk_count = (sip_continuity['status'] == 'At-Risk').sum()
at_risk_pct = at_risk_count / qualified_investors * 100 if qualified_investors > 0 else 0

print(f"  Total SIP investors:           {total_sip_investors:,}")
print(f"  Investors with 6+ SIPs:        {qualified_investors:,}")
print(f"  At-Risk (avg gap > 35 days):   {at_risk_count:,}  ({at_risk_pct:.1f}%)")
print(f"  Regular:                       {qualified_investors - at_risk_count:,}")
print(f"  Avg gap (all qualified):       {sip_continuity['avg_gap_days'].mean():.1f} days")
print(f"  Median gap:                    {sip_continuity['avg_gap_days'].median():.1f} days")

# ======================================================================
# 6. Sector HHI Concentration
# ======================================================================
print("\n[6/7] Computing Sector HHI Concentration...")

sector_weights = (holdings_df.groupby(['amfi_code', 'sector'])['weight_pct']
                  .sum().reset_index())
hhi_per_fund = (sector_weights.groupby('amfi_code')
                .apply(lambda g: (g['weight_pct'] ** 2).sum())
                .rename('HHI'))

hhi_df = hhi_per_fund.reset_index()
hhi_df['scheme_name'] = hhi_df['amfi_code'].map(amfi_to_name)
hhi_df['category'] = hhi_df['amfi_code'].map(amfi_to_cat)

equity_amfi = fund_master[fund_master['category'] == 'Equity']['amfi_code'].tolist()
hhi_equity = hhi_df[hhi_df['amfi_code'].isin(equity_amfi)].copy()

def classify_hhi(val):
    if val > 2500:
        return 'Highly Concentrated'
    elif val > 1500:
        return 'Moderately Concentrated'
    else:
        return 'Diversified'

hhi_equity['concentration'] = hhi_equity['HHI'].apply(classify_hhi)
hhi_equity = hhi_equity.sort_values('HHI', ascending=False).reset_index(drop=True)

print("\n  HHI Concentration Distribution:")
for status, count in hhi_equity['concentration'].value_counts().items():
    print(f"    {status}: {count}")
print("\n  Top 10 by HHI:")
for _, row in hhi_equity.head(10).iterrows():
    print(f"    HHI {row['HHI']:>8.1f} | {row['concentration']:<25} | {row['scheme_name'][:45]}")

# ======================================================================
# 7. Fund Recommender
# ======================================================================
print("\n[7/7] Fund Recommendations by Risk Appetite...")

RISK_MAP = {
    'Low':      ['Low'],
    'Moderate': ['Moderate'],
    'High':     ['High', 'Moderately High', 'Very High'],
}

DISPLAY_COLS = ['scheme_name', 'fund_house', 'risk_grade', 'sharpe_ratio',
                'return_1yr_pct', 'return_3yr_pct', 'expense_ratio_pct']

for level in ['Low', 'Moderate', 'High']:
    emoji = {'Low': '[LOW]', 'Moderate': '[MOD]', 'High': '[HIGH]'}[level]
    grades = RISK_MAP[level]
    filtered = perf_df[perf_df['risk_grade'].isin(grades)].copy()
    top3 = filtered.sort_values('sharpe_ratio', ascending=False).head(3)
    cols = [c for c in DISPLAY_COLS if c in top3.columns]
    print(f"\n  {emoji} Risk Appetite: {level}")
    print("  " + "-" * 90)
    for _, row in top3[cols].iterrows():
        print(f"    Sharpe {row['sharpe_ratio']:.2f} | 1yr {row['return_1yr_pct']:>5.1f}% | "
              f"3yr {row['return_3yr_pct']:>5.1f}% | ER {row['expense_ratio_pct']:.2f}% | "
              f"{row['scheme_name'][:45]}")

print("\n" + "=" * 70)
print("  All analytics complete!")
print(f"  var_cvar_report.csv      -> {csv_path}")
print(f"  rolling_sharpe_chart.png -> {chart_path}")
print("=" * 70)
