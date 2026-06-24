# Data Dictionary

## dim_fund

| Column | Type | Description |
|----------|------|-------------|
| amfi_code | TEXT | Unique AMFI Scheme Code |
| fund_house | TEXT | AMC Name |
| scheme_name | TEXT | Fund Name |
| category | TEXT | Equity/Debt/Hybrid |
| sub_category | TEXT | Large Cap, Mid Cap etc |
| expense_ratio_pct | REAL | Expense ratio of the fund |
| risk_category | TEXT | Risk classification |

## dim_date

| Column | Type | Description |
|----------|------|-------------|
| date_id | INTEGER | Primary Key |
| full_date | DATE | The actual date |
| year | INTEGER | Year |
| quarter | INTEGER | Quarter (1-4) |
| month | INTEGER | Month (1-12) |

## fact_nav

| Column | Type | Description |
|----------|------|-------------|
| amfi_code | TEXT | Scheme Code |
| nav_date | DATE | NAV Date |
| nav | REAL | Net Asset Value |

## fact_transactions

| Column | Type | Description |
|----------|------|-------------|
| tx_id | INTEGER | Transaction ID |
| investor_id | TEXT | Investor Identifier |
| amfi_code | TEXT | Scheme Code |
| transaction_date | DATE | Date of transaction |
| transaction_type | TEXT | Type (e.g. SIP, Lumpsum, Redemption) |
| amount_inr | REAL | Transaction Amount in INR |

## fact_performance

| Column | Type | Description |
|----------|------|-------------|
| amfi_code | TEXT | Scheme Code |
| return_1yr_pct | REAL | 1 Year Return % |
| return_3yr_pct | REAL | 3 Year Return % |
| return_5yr_pct | REAL | 5 Year Return % |
| alpha | REAL | Alpha |
| beta | REAL | Beta |
| sharpe_ratio | REAL | Sharpe Ratio |
| sortino_ratio | REAL | Sortino Ratio |
| max_drawdown_pct | REAL | Max Drawdown % |

## fact_aum

| Column | Type | Description |
|----------|------|-------------|
| fund_house | TEXT | AMC Name |
| quarter | TEXT | Quarter of the AUM record |
| aum_crore | REAL | AUM in Crores |

## sip_inflows

| Column | Type | Description |
|----------|------|-------------|
| month | TEXT | Month |
| sip_inflow_crore | REAL | Total SIP inflows in Crores |
| active_sip_accounts_crore | REAL | Number of active SIP accounts |
| new_sip_accounts_lakh | REAL | Number of new SIP accounts |
| sip_aum_lakh_crore | REAL | Total SIP AUM |
| yoy_growth_pct | REAL | Year-over-year growth % |
