"""
src/publisher/youtube_uploader.py - Headless YouTube Data API v3 Uploader
Supports OAuth2 refresh tokens, chunked resumable upload, custom thumbnails, and chapter timestamps.
"""

import os
import time
import json
import http.client
import httplib2
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "storage/youtube_credentials.json"

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine
)

def authenticate_youtube(interactive: bool = False):
    """
    Returns an authenticated YouTube service.
    Looks for persistent credentials in storage/youtube_credentials.json or environment.
    """
    creds = None

    # Check for credentials stored in Google Drive
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"[YouTube Auth] Warning: could not load stored credentials: {e}")

    # Check environment variables fallback
    if not creds or not creds.valid:
        client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

        if client_id and client_secret and refresh_token:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )

    # If interactive and client_secrets.json exists, prompt user to authorize once
    if (not creds or not creds.valid) and interactive:
        client_secret_file = "client_secret.json"
        if os.path.exists(client_secret_file):
            print("[YouTube Auth] Initiating one-time browser authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=8080)
            # Save token to Google Drive for future headless runs
            os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
            with open(CREDENTIALS_FILE, "w") as f:
                f.write(creds.to_json())
            print(f"[YouTube Auth] Credentials saved to {CREDENTIALS_FILE}!")
        else:
            print(f"[YouTube Auth] No '{client_secret_file}' found for interactive login.")

    if creds and creds.valid:
        return build("youtube", "v3", credentials=creds)
    elif creds and creds.refresh_token:
        # Refresh automatically
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)

    return None

def resumable_upload(insert_request):
    """Executes a chunked resumable upload with exponential backoff."""
    response = None
    error = None
    retry = 0
    max_retries = 10

    print("[YouTube Upload] Streaming video chunks to YouTube...")
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  -> Upload progress: {pct}%")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"HTTP error {e.resp.status}: {e.content}"
            else:
                raise e
        except RETRIABLE_EXCEPTIONS as e:
            error = f"Network error: {e}"

        if error is not None:
            print(f"[YouTube Upload] {error}")
            retry += 1
            if retry > max_retries:
                raise RuntimeError("Max retries exceeded during YouTube upload.")
            wait_s = 2 ** retry
            print(f"  Retrying in {wait_s}s...")
            time.sleep(wait_s)
            error = None

    video_id = response.get("id")
    print(f"[YouTube Upload] Upload completed! Video ID: {video_id}")
    return video_id

def upload_video_to_youtube(
    video_file_path: str,
    thumbnail_file_path: str,
    metadata: dict,
    interactive_auth: bool = False
) -> str | None:
    youtube = authenticate_youtube(interactive=interactive_auth)

    if not youtube:
        print("\n" + "!" * 60)
        print("[YouTube Uploader] NOTE: YouTube API credentials not configured yet.")
        print(f"To enable automated uploading, either:")
        print(f"  1. Place your Google Cloud 'client_secret.json' in this directory and run:")
        print(f"     .venv/bin/python src/publisher/youtube_uploader.py --auth")
        print(f"  2. Or set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN env vars.")
        print(f"The video and metadata have been staged in Google Drive:")
        print(f"  Video:     {video_file_path}")
        print(f"  Thumbnail: {thumbnail_file_path}")
        print("!" * 60 + "\n")
        return None

    body = {
        "snippet": {
            "title": metadata["title"][:100],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": metadata.get("categoryId", "10"),
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus": metadata.get("privacyStatus", "unlisted"),
            "selfDeclaredMadeForKids": False
        }
    }

    # 10MB chunked upload
    media = MediaFileUpload(video_file_path, chunksize=10 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    insert_req = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    video_id = resumable_upload(insert_req)

    # Attach custom thumbnail (graceful if channel lacks phone verification for custom thumbnails)
    if thumbnail_file_path and os.path.exists(thumbnail_file_path):
        print(f"[YouTube Uploader] Uploading custom thumbnail...")
        try:
            thumb_media = MediaFileUpload(thumbnail_file_path, mimetype="image/png")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media
            ).execute()
            print(f"  ✓ Thumbnail attached!")
        except Exception as e:
            print(f"  ⚠️ Custom thumbnail could not be set automatically (channel may need 1-time phone verification at youtube.com/verify): {e}")

    video_url = f"https://youtu.be/{video_id}"
    print(f"\n🎉 VIDEO IS LIVE ON YOUTUBE: {video_url}")
    return video_id

if __name__ == "__main__":
    import sys
    if "--auth" in sys.argv:
        authenticate_youtube(interactive=True)
