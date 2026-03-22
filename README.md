<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&pause=1000&color=F97316&center=true&vCenter=true&width=700&lines=Retail+Sales+%26+Marketing+Intelligence;Customer+Segmentation+%7C+RFM+Analysis;K-Means+Clustering+%7C+Trend+Explorer" alt="Typing SVG" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.20-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)

[![GitHub](https://img.shields.io/badge/GitHub-raselmian03-181717?style=for-the-badge&logo=github)](https://github.com/raselmian03)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://raselmian03-retail-dashboard.streamlit.app)

</div>

---

## Overview

An end-to-end interactive sales analytics dashboard built on the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail). The app lets business users slice data by country and time period, explore revenue trends, understand customer behaviour through RFM scoring, and discover natural customer segments using K-Means clustering — all in one fast, filterable interface.

---

## Demo

<div align="center">

> **Live on Streamlit Cloud →** [Open Dashboard](https://raselmian03-retail-dashboard.streamlit.app)

![Dashboard Preview](https://raw.githubusercontent.com/raselmian03/retail-sales-dashboard/main/assets/demo.gif)

</div>

---

## Features

| Section | What it shows |
|---|---|
| **KPI Metrics** | Total revenue, orders, customers, products & average order value |
| **Monthly Revenue Trend** | Interactive line chart filterable by country & period |
| **Top 10 Products** | Horizontal bar chart of highest-revenue products |
| **Top 10 Countries** | Revenue breakdown by market |
| **Sales Patterns** | Revenue heatmap by day-of-week and hour-of-day |
| **Customer Analysis** | Top customers + repeat vs one-time buyer split |
| **RFM Segmentation** | Champions, Loyal, Potential Loyalists, At Risk, Lost |
| **K-Means Clustering** | Configurable clusters (2–8) with PCA scatter plot |
| **Business Recommendations** | Actionable strategy cards based on findings |

---

## Tech Stack

```
app.py                    ← Streamlit dashboard (single-file)
├── Data layer            ← Pandas + Parquet cache (10× faster reload)
├── Visualisation         ← Plotly Express & Graph Objects
├── Segmentation          ← RFM scoring with quartile binning
└── Clustering            ← K-Means (scikit-learn) + PCA projection
```

---

## Dataset

- **Source:** [UCI Machine Learning Repository – Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail)
- **Records:** ~541 000 transactions
- **Period:** Dec 2010 – Dec 2011
- **Market:** UK-based retailer, sales to 38 countries

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/raselmian03/retail-sales-dashboard.git
cd retail-sales-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add the dataset
#    Download "Online Retail.xlsx" from UCI and place it in the project root.
#    (First run creates a parquet cache; subsequent runs load instantly.)

# 4. Launch
streamlit run app.py
```

> The app ships with a pre-built parquet cache so you can explore all charts immediately without downloading the Excel file.

---

## Project Structure

```
retail-sales-dashboard/
├── app.py                        # Main Streamlit app
├── online_retail_cache.parquet   # Pre-processed data cache
├── requirements.txt
└── .gitignore
```

---

## Dashboard Walkthrough

### 1 · Sidebar Filters
Select one or more countries and year-month periods. Every chart updates instantly via Streamlit's caching layer.

### 2 · RFM Segmentation
Customers are scored on Recency, Frequency and Monetary value, then grouped into five actionable segments. The table alongside the chart shows average RFM values per group.

### 3 · K-Means Clustering
Drag the slider to choose 2–8 clusters. The algorithm runs on five normalised features (Recency, Frequency, Monetary, Total Quantity, Unique Products). A PCA scatter plot gives a 2-D view of how well the clusters separate.

---

<div align="center">

Made by **[raselmian03](https://github.com/raselmian03)**

</div>
