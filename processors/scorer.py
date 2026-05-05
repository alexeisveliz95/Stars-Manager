from typing import List
from models.content_item import ContentItem

def calculate_score(item: ContentItem) -> float:
    """Calcula score compuesto (0-1)."""
    base = item.score  # score inicial
    
    # Bonus por momentum
    momentum_bonus = min(0.3, item.momentum * 0.1)
    
    # Bonus por categorías de alto valor
    high_value_cats = {"AI", "Security", "Tools", "LLM"}
    cat_bonus = 0.2 if any(cat in high_value_cats for cat in item.categories) else 0.0
    
    # Bonus por longitud de descripción
    desc_bonus = 0.1 if item.summary and len(item.summary) > 100 else 0.0
    
    final_score = min(1.0, base + momentum_bonus + cat_bonus + desc_bonus)
    item.score = round(final_score, 3)
    return item.score


def rank_items(items: List[ContentItem], top_n: int = 20) -> List[ContentItem]:
    """Rankea y devuelve los mejores items."""
    for item in items:
        calculate_score(item)
    
    sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
    return sorted_items[:top_n]