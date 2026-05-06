# models/content_item.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Any


class ContentItem(BaseModel):
    """Modelo universal para todo el pipeline."""
    # Identity
    id: str
    source: str                      # github_trending, github_stars, hackerone, reddit, etc.

    # Core
    title: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Content
    summary: Optional[str] = None
    full_text: Optional[str] = None

    # Classification
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

    # Scoring
    score: float = 0.0
    momentum: float = 0.0

    # Metadata
    language: Optional[str] = None
    owner: Optional[str] = None

    # Raw data preservation
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_tag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower not in [t.lower() for t in self.tags]:
            self.tags.append(tag)

    def add_category(self, category: str):
        if category not in self.categories:
            self.categories.append(category)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }