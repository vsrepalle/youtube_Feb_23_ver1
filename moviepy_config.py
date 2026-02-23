# moviepy_config.py
# This file MUST be imported BEFORE any moviepy-related code
# It sets the correct path to ImageMagick so TextClip works

from moviepy.config import change_settings

change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
})

print("ImageMagick path configured successfully")  # optional debug line