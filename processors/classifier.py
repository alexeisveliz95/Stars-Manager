# processors/classifier.py
import re
from typing import List
from models.content_item import ContentItem

CATEGORIES = {
    "AI": ["llm", "gpt", "llama", "groq", "openai", "anthropic", "neural", "deep learning"],
    "Security": ["security", "vulnerability", "exploit", "hackerone", "cve", "pentest", "bug bounty"],
    "Tools": ["tool", "cli", "framework", "library", "devtool", "utility"],
    "Web": ["react", "nextjs", "tailwind", "frontend", "vue", "svelte"],
    "DevOps": ["docker", "kubernetes", "ci/cd", "terraform"],
    # Agrega más según necesites
}

def classify_item(item: ContentItem) -> ContentItem:
    """Clasifica y muta el item (retorna para chaining)."""
    if not item.title and not item.summary:
        item.add_category("General")
        return item

    text = f"{item.title} {item.summary or ''} {str(item.raw_data)}".lower()

    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            item.add_category(category)
            item.add_tag(category.lower())

    if not item.categories:
        item.add_category("General")

    return item


def classify_batch(items: List[ContentItem]) -> List[ContentItem]:
    return [classify_item(item) for item in items]