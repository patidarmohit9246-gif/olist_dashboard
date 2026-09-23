# E-commerce Sales & Customer Insights Dashboard

An interactive Streamlit dashboard analyzing the Olist Brazilian E-Commerce dataset (~110K orders, 2016-2018).

## Live Demo
[Add your deployed link here once hosted]

## What it does
- Cleans and merges 5 raw CSV tables (orders, items, customers, products, categories)
- Calculates KPIs: Revenue, Orders, Average Order Value, Repeat-Customer Rate
- Monthly revenue trend analysis
- Category and state-level revenue breakdown
- Cohort retention analysis (heatmap)
- RFM (Recency, Frequency, Monetary) customer segmentation
- Interactive filters: date range, state, category
- Data-backed business recommendations

## Key Findings
- Repeat-customer rate is only ~3%
- Sao Paulo drives ~38% of total revenue
- Revenue peaked in November 2017 (Black Friday) and plateaued through 2018
- Cohort retention stays below 1% in every month post-purchase

## Tools Used
- Python (pandas, plotly)
- Streamlit
- Dataset: [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## How to run locally
```
pip install streamlit pandas plotly
streamlit run app.py
```
