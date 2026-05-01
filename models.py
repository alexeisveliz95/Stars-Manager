from pydantic import BaseModel
from typing import List, Optional

class Repo(BaseModel):
    name: str
    html_url: str
    description: Optional[str]
    stars: int
    language: Optional[str]
    topics: List[str]
    category: Optional[str] = "Otros"