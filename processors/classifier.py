import re
from typing import List, Dict
from models.content_item import ContentItem

# Carga desde config/categories.yaml en el futuro
CATEGORIES: Dict[str, List[str]] = {
    "AI": ["llm", "gpt", "llama", "groq", "openai", "anthropic", "machine learning", "deep learning", "neural"],
    "Security": ["security", "vulnerability", "exploit", "hackerone", "cve", "pentest", "bug bounty"],
    "Tools": ["tool", "cli", "framework", "library", "devtool", "utility"],
    "Web": ["react", "nextjs", "tailwind", "frontend", "vue", "svelte"],
    "Data": ["pandas", "sql", "data", "analytics", "mlops"],
    "DevOps": ["docker", "kubernetes", "ci/cd", "terraform", "ansible"],
    # Añade más según necesites
}

def classify_item(item: ContentItem) -> ContentItem:
    """Clasifica un item usando reglas + posible fallback a LLM."""
    if not item.title and not item.summary:
        item.add_category("General")
        return item

    text = f"{item.title} {item.summary or ''} {str(item.raw_data)}".lower()

    matched = False
    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            item.add_category(category)
            item.add_tag(category.lower())
            matched = True

    if not matched:
        item.add_category("General")

    return item


def classify_batch(items: List[ContentItem]) -> List[ContentItem]:
    """Clasifica una lista completa de items."""
    return [classify_item(item) for item in items]