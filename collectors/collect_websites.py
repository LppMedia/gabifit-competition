"""
Collect website content for coaches via Apify RAG Web Browser.

For coaches with known website URLs: scrapes them directly.
For coaches without websites: runs a Google query to find their pricing/services page.

Output:
  data/raw/websites_raw.json — list of { coach_username, coach_name, url, markdown_content }
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collectors.apify_client import run_actor
from seeds.coach_usernames import COACHES

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def scrape_url(url: str) -> str:
    """Fetch a single URL as Markdown via RAG Web Browser."""
    items = run_actor(
        actor_id="apify/rag-web-browser",
        run_input={
            "query": url,
            "maxResults": 1,
            "outputFormats": ["markdown"],
            "scrapingTool": "raw-http",
        },
        timeout_secs=120,
    )
    if items:
        return items[0].get("markdown", items[0].get("text", ""))
    return ""


def search_coach(name: str, instagram: str) -> str:
    """Run a Google search to find pricing/offer info for coaches without websites."""
    query = f"{name} coach fitness precio republica dominicana"
    items = run_actor(
        actor_id="apify/rag-web-browser",
        run_input={
            "query": query,
            "maxResults": 3,
            "outputFormats": ["markdown"],
        },
        timeout_secs=120,
    )
    # Combine text from top results
    combined = ""
    for item in items:
        combined += item.get("markdown", item.get("text", "")) + "\n\n"
    return combined


def run():
    results = []

    for coach in COACHES:
        username = coach.get("instagram") or coach.get("tiktok") or coach["name"]
        name = coach["name"]
        website = coach.get("website")

        print(f"\n[websites] Processing: {name} (@{username})")

        if website:
            print(f"  Scraping direct URL: {website}")
            content = scrape_url(website)
            url_used = website
        else:
            print(f"  No website — running Google search")
            content = search_coach(name, coach.get("instagram", ""))
            url_used = f"search:{name}"

        results.append({
            "coach_username": username,
            "coach_name": name,
            "url": url_used,
            "markdown_content": content,
        })

    path = os.path.join(RAW_DIR, "websites_raw.json")
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[websites] Saved {len(results)} entries -> {path}")


if __name__ == "__main__":
    run()
