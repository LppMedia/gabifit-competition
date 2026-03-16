"""
Collect TikTok profiles and videos for all coaches in the seed list.

Outputs:
  data/raw/tiktok_profiles.json  — one entry per coach profile
  data/raw/tiktok_videos.json    — one entry per video (up to 15 per coach)
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collectors.apify_client import run_actor
from seeds.coach_usernames import TIKTOK_USERNAMES

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def collect_profiles(usernames: list) -> list:
    print(f"\n[tiktok] Scraping {len(usernames)} profiles...")
    items = run_actor(
        actor_id="clockworks/tiktok-profile-scraper",
        run_input={"profiles": usernames},
        timeout_secs=300,
    )
    return items


def collect_videos(usernames: list) -> list:
    print(f"\n[tiktok] Scraping videos for {len(usernames)} profiles...")
    items = run_actor(
        actor_id="clockworks/free-tiktok-scraper",
        run_input={
            "profiles": usernames,
            "resultsPerPage": 15,
        },
        timeout_secs=600,
    )
    return items


def save(data: list, filename: str):
    path = os.path.join(RAW_DIR, filename)
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(data)} records -> {path}")


def run():
    if not TIKTOK_USERNAMES:
        print("[tiktok] No TikTok usernames in seed list.")
        return

    profiles = collect_profiles(TIKTOK_USERNAMES)
    save(profiles, "tiktok_profiles.json")

    videos = collect_videos(TIKTOK_USERNAMES)
    save(videos, "tiktok_videos.json")

    print("\n[tiktok] Collection complete.")


if __name__ == "__main__":
    run()
