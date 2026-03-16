"""
Process raw TikTok data into clean CSVs.

Inputs:
  data/raw/tiktok_profiles.json
  data/raw/tiktok_videos.json

Outputs:
  data/processed/tiktok_videos_clean.csv
  (profile metrics returned for merge_coaches.py)
"""

import json
import os
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def _safe_int(val, default=0) -> int:
    try:
        return int(val or default)
    except (TypeError, ValueError):
        return default


def process_profiles(profiles: list) -> pd.DataFrame:
    rows = []
    for p in profiles:
        username = (
            p.get("uniqueId")
            or p.get("username")
            or p.get("authorMeta", {}).get("name", "unknown")
        )
        followers = _safe_int(
            p.get("followers")
            or p.get("followerCount")
            or p.get("stats", {}).get("followerCount")
            or p.get("authorMeta", {}).get("fans")
        )
        total_likes = _safe_int(
            p.get("heartCount")
            or p.get("heart")
            or p.get("stats", {}).get("heartCount")
            or p.get("authorMeta", {}).get("heart")
        )
        video_count = _safe_int(
            p.get("videoCount")
            or p.get("video")
            or p.get("stats", {}).get("videoCount")
            or p.get("authorMeta", {}).get("video")
        )
        bio = (
            p.get("signature")
            or p.get("bio")
            or p.get("desc")
            or p.get("authorMeta", {}).get("signature", "")
        )
        bio_link = (
            p.get("bioLink")
            or p.get("bio_link")
            or p.get("authorMeta", {}).get("bioLink")
            or ""
        )

        rows.append({
            "coach_username": username,
            "tt_followers": followers,
            "tt_total_likes": total_likes,
            "tt_video_count": video_count,
            "tt_bio": bio,
            "tt_bio_link": bio_link,
            "tt_has_bio_link": bool(bio_link),
        })
    return pd.DataFrame(rows)


def process_videos(videos: list) -> pd.DataFrame:
    rows = []
    for v in videos:
        username = (
            v.get("authorMeta", {}).get("name")
            or v.get("uniqueId")
            or v.get("username")
            or "unknown"
        )
        play_count = _safe_int(v.get("playCount") or v.get("plays") or v.get("stats", {}).get("playCount"))
        like_count = _safe_int(v.get("diggCount") or v.get("likes") or v.get("stats", {}).get("diggCount"))
        comment_count = _safe_int(v.get("commentCount") or v.get("comments") or v.get("stats", {}).get("commentCount"))
        share_count = _safe_int(v.get("shareCount") or v.get("shares") or v.get("stats", {}).get("shareCount"))
        desc = v.get("desc") or v.get("description") or v.get("text") or ""

        rows.append({
            "coach_username": username,
            "video_id": v.get("id") or v.get("videoId") or "",
            "play_count": play_count,
            "like_count": like_count,
            "comment_count": comment_count,
            "share_count": share_count,
            "create_date": v.get("createTime") or v.get("createTimeISO") or "",
            "description_length": len(desc),
            "hashtag_count": desc.count("#"),
        })

    return pd.DataFrame(rows)


def enrich_profiles(profiles_df: pd.DataFrame, videos_df: pd.DataFrame) -> pd.DataFrame:
    if videos_df.empty or profiles_df.empty:
        profiles_df["tt_avg_views"] = 0.0
        profiles_df["tt_avg_likes"] = 0.0
        profiles_df["tt_engagement_rate"] = 0.0
        profiles_df["tt_view_to_follower_ratio"] = 0.0
        return profiles_df

    # Per-video engagement rate
    videos_df = videos_df.copy()
    videos_df["video_engagement"] = (
        videos_df["like_count"] + videos_df["comment_count"] + videos_df["share_count"]
    )

    agg = videos_df.groupby("coach_username").agg(
        tt_avg_views=("play_count", "mean"),
        tt_avg_likes=("like_count", "mean"),
        tt_avg_engagement=("video_engagement", "mean"),
    ).reset_index()

    enriched = profiles_df.merge(agg, on="coach_username", how="left")
    enriched["tt_avg_views"] = enriched["tt_avg_views"].fillna(0)
    enriched["tt_avg_likes"] = enriched["tt_avg_likes"].fillna(0)

    enriched["tt_engagement_rate"] = enriched.apply(
        lambda r: round(r["tt_avg_engagement"] / r["tt_followers"] * 100, 2)
        if r["tt_followers"] > 0 else 0.0,
        axis=1,
    )
    enriched["tt_view_to_follower_ratio"] = enriched.apply(
        lambda r: round(r["tt_avg_views"] / r["tt_followers"], 2)
        if r["tt_followers"] > 0 else 0.0,
        axis=1,
    )
    return enriched


def run() -> pd.DataFrame:
    profiles_path = os.path.join(RAW_DIR, "tiktok_profiles.json")
    videos_path = os.path.join(RAW_DIR, "tiktok_videos.json")

    if not os.path.exists(profiles_path):
        print("[tiktok_processor] No tiktok_profiles.json found.")
        return pd.DataFrame()

    with open(profiles_path, encoding="utf-8") as f:
        profiles_raw = json.load(f)

    videos_raw = []
    if os.path.exists(videos_path):
        with open(videos_path, encoding="utf-8") as f:
            videos_raw = json.load(f)

    profiles_df = process_profiles(profiles_raw)
    videos_df = process_videos(videos_raw)
    profiles_enriched = enrich_profiles(profiles_df, videos_df)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    videos_out = os.path.join(PROCESSED_DIR, "tiktok_videos_clean.csv")
    videos_df.to_csv(videos_out, index=False)
    print(f"[tiktok_processor] Saved {len(videos_df)} videos -> {videos_out}")

    return profiles_enriched


if __name__ == "__main__":
    df = run()
    print(df[["coach_username", "tt_followers", "tt_engagement_rate", "tt_view_to_follower_ratio"]].to_string())
