-- 1 Top 5 fund houses by AUM
SELECT fund_house,
SUM(aum_crore) total_aum
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum DESC
LIMIT 5;

-- 2 Average NAV by month
SELECT
strftime('%Y-%m', nav_date),
AVG(nav)
FROM fact_nav
GROUP BY 1;

-- 3 SIP YoY Growth
SELECT month,
yoy_growth_pct
FROM sip_inflows;

-- 4 Transactions by State
SELECT state,
COUNT(*) tx_count
FROM fact_transactions
GROUP BY state
ORDER BY tx_count DESC;

-- 5 Funds with Expense Ratio < 1%
SELECT scheme_name,
expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1;

-- 6 Top 10 Funds by Sharpe Ratio
SELECT amfi_code,
sharpe_ratio
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 10;

-- 7 Highest Alpha Funds
SELECT amfi_code,
alpha
FROM fact_performance
ORDER BY alpha DESC
LIMIT 10;

-- 8 Average Investment by Age Group
SELECT age_group,
AVG(amount_inr)
FROM fact_transactions
GROUP BY age_group;

-- 9 Redemption Volume
SELECT
SUM(amount_inr)
FROM fact_transactions
WHERE transaction_type='Redemption';

-- 10 Category-wise Scheme Count
SELECT category,
COUNT(*)
FROM dim_fund
GROUP BY category;
