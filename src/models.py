from pydantic import BaseModel, Field
from typing import List, Optional

class Repo(BaseModel):
    name: str
    html_url: str
    description: Optional[str] = None
    stars: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    category: Optional[str] = "Otros"