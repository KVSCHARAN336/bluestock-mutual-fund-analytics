"""
BlueStock MF Capstone — Interactive Streamlit Dashboard
========================================================
4-page interactive dashboard with slicers, KPI cards, and dynamic charts.
Alternative to Power BI (Bonus B2) — also fulfills D5 deliverable.

Usage:
    streamlit run dashboard/streamlit_app.py

Pages:
  1. Industry Overview — AUM growth, folio count, SIP trends
  2. Fund Performance — NAV trends, Sharpe comparison, benchmark overlay
  3. Investor Analytics — Demographics, transactions, cohort analysis
  4. SIP & Market Trends — SIP inflows, category flows, growth metrics
"""

import sys
import os
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BlueStock MF Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Theme & Styling
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stMetric { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border: 1px solid #334155; border-radius: 12px; padding: 16px; }
    .stMetric label { color: #94a3b8 !important; font-size: 0.85rem !important; }
    .stMetric [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.8rem !important; }
    .stMetric [data-testid="stMetricDelta"] { font-size: 0.9rem !important; }
    h1 { color: #e2e8f0 !important; }
    h2, h3 { color: #cbd5e1 !important; }
    .stSidebar { background: #1e293b !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e293b; border-radius: 8px; color: #94a3b8;
        padding: 8px 20px; border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important; border: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Data Loading (cached)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {}
    data['fund_master'] = pd.read_csv(RAW_DIR / "01_fund_master.csv")
    data['nav'] = pd.read_csv(RAW_DIR / "02_nav_history.csv")
    data['nav']['date'] = pd.to_datetime(data['nav']['date'])
    data['aum'] = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    data['aum']['date'] = pd.to_datetime(data['aum']['date'])
    data['sip'] = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    data['category'] = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
    data['folio'] = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv")
    data['perf'] = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
    data['tx'] = pd.read_csv(RAW_DIR / "08_investor_transactions.csv")
    data['tx']['transaction_date'] = pd.to_datetime(data['tx']['transaction_date'])
    data['holdings'] = pd.read_csv(RAW_DIR / "09_portfolio_holdings - 09_portfolio_holdings.csv")
    data['bench'] = pd.read_csv(RAW_DIR / "10_benchmark_indices - 10_benchmark_indices.csv")
    data['bench']['date'] = pd.to_datetime(data['bench']['date'])

    # Merge fund info
    data['perf_full'] = data['perf'].merge(
        data['fund_master'][['amfi_code', 'fund_house', 'scheme_name', 'category']],
        on='amfi_code', how='left', suffixes=('', '_master')
    )
    return data

data = load_data()

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — Global Filters
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("🔷 BlueStock MF")
st.sidebar.markdown("---")

# Fund house filter
all_houses = sorted(data['fund_master']['fund_house'].unique())
selected_houses = st.sidebar.multiselect(
    "📌 Fund House", all_houses, default=all_houses,
    help="Filter all pages by fund house"
)

# Category filter
all_categories = sorted(data['fund_master']['category'].unique())
selected_categories = st.sidebar.multiselect(
    "📂 Category", all_categories, default=all_categories,
    help="Filter by fund category"
)

# Risk filter
if 'risk_grade' in data['perf'].columns:
    all_risks = sorted(data['perf']['risk_grade'].dropna().unique())
    selected_risks = st.sidebar.multiselect(
        "⚠️ Risk Grade", all_risks, default=all_risks
    )
else:
    selected_risks = None

# Apply filters to fund master
filtered_funds = data['fund_master'][
    (data['fund_master']['fund_house'].isin(selected_houses)) &
    (data['fund_master']['category'].isin(selected_categories))
]
filtered_amfis = filtered_funds['amfi_code'].tolist()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered_amfis)} of {len(data['fund_master'])} schemes")

# ──────────────────────────────────────────────────────────────────────────────
# Title
# ──────────────────────────────────────────────────────────────────────────────
st.title("📊 BlueStock Mutual Fund Analytics Dashboard")

# ──────────────────────────────────────────────────────────────────────────────
# TABS — 4 Pages
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Industry Overview",
    "📈 Fund Performance",
    "👤 Investor Analytics",
    "💰 SIP & Market Trends"
])

# ======================================================================
# PAGE 1 — Industry Overview
# ======================================================================
with tab1:
    st.header("🏛️ Industry Overview")

    # KPI Cards
    aum_latest = data['aum'].groupby('fund_house')['aum_crore'].last().sum()
    total_folios = data['folio']['total_folios_crore'].iloc[-1] if 'total_folios_crore' in data['folio'].columns else data['folio'].iloc[-1, 1]
    total_schemes = len(data['fund_master'])
    total_amcs = data['fund_master']['fund_house'].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total AUM", f"₹{aum_latest/100:.1f} L Cr")
    c2.metric("Total Schemes", f"{total_schemes}")
    c3.metric("Fund Houses", f"{total_amcs}")
    c4.metric("Total Folios", f"{total_folios:.1f} Cr" if isinstance(total_folios, float) else str(total_folios))

    st.markdown("---")

    # AUM by Fund House
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("AUM by Fund House")
        aum_by_house = data['aum'][data['aum']['fund_house'].isin(selected_houses)]
        aum_latest_house = aum_by_house.sort_values('date').groupby('fund_house')['aum_crore'].last().sort_values(ascending=True)
        fig = px.bar(
            x=aum_latest_house.values, y=aum_latest_house.index,
            orientation='h', color=aum_latest_house.values,
            color_continuous_scale='Blues',
            labels={'x': 'AUM (₹ Crore)', 'y': 'Fund House'}
        )
        fig.update_layout(height=400, showlegend=False, coloraxis_showscale=False,
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("AUM Growth Over Time")
        aum_trend = data['aum'][data['aum']['fund_house'].isin(selected_houses)]
        aum_total = aum_trend.groupby('date')['aum_crore'].sum().reset_index()
        fig = px.area(aum_total, x='date', y='aum_crore',
                     labels={'date': 'Date', 'aum_crore': 'Total AUM (₹ Cr)'},
                     color_discrete_sequence=['#3b82f6'])
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    # Category distribution
    st.subheader("Schemes by Category")
    cat_counts = filtered_funds['category'].value_counts()
    fig = px.pie(values=cat_counts.values, names=cat_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4)
    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                     font=dict(color='#94a3b8'))
    st.plotly_chart(fig, use_container_width=True)


# ======================================================================
# PAGE 2 — Fund Performance
# ======================================================================
with tab2:
    st.header("📈 Fund Performance")

    # Date range slicer
    nav_filtered = data['nav'][data['nav']['amfi_code'].isin(filtered_amfis)]
    min_date = nav_filtered['date'].min().date()
    max_date = nav_filtered['date'].max().date()

    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with date_col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    nav_filtered = nav_filtered[
        (nav_filtered['date'] >= pd.Timestamp(start_date)) &
        (nav_filtered['date'] <= pd.Timestamp(end_date))
    ]

    st.markdown("---")

    # NAV Trend — select up to 5 funds
    st.subheader("NAV Trend Comparison")
    fund_names = filtered_funds.set_index('amfi_code')['scheme_name'].to_dict()
    available_funds = {v: k for k, v in fund_names.items() if k in nav_filtered['amfi_code'].unique()}
    selected_fund_names = st.multiselect(
        "Select Funds (max 5)", list(available_funds.keys()),
        default=list(available_funds.keys())[:3]
    )
    selected_fund_amfis = [available_funds[n] for n in selected_fund_names[:5]]

    if selected_fund_amfis:
        nav_plot = nav_filtered[nav_filtered['amfi_code'].isin(selected_fund_amfis)].copy()
        nav_plot['scheme'] = nav_plot['amfi_code'].map(fund_names)
        fig = px.line(nav_plot, x='date', y='nav', color='scheme',
                     labels={'date': 'Date', 'nav': 'NAV (₹)', 'scheme': 'Fund'},
                     color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'),
                         legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    # Sharpe vs Sortino scatter
    col1, col2 = st.columns(2)
    perf_f = data['perf_full'][data['perf_full']['amfi_code'].isin(filtered_amfis)]

    with col1:
        st.subheader("Sharpe vs Return (1yr)")
        fig = px.scatter(perf_f, x='sharpe_ratio', y='return_1yr_pct',
                        color='category', size='expense_ratio_pct',
                        hover_name='scheme_name',
                        labels={'sharpe_ratio': 'Sharpe Ratio', 'return_1yr_pct': '1-Year Return (%)'},
                        color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk-Return Matrix")
        if 'max_drawdown_pct' in perf_f.columns:
            fig = px.scatter(perf_f, x='max_drawdown_pct', y='return_3yr_pct',
                            color='category', hover_name='scheme_name',
                            labels={'max_drawdown_pct': 'Max Drawdown (%)', 'return_3yr_pct': '3-Year Return (%)'},
                            color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
            st.plotly_chart(fig, use_container_width=True)

    # Performance table
    st.subheader("📋 Fund Scorecard")
    display_cols = ['scheme_name', 'fund_house', 'category', 'sharpe_ratio',
                   'return_1yr_pct', 'return_3yr_pct', 'expense_ratio_pct']
    display_cols = [c for c in display_cols if c in perf_f.columns]
    st.dataframe(
        perf_f[display_cols].sort_values('sharpe_ratio', ascending=False).reset_index(drop=True),
        use_container_width=True, height=400
    )


# ======================================================================
# PAGE 3 — Investor Analytics
# ======================================================================
with tab3:
    st.header("👤 Investor Analytics")

    tx_f = data['tx'][data['tx']['amfi_code'].isin(filtered_amfis)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Investors", f"{tx_f['investor_id'].nunique():,}")
    c2.metric("Total Transactions", f"{len(tx_f):,}")
    c3.metric("Avg Transaction", f"₹{tx_f['amount_inr'].mean():,.0f}")
    c4.metric("Total Invested", f"₹{tx_f['amount_inr'].sum()/1e7:.1f} Cr")

    st.markdown("---")

    # Transaction type filter
    tx_types = st.multiselect(
        "Transaction Type", ['SIP', 'Lumpsum', 'Redemption'],
        default=['SIP', 'Lumpsum', 'Redemption']
    )
    tx_f = tx_f[tx_f['transaction_type'].isin(tx_types)]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Transactions Over Time")
        tx_monthly = tx_f.groupby(tx_f['transaction_date'].dt.to_period('M')).agg(
            count=('amount_inr', 'count'),
            total=('amount_inr', 'sum')
        ).reset_index()
        tx_monthly['transaction_date'] = tx_monthly['transaction_date'].astype(str)
        fig = px.bar(tx_monthly, x='transaction_date', y='count',
                    labels={'transaction_date': 'Month', 'count': 'Transactions'},
                    color_discrete_sequence=['#3b82f6'])
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Transaction Type Distribution")
        type_dist = tx_f['transaction_type'].value_counts()
        fig = px.pie(values=type_dist.values, names=type_dist.index,
                    color_discrete_sequence=['#3b82f6', '#8b5cf6', '#ef4444'],
                    hole=0.45)
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    # Demographics
    col3, col4 = st.columns(2)

    with col3:
        if 'gender' in tx_f.columns:
            st.subheader("Gender Distribution")
            gender = tx_f.drop_duplicates('investor_id')['gender'].value_counts()
            fig = px.pie(values=gender.values, names=gender.index,
                        color_discrete_sequence=['#3b82f6', '#ec4899', '#a855f7'],
                        hole=0.4)
            fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='#94a3b8'))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        if 'state' in tx_f.columns:
            st.subheader("Top 10 States")
            state_counts = tx_f.drop_duplicates('investor_id')['state'].value_counts().head(10)
            fig = px.bar(x=state_counts.values, y=state_counts.index,
                        orientation='h', color=state_counts.values,
                        color_continuous_scale='Viridis',
                        labels={'x': 'Investors', 'y': 'State'})
            fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(color='#94a3b8'))
            st.plotly_chart(fig, use_container_width=True)

    # SIP Amount Distribution
    st.subheader("SIP Amount Distribution")
    sip_tx = tx_f[tx_f['transaction_type'] == 'SIP']
    if len(sip_tx) > 0:
        fig = px.histogram(sip_tx, x='amount_inr', nbins=30,
                          labels={'amount_inr': 'SIP Amount (₹)', 'count': 'Frequency'},
                          color_discrete_sequence=['#8b5cf6'])
        fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)


# ======================================================================
# PAGE 4 — SIP & Market Trends
# ======================================================================
with tab4:
    st.header("💰 SIP & Market Trends")

    # SIP KPIs
    sip_df = data['sip']
    if len(sip_df) > 0:
        c1, c2, c3, c4 = st.columns(4)
        latest = sip_df.iloc[-1]
        c1.metric("Latest SIP Inflow", f"₹{latest.get('sip_inflow_crore', 0):,.0f} Cr")
        c2.metric("Active SIP Accounts", f"{latest.get('active_sip_accounts_crore', 0):.1f} Cr")
        c3.metric("New SIPs (Monthly)", f"{latest.get('new_sip_accounts_lakh', 0):.1f} Lakh")
        c4.metric("YoY Growth", f"{latest.get('yoy_growth_pct', 0):.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("SIP Monthly Inflows")
        fig = px.bar(sip_df, x='month', y='sip_inflow_crore',
                    labels={'month': 'Month', 'sip_inflow_crore': 'SIP Inflow (₹ Crore)'},
                    color='sip_inflow_crore', color_continuous_scale='Blues')
        fig.update_layout(height=400, showlegend=False, coloraxis_showscale=False,
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("SIP YoY Growth Rate")
        if 'yoy_growth_pct' in sip_df.columns:
            fig = px.line(sip_df, x='month', y='yoy_growth_pct',
                         labels={'month': 'Month', 'yoy_growth_pct': 'YoY Growth (%)'},
                         markers=True, color_discrete_sequence=['#10b981'])
            fig.add_hline(y=0, line_dash='dash', line_color='#ef4444', opacity=0.5)
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
            st.plotly_chart(fig, use_container_width=True)

    # Category-wise inflows
    st.subheader("Category-wise Net Inflows")
    time_granularity = st.selectbox("Time Granularity", ["Monthly", "Quarterly"], index=0)
    cat_df = data['category']
    if 'month' in cat_df.columns:
        fig = px.bar(cat_df, x='month', y='net_inflow_crore', color='category',
                    labels={'month': 'Month', 'net_inflow_crore': 'Net Inflow (₹ Cr)'},
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    barmode='relative')
        fig.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'),
                         legend=dict(orientation='h', y=-0.3))
        st.plotly_chart(fig, use_container_width=True)

    # Benchmark comparison
    st.subheader("Benchmark Index Performance")
    bench = data['bench']
    bench_cols = [c for c in bench.columns if c != 'date']
    selected_idx = st.multiselect("Select Index", bench_cols, default=bench_cols[:2])
    if selected_idx:
        bench_norm = bench[['date'] + selected_idx].copy()
        for col in selected_idx:
            bench_norm[col] = bench_norm[col] / bench_norm[col].iloc[0] * 100
        bench_melt = bench_norm.melt(id_vars='date', var_name='Index', value_name='Normalized (Base=100)')
        fig = px.line(bench_melt, x='date', y='Normalized (Base=100)', color='Index',
                     color_discrete_sequence=['#3b82f6', '#ef4444', '#10b981'])
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)',
                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.85rem;'>"
    "📊 BlueStock MF Analytics Dashboard | "
    "Data: AMFI India | "
    "Built with Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True
)
