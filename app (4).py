import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

# Sample dataset
companies_data = [
    {"Company": "Alpha Energy", "Industry": "Energy", "Region": "Europe", "MarketCap": 2000, "RevenueGrowth": 12.5, "ProfitMargin": 8.2, "ROE": 16.3, "ESGScore": 75, "SharpeRatio": 1.2, "Beta": 0.95, "EPS": 1.25},
    {"Company": "Beta Power", "Industry": "Energy", "Region": "Europe", "MarketCap": 1500, "RevenueGrowth": 10.1, "ProfitMargin": 7.5, "ROE": 14.8, "ESGScore": 80, "SharpeRatio": 1.0, "Beta": 1.10, "EPS": 1.10},
    {"Company": "Gamma Oil", "Industry": "Energy", "Region": "Europe", "MarketCap": 1800, "RevenueGrowth": 15.0, "ProfitMargin": 9.0, "ROE": 17.5, "ESGScore": 70, "SharpeRatio": 1.1, "Beta": 1.05, "EPS": 1.30},
    {"Company": "Delta Renewables", "Industry": "Energy", "Region": "Europe", "MarketCap": 1600, "RevenueGrowth": 18.2, "ProfitMargin": 10.5, "ROE": 19.0, "ESGScore": 85, "SharpeRatio": 1.3, "Beta": 0.90, "EPS": 1.45},
    {"Company": "Epsilon Gas", "Industry": "Energy", "Region": "Europe", "MarketCap": 1400, "RevenueGrowth": 9.8, "ProfitMargin": 6.9, "ROE": 13.2, "ESGScore": 65, "SharpeRatio": 0.9, "Beta": 1.20, "EPS": 0.95},
    {"Company": "Zeta Solar", "Industry": "Energy", "Region": "Europe", "MarketCap": 1700, "RevenueGrowth": 16.0, "ProfitMargin": 11.0, "ROE": 20.1, "ESGScore": 90, "SharpeRatio": 1.4, "Beta": 0.85, "EPS": 1.60},
    {"Company": "Omega Tech", "Industry": "Technology", "Region": "North America", "MarketCap": 5000, "RevenueGrowth": 25.0, "ProfitMargin": 18.0, "ROE": 22.5, "ESGScore": 88, "SharpeRatio": 1.6, "Beta": 1.00, "EPS": 2.10},
    {"Company": "Sigma Health", "Industry": "Healthcare", "Region": "Asia", "MarketCap": 3000, "RevenueGrowth": 20.0, "ProfitMargin": 15.0, "ROE": 21.0, "ESGScore": 82, "SharpeRatio": 1.5, "Beta": 1.10, "EPS": 1.80},
    {"Company": "Lambda Retail", "Industry": "Retail", "Region": "Europe", "MarketCap": 2500, "RevenueGrowth": 14.0, "ProfitMargin": 9.5, "ROE": 17.0, "ESGScore": 78, "SharpeRatio": 1.2, "Beta": 1.15, "EPS": 1.35}
]

# Convert to DataFrame
df = pd.DataFrame(companies_data)

st.set_page_config(page_title="AI Stock Selector", layout="wide")
st.title("📈 AI-Powered Stock Selector")

# Sidebar filters
st.sidebar.header("🔍 Filter Criteria")
industry = st.sidebar.selectbox("Select Industry", sorted(df["Industry"].unique()))
region = st.sidebar.selectbox("Select Region", sorted(df["Region"].unique()))
market_cap_min = st.sidebar.slider("Minimum Market Cap", int(df["MarketCap"].min()), int(df["MarketCap"].max()), int(df["MarketCap"].min()))
market_cap_max = st.sidebar.slider("Maximum Market Cap", int(df["MarketCap"].min()), int(df["MarketCap"].max()), int(df["MarketCap"].max()))
roe_min = st.sidebar.slider("Minimum ROE", 0.0, 30.0, 15.0)
esg_min = st.sidebar.slider("Minimum ESG Score", 0, 100, 70)

# Apply filters
filtered_df = df[
    (df["Industry"] == industry) &
    (df["Region"] == region) &
    (df["MarketCap"] >= market_cap_min) &
    (df["MarketCap"] <= market_cap_max) &
    (df["ROE"] >= roe_min) &
    (df["ESGScore"] >= esg_min)
]

# Scoring mechanism
weights = {
    "RevenueGrowth": 0.25,
    "ProfitMargin": 0.25,
    "ROE": 0.25,
    "ESGScore": 0.25
}

for metric in weights:
    filtered_df[metric + "_Norm"] = (filtered_df[metric] - filtered_df[metric].min()) / (filtered_df[metric].max() - filtered_df[metric].min())

filtered_df["Score"] = sum(filtered_df[metric + "_Norm"] * weight for metric, weight in weights.items())

ranked_df = filtered_df.sort_values(by="Score", ascending=False)[["Company", "Industry", "Region", "MarketCap", "RevenueGrowth", "ProfitMargin", "ROE", "ESGScore", "SharpeRatio", "Beta", "EPS", "Score"]]

st.subheader("🏆 Top Ranked Companies")
st.dataframe(ranked_df)

# Score breakdown chart
st.subheader("📊 Score Breakdown by Company")
if not ranked_df.empty:
    score_components = [metric + "_Norm" for metric in weights]
    score_df = filtered_df[["Company"] + score_components].set_index("Company")
    score_df = score_df.reset_index().melt(id_vars="Company", var_name="Metric", value_name="Normalized Score")

    chart = alt.Chart(score_df).mark_bar().encode(
        x=alt.X("Company:N", title="Company"),
        y=alt.Y("Normalized Score:Q", title="Score"),
        color="Metric:N",
        tooltip=["Company", "Metric", "Normalized Score"]
    ).properties(width=800)

    st.altair_chart(chart, use_container_width=True)

# EPS trend chart
st.subheader("📈 EPS Trends Over Time")
eps_data = {
    "Quarter": ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023"] * len(filtered_df),
    "Company": sum([[c] * 4 for c in filtered_df["Company"].tolist()], []),
    "EPS": sum([[row["EPS"] - 0.15, row["EPS"] - 0.10, row["EPS"] - 0.05, row["EPS"]] for _, row in filtered_df.iterrows()], [])
}

eps_df = pd.DataFrame(eps_data)
fig = px.line(eps_df, x="Quarter", y="EPS", color="Company", markers=True, title="EPS Trends Over Time")
st.plotly_chart(fig, use_container_width=True)

# Company profile cards
st.subheader("📋 Company Profiles")
for _, row in ranked_df.iterrows():
    with st.expander(row["Company"]):
        st.write(f"**Industry:** {row['Industry']}")
        st.write(f"**Region:** {row['Region']}")
        st.write(f"**Market Cap:** {row['MarketCap']} M")
        st.write(f"**Revenue Growth:** {row['RevenueGrowth']}%")
        st.write(f"**Profit Margin:** {row['ProfitMargin']}%")
        st.write(f"**ROE:** {row['ROE']}%")
        st.write(f"**ESG Score:** {row['ESGScore']}")
        st.write(f"**Sharpe Ratio:** {row['SharpeRatio']}")
        st.write(f"**Beta:** {row['Beta']}")
        st.write(f"**EPS (Last Quarter):** {row['EPS']}")
        st.write(f"**Composite Score:** {round(row['Score'], 2)}")

# Download button
st.subheader("📥 Export Results")
csv = ranked_df.to_csv(index=False)
st.download_button("Download Ranked Companies as CSV", csv, "ranked_companies.csv", "text/csv")

st.markdown("---")
st.markdown("**Note:** Scores are calculated using a weighted average of normalized performance metrics. Sharpe Ratio, Beta, and EPS are shown for reference only.")