-- Nifty100 Exploratory Analysis Queries
-- Day 07 Sprint Wrap-Up & Review

-- 1. Table Row Counts Verification
SELECT 'sectors' AS table_name, COUNT(*) AS row_count FROM sectors
UNION ALL
SELECT 'companies', COUNT(*) FROM companies
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL
SELECT 'financial_ratios', COUNT(*) FROM financial_ratios
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL
SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL
SELECT 'peer_groups', COUNT(*) FROM peer_groups
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices;

-- 2. Companies Distribution by Sector
SELECT s.sector_name, COUNT(c.company_id) AS company_count
FROM sectors s
LEFT JOIN companies c ON s.sector_id = c.sector_id
GROUP BY s.sector_id
ORDER BY company_count DESC;

-- 3. Industry Peer Group Mapping View
SELECT c.name AS company_name, c.ticker, p.name AS peer_name, p.ticker AS peer_ticker
FROM peer_groups pg
JOIN companies c ON pg.company_id = c.company_id
JOIN companies p ON pg.peer_company_id = p.company_id
LIMIT 10;

-- 4. Years of Financial Data Coverage Per Company
SELECT c.name, c.ticker, COUNT(pl.year) AS years_count
FROM companies c
LEFT JOIN profitandloss pl ON c.company_id = pl.company_id
GROUP BY c.company_id
ORDER BY years_count ASC
LIMIT 10;

-- 5. Detect Companies with Less than 5 Years of Data
SELECT c.name, c.ticker, COUNT(pl.year) AS years_count
FROM companies c
JOIN profitandloss pl ON c.company_id = pl.company_id
GROUP BY c.company_id
HAVING years_count < 5
ORDER BY years_count ASC;

-- 6. Unified Financial View (P&L + Balance Sheet + Cash Flow) for Reliance (ID = 1)
SELECT 
    pl.year,
    pl.sales,
    pl.operating_profit,
    pl.net_profit,
    bs.total_assets,
    bs.total_liabilities,
    cf.net_cash_flow
FROM profitandloss pl
JOIN balancesheet bs ON pl.company_id = bs.company_id AND pl.year = bs.year
JOIN cashflow cf ON pl.company_id = cf.company_id AND pl.year = cf.year
WHERE pl.company_id = 1
ORDER BY pl.year DESC;

-- 7. Balance Sheet Discrepancy Integrity Check
SELECT 
    c.name,
    bs.year,
    bs.total_assets,
    (bs.share_capital + bs.reserves + bs.borrowings + bs.other_liabilities) AS calculated_liab,
    abs(bs.total_assets - (bs.share_capital + bs.reserves + bs.borrowings + bs.other_liabilities)) AS discrepancy
FROM balancesheet bs
JOIN companies c ON bs.company_id = c.company_id
WHERE discrepancy > 1.0
LIMIT 10;

-- 8. Top 5 Companies by Operating Profit Margin (OPM %)
SELECT c.name, c.ticker, pl.year, pl.sales, pl.operating_profit,
       round((pl.operating_profit / pl.sales) * 100, 2) AS calculated_opm_pct
FROM profitandloss pl
JOIN companies c ON pl.company_id = c.company_id
WHERE pl.sales > 0
ORDER BY calculated_opm_pct DESC
LIMIT 5;

-- 9. Sector-level average Stock Prices & Trading Volumes
SELECT s.sector_name, round(AVG(sp.close_price), 2) AS avg_close, round(AVG(sp.volume), 0) AS avg_volume
FROM sectors s
JOIN companies c ON s.sector_id = c.sector_id
JOIN stock_prices sp ON c.company_id = sp.company_id
GROUP BY s.sector_id
ORDER BY avg_close DESC;

-- 10. Qualitative Analysis (Pros and Cons) for Top Companies
SELECT c.name, pc.type, pc.point_text
FROM prosandcons pc
JOIN companies c ON pc.company_id = c.company_id
WHERE c.company_id <= 3
ORDER BY c.company_id, pc.type;
