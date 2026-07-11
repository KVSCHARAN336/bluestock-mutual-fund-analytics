# 📊 Bluestock Mutual Fund Analytics Platform

> **Capstone Project — Full Deliverables Summary**  
> A production-grade end-to-end data engineering and advanced analytics pipeline for Indian mutual fund analytics.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0+-green?logo=pandas)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Project%20Complete-brightgreen)

---

## 🎯 Project Overview

The **Bluestock Mutual Fund Analytics Platform** is a comprehensive solution that ingests, validates, cleans, and analyzes mutual fund data from the Indian market. The project tracks **10 fund houses**, **40 schemes**, and provides real-time NAV tracking, portfolio optimization, and risk metrics forecasting.

---

## 📁 Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                        # Original CSV datasets
│   │   └── live_nav/               # Per-scheme live NAV downloads
│   ├── processed/                  # Cleaned & transformed datasets
│   └── db/
│       └── bluestock_mf.db         # SQLite Database
├── notebooks/                      # Standardized Jupyter notebooks
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb # Includes Monte Carlo & Portfolio Opt
├── sql/
│   ├── schema.sql                  # Idempotent DB schema
│   └── queries.sql                 # SQL analytics queries
├── dashboard/
│   └── streamlit_app.py            # Streamlit Interactive Dashboard
├── reports/                        # PDF & Markdown deliverables
│   ├── Final_Report.md             # Complete Capstone Final Report
│   ├── Dashboard.pdf               # Static export of dashboard layouts
│   ├── fund_scorecard.csv          # Risk-return stats (CAGR, Sharpe, MaxDD)
│   ├── alpha_beta.csv              # Beta coefficients vs benchmark
│   ├── var_cvar_report.csv         # Scheme-level tail risk metrics
│   ├── weekly_performance_summary.html # Generated HTML report (Bonus B5)
│   └── charts/                     # Generated charts & plots
├── scripts/
│   ├── etl_pipeline.py             # End-to-end ETL script
│   ├── compute_metrics.py          # Metrics calculation script
│   ├── recommender.py              # CLI fund recommender
│   ├── live_nav_fetch.py           # MFAPI live NAV fetcher
│   ├── run_analytics.py            # Advanced analytics runner
│   ├── monte_carlo.py              # B3: Monte Carlo projection
│   └── portfolio_optimization.py   # B4: Portfolio optimization
├── tests/
│   └── test_data_ingestion.py      # Unit tests
├── logs/                           # Automated runtime logs
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Quick Start & Usage

### 1. Set Up Environment
Create and activate a virtual environment, then install requirements:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the ETL Pipeline (D1 & D2)
Ingests raw data, cleans it, and loads the SQLite database:
```bash
python scripts/etl_pipeline.py
```

### 3. Compute Risk-Return Metrics (D4)
Computes Sharpe, Sortino, Alpha, Beta, Max Drawdown, and VaR:
```bash
python scripts/compute_metrics.py
```

### 4. Run CLI Fund Recommender (D6)
Retrieve top 3 funds matching a specified risk appetite (Low / Moderate / High):
```bash
python scripts/recommender.py --risk High
```

### 5. Launch the Interactive Dashboard (D5 & Bonus B2)
Launches the 4-page interactive Streamlit dashboard:
```bash
streamlit run dashboard/streamlit_app.py
```

### 6. Run Bonus Simulations (Bonus B3, B4 & B5)
- **Monte Carlo NAV Projection (B3):**
  ```bash
  python scripts/monte_carlo.py
  ```
- **Portfolio Optimization (B4):**
  ```bash
  python scripts/portfolio_optimization.py
  ```
- **HTML Weekly Performance Report (B5):**
  ```bash
  python scripts/email_report_generator.py
  ```

---

## 🏆 Completed Deliverables Scorecard

| ID | Weight | Deliverable | Location / Script |
|----|--------|-------------|-------------------|
| **D1** | 15% | ETL Pipeline | `scripts/etl_pipeline.py` |
| **D2** | 10% | SQLite Database | `data/db/bluestock_mf.db` |
| **D3** | 15% | EDA Notebook | `notebooks/03_eda_analysis.ipynb` |
| **D4** | 15% | Performance Metrics | `notebooks/04_performance_analytics.ipynb`, `scripts/compute_metrics.py` |
| **D5** | 20% | Interactive Dashboard | `dashboard/streamlit_app.py` / `reports/Dashboard.pdf` |
| **D6** | 10% | Advanced Analytics | `notebooks/05_advanced_analytics.ipynb`, `scripts/recommender.py` |
| **D7** | 15% | Final Report | `reports/Final_Report.md` |

### 🌟 Bonus Challenges Completed (+40 Marks Total)
- **B2 (+10)**: Build a Streamlit web app alternative to Power BI (`dashboard/streamlit_app.py`)
- **B3 (+10)**: 5-Year Monte Carlo NAV simulation with uncertainty bands (`scripts/monte_carlo.py` & integrated in Notebook 5)
- **B4 (+10)**: Markowitz Efficient Frontier portfolio optimization (`scripts/portfolio_optimization.py` & integrated in Notebook 5)
- **B5 (+10)**: Weekly HTML email report generator (`scripts/email_report_generator.py` & saved to `reports/weekly_performance_summary.html`)

---

## 👥 Team

**Bluestock Fintech Analytics Team**

*Built with ❤️ for the Indian Mutual Fund ecosystem*
