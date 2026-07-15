"""
Sprint 2 — Day 10: CAGR Engine
================================
Compound Annual Growth Rate calculator with 6 edge-case handlers.

Edge Cases:
  1. Positive→Positive: compute normally
  2. Positive→Negative: return None, flag DECLINE_TO_LOSS
  3. Negative→Positive: return None, flag TURNAROUND
  4. Negative→Negative: return None, flag BOTH_NEGATIVE
  5. Zero base: return None, flag ZERO_BASE
  6. Less than n years of data: return None, flag INSUFFICIENT
"""

from typing import Optional, Tuple, List, Dict
import pandas as pd


def compute_cagr(start_value: float, end_value: float, n_years: int) -> Tuple[Optional[float], str]:
    """
    CAGR = ((end / start) ^ (1/n) - 1) × 100

    Returns:
        (cagr_value, flag)  where flag is '' for normal or an edge-case label.
    """
    if n_years <= 0:
        return None, "INSUFFICIENT"

    # Edge case 5: Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Edge case 3: Negative→Positive (TURNAROUND)
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Edge case 2: Positive→Negative (DECLINE_TO_LOSS)
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Edge case 4: Both negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Edge case: end is zero (decline to zero)
    if end_value == 0:
        return -100.0, ""

    # Normal case: both positive
    ratio = end_value / start_value
    cagr = (ratio ** (1.0 / n_years) - 1) * 100
    return round(cagr, 2), ""


def compute_cagr_for_series(values: Dict[str, float], current_year: str,
                            n_years: int) -> Tuple[Optional[float], str]:
    """
    Given a dict of {year: value} and a current_year, compute CAGR over n_years.
    The start year is calculated by subtracting n_years from the current year.

    Returns (cagr_value, flag).
    """
    if not values or current_year not in values:
        return None, "INSUFFICIENT"

    # Extract base year (YYYY-MM format, subtract n_years from YYYY part)
    try:
        if current_year == "TTM":
            return None, "INSUFFICIENT"
        parts = current_year.split("-")
        current_yyyy = int(parts[0])
        month = parts[1] if len(parts) > 1 else "03"
        start_yyyy = current_yyyy - n_years
        start_year = f"{start_yyyy}-{month}"
    except (ValueError, IndexError):
        return None, "INSUFFICIENT"

    if start_year not in values:
        return None, "INSUFFICIENT"

    start_val = values[start_year]
    end_val = values[current_year]

    return compute_cagr(start_val, end_val, n_years)


def compute_all_cagrs(company_data: pd.DataFrame, metric_col: str,
                      current_year: str) -> Dict[str, Tuple[Optional[float], str]]:
    """
    Compute 3yr, 5yr, 10yr CAGRs for a given metric column.

    Args:
        company_data: DataFrame with 'year' and metric_col columns for ONE company.
        metric_col: Column name (e.g. 'sales', 'net_profit', 'eps').
        current_year: The year to compute CAGRs for.

    Returns:
        Dict with keys '3yr', '5yr', '10yr', each mapping to (value, flag).
    """
    # Build year→value mapping
    values = {}
    for _, row in company_data.iterrows():
        yr = row.get("year")
        val = row.get(metric_col)
        if yr is not None and val is not None and not pd.isna(val):
            values[str(yr)] = float(val)

    results = {}
    for window, label in [(3, "3yr"), (5, "5yr"), (10, "10yr")]:
        cagr_val, flag = compute_cagr_for_series(values, current_year, window)
        results[label] = (cagr_val, flag)

    return results
