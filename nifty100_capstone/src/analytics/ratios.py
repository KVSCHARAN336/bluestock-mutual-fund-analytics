"""
Sprint 2 — Day 08 & 09: Profitability, Leverage & Efficiency Ratios
====================================================================
Implements NPM, OPM, ROE, ROCE, ROA, D/E, ICR, Net Debt, Asset Turnover.
Handles edge cases: negative equity, debt-free, zero denominators, financial sector carve-outs.
"""

from typing import Optional, Tuple

# ─────────────────────────────────────────────
# Day 08 — Profitability Ratios
# ─────────────────────────────────────────────

def net_profit_margin(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """NPM = net_profit / sales × 100. Returns None if sales is 0 or missing."""
    if sales is None or net_profit is None or sales == 0:
        return None
    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """OPM = operating_profit / sales × 100. Returns None if sales is 0 or missing."""
    if sales is None or operating_profit is None or sales == 0:
        return None
    return round((operating_profit / sales) * 100, 2)


def opm_cross_check(computed_opm: Optional[float], reported_opm: Optional[float], threshold: float = 1.0) -> Optional[str]:
    """
    Cross-check computed OPM against the reported opm_percentage field.
    Returns a warning message if difference > threshold %, else None.
    """
    if computed_opm is None or reported_opm is None:
        return None
    diff = abs(computed_opm - reported_opm)
    if diff > threshold:
        return f"OPM mismatch: computed={computed_opm:.2f}%, reported={reported_opm:.2f}%, diff={diff:.2f}%"
    return None


def return_on_equity(net_profit: Optional[float], equity_capital: Optional[float],
                     reserves: Optional[float]) -> Optional[float]:
    """ROE = net_profit / (equity_capital + reserves) × 100. Returns None if equity+reserves <= 0."""
    if net_profit is None or equity_capital is None or reserves is None:
        return None
    shareholder_equity = equity_capital + reserves
    if shareholder_equity <= 0:
        return None
    return round((net_profit / shareholder_equity) * 100, 2)


def return_on_capital_employed(operating_profit: Optional[float], other_income: Optional[float],
                               equity_capital: Optional[float], reserves: Optional[float],
                               borrowings: Optional[float]) -> Optional[float]:
    """
    ROCE = EBIT / Capital Employed × 100
    EBIT = operating_profit + other_income
    Capital Employed = equity_capital + reserves + borrowings
    Returns None if capital employed <= 0.
    """
    if operating_profit is None or equity_capital is None or reserves is None or borrowings is None:
        return None
    other_inc = other_income if other_income is not None else 0.0
    ebit = operating_profit + other_inc
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return round((ebit / capital_employed) * 100, 2)


def return_on_assets(net_profit: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """ROA = net_profit / total_assets × 100. Returns None if total_assets is 0 or missing."""
    if net_profit is None or total_assets is None or total_assets == 0:
        return None
    return round((net_profit / total_assets) * 100, 2)


# ─────────────────────────────────────────────
# Day 09 — Leverage & Efficiency Ratios
# ─────────────────────────────────────────────

def debt_to_equity(borrowings: Optional[float], equity_capital: Optional[float],
                   reserves: Optional[float]) -> Optional[float]:
    """
    D/E = borrowings / (equity_capital + reserves).
    Returns 0 (not None) if borrowings = 0 (debt-free).
    Returns None if equity+reserves <= 0.
    """
    if equity_capital is None or reserves is None:
        return None
    shareholder_equity = equity_capital + reserves
    if shareholder_equity <= 0:
        return None
    b = borrowings if borrowings is not None else 0.0
    if b == 0:
        return 0.0
    return round(b / shareholder_equity, 2)


def high_leverage_flag(de_ratio: Optional[float], is_financial_sector: bool) -> int:
    """
    Returns 1 if D/E > 5 AND company is NOT in Financials sector.
    Financial sector companies are exempt (structurally high leverage is normal).
    """
    if de_ratio is None:
        return 0
    if is_financial_sector:
        return 0
    return 1 if de_ratio > 5.0 else 0


def interest_coverage_ratio(operating_profit: Optional[float], other_income: Optional[float],
                            interest: Optional[float]) -> Tuple[Optional[float], str]:
    """
    ICR = (operating_profit + other_income) / interest.
    Returns (None, 'Debt Free') if interest = 0.
    Returns (value, 'At Risk') if ICR < 1.5.
    Returns (value, '') otherwise.
    """
    if interest is None or interest == 0:
        return None, "Debt Free"
    if operating_profit is None:
        return None, ""
    other_inc = other_income if other_income is not None else 0.0
    icr = round((operating_profit + other_inc) / interest, 2)
    label = "At Risk" if icr < 1.5 else ""
    return icr, label


def net_debt(borrowings: Optional[float], investments: Optional[float]) -> Optional[float]:
    """Net Debt = borrowings - investments (investments as liquid asset proxy)."""
    b = borrowings if borrowings is not None else 0.0
    inv = investments if investments is not None else 0.0
    return round(b - inv, 2)


def asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """Asset Turnover = sales / total_assets. Returns None if total_assets is 0 or missing."""
    if sales is None or total_assets is None or total_assets == 0:
        return None
    return round(sales / total_assets, 2)


# ─────────────────────────────────────────────
# Per-Share Metrics
# ─────────────────────────────────────────────

def book_value_per_share(equity_capital: Optional[float], reserves: Optional[float],
                         face_value: int = 10) -> Optional[float]:
    """Book Value Per Share = (equity_capital + reserves) / (equity_capital / face_value)."""
    if equity_capital is None or reserves is None or equity_capital == 0:
        return None
    num_shares = equity_capital / face_value
    if num_shares <= 0:
        return None
    return round((equity_capital + reserves) / num_shares, 2)
