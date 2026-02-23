"""Hybrid image fetcher for YouTube Shorts
- Google Images (SerpApi) for cricket, Bollywood, entertainment
- Pexels for space, AI, gadgets, general / conceptual news
"""

import requests
from pathlib import Path
from typing import List, Dict, Any
import config
import time
import hashlib  # to detect true duplicate content

def fetch_images(data: Dict[str, Any], count: int = 6) -> List[Path]:
    """
    Main function to fetch relevant images based on topic.
    Returns list of Path objects to downloaded images.
    """
    print("\n" + "═"*70)
    print("IMAGE FETCH START")
    print("═"*70)

    news_type = data.get("news_type", "").lower()
    channel = data.get("channel", "").lower()
    search_key = data.get("metadata", {}).get("search_key", "")
    headline = data.get("headline", "")

    # ───────────────────────────────────────────────
    # Decide which source to prefer
    # ───────────────────────────────────────────────
    use_google = any(
        kw in news_type or kw in channel.lower() or kw in headline.lower()
        for kw in ["cricket", "sports", "ipl", "bollywood", "entertainment", "celebrity", "actor", "actress"]
    )

    print(f"[DECISION] Use Google Images first: {use_google}")
    print(f"  news_type  = {news_type}")
    print(f"  channel    = {channel}")
    print(f"  headline   = {headline[:80]}...")
    print(f"  search_key = {search_key[:80]}...")

    images = []
    temp_dir = Path("temp/images")
    temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Temp folder: {temp_dir.resolve()}")

    # ───────────────────────────────────────────────
    # Google Images – for cricket / Bollywood / entertainment
    # ───────────────────────────────────────────────
    if use_google and hasattr(config, "SERPAPI_KEY") and config.SERPAPI_KEY:
        print("[Google] Starting multi-query search...")
        base_queries = [
            search_key or headline,
            f"{headline} photos 2026",
            f"{news_type} news images today",
            f"{channel} viral photos",
            f"{data.get('location', '')} spotted celebrity"
        ]
        queries = [q for q in base_queries if q.strip()][:5]  # max 5 unique
        print(f"[Google] Using {len(queries)} refined queries")

        all_urls = []
        seen_hashes = set()

        for q in queries:
            try:
                params = {
                    "engine": "google_images",
                    "q": q,
                    "api_key": config.SERPAPI_KEY,
                    "tbs": "isz:lt,islt:qsvga,cdr:1,cd_min:1/1/2025",  # recent + large
                    "num": count * 3
                }
                r = requests.get("https://serpapi.com/search.json", params=params, timeout=15)
                print(f"  Query '{q[:50]}...': Status {r.status_code}")

                if r.status_code == 200:
                    results = r.json().get("images_results", [])
                    print(f"    → {len(results)} results")
                    for img in results:
                        src = img.get("original") or img.get("link")
                        if src and src not in all_urls:
                            all_urls.append(src)
                else:
                    print(f"    → Error: {r.text[:200]}...")
            except Exception as e:
                print(f"  Query failed: {e}")

        # Download best unique images
        downloaded = []
        for i, src_url in enumerate(all_urls):
            if len(downloaded) >= count:
                break

            try:
                ext = src_url.split('.')[-1].split('?')[0].lower() or 'jpg'
                img_path = temp_dir / f"google_{i:02d}_{int(time.time())}.{ext}"

                img_resp = requests.get(src_url, timeout=12, stream=True)
                if img_resp.status_code != 200:
                    continue

                img_data = img_resp.content
                size_kb = len(img_data) / 1024
                if size_kb < 50:
                    print(f"  Skip small: {size_kb:.1f} KB")
                    continue

                # Duplicate check by content hash
                img_hash = hashlib.md5(img_data).hexdigest()
                if img_hash in seen_hashes:
                    print("  Skip duplicate")
                    continue
                seen_hashes.add(img_hash)

                with open(img_path, "wb") as f:
                    f.write(img_data)
                print(f"[Google] Saved: {img_path.name} ({size_kb:.1f} KB)")
                downloaded.append(img_path)

            except Exception as e:
                print(f"  Download failed: {e}")

        images.extend(downloaded)
        print(f"[Google] Collected {len(downloaded)} valid images")

    # ───────────────────────────────────────────────
    # Pexels fallback / primary for non-celeb/sports topics
    # ───────────────────────────────────────────────
    if len(images) < count:
        print("[Pexels] Starting fallback / primary search...")
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": config.PEXELS_API_KEY}
            params = {
                "query": search_key or headline,
                "per_page": count - len(images),
                "orientation": "portrait"
            }
            r = requests.get(url, params=params, headers=headers, timeout=15)
            print(f"[Pexels] Status: {r.status_code}")

            if r.status_code == 200:
                photos = r.json().get("photos", [])
                print(f"[Pexels] Found {len(photos)} photos")

                for i, photo in enumerate(photos):
                    img_url = photo["src"].get("large2x") or photo["src"].get("large")
                    if img_url:
                        img_url += "?w=1080&h=1920&fit=crop&auto=compress"
                        img_path = temp_dir / f"pexels_{len(images):02d}.jpg"
                        img_data = requests.get(img_url, timeout=10).content
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        print(f"[Pexels] Saved: {img_path.name}")
                        images.append(img_path)
            else:
                print(f"[Pexels] Error: {r.text[:200]}...")
        except Exception as e:
            print(f"[Pexels] Error: {e}")

    # ───────────────────────────────────────────────
    # Ultimate fallback: black images
    # ───────────────────────────────────────────────
    while len(images) < count:
        from PIL import Image
        black = Image.new("RGB", (1080, 1920), (10,10,30))
        p = temp_dir / f"fallback_{len(images):02d}.jpg"
        black.save(p)
        images.append(p)
        print(f"[FALLBACK] Created black placeholder: {p.name}")

    print(f"[IMAGE FETCH END] Returning {len(images)} images")
    return images[:count]