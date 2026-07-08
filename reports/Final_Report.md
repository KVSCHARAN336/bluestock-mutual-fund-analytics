# BlueStock Mutual Fund Analytics — Final Report

**BlueStock Fintech Capstone Project**  
**Date:** July 2026  
**Author:** BlueStock Fintech Analytics Team

---

## Executive Summary

This capstone project builds a comprehensive **end-to-end mutual fund analytics platform** covering 40 schemes across 10 AMCs (Asset Management Companies) in India. The platform spans data ingestion, cleaning, exploratory analysis, performance benchmarking, risk quantification, investor behavior analytics, and an automated fund recommender.

**Key Deliverables:**
- Unified ETL pipeline loading 10 CSV datasets into SQLite
- 5 Jupyter notebooks covering ingestion, cleaning, EDA, performance, and advanced analytics
- Interactive 4-page dashboard with cross-filtering
- VaR/CVaR risk reports, fund scorecards, and alpha/beta analysis
- CLI-based fund recommender by risk appetite
- Rolling Sharpe, investor cohort, SIP continuity, and sector HHI analyses

**Key Findings:**
- Small-cap funds carry **17× more daily tail risk** than liquid funds (VaR −2.69% vs −0.02%)
- **97.8%** of SIP investors with 6+ transactions show gap > 35 days — indicating churn risk
- Top Sharpe performers: Mirae Asset Large Cap (1.45), Kotak Flexicap (1.31)
- **4 equity funds** exceed HHI 2,500 — highly concentrated sector exposure

---

## 1. Data Sources & ETL Pipeline

### 1.1 Datasets

| # | Dataset | Records | Key Fields |
|---|---------|---------|------------|
| 01 | Fund Master | 40 | amfi_code, scheme_name, fund_house, category |
| 02 | NAV History | 46,000 | amfi_code, date, nav (Jan 2022 – May 2026) |
| 03 | AUM by Fund House | 90 | fund_house, date, aum_crore |
| 04 | Monthly SIP Inflows | 48 | month, sip_inflow_crore, active_accounts |
| 05 | Category Inflows | 144 | category, month, inflow_crore |
| 06 | Industry Folio Count | 21 | year, total_folios |
| 07 | Scheme Performance | 40 | sharpe_ratio, alpha, beta, returns, risk_grade |
| 08 | Investor Transactions | 32,778 | investor_id, transaction_type, amount_inr |
| 09 | Portfolio Holdings | 322 | amfi_code, stock, sector, weight_pct |
| 10 | Benchmark Indices | 8,050 | date, nifty_50, nifty_midcap_150 |

### 1.2 ETL Pipeline (`scripts/etl_pipeline.py`)

The unified ETL pipeline runs end-to-end in **~1.2 seconds** with zero manual steps:

1. **Ingest:** Load all 10 raw CSVs from `data/raw/`, validate file existence
2. **Clean:** Parse dates, forward-fill NAV gaps (weekends/holidays), standardise transaction types, coerce numeric columns, remove invalid records
3. **Load:** Apply SQL schema and load into SQLite at `data/db/bluestock_mf.db` with 6 normalised tables

**Key cleaning operations:**
- NAV: `ffill()` within each fund group to handle non-trading days
- Transactions: Standardise SIP/Lumpsum/Redemption labels, filter amount > 0
- Performance: Coerce all return/ratio columns to numeric with `errors='coerce'`

### 1.3 Database Schema

| Table | Type | Rows | Primary Key |
|-------|------|------|-------------|
| dim_fund | Dimension | 40 | amfi_code |
| dim_date | Dimension | — | date_id |
| fact_nav | Fact | 46,000 | amfi_code + nav_date |
| fact_transactions | Fact | 32,778 | tx_id (auto) |
| fact_performance | Fact | 40 | amfi_code |
| fact_aum | Fact | 90 | fund_house + quarter |
| sip_inflows | Fact | 48 | month |

---

## 2. Exploratory Data Analysis (EDA)

### 2.1 Industry Overview
- Indian MF industry AUM grew from **₹37.7 lakh crore** (2022) to **₹66.2 lakh crore** (2026)
- Total folios crossed **21 crore** — reflecting deepening retail participation
- SIP monthly inflows peaked at **₹26,000+ crore** in late 2024

### 2.2 Fund Performance Distribution
- **Equity funds** delivered 10–20% 1-year returns on average
- **Debt/Liquid funds** returned 5–9% with significantly lower volatility
- Expense ratios range from 0.20% (Direct ETFs) to 2.5% (Regular Small Caps)

### 2.3 Investor Demographics
- **5,000 unique investors** across 40 schemes
- Transaction mix: SIP (55%), Lumpsum (25%), Redemption (20%)
- Average SIP amount: ₹10,997 (2024 cohort), ₹13,505 (2025 cohort)

### 2.4 Key EDA Charts
- NAV trend lines across risk tiers
- AUM growth trajectory by fund house
- SIP inflow monthly trend with YoY growth
- Category-wise inflow heatmap
- Investor demographics (age, gender, state, tier distribution)

---

## 3. Performance Analytics

### 3.1 Risk-Return Metrics

All metrics computed using **252 trading days** for annualisation (not calendar days).

| Metric | Formula | Purpose |
|--------|---------|---------|
| Sharpe Ratio | (Rp − Rf) / σp × √252 | Risk-adjusted return |
| Sortino Ratio | (Rp − Rf) / σdownside × √252 | Downside-adjusted return |
| Alpha (Jensen's) | Rp − [Rf + β(Rm − Rf)] | Excess return vs benchmark |
| Beta | Cov(Rp, Rm) / Var(Rm) | Market sensitivity |
| Max Drawdown | (Peak − Trough) / Peak | Worst peak-to-trough decline |
| CAGR | (Vfinal/Vinitial)^(252/n) − 1 | Annualised compound growth |

### 3.2 Top Performers by Sharpe Ratio

| Rank | Fund | Sharpe | CAGR | Max DD |
|------|------|--------|------|--------|
| 1 | Mirae Asset Large Cap | 1.45 | 29.2% | −11.3% |
| 2 | Kotak Flexicap Fund | 1.31 | 29.2% | −13.0% |
| 3 | Mirae Asset Tax Saver | 1.23 | 30.4% | −16.4% |
| 4 | SBI Bluechip Fund | 1.21 | 24.8% | −15.0% |
| 5 | ICICI Pru Midcap Fund | 1.18 | 32.1% | −18.2% |

### 3.3 Alpha & Beta Analysis
- **Positive alpha funds:** Mirae Asset Large Cap, Kotak Flexicap — consistently generating excess returns over Nifty 50
- **High beta (>1.2):** Small-cap and mid-cap funds — amplified market movements
- **Low beta (<0.8):** Gilt and liquid funds — defensive positioning

---

## 4. Advanced Analytics

### 4.1 Historical VaR (95%) & CVaR

**Value at Risk** at 95% confidence = 5th percentile of daily return distribution.  
**CVaR (Expected Shortfall)** = mean of all returns below the VaR threshold.

| Risk Tier | Avg VaR (95%) | Avg CVaR | Fund Count |
|-----------|---------------|----------|------------|
| Low (Gilt/Liquid) | −0.15% | −0.21% | 6 |
| Moderate (Large Cap) | −1.36% | −1.72% | 14 |
| High (Mid Cap) | −1.84% | −2.31% | 8 |
| Very High (Small Cap) | −2.55% | −3.15% | 6 |

**Finding:** CVaR is consistently **1.2–1.4× worse** than VaR across all tiers, confirming fat-tail distributions in equity fund returns.

### 4.2 Rolling 90-Day Sharpe Ratio

Rolling Sharpe computed as: `rolling(90).mean() / rolling(90).std() × √252`

5 key funds plotted across risk tiers (2022–2026):
- **Gilt funds** maintain stable Sharpe (1.5–4.0) regardless of market regime
- **Small-cap funds** show the highest Sharpe volatility (−4 to +4)
- All equity funds dipped below 0 during the late-2024/early-2025 correction

### 4.3 Investor Cohort Analysis

Investors grouped by year of first transaction:

| Cohort | Investors | Avg SIP | Total Invested | Top Fund |
|--------|-----------|---------|----------------|----------|
| 2024 | 4,803 | ₹10,997 | ₹225.8 Crore | Mirae Asset Emerging Bluechip |
| 2025 | 197 | ₹13,505 | ₹1.9 Crore | SBI Small Cap – Direct |

**Finding:** 2025 cohort invests 23% higher per SIP, with a tilt toward small-cap aggression.

### 4.4 SIP Continuity Analysis

| Metric | Value |
|--------|-------|
| Total SIP investors | 4,762 |
| Qualified (6+ SIPs) | 1,362 |
| At-Risk (gap > 35 days) | 1,332 (97.8%) |
| Average gap | 64.9 days |
| Median gap | 64.7 days |

**Recommendation:** AMCs should deploy nudge campaigns (SMS/email) when gap exceeds 45 days. Historical data suggests 2 consecutive missed SIPs leads to 60%+ permanent discontinuation.

### 4.5 Sector HHI Concentration

Herfindahl-Hirschman Index = Σ(weight_i²) per fund across sectors.

| Classification | HHI Range | Fund Count |
|---------------|-----------|------------|
| Highly Concentrated | > 2,500 | 4 |
| Moderately Concentrated | 1,500–2,500 | 27 |
| Diversified | < 1,500 | 3 |

Most concentrated: **Axis Bluechip (HHI 2,968)**, driven by heavy Banking + IT sector weights.

### 4.6 Fund Recommender

Simple rule-based recommender mapping risk appetite to top funds by Sharpe ratio:

| Risk Level | #1 Pick | Sharpe |
|-----------|---------|--------|
| Low | ICICI Pru Liquid Fund | 7.68 |
| Moderate | HDFC Top 100 Fund | 1.06 |
| High | Kotak Flexicap Fund | 0.98 |

CLI: `python scripts/recommender.py --risk High`

---

## 5. Dashboard Design

4-page interactive dashboard with cross-filtering:

1. **Industry Overview** — AUM growth, folio count, SIP trends, category distribution
2. **Fund Performance** — NAV trends, Sharpe/Sortino comparison, benchmark overlay
3. **Investor Analytics** — Demographics, transaction patterns, cohort analysis
4. **SIP & Market Trends** — SIP inflow timeseries, category flows, growth metrics

Each page includes 2+ interactive slicers (fund house, category, time period, risk grade).

---

## 6. Conclusions & Recommendations

### For Investors:
1. **Small-cap funds** offer highest CAGR (25–35%) but carry 17× more daily tail risk than liquid funds — suitable only for 5+ year horizons
2. **Large-cap funds** with Sharpe > 1.0 (Mirae Asset, HDFC Top 100) offer the best risk-adjusted returns
3. Investors holding multiple large-cap funds should check **cross-fund sector overlap** — the "diversification illusion" is real

### For AMCs:
1. **SIP retention** is critical — deploy automated nudge campaigns at the 35-day gap mark
2. **2025 cohort** shows higher SIP amounts but smaller total investment — focus on tenure extension
3. **Direct plan adoption** is growing — ensure digital onboarding experience matches expectations

### For Portfolio Managers:
1. Funds with HHI > 2,500 should consider **sector rebalancing** to reduce concentration risk
2. Rolling Sharpe dropping below −1.0 for small-cap funds is a reliable **regime-change signal**
3. Alpha generation is strongest in **mid-cap and flexi-cap** categories — active management adds value here

---

## Appendix: Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/               ← 10 original CSV files
│   ├── processed/         ← 10 cleaned CSVs
│   └── db/                ← bluestock_mf.db (SQLite)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/
│   ├── etl_pipeline.py         ← Unified end-to-end ETL
│   ├── compute_metrics.py      ← Sharpe, Alpha, Beta, VaR calculator
│   ├── recommender.py          ← CLI fund recommender
│   ├── live_nav_fetch.py       ← Live NAV fetcher from mfapi.in
│   └── run_analytics.py        ← Advanced analytics runner
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── reports/
│   ├── Final_Report.md
│   ├── Dashboard.pdf
│   ├── fund_scorecard.csv
│   ├── alpha_beta.csv
│   ├── var_cvar_report.csv
│   └── charts/                 ← 18 generated charts
└── README.md
```

**GitHub:** github.com/KVSCHARAN336/bluestock-mutual-fund-analytics
