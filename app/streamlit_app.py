# Imports

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# load data and mapping

df = pd.read_csv("data/Melbourne_clean.csv")
df["date"] = pd.to_datetime(df["date"])

type_labels = {"h": "House", "u": "Unit", "t": "Townhouse"}

df["type_full"] = df["type"].map(type_labels)

st.set_page_config(page_title="Melbourne Real Estate Dashboard", layout="wide")


# title and filters

st.title("Melbourne Real Estate Market Dashboard")
st.markdown("Interactive dashboard to explore housing market trends in Melbourne.")

st.sidebar.header("Filters")

suburb = st.sidebar.multiselect(
    "Select Suburb(s)", options=sorted(df["suburb"].unique()), default=None
)
property_type = st.sidebar.multiselect(
    "Select Property Type(s)", options=df["type_full"].unique(), default=None
)
date_range = st.sidebar.date_input(
    "Select Date Range", [df["date"].min(), df["date"].max()]
)

filtered_df = df.copy()
if suburb:
    filtered_df = filtered_df[filtered_df["suburb"].isin(suburb)]
if property_type:
    filtered_df = filtered_df[filtered_df["type_full"].isin(property_type)]
filtered_df = filtered_df[
    (filtered_df["date"] >= pd.to_datetime(date_range[0]))
    & (filtered_df["date"] <= pd.to_datetime(date_range[1]))
]

# Kpi display

st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Listings", f"{len(filtered_df)}")
col2.metric("Average Price", f"${filtered_df['price'].mean():,.0f}")
col3.metric("Median Price", f"${filtered_df['price'].mean():,.0f}")

# Visuals

st.subheader("Price Distribution by Property Type")
box_fig = px.box(
    filtered_df,
    x="type_full",
    y="price",
    points="outliers",
    color="type_full",
    labels={"type_full": "Property Type", "price": "Price"},
)
box_fig.update_layout(yaxis_tickformat=".2s")
st.plotly_chart(box_fig, use_container_width=True)

# Map

st.subheader("Average Price by Suburb")

map_df = (
    filtered_df.groupby("suburb")
    .agg({"lattitude": "mean", "longtitude": "mean", "price": "mean"})
    .reset_index()
)

map_fig = px.scatter_mapbox(
    map_df,
    lat="lattitude",
    lon="longtitude",
    size="price",
    color="price",
    hover_name="suburb",
    color_continuous_scale="Viridis",
    zoom=9,
    mapbox_style="carto-positron",
    size_max=20,
    height=700,
)
st.plotly_chart(map_fig, use_container_width=True)
