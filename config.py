# config.py - API keys & project settings
# NEVER commit this file to git or share it publicly!

# ───────────────────────────────────────────────
# Image APIs
# ───────────────────────────────────────────────

PEXELS_API_KEY = "Oszdsq7V3DU1S8t1n6coHlHHeHb76cxZjb1HRYYvru32CpQYSmrO52ax"             # Get from: https://www.pexels.com/api/
SERPAPI_KEY    = "4ec0080d442d1ccc962b952fc5b2ff84958f1b57932aec0c4090eeb22817025b"                # Get from: https://serpapi.com (free 100 searches/month)

# ───────────────────────────────────────────────
# ImageMagick (required for TextClip & subtitles)
# ───────────────────────────────────────────────

IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

# ───────────────────────────────────────────────
# Video settings
# ───────────────────────────────────────────────

VIDEO_WIDTH    = 1080
VIDEO_HEIGHT   = 1920
FPS            = 30
HEADER_HEIGHT  = int(VIDEO_HEIGHT * 0.20)  # 384px ≈ 20% top for headline + hook

# ───────────────────────────────────────────────
# YouTube upload settings (optional)
# ───────────────────────────────────────────────

YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"     # OAuth file from Google Cloud
YOUTUBE_CATEGORY_ID = "27"                              # Education / News
DEFAULT_PRIVACY_STATUS = "public"                       # or "private" / "unlisted"

# ───────────────────────────────────────────────
# Other settings
# ───────────────────────────────────────────────

TEMP_DIR = "temp"
OUTPUT_DIR = "output"
DEFAULT_IMAGE_COUNT = 6

# YouTube API settings (for uploader.py)
YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"     # Download from Google Cloud Console
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_CATEGORY_ID = "27"                               # 27 = Education / News
DEFAULT_PRIVACY_STATUS = "public"                        # or "private" / "unlisted"