import re
from typing import List
from models.content_item import ContentItem
from config import CATEGORIES_DB   # ← Usamos tu config original

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Limpieza útil para Markdown y X
    cleaned = text.encode("ascii", "ignore").decode("ascii")
    return cleaned.replace("|", "-").replace("\n", " ").strip()


def classify_item(item: ContentItem) -> ContentItem:
    """Versión mejorada: combina lo bueno de classifier_old + ContentItem"""
    text_to_analyze = f"{item.title} {item.summary or ''} {' '.join(item.tags)}"
    text_clean = clean_text(text_to_analyze).lower()

    # Priorizamos por orden de CATEGORIES_DB (importante)
    for category, keywords in CATEGORIES_DB.items():
        if any(re.search(r'\b' + re.escape(kw.lower()) + r'\b', text_clean) for kw in keywords):
            item.add_category(category)
            item.add_tag(category.lower())
            break  # Tomamos la primera coincidencia más prioritaria

    if not item.categories:
        item.add_category("Otros")

    return item


def classify_batch(items: List[ContentItem]) -> List[ContentItem]:
    return [classify_item(item) for item in items]