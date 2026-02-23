import os
import json
import tkinter as tk
from tkinter import filedialog
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configuration
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
JSON_DATA_FILE = 'data.json'
CLIENT_SECRETS_FILE = 'client_secret.json' # Download this from Google Cloud Console

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build('youtube', 'v3', credentials=credentials)

def pick_video_file():
    root = tk.Tk()
    root.withdraw() # Hide the main tkinter window
    file_path = filedialog.askopenfilename(
        title="Select Video to Upload",
        filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
    )
    return file_path

def upload_video(youtube, video_path, metadata):
    # Extract metadata from your JSON structure
    snippet = {
        'title': metadata['metadata']['title'],
        'description': metadata['metadata']['description'],
        'tags': metadata['metadata']['tags'],
        'categoryId': '22' # 22 is 'People & Blogs'. Use '27' for Education or '17' for Sports.
    }
    
    status = {
        'privacyStatus': 'private', # Default to private as per your preference
        'selfDeclaredMadeForKids': False
    }

    body = dict(snippet=snippet, status=status)

    print(f"🚀 Starting upload for: {snippet['title']}")
    
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    response = insert_request.execute()
    print(f"✅ Success! Video ID: {response['id']}")

def main():
    # 1. Pick the file
    video_file = pick_video_file()
    if not video_file:
        print("❌ No file selected. Exiting.")
        return

    # 2. Load the metadata from data.json
    if not os.path.exists(JSON_DATA_FILE):
        print(f"❌ {JSON_DATA_FILE} not found!")
        return
        
    with open(JSON_DATA_FILE, 'r') as f:
        data = json.load(f)

    # 3. Authenticate and Upload
    try:
        youtube = get_authenticated_service()
        upload_video(youtube, video_file, data)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()