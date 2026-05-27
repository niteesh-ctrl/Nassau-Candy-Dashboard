import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from PIL import Image
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS - Beautiful Background & Styling
# =========================================================
st.markdown("""
<style>

/* App background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        135deg, #f5f7fa 0%, #e8ecf1 100%);
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg, #1a1a2e 0%,
        #16213e 50%, #0f3460 100%);
}

/* Sidebar text */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #e0e0e0 !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFD700 !important;
}

/* KPI metric cards */
div[data-testid="metric-container"] {
    background: white;
    border-left: 5px solid #e94560;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Metric label */
div[data-testid="metric-container"] label {
    color: #555 !important;
    font-size: 0.85rem !important;
}

/* Metric value */
div[data-testid="metric-container"]
[data-testid="stMetricValue"] {
    color: #1a1a2e !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* Chart container */
.stPlotlyChart {
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    background: white;
    padding: 8px;
}

/* Dataframe */
.stDataFrame {
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Divider */
hr {
    border-color: #FFD700 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_final.csv")
    df['Order Date'] = pd.to_datetime(
        df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(
        df['Ship Date'], errors='coerce')
    for col in [
        'Gross Margin%', 'Sales',
        'Gross Profit', 'Units',
        'Cost', 'Shipping Days'
    ]:
        df[col] = pd.to_numeric(
            df[col], errors='coerce')
    return df

df = load_data()


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("""
<div style='text-align:center;
     padding:15px 10px 5px 10px;'>
    <div style='font-size:3rem;'>🍬</div>
    <h2 style='color:#FFD700 !important;
               font-size:1.4rem;
               margin:5px 0;'>
        Nassau Candy
    </h2>
    <p style='color:#aaa !important;
              font-size:0.8rem; margin:0;'>
        Profitability Analytics Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ---- USER CAPABILITY 1: Date Range Selector ----
st.sidebar.markdown(
    "### 📅 Date Range Selector")
date_min = df['Order Date'].dropna().min().date()
date_max = df['Order Date'].dropna().max().date()
date_range = st.sidebar.date_input(
    "Select Order Date Range:",
    value=[date_min, date_max],
    min_value=date_min,
    max_value=date_max
)
st.sidebar.markdown("---")

# ---- USER CAPABILITY 2: Division Filter ----
st.sidebar.markdown(
    "### 🏢 Division Filter")
all_divisions = sorted(
    df['Division'].dropna().unique().tolist())
selected_divisions = st.sidebar.multiselect(
    "Select Division(s):",
    options=all_divisions,
    default=all_divisions
)
st.sidebar.markdown("---")

# ---- USER CAPABILITY 3: Margin Threshold Slider ----
st.sidebar.markdown(
    "### 📊 Margin Threshold Slider")
margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin %:",
    min_value=0,
    max_value=100,
    value=0,
    step=1,
    help=(
        "Only show products with "
        "margin above this value"
    )
)
st.sidebar.markdown("---")

# ---- USER CAPABILITY 4: Product Search ----
st.sidebar.markdown(
    "### 🔍 Product Search")
all_products = sorted(
    df['Product Name'].dropna().unique().tolist())
selected_products = st.sidebar.multiselect(
    "Select Product(s):",
    options=all_products,
    default=all_products
)
st.sidebar.markdown("---")

# ---- Sidebar Filter Summary ----
st.sidebar.markdown("""
<div style='background:rgba(255,255,255,0.07);
     padding:12px; border-radius:10px;
     border:1px solid rgba(255,255,255,0.1);'>
    <p style='color:#FFD700 !important;
              font-weight:bold; margin:0 0 8px 0;
              font-size:0.9rem;'>
        ✅ Active Filters
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.write(
    f"🏢 Divisions: **{len(selected_divisions)}**")
st.sidebar.write(
    f"🛍️ Products: **{len(selected_products)}**")
st.sidebar.write(
    f"📊 Min Margin: **{margin_threshold}%**")


# =========================================================
# APPLY FILTERS
# =========================================================
filtered = df.copy()

if len(date_range) == 2:
    filtered = filtered[
        (filtered['Order Date'].dt.date
         >= date_range[0]) &
        (filtered['Order Date'].dt.date
         <= date_range[1])
    ]

if selected_divisions:
    filtered = filtered[
        filtered['Division'].isin(
            selected_divisions)]

if selected_products:
    filtered = filtered[
        filtered['Product Name'].isin(
            selected_products)]

filtered = filtered[
    filtered['Gross Margin%'] >= margin_threshold
]


# =========================================================
# DASHBOARD HEADER WITH IMAGE
# =========================================================

# Header with logo/image
header_col1, header_col2 = st.columns([1, 3])

with header_col1:
    # Candy store image
    st.image(
        "https://plus.unsplash.com/premium_photo-1675033559214-4ff3bd24a177?q=80&w=663&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        caption="Nassau Candy Distributor",
        width = 'stretch'
    )

with header_col2:
    st.markdown("""
<div style='background:linear-gradient(
     135deg,#1a1a2e 0%,#e94560 100%);
     padding:30px; border-radius:16px;
     height:100%;'>
    <h1 style='color:white; margin:0;
               font-size:2rem;
               font-weight:800;'>
        🍬 Nassau Candy Distributor
    </h1>
    <h3 style='color:#FFD700;
               margin:8px 0 0 0;
               font-size:1.1rem;
               font-weight:400;'>
        Product Line Profitability &
        Margin Performance Analysis
    </h3>
    <p style='color:#ecf0f1;
              margin:12px 0 0 0;
              font-size:0.9rem;'>
        📊 Explore product profitability,
        division performance, cost diagnostics,
        and profit concentration —
        all in one interactive dashboard.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# No data warning
if len(filtered) == 0:
    st.error(
        "⚠️ No data matches your current "
        "filters. Please adjust your selections."
    )
    st.stop()


# =========================================================
# KPI CARDS
# =========================================================
total_sales = filtered['Sales'].sum()
total_profit = filtered['Gross Profit'].sum()
avg_margin = filtered['Gross Margin%'].mean()
total_units = filtered['Units'].sum()
n_products = filtered['Product Name'].nunique()
profit_margin_pct = (
    total_profit / total_sales * 100
    if total_sales > 0 else 0
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Sales",
          f"${total_sales:,.0f}")
k2.metric("📈 Total Profit",
          f"${total_profit:,.0f}")
k3.metric("📊 Avg Gross Margin",
          f"{avg_margin:.1f}%")
k4.metric("📦 Total Units",
          f"{total_units:,}")
k5.metric("🛍️ Active Products",
          f"{n_products}")

st.markdown("---")


# =========================================================
# MODULE 1: PRODUCT PROFITABILITY OVERVIEW
# =========================================================
st.markdown("""
<div style='background:linear-gradient(
     90deg,#11998e,#38ef7d);
     padding:14px 22px; border-radius:12px;
     margin-bottom:18px;'>
    <h2 style='color:white; margin:0;
               font-size:1.4rem; border:none;'>
        🏆 Module 1: Product Profitability Overview
    </h2>
    <p style='color:rgba(255,255,255,0.85);
              margin:4px 0 0 0; font-size:0.85rem;'>
        Product-level margin leaderboard
        & profit contribution charts
    </p>
</div>
""", unsafe_allow_html=True)

# Product aggregation
prod = filtered.groupby('Product Name').agg(
    Sales=('Sales', 'sum'),
    Gross_Profit=('Gross Profit', 'sum'),
    Units=('Units', 'sum'),
    Gross_Margin=('Gross Margin%', 'mean'),
    Cost=('Cost', 'sum')
).reset_index().round(2)
prod = prod.sort_values(
    'Gross_Profit', ascending=False)

# Category labels
def categorize(row):
    med = prod['Gross_Profit'].median()
    if (row['Gross_Margin'] >= 60 and
            row['Gross_Profit'] >= med):
        return '⭐ High Profit/High Margin'
    elif (row['Sales'] >= prod['Sales'].median()
            and row['Gross_Margin'] < 50):
        return '⚠️ High Sales/Low Margin'
    else:
        return '❌ Low Profit'

prod['Category'] = prod.apply(
    categorize, axis=1)
prod['Profit Contribution%'] = (
    prod['Gross_Profit'] /
    prod['Gross_Profit'].sum() * 100
).round(2)

# 1A — Product-level margin leaderboard
st.markdown(
    "#### 📋 Product-Level Margin Leaderboard")

m1, m2 = st.columns([1, 1.5])

with m1:
    st.dataframe(
        prod[[
            'Product Name', 'Gross_Profit',
            'Gross_Margin',
            'Profit Contribution%', 'Category'
        ]].rename(columns={
            'Gross_Profit': 'Gross Profit ($)',
            'Gross_Margin': 'Margin %'
        }),
        use_container_width=True,
        height=430,
        hide_index=True
    )

with m2:
    fig_lead = px.bar(
        prod.sort_values('Gross_Margin'),
        x='Gross_Margin',
        y='Product Name',
        orientation='h',
        color='Gross_Margin',
        color_continuous_scale='RdYlGn',
        title='📊 Gross Margin % Leaderboard',
        text='Gross_Margin',
        labels={
            'Gross_Margin': 'Gross Margin %',
            'Product Name': ''
        }
    )
    fig_lead.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_lead.add_vline(
        x=margin_threshold,
        line_dash='dash',
        line_color='red',
        annotation_text=(
            f'Threshold: {margin_threshold}%')
    )
    fig_lead.update_layout(
        height=430,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    st.plotly_chart(
        fig_lead, use_container_width=True)

# 1B — Profit contribution charts
st.markdown(
    "#### 💰 Profit Contribution Charts")

pc1, pc2 = st.columns(2)

with pc1:
    fig_pc1 = px.bar(
        prod.sort_values(
            'Profit Contribution%',
            ascending=False),
        x='Product Name',
        y='Profit Contribution%',
        color='Profit Contribution%',
        color_continuous_scale='Blues',
        title='📈 Profit Contribution % by Product',
        text='Profit Contribution%',
        labels={
            'Profit Contribution%': 'Profit Share %'
        }
    )
    fig_pc1.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_pc1.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_tickangle=-30
    )
    st.plotly_chart(
        fig_pc1, use_container_width=True)

with pc2:
    fig_pc2 = px.pie(
        prod,
        names='Product Name',
        values='Gross_Profit',
        title='🥧 Profit Share by Product',
        hole=0.42,
        color_discrete_sequence=(
            px.colors.qualitative.Set3)
    )
    fig_pc2.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    fig_pc2.update_layout(height=400)
    st.plotly_chart(
        fig_pc2, use_container_width=True)

# Category summary
cc1, cc2, cc3 = st.columns(3)
high = prod[prod['Category'].str.contains('⭐')]
warn = prod[prod['Category'].str.contains('⚠️')]
low = prod[prod['Category'].str.contains('❌')]
cc1.success(
    f"⭐ High Profit/Margin: **{len(high)}** products")
cc2.warning(
    f"⚠️ High Sales/Low Margin: **{len(warn)}** products")
cc3.error(
    f"❌ Low Profit: **{len(low)}** products")

st.markdown("---")


# =========================================================
# MODULE 2: DIVISION PERFORMANCE DASHBOARD
# =========================================================
st.markdown("""
<div style='background:linear-gradient(
     90deg,#f093fb,#f5576c);
     padding:14px 22px; border-radius:12px;
     margin-bottom:18px;'>
    <h2 style='color:white; margin:0;
               font-size:1.4rem; border:none;'>
        🏢 Module 2: Division Performance Dashboard
    </h2>
    <p style='color:rgba(255,255,255,0.85);
              margin:4px 0 0 0; font-size:0.85rem;'>
        Revenue vs profit comparison
        & margin distribution by division
    </p>
</div>
""", unsafe_allow_html=True)

div = filtered.groupby('Division').agg(
    Sales=('Sales', 'sum'),
    Gross_Profit=('Gross Profit', 'sum'),
    Gross_Margin=('Gross Margin%', 'mean'),
    Units=('Units', 'sum'),
    Cost=('Cost', 'sum')
).reset_index().round(2)

div['Revenue Contribution%'] = (
    div['Sales'] / div['Sales'].sum() * 100
).round(2)
div['Profit Contribution%'] = (
    div['Gross_Profit'] /
    div['Gross_Profit'].sum() * 100
).round(2)

# 2A — Revenue vs Profit Comparison
st.markdown(
    "#### 💰 Revenue vs Profit Comparison")

d1, d2 = st.columns(2)

with d1:
    fig_div1 = px.bar(
        div,
        x='Division',
        y=['Sales', 'Gross_Profit'],
        barmode='group',
        title='📊 Revenue vs Profit by Division',
        color_discrete_map={
            'Sales': '#3498db',
            'Gross_Profit': '#2ecc71'
        },
        labels={
            'value': 'Amount ($)',
            'variable': 'Metric'
        }
    )
    fig_div1.update_traces(
        texttemplate='$%{y:,.0f}',
        textposition='outside'
    )
    fig_div1.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(
        fig_div1, use_container_width=True)

with d2:
    fig_div2 = px.pie(
        div,
        names='Division',
        values='Gross_Profit',
        title='🥧 Profit Contribution by Division',
        hole=0.45,
        color_discrete_map={
            'Chocolate': '#8B4513',
            'Sugar': '#FFD700',
            'Other': '#9B59B6'
        }
    )
    fig_div2.update_traces(
        textposition='inside',
        textinfo='percent+label+value'
    )
    fig_div2.update_layout(height=400)
    st.plotly_chart(
        fig_div2, use_container_width=True)

# 2B — Margin Distribution by Division
st.markdown(
    "#### 📊 Margin Distribution by Division")

d3, d4 = st.columns(2)

with d3:
    fig_div3 = px.bar(
        div,
        x='Division',
        y='Gross_Margin',
        color='Gross_Margin',
        color_continuous_scale='RdYlGn',
        title='📊 Avg Gross Margin % by Division',
        text='Gross_Margin',
        labels={'Gross_Margin': 'Avg Margin %'}
    )
    fig_div3.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_div3.add_hline(
        y=60,
        line_dash='dash',
        line_color='green',
        annotation_text='Target: 60%',
        annotation_position='right'
    )
    fig_div3.update_layout(
        height=380,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(
        fig_div3, use_container_width=True)

with d4:
    fig_div4 = px.box(
        filtered,
        x='Division',
        y='Gross Margin%',
        color='Division',
        title='📦 Margin Distribution (Box Plot)',
        color_discrete_map={
            'Chocolate': '#8B4513',
            'Sugar': '#FFD700',
            'Other': '#9B59B6'
        },
        points='all'
    )
    fig_div4.update_layout(
        height=380,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    st.plotly_chart(
        fig_div4, use_container_width=True)

st.markdown("**📋 Division Summary Table:**")
st.dataframe(
    div.rename(columns={
        'Gross_Profit': 'Gross Profit ($)',
        'Gross_Margin': 'Avg Margin %',
        'Revenue Contribution%': 'Revenue Share %',
        'Profit Contribution%': 'Profit Share %'
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# =========================================================
# MODULE 3: COST VS MARGIN DIAGNOSTICS
# =========================================================
st.markdown("""
<div style='background:linear-gradient(
     90deg,#f7971e,#ffd200);
     padding:14px 22px; border-radius:12px;
     margin-bottom:18px;'>
    <h2 style='color:#1a1a2e; margin:0;
               font-size:1.4rem; border:none;'>
        💸 Module 3: Cost vs Margin Diagnostics
    </h2>
    <p style='color:rgba(0,0,0,0.6);
              margin:4px 0 0 0; font-size:0.85rem;'>
        Cost-sales scatter plots
        & margin risk flags
    </p>
</div>
""", unsafe_allow_html=True)

cost = filtered.groupby('Product Name').agg(
    Cost=('Cost', 'sum'),
    Sales=('Sales', 'sum'),
    Gross_Profit=('Gross Profit', 'sum'),
    Gross_Margin=('Gross Margin%', 'mean'),
    Units=('Units', 'sum')
).reset_index().round(2)

cost['Risk_Flag'] = cost['Gross_Margin'].apply(
    lambda x:
    '🔴 High Risk' if x < 15
    else ('🟡 Medium Risk' if x < 50
          else '🟢 Safe')
)

# 3A — Cost-sales scatter plots
st.markdown(
    "#### 🎯 Cost-Sales Scatter Plots")

c1, c2 = st.columns(2)

with c1:
    fig_c1 = px.scatter(
        cost,
        x='Cost',
        y='Sales',
        color='Risk_Flag',
        size='Gross_Profit',
        hover_name='Product Name',
        hover_data={
            'Cost': ':$,.2f',
            'Sales': ':$,.2f',
            'Gross_Margin': ':.1f',
            'Risk_Flag': True
        },
        color_discrete_map={
            '🔴 High Risk': '#e74c3c',
            '🟡 Medium Risk': '#f39c12',
            '🟢 Safe': '#2ecc71'
        },
        title='🎯 Cost vs Sales\n'
              '(Bubble size = Gross Profit)',
        labels={
            'Cost': 'Total Cost ($)',
            'Sales': 'Total Sales ($)',
            'Risk_Flag': 'Risk Level'
        }
    )
    fig_c1.update_layout(
        height=420,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(
        fig_c1, use_container_width=True)

with c2:
    fig_c2 = px.scatter(
        cost,
        x='Cost',
        y='Gross_Profit',
        color='Gross_Margin',
        size='Units',
        hover_name='Product Name',
        color_continuous_scale='RdYlGn',
        title='💰 Cost vs Gross Profit\n'
              '(Color = Margin %)',
        text='Product Name',
        labels={
            'Cost': 'Total Cost ($)',
            'Gross_Profit': 'Gross Profit ($)',
            'Gross_Margin': 'Margin %'
        }
    )
    fig_c2.update_traces(
        textposition='top center',
        textfont_size=8
    )
    fig_c2.update_layout(
        height=420,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(
        fig_c2, use_container_width=True)

# 3B — Margin risk flags
st.markdown("#### ⚠️ Margin Risk Flags")

c3, c4 = st.columns(2)

with c3:
    fig_c3 = px.bar(
        cost.sort_values('Gross_Margin'),
        x='Gross_Margin',
        y='Product Name',
        orientation='h',
        color='Risk_Flag',
        color_discrete_map={
            '🔴 High Risk': '#e74c3c',
            '🟡 Medium Risk': '#f39c12',
            '🟢 Safe': '#2ecc71'
        },
        title='🚦 Margin Risk Flag by Product',
        text='Gross_Margin',
        labels={
            'Gross_Margin': 'Gross Margin %',
            'Product Name': '',
            'Risk_Flag': 'Risk'
        }
    )
    fig_c3.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_c3.add_vline(
        x=50,
        line_dash='dash',
        line_color='black',
        annotation_text='Safe Line (50%)'
    )
    fig_c3.update_layout(
        height=420,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(
        fig_c3, use_container_width=True)

with c4:
    risk_grp = cost.groupby(
        'Risk_Flag'
    ).size().reset_index(name='Count')

    fig_c4 = px.pie(
        risk_grp,
        names='Risk_Flag',
        values='Count',
        title='📊 Risk Distribution',
        color='Risk_Flag',
        color_discrete_map={
            '🔴 High Risk': '#e74c3c',
            '🟡 Medium Risk': '#f39c12',
            '🟢 Safe': '#2ecc71'
        },
        hole=0.45
    )
    fig_c4.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    fig_c4.update_layout(height=420)
    st.plotly_chart(
        fig_c4, use_container_width=True)

risky = cost[cost['Risk_Flag'] != '🟢 Safe']
if len(risky) > 0:
    st.markdown(
        "**🚨 Products Needing Attention:**")
    st.dataframe(
        risky[[
            'Product Name', 'Cost',
            'Sales', 'Gross_Profit',
            'Gross_Margin', 'Risk_Flag'
        ]].rename(columns={
            'Gross_Profit': 'Gross Profit ($)',
            'Gross_Margin': 'Margin %',
            'Risk_Flag': '⚠️ Risk Level'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.success(
        "✅ All products are financially safe!")

st.markdown("---")


# =========================================================
# MODULE 4: PROFIT CONCENTRATION ANALYSIS
# =========================================================
st.markdown("""
<div style='background:linear-gradient(
     90deg,#4776E6,#8E54E9);
     padding:14px 22px; border-radius:12px;
     margin-bottom:18px;'>
    <h2 style='color:white; margin:0;
               font-size:1.4rem; border:none;'>
        📈 Module 4: Profit Concentration Analysis
    </h2>
    <p style='color:rgba(255,255,255,0.85);
              margin:4px 0 0 0; font-size:0.85rem;'>
        Pareto charts & dependency indicators
    </p>
</div>
""", unsafe_allow_html=True)

pareto = prod.sort_values(
    'Gross_Profit', ascending=False).copy()
pareto['Cumulative Profit%'] = (
    pareto['Gross_Profit'].cumsum() /
    pareto['Gross_Profit'].sum() * 100
).round(2)
pareto['Cumulative Revenue%'] = (
    pareto['Sales'].cumsum() /
    pareto['Sales'].sum() * 100
).round(2)
top80 = pareto[pareto['Cumulative Profit%'] <= 80]

# 4A — Pareto Charts
st.markdown("#### 📊 Pareto Charts")

p1, p2 = st.columns(2)

with p1:
    fig_p1 = go.Figure()
    fig_p1.add_trace(go.Bar(
        x=pareto['Product Name'],
        y=pareto['Gross_Profit'],
        name='Gross Profit',
        marker_color='#3498db',
        text=pareto['Gross_Profit'],
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    ))
    fig_p1.add_trace(go.Scatter(
        x=pareto['Product Name'],
        y=pareto['Cumulative Profit%'],
        name='Cumulative Profit %',
        yaxis='y2',
        line=dict(color='#e74c3c', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#e74c3c')
    ))
    fig_p1.update_layout(
        title='📊 Pareto — Profit Concentration',
        yaxis=dict(title='Gross Profit ($)'),
        yaxis2=dict(
            title='Cumulative Profit %',
            overlaying='y',
            side='right',
            range=[0, 115]
        ),
        height=430,
        plot_bgcolor='white',
        paper_bgcolor='white',
        shapes=[dict(
            type='line',
            y0=80, y1=80,
            x0=0, x1=1,
            xref='paper', yref='y2',
            line=dict(
                color='green',
                dash='dash',
                width=2
            )
        )],
        annotations=[dict(
            x=0.5, y=83,
            xref='paper', yref='y2',
            text='80% Profit Line',
            showarrow=False,
            font=dict(color='green', size=11)
        )]
    )
    st.plotly_chart(
        fig_p1, use_container_width=True)

with p2:
    fig_p2 = go.Figure()
    fig_p2.add_trace(go.Bar(
        x=pareto['Product Name'],
        y=pareto['Sales'],
        name='Revenue',
        marker_color='#2ecc71',
        text=pareto['Sales'],
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    ))
    fig_p2.add_trace(go.Scatter(
        x=pareto['Product Name'],
        y=pareto['Cumulative Revenue%'],
        name='Cumulative Revenue %',
        yaxis='y2',
        line=dict(color='#9b59b6', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#9b59b6')
    ))
    fig_p2.update_layout(
        title='📊 Pareto — Revenue Concentration',
        yaxis=dict(title='Revenue ($)'),
        yaxis2=dict(
            title='Cumulative Revenue %',
            overlaying='y',
            side='right',
            range=[0, 115]
        ),
        height=430,
        plot_bgcolor='white',
        paper_bgcolor='white',
        shapes=[dict(
            type='line',
            y0=80, y1=80,
            x0=0, x1=1,
            xref='paper', yref='y2',
            line=dict(
                color='green',
                dash='dash',
                width=2
            )
        )]
    )
    st.plotly_chart(
        fig_p2, use_container_width=True)

# 4B — Dependency Indicators
st.markdown("#### 🔗 Dependency Indicators")

top1_pct = pareto.iloc[0]['Profit Contribution%']
top3_pct = (
    pareto.head(3)['Profit Contribution%'].sum())
pct_prods = (
    len(top80) / len(pareto) * 100)
concentration_risk = (
    "🔴 HIGH" if top1_pct > 30
    else ("🟡 MEDIUM"
          if top1_pct > 20
          else "🟢 LOW")
)

dep1, dep2, dep3, dep4 = st.columns(4)
dep1.metric(
    "🏆 Products = 80% Profit",
    f"{len(top80)} products",
    delta=f"{pct_prods:.0f}% of portfolio"
)
dep2.metric(
    "📊 Top Product Share",
    f"{top1_pct:.1f}%",
    delta="of total profit"
)
dep3.metric(
    "📦 Top 3 Products Share",
    f"{top3_pct:.1f}%",
    delta="of total profit"
)
dep4.metric(
    "⚠️ Concentration Risk",
    concentration_risk,
    delta="Dependency Level"
)

# Dependency alert
if top1_pct > 30:
    st.error(
        f"🚨 **Over-Dependency Risk!** "
        f"**'{pareto.iloc[0]['Product Name']}'** "
        f"alone contributes **{top1_pct:.1f}%** "
        f"of total profit. "
        f"Business diversification needed!"
    )
elif top3_pct > 80:
    st.warning(
        f"⚠️ **High Concentration!** "
        f"Top 3 products = **{top3_pct:.1f}%** "
        f"of total profit. Monitor closely!"
    )
else:
    st.success(
        "✅ Healthy profit distribution "
        "across products!"
    )

st.markdown("**📋 Pareto Analysis Table:**")
st.dataframe(
    pareto[[
        'Product Name', 'Gross_Profit',
        'Profit Contribution%',
        'Cumulative Profit%'
    ]].rename(columns={
        'Gross_Profit': 'Gross Profit ($)',
        'Profit Contribution%': 'Profit Share %',
        'Cumulative Profit%': 'Cumulative %'
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# =========================================================
# KEY BUSINESS INSIGHTS
# =========================================================
st.markdown("""
<div style='background:linear-gradient(
     90deg,#1a1a2e,#16213e);
     padding:14px 22px; border-radius:12px;
     margin-bottom:18px;'>
    <h2 style='color:white; margin:0;
               font-size:1.4rem; border:none;'>
        📌 Key Business Insights
    </h2>
</div>
""", unsafe_allow_html=True)

ins1, ins2 = st.columns(2)

with ins1:
    top_prod = pareto.iloc[0]['Product Name']
    top_prof = pareto.iloc[0]['Gross_Profit']
    low_prod = pareto.iloc[-1]['Product Name']
    low_prof = pareto.iloc[-1]['Gross_Profit']
    top_div = div.sort_values(
        'Gross_Profit',
        ascending=False
    ).iloc[0]['Division']
    best_margin = prod.sort_values(
        'Gross_Margin',
        ascending=False
    ).iloc[0]['Product Name']

    st.success(
        f"🏆 **Best Product:** {top_prod} "
        f"→ ${top_prof:,.2f} profit"
    )
    st.error(
        f"⚠️ **Lowest Product:** {low_prod} "
        f"→ ${low_prof:,.2f} profit"
    )
    st.info(
        f"🏢 **Best Division:** {top_div}"
    )
    st.info(
        f"💎 **Best Margin Product:** {best_margin}"
    )
    st.warning(
        f"🚨 **{len(risky)} products** "
        f"need pricing/cost review!"
    )

with ins2:
    st.info(
        f"📊 **Overall Profit Margin:** "
        f"{profit_margin_pct:.1f}%"
    )
    st.success(
        f"💰 **Total Revenue:** "
        f"${total_sales:,.2f}"
    )
    st.success(
        f"📈 **Total Profit:** "
        f"${total_profit:,.2f}"
    )
    st.info(
        f"🎯 **Pareto Finding:** Only "
        f"**{len(top80)}/{len(pareto)} products** "
        f"= 80% of all profit!"
    )
    if concentration_risk == "🔴 HIGH":
        st.error(
            "🔴 **HIGH dependency risk** — "
            "Too reliant on few products!"
        )
    else:
        st.success(
            "✅ **Healthy distribution** — "
            "Good product diversification!"
        )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("""
<div style='text-align:center;
     padding:18px;
     background:linear-gradient(
         90deg,#1a1a2e,#e94560);
     border-radius:12px;'>
    <p style='color:white; margin:0;
              font-size:0.95rem;'>
        🍬 <b>Nassau Candy Distributor</b> |
        Product Line Profitability &
        Margin Performance Analysis |
        Built with Streamlit & Plotly
    </p>
</div>
""", unsafe_allow_html=True)
