"""
Sidebar filter widgets shared across all dashboard pages.

Returns a filtered DataFrame based on user selections.
"""

import streamlit as st
import pandas as pd


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered coaches DataFrame."""

    st.sidebar.header("Filters")

    # --- Platform filter ---
    platform_options = ["All", "Instagram", "TikTok", "Both platforms"]
    selected_platform = st.sidebar.selectbox("Platform", platform_options)

    # --- Minimum followers ---
    max_followers = int(df["total_social_followers"].max()) if "total_social_followers" in df.columns and len(df) > 0 else 100000
    min_followers = st.sidebar.slider(
        "Min total followers",
        min_value=0,
        max_value=max(max_followers, 1000),
        value=0,
        step=500,
        format="%d",
    )

    # --- Service type filter ---
    service_columns = {
        "Online coaching": "offers_online",
        "In-person training": "offers_in_person",
        "Nutrition plan": "offers_nutrition",
        "Transformation program": "offers_transformation",
        "Group classes": "offers_group",
    }
    available_services = {
        label: col
        for label, col in service_columns.items()
        if col in df.columns
    }
    selected_services = st.sidebar.multiselect(
        "Services offered",
        options=list(available_services.keys()),
        default=[],
    )

    # --- Has pricing filter ---
    only_with_pricing = st.sidebar.checkbox("Only coaches with pricing info", value=False)

    # --- Apply filters ---
    filtered = df.copy()

    if selected_platform == "Instagram":
        filtered = filtered[filtered.get("primary_platform", pd.Series("instagram")) == "instagram"]
    elif selected_platform == "TikTok":
        filtered = filtered[filtered.get("primary_platform", pd.Series("tiktok")) == "tiktok"]
    elif selected_platform == "Both platforms":
        filtered = filtered[filtered.get("primary_platform", pd.Series("both")) == "both"]

    if "total_social_followers" in filtered.columns:
        filtered = filtered[filtered["total_social_followers"] >= min_followers]

    for label in selected_services:
        col = available_services[label]
        if col in filtered.columns:
            filtered = filtered[filtered[col] == True]

    if only_with_pricing and "min_price_usd" in filtered.columns:
        filtered = filtered[filtered["min_price_usd"].notna()]

    return filtered
