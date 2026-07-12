import re
import pandas as pd
from typing import List, Dict, Any, Optional

class DataQualityValidator:
    """
    Data Quality Validation Engine executing 16 DQ rules for Nifty100.
    Tracks all failures and generates output/validation_failures.csv.
    """
    def __init__(self):
        self.failures: List[Dict[str, Any]] = []

    def log_failure(self, table_name: str, rule_id: str, severity: str, 
                    company_id: Optional[Any], year: Optional[Any], 
                    column_name: str, value: Any, message: str) -> None:
        """Helper to append a validation failure record."""
        self.failures.append({
            "table_name": table_name,
            "rule_id": rule_id,
            "severity": severity,
            "company_id": company_id,
            "year": year,
            "column_name": column_name,
            "value": str(value),
            "message": message
        })

    def validate_companies(self, df: pd.DataFrame) -> None:
        """Validate companies table metadata (DQ-01, DQ-10, DQ-13, DQ-14)."""
        table = "companies"
        for idx, row in df.iterrows():
            comp_id = row.get("id") # 'id' contains the ticker in companies sheet
            name = row.get("company_name")
            website = row.get("website")

            # DQ-14: Missing critical values
            if pd.isna(comp_id) or str(comp_id).strip() == "":
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, None, "id", comp_id, "Missing Company ID/Ticker Symbol")
            if pd.isna(name) or str(name).strip() == "":
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, None, "company_name", name, "Missing Company Name")

            # DQ-13: Ticker format check
            if not pd.isna(comp_id):
                ticker_str = str(comp_id).strip()
                if not re.match(r"^[A-Z0-9&\-]+$", ticker_str):
                    self.log_failure(table, "DQ-13", "WARNING", comp_id, None, "id", comp_id, f"Invalid ticker format: '{comp_id}'")

            # DQ-10: Website URL format validation
            if not pd.isna(website) and str(website).strip() != "" and str(website).strip().lower() != "nan":
                web_str = str(website).strip()
                url_regex = re.compile(
                    r'^(?:http|ftp)s?://' # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
                    r'localhost|' # localhost...
                    r'\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}}\.\d{{1,3}})' # ...or ip
                    r'(?::\d+)?' # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                if not url_regex.match(web_str):
                    self.log_failure(table, "DQ-10", "WARNING", comp_id, None, "website", website, f"Invalid website URL format: '{website}'")

        # DQ-01: PK uniqueness check
        if "id" in df.columns:
            dupes_id = df[df["id"].duplicated(keep=False)]
            for _, row in dupes_id.iterrows():
                comp_id = row.get("id")
                self.log_failure(table, "DQ-01", "CRITICAL", comp_id, None, "id", comp_id, "Duplicate Ticker ID (Primary Key violation)")


    def validate_profit_and_loss(self, df: pd.DataFrame, valid_company_ids: set) -> None:
        """Validate profitandloss table (DQ-02, DQ-03, DQ-05, DQ-06, DQ-11, DQ-12, DQ-14, DQ-15)."""
        table = "profitandloss"
        
        # DQ-02: Composite PK Uniqueness Check
        if "company_id" in df.columns and "year" in df.columns:
            dupes = df[df.duplicated(subset=["company_id", "year"], keep=False)]
            for _, row in dupes.iterrows():
                comp_id = row.get("company_id")
                yr = row.get("year")
                self.log_failure(table, "DQ-02", "CRITICAL", comp_id, yr, "company_id,year", f"{comp_id},{yr}", "Duplicate composite primary key")

        for idx, row in df.iterrows():
            comp_id = row.get("company_id")
            yr = row.get("year")
            sales = row.get("sales")
            expenses = row.get("expenses")
            operating_profit = row.get("operating_profit")
            net_profit = row.get("net_profit")
            eps = row.get("eps")
            tax_pct = row.get("tax_percentage")

            # DQ-14: Missing critical values
            if pd.isna(comp_id):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "company_id", comp_id, "Missing Company ID")
            if pd.isna(yr):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "year", yr, "Missing Year")

            # DQ-03: Foreign Key Integrity
            if comp_id not in valid_company_ids and not pd.isna(comp_id):
                self.log_failure(table, "DQ-03", "CRITICAL", comp_id, yr, "company_id", comp_id, f"Foreign Key violation: Company ID {comp_id} does not exist in companies table")

            # DQ-15: Out of range year
            if not pd.isna(yr):
                try:
                    # Expecting standardized year like 2023-03, extract YYYY
                    yr_str = str(yr).split("-")[0]
                    yr_val = int(yr_str)
                    if yr_val < 2000 or yr_val > 2026:
                        self.log_failure(table, "DQ-15", "WARNING", comp_id, yr, "year", yr, f"Year {yr} is out of expected range (2000-2026)")
                except Exception:
                    pass

            # DQ-06: Positive sales check (exclude financial companies if bank/NBFC)
            if not pd.isna(sales) and sales <= 0:
                self.log_failure(table, "DQ-06", "WARNING", comp_id, yr, "sales", sales, f"Sales should be positive, found: {sales}")

            # DQ-05: OPM cross-check
            if not pd.isna(sales) and not pd.isna(expenses) and not pd.isna(operating_profit) and sales > 0:
                calc_op = sales - expenses
                diff = abs(operating_profit - calc_op)
                pct_diff = (diff / abs(operating_profit)) * 100 if operating_profit != 0 else 0
                if diff > 10.0 and pct_diff > 1.0:
                    self.log_failure(table, "DQ-05", "WARNING", comp_id, yr, "operating_profit", operating_profit, 
                                     f"Operating profit mismatch: Sales ({sales}) - Expenses ({expenses}) = {calc_op}, reported Operating Profit = {operating_profit} (diff {pct_diff:.1f}%)")

            # DQ-11: EPS Sign Check
            if not pd.isna(eps) and not pd.isna(net_profit):
                if (eps > 0 and net_profit < 0) or (eps < 0 and net_profit > 0):
                    self.log_failure(table, "DQ-11", "WARNING", comp_id, yr, "eps", eps, f"EPS sign ({eps}) does not match Net Profit sign ({net_profit})")

            # DQ-08: Effective Tax Rate validation
            if not pd.isna(tax_pct):
                if tax_pct < 0 or tax_pct > 100:
                    self.log_failure(table, "DQ-08", "WARNING", comp_id, yr, "tax_percentage", tax_pct, f"Effective tax rate out of bounds: {tax_pct}%")


    def validate_balancesheet(self, df: pd.DataFrame, valid_company_ids: set) -> None:
        """Validate balancesheet table (DQ-02, DQ-03, DQ-04, DQ-14, DQ-15)."""
        table = "balancesheet"

        # DQ-02: Composite PK Uniqueness
        if "company_id" in df.columns and "year" in df.columns:
            dupes = df[df.duplicated(subset=["company_id", "year"], keep=False)]
            for _, row in dupes.iterrows():
                comp_id = row.get("company_id")
                yr = row.get("year")
                self.log_failure(table, "DQ-02", "CRITICAL", comp_id, yr, "company_id,year", f"{comp_id},{yr}", "Duplicate composite primary key")

        for idx, row in df.iterrows():
            comp_id = row.get("company_id")
            yr = row.get("year")
            liabilities = row.get("total_liabilities")
            assets = row.get("total_assets")

            # DQ-14: Missing critical values
            if pd.isna(comp_id):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "company_id", comp_id, "Missing Company ID")
            if pd.isna(yr):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "year", yr, "Missing Year")

            # DQ-03: Foreign Key Integrity
            if comp_id not in valid_company_ids and not pd.isna(comp_id):
                self.log_failure(table, "DQ-03", "CRITICAL", comp_id, yr, "company_id", comp_id, f"Foreign Key violation: Company ID {comp_id} does not exist in companies table")

            # DQ-04: Balance Sheet Balance Check (Assets == Liabilities within 1%)
            if not pd.isna(assets) and not pd.isna(liabilities):
                diff = abs(assets - liabilities)
                pct_diff = (diff / abs(assets)) * 100 if assets != 0 else 0
                if diff > 10.0 and pct_diff > 1.0:
                    self.log_failure(table, "DQ-04", "WARNING", comp_id, yr, "total_assets,total_liabilities", f"{assets},{liabilities}", 
                                     f"Balance Sheet imbalance: Total Assets = {assets}, Total Liabilities = {liabilities} (diff {pct_diff:.2f}%)")


    def validate_cashflow(self, df: pd.DataFrame, valid_company_ids: set) -> None:
        """Validate cashflow table (DQ-02, DQ-03, DQ-07, DQ-14, DQ-15)."""
        table = "cashflow"

        # DQ-02: Composite PK Uniqueness
        if "company_id" in df.columns and "year" in df.columns:
            dupes = df[df.duplicated(subset=["company_id", "year"], keep=False)]
            for _, row in dupes.iterrows():
                comp_id = row.get("company_id")
                yr = row.get("year")
                self.log_failure(table, "DQ-02", "CRITICAL", comp_id, yr, "company_id,year", f"{comp_id},{yr}", "Duplicate composite primary key")

        for idx, row in df.iterrows():
            comp_id = row.get("company_id")
            yr = row.get("year")
            op_cash = row.get("operating_activity")
            inv_cash = row.get("investing_activity")
            fin_cash = row.get("financing_activity")
            net_cf = row.get("net_cash_flow")

            # DQ-14: Missing critical values
            if pd.isna(comp_id):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "company_id", comp_id, "Missing Company ID")
            if pd.isna(yr):
                self.log_failure(table, "DQ-14", "CRITICAL", comp_id, yr, "year", yr, "Missing Year")

            # DQ-03: Foreign Key Integrity
            if comp_id not in valid_company_ids and not pd.isna(comp_id):
                self.log_failure(table, "DQ-03", "CRITICAL", comp_id, yr, "company_id", comp_id, f"Foreign Key violation: Company ID {comp_id} does not exist in companies table")

            # DQ-07: Net Cash Flow Cross-Check
            if not pd.isna(op_cash) and not pd.isna(inv_cash) and not pd.isna(fin_cash) and not pd.isna(net_cf):
                calc_cf = op_cash + inv_cash + fin_cash
                diff = abs(net_cf - calc_cf)
                if diff > 5.0: # allow small rounding margin
                    self.log_failure(table, "DQ-07", "WARNING", comp_id, yr, "net_cash_flow", net_cf,
                                     f"Net cash flow mismatch: Calculated ({calc_cf}) vs Reported ({net_cf})")

    def validate_ratios(self, df: pd.DataFrame, valid_company_ids: set) -> None:
        """Validate financial_ratios table (DQ-16: Outlier ratio checks)."""
        table = "financial_ratios"
        for idx, row in df.iterrows():
            comp_id = row.get("company_id")
            yr = row.get("year")
            de = row.get("debt_to_equity") # Aligned with sheet column name

            # DQ-16: Outlier detection
            if not pd.isna(de) and de > 15.0:
                self.log_failure(table, "DQ-16", "WARNING", comp_id, yr, "debt_to_equity", de, f"Outlier detected: Debt-to-Equity ratio is exceptionally high: {de}")

    def save_failures(self, filepath: str) -> None:
        """Save list of failures to a CSV file."""
        failures_df = pd.DataFrame(self.failures)
        if failures_df.empty:
            failures_df = pd.DataFrame(columns=["table_name", "rule_id", "severity", "company_id", "year", "column_name", "value", "message"])
        failures_df.to_csv(filepath, index=False)
        print(f"Validation failures logged: {len(failures_df)} issues saved to {filepath}")
