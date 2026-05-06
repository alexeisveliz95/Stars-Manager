from typing import List
from models.content_item import ContentItem

def calculate_score(item: ContentItem) -> float:
    """Calcula score compuesto (0-1) basado en múltiples factores."""
    base = getattr(item, 'score', 0.5)
    
    # Bonus por momentum (crecimiento)
    momentum_bonus = min(0.35, getattr(item, 'momentum', 0) * 0.12)
    
    # Bonus por categorías de alto valor
    high_value = {"AI", "Security", "Tools", "DevOps"}
    cat_bonus = 0.25 if any(cat in high_value for cat in item.categories) else 0.0
    
    # Bonus por calidad de descripción
    desc_bonus = 0.15 if item.summary and len(item.summary) > 80 else 0.0
    
    final_score = min(1.0, base + momentum_bonus + cat_bonus + desc_bonus)
    item.score = round(final_score, 3)
    return item.score


def rank_items(items: List[ContentItem], top_n: int = 15) -> List[ContentItem]:
    """Rankea y devuelve los mejores items."""
    for item in items:
        calculate_score(item)
    
    sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
    return sorted_items[:top_n]