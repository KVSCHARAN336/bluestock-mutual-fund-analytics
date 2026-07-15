"""
Sprint 2 — Day 14: 20 KPI Formula Unit Tests
==============================================
Tests for ratios.py, cagr.py, and cashflow_kpis.py.
"""

import pytest
from src.analytics.ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage_ratio,
    net_debt, asset_turnover
)
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_score, capex_intensity,
    fcf_conversion, classify_capital_allocation
)


# ─────────────────────────────────────────────
# 8 Tests: Profitability Ratios (Day 08)
# ─────────────────────────────────────────────

def test_npm_normal():
    """Normal NPM calculation."""
    assert net_profit_margin(150, 1000) == 15.0

def test_npm_zero_sales():
    """NPM returns None when sales is 0."""
    assert net_profit_margin(150, 0) is None

def test_opm_normal():
    """Normal OPM calculation."""
    assert operating_profit_margin(200, 1000) == 20.0

def test_opm_cross_check_mismatch():
    """OPM cross-check detects >1% mismatch."""
    warn = opm_cross_check(20.0, 17.5, threshold=1.0)
    assert warn is not None
    assert "mismatch" in warn.lower()

def test_roe_normal():
    """Normal ROE: net_profit / (equity + reserves) × 100."""
    assert return_on_equity(100, 200, 300) == 20.0  # 100/500 * 100

def test_roe_negative_equity():
    """ROE returns None when equity+reserves <= 0."""
    assert return_on_equity(100, 50, -100) is None

def test_roce_normal():
    """Normal ROCE: EBIT / capital_employed × 100."""
    # EBIT = 200+50=250, CE = 100+400+500=1000 → 25%
    assert return_on_capital_employed(200, 50, 100, 400, 500) == 25.0

def test_roa_zero_assets():
    """ROA returns None when total_assets is 0."""
    assert return_on_assets(100, 0) is None


# ─────────────────────────────────────────────
# 8 Tests: Leverage & Efficiency (Day 09)
# ─────────────────────────────────────────────

def test_de_debt_free():
    """D/E returns 0 (not None) when borrowings = 0."""
    assert debt_to_equity(0, 100, 400) == 0.0

def test_de_normal():
    """Normal D/E calculation."""
    assert debt_to_equity(250, 100, 400) == 0.5  # 250/500

def test_de_negative_equity():
    """D/E returns None when equity+reserves <= 0."""
    assert debt_to_equity(100, 50, -100) is None

def test_hlf_financial_sector():
    """High leverage flag suppressed for financial sector companies."""
    assert high_leverage_flag(8.0, True) == 0

def test_hlf_non_financial():
    """High leverage flag set when D/E > 5 and NOT financial sector."""
    assert high_leverage_flag(6.0, False) == 1

def test_icr_zero_interest():
    """ICR returns (None, 'Debt Free') when interest = 0."""
    val, label = interest_coverage_ratio(500, 50, 0)
    assert val is None
    assert label == "Debt Free"

def test_icr_normal():
    """Normal ICR calculation."""
    val, label = interest_coverage_ratio(400, 100, 100)
    assert val == 5.0  # (400+100)/100
    assert label == ""

def test_asset_turnover_normal():
    """Normal asset turnover calculation."""
    assert asset_turnover(5000, 10000) == 0.5


# ─────────────────────────────────────────────
# 10 Tests: CAGR (Day 10)
# ─────────────────────────────────────────────

def test_cagr_normal():
    """Normal CAGR: 100→200 over 5 years."""
    val, flag = compute_cagr(100, 200, 5)
    assert flag == ""
    assert abs(val - 14.87) < 0.1  # ~14.87%

def test_cagr_turnaround():
    """CAGR: negative→positive returns TURNAROUND flag."""
    val, flag = compute_cagr(-100, 200, 5)
    assert val is None
    assert flag == "TURNAROUND"

def test_cagr_decline_to_loss():
    """CAGR: positive→negative returns DECLINE_TO_LOSS flag."""
    val, flag = compute_cagr(200, -50, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_both_negative():
    """CAGR: both negative returns BOTH_NEGATIVE flag."""
    val, flag = compute_cagr(-100, -200, 5)
    assert val is None
    assert flag == "BOTH_NEGATIVE"

def test_cagr_zero_base():
    """CAGR: zero start value returns ZERO_BASE flag."""
    val, flag = compute_cagr(0, 200, 5)
    assert val is None
    assert flag == "ZERO_BASE"

def test_cagr_insufficient():
    """CAGR: n_years <= 0 returns INSUFFICIENT flag."""
    val, flag = compute_cagr(100, 200, 0)
    assert val is None
    assert flag == "INSUFFICIENT"

def test_fcf_normal():
    """FCF = operating + investing activity."""
    assert free_cash_flow(500, -200) == 300.0

def test_capex_intensity_asset_light():
    """CapEx intensity <3% = Asset Light."""
    pct, label = capex_intensity(-20, 1000)
    assert pct == 2.0
    assert label == "Asset Light"

def test_fcf_conversion_normal():
    """FCF conversion rate calculation."""
    assert fcf_conversion(150, 300) == 50.0  # 150/300 * 100

def test_capital_allocation_reinvestor():
    """Capital allocation: (+,-,-) = Reinvestor."""
    assert classify_capital_allocation(500, -200, -100) == "Reinvestor"
