import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

st.title("Retail Sales & Marketing Intelligence Dashboard")
st.markdown("Interactive dashboard built from the Online Retail dataset")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "Online Retail.xlsx")
PARQUET_PATH = os.path.join(BASE_DIR, "online_retail_cache.parquet")


# Data loading (parquet cache = ~10x faster after first run)
@st.cache_data(show_spinner="Loading data...")
def load_data():
    if os.path.exists(PARQUET_PATH):
        return pd.read_parquet(PARQUET_PATH)
    df = pd.read_excel(DATA_PATH)
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df.drop_duplicates()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["DayName"] = df["InvoiceDate"].dt.day_name()
    df["Hour"] = df["InvoiceDate"].dt.hour
    df.to_parquet(PARQUET_PATH, index=False)
    return df


# Cached computations keyed by filter selection (correct invalidation)

@st.cache_data(show_spinner=False)
def get_filtered(countries, months):
    return data[data["Country"].isin(countries) & data["YearMonth"].isin(months)].copy()


@st.cache_data(show_spinner=False)
def compute_monthly_sales(countries, months):
    fd = get_filtered(countries, months)
    return fd.groupby("YearMonth", as_index=False)["Revenue"].sum().sort_values("YearMonth")


@st.cache_data(show_spinner=False)
def compute_top_products(countries, months):
    fd = get_filtered(countries, months)
    return (fd.groupby("Description", as_index=False)["Revenue"]
              .sum().sort_values("Revenue", ascending=False).head(10))


@st.cache_data(show_spinner=False)
def compute_top_countries(countries, months):
    fd = get_filtered(countries, months)
    return (fd.groupby("Country", as_index=False)["Revenue"]
              .sum().sort_values("Revenue", ascending=False).head(10))


@st.cache_data(show_spinner=False)
def compute_day_hour_sales(countries, months):
    fd = get_filtered(countries, months)
    day_sales = fd.groupby("DayName", as_index=False)["Revenue"].sum()
    hour_sales = fd.groupby("Hour", as_index=False)["Revenue"].sum()
    return day_sales, hour_sales


@st.cache_data(show_spinner=False)
def compute_customer_df(countries, months):
    fd = get_filtered(countries, months)
    return fd.groupby("CustomerID").agg(
        TotalRevenue=("Revenue", "sum"),
        TotalOrders=("InvoiceNo", "nunique"),
        TotalQuantity=("Quantity", "sum")
    ).reset_index()


@st.cache_data(show_spinner=False)
def compute_rfm(countries, months):
    fd = get_filtered(countries, months)
    snapshot_date = fd["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = fd.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum")
    ).reset_index()
    rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
    rfm["R_score"] = rfm["R_score"].astype(int)
    rfm["F_score"] = rfm["F_score"].astype(int)
    rfm["M_score"] = rfm["M_score"].astype(int)
    rfm["RFM_Total"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    def assign_segment(score):
        if score >= 10:
            return "Champions"
        elif score >= 8:
            return "Loyal Customers"
        elif score >= 6:
            return "Potential Loyalists"
        elif score >= 4:
            return "At Risk"
        else:
            return "Lost Customers"

    rfm["Segment"] = rfm["RFM_Total"].apply(assign_segment)
    return rfm


@st.cache_data(show_spinner="Running clustering...")
def compute_clustering(countries, months, n_clusters):
    fd = get_filtered(countries, months)
    snapshot_date = fd["InvoiceDate"].max() + pd.Timedelta(days=1)
    cluster_data = fd.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
        TotalQuantity=("Quantity", "sum"),
        UniqueProducts=("StockCode", "nunique")
    ).reset_index()
    features = ["Recency", "Frequency", "Monetary", "TotalQuantity", "UniqueProducts"]
    X_scaled = StandardScaler().fit_transform(cluster_data[features])
    cluster_data["Cluster"] = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(X_scaled).astype(str)
    pca = PCA(n_components=2, random_state=42).fit_transform(X_scaled)
    cluster_data["PC1"] = pca[:, 0]
    cluster_data["PC2"] = pca[:, 1]
    return cluster_data, features


# Load data 
data = load_data()

# Sidebar filters 
st.sidebar.header("Filter Options")
country_options = sorted(data["Country"].unique())
selected_countries = st.sidebar.multiselect("Select Country", country_options, default=country_options)

month_options = sorted(data[data["Country"].isin(selected_countries)]["YearMonth"].unique())
selected_months = st.sidebar.multiselect("Select Year-Month", month_options, default=month_options)

c = tuple(sorted(selected_countries))
m = tuple(sorted(selected_months))

fd = get_filtered(c, m)

#  KPI Metrics 
total_revenue = fd["Revenue"].sum()
total_orders = fd["InvoiceNo"].nunique()
total_customers = fd["CustomerID"].nunique()
total_products = fd["StockCode"].nunique()
avg_order_value = fd.groupby("InvoiceNo")["Revenue"].sum().mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Total Customers", f"{total_customers:,}")
col4.metric("Total Products", f"{total_products:,}")
col5.metric("Avg Order Value", f"£{avg_order_value:,.2f}")

st.divider()

# Monthly Revenue Trend 
st.subheader("Monthly Revenue Trend")
monthly_sales = compute_monthly_sales(c, m)
fig_monthly = px.line(monthly_sales, x="YearMonth", y="Revenue", markers=True,
                      labels={"YearMonth": "Month", "Revenue": "Revenue (£)"})
st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

# Top Products & Countries 
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Products by Revenue")
    top_products = compute_top_products(c, m)
    fig_products = px.bar(top_products, x="Revenue", y="Description", orientation="h",
                          labels={"Revenue": "Revenue (£)", "Description": "Product"})
    fig_products.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_products, use_container_width=True)

with col_right:
    st.subheader("Top 10 Countries by Revenue")
    top_countries = compute_top_countries(c, m)
    fig_countries = px.bar(top_countries, x="Revenue", y="Country", orientation="h",
                           labels={"Revenue": "Revenue (£)"})
    fig_countries.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_countries, use_container_width=True)

st.divider()

# Sales Patterns 
st.subheader("Sales Patterns")
day_sales, hour_sales = compute_day_hour_sales(c, m)

col_day, col_hour = st.columns(2)
with col_day:
    st.markdown("Revenue by Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_sales["DayName"] = pd.Categorical(day_sales["DayName"], categories=day_order, ordered=True)
    day_sales = day_sales.sort_values("DayName")
    fig_day = px.bar(day_sales, x="DayName", y="Revenue",
                     labels={"DayName": "Day", "Revenue": "Revenue (£)"})
    st.plotly_chart(fig_day, use_container_width=True)

with col_hour:
    st.markdown("Revenue by Hour of Day")
    fig_hour = px.bar(hour_sales, x="Hour", y="Revenue",
                      labels={"Hour": "Hour (24h)", "Revenue": "Revenue (£)"})
    st.plotly_chart(fig_hour, use_container_width=True)

st.divider()

# Customer Analysis 
st.subheader("Customer Analysis")
customer_df = compute_customer_df(c, m)

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("Top 10 Customers by Revenue")
    top_customers = customer_df.sort_values("TotalRevenue", ascending=False).head(10)
    fig_top_customers = px.bar(top_customers, x="TotalRevenue", y="CustomerID",
                               orientation="h", labels={"TotalRevenue": "Revenue (£)", "CustomerID": "Customer ID"})
    fig_top_customers.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_top_customers, use_container_width=True)

with col_right:
    st.markdown("Repeat vs One-Time Customers")
    customer_df["CustomerType"] = np.where(customer_df["TotalOrders"] > 1, "Repeat Customer", "One-time Customer")
    customer_type_counts = customer_df["CustomerType"].value_counts().reset_index()
    customer_type_counts.columns = ["CustomerType", "Count"]
    fig_customer_type = px.pie(customer_type_counts, names="CustomerType", values="Count",
                               color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_customer_type, use_container_width=True)

st.divider()

# RFM Segmentation
st.subheader("RFM Segmentation")
rfm = compute_rfm(c, m)

col_rfm1, col_rfm2 = st.columns(2)
with col_rfm1:
    segment_counts = rfm["Segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Count"]
    fig_rfm = px.bar(segment_counts, x="Segment", y="Count", color="Segment",
                     color_discrete_sequence=px.colors.qualitative.Set1,
                     labels={"Count": "Number of Customers"})
    st.plotly_chart(fig_rfm, use_container_width=True)

with col_rfm2:
    segment_avg = rfm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean().round(2)
    st.markdown("Average RFM Values per Segment")
    st.dataframe(segment_avg, use_container_width=True)

st.divider()

# Customer Clustering 
st.subheader("Customer Clustering (K-Means)")
n_clusters = st.slider("Select number of clusters", min_value=2, max_value=8, value=4)
cluster_data, features = compute_clustering(c, m, n_clusters)

col_cl1, col_cl2 = st.columns(2)
with col_cl1:
    st.markdown("Cluster Summary (Average Features)")
    cluster_summary = cluster_data.groupby("Cluster")[features].mean().round(2)
    st.dataframe(cluster_summary, use_container_width=True)

with col_cl2:
    st.markdown("Customers per Cluster")
    cluster_counts = cluster_data["Cluster"].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Count"]
    fig_cc = px.bar(cluster_counts, x="Cluster", y="Count",
                    labels={"Cluster": "Cluster", "Count": "Number of Customers"})
    st.plotly_chart(fig_cc, use_container_width=True)

fig_pca = px.scatter(
    cluster_data,
    x="PC1",
    y="PC2",
    color=cluster_data["Cluster"].astype(str),
    labels={"color": "Cluster"},
    title="PCA View of Customer Clusters",
    opacity=0.7,
)
st.plotly_chart(fig_pca, use_container_width=True)

st.divider()

# Business Recommendations 
st.subheader("Business Recommendations")
st.markdown("""
- Loyalty campaigns — Focus rewards on Champions and Loyal Customers to retain high-value customers.
- Re-engagement — Target At Risk and Lost Customers with personalised win-back offers.
- Product promotion — Invest marketing budget behind the top-performing products by revenue.
- Country strategy — Prioritise the top revenue markets; test growth campaigns in mid-tier countries.
- Cluster-based personalisation — Use customer clusters to tailor messaging and product recommendations.
- Peak-hours targeting — Run promotions during high-traffic hours to maximise conversion.
- Repeat-customer programme — Convert one-time buyers with incentives for a second purchase.
""")
