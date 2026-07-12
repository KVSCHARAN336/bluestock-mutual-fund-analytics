-- Nifty100 SQLite Relational Database Schema
-- Enabled via PRAGMA foreign_keys = ON; in application code

DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS peer_groups;
DROP TABLE IF EXISTS prosandcons;
DROP TABLE IF EXISTS analysis;
DROP TABLE IF EXISTS financial_ratios;
DROP TABLE IF EXISTS cashflow;
DROP TABLE IF EXISTS balancesheet;
DROP TABLE IF EXISTS profitandloss;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS sectors;

-- 1. Sectors Dimension Table
CREATE TABLE sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name TEXT NOT NULL UNIQUE
);

-- 2. Companies Registry Table
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ticker TEXT NOT NULL UNIQUE,
    sector_id INTEGER,
    website TEXT,
    FOREIGN KEY(sector_id) REFERENCES sectors(sector_id) ON DELETE SET NULL
);

-- 3. Documents Table
CREATE TABLE documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    document_type TEXT,
    url TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 4. Profit & Loss Fact Table
CREATE TABLE profitandloss (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_pct REAL,
    net_profit REAL,
    eps REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 5. Balance Sheet Fact Table
CREATE TABLE balancesheet (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    share_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_assets REAL,
    total_assets REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 6. Cash Flow Fact Table
CREATE TABLE cashflow (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    operating_cash REAL,
    investing_cash REAL,
    financing_cash REAL,
    net_cash_flow REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 7. Financial Ratios Table
CREATE TABLE financial_ratios (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    pe_ratio REAL,
    pb_ratio REAL,
    debt_equity REAL,
    interest_coverage REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 8. Advanced Analysis Metrics Table
CREATE TABLE analysis (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    opm_pct REAL,
    npat_margin_pct REAL,
    roe_pct REAL,
    PRIMARY KEY(company_id, year),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 9. Qualitative Pros & Cons Table
CREATE TABLE prosandcons (
    pro_con_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('PRO', 'CON')),
    point_text TEXT NOT NULL,
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 10. Peer Group Cross-Reference Table
CREATE TABLE peer_groups (
    company_id INTEGER NOT NULL,
    peer_company_id INTEGER NOT NULL,
    PRIMARY KEY(company_id, peer_company_id),
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY(peer_company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 11. Stock Price Time-Series Table
CREATE TABLE stock_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    price_date DATE NOT NULL,
    close_price REAL,
    volume INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- Indexes for performance queries
CREATE INDEX idx_nav_prices ON stock_prices(company_id, price_date);
CREATE INDEX idx_pl_comp_year ON profitandloss(company_id, year);
CREATE INDEX idx_bs_comp_year ON balancesheet(company_id, year);
