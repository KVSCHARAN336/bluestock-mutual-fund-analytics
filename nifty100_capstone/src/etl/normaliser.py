import re
from typing import Optional, Any

def normalize_year(year_val: Any) -> Optional[str]:
    """
    Standardises various financial year formats into a YYYY-MM string or 'TTM'.
    Examples:
      - 2021.0 or 2021 -> "2021-03" (defaults to March financial year close)
      - "Mar 2024" or "Mar-24" -> "2024-03"
      - "Dec 2012" -> "2012-12"
      - "TTM" -> "TTM"
      - "2020-21" or "2020-2021" -> "2021-03"
      - "FY21" -> "2021-03"
    """
    if year_val is None or (isinstance(year_val, float) and np_isnan_check(year_val)):
        return None
        
    s = str(year_val).strip()
    if not s:
        return None

    # Handle TTM
    if s.upper() == "TTM":
        return "TTM"

    # Map of month names to numbers
    months_map = {
        "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
        "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
    }

    # Pattern A: Month Name + Year (e.g. "Mar 2024" or "Mar-24" or "March 2024")
    m_month_year = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ]*(\d{2,4})", s, re.IGNORECASE)
    if m_month_year:
        month_name = m_month_year.group(1).upper()
        month_num = months_map[month_name]
        year_part = m_month_year.group(2)
        if len(year_part) == 2:
            val = int(year_part)
            year_val_clean = 2000 + val if val <= 50 else 1900 + val
        else:
            year_val_clean = int(year_part)
        return f"{year_val_clean}-{month_num}"

    # Pattern B: FY YYYY-YY or FY YYYY-YYYY range (e.g. "FY 2020-21")
    m_fy_range = re.match(r"^FY\s*(\d{4})-(\d{2,4})$", s, re.IGNORECASE)
    if m_fy_range:
        start_year = int(m_fy_range.group(1))
        end_part = m_fy_range.group(2)
        if len(end_part) == 2:
            century = start_year // 100
            end_year = century * 100 + int(end_part)
            if end_year < start_year:
                end_year += 100
            return f"{end_year}-03"
        elif len(end_part) == 4:
            return f"{int(end_part)}-03"

    # Pattern C: Financial Year Range "YYYY-YY" or "YYYY-YYYY" without FY (e.g., "2020-21" or "2021-2022")
    m_range = re.match(r"^(\d{4})-(\d{2,4})$", s)
    if m_range:
        start_year = int(m_range.group(1))
        end_part = m_range.group(2)
        if len(end_part) == 2:
            century = start_year // 100
            end_year = century * 100 + int(end_part)
            if end_year < start_year:
                end_year += 100
            return f"{end_year}-03"
        elif len(end_part) == 4:
            return f"{int(end_part)}-03"

    # Pattern D: "FY" format (e.g., "FY21", "FY 21", "FY2021", "FY 2021")
    m_fy = re.match(r"^FY\s*(\d{2,4})$", s, re.IGNORECASE)
    if m_fy:
        digits = m_fy.group(1)
        if len(digits) == 2:
            val = int(digits)
            year_val_clean = 2000 + val if val <= 50 else 1900 + val
        elif len(digits) == 4:
            year_val_clean = int(digits)
        return f"{year_val_clean}-03"

    # Pattern E: Simple Year digit (e.g., 2021 or 2021.0 or "2021")
    m_simple = re.match(r"^(\d{4})(?:\.0+)?$", s)
    if m_simple:
        return f"{m_simple.group(1)}-03"

    # Fallback search: extract any 4-digit number that looks like a year
    m_search = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if m_search:
        return f"{m_search.group(1)}-03"

    raise ValueError(f"Unable to parse financial year: '{year_val}'")

def normalize_ticker(ticker_val: Any) -> Optional[str]:
    """
    Standardises stock tickers by:
      - Stripping whitespace and converting to uppercase
      - Removing exchange suffixes (.NS, .BO)
      - Removing exchange prefixes (BSE:, BOM:, NSE:, BOM : )
      - Extracting core alpha-numeric code
    """
    if ticker_val is None or (isinstance(ticker_val, float) and np_isnan_check(ticker_val)):
        return None
        
    s = str(ticker_val).strip().upper()
    if not s:
        return None

    # Remove exchange prefixes (BSE:, NSE:, BOM:)
    s = re.sub(r"^(?:BSE|NSE|BOM)\s*:\s*", "", s)

    # Remove exchange suffixes (.NS, .BO)
    s = re.sub(r"\.(?:NS|BO)$", "", s)

    s = s.strip()
    if re.match(r"^\d+$", s):
        return s

    s = re.sub(r"[^A-Z0-9&\-]", "", s)
    return s if s else None

def np_isnan_check(val: Any) -> bool:
    try:
        import numpy as np
        return np.isnan(val)
    except ImportError:
        return val != val
