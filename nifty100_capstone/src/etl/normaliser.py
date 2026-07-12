import re
from typing import Optional, Any

def normalize_year(year_val: Any) -> Optional[int]:
    """
    Standardises various financial year formats into a 4-digit calendar year integer.
    Examples:
      - 2021.0 or 2021 -> 2021
      - " 2021 " -> 2021
      - "FY21" or "FY 21" -> 2021
      - "FY 2021" or "FY2021" -> 2021
      - "2020-21" -> 2021
      - "2021-22" -> 2022
      - "2021-2022" -> 2022
    """
    if year_val is None or (isinstance(year_val, float) and np_isnan_check(year_val)):
        return None
        
    # Handle direct numeric types
    if isinstance(year_val, (int, float)):
        try:
            val = int(year_val)
            if 1900 <= val <= 2100:
                return val
        except (ValueError, TypeError):
            pass

    # Convert to string and clean
    s = str(year_val).strip()
    if not s:
        return None

    # Pattern 1: Simple 4-digit number (e.g., "2021" or "2021.0")
    m_simple = re.match(r"^(\d{4})(?:\.0+)?$", s)
    if m_simple:
        return int(m_simple.group(1))

    # Pattern 2: Financial Year Range "YYYY-YY" or "YYYY-YYYY" (e.g., "2020-21" or "2021-2022")
    m_range = re.match(r"^(\d{4})-(\d{2,4})$", s)
    if m_range:
        start_year = int(m_range.group(1))
        end_part = m_range.group(2)
        if len(end_part) == 2:
            # e.g., "2020-21" -> 2021
            century = start_year // 100
            end_year = century * 100 + int(end_part)
            if end_year < start_year: # Handle century boundary like 1999-00
                end_year += 100
            return end_year
        elif len(end_part) == 4:
            # e.g., "2021-2022" -> 2022
            return int(end_part)

    # Pattern 3: "FY" format (e.g., "FY21", "FY 21", "FY2021", "FY 2021")
    m_fy = re.match(r"^FY\s*(\d{2,4})$", s, re.IGNORECASE)
    if m_fy:
        digits = m_fy.group(1)
        if len(digits) == 2:
            val = int(digits)
            # Threshold: <= 50 -> 20XX, > 50 -> 19XX
            return 2000 + val if val <= 50 else 1900 + val
        elif len(digits) == 4:
            return int(digits)

    # Pattern 4: Year with FY prefix and range (e.g. "FY 2020-21")
    m_fy_range = re.match(r"^FY\s*(\d{4})-(\d{2,4})$", s, re.IGNORECASE)
    if m_fy_range:
        start_year = int(m_fy_range.group(1))
        end_part = m_fy_range.group(2)
        if len(end_part) == 2:
            return (start_year // 100) * 100 + int(end_part)
        elif len(end_part) == 4:
            return int(end_part)

    # Fallback search: extract any 4-digit number that looks like a year
    m_search = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if m_search:
        return int(m_search.group(1))

    raise ValueError(f"Unable to parse financial year: '{year_val}'")

def normalize_ticker(ticker_val: Any) -> Optional[str]:
    """
    Standardises stock tickers by:
      - Stripping whitespace and converting to uppercase
      - Removing exchange suffixes (.NS, .BO)
      - Removing exchange prefixes (BSE:, BOM:, NSE:, BOM : )
      - Extracting core alpha-numeric code
    Examples:
      - "RELIANCE.NS" -> "RELIANCE"
      - "TCS.BO" -> "TCS"
      - "BSE:500325" -> "500325"
      - "BOM : 500325" -> "500325"
      - "  RELIANCE  " -> "RELIANCE"
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

    # Remove leading/trailing spaces again
    s = s.strip()

    # If it is numeric (BSE code), keep it clean
    if re.match(r"^\d+$", s):
        return s

    # Ensure it only contains standard ticker characters (remove any extra text/junk)
    # Tickers are usually alphanumeric, e.g. "RELIANCE" or "M&M" or "L&TFH" or "SBI-E"
    s = re.sub(r"[^A-Z0-9&\-]", "", s)
    
    return s if s else None

def np_isnan_check(val: Any) -> bool:
    """Helper to check for nan without importing numpy globally if not needed."""
    try:
        import numpy as np
        return np.isnan(val)
    except ImportError:
        return val != val
