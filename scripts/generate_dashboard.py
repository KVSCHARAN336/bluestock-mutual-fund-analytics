"""
Day 5: Bluestock Mutual Fund Analytics — Interactive Dashboard Generator
Generates 4-page dashboard with KPI cards, interactive charts, and exports to PNG + PDF.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# ── Paths ────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
CHARTS_DIR = os.path.join(REPORTS_DIR, 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Bluestock Theme ─────────────────────────────────────────────────────
COLORS = {
    'bg': '#0B1120',
    'card_bg': '#131B2E',
    'accent': '#3B82F6',
    'accent2': '#8B5CF6',
    'accent3': '#06B6D4',
    'accent4': '#10B981',
    'accent5': '#F59E0B',
    'text': '#E2E8F0',
    'subtext': '#94A3B8',
    'grid': '#1E293B',
}
PALETTE = [COLORS['accent'], COLORS['accent2'], COLORS['accent3'],
           COLORS['accent4'], COLORS['accent5'], '#EF4444', '#EC4899',
           '#14B8A6', '#A78BFA', '#FB923C']

def base_layout():
    return dict(
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Inter, Arial, sans-serif', color=COLORS['text'], size=12),
        margin=dict(l=60, r=30, t=60, b=50),
        xaxis=dict(gridcolor=COLORS['grid'], zerolinecolor=COLORS['grid']),
        yaxis=dict(gridcolor=COLORS['grid'], zerolinecolor=COLORS['grid']),
    )

# ── Load Data ────────────────────────────────────────────────────────────
def load_data():
    d = {}
    d['aum'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_aum_by_fund_house.csv'))
    d['aum']['date'] = pd.to_datetime(d['aum']['date'])
    d['bench'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_benchmark_indices.csv'))
    d['bench']['date'] = pd.to_datetime(d['bench']['date'])
    d['cat'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_category_inflows.csv'))
    d['cat']['month'] = pd.to_datetime(d['cat']['month'])
    d['master'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_fund_master.csv'))
    d['folio'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_industry_folio_count.csv'))
    d['folio']['month'] = pd.to_datetime(d['folio']['month'])
    d['sip'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_monthly_sip_inflows.csv'))
    d['sip']['month'] = pd.to_datetime(d['sip']['month'])
    d['nav'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_nav_history.csv'))
    d['nav']['date'] = pd.to_datetime(d['nav']['date'])
    d['perf'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_scheme_performance.csv'))
    d['txn'] = pd.read_csv(os.path.join(DATA_DIR, 'clean_transactions.csv'))
    d['txn']['transaction_date'] = pd.to_datetime(d['txn']['transaction_date'])
    d['scorecard'] = pd.read_csv(os.path.join(REPORTS_DIR, 'fund_scorecard.csv'))
    return d


# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — INDUSTRY OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
def page1_industry_overview(d):
    fig = make_subplots(
        rows=3, cols=4,
        row_heights=[0.18, 0.42, 0.40],
        specs=[
            [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
            [{'type': 'xy', 'colspan': 4}, None, None, None],
            [{'type': 'xy', 'colspan': 4}, None, None, None],
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.06,
        subplot_titles=['', '', '', '', 'Industry AUM Trend (2022–2025)', 'AUM by Fund House (Latest Quarter)']
    )

    # KPI Cards
    total_aum = d['aum'].groupby('date')['aum_crore'].sum().iloc[-1]
    latest_sip = d['sip']['sip_inflow_crore'].iloc[-1]
    latest_folio = d['folio']['total_folios_crore'].iloc[-1]
    total_schemes = d['master']['amfi_code'].nunique()

    kpis = [
        ('Total AUM', f"₹{total_aum/100000:.1f}L Cr", COLORS['accent']),
        ('SIP Inflows', f"₹{latest_sip:,.0f} Cr", COLORS['accent2']),
        ('Total Folios', f"{latest_folio:.2f} Cr", COLORS['accent3']),
        ('Schemes', f"{total_schemes:,}", COLORS['accent4']),
    ]
    for i, (title, val, color) in enumerate(kpis, 1):
        fig.add_trace(go.Indicator(
            mode='number',
            value=None,
            title=dict(text=f"<b>{title}</b>", font=dict(size=14, color=COLORS['subtext'])),
            number=dict(font=dict(size=28, color=color), valueformat='', suffix=''),
        ), row=1, col=i)
        # Use annotation to show formatted value
        fig.add_annotation(
            text=f"<b>{val}</b>",
            xref=f"x{i} domain" if i > 1 else "x domain",
            yref=f"y{i} domain" if i > 1 else "y domain",
            x=0.5, y=0.3,
            showarrow=False,
            font=dict(size=26, color=color),
        )

    # AUM Trend Line
    aum_trend = d['aum'].groupby('date')['aum_crore'].sum().reset_index()
    fig.add_trace(go.Scatter(
        x=aum_trend['date'], y=aum_trend['aum_crore'] / 100000,
        mode='lines+markers',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8, color=COLORS['accent']),
        name='Total AUM (Lakh Cr)',
        hovertemplate='%{x|%b %Y}<br>AUM: ₹%{y:.1f}L Cr<extra></extra>',
    ), row=2, col=1)
    fig.update_yaxes(title_text='AUM (₹ Lakh Cr)', row=2, col=1)

    # AUM by Fund House Bar
    latest_date = d['aum']['date'].max()
    latest_aum = d['aum'][d['aum']['date'] == latest_date].sort_values('aum_crore', ascending=True)
    fig.add_trace(go.Bar(
        y=latest_aum['fund_house'], x=latest_aum['aum_crore'],
        orientation='h',
        marker=dict(color=px.colors.sample_colorscale('Viridis', [i/len(latest_aum) for i in range(len(latest_aum))])),
        hovertemplate='%{y}<br>AUM: ₹%{x:,.0f} Cr<extra></extra>',
    ), row=3, col=1)
    fig.update_xaxes(title_text='AUM (₹ Crore)', row=3, col=1)

    fig.update_layout(
        **base_layout(),
        title=dict(text='<b>Bluestock MF Analytics - Industry Overview</b>', font=dict(size=20)),
        height=1000, width=1400, showlegend=False,
    )
    fig.write_image(os.path.join(CHARTS_DIR, 'page1_industry_overview.png'), scale=2)
    print('[OK] Page 1: Industry Overview exported.')
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — FUND PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════
def page2_fund_performance(d):
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.55, 0.45],
        specs=[
            [{'type': 'xy'}, {'type': 'xy'}],
            [{'type': 'xy', 'colspan': 2}, None],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
        subplot_titles=[
            'Return vs Risk (Bubble = AUM)',
            'Fund Scorecard — Top 15',
            'NAV Trend: Top 5 Funds vs NIFTY 100 (3yr)',
        ]
    )

    perf = d['perf'].copy()

    # Scatter: return vs risk
    fig.add_trace(go.Scatter(
        x=perf['return_3yr_pct'], y=perf['std_dev_ann_pct'],
        mode='markers',
        marker=dict(
            size=perf['aum_crore'].clip(upper=50000) / 1500 + 6,
            color=perf['sharpe_ratio'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Sharpe', x=0.46, len=0.45, y=0.78),
            line=dict(width=1, color='white'),
        ),
        text=perf['scheme_name'],
        hovertemplate='<b>%{text}</b><br>3yr Return: %{x:.1f}%<br>StdDev: %{y:.1f}%<br><extra></extra>',
    ), row=1, col=1)
    fig.update_xaxes(title_text='3yr Return (%)', row=1, col=1)
    fig.update_yaxes(title_text='Annualized StdDev (%)', row=1, col=1)

    # Scorecard Table as horizontal bar
    sc = d['scorecard'].head(15).sort_values('Composite_Score', ascending=True)
    short_names = [n[:30] + '…' if len(n) > 30 else n for n in sc['scheme_name']]
    fig.add_trace(go.Bar(
        y=short_names,
        x=sc['Composite_Score'],
        orientation='h',
        marker=dict(
            color=sc['Composite_Score'],
            colorscale=[[0, COLORS['accent2']], [1, COLORS['accent4']]],
        ),
        text=[f"{v:.0f}" for v in sc['Composite_Score']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>',
    ), row=1, col=2)
    fig.update_xaxes(title_text='Composite Score (0-100)', row=1, col=2)

    # NAV Trend: top 5 vs benchmark
    amfi_to_name = d['master'].set_index('amfi_code')['scheme_name'].to_dict()
    top5 = d['scorecard'].head(5)['scheme_name'].tolist()
    top5_amfi = [k for k, v in amfi_to_name.items() if v in top5]

    nav_df = d['nav'][d['nav']['amfi_code'].isin(top5_amfi)].copy()
    end_date = nav_df['date'].max()
    start_date = end_date - pd.DateOffset(years=3)
    nav_df = nav_df[nav_df['date'] >= start_date]

    for i, amfi in enumerate(top5_amfi):
        fund_nav = nav_df[nav_df['amfi_code'] == amfi].sort_values('date')
        if len(fund_nav) == 0:
            continue
        normalized = fund_nav['nav'] / fund_nav['nav'].iloc[0] * 100
        name = amfi_to_name.get(amfi, str(amfi))
        fig.add_trace(go.Scatter(
            x=fund_nav['date'], y=normalized,
            mode='lines', name=name[:25],
            line=dict(color=PALETTE[i], width=2),
            hovertemplate='%{x|%b %Y}<br>Value: %{y:.1f}<extra></extra>',
        ), row=2, col=1)

    # Add NIFTY100 benchmark
    nifty = d['bench'][d['bench']['index_name'] == 'NIFTY100'].copy()
    nifty = nifty[nifty['date'] >= start_date].sort_values('date')
    if len(nifty) > 0:
        nifty_norm = nifty['close_value'] / nifty['close_value'].iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=nifty['date'], y=nifty_norm,
            mode='lines', name='NIFTY 100',
            line=dict(color='white', width=2, dash='dash'),
        ), row=2, col=1)

    fig.update_yaxes(title_text='Normalized Value (Base=100)', row=2, col=1)

    fig.update_layout(
        **base_layout(),
        title=dict(text='<b>Fund Performance Dashboard</b>', font=dict(size=20)),
        height=1000, width=1400,
        legend=dict(x=0.55, y=0.42, bgcolor='rgba(0,0,0,0.3)', font=dict(size=10)),
    )
    fig.write_image(os.path.join(CHARTS_DIR, 'page2_fund_performance.png'), scale=2)
    print('[OK] Page 2: Fund Performance exported.')
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — INVESTOR ANALYTICS
# ══════════════════════════════════════════════════════════════════════════
def page3_investor_analytics(d):
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{'type': 'xy'}, {'type': 'domain'}],
            [{'type': 'xy'}, {'type': 'xy'}],
        ],
        vertical_spacing=0.14,
        horizontal_spacing=0.10,
        subplot_titles=[
            'Transaction Amount by State (Top 10)',
            'SIP / Lumpsum / Redemption Split',
            'Avg SIP Amount by Age Group',
            'Monthly Transaction Volume',
        ]
    )

    txn = d['txn'].copy()

    # Bar: transaction amount by state
    state_amt = txn.groupby('state')['amount_inr'].sum().nlargest(10).sort_values(ascending=True)
    fig.add_trace(go.Bar(
        y=state_amt.index, x=state_amt.values / 1e7,
        orientation='h',
        marker=dict(color=PALETTE[:len(state_amt)]),
        hovertemplate='%{y}<br>₹%{x:.0f} Cr<extra></extra>',
    ), row=1, col=1)
    fig.update_xaxes(title_text='Amount (₹ Cr)', row=1, col=1)

    # Donut: transaction type split
    type_split = txn.groupby('transaction_type')['amount_inr'].sum()
    fig.add_trace(go.Pie(
        labels=type_split.index, values=type_split.values,
        hole=0.5,
        marker=dict(colors=[COLORS['accent'], COLORS['accent2'], COLORS['accent5']]),
        textinfo='label+percent',
        textfont=dict(size=11),
        hovertemplate='%{label}<br>₹%{value:,.0f}<extra></extra>',
    ), row=1, col=2)

    # Bar: avg SIP amount by age group
    sip_txn = txn[txn['transaction_type'] == 'SIP']
    age_sip = sip_txn.groupby('age_group')['amount_inr'].mean().sort_values(ascending=True)
    fig.add_trace(go.Bar(
        y=age_sip.index, x=age_sip.values,
        orientation='h',
        marker=dict(color=[PALETTE[i % len(PALETTE)] for i in range(len(age_sip))]),
        hovertemplate='%{y}<br>Avg SIP: ₹%{x:,.0f}<extra></extra>',
    ), row=2, col=1)
    fig.update_xaxes(title_text='Avg Amount (₹)', row=2, col=1)

    # Line: monthly transaction volume
    txn['month'] = txn['transaction_date'].dt.to_period('M').dt.to_timestamp()
    monthly_vol = txn.groupby('month').size().reset_index(name='count')
    fig.add_trace(go.Scatter(
        x=monthly_vol['month'], y=monthly_vol['count'],
        mode='lines+markers',
        line=dict(color=COLORS['accent3'], width=2),
        marker=dict(size=5),
        hovertemplate='%{x|%b %Y}<br>Transactions: %{y:,}<extra></extra>',
    ), row=2, col=2)
    fig.update_yaxes(title_text='# Transactions', row=2, col=2)

    fig.update_layout(
        **base_layout(),
        title=dict(text='<b>Investor Analytics</b>', font=dict(size=20)),
        height=1000, width=1400, showlegend=False,
    )
    fig.write_image(os.path.join(CHARTS_DIR, 'page3_investor_analytics.png'), scale=2)
    print('[OK] Page 3: Investor Analytics exported.')
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIP & MARKET TRENDS
# ══════════════════════════════════════════════════════════════════════════
def page4_sip_market_trends(d):
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.55, 0.45],
        specs=[
            [{'type': 'xy', 'secondary_y': True, 'colspan': 2}, None],
            [{'type': 'xy'}, {'type': 'xy'}],
        ],
        vertical_spacing=0.14,
        horizontal_spacing=0.10,
        subplot_titles=[
            'SIP Inflow (Bar) vs Nifty 50 (Line) — 2022–2025',
            'Category Inflow Heatmap',
            'Top 5 Categories by Net Inflow (FY25)',
        ]
    )

    sip = d['sip'].copy()
    nifty50 = d['bench'][d['bench']['index_name'] == 'NIFTY50'].copy().sort_values('date')
    # Resample nifty to monthly
    nifty50.set_index('date', inplace=True)
    nifty50_monthly = nifty50['close_value'].resample('MS').last().reset_index()

    # Dual axis: SIP bar + Nifty line
    fig.add_trace(go.Bar(
        x=sip['month'], y=sip['sip_inflow_crore'],
        name='SIP Inflow (₹ Cr)',
        marker=dict(color=COLORS['accent'], opacity=0.8),
        hovertemplate='%{x|%b %Y}<br>SIP: ₹%{y:,.0f} Cr<extra></extra>',
    ), row=1, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(
        x=nifty50_monthly['date'], y=nifty50_monthly['close_value'],
        name='Nifty 50',
        mode='lines',
        line=dict(color=COLORS['accent5'], width=2),
        hovertemplate='%{x|%b %Y}<br>Nifty 50: %{y:,.0f}<extra></extra>',
    ), row=1, col=1, secondary_y=True)

    fig.update_yaxes(title_text='SIP Inflow (₹ Cr)', row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text='Nifty 50 Close', row=1, col=1, secondary_y=True)

    # Category Inflow Heatmap
    cat = d['cat'].copy()
    cat['month_str'] = cat['month'].dt.strftime('%Y-%m')
    pivot = cat.pivot_table(index='category', columns='month_str', values='net_inflow_crore', aggfunc='sum')
    pivot = pivot.fillna(0)

    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale='RdYlGn',
        hovertemplate='Category: %{y}<br>Month: %{x}<br>Inflow: ₹%{z:,.0f} Cr<extra></extra>',
        colorbar=dict(title='₹ Cr', x=0.46, len=0.4, y=0.18),
    ), row=2, col=1)

    # Top 5 categories by net inflow FY25 (Apr 2024 – Mar 2025)
    fy25 = cat[(cat['month'] >= '2024-04-01') & (cat['month'] <= '2025-03-31')]
    top_cat = fy25.groupby('category')['net_inflow_crore'].sum().nlargest(5).sort_values(ascending=True)
    fig.add_trace(go.Bar(
        y=top_cat.index, x=top_cat.values,
        orientation='h',
        marker=dict(color=[PALETTE[i] for i in range(len(top_cat))]),
        hovertemplate='%{y}<br>Net Inflow: ₹%{x:,.0f} Cr<extra></extra>',
    ), row=2, col=2)
    fig.update_xaxes(title_text='Net Inflow (₹ Cr)', row=2, col=2)

    fig.update_layout(
        **base_layout(),
        title=dict(text='<b>SIP & Market Trends</b>', font=dict(size=20)),
        height=1000, width=1400,
        legend=dict(x=0.7, y=0.95, bgcolor='rgba(0,0,0,0.3)'),
    )
    fig.write_image(os.path.join(CHARTS_DIR, 'page4_sip_market_trends.png'), scale=2)
    print('[OK] Page 4: SIP & Market Trends exported.')
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PDF EXPORT
# ══════════════════════════════════════════════════════════════════════════
def export_pdf():
    from fpdf import FPDF
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pages = [
        'page1_industry_overview.png',
        'page2_fund_performance.png',
        'page3_investor_analytics.png',
        'page4_sip_market_trends.png',
    ]
    for p in pages:
        path = os.path.join(CHARTS_DIR, p)
        if os.path.exists(path):
            pdf.add_page()
            pdf.image(path, x=5, y=5, w=287)
    pdf.output(os.path.join(REPORTS_DIR, 'Dashboard.pdf'))
    print('[OK] Dashboard.pdf exported.')


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Loading data...')
    data = load_data()
    print('Generating Page 1...')
    page1_industry_overview(data)
    print('Generating Page 2...')
    page2_fund_performance(data)
    print('Generating Page 3...')
    page3_investor_analytics(data)
    print('Generating Page 4...')
    page4_sip_market_trends(data)
    print('Generating PDF...')
    export_pdf()
    print('\nAll dashboard pages and PDF generated successfully!')
