-- Nifty100 SQLite Relational Database Schema (Aligned with Real Dataset Sheets)
-- Enabled via PRAGMA foreign_keys = ON; in application code

DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS peer_groups;
DROP TABLE IF EXISTS market_cap;
DROP TABLE IF EXISTS financial_ratios;
DROP TABLE IF EXISTS prosandcons;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS analysis;
DROP TABLE IF EXISTS cashflow;
DROP TABLE IF EXISTS balancesheet;
DROP TABLE IF EXISTS profitandloss;
DROP TABLE IF EXISTS sectors;
DROP TABLE IF EXISTS companies;

-- 1. Companies Table (Master Reference)
CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value INTEGER,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

-- 2. Sectors Table (Company Sector Mapping)
CREATE TABLE sectors (
    company_id TEXT PRIMARY KEY,
    broad_sector TEXT,
    sub_sector TEXT,
    index_weight_pct REAL,
    market_cap_category TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 3. Profit & Loss Table
CREATE TABLE profitandloss (
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 4. Balance Sheet Table
CREATE TABLE balancesheet (
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 5. Cash Flow Table
CREATE TABLE cashflow (
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Analysis Table (Pre-computed Growth Metrics)
CREATE TABLE analysis (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 7. Documents Table (Annual Report URLs)
CREATE TABLE documents (
    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    annual_report TEXT,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 8. Qualitative Pros & Cons Table
CREATE TABLE prosandcons (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 9. Financial Ratios Table (Sprint 2: 50+ KPI columns)
CREATE TABLE financial_ratios (
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    -- Profitability Ratios (Day 08)
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    roce_pct REAL,
    roa_pct REAL,
    -- Leverage & Efficiency (Day 09)
    debt_to_equity REAL,
    high_leverage_flag INTEGER DEFAULT 0,
    interest_coverage REAL,
    icr_label TEXT,
    net_debt_cr REAL,
    asset_turnover REAL,
    -- Cash Flow KPIs (Day 11)
    free_cash_flow_cr REAL,
    capex_cr REAL,
    cash_from_operations_cr REAL,
    cfo_quality_score REAL,
    cfo_quality_label TEXT,
    capex_intensity_pct REAL,
    capex_intensity_label TEXT,
    fcf_conversion_pct REAL,
    capital_allocation_pattern TEXT,
    -- Per-share & Payout Metrics
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    -- CAGR Metrics (Day 10)
    revenue_cagr_3yr REAL,
    revenue_cagr_3yr_flag TEXT,
    revenue_cagr_5yr REAL,
    revenue_cagr_5yr_flag TEXT,
    revenue_cagr_10yr REAL,
    revenue_cagr_10yr_flag TEXT,
    pat_cagr_3yr REAL,
    pat_cagr_3yr_flag TEXT,
    pat_cagr_5yr REAL,
    pat_cagr_5yr_flag TEXT,
    pat_cagr_10yr REAL,
    pat_cagr_10yr_flag TEXT,
    eps_cagr_3yr REAL,
    eps_cagr_3yr_flag TEXT,
    eps_cagr_5yr REAL,
    eps_cagr_5yr_flag TEXT,
    eps_cagr_10yr REAL,
    eps_cagr_10yr_flag TEXT,
    -- Composite Score (Day 12)
    composite_quality_score REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 10. Market Capitalization & Valuation Multiples Table
CREATE TABLE market_cap (
    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    market_cap_crore REAL,
    enterprise_value_crore REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,
    dividend_yield_pct REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 11. Peer Groups Table
CREATE TABLE peer_groups (
    peer_group_name TEXT NOT NULL,
    company_id TEXT NOT NULL,
    is_benchmark INTEGER,
    PRIMARY KEY(peer_group_name, company_id),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 12. Stock Prices Table (Monthly OHLCV)
CREATE TABLE stock_prices (
    company_id TEXT NOT NULL,
    price_date DATE NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    adjusted_close REAL,
    PRIMARY KEY(company_id, price_date),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_stock_prices ON stock_prices(company_id, price_date);
CREATE INDEX idx_pl_year ON profitandloss(company_id, year);
CREATE INDEX idx_bs_year ON balancesheet(company_id, year);
CREATE INDEX idx_cf_year ON cashflow(company_id, year);
