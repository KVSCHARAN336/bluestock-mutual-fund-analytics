import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    # Metadata for the notebook
    nb['metadata'] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    }

    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("# Day 4: Advanced Performance Analytics"))

    cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plotting styles
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

os.makedirs('../reports', exist_ok=True)
os.makedirs('../reports/charts', exist_ok=True)

# Define paths
data_dir = '../data/processed'
"""))

    cells.append(nbf.v4.new_markdown_cell("## 1. Load Data"))
    
    cells.append(nbf.v4.new_code_cell("""\
# Load NAV data
nav_df = pd.read_csv(f'{data_dir}/clean_nav_history.csv')
nav_df['date'] = pd.to_datetime(nav_df['date'])

# Load Fund Master
fund_master = pd.read_csv(f'{data_dir}/clean_fund_master.csv')

# Load Benchmark Indices
bench_df = pd.read_csv(f'{data_dir}/clean_benchmark_indices.csv')
bench_df['date'] = pd.to_datetime(bench_df['date'])

# Create a mapping dictionary for scheme names
amfi_to_name = fund_master.set_index('amfi_code')['scheme_name'].to_dict()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 2. Calculate Daily Returns"))

    cells.append(nbf.v4.new_code_cell("""\
# Pivot NAV data
nav_pivot = nav_df.pivot(index='date', columns='amfi_code', values='nav')
nav_pivot.columns = [amfi_to_name.get(col, col) for col in nav_pivot.columns]
nav_pivot.sort_index(inplace=True)

# Calculate Daily Returns
daily_returns = nav_pivot.pct_change().dropna(how='all')

print("Daily Returns Shape:", daily_returns.shape)
daily_returns.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 3. Calculate CAGR (1yr, 3yr, 5yr)"))
    
    cells.append(nbf.v4.new_code_cell("""\
def calculate_cagr(df, years):
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(years=years)
    
    cagrs = {}
    for col in df.columns:
        valid_data = df[col].dropna()
        if len(valid_data) == 0:
            cagrs[col] = np.nan
            continue
            
        fund_end = valid_data.index.max()
        target_start = fund_end - pd.DateOffset(years=years)
        
        if target_start < valid_data.index.min():
            actual_start = valid_data.index.min()
        else:
            # First date on or after target_start
            actual_start = valid_data[valid_data.index >= target_start].index[0]
            
        val_start = valid_data.loc[actual_start]
        val_end = valid_data.loc[fund_end]
        
        actual_years = (fund_end - actual_start).days / 365.25
        
        if actual_years <= 0 or val_start <= 0:
            cagrs[col] = np.nan
        else:
            cagrs[col] = (val_end / val_start) ** (1 / actual_years) - 1
            
    return pd.Series(cagrs)

cagr_1yr = calculate_cagr(nav_pivot, 1)
cagr_3yr = calculate_cagr(nav_pivot, 3)
cagr_5yr = calculate_cagr(nav_pivot, 5) # Will compute over max available (~4 years)

cagr_df = pd.DataFrame({
    'CAGR_1yr': cagr_1yr,
    'CAGR_3yr': cagr_3yr,
    'CAGR_5yr_max': cagr_5yr
})
cagr_df.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 4. Compute Sharpe and Sortino Ratios"))

    cells.append(nbf.v4.new_code_cell("""\
risk_free_rate = 0.065
daily_rf = (1 + risk_free_rate) ** (1/252) - 1

# Sharpe Ratio
ann_returns = daily_returns.mean() * 252
ann_volatility = daily_returns.std() * np.sqrt(252)
sharpe_ratio = (ann_returns - risk_free_rate) / ann_volatility

# Sortino Ratio
downside_returns = daily_returns.copy()
downside_returns[downside_returns > 0] = 0
downside_volatility = downside_returns.std() * np.sqrt(252)
sortino_ratio = (ann_returns - risk_free_rate) / downside_volatility

ratios_df = pd.DataFrame({
    'Sharpe_Ratio': sharpe_ratio,
    'Sortino_Ratio': sortino_ratio
})
ratios_df.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 5. Calculate Alpha and Beta against NIFTY 100"))

    cells.append(nbf.v4.new_code_cell("""\
# Prepare NIFTY100
nifty100 = bench_df[bench_df['index_name'] == 'NIFTY100'].set_index('date')['close_value']
nifty100.sort_index(inplace=True)
nifty100_returns = nifty100.pct_change().dropna()

alphas = {}
betas = {}

for col in daily_returns.columns:
    merged = pd.concat([daily_returns[col], nifty100_returns], axis=1).dropna()
    if len(merged) < 50:
        alphas[col] = np.nan
        betas[col] = np.nan
        continue
        
    slope, intercept, r_value, p_value, std_err = stats.linregress(merged.iloc[:, 1], merged.iloc[:, 0])
    
    betas[col] = slope
    alphas[col] = intercept * 252 # Annualize alpha

alpha_beta_df = pd.DataFrame({
    'scheme_name': list(alphas.keys()),
    'Alpha': list(alphas.values()),
    'Beta': list(betas.values())
})

alpha_beta_df.to_csv('../reports/alpha_beta.csv', index=False)
alpha_beta_df.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 6. Maximum Drawdown"))
    
    cells.append(nbf.v4.new_code_cell("""\
rolling_max = nav_pivot.cummax()
drawdowns = (nav_pivot / rolling_max) - 1
max_drawdown = drawdowns.min()

max_dd_df = pd.DataFrame({'Max_Drawdown': max_drawdown})
max_dd_df.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 7. Fund Scorecard (0-100)"))

    cells.append(nbf.v4.new_code_cell("""\
# Combine all metrics
scorecard = pd.concat([cagr_df, ratios_df, max_dd_df], axis=1)
scorecard = scorecard.merge(alpha_beta_df.set_index('scheme_name'), left_index=True, right_index=True)

# Add Expense Ratio
fund_master_idx = fund_master.set_index('scheme_name')
scorecard = scorecard.join(fund_master_idx['expense_ratio_pct'])

# Ranks
rank_3yr_ret = scorecard['CAGR_3yr'].rank(pct=True)
rank_sharpe = scorecard['Sharpe_Ratio'].rank(pct=True)
rank_alpha = scorecard['Alpha'].rank(pct=True)
rank_exp = scorecard['expense_ratio_pct'].rank(pct=True, ascending=False) # Lower is better
rank_dd = scorecard['Max_Drawdown'].rank(pct=True) # Higher (closer to 0) is better

# Composite Score: 30% × 3yr return + 25% × Sharpe + 20% × Alpha + 15% × inverse Expense Ratio + 10% × inverse Max DD
scorecard['Composite_Score'] = (
    0.30 * rank_3yr_ret + 
    0.25 * rank_sharpe + 
    0.20 * rank_alpha + 
    0.15 * rank_exp + 
    0.10 * rank_dd
) * 100

scorecard = scorecard.sort_values(by='Composite_Score', ascending=False)
scorecard.index.name = 'scheme_name'
scorecard.reset_index(inplace=True)

scorecard.to_csv('../reports/fund_scorecard.csv', index=False)
scorecard.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("## 8. Benchmark Comparison Chart"))

    cells.append(nbf.v4.new_code_cell("""\
top_5_funds = scorecard.head(5)['scheme_name'].tolist()

# Get normalized cumulative returns over 3 years
end_date = nav_pivot.index.max()
start_date = end_date - pd.DateOffset(years=3)

# Filter data
nav_3y = nav_pivot.loc[start_date:end_date, top_5_funds].dropna(how='all')
if len(nav_3y) > 0:
    nav_3y = nav_3y / nav_3y.iloc[0] * 100

# Get benchmarks
nifty50 = bench_df[bench_df['index_name'] == 'NIFTY50'].set_index('date')['close_value']
nifty100 = bench_df[bench_df['index_name'] == 'NIFTY100'].set_index('date')['close_value']

bench_3y = pd.concat([nifty50, nifty100], axis=1, keys=['NIFTY50', 'NIFTY100'])
bench_3y = bench_3y.loc[start_date:end_date].dropna(how='all')
if len(bench_3y) > 0:
    bench_3y = bench_3y / bench_3y.iloc[0] * 100

plt.figure(figsize=(14, 7))

for fund in top_5_funds:
    if fund in nav_3y.columns:
        plt.plot(nav_3y.index, nav_3y[fund], label=fund, linewidth=2)

plt.plot(bench_3y.index, bench_3y['NIFTY50'], label='NIFTY 50', color='black', linestyle='--', linewidth=2.5)
plt.plot(bench_3y.index, bench_3y['NIFTY100'], label='NIFTY 100', color='gray', linestyle='-.', linewidth=2.5)

plt.title('Top 5 Funds vs Benchmarks (3-Year Cumulative Return)')
plt.xlabel('Date')
plt.ylabel('Normalized Value (Base = 100)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.savefig('../reports/charts/benchmark_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Compute tracking error for top 5 funds vs NIFTY 100
tracking_errors = {}
for fund in top_5_funds:
    if fund in daily_returns.columns:
        diff = daily_returns[fund] - nifty100_returns
        tracking_errors[fund] = diff.std() * np.sqrt(252)

te_df = pd.DataFrame(list(tracking_errors.items()), columns=['Fund', 'Tracking_Error'])
print("Tracking Error for Top 5 Funds:")
print(te_df)
"""))

    nb['cells'] = cells
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/Performance_Analytics.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print("Notebook Performance_Analytics.ipynb successfully generated!")

if __name__ == '__main__':
    create_notebook()
