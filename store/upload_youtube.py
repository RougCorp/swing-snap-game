#!/usr/bin/env python3
"""Upload Swing & Snap ad videos to YouTube (unlisted) for Google Ads.

Setup (once):
  1. Go to https://console.cloud.google.com/
  2. Create project → APIs & Services → Enable "YouTube Data API v3"
  3. APIs & Services → Credentials → Create Credentials → OAuth client ID
     → Application type: Desktop app → Download JSON
  4. Save the downloaded file as:
       /Users/rougon/Documents/CREAPP/swing-snap/store/client_secrets.json
  5. Run this script — a browser opens for Google sign-in, then uploads start.

Videos uploaded as UNLISTED so only your Google Ads account can use them.
"""

import os
import sys
import pickle
import http.client
import httplib2
import time
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ── Config ─────────────────────────────────────────────────────────────────────

BASE         = Path(__file__).parent
SECRETS_FILE = BASE / "client_secrets.json"
TOKEN_FILE   = BASE / ".youtube_token.pkl"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

VIDEOS = [
    {
        "path":        BASE / "video" / "swing_snap_ads_portrait.mp4",
        "title":       "Swing & Snap — Portrait Ad (9:16)",
        "description": (
            "Swing & Snap — the addictive one-finger mobile game.\n"
            "Tap to release the rope and snap to the next pivot!\n\n"
            "Available free on iOS & Android."
        ),
        "tags":    ["swing snap", "mobile game", "casual", "ios", "android",
                    "hypercasual", "arcade", "one finger", "ad"],
        "format":  "portrait 9:16",
    },
    {
        "path":        BASE / "video" / "swing_snap_ads_landscape.mp4",
        "title":       "Swing & Snap — Landscape Ad (16:9)",
        "description": (
            "Swing & Snap — the addictive one-finger mobile game.\n"
            "Tap to release the rope and snap to the next pivot!\n\n"
            "Available free on iOS & Android."
        ),
        "tags":    ["swing snap", "mobile game", "casual", "ios", "android",
                    "hypercasual", "arcade", "one finger", "ad"],
        "format":  "landscape 16:9",
    },
]

# ── Auth ────────────────────────────────────────────────────────────────────────

def get_authenticated_service():
    if not SECRETS_FILE.exists():
        print("❌  client_secrets.json not found.")
        print(f"    Expected at: {SECRETS_FILE}")
        print()
        print("    Steps to create it:")
        print("    1. https://console.cloud.google.com/")
        print("    2. APIs & Services → Library → search 'YouTube Data API v3' → Enable")
        print("    3. APIs & Services → Credentials → + Create Credentials → OAuth client ID")
        print("       → Application type: Desktop app → any name → Create → Download JSON")
        print(f"    4. Rename downloaded file to 'client_secrets.json' and place it here:")
        print(f"       {SECRETS_FILE}")
        print()
        sys.exit(1)

    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄  Refreshing access token…")
            creds.refresh(Request())
        else:
            print("🌐  Opening browser for Google sign-in…")
            flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("✅  Authenticated — token saved for next time.\n")

    return build("youtube", "v3", credentials=creds)


# ── Upload ──────────────────────────────────────────────────────────────────────

def upload_video(youtube, video: dict):
    path = video["path"]
    if not path.exists():
        print(f"  ⚠️  File not found, skipping: {path.name}")
        return None

    size_mb = path.stat().st_size / 1024 / 1024
    print(f"\n📤  Uploading {path.name}  ({size_mb:.1f} MB) …")

    body = {
        "snippet": {
            "title":       video["title"],
            "description": video["description"],
            "tags":        video["tags"],
            "categoryId":  "20",            # Gaming
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":         "unlisted",   # visible only via direct link / Google Ads
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=4 * 1024 * 1024,   # 4 MB chunks
    )

    request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    last_pct = -1

    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            if pct != last_pct:
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                print(f"\r    [{bar}] {pct}%", end="", flush=True)
                last_pct = pct

    print()
    video_id  = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  ✅  Uploaded!  ID: {video_id}")
    print(f"      URL:  {video_url}")
    return video_url


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print("=== Swing & Snap — YouTube Upload ===\n")

    youtube = get_authenticated_service()

    results = []
    for v in VIDEOS:
        url = upload_video(youtube, v)
        if url:
            results.append((v["format"], url))

    print("\n" + "═" * 55)
    print("✅  Done! Copy these URLs into Google Ads:\n")
    for fmt, url in results:
        print(f"  {fmt:20s}  {url}")
    print()
    print("In Google Ads → Assets → Video → paste URL above.")
    print("Set video format: In-stream or Bumper as needed.")
    print("═" * 55)


if __name__ == "__main__":
    main()
