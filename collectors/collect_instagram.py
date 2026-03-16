"""
Collect Instagram profiles and posts for all coaches in the seed list.

Outputs:
  data/raw/instagram_profiles.json  — one entry per coach profile
  data/raw/instagram_posts.json     — one entry per post (up to 12 per coach)
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collectors.apify_client import run_actor
from seeds.coach_usernames import INSTAGRAM_USERNAMES

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def collect_profiles(usernames: list) -> list:
    print(f"\n[instagram] Scraping {len(usernames)} profiles...")
    items = run_actor(
        actor_id="apify/instagram-profile-scraper",
        run_input={"usernames": usernames},
        timeout_secs=300,
    )
    return items


def collect_posts(usernames: list) -> list:
    print(f"\n[instagram] Scraping posts for {len(usernames)} profiles...")
    items = run_actor(
        actor_id="apify/instagram-post-scraper",
        run_input={
            "username": usernames,
            "resultsLimit": 12,
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
    if not INSTAGRAM_USERNAMES:
        print("[instagram] No usernames in seed list. Add coaches to seeds/coach_usernames.py")
        return

    profiles = collect_profiles(INSTAGRAM_USERNAMES)
    save(profiles, "instagram_profiles.json")

    posts = collect_posts(INSTAGRAM_USERNAMES)
    save(posts, "instagram_posts.json")

    print("\n[instagram] Collection complete.")


if __name__ == "__main__":
    run()
