# YouTube uploader 
"""YouTube upload (OAuth flow)"""

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        config.YOUTUBE_CLIENT_SECRETS_FILE,
        scopes=config.YOUTUBE_SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id="27",   # Education
    privacy_status="public"
):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print("Uploading...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print("Upload complete!")
    print(f"Video ID: {response['id']}")
    print(f"Link: https://youtu.be/{response['id']}")

    return response["id"]