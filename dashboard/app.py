"""
Gabifit Dashboard — Main Entry Point

Streamlit multi-page app for Dominican Republic fitness coaching
competitive intelligence.

Run with:
  streamlit run dashboard/app.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from dashboard.components.data_loader import data_ready, data_status

st.set_page_config(
    page_title="Gabifit — DR Fitness Market Intelligence",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Header ---
st.title("🏋️ Gabifit — DR Fitness Market Intelligence")
st.markdown(
    "Competitive intelligence dashboard for the Dominican Republic fitness coaching market. "
    "Data sourced from Instagram, TikTok, and coach websites."
)

# --- Data readiness check ---
if not data_ready():
    st.error(
        "**No processed data found.** Run the data pipeline first:\n\n"
        "```bash\n"
        "# 1. Add your coaches to seeds/coach_usernames.py\n"
        "# 2. Add your Apify token to .env: APIFY_TOKEN=apify_api_xxx\n"
        "# 3. Collect data:\n"
        "python run_collection.py\n\n"
        "# 4. Process data:\n"
        "python run_processing.py\n\n"
        "# 5. Reload this page\n"
        "```"
    )
    st.stop()

# --- Sidebar status ---
st.sidebar.title("Gabifit Dashboard")
st.sidebar.markdown("---")

status = data_status()
st.sidebar.markdown("**Data Files**")
for filename, present in status.items():
    icon = "✅" if present else "❌"
    st.sidebar.markdown(f"{icon} `{filename}`")
st.sidebar.markdown("---")
st.sidebar.info("Use the pages menu (top left) to navigate between sections.")

# --- Quick summary on home page ---
from dashboard.components.data_loader import load_coaches_master

df = load_coaches_master()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Coaches Tracked", len(df))
    with col2:
        total_followers = int(df["total_social_followers"].sum()) if "total_social_followers" in df.columns else 0
        st.metric("Total Followers", f"{total_followers:,}")
    with col3:
        avg_eng = df["ig_engagement_rate"].mean() if "ig_engagement_rate" in df.columns else 0
        st.metric("Avg IG Engagement", f"{avg_eng:.1f}%" if avg_eng else "N/A")
    with col4:
        with_pricing = df["min_price_usd"].notna().sum() if "min_price_usd" in df.columns else 0
        st.metric("Coaches With Pricing", f"{with_pricing}/{len(df)}")

    st.markdown("---")
    st.subheader("Navigate to a section:")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### 💰 Pricing\nCompare coaching prices across the DR market.")
    with c2:
        st.markdown("### 📱 Social Media\nFollowers, engagement rates, platform breakdown.")
    with c3:
        st.markdown("### 🛎️ Services\nWhat each coach offers and market gaps.")
    with c4:
        st.markdown("### 🔗 Funnels\nHow coaches attract and convert clients.")
