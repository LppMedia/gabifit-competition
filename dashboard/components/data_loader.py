"""
Cached CSV loaders for the Streamlit dashboard.

All functions use @st.cache_data so CSVs are read from disk only once
per Streamlit session (fast subsequent page navigations).
"""

import os
import json
import pandas as pd
import streamlit as st

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


def _path(filename: str) -> str:
    return os.path.join(PROCESSED_DIR, filename)


def _file_exists(filename: str) -> bool:
    return os.path.exists(_path(filename))


@st.cache_data
def load_coaches_master() -> pd.DataFrame:
    if not _file_exists("coaches_master.csv"):
        return pd.DataFrame()
    df = pd.read_csv(_path("coaches_master.csv"))
    # Ensure numeric columns are the right type
    for col in ["ig_followers", "tt_followers", "total_social_followers"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in ["ig_engagement_rate", "tt_engagement_rate", "tt_view_to_follower_ratio",
                "min_price_usd", "max_price_usd", "ig_avg_likes", "ig_avg_comments"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["has_website", "has_lead_magnet", "has_whatsapp_cta", "uses_linktree",
                "offers_online", "offers_in_person", "offers_nutrition",
                "offers_transformation", "offers_group", "ig_verified"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    return df


@st.cache_data
def load_instagram_posts() -> pd.DataFrame:
    if not _file_exists("instagram_posts_clean.csv"):
        return pd.DataFrame()
    df = pd.read_csv(_path("instagram_posts_clean.csv"))
    for col in ["likes", "comments"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    return df


@st.cache_data
def load_tiktok_videos() -> pd.DataFrame:
    if not _file_exists("tiktok_videos_clean.csv"):
        return pd.DataFrame()
    df = pd.read_csv(_path("tiktok_videos_clean.csv"))
    for col in ["play_count", "like_count", "comment_count", "share_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data
def load_services_pricing() -> pd.DataFrame:
    if not _file_exists("services_pricing.csv"):
        return pd.DataFrame()
    df = pd.read_csv(_path("services_pricing.csv"))
    for col in ["min_price_usd", "max_price_usd"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")


@st.cache_data
def load_raw_instagram_profiles() -> list:
    path = os.path.join(RAW_DIR, "instagram_profiles.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_raw_instagram_posts() -> list:
    path = os.path.join(RAW_DIR, "instagram_posts.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_all_images_b64() -> dict:
    """Load all profile + post images as base64 in one cached call."""
    import base64
    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
    result = {}
    for folder in ("profiles", "posts"):
        folder_path = os.path.join(base, folder)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                fpath = os.path.join(folder_path, fname)
                key = f"data/images/{folder}/{fname}"
                with open(fpath, "rb") as f:
                    result[key] = base64.b64encode(f.read()).decode()
    return result


def get_local_image_b64(rel_path: str, image_cache: dict = None) -> str:
    """Return base64-encoded image string. Pass image_cache from load_all_images_b64()."""
    if image_cache is not None:
        return image_cache.get(rel_path, "")
    # Fallback: direct read (slow, uncached)
    import base64
    full_path = os.path.join(os.path.dirname(__file__), "..", "..", rel_path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def data_ready() -> bool:
    """True if the minimum required data for the dashboard is present."""
    return _file_exists("coaches_master.csv")


def data_status() -> dict:
    """Return which data files are present."""
    files = ["coaches_master.csv", "instagram_posts_clean.csv",
             "tiktok_videos_clean.csv", "services_pricing.csv"]
    return {f: _file_exists(f) for f in files}
