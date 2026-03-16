"""
Page 4: Marketing Funnels

How Dominican Republic fitness coaches attract and convert clients.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st
import pandas as pd
from dashboard.components.data_loader import load_coaches_master
from dashboard.components.filters import apply_sidebar_filters
from dashboard.components import charts

st.set_page_config(page_title="Funnels — Gabifit", layout="wide")

st.title("🔗 Marketing Funnels")
st.markdown("How coaches attract clients — their CTAs, lead magnets, and funnel sophistication.")

df = load_coaches_master()

if df.empty:
    st.warning("No data available. Run the data pipeline first.")
    st.stop()

filtered = apply_sidebar_filters(df)

# --- Key Metrics ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    wa_count = int(filtered["has_whatsapp_cta"].fillna(False).sum()) if "has_whatsapp_cta" in filtered.columns else 0
    st.metric("Using WhatsApp CTA", f"{wa_count}/{len(filtered)}")
with col2:
    lt_count = int(filtered["uses_linktree"].fillna(False).sum()) if "uses_linktree" in filtered.columns else 0
    st.metric("Using Linktree", f"{lt_count}/{len(filtered)}")
with col3:
    web_count = int(filtered["has_website"].fillna(False).sum()) if "has_website" in filtered.columns else 0
    st.metric("Have a Website", f"{web_count}/{len(filtered)}")
with col4:
    lm_count = int(filtered["has_lead_magnet"].fillna(False).sum()) if "has_lead_magnet" in filtered.columns else 0
    st.metric("Have Lead Magnet", f"{lm_count}/{len(filtered)}")

st.markdown("---")

# --- Sankey ---
st.subheader("Funnel Flow: Platform -> CTA -> Conversion")
fig = charts.funnel_sankey(filtered)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- CTA + Engagement ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("CTA Channel Distribution")
    fig = charts.cta_distribution_bar(filtered)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Engagement Rate vs Lead Magnet")
    fig = charts.engagement_vs_lead_magnet(filtered)
    st.plotly_chart(fig, use_container_width=True)

# --- Funnel Score Leaderboard ---
st.markdown("---")
st.subheader("Funnel Sophistication Score — Top 10 Coaches")
st.caption(
    "Score (0–8): website (+2), lead magnet (+2), Linktree (+1), WhatsApp CTA (+1), "
    "IG engagement > 3% (+1), TikTok view ratio > 2x (+1)"
)

score_cols = ["full_name", "funnel_score", "top_cta_channel", "has_website",
              "has_lead_magnet", "uses_linktree", "ig_engagement_rate", "tt_view_to_follower_ratio"]
available_cols = [c for c in score_cols if c in filtered.columns]

if "funnel_score" in filtered.columns and not filtered.empty:
    top10 = filtered[available_cols].sort_values("funnel_score", ascending=False).head(10)
    rename_map = {
        "full_name": "Coach",
        "funnel_score": "Score",
        "top_cta_channel": "Primary CTA",
        "has_website": "Website",
        "has_lead_magnet": "Lead Magnet",
        "uses_linktree": "Linktree",
        "ig_engagement_rate": "IG Eng %",
        "tt_view_to_follower_ratio": "TT View Ratio",
    }
    top10 = top10.rename(columns={k: v for k, v in rename_map.items() if k in top10.columns})
    st.dataframe(top10, use_container_width=True)
else:
    st.info("Funnel score not available. Run data processing to compute it.")

# --- Insights Summary ---
st.markdown("---")
st.subheader("Key Insights")

insights = []

if "top_cta_channel" in filtered.columns:
    dominant_cta = filtered["top_cta_channel"].value_counts().idxmax() if not filtered.empty else "N/A"
    insights.append(f"**Most common CTA:** {dominant_cta}")

if "has_lead_magnet" in filtered.columns:
    pct_magnet = filtered["has_lead_magnet"].fillna(False).mean() * 100
    insights.append(
        f"**{pct_magnet:.0f}%** of coaches use a lead magnet — "
        + ("high adoption" if pct_magnet > 50 else "large opportunity to stand out")
    )

if "has_website" in filtered.columns:
    pct_web = filtered["has_website"].fillna(False).mean() * 100
    insights.append(
        f"**{pct_web:.0f}%** of coaches have a website — "
        + ("most have web presence" if pct_web > 60 else "many rely only on social media")
    )

if "ig_engagement_rate" in filtered.columns:
    avg_eng = filtered["ig_engagement_rate"].mean()
    if not pd.isna(avg_eng):
        bench = "above" if avg_eng > 3 else "below"
        insights.append(f"Average IG engagement rate is **{avg_eng:.1f}%** ({bench} the 3% industry benchmark)")

for insight in insights:
    st.markdown(f"- {insight}")
