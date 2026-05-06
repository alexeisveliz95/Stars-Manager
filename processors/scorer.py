# processors/scorer.py
from typing import List
from models.content_item import ContentItem

def calculate_score(item: ContentItem) -> ContentItem:
    """Calcula score compuesto."""
    base = item.score if item.score > 0 else 0.4

    momentum_bonus = min(0.35, item.momentum * 0.15)
    high_value_bonus = 0.25 if any(cat in {"AI", "Security", "Tools"} for cat in item.categories) else 0.0
    desc_bonus = 0.15 if item.summary and len(item.summary) > 100 else 0.0

    item.score = round(min(1.0, base + momentum_bonus + high_value_bonus + desc_bonus), 3)
    return item


def rank_items(items: List[ContentItem], top_n: int = 20) -> List[ContentItem]:
    for item in items:
        calculate_score(item)
    return sorted(items, key=lambda x: x.score, reverse=True)[:top_n]