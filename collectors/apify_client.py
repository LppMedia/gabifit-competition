"""
Thin wrapper around the Apify HTTP API.

Uses the APIFY_TOKEN environment variable (set in .env).
All collectors call run_actor() and poll until the run finishes,
then return the items list from the default dataset.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
BASE_URL = "https://api.apify.com/v2"


def _headers():
    return {"Authorization": f"Bearer {APIFY_TOKEN}"}


def run_actor(actor_id: str, run_input: dict, timeout_secs: int = 300) -> list:
    """
    Run an Apify actor synchronously and return all output items.

    Args:
        actor_id:    e.g. "apify/instagram-profile-scraper"
        run_input:   dict sent as the actor's input JSON
        timeout_secs: how long to wait before giving up

    Returns:
        List of output items from the actor's default dataset.
    """
    if not APIFY_TOKEN:
        raise EnvironmentError(
            "APIFY_TOKEN not set. Add it to a .env file: APIFY_TOKEN=apify_api_xxx"
        )

    # Start the run — Apify REST API requires ~ instead of / in actor IDs
    actor_id_url = actor_id.replace("/", "~")
    start_url = f"{BASE_URL}/acts/{actor_id_url}/runs"
    resp = requests.post(
        start_url,
        headers=_headers(),
        json=run_input,
        timeout=30,
    )
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]
    print(f"  [apify] Started actor={actor_id} run_id={run_id}")

    # Poll until finished
    deadline = time.time() + timeout_secs
    while time.time() < deadline:
        status_url = f"{BASE_URL}/actor-runs/{run_id}"
        status_resp = requests.get(status_url, headers=_headers(), timeout=15)
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]
        print(f"  [apify] run_id={run_id} status={status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
        time.sleep(10)
    else:
        raise TimeoutError(f"Actor {actor_id} did not finish within {timeout_secs}s")

    if status != "SUCCEEDED":
        raise RuntimeError(f"Actor {actor_id} ended with status={status}")

    # Fetch dataset items
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    items_url = f"{BASE_URL}/datasets/{dataset_id}/items?limit=9999"
    items_resp = requests.get(items_url, headers=_headers(), timeout=30)
    items_resp.raise_for_status()
    items = items_resp.json()
    print(f"  [apify] Fetched {len(items)} items from dataset {dataset_id}")
    return items
