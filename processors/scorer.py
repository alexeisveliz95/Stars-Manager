from typing import List
from models.content_item import ContentItem


def calculate_score(item: ContentItem) -> ContentItem:
    """Scoring avanzado y equilibrado."""
    base = max(item.score, 0.4)

    # Momentum (crecimiento)
    momentum_bonus = min(0.42, (item.momentum ** 0.55) * 0.22) if item.momentum > 0 else 0.0

    # Calidad del summary
    quality_bonus = 0.0
    if item.summary:
        length = len(item.summary)
        if length > 200:      quality_bonus += 0.20
        elif length > 120:    quality_bonus += 0.14
        elif length > 60:     quality_bonus += 0.07

    # Categorías de alto valor
    high_value = {"AI", "Security", "Tools", "DevOps"}
    cat_bonus = 0.25 if any(c in high_value for c in item.categories) else 0.10

    # Metadata extra
    meta_bonus = 0.0
    stars = item.raw_data.get("stargazers_count") or item.raw_data.get("stars", 0)
    if stars > 8000:   meta_bonus += 0.12
    elif stars > 2000: meta_bonus += 0.07

    final = base + momentum_bonus + quality_bonus + cat_bonus + meta_bonus
    item.score = round(min(1.0, final), 3)
    return item


def rank_items(items: List[ContentItem], top_n: int = 20) -> List[ContentItem]:
    for item in items:
        calculate_score(item)
    return sorted(items, key=lambda x: x.score, reverse=True)[:top_n]