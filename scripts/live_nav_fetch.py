"""
Bluestock Mutual Fund Analytics - Live NAV Fetcher
====================================================
Fetches real-time NAV data from the MFAPI (https://api.mfapi.in)
with structured logging, retry mechanism, and error handling.

Author : Bluestock Fintech Analytics Team
Created: 2026-06-23
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ──────────────────────────────────────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "live_nav_fetch.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("live_nav_fetch")

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
LIVE_NAV_DIR = RAW_DIR / "live_nav"

MFAPI_BASE_URL = "https://api.mfapi.in/mf"

# Schemes to fetch
SCHEMES: Dict[int, str] = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0  # seconds
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 1.0  # seconds between requests


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Session with Retry
# ──────────────────────────────────────────────────────────────────────────────
def create_session() -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "BluestockMFAnalytics/1.0",
        "Accept": "application/json",
    })
    return session


# ──────────────────────────────────────────────────────────────────────────────
# Core Fetch Functions
# ──────────────────────────────────────────────────────────────────────────────
def fetch_nav_data(session: requests.Session, amfi_code: int) -> Optional[Dict]:
    """
    Fetch NAV data for a given AMFI code from MFAPI.

    Returns the parsed JSON response or None on failure.
    """
    url = f"{MFAPI_BASE_URL}/{amfi_code}"
    logger.info(f"Fetching NAV data for AMFI code {amfi_code} from {url}")

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        if "status" in data and data["status"] == "FAIL":
            logger.error(f"  API returned FAIL status for code {amfi_code}")
            return None

        scheme_name = data.get("meta", {}).get("scheme_name", "Unknown")
        nav_count = len(data.get("data", []))
        logger.info(f"  [OK] Fetched {nav_count} NAV records for '{scheme_name}'")

        return data

    except requests.exceptions.Timeout:
        logger.error(f"  [TIMEOUT] Timeout fetching code {amfi_code} (>{REQUEST_TIMEOUT}s)")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"  [CONN_ERR] Connection error fetching code {amfi_code}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"  [HTTP_ERR] HTTP error for code {amfi_code}: {e}")
        return None
    except json.JSONDecodeError:
        logger.error(f"  [JSON_ERR] Invalid JSON response for code {amfi_code}")
        return None
    except Exception as e:
        logger.error(f"  [ERROR] Unexpected error for code {amfi_code}: {e}")
        return None


def parse_nav_to_dataframe(data: Dict) -> Optional[pd.DataFrame]:
    """Parse MFAPI JSON response into a clean DataFrame."""
    if not data or "data" not in data:
        return None

    nav_records = data["data"]
    if not nav_records:
        return None

    meta = data.get("meta", {})

    df = pd.DataFrame(nav_records)

    # Clean and transform
    df.rename(columns={"date": "date_str", "nav": "nav"}, inplace=True)

    # Parse dates (MFAPI returns dd-MM-yyyy format)
    df["date"] = pd.to_datetime(df["date_str"], format="%d-%m-%Y", errors="coerce")

    # Convert NAV to numeric
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # Add metadata
    df["scheme_code"] = meta.get("scheme_code", "")
    df["scheme_name"] = meta.get("scheme_name", "")
    df["fund_house"] = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    # Select and order columns
    df = df[[
        "scheme_code", "scheme_name", "fund_house",
        "date", "nav",
        "scheme_type", "scheme_category",
    ]].copy()

    # Sort by date descending (latest first)
    df.sort_values("date", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Drop rows with invalid dates or NAVs
    df.dropna(subset=["date", "nav"], inplace=True)

    return df


def save_nav_csv(df: pd.DataFrame, filepath: Path, scheme_name: str) -> bool:
    """Save NAV DataFrame to CSV."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)
        logger.info(f"  [SAVED] {len(df)} records to {filepath.name}")
        return True
    except Exception as e:
        logger.error(f"  [ERROR] Failed to save {filepath.name}: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline Functions
# ──────────────────────────────────────────────────────────────────────────────
def fetch_single_live_nav(session: requests.Session, amfi_code: int = 125497) -> Optional[Path]:
    """
    Fetch latest NAV for HDFC Top 100 Direct (Requirement #9).
    Saves to data/raw/HDFC_Top100_live_nav.csv
    """
    logger.info("\n" + "─" * 60)
    logger.info("TASK: Fetch Live NAV — HDFC Top 100 Direct (125497)")
    logger.info("─" * 60)

    data = fetch_nav_data(session, amfi_code)
    if data is None:
        return None

    df = parse_nav_to_dataframe(data)
    if df is None or df.empty:
        logger.error("Failed to parse NAV data.")
        return None

    # Show latest NAV
    latest = df.iloc[0]
    logger.info(f"\n  [NAV] Latest NAV:")
    logger.info(f"     Scheme: {latest['scheme_name']}")
    logger.info(f"     Date:   {latest['date'].strftime('%Y-%m-%d')}")
    logger.info(f"     NAV:    Rs.{latest['nav']:.4f}")

    filepath = RAW_DIR / "HDFC_Top100_live_nav.csv"
    save_nav_csv(df, filepath, "HDFC Top 100")

    return filepath


def fetch_additional_nav_history(session: requests.Session) -> List[Path]:
    """
    Fetch NAV history for additional schemes (Requirement #10).
    Saves each to data/raw/live_nav/<scheme_name>.csv
    """
    logger.info("\n" + "─" * 60)
    logger.info("TASK: Fetch Additional NAV History")
    logger.info("─" * 60)

    LIVE_NAV_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for amfi_code, scheme_name in SCHEMES.items():
        if amfi_code == 125497:
            continue  # Already fetched separately

        logger.info(f"\n{'─' * 40}")
        logger.info(f"Fetching: {scheme_name} (AMFI: {amfi_code})")

        data = fetch_nav_data(session, amfi_code)
        if data is None:
            continue

        df = parse_nav_to_dataframe(data)
        if df is None or df.empty:
            logger.warning(f"  No data parsed for {scheme_name}")
            continue

        # Show latest NAV
        latest = df.iloc[0]
        logger.info(f"  [NAV] Latest: Rs.{latest['nav']:.4f} ({latest['date'].strftime('%Y-%m-%d')})")
        logger.info(f"  [DATA] Records: {len(df)} (from {df['date'].min().strftime('%Y-%m-%d')} "
                    f"to {df['date'].max().strftime('%Y-%m-%d')})")

        # Clean filename
        safe_name = scheme_name.replace(" ", "_").replace("/", "_")
        filepath = LIVE_NAV_DIR / f"{safe_name}_{amfi_code}.csv"
        if save_nav_csv(df, filepath, scheme_name):
            saved_files.append(filepath)

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    return saved_files


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    """Execute the live NAV fetch pipeline."""
    logger.info("=" * 80)
    logger.info("BLUESTOCK MUTUAL FUND ANALYTICS — LIVE NAV FETCHER")
    logger.info("=" * 80)

    start_time = datetime.now()
    session = create_session()

    # Requirement 9: Fetch HDFC Top 100 Direct live NAV
    hdfc_path = fetch_single_live_nav(session, amfi_code=125497)

    # Requirement 10: Fetch additional NAV history
    additional_paths = fetch_additional_nav_history(session)

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    total_files = (1 if hdfc_path else 0) + len(additional_paths)

    logger.info("\n" + "=" * 80)
    logger.info("LIVE NAV FETCH - COMPLETE")
    logger.info(f"  Files saved:   {total_files}")
    logger.info(f"  HDFC Top 100:  {'[OK]' if hdfc_path else '[FAIL]'}")
    logger.info(f"  Additional:    {len(additional_paths)} scheme(s)")
    logger.info(f"  Elapsed time:  {elapsed:.1f}s")
    logger.info("=" * 80)

    if hdfc_path:
        logger.info(f"\n  [FILE] {hdfc_path}")
    for p in additional_paths:
        logger.info(f"  [FILE] {p}")


if __name__ == "__main__":
    main()
