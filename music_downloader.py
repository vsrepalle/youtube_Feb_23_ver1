# music_downloader.py
import os
import requests
from pathlib import Path
import config
import sys

# Try to import audio libraries, but provide fallbacks if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("[WARN] numpy not installed. Silent audio creation will be limited.")

try:
    from scipy.io import wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


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
        "AI": "ai_music.mp3",
        "Technology": "tech_music.mp3",
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
    # If music_urls doesn't exist in config, use empty dict
    music_urls = getattr(config.AUDIO, "music_urls", {}) if hasattr(config, 'AUDIO') else {}
    url = music_urls.get(category, music_urls.get("default", ""))
    
    # For demo purposes - if no URL or example.com, create placeholder
    if not url or "example.com" in url:
        print(f"[INFO] Using placeholder for {category}. Creating silent audio...")
        return create_silent_audio(music_path)
    
    # Download the music
    try:
        print(f"[INFO] Downloading music for '{category}' from {url}")
        
        # Add user-agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, stream=True, headers=headers, timeout=30)
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
        # Method 1: Using pydub (easiest)
        if HAS_PYDUB:
            print("[INFO] Using pydub to create silent audio...")
            silent = AudioSegment.silent(duration=duration*1000)  # duration in milliseconds
            silent.export(music_path, format="mp3")
            print(f"[INFO] Created silent audio at {music_path}")
            return str(music_path)
        
        # Method 2: Using scipy + numpy
        elif HAS_NUMPY and HAS_SCIPY:
            print("[INFO] Using numpy+scipy to create silent audio...")
            sample_rate = 44100
            silent_array = np.zeros(sample_rate * duration, dtype=np.int16)
            
            # Save as WAV first
            wav_path = music_path.with_suffix('.wav')
            wavfile.write(wav_path, sample_rate, silent_array)
            
            # Try to convert to MP3 (requires ffmpeg)
            try:
                import subprocess
                subprocess.run(['ffmpeg', '-i', str(wav_path), '-y', str(music_path)], 
                             capture_output=True, check=True)
                wav_path.unlink()  # Remove WAV file
                print(f"[INFO] Created silent audio at {music_path}")
                return str(music_path)
            except:
                # If ffmpeg fails, just return the WAV path
                print(f"[INFO] Created silent WAV at {wav_path}")
                return str(wav_path)
        
        # Method 3: Create an empty file (not ideal but better than nothing)
        else:
            print("[WARN] No audio libraries available. Creating empty placeholder.")
            with open(music_path, 'wb') as f:
                f.write(b'')  # Empty file
            return str(music_path)
            
    except Exception as e:
        print(f"[ERROR] Could not create silent audio: {e}")
        # Create an empty file as last resort
        try:
            with open(music_path, 'wb') as f:
                f.write(b'')
            return str(music_path)
        except:
            return None


def ensure_music_exists(news_type, force_download=False):
    """
    Main function to call from main.py
    """
    # Check if auto_download_music is enabled in config
    auto_download = False
    if hasattr(config, 'AUDIO') and isinstance(config.AUDIO, dict):
        auto_download = config.AUDIO.get("auto_download_music", False)
    elif hasattr(config, 'AUDIO') and hasattr(config.AUDIO, 'get'):
        auto_download = config.AUDIO.get("auto_download_music", False)
    
    if not auto_download and not force_download:
        # Check if default music exists
        music_dir = Path("background_music")
        music_dir.mkdir(exist_ok=True)
        
        # Try category-specific first, then default
        category_map = {
            "TechNews": "tech_music.mp3",
            "Entertainment": "entertainment_music.mp3",
            "BollywoodNews": "bollywood_music.mp3",
            "Artificial Intelligence": "ai_music.mp3",
            "AI": "ai_music.mp3",
            "default": "default_music.mp3"
        }
        
        filename = category_map.get(news_type, category_map["default"])
        music_path = music_dir / filename
        
        if music_path.exists():
            return str(music_path)
        
        # Try default
        default_path = music_dir / "default_music.mp3"
        if default_path.exists():
            return str(default_path)
        
        print("[WARN] No music found and auto-download is disabled")
        return None
    
    return download_music_for_category(news_type, force_download)


# Simple test function
if __name__ == "__main__":
    print("Testing music downloader...")
    
    # Test with different categories
    test_categories = ["TechNews", "Entertainment", "Artificial Intelligence", "default"]
    
    for category in test_categories:
        print(f"\nTesting category: {category}")
        path = ensure_music_exists(category, force_download=True)
        if path:
            print(f"  → Result: {path}")
        else:
            print(f"  → Failed for {category}")