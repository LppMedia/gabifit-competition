"""
Master data processing script.

Runs all processors in sequence and produces coaches_master.csv.

Usage:
  python run_processing.py

After this completes, run the dashboard:
  streamlit run dashboard/app.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def verify_outputs():
    import pandas as pd
    processed_dir = os.path.join(os.path.dirname(__file__), "data", "processed")

    print("\n--- Output Verification ---")
    for filename in ["coaches_master.csv", "instagram_posts_clean.csv",
                     "tiktok_videos_clean.csv", "services_pricing.csv"]:
        path = os.path.join(processed_dir, filename)
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"  {filename}: {len(df)} rows, {len(df.columns)} columns")
        else:
            print(f"  {filename}: NOT FOUND")

    master_path = os.path.join(processed_dir, "coaches_master.csv")
    if os.path.exists(master_path):
        df = pd.read_csv(master_path)
        print("\n  coaches_master.csv sample stats:")
        if "ig_engagement_rate" in df.columns:
            print(f"    avg IG engagement rate: {df['ig_engagement_rate'].mean():.2f}%")
        if "tt_view_to_follower_ratio" in df.columns:
            print(f"    avg TT view/follower ratio: {df['tt_view_to_follower_ratio'].mean():.2f}")
        if "min_price_usd" in df.columns:
            with_price = df["min_price_usd"].notna().sum()
            print(f"    coaches with detected pricing: {with_price}/{len(df)}")
        if "top_cta_channel" in df.columns:
            print(f"    CTA distribution:\n{df['top_cta_channel'].value_counts().to_string()}")
    print("---------------------------\n")


def main():
    print("=" * 60)
    print("GABIFIT DATA PROCESSING")
    print("=" * 60)

    print("\n[1/3] Processing Instagram data...")
    from processors.instagram_processor import run as ig_run
    ig_profiles = ig_run()
    print(f"  Instagram profiles processed: {len(ig_profiles)}")

    print("\n[2/3] Processing TikTok data...")
    from processors.tiktok_processor import run as tt_run
    tt_profiles = tt_run()
    print(f"  TikTok profiles processed: {len(tt_profiles)}")

    print("\n[3/4] Processing website/services data...")
    from processors.website_processor import run as web_run
    web_data = web_run()
    print(f"  Website entries processed: {len(web_data)}")

    print("\n[4/4] Merging all sources into coaches_master.csv...")
    from processors.merge_coaches import run as merge_run
    master = merge_run()

    verify_outputs()

    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("Processed data saved in: data/processed/")
    print("Next step: streamlit run dashboard/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
