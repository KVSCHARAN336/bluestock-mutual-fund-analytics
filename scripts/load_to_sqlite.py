from sqlalchemy import create_engine
import pandas as pd
import sqlite3
from pathlib import Path

def load_data():
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "bluestock_mf.db"
    engine = create_engine(f"sqlite:///{db_path}")

    # First, apply the schema.sql to create the tables properly
    with sqlite3.connect(db_path) as conn:
        with open(project_root / "sql" / "schema.sql", "r") as f:
            conn.executescript(f.read())
            
    print("Loading dim_fund...")
    df_fund = pd.read_csv(project_root / "data" / "processed" / "clean_fund_master.csv")
    df_fund = df_fund[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "expense_ratio_pct", "risk_category"]]
    df_fund.to_sql("dim_fund", engine, if_exists="replace", index=False)

    print("Loading fact_nav...")
    df_nav = pd.read_csv(project_root / "data" / "processed" / "clean_nav_history.csv")
    df_nav = df_nav.rename(columns={"date": "nav_date"})
    df_nav.to_sql("fact_nav", engine, if_exists="replace", index=False)

    print("Loading fact_transactions...")
    df_tx = pd.read_csv(project_root / "data" / "processed" / "clean_transactions.csv")
    # Exclude tx_id so it auto-increments, or just use pandas to_sql and replace
    df_tx.to_sql("fact_transactions", engine, if_exists="replace", index=False)

    print("Loading fact_performance...")
    df_perf = pd.read_csv(project_root / "data" / "processed" / "clean_scheme_performance.csv")
    df_perf = df_perf[["amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio", "max_drawdown_pct"]]
    df_perf.to_sql("fact_performance", engine, if_exists="replace", index=False)

    print("Loading fact_aum...")
    # Map aum date to quarter roughly or just load
    df_aum = pd.read_csv(project_root / "data" / "processed" / "clean_aum_by_fund_house.csv")
    df_aum["quarter"] = pd.to_datetime(df_aum["date"]).dt.to_period("Q").astype(str)
    df_aum = df_aum[["fund_house", "quarter", "aum_crore"]]
    df_aum.to_sql("fact_aum", engine, if_exists="replace", index=False)
    
    print("Loading sip_inflows...")
    df_sip = pd.read_csv(project_root / "data" / "processed" / "clean_monthly_sip_inflows.csv")
    df_sip.to_sql("sip_inflows", engine, if_exists="replace", index=False)
    
    print("Database loading complete. Created bluestock_mf.db")

if __name__ == "__main__":
    load_data()
