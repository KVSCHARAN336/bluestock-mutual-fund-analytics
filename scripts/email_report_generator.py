"""
BlueStock MF Capstone — Automated HTML Email Report Generator
=============================================================
Fulfills Bonus Challenge B5.
Generates a beautifully formatted, premium-styled HTML performance report
from the SQLite database metrics. Saves it as reports/weekly_performance_summary.html.

Usage:
    python scripts/email_report_generator.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("  Bonus B5: Automated Weekly HTML Email Report Generator")
print("=" * 60)

if not DB_PATH.exists():
    print(f"Error: SQLite database not found at {DB_PATH}. Run scripts/etl_pipeline.py first.")
    sys.exit(1)

# Connect to database and fetch summary stats
conn = sqlite3.connect(DB_PATH)

# Query 1: Top 5 Funds by Sharpe Ratio
top_funds_query = """
    SELECT f.scheme_name, f.category, p.sharpe_ratio, p.return_1yr_pct, p.max_drawdown_pct
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    ORDER BY p.sharpe_ratio DESC
    LIMIT 5
"""
top_funds_df = pd.read_sql(top_funds_query, conn)

# Query 2: Risk Class Average returns
risk_avg_query = """
    SELECT f.risk_category, AVG(p.return_1yr_pct) as avg_1yr_return, AVG(p.sharpe_ratio) as avg_sharpe
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    GROUP BY f.risk_category
    ORDER BY avg_1yr_return DESC
"""
risk_avg_df = pd.read_sql(risk_avg_query, conn)

# Query 3: Latest AUM Market share
aum_query = """
    SELECT fund_house, aum_crore
    FROM fact_aum
    WHERE quarter = (SELECT MAX(quarter) FROM fact_aum)
    ORDER BY aum_crore DESC
    LIMIT 5
"""
aum_df = pd.read_sql(aum_query, conn)

conn.close()

# Generate beautiful HTML using embedded styling
now_str = datetime.now().strftime("%B %d, %Y")

html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BlueStock MF Weekly Analytics Summary</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0B1120;
            color: #E2E8F0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #131B2E;
            border-radius: 12px;
            border: 1px solid #1E293B;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }}
        .header {{
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: 0.5px;
        }}
        .header p {{
            margin: 8px 0 0 0;
            font-size: 14px;
            color: #93C5FD;
        }}
        .content {{
            padding: 30px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #3B82F6;
            margin-top: 0;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #1E293B;
            padding-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }}
        th {{
            text-align: left;
            padding: 10px;
            font-size: 12px;
            font-weight: 600;
            color: #94A3B8;
            border-bottom: 1px solid #1E293B;
            text-transform: uppercase;
        }}
        td {{
            padding: 12px 10px;
            font-size: 13px;
            color: #E2E8F0;
            border-bottom: 1px solid #1E293B;
        }}
        tr:hover td {{
            background-color: #1E293B;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-positive {{
            background-color: rgba(16, 185, 129, 0.15);
            color: #10B981;
        }}
        .badge-negative {{
            background-color: rgba(239, 68, 68, 0.15);
            color: #EF4444;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }}
        .card {{
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 15px;
        }}
        .card-value {{
            font-size: 20px;
            font-weight: 700;
            color: #10B981;
            margin-bottom: 5px;
        }}
        .card-label {{
            font-size: 12px;
            color: #94A3B8;
            text-transform: uppercase;
        }}
        .footer {{
            background-color: #0F172A;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #1E293B;
        }}
        .footer p {{
            margin: 0;
            font-size: 11px;
            color: #64748B;
        }}
        .footer a {{
            color: #3B82F6;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BLUESTOCK MUTUAL FUND ANALYTICS</h1>
            <p>Weekly Market & Performance Summary &bull; {now_str}</p>
        </div>
        
        <div class="content">
            <div class="section-title">🏆 Top 5 Schemes by Sharpe Ratio</div>
            <table>
                <thead>
                    <tr>
                        <th>Scheme</th>
                        <th>Category</th>
                        <th>Sharpe</th>
                        <th>1-Yr Return</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in top_funds_df.iterrows():
    name = row['scheme_name']
    short_name = name[:35] + "..." if len(name) > 38 else name
    html_content += f"""
                    <tr>
                        <td><strong>{short_name}</strong></td>
                        <td>{row['category']}</td>
                        <td><span class="badge badge-positive">{row['sharpe_ratio']:.2f}</span></td>
                        <td>{row['return_1yr_pct']:.2f}%</td>
                    </tr>"""

html_content += """
                </tbody>
            </table>

            <div class="section-title">📊 Asset/Risk Category Benchmarks</div>
            <table>
                <thead>
                    <tr>
                        <th>Risk Tier</th>
                        <th>Avg 1-Yr Return</th>
                        <th>Avg Sharpe</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in risk_avg_df.iterrows():
    html_content += f"""
                    <tr>
                        <td><strong>{row['risk_category']}</strong></td>
                        <td>{row['avg_1yr_return']:.2f}%</td>
                        <td>{row['avg_sharpe']:.2f}</td>
                    </tr>"""

html_content += """
                </tbody>
            </table>

            <div class="section-title">🏛️ Top AMC AUM Rankings</div>
            <table>
                <thead>
                    <tr>
                        <th>Fund House (AMC)</th>
                        <th>Latest AUM (₹ Crore)</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in aum_df.iterrows():
    html_content += f"""
                    <tr>
                        <td>{row['fund_house']}</td>
                        <td><strong>₹{row['aum_crore']:,.2f} Cr</strong></td>
                    </tr>"""

html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>This is an automated report generated by the BlueStock MF Analytics Pipeline.</p>
            <p>Configure subscription settings in your <a href="http://localhost:8501">Dashboard</a></p>
            <p style="margin-top: 10px;">&copy; 2026 BlueStock Fintech. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

# Write HTML file
output_path = REPORTS_DIR / "weekly_performance_summary.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n  Success! Beautiful HTML email report created at:")
print(f"  {output_path}")
print("=" * 60)
conn.close()
