from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "cleaned" / "superstore_cleaned.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["Order Date", "Ship Date"])


df = load_data()

st.title("E-Commerce Sales & Customer Behavior Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

all_years = sorted(df["Year"].unique())
all_regions = sorted(df["Region"].unique())
all_categories = sorted(df["Category"].unique())

years = st.sidebar.multiselect("Year", all_years, default=all_years)
regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)
categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)

filtered = df[
    df["Year"].isin(years)
    & df["Region"].isin(regions)
    & df["Category"].isin(categories)
]

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# KPI numbers
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order ID"].nunique()
avg_order_value = total_sales / total_orders

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"{total_sales:,.0f}")
col2.metric("Total Profit", f"{total_profit:,.0f}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Avg Order Value", f"{avg_order_value:,.0f}")

# Monthly sales trend
st.subheader("Monthly Sales Trend")

monthly = (filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"]
                   .sum()
                   .reset_index())
monthly["Order Date"] = monthly["Order Date"].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly["Order Date"], monthly["Sales"], marker="o")
ax.set_xlabel("Month")
ax.set_ylabel("Total Sales")
st.pyplot(fig)

# Category and Region charts
left, right = st.columns(2)

with left:
    st.subheader("Sales by Category")
    st.bar_chart(filtered.groupby("Category")["Sales"].sum())

with right:
    st.subheader("Sales by Region")
    st.bar_chart(filtered.groupby("Region")["Sales"].sum())

# Top products and customers
left2, right2 = st.columns(2)

with left2:
    st.subheader("Top 10 Products by Sales")
    top_products = (filtered.groupby("Product Name")["Sales"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(10)
                            .round(0)
                            .reset_index())
    st.dataframe(top_products, hide_index=True)

with right2:
    st.subheader("Top 10 Customers by Sales")
    top_customers = (filtered.groupby("Customer Name")["Sales"]
                             .sum()
                             .sort_values(ascending=False)
                             .head(10)
                             .round(0)
                             .reset_index())
    st.dataframe(top_customers, hide_index=True)