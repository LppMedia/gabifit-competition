"""
Merge all processed data sources into coaches_master.csv.

Joins on coach_username (Instagram handle as primary key).
Handles missing platforms gracefully (null columns, not dropped rows).

Output:
  data/processed/coaches_master.csv
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from seeds.coach_usernames import COACHES

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def _funnel_score(row) -> int:
    """0–8 score representing how sophisticated a coach's marketing funnel is."""
    score = 0
    score += 2 if row.get("has_website") else 0
    score += 2 if row.get("has_lead_magnet") else 0
    score += 1 if row.get("uses_linktree") else 0
    score += 1 if row.get("has_whatsapp_cta") else 0
    score += 1 if (row.get("ig_engagement_rate") or 0) > 3.0 else 0
    score += 1 if (row.get("tt_view_to_follower_ratio") or 0) > 2.0 else 0
    return score


def _primary_platform(row) -> str:
    has_ig = (row.get("ig_followers") or 0) > 0
    has_tt = (row.get("tt_followers") or 0) > 0
    if has_ig and has_tt:
        return "both"
    if has_tt:
        return "tiktok"
    return "instagram"


def _top_cta(row) -> str:
    """Determine primary CTA channel, combining IG bio and website data."""
    if row.get("has_whatsapp_cta") or row.get("ig_bio_cta_type") == "whatsapp":
        return "whatsapp"
    if row.get("uses_linktree") or row.get("ig_bio_cta_type") == "linktree":
        return "linktree"
    if row.get("has_website") or row.get("ig_bio_cta_type") == "direct_website":
        return "direct_website"
    if row.get("ig_bio_cta_type") == "email":
        return "email"
    return "none"


def build_seed_frame() -> pd.DataFrame:
    """Build base DataFrame from the seed list so every coach has a row."""
    rows = []
    for c in COACHES:
        rows.append({
            "coach_username": c.get("instagram") or c.get("tiktok") or c["name"],
            "full_name": c["name"],
            "seed_instagram": c.get("instagram"),
            "seed_tiktok": c.get("tiktok"),
            "seed_website": c.get("website"),
        })
    return pd.DataFrame(rows)


def run():
    seed_df = build_seed_frame()

    # Load Instagram profiles (already enriched with engagement stats)
    ig_path = os.path.join(PROCESSED_DIR, "instagram_posts_clean.csv")
    ig_profiles_path = None  # profiles are returned in-memory from processor

    # Re-run processors to get enriched profile DataFrames
    from processors.instagram_processor import run as ig_run
    from processors.tiktok_processor import run as tt_run
    from processors.website_processor import run as web_run

    ig_profiles = ig_run()  # returns enriched profiles DataFrame
    tt_profiles = tt_run()  # returns enriched profiles DataFrame
    web_data = web_run()    # returns services_pricing DataFrame

    # Start with seed frame (guarantees all coaches are present)
    master = seed_df.copy()

    # Merge Instagram
    if not ig_profiles.empty:
        ig_cols = [c for c in ig_profiles.columns if c != "full_name"]
        master = master.merge(
            ig_profiles[ig_cols],
            left_on="coach_username",
            right_on="coach_username",
            how="left",
        )

    # Merge TikTok (join on seed tiktok username -> tt coach_username)
    if not tt_profiles.empty:
        tt_profiles_renamed = tt_profiles.copy()
        tt_profiles_renamed = tt_profiles_renamed.rename(
            columns={"coach_username": "tt_coach_username"}
        )
        master = master.merge(
            tt_profiles_renamed,
            left_on="seed_tiktok",
            right_on="tt_coach_username",
            how="left",
        )
        master = master.drop(columns=["tt_coach_username"], errors="ignore")

    # Merge website/services data
    if not web_data.empty:
        master = master.merge(
            web_data,
            on="coach_username",
            how="left",
        )

    # Compute derived columns
    master["ig_followers"] = master.get("ig_followers", pd.Series(0)).fillna(0).astype(int)
    master["tt_followers"] = master.get("tt_followers", pd.Series(0)).fillna(0).astype(int)
    master["total_social_followers"] = master["ig_followers"] + master["tt_followers"]
    master["primary_platform"] = master.apply(_primary_platform, axis=1)
    master["top_cta_channel"] = master.apply(_top_cta, axis=1)
    master["funnel_score"] = master.apply(_funnel_score, axis=1)

    # Clean up helper columns
    master = master.drop(columns=["seed_instagram", "seed_tiktok", "seed_website"], errors="ignore")

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "coaches_master.csv")
    master.to_csv(out_path, index=False)
    print(f"\n[merge_coaches] Saved {len(master)} coaches -> {out_path}")

    # Sanity checks
    print("\n--- Sanity Checks ---")
    print(f"Total coaches: {len(master)}")
    if "ig_engagement_rate" in master.columns:
        bad_eng = master[master["ig_engagement_rate"] > 50]
        if len(bad_eng) > 0:
            print(f"WARNING: {len(bad_eng)} coaches have ig_engagement_rate > 50 (possible data error)")
    if "min_price_usd" in master.columns:
        bad_price = master[master["min_price_usd"] > 2000]
        if len(bad_price) > 0:
            print(f"WARNING: {len(bad_price)} coaches have min_price_usd > 2000 (possible RD$/USD conversion error)")
    if "top_cta_channel" in master.columns:
        cta_none_pct = (master["top_cta_channel"] == "none").mean() * 100
        print(f"Coaches with no detected CTA: {cta_none_pct:.0f}%")
    print("---------------------\n")

    return master


if __name__ == "__main__":
    df = run()
    print(df[["coach_username", "ig_followers", "tt_followers", "funnel_score", "top_cta_channel"]].to_string())
