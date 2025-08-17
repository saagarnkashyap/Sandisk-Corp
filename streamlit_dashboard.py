import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Semiconductor Financial Dashboard",
    page_icon="Sandisk-Logo-500x281.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Semiconductor Companies Financial Dashboard")
st.markdown("""
This dashboard analyzes financial data for semiconductor companies (WDC, Intel, Micron, TSMC) 
with focus on inventory and sales metrics for internship case study presentation.
""")

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

import os

# Get path relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
processed_file_path = os.path.join(BASE_DIR, "processed_inventory_data.csv")


df = load_data(processed_file_path)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

companies = df["Company"].unique()
selected_companies = st.sidebar.multiselect(
    "Select Companies", 
    companies, 
    default=companies.tolist(),
    help="Choose which companies to include in the analysis"
)

df_filtered = df[df["Company"].isin(selected_companies)]

# Date Range Filter
min_date = df_filtered["Date"].min()
max_date = df_filtered["Date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range", 
    value=(min_date, max_date), 
    min_value=min_date, 
    max_value=max_date,
    help="Filter data by date range"
)

if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["Date"] >= pd.Timestamp(date_range[0])) & 
        (df_filtered["Date"] <= pd.Timestamp(date_range[1]))
    ]

# Metric selector
metrics = df["Metric"].unique()
selected_metric = st.sidebar.selectbox(
    "Focus Metric for Analysis",
    metrics,
    index=0,
    help="Select a metric to highlight in detailed analysis"
)

# Ensure 'Value' column is numeric
df_filtered["Value"] = pd.to_numeric(df_filtered["Value"], errors="coerce")

# Key Metrics Section
st.header("Key Metrics Overview")

col1, col2, col3, col4 = st.columns(4)

# Calculate metrics
inventory_df = df_filtered[df_filtered["Metric"] == "Inventory"]
revenue_df = df_filtered[df_filtered["Metric"] == "Revenue"]
cogs_df = df_filtered[df_filtered["Metric"] == "Cost Of Goods Sold"]
cash_df = df_filtered[df_filtered["Metric"] == "Cash On Hand"]

# Average calculations
avg_inventory = inventory_df["Value"].mean() if not inventory_df.empty else 0
avg_revenue = revenue_df["Value"].mean() if not revenue_df.empty else 0
avg_cogs = cogs_df["Value"].mean() if not cogs_df.empty else 0
avg_cash = cash_df["Value"].mean() if not cash_df.empty else 0

# Inventory Turnover calculation
inventory_turnover = avg_cogs / avg_inventory if (avg_cogs and avg_inventory and avg_inventory != 0) else 0

with col1:
    st.metric(
        label="Average Inventory", 
        value=f"${avg_inventory:,.0f}M" if avg_inventory else "N/A",
        delta=f"{len(inventory_df)} data points"
    )
with col2:
    st.metric(
        label="Average Revenue", 
        value=f"${avg_revenue:,.0f}M" if avg_revenue else "N/A",
        delta=f"{len(revenue_df)} data points"
    )
with col3:
    st.metric(
        label="Inventory Turnover", 
        value=f"{inventory_turnover:.2f}" if inventory_turnover else "N/A",
        delta="COGS/Inventory ratio"
    )
with col4:
    st.metric(
        label="Average Cash", 
        value=f"${avg_cash:,.0f}M" if avg_cash else "N/A",
        delta=f"{len(cash_df)} data points"
    )

# Financial Analysis Section
st.header("Financial Analysis")

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Trends", "Comparisons", "Detailed Metrics"])

with tab1:
    st.subheader("Revenue and Inventory Trends Over Time")
    
    # Revenue Over Time
    if not revenue_df.empty:
        fig_revenue = px.line(
            revenue_df, 
            x="Date", 
            y="Value", 
            color="Company", 
            title="Revenue Over Time (in USD)",
            markers=True
        )
        fig_revenue.update_layout(
            xaxis_title="Date",
            yaxis_title="Revenue (USD)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.warning("No revenue data available for selected filters.")

    # Inventory Over Time
    if not inventory_df.empty:
        fig_inventory = px.line(
            inventory_df, 
            x="Date", 
            y="Value", 
            color="Company", 
            title="Inventory Over Time (in USD)",
            markers=True
        )
        fig_inventory.update_layout(
            xaxis_title="Date",
            yaxis_title="Inventory (USD)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_inventory, use_container_width=True)
    else:
        st.warning("No inventory data available for selected filters.")

with tab2:
    st.subheader("Company Comparisons")
    
    # Company comparison by selected metric
    metric_df = df_filtered[df_filtered["Metric"] == selected_metric]
    if not metric_df.empty:
        # Bar chart comparison
        avg_by_company = metric_df.groupby("Company")["Value"].mean().reset_index()
        fig_comparison = px.bar(
            avg_by_company,
            x="Company",
            y="Value",
            title=f"Average {selected_metric} by Company",
            color="Company"
        )
        fig_comparison.update_layout(
            xaxis_title="Company",
            yaxis_title=f"{selected_metric} (USD)"
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Box plot for distribution
        fig_box = px.box(
            metric_df,
            x="Company",
            y="Value",
            title=f"{selected_metric} Distribution by Company"
        )
        fig_box.update_layout(
            xaxis_title="Company",
            yaxis_title=f"{selected_metric} (USD)"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning(f"No data available for {selected_metric} with current filters.")

with tab3:
    st.subheader("Detailed Financial Metrics")
    
    # Multi-metric comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost of Goods Sold vs Gross Profit
        cogs_gp_df = df_filtered[df_filtered["Metric"].isin(["Cost Of Goods Sold", "Gross Profit"])]
        if not cogs_gp_df.empty:
            fig_cogs_gp = px.bar(
                cogs_gp_df, 
                x="Date", 
                y="Value", 
                color="Metric", 
                facet_col="Company",
                title="Cost of Goods Sold vs Gross Profit",
                barmode="group"
            )
            fig_cogs_gp.update_layout(height=400)
            st.plotly_chart(fig_cogs_gp, use_container_width=True)
        else:
            st.warning("No COGS/Gross Profit data available.")
    
    with col2:
        # Cash on Hand Over Time
        if not cash_df.empty:
            fig_cash = px.line(
                cash_df, 
                x="Date", 
                y="Value", 
                color="Company", 
                title="Cash On Hand Over Time",
                markers=True
            )
            fig_cash.update_layout(height=400)
            st.plotly_chart(fig_cash, use_container_width=True)
        else:
            st.warning("No cash data available.")

    # Inventory Turnover Analysis
    turnover_df = df_filtered[df_filtered["Metric"] == "Inventory Turnover"]
    if not turnover_df.empty:
        fig_turnover = px.scatter(
            turnover_df,
            x="Date",
            y="Value",
            color="Company",
            size="Value",
            title="Inventory Turnover Ratio Over Time",
            hover_data=["Company", "Date", "Value"]
        )
        fig_turnover.update_layout(
            xaxis_title="Date",
            yaxis_title="Inventory Turnover Ratio"
        )
        st.plotly_chart(fig_turnover, use_container_width=True)
    else:
        st.warning("No inventory turnover data available.")

# with tab4:
#     st.subheader(f"Focus Analysis: {selected_metric}")
    
#     focus_df = df_filtered[df_filtered["Metric"] == selected_metric]
#     if not focus_df.empty:
#         # Summary statistics
#         st.write("**Summary Statistics:**")
#         summary_stats = focus_df.groupby("Company")["Value"].agg([
#             'count', 'mean', 'median', 'std', 'min', 'max'
#         ]).round(2)
#         st.dataframe(summary_stats)
        
#         # Correlation analysis if multiple companies
#         if len(selected_companies) > 1:
#             st.write("**Correlation Analysis:**")
#             pivot_df = focus_df.pivot_table(
#                 index="Date", 
#                 columns="Company", 
#                 values="Value"
#             )
#             correlation_matrix = pivot_df.corr()
            
#             fig_corr = px.imshow(
#                 correlation_matrix,
#                 title=f"{selected_metric} Correlation Matrix",
#                 color_continuous_scale="RdBu",
#                 aspect="auto"
#             )
#             st.plotly_chart(fig_corr, use_container_width=True)
        
#         # Growth rate analysis
#         st.write("**Quarter-over-Quarter Growth Rates:**")
#         growth_data = []
#         for company in selected_companies:
#             company_data = focus_df[focus_df["Company"] == company].sort_values("Date")
#             if len(company_data) > 1:
#                 company_data["Growth_Rate"] = company_data["Value"].pct_change() * 100
#                 growth_data.append(company_data)
        
#         if growth_data:
#             growth_df = pd.concat(growth_data)
#             growth_df = growth_df.dropna(subset=["Growth_Rate"])
            
#             if not growth_df.empty:
#                 fig_growth = px.bar(
#                     growth_df,
#                     x="Date",
#                     y="Growth_Rate",
#                     color="Company",
#                     title=f"{selected_metric} Quarter-over-Quarter Growth Rate (%)",
#                     barmode="group"
#                 )
#                 fig_growth.update_layout(
#                     xaxis_title="Date",
#                     yaxis_title="Growth Rate (%)"
#                 )
#                 st.plotly_chart(fig_growth, use_container_width=True)
#     else:
#         st.warning(f"No data available for {selected_metric}.")

# Raw Data Section
st.header("Raw Data")
st.write(f"Showing {len(df_filtered)} records")

# Add search functionality
search_term = st.text_input("Search in data:", placeholder="Enter company name, metric, or value...")
if search_term:
    mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
    df_display = df_filtered[mask]
else:
    df_display = df_filtered

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True
)

# Download section
st.header("Download Data")
col1, col2 = st.columns(2)

with col1:
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"semiconductor_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    st.info("""
    **Data Source:** Macrotrends   
    **Dashboard for:** Sandisk Internship (Case Study Presentation)  
    **Last Updated:** """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Saagar N Kashyap • Data Analysis for SDC</p>
</div>
""", unsafe_allow_html=True)

