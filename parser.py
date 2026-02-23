# parser.py
"""Parse and validate input JSON with Pydantic"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator, ValidationError
import json

class Metadata(BaseModel):
    title: str
    description: str
    tags: List[str]
    search_key: str
    aspect_ratio: str = Field(default="9:16_FILL")

    # New SEO fields (optional)
    youtube_title_options: Optional[List[str]] = None
    youtube_description_options: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    thumbnail_text_overlay: Optional[str] = None
    video_keywords: Optional[str] = None
    target_audience: Optional[str] = None

    class Config:
        extra = "forbid"  # reject unknown fields

class NewsInput(BaseModel):
    day: str
    date: str
    location: str
    type: str
    news_type: str
    channel: str
    headline: str = Field(..., min_length=5)
    hook_text: str = Field(..., min_length=10)
    details: str = Field(..., min_length=50)
    subscribe_hook: str = Field(..., min_length=10)
    metadata: Metadata

    @validator('date')
    def validate_date_format(cls, v):
        if not len(v.split('-')) == 3:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    class Config:
        extra = "forbid"

def parse_input(json_path: str | Path) -> Dict[str, Any]:
    path = Path(json_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    with open(path, encoding="utf-8") as f:
        raw_data = json.load(f)

    try:
        validated = NewsInput(**raw_data)
        print("[VALIDATION] JSON is valid ✓")
        return validated.dict()
    except ValidationError as e:
        print("\n" + "═"*80)
        print("JSON VALIDATION ERROR")
        print("═"*80)
        print("Errors:")
        for err in e.errors():
            print(f"  → {err['loc']}: {err['msg']}")
        print("\nExpected schema:")
        print(NewsInput.schema_json(indent=2))
        print("═"*80)
        raise ValueError("Invalid JSON structure") from e