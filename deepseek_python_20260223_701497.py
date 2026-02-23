import os
import requests
from pathlib import Path
import config
import json

def download_music_for_category(category, force_download=False):
    """
    Download background music for a specific category if not already present
    """
    music_dir = Path("background_music")
    music_dir.mkdir(exist_ok=True)
    
    # Map category to filename
    category_map = {
        "TechNews": "tech_music.mp3",
        "Entertainment": "entertainment_music.mp3",
        "BollywoodNews": "bollywood_music.mp3",
        "Artificial Intelligence": "ai_music.mp3",
        "Sports": "sports_music.mp3",
        "default": "default_music.mp3"
    }
    
    # Get filename for category
    filename = category_map.get(category, category_map["default"])
    music_path = music_dir / filename
    
    # Check if music already exists
    if music_path.exists() and not force_download:
        print(f"[INFO] Music for '{category}' already exists at {music_path}")
        return str(music_path)
    
    # Get URL from config
    url = config.AUDIO["music_urls"].get(category, config.AUDIO["music_urls"]["default"])
    
    # For demo purposes - if URLs are not real, create placeholder
    if "example.com" in url:
        print(f"[WARN] Using placeholder URL for {category}. Creating silent audio...")
        return create_silent_audio(music_path)
    
    # Download the music
    try:
        print(f"[INFO] Downloading music for '{category}' from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(music_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[SUCCESS] Music downloaded to {music_path}")
        return str(music_path)
    except Exception as e:
        print(f"[ERROR] Failed to download music: {e}")
        print("[INFO] Creating silent audio as fallback...")
        return create_silent_audio(music_path)

def create_silent_audio(music_path, duration=300):
    """
    Create a silent audio file as fallback
    """
    try:
        import numpy as np
        from scipy.io import wavfile
        import soundfile as sf
        from pydub import AudioSegment
        
        # Create 5 minutes of silence (300 seconds)
        sample_rate = 44100
        silent_array = np.zeros(sample_rate * duration, dtype=np.int16)
        
        # Save as WAV first
        wav_path = music_path.with_suffix('.wav')
        wavfile.write(wav_path, sample_rate, silent_array)
        
        # Convert to MP3
        audio = AudioSegment.from_wav(wav_path)
        audio.export(music_path, format="mp3")
        
        # Clean up WAV
        wav_path.unlink()
        
        print(f"[INFO] Created silent fallback audio at {music_path}")
        return str(music_path)
    except Exception as e:
        print(f"[ERROR] Could not create silent audio: {e}")
        return None

def ensure_music_exists(news_type, force_download=False):
    """
    Main function to call from main.py
    """
    if not config.AUDIO["auto_download_music"]:
        # Check if default music exists
        default_path = Path("background_music/default_music.mp3")
        if default_path.exists():
            return str(default_path)
        else:
            print("[WARN] Auto-download disabled and no music found")
            return None
    
    return download_music_for_category(news_type, force_download)

# For testing
if __name__ == "__main__":
    # Test with different categories
    for category in ["TechNews", "Entertainment", "BollywoodNews", "Artificial Intelligence"]:
        path = ensure_music_exists(category)
        print(f"{category}: {path}")