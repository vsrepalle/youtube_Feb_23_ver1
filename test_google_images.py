# test_google_images_improved.py
# Fixed version: avoids duplicates, skips broken/invalid images, prefers full-size

import requests
from pathlib import Path
import time
import hashlib  # to detect duplicate content
import os

# ───────────────────────────────────────────────
# CONFIG
# ───────────────────────────────────────────────
SERPAPI_KEY = "4ec0080d442d1ccc962b952fc5b2ff84958f1b57932aec0c4090eeb22817025b"  # ← replace with real key
SAVE_FOLDER = "temp/google_images_test"

def fetch_google_images(query: str, count: int = 6, min_size_kb: int = 50) -> list[Path]:
    print("\n" + "═"*70)
    print(f"Scenario: {query}")
    print("═"*70)

    temp_dir = Path(SAVE_FOLDER)
    temp_dir.mkdir(parents=True, exist_ok=True)

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_images",
        "q": query,
        "api_key": SERPAPI_KEY,
        "tbs": "isz:lt,islt:qsvga,cdr:1,cd_min:1/1/2025",  # recent + large
        "num": 20  # fetch more → filter best
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        print(f"Status: {r.status_code} | Query: {query}")

        if r.status_code != 200:
            print("Error:", r.text[:300])
            return []

        data = r.json()
        results = data.get("images_results", [])
        print(f"Total results from SerpApi: {len(results)}")

        downloaded = []
        seen_hashes = set()  # avoid true duplicates

        for i, img in enumerate(results):
            if len(downloaded) >= count:
                break

            src_url = img.get("original") or img.get("link")
            if not src_url or "thumbnail" in src_url.lower():
                continue

            # Clean URL (remove tracking params)
            src_url = src_url.split('?')[0]

            # Generate filename
            ext = src_url.split('.')[-1].split('&')[0].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                ext = 'jpg'
            filename = f"google_{i:02d}_{int(time.time())}.{ext}"
            img_path = temp_dir / filename

            print(f"  Trying → {src_url[:80]}...")

            try:
                img_resp = requests.get(src_url, timeout=12, stream=True)
                if img_resp.status_code != 200:
                    print(f"    Skip (status {img_resp.status_code})")
                    continue

                # Read content and check size
                img_data = img_resp.content
                size_kb = len(img_data) / 1024
                if size_kb < min_size_kb:
                    print(f"    Skip (too small: {size_kb:.1f} KB)")
                    continue

                # Check duplicate by hash
                img_hash = hashlib.md5(img_data).hexdigest()
                if img_hash in seen_hashes:
                    print(f"    Skip (duplicate hash)")
                    continue
                seen_hashes.add(img_hash)

                with open(img_path, "wb") as f:
                    f.write(img_data)

                print(f"    Saved: {filename} ({size_kb:.1f} KB)")
                downloaded.append(img_path)

            except Exception as e:
                print(f"    Failed: {str(e)[:60]}")

        print(f"Success: {len(downloaded)} unique images saved")
        return downloaded

    except Exception as e:
        print(f"Request failed: {e}")
        return []

if __name__ == "__main__":
    scenarios = [
        "Deepika Padukone Ranveer Singh twins spotted Mumbai February 2026",
        "Virat Kohli Anushka Sharma airport family 2026",
        "Rohit Sharma batting century Ahmedabad Test February 2026",
        "IPL 2026 match action photos today",
        "Kangana Ranaut latest controversy photos February 2026"
    ]

    for i, q in enumerate(scenarios, 1):
        print(f"\nScenario {i}/{len(scenarios)}")
        fetch_google_images(q, count=5)
        time.sleep(2)  # avoid rate limiting