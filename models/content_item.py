from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Any

class ContentItem(BaseModel):
    """Modelo unificado para cualquier pieza de contenido (repos, noticias, reportes, etc.)."""
    id: str
    source: str                      # github_trending, hackerone, reddit, rss...
    title: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    summary: Optional[str] = None
    full_text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    score: float = 0.0               # 0.0 a 1.0 (momentum + relevancia)
    momentum: float = 0.0            # Solo para trending (stars growth, etc.)
    language: Optional[str] = None
    owner: Optional[str] = None
    
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_tag(self, tag: str):
        if tag.lower() not in [t.lower() for t in self.tags]:
            self.tags.append(tag)

    def add_category(self, cat: str):
        if cat not in self.categories:
            self.categories.append(cat)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}