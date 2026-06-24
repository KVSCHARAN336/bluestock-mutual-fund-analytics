# Day-1 Data Quality Report

**Generated:** 2026-06-23 20:27:00
**Platform:** Bluestock Mutual Fund Analytics
**Datasets Analyzed:** 10

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Datasets | 10 |
| Total Rows | 87,533 |
| Total Columns | 81 |
| Total Missing Values | 12 |
| Total Duplicate Rows | 0 |
| Total Quality Issues | 1 |

---

## Dataset Profiles

### fund_master

| Metric | Value |
|--------|-------|
| Rows | 40 |
| Columns | 15 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.03 MB |

**Data Types:**

| Column | Type |
|--------|------|
| amfi_code | int64 |
| fund_house | object |
| scheme_name | object |
| category | object |
| sub_category | object |
| plan | object |
| launch_date | object |
| benchmark | object |
| expense_ratio_pct | float64 |
| exit_load_pct | float64 |
| min_sip_amount | int64 |
| min_lumpsum_amount | int64 |
| fund_manager | object |
| risk_category | object |
| sebi_category_code | object |

**First 5 Rows:**

```
   amfi_code       fund_house                                   scheme_name category sub_category     plan launch_date                  benchmark  expense_ratio_pct  exit_load_pct  min_sip_amount  min_lumpsum_amount   fund_manager risk_category sebi_category_code
0     119551  SBI Mutual Fund     SBI Bluechip Fund - Regular Plan - Growth   Equity    Large Cap  Regular  2006-02-14              NIFTY 100 TRI               1.54            1.0             500                1000  Sohini Andani      Moderate               EC01
1     119552  SBI Mutual Fund      SBI Bluechip Fund - Direct Plan - Growth   Equity    Large Cap   Direct  2013-01-01              NIFTY 100 TRI               0.66            1.0             500                1000  Sohini Andani      Moderate               EC01
2     119598  SBI Mutual Fund    SBI Small Cap Fund - Regular Plan - Growth   Equity    Small Cap  Regular  2009-09-09       BSE 250 SmallCap TRI               1.43            1.0             500                1000  R. Srinivasan     Very High               EC03
3     119599  SBI Mutual Fund     SBI Small Cap Fund - Direct Plan - Growth   Equity    Small Cap   Direct  2013-01-01       BSE 250 SmallCap TRI               0.72            1.0             500                1000  R. Srinivasan     Very High               EC03
4     119120  SBI Mutual Fund  SBI Magnum Gilt Fund - Regular Plan - Growth     Debt         Gilt  Regular  2000-12-30  CRISIL Dynamic Gilt Index               0.77            0.0             500                1000   Dinesh Ahuja           Low               DC02
```

---

### nav_history

| Metric | Value |
|--------|-------|
| Rows | 46,000 |
| Columns | 3 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 3.29 MB |

**Data Types:**

| Column | Type |
|--------|------|
| amfi_code | int64 |
| date | object |
| nav | float64 |

**First 5 Rows:**

```
   amfi_code        date      nav
0     119551  2022-01-03  54.3856
1     119551  2022-01-04  54.3474
2     119551  2022-01-05  54.6869
3     119551  2022-01-06  55.4550
4     119551  2022-01-07  55.3692
```

---

### aum_by_fund_house

| Metric | Value |
|--------|-------|
| Rows | 90 |
| Columns | 5 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.01 MB |

**Data Types:**

| Column | Type |
|--------|------|
| date | object |
| fund_house | object |
| aum_lakh_crore | float64 |
| aum_crore | int64 |
| num_schemes | int64 |

**First 5 Rows:**

```
         date           fund_house  aum_lakh_crore  aum_crore  num_schemes
0  2022-03-31      SBI Mutual Fund            6.05     605000          186
1  2022-03-31  ICICI Prudential MF            4.65     465000          216
2  2022-03-31     HDFC Mutual Fund            4.35     435000          195
3  2022-03-31      Nippon India MF            2.70     270000          177
4  2022-03-31    Kotak Mahindra MF            2.70     270000          168
```

---

### monthly_sip_inflows

| Metric | Value |
|--------|-------|
| Rows | 48 |
| Columns | 6 |
| Missing Values | 12 (4.17%) |
| Duplicate Rows | 0 |
| Memory | 0.0 MB |

**Data Types:**

| Column | Type |
|--------|------|
| month | object |
| sip_inflow_crore | int64 |
| active_sip_accounts_crore | float64 |
| new_sip_accounts_lakh | float64 |
| sip_aum_lakh_crore | float64 |
| yoy_growth_pct | float64 |

**Missing Values by Column:**

| Column | Count | % |
|--------|-------|---|
| yoy_growth_pct | 12 | 25.0% |

**First 5 Rows:**

```
     month  sip_inflow_crore  active_sip_accounts_crore  new_sip_accounts_lakh  sip_aum_lakh_crore  yoy_growth_pct
0  2022-01             11517                       4.91                   9.10                4.80             NaN
1  2022-02             11438                       4.93                   8.20                4.85             NaN
2  2022-03             12328                       5.09                  10.50                5.01             NaN
3  2022-04             11863                       5.48                   9.52                5.12             NaN
4  2022-05             12286                       5.55                   8.10                5.15             NaN
```

---

### category_inflows

| Metric | Value |
|--------|-------|
| Rows | 144 |
| Columns | 3 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.02 MB |

**Data Types:**

| Column | Type |
|--------|------|
| month | object |
| category | object |
| net_inflow_crore | float64 |

**First 5 Rows:**

```
     month         category  net_inflow_crore
0  2024-04        Large Cap            2413.0
1  2024-04          Mid Cap            3897.0
2  2024-04        Small Cap            3533.0
3  2024-04        Flexi Cap            4947.0
4  2024-04  Large & Mid Cap            4214.0
```

---

### industry_folio_count

| Metric | Value |
|--------|-------|
| Rows | 21 |
| Columns | 6 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.0 MB |

**Data Types:**

| Column | Type |
|--------|------|
| month | object |
| total_folios_crore | float64 |
| equity_folios_crore | float64 |
| debt_folios_crore | float64 |
| hybrid_folios_crore | float64 |
| others_folios_crore | float64 |

**First 5 Rows:**

```
     month  total_folios_crore  equity_folios_crore  debt_folios_crore  hybrid_folios_crore  others_folios_crore
0  2022-01               13.26                 9.28               1.86                 0.80                 1.33
1  2022-04               13.91                 9.74               1.95                 0.83                 1.39
2  2022-07               13.85                 9.69               1.94                 0.83                 1.38
3  2022-10               14.12                 9.88               1.98                 0.85                 1.41
4  2023-01               14.81                10.37               2.07                 0.89                 1.48
```

---

### scheme_performance

| Metric | Value |
|--------|-------|
| Rows | 40 |
| Columns | 19 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.02 MB |

**Data Types:**

| Column | Type |
|--------|------|
| amfi_code | int64 |
| scheme_name | object |
| fund_house | object |
| category | object |
| plan | object |
| return_1yr_pct | float64 |
| return_3yr_pct | float64 |
| return_5yr_pct | float64 |
| benchmark_3yr_pct | float64 |
| alpha | float64 |
| beta | float64 |
| sharpe_ratio | float64 |
| sortino_ratio | float64 |
| std_dev_ann_pct | float64 |
| max_drawdown_pct | float64 |
| aum_crore | int64 |
| expense_ratio_pct | float64 |
| morningstar_rating | int64 |
| risk_grade | object |

**First 5 Rows:**

```
   amfi_code                                   scheme_name       fund_house   category     plan  return_1yr_pct  return_3yr_pct  return_5yr_pct  benchmark_3yr_pct  alpha  beta  sharpe_ratio  sortino_ratio  std_dev_ann_pct  max_drawdown_pct  aum_crore  expense_ratio_pct  morningstar_rating risk_grade
0     119551     SBI Bluechip Fund - Regular Plan - Growth  SBI Mutual Fund  Large Cap  Regular           12.42           12.36           14.45              11.49   0.87  0.89          0.88           1.29             14.0            -21.70      14288               1.54                   4   Moderate
1     119552      SBI Bluechip Fund - Direct Plan - Growth  SBI Mutual Fund  Large Cap   Direct           15.25           11.30           14.23               9.52   1.78  0.87          0.81           1.29             14.0            -24.43       1231               0.66                   3   Moderate
2     119598    SBI Small Cap Fund - Regular Plan - Growth  SBI Mutual Fund  Small Cap  Regular           24.56           23.39           20.67              22.16   1.23  0.89          0.94           1.35             25.0            -13.35      19259               1.43                   5  Very High
3     119599     SBI Small Cap Fund - Direct Plan - Growth  SBI Mutual Fund  Small Cap   Direct           20.59           23.14           21.82              22.01   1.13  1.04          0.93           1.67             25.0            -24.78      36061               0.72                   4  Very High
4     119120  SBI Magnum Gilt Fund - Regular Plan - Growth  SBI Mutual Fund       Gilt  Regular            5.34            6.07            5.43               4.47   1.60  0.22          1.52           2.11              4.0             -2.30      24101               0.77                   5        Low
```

---

### investor_transactions

| Metric | Value |
|--------|-------|
| Rows | 32,778 |
| Columns | 13 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 18.19 MB |

**Data Types:**

| Column | Type |
|--------|------|
| investor_id | object |
| transaction_date | object |
| amfi_code | int64 |
| transaction_type | object |
| amount_inr | int64 |
| state | object |
| city | object |
| city_tier | object |
| age_group | object |
| gender | object |
| annual_income_lakh | float64 |
| payment_mode | object |
| kyc_status | object |

**First 5 Rows:**

```
  investor_id transaction_date  amfi_code transaction_type  amount_inr        state       city city_tier age_group  gender  annual_income_lakh payment_mode kyc_status
0   INV003054       2024-01-01     119092              SIP        1834    Telangana  Hyderabad       T30       56+  Female                77.1          UPI   Verified
1   INV002952       2024-01-01     148567       Redemption      392882       Punjab   Amritsar       B30     18-25    Male                 7.1       Cheque   Verified
2   INV003420       2024-01-01     118636              SIP         912      Haryana  Faridabad       B30     36-45    Male                47.2      Mandate   Verified
3   INV003436       2024-01-01     118634              SIP        1102  Maharashtra     Mumbai       T30     36-45  Female                54.4       Cheque    Pending
4   INV004691       2024-01-01     119094          Lumpsum        8682        Delhi      Noida       T30     26-35    Male                14.5  Net Banking    Pending
```

---

### portfolio_holdings

| Metric | Value |
|--------|-------|
| Rows | 322 |
| Columns | 8 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.08 MB |

**Data Types:**

| Column | Type |
|--------|------|
| amfi_code | int64 |
| stock_symbol | object |
| stock_name | object |
| sector | object |
| weight_pct | float64 |
| market_value_cr | float64 |
| current_price_inr | float64 |
| portfolio_date | object |

**First 5 Rows:**

```
   amfi_code stock_symbol                stock_name       sector  weight_pct  market_value_cr  current_price_inr portfolio_date
0     119551    POWERGRID    Power Grid Corporation    Utilities       13.85           737.09            6011.08     2025-12-31
1     119551     HDFCBANK             HDFC Bank Ltd      Banking       11.19            88.97            1074.65     2025-12-31
2     119551       GRASIM     Grasim Industries Ltd  Diversified        9.90           208.45            5964.59     2025-12-31
3     119551      DRREDDY  Dr. Reddy's Laboratories       Pharma        4.76           161.32            3748.82     2025-12-31
4     119551   ASIANPAINT          Asian Paints Ltd       Paints       10.25           725.90            1321.45     2025-12-31
```

---

### benchmark_indices

| Metric | Value |
|--------|-------|
| Rows | 8,050 |
| Columns | 3 |
| Missing Values | 0 (0.0%) |
| Duplicate Rows | 0 |
| Memory | 0.97 MB |

**Data Types:**

| Column | Type |
|--------|------|
| date | object |
| index_name | object |
| close_value | float64 |

**First 5 Rows:**

```
         date index_name  close_value
0  2022-01-03    NIFTY50     17492.79
1  2022-01-04    NIFTY50     17689.64
2  2022-01-05    NIFTY50     17835.05
3  2022-01-06    NIFTY50     17878.51
4  2022-01-07    NIFTY50     17759.15
```

---

## Data Quality Issues

### fund_master — 0 issue(s)

✅ No quality issues detected.

---

### nav_history — 0 issue(s)

✅ No quality issues detected.

---

### aum_by_fund_house — 0 issue(s)

✅ No quality issues detected.

---

### monthly_sip_inflows — 1 issue(s)

| Check | Column | Count | % | Severity |
|-------|--------|-------|---|----------|
| missing_values | yoy_growth_pct | 12 | 25.0% | HIGH |

---

### category_inflows — 0 issue(s)

✅ No quality issues detected.

---

### industry_folio_count — 0 issue(s)

✅ No quality issues detected.

---

### scheme_performance — 0 issue(s)

✅ No quality issues detected.

---

### investor_transactions — 0 issue(s)

✅ No quality issues detected.

---

### portfolio_holdings — 0 issue(s)

✅ No quality issues detected.

---

### benchmark_indices — 0 issue(s)

✅ No quality issues detected.

---

## Recommendations

1. **Missing Values:** Handle missing `yoy_growth_pct` in SIP inflows (expected for first year).
2. **Data Types:** Convert date columns to datetime for time-series analysis.
3. **Duplicates:** Investigate any duplicate rows in transaction data.
4. **NAV Validation:** Ensure all NAV values are positive and within reasonable range.
5. **AMFI Consistency:** Cross-validate AMFI codes across all datasets.

---

*Report generated by Bluestock MF Analytics Pipeline — 2026-06-23 20:27:00*