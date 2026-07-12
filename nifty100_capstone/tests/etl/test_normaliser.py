import pytest
# pyrefly: ignore [missing-import]
from src.etl.normaliser import normalize_year, normalize_ticker

# ==============================================================================
# 20 Test Cases for normalize_year()
# ==============================================================================

def test_normalize_year_int():
    assert normalize_year(2021) == "2021-03"

def test_normalize_year_float():
    assert normalize_year(2021.0) == "2021-03"

def test_normalize_year_float_zero():
    assert normalize_year(2020.0) == "2020-03"

def test_normalize_year_simple_string():
    assert normalize_year("2021") == "2021-03"

def test_normalize_year_string_spaces():
    assert normalize_year("  2021  ") == "2021-03"

def test_normalize_year_string_float():
    assert normalize_year("2021.0") == "2021-03"

def test_normalize_year_fy_short():
    assert normalize_year("FY21") == "2021-03"

def test_normalize_year_fy_short_space():
    assert normalize_year("FY 21") == "2021-03"

def test_normalize_year_fy_long():
    assert normalize_year("FY2021") == "2021-03"

def test_normalize_year_fy_long_space():
    assert normalize_year("FY 2021") == "2021-03"

def test_normalize_year_range_short():
    assert normalize_year("2020-21") == "2021-03"

def test_normalize_year_range_short_next():
    assert normalize_year("2021-22") == "2022-03"

def test_normalize_year_range_long():
    assert normalize_year("2021-2022") == "2022-03"

def test_normalize_year_fy_range():
    assert normalize_year("FY 2020-21") == "2021-03"

def test_normalize_year_century_boundary():
    assert normalize_year("1999-00") == "2000-03"

def test_normalize_year_century_boundary_90s():
    assert normalize_year("FY99") == "1999-03"

def test_normalize_year_fy_boundary_00():
    assert normalize_year("FY 00") == "2000-03"

def test_normalize_year_month_text():
    assert normalize_year("March 2021") == "2021-03"

def test_normalize_year_date_slash():
    assert normalize_year("2021/03/31") == "2021-03"

def test_normalize_year_ttm():
    assert normalize_year("TTM") == "TTM"

def test_normalize_year_invalid():
    with pytest.raises(ValueError):
        normalize_year("abc")


# ==============================================================================
# 15 Test Cases for normalize_ticker()
# ==============================================================================

def test_normalize_ticker_simple():
    assert normalize_ticker("RELIANCE") == "RELIANCE"

def test_normalize_ticker_spaces():
    assert normalize_ticker("  RELIANCE  ") == "RELIANCE"

def test_normalize_ticker_lowercase():
    assert normalize_ticker("reliance") == "RELIANCE"

def test_normalize_ticker_ns_suffix():
    assert normalize_ticker("RELIANCE.NS") == "RELIANCE"

def test_normalize_ticker_bo_suffix():
    assert normalize_ticker("TCS.BO") == "TCS"

def test_normalize_ticker_bse_prefix():
    assert normalize_ticker("BSE:500325") == "500325"

def test_normalize_ticker_bom_prefix():
    assert normalize_ticker("BOM:500325") == "500325"

def test_normalize_ticker_prefix_spaces():
    assert normalize_ticker("BOM : 500325") == "500325"

def test_normalize_ticker_nse_prefix():
    assert normalize_ticker("NSE:RELIANCE") == "RELIANCE"

def test_normalize_ticker_numeric():
    assert normalize_ticker("500325") == "500325"

def test_normalize_ticker_numeric_spaces():
    assert normalize_ticker(" 500325 ") == "500325"

def test_normalize_ticker_ampersand():
    assert normalize_ticker("M&M") == "M&M"

def test_normalize_ticker_hyphen():
    assert normalize_ticker("SBI-E") == "SBI-E"

def test_normalize_ticker_combined():
    assert normalize_ticker("NSE:RELIANCE.NS") == "RELIANCE"

def test_normalize_ticker_empty():
    assert normalize_ticker(None) is None
    assert normalize_ticker("") is None
