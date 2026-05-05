from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Any

class ContentItem(BaseModel):
    """Modelo central unificado para todo el contenido."""
    id: str
    source: str
    title: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    summary: Optional[str] = None
    full_text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)  # AI, Security, Tools, etc.
    
    score: float = 0.0  # Relevancia (0-1)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }