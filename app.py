import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E-commerce Insights", layout="wide")

# --- Custom colorful styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    background-attachment: fixed;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #240046 0%, #3c096c 100%);
}
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 20px;
    border-radius: 15px;
    color: white;
    box-shadow: 0 4px 15px rgba(106, 17, 203, 0.5);
}
div[data-testid="stMetric"] label { color: #e0e0e0 !important; }
h1 {
    color: #ff6b6b;
    text-shadow: 2px 2px 8px rgba(255, 107, 107, 0.4);
}
h2, h3 { color: #4ecdc4; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 15px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)
st.title("E-commerce Sales & Customer Insights Dashboard")

df = pd.read_csv("data/cleaned_orders.csv")
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["Month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

state_names = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapa", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceara", "DF": "Distrito Federal", "ES": "Espirito Santo",
    "GO": "Goias", "MA": "Maranhao", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Para", "PB": "Paraiba", "PR": "Parana",
    "PE": "Pernambuco", "PI": "Piaui", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondonia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "Sao Paulo", "SE": "Sergipe", "TO": "Tocantins"
}
df["state_name"] = df["customer_state"].map(state_names)

# --- Sidebar filters ---
st.sidebar.header("Filters")

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

state_options = sorted(df["state_name"].unique())
selected_state_names = st.sidebar.multiselect("State", state_options, default=state_options)

categories = sorted(df["product_category_name_english"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

start_date, end_date = date_range
mask = (
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["state_name"].isin(selected_state_names)) &
    (df["product_category_name_english"].isin(selected_categories))
)
filtered = df[mask]

# --- KPIs ---
revenue = filtered["price"].sum()
orders = filtered["order_id"].nunique()
aov = revenue / orders if orders > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"R$ {revenue:,.0f}")
col2.metric("Total Orders", f"{orders:,}")
col3.metric("Avg Order Value", f"R$ {aov:,.2f}")

st.markdown("---")

# --- Two charts side by side ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Monthly Revenue Trend")
    monthly = filtered.groupby("Month")["price"].sum().reset_index()
    fig = px.line(monthly, x="Month", y="price", markers=True, color_discrete_sequence=["#00cec9"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Revenue by Category (Top 10)")
    cat_rev = filtered.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_cat = px.bar(cat_rev, x="product_category_name_english", y="price", color="price", color_continuous_scale="Plasma")
    fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_cat, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Revenue by State (Top 10)")
    state_rev = filtered.groupby("state_name")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_state = px.bar(state_rev, x="state_name", y="price", color="price", color_continuous_scale="Viridis")
    fig_state.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_state, use_container_width=True)

with chart_col4:
    st.subheader("Cohort Retention (%)")
    cohort_df = filtered.copy()
    cohort_df["cohort_month"] = cohort_df.groupby("customer_unique_id")["order_purchase_timestamp"].transform("min").dt.to_period("M")
    cohort_df["order_month"] = cohort_df["order_purchase_timestamp"].dt.to_period("M")
    cohort_df["months_since"] = (cohort_df["order_month"].dt.year - cohort_df["cohort_month"].dt.year) * 12 + (cohort_df["order_month"].dt.month - cohort_df["cohort_month"].dt.month)

    cohort_counts = cohort_df.groupby(["cohort_month", "months_since"])["customer_unique_id"].nunique().reset_index()
    cohort_pivot = cohort_counts.pivot_table(index="cohort_month", columns="months_since", values="customer_unique_id")

    cohort_size = cohort_pivot[0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    retention.index = retention.index.astype(str)

    retention_display = retention.iloc[:, 1:13].round(1)
    retention_display = retention_display.dropna(how="all")

    fig_heatmap = px.imshow(
        retention_display,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Magma",
        labels=dict(x="Months since first purchase", y="Cohort month", color="Retention %")
    )
    fig_heatmap.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# --- Recommendations ---
st.subheader("Recommendations")
st.markdown("""
1. **Repeat-customer rate is only ~3%.** Most shoppers buy once and never return. Post-purchase email campaigns or loyalty discounts could be tested to improve retention.
2. **Revenue is concentrated in a few states.** Sao Paulo alone drives ~38% of revenue. Expansion or targeted marketing in mid-tier states (Rio Grande do Sul, Parana) could diversify growth.
3. **Growth slowed sharply after November 2017 (Black Friday peak).** 2018 revenue plateaued between R$ 8-9.8 lakh/month instead of continuing to grow. Marketing spend timing should be reviewed.
4. **High-ticket categories like computers have few orders but high average value.** Only 177 orders averaged R$ 1,235 each. Promoting this category to a wider audience could unlock revenue with minimal extra marketing spend.
5. **Cohort retention stays below 1% every month with no improving trend.** This suggests no current re-engagement strategy is working; a structured retention campaign (email, coupons) is worth testing and measuring.
""")