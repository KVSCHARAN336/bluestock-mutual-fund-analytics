# 📊 Bluestock Mutual Fund Analytics Platform

> **Capstone Project — Day-2 Deliverables**
> A production-grade data engineering pipeline for Indian mutual fund analytics, built with Python, pandas, and real-time MFAPI integration.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0+-green?logo=pandas)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Day%202%20Complete-brightgreen)

---

## 🎯 Project Overview

The **Bluestock Mutual Fund Analytics Platform** is a comprehensive data engineering and analytics solution that ingests, validates, and analyzes mutual fund data from the Indian market. It covers **10 fund houses**, **40+ schemes**, and provides real-time NAV tracking via the MFAPI.

### Key Capabilities

- **Data Ingestion** — Automated loading & profiling of 10 CSV datasets
- **Data Quality Validation** — Missing values, duplicates, invalid codes, risk category checks
- **AMFI Code Cross-Validation** — Ensures scheme consistency across datasets
- **Live NAV Integration** — Real-time NAV fetching from [MFAPI](https://api.mfapi.in)
- **Structured Reporting** — Auto-generated Markdown quality & validation reports
- **Production Logging** — Structured logging with file + console output

---

## 📁 Project Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                        # Raw CSV data & live NAV downloads
│   │   └── live_nav/               # Per-scheme live NAV CSVs
│   └── processed/                  # Cleaned & transformed datasets
├── notebooks/                      # Jupyter analysis notebooks
├── sql/                            # SQL scripts & schema definitions
├── dashboard/                      # Dashboard assets (Plotly/Streamlit)
├── reports/                        # Generated reports
│   ├── day1_data_quality_report.md # Comprehensive data quality report
│   └── amfi_validation_report.md   # AMFI code cross-validation report
├── scripts/
│   ├── data_ingestion.py           # Main ingestion pipeline
│   └── live_nav_fetch.py           # MFAPI live NAV fetcher
├── tests/
│   ├── __init__.py
│   └── test_data_ingestion.py      # Unit tests
├── logs/                           # Runtime logs (auto-created)
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata & tool config
└── .gitignore                      # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/bluestock-mutual-fund-analytics.git
cd bluestock-mutual-fund-analytics
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Place Data Files

Ensure the 10 CSV source files are in the **parent directory** of the project:

```
BLUE STOCKS/                        # Parent directory
├── 01_fund_master.csv
├── 02_nav_history.csv
├── 03_aum_by_fund_house.csv
├── 04_monthly_sip_inflows.csv
├── 05_category_inflows.csv
├── 06_industry_folio_count.csv
├── 07_scheme_performance.csv
├── 08_investor_transactions.csv
├── 09_portfolio_holdings - 09_portfolio_holdings.csv
├── 10_benchmark_indices - 10_benchmark_indices.csv
└── bluestock_mf_capstone/          # This project
```

### 5. Run Data Ingestion

```bash
python scripts/data_ingestion.py
```

This will:
- Load & profile all 10 datasets
- Run data quality validations
- Cross-validate AMFI codes
- Generate reports in `reports/`
- Copy raw data to `data/raw/`

### 6. Fetch Live NAV Data

```bash
python scripts/live_nav_fetch.py
```

This will:
- Fetch live NAV for HDFC Top 100 Direct (125497)
- Fetch NAV history for 5 additional schemes
- Save CSVs to `data/raw/` and `data/raw/live_nav/`

### 7. Run Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 📊 Data Sources

### Static Datasets (10 CSVs)

| # | Dataset | Description | Rows | Cols |
|---|---------|-------------|------|------|
| 01 | Fund Master | Scheme metadata & attributes | 41 | 15 |
| 02 | NAV History | Historical NAV (2022-2025) | ~46,000 | 3 |
| 03 | AUM by Fund House | AUM over time by AMC | 91 | 5 |
| 04 | Monthly SIP Inflows | SIP trends (2022-2025) | 49 | 6 |
| 05 | Category Inflows | Net inflows by category | 145 | 3 |
| 06 | Industry Folio Count | Folio growth by segment | 22 | 6 |
| 07 | Scheme Performance | Returns, risk metrics | 41 | 19 |
| 08 | Investor Transactions | Individual transactions | ~32,700 | 13 |
| 09 | Portfolio Holdings | Top holdings per scheme | 322 | 8 |
| 10 | Benchmark Indices | NIFTY/BSE daily indices | ~8,050 | 3 |

### Live API

| Source | Endpoint | Usage |
|--------|----------|-------|
| MFAPI | `https://api.mfapi.in/mf/{code}` | Real-time & historical NAV |

### Schemes Tracked

| AMFI Code | Scheme | Fund House |
|-----------|--------|------------|
| 125497 | HDFC Top 100 Direct | HDFC Mutual Fund |
| 119551 | SBI Bluechip | SBI Mutual Fund |
| 120503 | ICICI Bluechip | ICICI Prudential MF |
| 118632 | Nippon Large Cap | Nippon India MF |
| 119092 | Axis Bluechip | Axis Mutual Fund |
| 120841 | Kotak Bluechip | Kotak Mahindra MF |

---

## 📋 Day-1 Outputs

| Deliverable | Status | Location |
|-------------|--------|----------|
| Project structure | ✅ | Root directory |
| requirements.txt | ✅ | `requirements.txt` |
| pyproject.toml | ✅ | `pyproject.toml` |
| .gitignore | ✅ | `.gitignore` |
| data_ingestion.py | ✅ | `scripts/data_ingestion.py` |
| live_nav_fetch.py | ✅ | `scripts/live_nav_fetch.py` |
| Data quality report | ✅ | `reports/day1_data_quality_report.md` |
| AMFI validation report | ✅ | `reports/amfi_validation_report.md` |
| Unit tests | ✅ | `tests/test_data_ingestion.py` |
| README.md | ✅ | `README.md` |
| Git repository | ✅ | Initialized with initial commit |

---

## 📋 Day-2 Outputs

| Deliverable | Status | Location |
|-------------|--------|----------|
| data_cleaning.py | ✅ | `scripts/data_cleaning.py` |
| load_to_sqlite.py | ✅ | `scripts/load_to_sqlite.py` |
| SQLite database | ✅ | `bluestock_mf.db` |
| SQL schema | ✅ | `sql/schema.sql` |
| SQL queries | ✅ | `sql/queries.sql` |
| Data dictionary | ✅ | `data_dictionary.md` |
| 10 Cleaned CSVs | ✅ | `data/processed/` |

---

## 🔧 Configuration

### Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `MFAPI_TIMEOUT` | `30` | API request timeout (seconds) |
| `MFAPI_MAX_RETRIES` | `3` | Max retry attempts |
| `MFAPI_RATE_LIMIT` | `1.0` | Delay between API calls (seconds) |

### Logging

Logs are written to `logs/` directory:
- `data_ingestion.log` — Ingestion pipeline logs
- `live_nav_fetch.log` — NAV fetch logs

---

## 🛣️ Roadmap

### Day 2 — Data Cleaning & Transformation
- [x] Handle missing values & outliers
- [x] Normalize date formats
- [x] Create derived features (returns, volatility)
- [x] Build SQLite/PostgreSQL schema

### Day 3 — Exploratory Data Analysis
- [ ] NAV trend analysis
- [ ] AUM growth visualization
- [ ] SIP inflow patterns
- [ ] Category performance comparison

### Day 4 — Advanced Analytics
- [ ] Risk-adjusted return metrics
- [ ] Portfolio optimization
- [ ] Investor behavior segmentation
- [ ] Benchmark comparison

### Day 5 — Dashboard & Deployment
- [ ] Interactive Plotly/Streamlit dashboard
- [ ] Automated data refresh pipeline
- [ ] CI/CD with GitHub Actions
- [ ] Documentation & presentation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team

**Bluestock Fintech Analytics Team**

---

*Built with ❤️ for the Indian Mutual Fund ecosystem*
