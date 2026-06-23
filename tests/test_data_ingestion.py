"""
Bluestock MF Analytics — Unit Tests for Data Ingestion
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from data_ingestion import (
    profile_dataset,
    validate_data_quality,
    validate_amfi_codes,
    explore_fund_master,
    _validate_fund_master,
    _validate_nav_history,
)


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def sample_fund_master():
    """Create a minimal fund master DataFrame for testing."""
    return pd.DataFrame({
        "amfi_code": [119551, 120503, 118632, 119092, 120841],
        "fund_house": [
            "SBI Mutual Fund", "ICICI Prudential MF",
            "Nippon India MF", "Axis Mutual Fund", "Kotak Mahindra MF",
        ],
        "scheme_name": [
            "SBI Bluechip Fund", "ICICI Pru Bluechip Fund",
            "Nippon India Large Cap Fund", "Axis Bluechip Fund",
            "Kotak Bluechip Fund",
        ],
        "category": ["Equity"] * 5,
        "sub_category": ["Large Cap"] * 5,
        "plan": ["Regular", "Regular", "Regular", "Regular", "Regular"],
        "launch_date": [
            "2006-02-14", "2008-05-23", "2004-08-08",
            "2010-01-05", "2005-12-29",
        ],
        "benchmark": ["NIFTY 100 TRI"] * 5,
        "expense_ratio_pct": [1.54, 1.42, 1.51, 1.64, 1.59],
        "exit_load_pct": [1.0] * 5,
        "min_sip_amount": [500] * 5,
        "min_lumpsum_amount": [1000] * 5,
        "fund_manager": [
            "Sohini Andani", "Anish Tawakley", "Sailesh Raj Bhan",
            "Shreyash Devalkar", "Harsha Upadhyaya",
        ],
        "risk_category": ["Moderate"] * 5,
        "sebi_category_code": ["EC01"] * 5,
    })


@pytest.fixture
def sample_nav_history():
    """Create a minimal NAV history DataFrame for testing."""
    records = []
    for code in [119551, 120503, 118632, 119092]:
        for i in range(10):
            records.append({
                "amfi_code": code,
                "date": f"2025-01-{i+1:02d}",
                "nav": 50.0 + np.random.uniform(-5, 5),
            })
    return pd.DataFrame(records)


@pytest.fixture
def sample_empty_df():
    """Create an empty DataFrame."""
    return pd.DataFrame()


# ──────────────────────────────────────────────────────────────────────────────
# Tests: Profile Dataset
# ──────────────────────────────────────────────────────────────────────────────
class TestProfileDataset:
    def test_profile_returns_dict(self, sample_fund_master):
        result = profile_dataset("test", sample_fund_master)
        assert isinstance(result, dict)

    def test_profile_contains_required_keys(self, sample_fund_master):
        result = profile_dataset("test", sample_fund_master)
        required_keys = [
            "name", "shape", "dtypes", "head", "missing_values",
            "total_missing", "missing_pct", "duplicate_rows",
            "summary_stats", "memory_mb",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_profile_shape(self, sample_fund_master):
        result = profile_dataset("test", sample_fund_master)
        assert result["shape"] == (5, 15)

    def test_profile_no_missing(self, sample_fund_master):
        result = profile_dataset("test", sample_fund_master)
        assert result["total_missing"] == 0

    def test_profile_no_duplicates(self, sample_fund_master):
        result = profile_dataset("test", sample_fund_master)
        assert result["duplicate_rows"] == 0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: Validate Data Quality
# ──────────────────────────────────────────────────────────────────────────────
class TestValidateDataQuality:
    def test_clean_data_no_issues(self, sample_fund_master):
        result = validate_data_quality("fund_master", sample_fund_master)
        assert result["dataset"] == "fund_master"
        assert isinstance(result["issues"], list)

    def test_missing_values_detected(self):
        df = pd.DataFrame({"a": [1, 2, None], "b": [None, None, 3]})
        result = validate_data_quality("test", df)
        missing_issues = [i for i in result["issues"] if i["check"] == "missing_values"]
        assert len(missing_issues) > 0

    def test_duplicates_detected(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
        result = validate_data_quality("test", df)
        dup_issues = [i for i in result["issues"] if i["check"] == "duplicate_rows"]
        assert len(dup_issues) == 1
        assert dup_issues[0]["count"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Tests: AMFI Validation
# ──────────────────────────────────────────────────────────────────────────────
class TestAMFIValidation:
    def test_full_coverage(self, sample_fund_master, sample_nav_history):
        # NAV history has 4 of 5 codes
        result = validate_amfi_codes(sample_fund_master, sample_nav_history)
        assert result["total_master_schemes"] == 5
        assert result["matched_schemes"] == 4
        assert 120841 in result["missing_from_nav"]
        assert result["coverage_pct"] == 80.0

    def test_perfect_match(self):
        master = pd.DataFrame({"amfi_code": [100, 200]})
        nav = pd.DataFrame({"amfi_code": [100, 200, 100, 200]})
        result = validate_amfi_codes(master, nav)
        assert result["coverage_pct"] == 100.0
        assert len(result["missing_from_nav"]) == 0


# ──────────────────────────────────────────────────────────────────────────────
# Tests: Fund Master Exploration
# ──────────────────────────────────────────────────────────────────────────────
class TestFundMasterExploration:
    def test_exploration_keys(self, sample_fund_master):
        result = explore_fund_master(sample_fund_master)
        assert "unique_fund_houses" in result
        assert "num_fund_houses" in result
        assert result["num_fund_houses"] == 5

    def test_total_schemes(self, sample_fund_master):
        result = explore_fund_master(sample_fund_master)
        assert result["total_schemes"] == 5

    def test_categories(self, sample_fund_master):
        result = explore_fund_master(sample_fund_master)
        assert "Equity" in result["categories"]


# ──────────────────────────────────────────────────────────────────────────────
# Tests: Fund Master Specific Validations
# ──────────────────────────────────────────────────────────────────────────────
class TestFundMasterValidation:
    def test_valid_risk_categories(self, sample_fund_master):
        issues = _validate_fund_master(sample_fund_master)
        risk_issues = [i for i in issues if i["check"] == "invalid_risk_category"]
        assert len(risk_issues) == 0

    def test_invalid_risk_category_detected(self):
        df = pd.DataFrame({
            "amfi_code": [100],
            "risk_category": ["INVALID"],
            "category": ["Equity"],
            "launch_date": ["2020-01-01"],
        })
        issues = _validate_fund_master(df)
        risk_issues = [i for i in issues if i["check"] == "invalid_risk_category"]
        assert len(risk_issues) == 1


# ──────────────────────────────────────────────────────────────────────────────
# Tests: NAV History Validation
# ──────────────────────────────────────────────────────────────────────────────
class TestNAVHistoryValidation:
    def test_valid_nav_no_issues(self, sample_nav_history):
        issues = _validate_nav_history(sample_nav_history)
        nav_issues = [i for i in issues if i["check"] == "invalid_nav_values"]
        assert len(nav_issues) == 0

    def test_negative_nav_detected(self):
        df = pd.DataFrame({
            "amfi_code": [100, 100],
            "date": ["2025-01-01", "2025-01-02"],
            "nav": [-5.0, 50.0],
        })
        issues = _validate_nav_history(df)
        nav_issues = [i for i in issues if i["check"] == "invalid_nav_values"]
        assert len(nav_issues) == 1
        assert nav_issues[0]["count"] == 1
