# Note to Admin / Evaluator

## Project: Nifty 100 — Financial Analytics Capstone

**Submitted by:** KVS Charan  
**Repository:** [github.com/KVSCHARAN336/bluestock-mutual-fund-analytics](https://github.com/KVSCHARAN336/bluestock-mutual-fund-analytics)  
**Date:** July 2026

---

## Project Overview

This capstone project builds a **complete financial analytics pipeline** for the **Nifty 100 index constituents** (92 companies). It ingests raw financial data from Excel workbooks, validates and normalises it through a robust ETL pipeline, loads it into a relational SQLite database, and computes **50+ Key Performance Indicators (KPIs)** using a custom-built Financial Ratio Engine.

---

## Completed Sprints

### Sprint 1 — Data Foundation (Days 01–07)
- Environment setup with virtual environment and 20+ Python libraries
- Custom Excel Loader with year/ticker normalisation (handles `Mar 2024`, `TTM`, `FY23-24`, etc.)
- 16 Data Quality rules (PK uniqueness, FK integrity, range checks, balance sheet balancing)
- SQLite database with 10 relational tables, `PRAGMA foreign_keys = ON`
- All 12 source files loaded — **92 companies**, **1,164 P&L rows**, **1,140 BS rows**, **1,056 CF rows**
- 36 unit tests for normaliser — all passing

### Sprint 2 — Financial Ratio Engine (Days 08–14)
- **Profitability Ratios:** NPM, OPM, ROE, ROCE, ROA with edge case handling (negative equity returns None, zero sales returns None)
- **Leverage & Efficiency:** D/E, Interest Coverage, Net Debt, Asset Turnover with Financial sector carve-out (23 companies exempted from high-leverage flag)
- **CAGR Engine:** Revenue, PAT, EPS growth for 3yr, 5yr, 10yr windows with 6 edge-case handlers (TURNAROUND, DECLINE_TO_LOSS, BOTH_NEGATIVE, ZERO_BASE, INSUFFICIENT, normal)
- **Cash Flow KPIs:** FCF, CFO Quality Score, CapEx Intensity, FCF Conversion Rate, 8-pattern Capital Allocation classifier
- **Composite Quality Score:** Weighted scoring (0-100) across ROE, ROCE, NPM, D/E, ICR, CFO Quality
- **financial_ratios table:** 1,164 rows x 50+ KPI columns — zero null-only columns
- 26 KPI unit tests — all passing

---

## How to Run

### Prerequisites
- Python 3.10+
- Virtual environment (`.venv` at repository root)

### Setup
```bash
cd bluestock_mf_capstone/nifty100_capstone
pip install -r requirements.txt
```

### Sprint 1 — Load Data
```bash
python src/etl/loader.py
```
This will:
- Read all 12 raw Excel/CSV files from `data/raw/`
- Validate against 16 DQ rules
- Create and populate `data/db/nifty100.db` with 10 tables
- Generate `output/validation_failures.csv` and `output/load_audit.csv`

### Sprint 2 — Compute Financial Ratios
```bash
python src/analytics/compute_all.py
```
This will:
- Compute 50+ KPIs for all 92 companies across all years
- Populate the `financial_ratios` table in SQLite
- Generate `output/capital_allocation.csv` (1,056 rows, 8 patterns)
- Generate `output/ratio_edge_cases.log` (288 documented anomalies)

### Run All Tests
```bash
pytest -o pythonpath=src tests/ -v
```
Expected result: **62 passed, 0 failures**

---

## Key Deliverables

| Deliverable | Location | Details |
|---|---|---|
| SQLite Database | `data/db/nifty100.db` | 10 tables, 1,164 financial_ratios rows |
| ETL Pipeline | `src/etl/loader.py` | Full data ingestion and validation |
| Ratio Engine | `src/analytics/` | 4 modules (ratios, cagr, cashflow_kpis, compute_all) |
| Unit Tests | `tests/` | 62 tests (36 normaliser + 26 KPI) |
| Validation Report | `output/validation_failures.csv` | 903 DQ issues documented |
| Load Audit | `output/load_audit.csv` | Row counts per table |
| Capital Allocation | `output/capital_allocation.csv` | 8-pattern classifier for 1,056 company-years |
| Edge Case Log | `output/ratio_edge_cases.log` | 288 anomalies with categories |

---

## Project Structure

```
nifty100_capstone/
├── data/
│   ├── raw/                    # 14 source files (Excel + CSV)
│   └── db/nifty100.db          # SQLite database
├── db/schema.sql               # 10-table relational schema
├── src/
│   ├── etl/                    # loader, normaliser, validator
│   └── analytics/              # ratios, cagr, cashflow_kpis, compute_all
├── tests/
│   ├── etl/test_normaliser.py  # 36 normaliser tests
│   └── kpi/test_ratios.py      # 26 KPI formula tests
├── output/                     # Generated reports and CSVs
├── scripts/extract_raw_sheets.py
├── requirements.txt
└── Makefile
```

---

## Data Source

- **DATASET.xlsx** — Core financial data (P&L, Balance Sheet, Cash Flow, Ratios)
- **SUPPORTING_DATASETS.xlsx** — Supplementary data (Sectors, Peer Groups, Analysis, Market Cap, Stock Prices)
- All data is for **Nifty 100 constituents** in **Indian Rupees (Crore)**

---

## Technical Highlights

1. **Referential Integrity:** All child table rows validated against `companies.id` before insertion — 0 FK violations
2. **Year Normalisation:** Handles 12+ formats (e.g., `Mar 2024` to `2024-03`, `FY23-24` to `2024-03`, `TTM` preserved)
3. **Financial Sector Carve-Out:** 23 banks/NBFCs/insurers exempted from D/E warning flags (structurally high leverage)
4. **CAGR Edge Cases:** 6 handlers prevent misleading growth rates from negative-to-positive turnarounds
5. **Composite Quality Score:** Multi-factor weighted score enabling company comparison across sectors

---

## Verification Summary

| Check | Expected | Actual | Status |
|---|---|---|---|
| `financial_ratios` rows | >= 1,100 | 1,164 | PASS |
| Null-only KPI columns | 0 | 0 | PASS |
| Unit tests passing | 20+ | 62 | PASS |
| ROE spot-check (TCS) | < 0.1% diff | 0.0% diff | PASS |
| CAGR spot-check (TCS) | < 0.1% diff | 0.0% diff | PASS |
| FK integrity violations | 0 | 0 | PASS |

---

*All code is original, tested, and production-ready. The pipeline can be re-run end-to-end with a single command sequence.*
