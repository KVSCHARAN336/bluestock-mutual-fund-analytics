import pytest
from src.etl.normaliser import normalize_year, normalize_ticker

# ==============================================================================
# 20 Test Cases for normalize_year()
# ==============================================================================

def test_normalize_year_int():
    # 1. Simple integer input
    assert normalize_year(2021) == 2021

def test_normalize_year_float():
    # 2. Float input
    assert normalize_year(2021.0) == 2021

def test_normalize_year_float_zero():
    # 3. Another float input
    assert normalize_year(2020.0) == 2020

def test_normalize_year_simple_string():
    # 4. Standard string input
    assert normalize_year("2021") == 2021

def test_normalize_year_string_spaces():
    # 5. String with leading/trailing spaces
    assert normalize_year("  2021  ") == 2021

def test_normalize_year_string_float():
    # 6. Float representation inside string
    assert normalize_year("2021.0") == 2021

def test_normalize_year_fy_short():
    # 7. FY with 2 digits
    assert normalize_year("FY21") == 2021

def test_normalize_year_fy_short_space():
    # 8. FY with spaces and 2 digits
    assert normalize_year("FY 21") == 2021

def test_normalize_year_fy_long():
    # 9. FY with 4 digits
    assert normalize_year("FY2021") == 2021

def test_normalize_year_fy_long_space():
    # 10. FY with spaces and 4 digits
    assert normalize_year("FY 2021") == 2021

def test_normalize_year_range_short():
    # 11. Range "2020-21" (standard Indian FY representation)
    assert normalize_year("2020-21") == 2021

def test_normalize_year_range_short_next():
    # 12. Range "2021-22"
    assert normalize_year("2021-22") == 2022

def test_normalize_year_range_long():
    # 13. Range "2021-2022"
    assert normalize_year("2021-2022") == 2022

def test_normalize_year_fy_range():
    # 14. Prefix FY and range combined
    assert normalize_year("FY 2020-21") == 2021

def test_normalize_year_century_boundary():
    # 15. Century boundary range "1999-00" -> 2000
    assert normalize_year("1999-00") == 2000

def test_normalize_year_century_boundary_90s():
    # 16. FY in the 90s (FY99 -> 1999)
    assert normalize_year("FY99") == 1999

def test_normalize_year_fy_boundary_00():
    # 17. FY 00 -> 2000
    assert normalize_year("FY 00") == 2000

def test_normalize_year_month_text():
    # 18. String with month names
    assert normalize_year("March 2021") == 2021

def test_normalize_year_date_slash():
    # 19. Date string with slashes
    assert normalize_year("2021/03/31") == 2021

def test_normalize_year_invalid():
    # 20. Non-parseable string should raise ValueError
    with pytest.raises(ValueError):
        normalize_year("abc")


# ==============================================================================
# 15 Test Cases for normalize_ticker()
# ==============================================================================

def test_normalize_ticker_simple():
    # 1. Standard ticker
    assert normalize_ticker("RELIANCE") == "RELIANCE"

def test_normalize_ticker_spaces():
    # 2. Leading/trailing spaces
    assert normalize_ticker("  RELIANCE  ") == "RELIANCE"

def test_normalize_ticker_lowercase():
    # 3. Lowercase input
    assert normalize_ticker("reliance") == "RELIANCE"

def test_normalize_ticker_ns_suffix():
    # 4. Exchange suffix .NS
    assert normalize_ticker("RELIANCE.NS") == "RELIANCE"

def test_normalize_ticker_bo_suffix():
    # 5. Exchange suffix .BO
    assert normalize_ticker("TCS.BO") == "TCS"

def test_normalize_ticker_bse_prefix():
    # 6. Exchange prefix BSE:
    assert normalize_ticker("BSE:500325") == "500325"

def test_normalize_ticker_bom_prefix():
    # 7. Exchange prefix BOM:
    assert normalize_ticker("BOM:500325") == "500325"

def test_normalize_ticker_prefix_spaces():
    # 8. Exchange prefix with spaces
    assert normalize_ticker("BOM : 500325") == "500325"

def test_normalize_ticker_nse_prefix():
    # 9. Exchange prefix NSE:
    assert normalize_ticker("NSE:RELIANCE") == "RELIANCE"

def test_normalize_ticker_numeric():
    # 10. Numeric code
    assert normalize_ticker("500325") == "500325"

def test_normalize_ticker_numeric_spaces():
    # 11. Numeric code with spaces
    assert normalize_ticker(" 500325 ") == "500325"

def test_normalize_ticker_ampersand():
    # 12. Ticker with ampersand
    assert normalize_ticker("M&M") == "M&M"

def test_normalize_ticker_hyphen():
    # 13. Ticker with hyphen
    assert normalize_ticker("SBI-E") == "SBI-E"

def test_normalize_ticker_combined():
    # 14. Combined prefix and suffix
    assert normalize_ticker("NSE:RELIANCE.NS") == "RELIANCE"

def test_normalize_ticker_empty():
    # 15. Empty values should return None
    assert normalize_ticker(None) is None
    assert normalize_ticker("") is None
