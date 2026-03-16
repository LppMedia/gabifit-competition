"""
Page 2: Social Media Presence

Instagram and TikTok follower counts, engagement rates, and platform breakdown.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st
import pandas as pd
from dashboard.components.data_loader import load_coaches_master
from dashboard.components.filters import apply_sidebar_filters
from dashboard.components import charts

st.set_page_config(page_title="Social Media — Gabifit", layout="wide")

st.title("📱 Social Media Presence")
st.markdown("Follower counts, engagement rates, and platform distribution across DR fitness coaches.")

df = load_coaches_master()

if df.empty:
    st.warning("No data available. Run the data pipeline first.")
    st.stop()

filtered = apply_sidebar_filters(df)

# --- Key Metrics ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Coaches Tracked", len(filtered))
with col2:
    total_followers = int(filtered["total_social_followers"].sum()) if "total_social_followers" in filtered.columns else 0
    st.metric("Total Combined Followers", f"{total_followers:,}")
with col3:
    avg_eng = filtered["ig_engagement_rate"].mean() if "ig_engagement_rate" in filtered.columns else None
    st.metric("Avg IG Engagement Rate", f"{avg_eng:.1f}%" if avg_eng and not pd.isna(avg_eng) else "N/A")
with col4:
    avg_views = filtered["tt_avg_views"].mean() if "tt_avg_views" in filtered.columns else None
    st.metric("Avg TikTok Views/Video", f"{avg_views:,.0f}" if avg_views and not pd.isna(avg_views) else "N/A")

st.markdown("---")

# --- Scatter + Platform Pie ---
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Followers vs Engagement Rate")
    fig = charts.followers_vs_engagement(filtered)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Platform Distribution")
    fig = charts.platform_distribution_pie(filtered)
    st.plotly_chart(fig, use_container_width=True)

# --- Followers grouped bar ---
st.subheader("Instagram vs TikTok Followers per Coach")
fig = charts.followers_bar_comparison(filtered)
st.plotly_chart(fig, use_container_width=True)

# --- Top 10 Table ---
st.markdown("---")
st.subheader("Top 10 Coaches by Total Followers")

table_cols = ["full_name", "total_social_followers", "ig_followers", "tt_followers",
              "ig_engagement_rate", "tt_view_to_follower_ratio", "primary_platform"]
available_cols = [c for c in table_cols if c in filtered.columns]

if available_cols and not filtered.empty:
    top10 = filtered[available_cols].sort_values("total_social_followers", ascending=False).head(10)
    rename_map = {
        "full_name": "Coach",
        "total_social_followers": "Total Followers",
        "ig_followers": "IG Followers",
        "tt_followers": "TT Followers",
        "ig_engagement_rate": "IG Engagement %",
        "tt_view_to_follower_ratio": "TT View/Follower",
        "primary_platform": "Platform",
    }
    top10 = top10.rename(columns={k: v for k, v in rename_map.items() if k in top10.columns})
    st.dataframe(top10, use_container_width=True)
