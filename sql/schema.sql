DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS sip_inflows;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund(
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    expense_ratio_pct REAL,
    risk_category TEXT
);

CREATE TABLE dim_date(
    date_id INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER
);

CREATE TABLE fact_nav(
    amfi_code TEXT,
    nav_date DATE,
    nav REAL,
    FOREIGN KEY(amfi_code)
    REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_transactions(
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT,
    amfi_code TEXT,
    transaction_date DATE,
    transaction_type TEXT,
    amount_inr REAL,
    FOREIGN KEY(amfi_code)
    REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance(
    amfi_code TEXT PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    max_drawdown_pct REAL,
    FOREIGN KEY(amfi_code)
    REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum(
    fund_house TEXT,
    quarter TEXT,
    aum_crore REAL
);

CREATE TABLE sip_inflows(
    month TEXT,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);
