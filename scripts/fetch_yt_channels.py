#!/usr/bin/env python3
"""Fetch YouTube channel metadata for all accounts listed in fixtures/initial_data.json
and write the real channel IDs / descriptions back into that file.

Usage:
    # From the repo root (or inside the container):
    YOUTUBE_API_KEY=<key> python scripts/fetch_yt_channels.py

    # Or pass the key explicitly:
    python scripts/fetch_yt_channels.py --api-key AIza...

Requirements: httpx  (already in requirements.txt)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

FIXTURES_FILE = Path(__file__).parent.parent / "fixtures" / "initial_data.json"
YT_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"


def fetch_channel(handle: str, api_key: str) -> dict:
    """Return raw snippet + contentDetails for a channel @handle."""
    params = {
        "part": "snippet,contentDetails",
        "forHandle": handle,
        "key": api_key,
    }
    resp = httpx.get(YT_CHANNELS_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    if not items:
        raise ValueError(f"No channel found for handle '@{handle}'")

    item = items[0]
    snippet = item["snippet"]
    uploads_playlist_id = (
        item.get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads", "")
    )

    return {
        "account_id": item["id"],
        "description": snippet.get("description", ""),
        "country_code": snippet.get("country", ""),
        "uploads_playlist_id": uploads_playlist_id,
        # Keep name from fixture unless YouTube has a cleaner title
        "_yt_title": snippet.get("title", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate fixture with YouTube channel data")
    parser.add_argument("--api-key", default=os.getenv("YOUTUBE_API_KEY"), help="YouTube Data API v3 key")
    parser.add_argument("--fixture", default=str(FIXTURES_FILE), help="Path to the fixture JSON file")
    args = parser.parse_args()

    if not args.api_key:
        sys.exit(
            "ERROR: YouTube API key required.\n"
            "Set YOUTUBE_API_KEY env var or pass --api-key."
        )

    fixture_path = Path(args.fixture)
    with fixture_path.open() as f:
        fixture = json.load(f)

    accounts = fixture.get("accounts", [])
    updated = 0

    for account in accounts:
        handle = account.get("handle")
        if not handle:
            print(f"  SKIP  '{account.get('name')}' — no handle in fixture")
            continue

        print(f"  FETCH @{handle} ...", end=" ", flush=True)
        try:
            yt = fetch_channel(handle, args.api_key)
        except Exception as exc:
            print(f"ERROR: {exc}")
            continue

        account["account_id"] = yt["account_id"]
        account["description"] = yt["description"]
        account["country_code"] = yt["country_code"]
        account["uploads_playlist_id"] = yt["uploads_playlist_id"]
        # Optionally overwrite name with YouTube's canonical title
        # account["name"] = yt["_yt_title"]

        print(f"OK  ({yt['account_id']})")
        updated += 1

    with fixture_path.open("w") as f:
        json.dump(fixture, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nUpdated {updated}/{len(accounts)} accounts → {fixture_path}")


if __name__ == "__main__":
    main()
