import pandas as pd
import os

def clean_data():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    print("Cleaning nav_history...")
    df_nav = pd.read_csv(f"{raw_dir}/02_nav_history.csv")
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])
    df_nav = df_nav.drop_duplicates()
    df_nav["nav"] = df_nav.groupby("amfi_code")["nav"].ffill()
    invalid_nav = df_nav[df_nav["nav"] <= 0]
    print("Invalid NAV Records:", len(invalid_nav))
    df_nav.to_csv(f"{processed_dir}/clean_nav_history.csv", index=False)
    
    print("Cleaning investor_transactions...")
    df_tx = pd.read_csv(f"{raw_dir}/08_investor_transactions.csv")
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    mapping = {
        "sip": "SIP",
        "SIP": "SIP",
        "lumpsum": "Lumpsum",
        "Lumpsum": "Lumpsum",
        "redemption": "Redemption",
        "Redemption": "Redemption"
    }
    df_tx["transaction_type"] = df_tx["transaction_type"].astype(str).str.strip().map(mapping)
    df_tx = df_tx[df_tx["amount_inr"] > 0]
    valid_kyc = ["Verified", "Pending"]
    invalid_kyc = df_tx[~df_tx["kyc_status"].isin(valid_kyc)]
    print("Invalid KYC:", len(invalid_kyc))
    df_tx.to_csv(f"{processed_dir}/clean_transactions.csv", index=False)
    
    print("Cleaning scheme_performance...")
    df_perf = pd.read_csv(f"{raw_dir}/07_scheme_performance.csv")
    return_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio"
    ]
    for col in return_cols:
        df_perf[col] = pd.to_numeric(df_perf[col], errors="coerce")
    
    anomalies = df_perf[(df_perf["expense_ratio_pct"] < 0.1) | (df_perf["expense_ratio_pct"] > 2.5)]
    print("Expense Ratio Anomalies:")
    print(anomalies[["scheme_name", "expense_ratio_pct"]])
    df_perf.to_csv(f"{processed_dir}/clean_scheme_performance.csv", index=False)
    
    # Process the remaining 7 datasets to meet the "10 cleaned CSVs" deliverable
    print("Cleaning the remaining datasets...")
    remaining_files = {
        "01_fund_master.csv": "clean_fund_master.csv",
        "03_aum_by_fund_house.csv": "clean_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv": "clean_monthly_sip_inflows.csv",
        "05_category_inflows.csv": "clean_category_inflows.csv",
        "06_industry_folio_count.csv": "clean_industry_folio_count.csv",
        "09_portfolio_holdings - 09_portfolio_holdings.csv": "clean_portfolio_holdings.csv",
        "10_benchmark_indices - 10_benchmark_indices.csv": "clean_benchmark_indices.csv"
    }
    
    for raw_name, clean_name in remaining_files.items():
        df = pd.read_csv(f"{raw_dir}/{raw_name}")
        # Basic cleaning: drop complete duplicates
        df = df.drop_duplicates()
        df.to_csv(f"{processed_dir}/{clean_name}", index=False)
        print(f"Saved {clean_name}")

if __name__ == "__main__":
    clean_data()
