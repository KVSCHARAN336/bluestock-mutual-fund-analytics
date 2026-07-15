"""
Sprint 2 — Day 11: Cash Flow KPIs & Capital Allocation
========================================================
Implements FCF, CFO Quality, CapEx Intensity, FCF Conversion, and 8-pattern Capital Allocation classifier.
"""

from typing import Optional, Tuple, List, Dict
import pandas as pd


def free_cash_flow(operating_activity: Optional[float],
                   investing_activity: Optional[float]) -> Optional[float]:
    """FCF = operating_activity + investing_activity. Negative value is allowed."""
    if operating_activity is None or investing_activity is None:
        return None
    return round(operating_activity + investing_activity, 2)


def cfo_quality_score(cfo_values: List[Optional[float]],
                      pat_values: List[Optional[float]]) -> Tuple[Optional[float], str]:
    """
    CFO Quality = avg(CFO/PAT) over available years.
    >1.0 = 'High Quality', 0.5-1.0 = 'Moderate', <0.5 = 'Accrual Risk'.
    Returns None if no valid PAT values.
    """
    ratios = []
    for cfo, pat in zip(cfo_values, pat_values):
        if cfo is not None and pat is not None and pat != 0:
            ratios.append(cfo / pat)
    if not ratios:
        return None, ""
    avg_ratio = sum(ratios) / len(ratios)
    avg_ratio = round(avg_ratio, 2)
    if avg_ratio > 1.0:
        label = "High Quality"
    elif avg_ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return avg_ratio, label


def capex_intensity(investing_activity: Optional[float],
                    sales: Optional[float]) -> Tuple[Optional[float], str]:
    """
    CapEx Intensity = abs(investing_activity) / sales × 100.
    <3% = 'Asset Light', 3-8% = 'Moderate', >8% = 'Capital Intensive'.
    Returns None if sales is 0 or missing.
    """
    if investing_activity is None or sales is None or sales == 0:
        return None, ""
    pct = round(abs(investing_activity) / sales * 100, 2)
    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return pct, label


def fcf_conversion(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    """FCF Conversion = FCF / operating_profit × 100. Returns None if operating_profit is 0."""
    if fcf is None or operating_profit is None or operating_profit == 0:
        return None
    return round((fcf / operating_profit) * 100, 2)


def classify_capital_allocation(cfo: Optional[float], cfi: Optional[float],
                                cff: Optional[float]) -> str:
    """
    8-pattern classifier based on sign of (CFO, CFI, CFF).
    Returns a pattern label string.
    """
    if cfo is None or cfi is None or cff is None:
        return "Unknown"

    s_cfo = "+" if cfo >= 0 else "-"
    s_cfi = "+" if cfi >= 0 else "-"
    s_cff = "+" if cff >= 0 else "-"
    pattern = f"({s_cfo},{s_cfi},{s_cff})"

    labels = {
        "(+,-,-)": "Reinvestor",
        "(+,+,-)": "Liquidating Assets",
        "(-,+,+)": "Distress Signal",
        "(-,-,+)": "Growth Funded by Debt",
        "(+,+,+)": "Cash Accumulator",
        "(-,-,-)": "Pre-Revenue",
        "(+,-,+)": "Mixed",
        "(-,+,-)": "Restructuring",
    }
    return labels.get(pattern, "Other")


def generate_capital_allocation_csv(cf_data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate capital allocation pattern for every company-year.
    Input: DataFrame with columns company_id, year, operating_activity, investing_activity, financing_activity.
    Output: DataFrame with company_id, year, cfo_sign, cfi_sign, cff_sign, pattern_label.
    """
    results = []
    for _, row in cf_data.iterrows():
        cfo = row.get("operating_activity")
        cfi = row.get("investing_activity")
        cff = row.get("financing_activity")
        company_id = row.get("company_id")
        year = row.get("year")

        s_cfo = "+" if (cfo is not None and cfo >= 0) else "-"
        s_cfi = "+" if (cfi is not None and cfi >= 0) else "-"
        s_cff = "+" if (cff is not None and cff >= 0) else "-"

        pattern_label = classify_capital_allocation(cfo, cfi, cff)

        results.append({
            "company_id": company_id,
            "year": year,
            "cfo_sign": s_cfo,
            "cfi_sign": s_cfi,
            "cff_sign": s_cff,
            "pattern_label": pattern_label,
        })
    return pd.DataFrame(results)
