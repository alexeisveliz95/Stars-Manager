import re
from typing import List
from models.content_item import ContentItem

# Importar desde config más adelante
CATEGORIES_DB = {
    "AI": ["llm", "gpt", "llama", "groq", "anthropic", "openai", "deep learning", "neural", "ai "],
    "Security": ["security", "vulnerability", "exploit", "hackerone", "cve", "pentest", "bug bounty", "rce"],
    "Tools": ["tool", "cli", "framework", "library", "devtool", "utility"],
    "DevOps": ["docker", "kubernetes", "terraform", "ansible", "ci/cd"],
    "Web": ["react", "nextjs", "tailwind", "vue", "svelte", "frontend"],
    "Data": ["pandas", "sql", "mlops", "analytics"],
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.encode("ascii", "ignore").decode("ascii").replace("\n", " ").replace("|", "-").strip()


def classify_item(item: ContentItem) -> ContentItem:
    """Clasificación potente y prioritaria."""
    text = clean_text(f"{item.title} {item.summary or ''}").lower()

    for category, keywords in CATEGORIES_DB.items():
        for kw in keywords:
            if re.search(rf"\b{kw}\b", text):
                item.add_category(category)
                item.add_tag(category.lower())
                return item  # Prioridad alta: tomamos la primera coincidencia fuerte

    item.add_category("Otros")
    return item


def classify_batch(items: List[ContentItem]) -> List[ContentItem]:
    return [classify_item(item) for item in items]