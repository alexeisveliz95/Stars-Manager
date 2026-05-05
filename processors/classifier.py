import re
from typing import List
from models.content_item import ContentItem

# Carga desde config/categories.yaml en producción
CATEGORIES = {
    "AI": ["llm", "gpt", "llama", "groq", "ai ", "machine learning", "deep learning"],
    "Security": ["security", "vulnerability", "exploit", "hackerone", "cve", "pentest"],
    "Tools": ["tool", "cli", "framework", "library", "devtool"],
    "Web": ["react", "nextjs", "tailwind", "frontend"],
    # Añade más...
}

def classify_item(item: ContentItem) -> ContentItem:
    """Clasifica usando reglas + fallback LLM (opcional)."""
    text = f"{item.title} {item.summary or ''} {item.raw_data}".lower()
    
    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            item.add_category(category)
            item.add_tag(category.lower())
    
    # Si no tiene categorías, marcar como "General"
    if not item.categories:
        item.add_category("General")
    
    return item


def classify_batch(items: List[ContentItem]) -> List[ContentItem]:
    return [classify_item(item) for item in items]