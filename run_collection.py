"""
Master data collection script.

Runs all Apify collectors in sequence:
  1. Instagram profiles + posts
  2. TikTok profiles + videos
  3. Websites (direct scrape or Google search)

Usage:
  python run_collection.py
  python run_collection.py --skip instagram   # skip one platform
  python run_collection.py --only websites    # run only one step

Requires APIFY_TOKEN in .env file.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(description="Run Gabifit data collection")
    parser.add_argument("--skip", choices=["instagram", "tiktok", "websites"], help="Skip a step")
    parser.add_argument("--only", choices=["instagram", "tiktok", "websites"], help="Run only one step")
    args = parser.parse_args()

    steps = ["instagram", "tiktok", "websites"]
    if args.only:
        steps = [args.only]
    elif args.skip:
        steps = [s for s in steps if s != args.skip]

    print("=" * 60)
    print("GABIFIT DATA COLLECTION")
    print(f"Steps to run: {', '.join(steps)}")
    print("=" * 60)

    if "instagram" in steps:
        print("\n[1/3] Collecting Instagram data...")
        from collectors.collect_instagram import run as ig_run
        ig_run()

    if "tiktok" in steps:
        print("\n[2/3] Collecting TikTok data...")
        from collectors.collect_tiktok import run as tt_run
        tt_run()

    if "websites" in steps:
        print("\n[3/3] Collecting website data...")
        from collectors.collect_websites import run as web_run
        web_run()

    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("Raw data saved in: data/raw/")
    print("Next step: python run_processing.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
