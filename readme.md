## Expected JSON Input Schema

All fields are **required** unless noted otherwise.

```json
{
  "day": "Sunday",                     // string
  "date": "2026-02-22",                // YYYY-MM-DD
  "location": "Bandra, Mumbai",
  "type": "EntertainmentNews",
  "news_type": "Bollywood",            // used to choose image source
  "channel": "TrendWave Now",
  "headline": "...",
  "hook_text": "...",
  "details": "...",
  "subscribe_hook": "...",
  "metadata": {
    "title": "...",
    "description": "...",
    "tags": ["array", "of", "strings"],
    "search_key": "...",
    "aspect_ratio": "9:16_FILL"        // optional, default 9:16_FILL
  }
}