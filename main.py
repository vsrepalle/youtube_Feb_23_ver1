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

from parser import parse_input
from script_gen import build_english_script, translate_to_hindi
from audio_gen import generate_audio
from image_fetch import fetch_images
from video_compose import make_short_video
from uploader import upload_video


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Generator")
    parser.add_argument("--json", default="data.json", help="Input JSON file")
    parser.add_argument("--upload", action="store_true", help="Upload after creation")
    args = parser.parse_args()

    print(f"[START] Processing JSON: {args.json}")
    data = parse_input(args.json)

    # Generate timestamped filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"output/final_short_{timestamp}.mp4"

    # ----------------------------------------------------------
    # CHECK IF FILE EXISTS
    # ----------------------------------------------------------
    if os.path.exists(output_path):
        print("\nExisting video detected:")
        print(output_path)
        print("\nChoose an option:")
        print("  1 = Upload existing video")
        print("  2 = Recreate video and upload")
        print("  3 = Skip and exit")

        choice = input("Your choice (1/2/3): ").strip()

        if choice == "1":
            meta = data["metadata"]
            print("→ Uploading existing video...")
            upload_video(
                video_path=output_path,
                title=meta["title"],
                description=meta["description"],
                tags=meta.get("tags", [])
            )
            return

        elif choice == "3":
            print("Skipped.")
            return

        # If option 2 → continue and recreate

    # ----------------------------------------------------------
    # CREATE VIDEO
    # ----------------------------------------------------------
    print("→ Building script...")
    english = build_english_script(data)
    hindi = translate_to_hindi(english)

    print("→ Generating audio...")
    audio_file = generate_audio(hindi)

    print("→ Fetching images...")
    images = fetch_images(data)

    print(f"[INFO] Video will be saved as: {output_path}")

    video_path = make_short_video(
        images=images,
        audio_path=audio_file,
        english_text=english,
        headline=data["headline"],
        hook=data["hook_text"],
        subscribe_hook=data["subscribe_hook"],
        output_path=output_path
    )

    print(f"[SUCCESS] Video created: {video_path}")

    # ----------------------------------------------------------
    # PREVIEW
    # ----------------------------------------------------------
    print("[PREVIEW] Opening video for review...")
    try:
        os.startfile(os.path.abspath(video_path))
    except Exception as e:
        print(f"[WARNING] Auto-open failed: {e}")
        print("Please open manually: " + str(Path(video_path).resolve()))

    # ----------------------------------------------------------
    # UPLOAD CONFIRMATION
    # ----------------------------------------------------------
    print("\n" + "-" * 60)
    print("Video is ready. Do you want to upload it?")
    print("  y = yes")
    print("  n = no")
    print("-" * 60)

    choice = input("Your choice (y/n): ").strip().lower()

    if choice in ['y', 'yes']:
        meta = data["metadata"]
        print("→ Starting YouTube upload...")
        upload_video(
            video_path=video_path,
            title=meta["title"],
            description=meta["description"],
            tags=meta.get("tags", [])
        )
        print("[UPLOAD] Process completed.")
    else:
        print("Upload skipped. Video is saved at:", video_path)


if __name__ == "__main__":
    main()