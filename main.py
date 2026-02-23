# main.py - Force ImageMagick config FIRST (before any MoviePy import)

# === VERY IMPORTANT: THIS BLOCK MUST BE AT THE VERY TOP ===
from moviepy.config import change_settings

change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
})

print("[CONFIG] ImageMagick path forced globally")

# Quick test to prove TextClip works
try:
    from moviepy.editor import TextClip
    test_clip = TextClip("TEST TEXT", fontsize=50, color='white')
    print("[TEST] TextClip created successfully → ImageMagick is working!")
except Exception as e:
    print("[TEST FAIL] ImageMagick still not found:")
    print(e)
    raise

# Now safe to import everything else
import argparse
import json
from pathlib import Path
import os
import datetime
import sys

# Import project modules
from parser import parse_input
from script_gen import build_english_script, translate_to_hindi
from audio_gen import generate_audio
from image_fetch import fetch_images
from video_compose import make_short_video
from uploader import upload_video
from music_downloader import ensure_music_exists
import config


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import requests
        import numpy
        import PIL
        print("[OK] All core dependencies found")
    except ImportError as e:
        print(f"[WARN] Missing dependency: {e}")
        print("[INFO] Run: pip install requests numpy pillow")


def get_news_type(data):
    """Extract news type from data with fallback"""
    news_type = data.get("news_type") or data.get("type") or data.get("category", "default")
    return news_type


def process_single_scene(scene_data, scene_index, total_scenes, timestamp, force_music=False):
    """Process a single scene from the JSON array"""
    
    print(f"\n{'='*60}")
    print(f"PROCESSING SCENE {scene_index + 1} OF {total_scenes}")
    print(f"Headline: {scene_data.get('headline', 'Untitled')}")
    print(f"{'='*60}\n")
    
    # Get news type for category-specific music
    news_type = get_news_type(scene_data)
    
    # Create output filename for this scene
    safe_news_type = news_type.replace(" ", "_")
    safe_headline = scene_data.get('headline', 'untitled')[:30].replace(' ', '_').replace('/', '_')
    safe_headline = ''.join(c for c in safe_headline if c.isalnum() or c == '_')
    output_path = f"output/{safe_news_type}_{safe_headline}_{timestamp}.mp4"
    
    # Ensure background music exists
    try:
        music_path = ensure_music_exists(news_type, force_download=force_music)
        if music_path:
            print(f"[OK] Background music ready")
    except Exception as e:
        print(f"[WARN] Music check failed: {e}")
    
    # Build script
    print("→ Building script...")
    try:
        english = build_english_script(scene_data)
        hindi = translate_to_hindi(english)
        print("[OK] Script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return None
    
    # Generate audio
    print("→ Generating audio...")
    try:
        audio_file = generate_audio(hindi)
        print(f"[OK] Audio generated")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        return None
    
    # Fetch images
    print("→ Fetching images...")
    try:
        images = fetch_images(scene_data)
        print(f"[OK] Fetched {len(images)} images")
    except Exception as e:
        print(f"[WARN] Image fetching had issues: {e}")
        images = []
    
    # Create video
    print(f"→ Creating video...")
    try:
        video_path = make_short_video(
            images=images,
            audio_path=audio_file,
            english_text=english,
            headline=scene_data["headline"],
            hook=scene_data["hook_text"],
            subscribe_hook=scene_data["subscribe_hook"],
            news_type=news_type,
            output_path=output_path
        )
        print(f"[SUCCESS] Scene {scene_index + 1} video created: {video_path}")
        return video_path
    except Exception as e:
        print(f"[ERROR] Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Generator - Multi-Scene Support")
    parser.add_argument("--json", default="data.json", help="Input JSON file (can be single object or array)")
    parser.add_argument("--scene", type=int, help="Process only a specific scene (0-based index)")
    parser.add_argument("--upload", action="store_true", help="Upload after creation")
    parser.add_argument("--force-music-download", action="store_true", 
                       help="Force re-download of background music")
    parser.add_argument("--config-check", action="store_true", 
                       help="Check configuration and exit")
    parser.add_argument("--combine", action="store_true",
                       help="Combine all scenes into one video (NOT IMPLEMENTED YET)")
    args = parser.parse_args()

    # Optional: Just check config and exit
    if args.config_check:
        print("\n" + "="*50)
        print("CONFIGURATION CHECK")
        print("="*50)
        print(f"Video Dimensions: {config.VIDEO_WIDTH}x{config.VIDEO_HEIGHT}")
        print(f"FPS: {config.FPS}")
        print(f"Auto-download music: {config.AUDIO['auto_download_music']}")
        print("="*50)
        return

    # Check dependencies
    check_dependencies()

    # Create necessary directories
    Path("output").mkdir(exist_ok=True)
    Path("temp").mkdir(exist_ok=True)
    Path("background_music").mkdir(exist_ok=True)

    # Load and parse JSON
    print(f"\n[START] Loading JSON: {args.json}")
    try:
        with open(args.json, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON: {e}")
        sys.exit(1)
    
    # Check if it's an array (multiple scenes) or single object
    if isinstance(raw_data, list):
        scenes = raw_data
        print(f"[INFO] Detected {len(scenes)} scenes in JSON file")
    else:
        scenes = [raw_data]
        print("[INFO] Detected single scene in JSON file")
    
    # Validate each scene has required fields
    valid_scenes = []
    for i, scene in enumerate(scenes):
        required_fields = ["headline", "hook_text", "details", "subscribe_hook"]
        missing = [f for f in required_fields if f not in scene]
        if missing:
            print(f"[WARN] Scene {i+1} missing fields: {missing} - skipping")
        else:
            valid_scenes.append(scene)
    
    if not valid_scenes:
        print("[ERROR] No valid scenes found")
        sys.exit(1)
    
    print(f"[INFO] Processing {len(valid_scenes)} valid scenes")
    
    # Filter to specific scene if requested
    if args.scene is not None:
        if 0 <= args.scene < len(valid_scenes):
            valid_scenes = [valid_scenes[args.scene]]
            print(f"[INFO] Processing only scene {args.scene}")
        else:
            print(f"[ERROR] Scene {args.scene} not found (0-{len(valid_scenes)-1})")
            sys.exit(1)
    
    # Check if combining videos is requested (feature not yet implemented)
    if args.combine:
        print("[WARN] Combining videos is not yet implemented")
        print("[INFO] Will process scenes individually instead")
    
    # Generate timestamp for this run
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Process each scene
    created_videos = []
    for i, scene in enumerate(valid_scenes):
        video_path = process_single_scene(
            scene_data=scene,
            scene_index=i,
            total_scenes=len(valid_scenes),
            timestamp=timestamp,
            force_music=args.force_music_download
        )
        
        if video_path:
            created_videos.append({
                'path': video_path,
                'scene': scene,
                'index': i
            })
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Successfully created: {len(created_videos)}/{len(valid_scenes)} videos")
    
    for vid in created_videos:
        file_size = os.path.getsize(vid['path']) / (1024 * 1024)
        print(f"  • Scene {vid['index']+1}: {vid['path']} ({file_size:.2f} MB)")
    
    # Upload options
    if created_videos and args.upload:
        print("\n" + "-"*60)
        print("Upload Options:")
        print("  1 = Upload all videos")
        print("  2 = Select videos to upload")
        print("  3 = Skip upload")
        print("-"*60)
        
        upload_choice = input("Your choice (1/2/3): ").strip()
        
        if upload_choice == "1":
            for vid in created_videos:
                meta = vid['scene'].get("metadata", {})
                print(f"\n→ Uploading scene {vid['index']+1}...")
                try:
                    upload_video(
                        video_path=vid['path'],
                        title=meta.get("title", vid['scene']["headline"]),
                        description=meta.get("description", ""),
                        tags=meta.get("tags", [])
                    )
                    print(f"[OK] Uploaded scene {vid['index']+1}")
                except Exception as e:
                    print(f"[ERROR] Upload failed for scene {vid['index']+1}: {e}")
        
        elif upload_choice == "2":
            for vid in created_videos:
                choice = input(f"\nUpload scene {vid['index']+1}? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    meta = vid['scene'].get("metadata", {})
                    try:
                        upload_video(
                            video_path=vid['path'],
                            title=meta.get("title", vid['scene']["headline"]),
                            description=meta.get("description", ""),
                            tags=meta.get("tags", [])
                        )
                        print(f"[OK] Uploaded scene {vid['index']+1}")
                    except Exception as e:
                        print(f"[ERROR] Upload failed: {e}")
    
    # Preview option
    if created_videos:
        preview = input("\nPreview a video? (enter scene number or 'n'): ").strip()
        if preview.isdigit():
            idx = int(preview) - 1
            if 0 <= idx < len(created_videos):
                video_path = created_videos[idx]['path']
                print(f"Opening {video_path}...")
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(os.path.abspath(video_path))
                    elif os.name == 'posix':  # macOS/Linux
                        os.system(f'xdg-open "{os.path.abspath(video_path)}"')
                except Exception as e:
                    print(f"[WARNING] Auto-open failed: {e}")
    
    print("\n[ALL DONE] Thank you for using YouTube Shorts Generator!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)