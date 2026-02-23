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
# TEXT STYLING - Subtitles
# ───────────────────────────────────────────────

SUBTITLE = {
    "fontsize": 55,
    "color": "white",           # Default subtitle color
    "highlight_color": "yellow", # Currently spoken word color
    "stroke_color": "black",
    "stroke_width": 3,
    "font": "Arial-Bold",
    "position_y_offset": 250,    # Distance from bottom (config.VIDEO_HEIGHT - this value)
    "background_opacity": 0,      # 0 = no background, 0.5 = semi-transparent, 1 = solid
    "background_color": (0, 0, 0) # Black background (if opacity > 0)
}

# ───────────────────────────────────────────────
# TEXT STYLING - Header (Headline)
# ───────────────────────────────────────────────

HEADER = {
    "fontsize": 45,
    "color": "white",
    "stroke_color": "black",
    "stroke_width": 2,
    "font": "Arial-Bold",
    "background_opacity": 0.7,
    "background_color": (0, 0, 0),
    "height": 110,
    "position_y": 25
}

# ───────────────────────────────────────────────
# TEXT STYLING - Hook (Opening Text)
# ───────────────────────────────────────────────

HOOK = {
    "fontsize": 80,
    "color": "yellow",
    "stroke_color": "black",
    "stroke_width": 4,
    "font": "Arial-Bold",
    "duration": 3.5,              # How long hook appears
    "zoom_effect": True,           # Enable zoom effect
    "zoom_speed": 0.08              # Zoom factor per second
}

# ───────────────────────────────────────────────
# TEXT STYLING - End Screen (Subscribe)
# ───────────────────────────────────────────────

END_SCREEN = {
    "fontsize": 60,
    "color": "white",
    "stroke_color": "black",
    "stroke_width": 2,
    "font": "Arial-Bold",
    "duration": 4,
    "background_opacity": 0.85,
    "background_color": (0, 0, 0)
}

# ───────────────────────────────────────────────
# PROGRESS BAR STYLING
# ───────────────────────────────────────────────

PROGRESS_BAR = {
    "height": 10,
    "background_color": (50, 50, 50),
    "fill_color": (255, 0, 0),      # Red progress
    "position_y_offset": 10          # Distance from bottom
}

# ───────────────────────────────────────────────
# AUDIO SETTINGS
# ───────────────────────────────────────────────

AUDIO = {
    "speed_factor": 1.2,              # Speed up audio (1.0 = normal)
    "background_music_volume": 0.08,   # 0.0 to 1.0
    "auto_download_music": True,       # Download music if not found
    "music_urls": {                     # Category-specific music URLs
        "default": "https://example.com/default_music.mp3",
        "TechNews": "https://example.com/tech_music.mp3",
        "Entertainment": "https://example.com/entertainment_music.mp3",
        "BollywoodNews": "https://example.com/bollywood_music.mp3",
        "Artificial Intelligence": "https://example.com/ai_music.mp3"
    }
}

# ───────────────────────────────────────────────
# YouTube upload settings
# ───────────────────────────────────────────────

YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"     # OAuth file from Google Cloud
YOUTUBE_CATEGORY_ID = "27"                              # Education / News
DEFAULT_PRIVACY_STATUS = "public"                        # or "private" / "unlisted"

# ───────────────────────────────────────────────
# Other settings
# ───────────────────────────────────────────────

TEMP_DIR = "temp"
OUTPUT_DIR = "output"
DEFAULT_IMAGE_COUNT = 6

# YouTube API settings (for uploader.py)
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# AUDIO SETTINGS
AUDIO = {
    "speed_factor": 1.2,              # Speed up audio (1.0 = normal)
    "background_music_volume": 0.08,   # 0.0 to 1.0
    "auto_download_music": False,       # Set to False initially until you have real URLs
    "music_urls": {                     # Category-specific music URLs
        "default": "",                   # Leave empty to use silent audio
        "TechNews": "",
        "Entertainment": "",
        "BollywoodNews": "",
        "Artificial Intelligence": "",
        "AI": ""
    }
}