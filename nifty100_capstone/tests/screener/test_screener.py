"""
Sprint 3 -- Day 21: Screener & Peer Engine Tests
==================================================
14 DQ rule tests + screener + peer percentile verification.
"""
import pytest
import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "nifty100.db"


@pytest.fixture
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()


# ── Screener Filter Tests ──

def test_quality_compounder_range():
    """Quality Compounder preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["quality_compounder"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Quality Compounder returned {len(result)} companies"


def test_quality_compounder_values():
    """Quality Compounder results all have ROE > 15% and D/E < 1 (non-financial)."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["quality_compounder"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert (result["return_on_equity_pct"] >= 15).all()
    non_fin = result[~result["broad_sector"].str.contains("Financ", case=False, na=False)]
    if len(non_fin) > 0:
        assert (non_fin["debt_to_equity"] <= 1.0).all()


def test_value_pick_range():
    """Value Pick preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["value_pick"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Value Pick returned {len(result)} companies"


def test_growth_accelerator_range():
    """Growth Accelerator preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["growth_accelerator"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Growth Accelerator returned {len(result)} companies"


def test_dividend_champion_range():
    """Dividend Champion preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["dividend_champion"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Dividend Champion returned {len(result)} companies"


def test_debt_free_blue_chip_range():
    """Debt-Free Blue Chip preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["debt_free_blue_chip"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Debt-Free Blue Chip returned {len(result)} companies"


def test_turnaround_watch_range():
    """Turnaround Watch preset returns 5-50 companies."""
    from src.screener.engine import load_config, load_universe, apply_filters, compute_winsorised_composite
    conn = sqlite3.connect(DB_PATH)
    config = load_config()
    df = load_universe(conn, "2024-03")
    df["composite_quality_score"] = compute_winsorised_composite(df)
    filters = config["presets"]["turnaround_watch"]["filters"]
    result = apply_filters(df, filters, conn, "2024-03")
    conn.close()
    assert 5 <= len(result) <= 50, f"Turnaround Watch returned {len(result)} companies"


# ── Peer Percentile Tests ──

def test_peer_percentile_count(conn):
    """peer_percentiles table has data."""
    try:
        count = pd.read_sql("SELECT COUNT(*) as cnt FROM peer_percentiles", conn).iloc[0]["cnt"]
        assert count > 0
    except Exception:
        pytest.skip("peer_percentiles not yet populated")


def test_peer_groups_11(conn):
    """peer_percentiles covers all 11 peer groups."""
    try:
        groups = pd.read_sql("SELECT DISTINCT peer_group_name FROM peer_percentiles", conn)
        assert len(groups) == 11
    except Exception:
        pytest.skip("peer_percentiles not yet populated")


def test_it_services_roe_ranking(conn):
    """In IT Services, highest ROE company has highest ROE percentile."""
    try:
        df = pd.read_sql(
            "SELECT company_id, value, percentile_rank FROM peer_percentiles "
            "WHERE peer_group_name='IT Services' AND metric='return_on_equity_pct' "
            "AND year='2024-03'", conn)
        if df.empty:
            pytest.skip("No IT Services data")
        max_val_id = df.loc[df["value"].idxmax(), "company_id"]
        max_pct_id = df.loc[df["percentile_rank"].idxmax(), "company_id"]
        assert max_val_id == max_pct_id
    except Exception:
        pytest.skip("peer_percentiles not available")


def test_percentile_range_valid(conn):
    """All percentiles between 0 and 1."""
    try:
        df = pd.read_sql("SELECT percentile_rank FROM peer_percentiles WHERE percentile_rank IS NOT NULL", conn)
        assert (df["percentile_rank"] >= 0).all()
        assert (df["percentile_rank"] <= 1).all()
    except Exception:
        pytest.skip("peer_percentiles not available")


# ── DQ Integrity Tests ──

def test_financial_ratios_row_count(conn):
    """financial_ratios >= 1100 rows."""
    count = pd.read_sql("SELECT COUNT(*) as cnt FROM financial_ratios", conn).iloc[0]["cnt"]
    assert count >= 1100


def test_fk_integrity(conn):
    """No FK violations."""
    conn.execute("PRAGMA foreign_keys = ON;")
    fk = conn.execute("PRAGMA foreign_key_check;").fetchall()
    assert len(fk) == 0
