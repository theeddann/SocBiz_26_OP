import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
page_title="EV Charging Network Optimization",
page_icon="⚡",
layout="wide"
)

@st.cache_data
def load_data():
    pricing_df = pd.read_csv(
        "processed/dynamic_pricing_demo.csv"
    )

    monitoring_df = pd.read_csv(
        "processed/monitoring_output_demo.csv"
    )

    monitoring_results = pd.read_csv(
        "processed/monitoring_results.csv"
    )

    return pricing_df, monitoring_df, monitoring_results

pricing_df, monitoring_df, monitoring_results = load_data()

st.sidebar.header("Filters")

selected_status = st.sidebar.multiselect(
"Station Status",
pricing_df["status"].unique(),
default=pricing_df["status"].unique()
)

selected_hour = st.sidebar.slider(
"Hour Range",
0,
23,
(0, 23)
)

filtered_df = pricing_df[
(
pricing_df["status"].isin(selected_status)
)
&
(
pricing_df["hour"].between(
selected_hour[0],
selected_hour[1]
)
)
]

revenue_gain_pct = float(
monitoring_results.loc[
monitoring_results["Metric"] == "Revenue Gain %",
"Value"
].values[0]
)

avg_dynamic_price = float(
monitoring_results.loc[
monitoring_results["Metric"] == "Average Dynamic Price",
"Value"
].values[0]
)

charger_utilization = float(
monitoring_results.loc[
monitoring_results["Metric"] == "Charger Utilization %",
"Value"
].values[0]
)

waiting_time_reduction = float(
monitoring_results.loc[
monitoring_results["Metric"] == "Waiting Time Reduction %",
"Value"
].values[0]
)

customer_response_rate = float(
monitoring_results.loc[
monitoring_results["Metric"] == "Customer Response Rate %",
"Value"
].values[0]
)

st.title("⚡ EV Charging Network Optimization")

st.info(
"""
This AI-powered platform forecasts EV charging demand,
optimizes charging prices using dynamic pricing,
and monitors charger utilization in real time.

Key Result:
Revenue increased by 16.44% while encouraging
off-peak charging behaviour and reducing congestion.
"""
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
"Revenue Gain",
f"{revenue_gain_pct:.2f}%"
)

c2.metric(
"Avg Price",
f"₹{avg_dynamic_price:.2f}"
)

c3.metric(
"Utilization",
f"{charger_utilization:.2f}%"
)

c4.metric(
"Wait Reduction",
f"{waiting_time_reduction:.2f}%"
)

c5.metric(
"Response Rate",
f"{customer_response_rate:.2f}%"
)

st.divider()

st.header("Demand Prediction Agent")

avg_demand = filtered_df["predicted_demand"].mean()

peak_hour = (
filtered_df
.groupby("hour")["predicted_demand"]
.mean()
.idxmax()
)

st.success(
f"""
Average Predicted Demand: {avg_demand:.2f}

Peak Demand Hour: {peak_hour}:00
"""
)

hourly_demand = (
filtered_df
.groupby("hour")["predicted_demand"]
.mean()
.reset_index()
)

fig = px.line(
hourly_demand,
x="hour",
y="predicted_demand",
title="Predicted EV Charging Demand by Hour"
)

st.plotly_chart(
fig,
use_container_width=True
)

st.divider()

st.header("Dynamic Pricing Agent")

avg_price = filtered_df["new_dynamic_price"].mean()
max_price = filtered_df["new_dynamic_price"].max()
min_price = filtered_df["new_dynamic_price"].min()

c1, c2, c3 = st.columns(3)

c1.metric(
"Average Price",
f"₹{avg_price:.2f}"
)

c2.metric(
"Maximum Price",
f"₹{max_price:.2f}"
)

c3.metric(
"Minimum Price",
f"₹{min_price:.2f}"
)

price_by_hour = (
filtered_df
.groupby("hour")["new_dynamic_price"]
.mean()
.reset_index()
)

fig = px.line(
price_by_hour,
x="hour",
y="new_dynamic_price",
title="Dynamic Price Variation by Hour"
)

st.plotly_chart(
fig,
use_container_width=True
)

st.subheader("Revenue Comparison")

baseline_revenue = filtered_df["baseline_revenue"].sum()

dynamic_revenue = filtered_df["new_revenue_with_idle"].sum()

comparison = pd.DataFrame({
"Type": [
"Baseline Revenue",
"Dynamic Revenue"
],
"Revenue": [
baseline_revenue,
dynamic_revenue
]
})

fig = px.bar(
comparison,
x="Type",
y="Revenue",
color="Type",
title="Baseline vs Dynamic Revenue"
)

st.plotly_chart(
fig,
use_container_width=True
)

st.success(
f"""
Dynamic pricing increased revenue by
{revenue_gain_pct:.2f}% and generated
₹{(dynamic_revenue - baseline_revenue):,.0f}
additional revenue.
"""
)

st.divider()

st.header("Monitoring Agent")

status_counts = (
filtered_df["status"]
.value_counts()
.reset_index()
)

status_counts.columns = [
"Status",
"Count"
]

fig = px.bar(
status_counts,
x="Status",
y="Count",
color="Status",
title="Station Status Summary"
)

st.plotly_chart(
fig,
use_container_width=True
)

fig = px.histogram(
filtered_df,
x="utilization_rate",
nbins=40,
title="Utilization Distribution"
)

st.plotly_chart(
fig,
use_container_width=True
)

st.subheader("Top Congested Stations")

top_stations = (
filtered_df
.groupby("station_id")["queue_proxy"]
.mean()
.sort_values(ascending=False)
.head(10)
)

st.dataframe(top_stations)

st.divider()

st.header("Monitoring Output Preview")

show_cols = [
"station_id",
"hour",
"predicted_demand",
"new_dynamic_price",
"idle_penalty",
"status"
]

st.dataframe(
filtered_df[show_cols].head(20),
use_container_width=True
)

st.divider()

st.header("Final Results")

st.dataframe(
monitoring_results,
use_container_width=True
)

st.divider()

st.header("Recommendations")

recommendations = []

if revenue_gain_pct > 10:
    recommendations.append(
        "Dynamic pricing successfully increased revenue."
    )

if charger_utilization < 20:
    recommendations.append(
        "Low charger utilization detected. Promote off-peak charging."
    )

if waiting_time_reduction > 10:
    recommendations.append(
        "Queue management strategy is effective."
    )

if customer_response_rate < 50:
    recommendations.append(
        "Consider customer incentives for better adoption."
    )

for rec in recommendations:
    st.write("•", rec)

csv = filtered_df.to_csv(index=False)

st.download_button(
label="Download Results CSV",
data=csv,
file_name="ev_network_results.csv",
mime="text/csv"
)
