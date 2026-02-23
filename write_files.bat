@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo.
echo ==================================================
echo   YouTube Shorts Automation Project - File Writer
echo ==================================================
echo.

set "PROJECT_FOLDER=YouTubeShortsProject"

if exist "%PROJECT_FOLDER%" (
    echo Folder "%PROJECT_FOLDER%" already exists.
    echo Files inside will be overwritten.
    echo.
    echo Press any key to continue, or Ctrl+C to cancel.
    pause >nul
) else (
    mkdir "%PROJECT_FOLDER%"
)

cd /d "%PROJECT_FOLDER%" || (
    echo ERROR: Cannot enter folder "%PROJECT_FOLDER%"
    pause
    exit /b 1
)

:: Create subfolders
mkdir logs temp tests assets 2>nul

echo.
echo Creating project files...

:: ───────────────────────────────────────────────
:: requirements.txt
:: ───────────────────────────────────────────────
(
    echo googletrans==4.0.0-rc1
    echo gTTS
    echo requests
    echo moviepy
    echo pydub
    echo SpeechRecognition
    echo google-api-python-client
    echo google-auth-oauthlib
    echo google-auth-httplib2
    echo pillow
    echo python-dotenv
    echo unsplash-py
    echo pixabay-python
) > requirements.txt

:: ───────────────────────────────────────────────
:: config.py
:: ───────────────────────────────────────────────
(
    echo # config.py - API keys and settings
    echo # NEVER commit this file to git!
    echo.
    echo UNSPLASH_ACCESS_KEY       = "your_unsplash_access_key_here"
    echo PIXABAY_API_KEY           = "your_pixabay_api_key_here"
    echo.
    echo YOUTUBE_CLIENT_SECRETS_FILE = "client_secrets.json"
    echo.
    echo # You can also load secrets from .env using python-dotenv
) > config.py

:: ───────────────────────────────────────────────
:: README.md
:: ───────────────────────────────────────────────
(
    echo # YouTube Shorts Automation - Exam / UPSC Content Generator
    echo.
    echo Creates vertical YouTube Shorts ^(9:16^) with:
    echo • Hindi voice-over ^(gTTS^)
    echo • English subtitles ^(highlighted while speaking^)
    echo • Header text + image slideshow
    echo • Progress bar
    echo • Upload to YouTube
    echo.
    echo ## Features
    echo - Reads structured JSON input
    echo - Fetches royalty-free images ^(Unsplash / Pixabay^)
    echo - Translates text to Hindi + TTS
    echo - Builds video using MoviePy
    echo - Uploads using YouTube Data API v3
    echo.
    echo ## Setup
    echo 1. pip install -r requirements.txt
    echo 2. Fill API keys in config.py
    echo 3. Download OAuth client_secrets.json ^(Google Cloud Console^)
    echo.
    echo ## Usage
    echo python main.py --json data.json
    echo.
    echo ## Folder structure
    echo assets/          optional logos, fonts, backgrounds
    echo temp/            temporary files ^(audio, images, subs^)
    echo logs/            log files
    echo tests/           unit tests ^(pytest^)
) > README.md

:: ───────────────────────────────────────────────
:: data.json   ← example input file
:: ───────────────────────────────────────────────
(
    echo {
    echo   "day": "Sunday",
    echo   "date": "2026-02-22",
    echo   "location": "RBI Headquarters, Mumbai",
    echo   "type": "EducationalNews",
    echo   "news_type": "Economy",
    echo   "channel": "ExamPulse24_7",
    echo   "headline": "Topic 9/100: The Monetary Policy Multiplier!",
    echo   "hook_text": "UPSC Topic #9: If you don't understand how the RBI controls your pocket, you can't clear Prelims! Let's decode Monetary Policy.",
    echo   "details": "The Reserve Bank of India's Monetary Policy is a permanent resident of the UPSC question paper. Focus on the 'Quantitative Tools' like Repo Rate, SLR, and CRR. But here is the 2026 twist: UPSC is now asking about 'Standing Deposit Facility' (SDF) and 'Variable Rate Reverse Repo' (VRRR). Remember, when inflation is high, RBI sucks out liquidity. Understanding the 'Transmission of Monetary Policy' is the key to solving those tricky 2-statement questions. Tune with us for more such news.",
    echo   "subscribe_hook": "What happens to the money supply when the Repo Rate increases? Answer in the comments! Subscribe to find out more from our Top 100 series.",
    echo   "metadata": {
    echo     "title": "Topic 9/100: RBI Monetary Policy ^& SDF Explained ^| ExamPulse24_7",
    echo     "description": "Master Topic #9 of our UPSC Top 100 series. We break down RBI's monetary policy tools and the new SDF mechanism for Prelims 2026. #UPSCEconomy #RBI #MonetaryPolicy #IAS2026",
    echo     "tags": ["RBI Monetary Policy", "Repo Rate", "SDF UPSC", "Economy Prelims", "ExamPulse24_7"],
    echo     "search_key": "RBI Monetary Policy Tools UPSC ^| Difference between CRR and SLR ^| What is Standing Deposit Facility UPSC ^| Economy high yield topics 2026",
    echo     "aspect_ratio": "9:16_FILL"
    echo   }
    echo }
) > data.json

:: ───────────────────────────────────────────────
:: main.py  (minimal skeleton)
:: ───────────────────────────────────────────────
(
    echo # main.py
    echo import argparse
    echo import json
    echo from pathlib import Path
    echo.
    echo # Import your modules here later
    echo # from image_fetch import fetch_images
    echo # from video_compose import create_short
    echo # from uploader import upload_video
    echo.
    echo def main():
    echo     parser = argparse.ArgumentParser(description="YouTube Shorts Generator")
    echo     parser.add_argument("--json", default="data.json", help="Input JSON file")
    echo     args = parser.parse_args()
    echo.
    echo     json_path = Path(args.json)
    echo     if not json_path.is_file():
    echo         print(f"Error: {json_path} not found")
    echo         return 1
    echo.
    echo     with open(json_path, encoding="utf-8") as f:
    echo         data = json.load(f)
    echo.
    echo     print("Processing topic:", data.get("headline", "No headline"))
    echo     # ... call your pipeline functions here
    echo.
    echo if __name__ == "__main__":
    echo     main()
) > main.py

:: ───────────────────────────────────────────────
:: Empty module placeholders
:: ───────────────────────────────────────────────
echo. > parser.py          & echo """Parse and validate input JSON"""          >> parser.py
echo. > script_gen.py      & echo """Build English script + translate to Hindi""" >> script_gen.py
echo. > audio_gen.py       & echo """Generate Hindi TTS audio"""                 >> audio_gen.py
echo. > image_fetch.py     & echo """Download royalty-free images"""             >> image_fetch.py
echo. > subtitle_gen.py    & echo """Create timed .srt subtitles"""              >> subtitle_gen.py
echo. > video_compose.py   & echo """Compose final video with MoviePy"""         >> video_compose.py
echo. > uploader.py        & echo """Upload video to YouTube"""                  >> uploader.py

echo.
echo ==================================================
echo   Setup finished!
echo ==================================================
echo.
echo Next steps:
echo   1. Fill your API keys in config.py
echo   2. Place OAuth client_secrets.json in this folder
echo   3. pip install -r requirements.txt
echo   4. Start implementing the modules
echo.
echo Press any key to exit...
pause >nul