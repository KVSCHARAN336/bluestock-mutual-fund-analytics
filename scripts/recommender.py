"""
Fund Recommender — BlueStock MF Capstone
========================================
Input:  Risk appetite (Low / Moderate / High)
Output: Top 3 funds by Sharpe ratio within matching risk_grade

Usage:
    python recommender.py
    python recommender.py --risk High
"""

import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PERFORMANCE_CSV = os.path.join(SCRIPT_DIR, "07_scheme_performance.csv")

RISK_MAP = {
    "Low":      ["Low"],
    "Moderate": ["Moderate"],
    "High":     ["High", "Moderately High", "Very High"],
}

DISPLAY_COLS = [
    "scheme_name",
    "fund_house",
    "category",
    "risk_grade",
    "sharpe_ratio",
    "return_1yr_pct",
    "return_3yr_pct",
    "expense_ratio_pct",
    "morningstar_rating",
]

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_performance(path: str = PERFORMANCE_CSV) -> pd.DataFrame:
    """Load and validate scheme performance data."""
    df = pd.read_csv(path)
    required = {"risk_grade", "sharpe_ratio", "scheme_name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in performance CSV: {missing}")
    return df


def recommend(risk_appetite: str, df: pd.DataFrame | None = None, top_n: int = 3) -> pd.DataFrame:
    """
    Return top-N funds by Sharpe ratio for a given risk appetite.

    Parameters
    ----------
    risk_appetite : str
        One of 'Low', 'Moderate', 'High' (case-insensitive).
    df : pd.DataFrame, optional
        Pre-loaded performance DataFrame. Loaded from CSV if None.
    top_n : int
        Number of recommendations (default 3).

    Returns
    -------
    pd.DataFrame
        Top-N fund recommendations sorted by Sharpe ratio descending.
    """
    key = risk_appetite.strip().title()
    if key not in RISK_MAP:
        raise ValueError(
            f"Invalid risk appetite '{risk_appetite}'. Choose from: {list(RISK_MAP.keys())}"
        )

    if df is None:
        df = load_performance()

    grades = RISK_MAP[key]
    filtered = df[df["risk_grade"].isin(grades)].copy()

    if filtered.empty:
        print(f"  ⚠  No funds found for risk grade(s): {grades}")
        return pd.DataFrame(columns=DISPLAY_COLS)

    filtered = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    # Select display columns (only those that exist)
    cols = [c for c in DISPLAY_COLS if c in filtered.columns]
    return filtered[cols].reset_index(drop=True)


def print_table(df: pd.DataFrame, title: str = "") -> None:
    """Pretty-print a DataFrame as a table."""
    if title:
        print(f"\n{'═' * 80}")
        print(f"  {title}")
        print(f"{'═' * 80}")

    if df.empty:
        print("  (no results)")
        return

    try:
        from tabulate import tabulate
        print(tabulate(df, headers="keys", tablefmt="fancy_grid",
                       showindex=False, numalign="right"))
    except ImportError:
        print(df.to_string(index=False))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fund Recommender — top funds by Sharpe ratio for your risk appetite"
    )
    parser.add_argument(
        "--risk",
        type=str,
        default=None,
        choices=["Low", "Moderate", "High"],
        help="Risk appetite level. If omitted, prints all three.",
    )
    parser.add_argument(
        "--top", type=int, default=3,
        help="Number of recommendations per risk level (default: 3)",
    )
    args = parser.parse_args()

    df = load_performance()

    if args.risk:
        levels = [args.risk]
    else:
        levels = ["Low", "Moderate", "High"]

    print("\n🔷  BlueStock MF — Fund Recommender")
    print("─" * 80)

    for level in levels:
        recs = recommend(level, df=df, top_n=args.top)
        emoji = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}.get(level, "⚪")
        print_table(recs, title=f"{emoji}  Risk Appetite: {level}")

    print(f"\n{'─' * 80}")
    print("  Disclaimer: Past performance does not guarantee future returns.")
    print("  Data source: 07_scheme_performance.csv\n")


if __name__ == "__main__":
    main()
