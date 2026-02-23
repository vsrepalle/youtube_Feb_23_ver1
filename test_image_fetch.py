# test_image_fetch.py
# Run this file alone to test only image fetching

import sys
from pathlib import Path
from image_fetch import fetch_images
import config  # to access UNSPLASH_ACCESS_KEY

def main():
    # You can change these test values
    test_search_key = "cricket match stadium India 2026"
    test_count = 5

    print("=== Testing image_fetch.py ===")
    print(f"Search key: {test_search_key}")
    print(f"Requested count: {test_count}")
    print(f"Unsplash key in config: {'YES (length {len(config.UNSPLASH_ACCESS_KEY)})' if config.UNSPLASH_ACCESS_KEY != 'your_unsplash_access_key_here' else 'NO / placeholder'}")
    print("")

    try:
        images = fetch_images(
            search_key=test_search_key,
            count=test_count
        )
        print("\nResults:")
        for i, img_path in enumerate(images):
            exists = img_path.exists()
            size_kb = img_path.stat().st_size / 1024 if exists else 0
            print(f"{i+1}. {img_path.name}")
            print(f"   Exists: {exists}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Full path: {img_path.resolve()}")
            print("-" * 50)
    except Exception as e:
        print(f"\n[ERROR] fetch_images failed: {type(e).__name__}")
        print(f"Details: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()