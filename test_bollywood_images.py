# test_bollywood_images.py
# Standalone test script for fetching images related to Deepika-Ranveer or other Bollywood scenes

import requests
from pathlib import Path
import time
import config  # your config.py with PEXELS_API_KEY

def fetch_bollywood_images(
    query: str = "Deepika Padukone Ranveer Singh family twins spotted",
    count: int = 6,
    save_folder: str = "temp/test_bollywood_images"
) -> list[Path]:
    print("\n" + "="*60)
    print("Bollywood Image Fetch Test")
    print("="*60)
    print(f"Query: {query}")
    print(f"Count: {count}")
    print(f"Pexels key length: {len(config.PEXELS_API_KEY) if config.PEXELS_API_KEY else 0} chars")

    images = []
    temp_dir = Path(save_folder)
    temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving to: {temp_dir.resolve()}\n")

    # ───────────────────────────────────────────────
    # Try Pexels first
    # ───────────────────────────────────────────────
    if config.PEXELS_API_KEY and config.PEXELS_API_KEY != "your_pexels_key_here":
        print("[1] Trying Pexels API...")
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": config.PEXELS_API_KEY}
            params = {
                "query": query,
                "per_page": count,
                "orientation": "portrait",  # better for Shorts
            }
            print(f"  → URL: {url}")
            print(f"  → Params: {params}")

            r = requests.get(url, params=params, headers=headers, timeout=12)
            print(f"  → Status: {r.status_code}")

            if r.status_code == 200:
                data = r.json()
                photos = data.get("photos", [])
                print(f"  → Found {len(photos)} photos")

                for i, photo in enumerate(photos[:count]):
                    img_url = photo["src"].get("large2x") or photo["src"].get("large")
                    if img_url:
                        img_url += "?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop"
                        img_path = temp_dir / f"pexels_{i:02d}_{int(time.time())}.jpg"
                        print(f"  → Downloading {img_url[:80]}...")
                        try:
                            img_data = requests.get(img_url, timeout=10).content
                            with open(img_path, "wb") as f:
                                f.write(img_data)
                            size_kb = img_path.stat().st_size / 1024
                            print(f"  → Saved: {img_path.name} ({size_kb:.1f} KB)")
                            images.append(img_path)
                        except Exception as e:
                            print(f"  → Download failed: {e}")
            else:
                print(f"  → API error: {r.text[:200]}...")
        except Exception as e:
            print(f"[ERROR] Pexels failed: {e}")
    else:
        print("[WARNING] No valid Pexels key → skipping")

    print(f"\nImages after Pexels: {len(images)} / {count}")

    # ───────────────────────────────────────────────
    # Fallback: generic Bollywood keywords
    # ───────────────────────────────────────────────
    if len(images) < count:
        print("\n[2] Pexels not enough → using generic Bollywood fallback queries")
        fallback_queries = [
            "Bollywood celebrity couple",
            "Indian actress red carpet",
            "Deepika Padukone portrait",
            "Ranveer Singh actor",
            "Bollywood family moment"
        ]

        for fb_query in fallback_queries:
            if len(images) >= count:
                break
            print(f"  Trying fallback: {fb_query}")
            try:
                r = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": fb_query, "per_page": count - len(images), "orientation": "portrait"},
                    headers={"Authorization": config.PEXELS_API_KEY},
                    timeout=10
                )
                if r.status_code == 200:
                    photos = r.json().get("photos", [])
                    for photo in photos:
                        if len(images) >= count:
                            break
                        img_url = photo["src"].get("large")
                        if img_url:
                            img_path = temp_dir / f"fallback_{len(images):02d}.jpg"
                            img_data = requests.get(img_url, timeout=8).content
                            with open(img_path, "wb") as f:
                                f.write(img_data)
                            images.append(img_path)
                            print(f"  → Fallback saved: {img_path.name}")
            except Exception as e:
                print(f"  Fallback failed: {e}")

    # Final fallback: black if still nothing
    while len(images) < count:
        print("  Using pure black fallback")
        from PIL import Image
        black = Image.new("RGB", (1080, 1920), (20, 20, 40))
        p = temp_dir / f"black_fallback_{len(images):02d}.jpg"
        black.save(p)
        images.append(p)

    print("\n" + "="*60)
    print("Final results:")
    for i, p in enumerate(images):
        size = p.stat().st_size / 1024 if p.exists() else 0
        print(f"  {i+1}. {p.name}  ({size:.1f} KB)  Exists: {p.exists()}")
    print("="*60 + "\n")

    return images

if __name__ == "__main__":
    # Test with Deepika-Ranveer scene
    fetch_bollywood_images(
        query="Deepika Padukone Ranveer Singh twins family spotted Mumbai",
        count=6
    )

    # You can also test other queries like this:
    # fetch_bollywood_images("Virat Kohli Anushka Sharma family airport", count=5)