# processors/scorer.py
from typing import List
from models.content_item import ContentItem


def calculate_score(item: ContentItem) -> ContentItem:
    """
    Calcula un score compuesto (0.0 - 1.0) muy equilibrado.
    Combina momentum, calidad del contenido, relevancia y categoría.
    """
    # Base score
    base_score = item.score if item.score > 0 else 0.45

    # === 1. Momentum (crecimiento) - Muy importante para Trending ===
    if item.momentum > 0:
        # Log scaling para evitar que items con crecimiento extremo dominen
        momentum_bonus = min(0.40, (item.momentum ** 0.6) * 0.18)
    else:
        momentum_bonus = 0.0

    # === 2. Calidad del contenido ===
    quality_bonus = 0.0
    if item.summary:
        length = len(item.summary)
        if length > 180:
            quality_bonus += 0.18
        elif length > 100:
            quality_bonus += 0.12
        elif length > 50:
            quality_bonus += 0.06

    # Bonus por lenguaje (inglés suele ser mejor para contenido global)
    if item.language and item.language.lower() in {"english", "en", "python", "javascript", "typescript"}:
        quality_bonus += 0.08

    # === 3. Relevancia por categorías ===
    high_value_categories = {"AI", "Security", "Tools", "DevOps", "LLM"}
    category_bonus = 0.0
    
    for cat in item.categories:
        if cat in high_value_categories:
            category_bonus = max(category_bonus, 0.22)
        elif cat in {"Web", "Data", "Mobile"}:
            category_bonus = max(category_bonus, 0.12)

    # === 4. Bonus por metadata adicional ===
    metadata_bonus = 0.0
    if item.raw_data:
        stars = item.raw_data.get("stargazers_count") or item.raw_data.get("stars", 0)
        if stars > 5000:
            metadata_bonus += 0.10
        elif stars > 1000:
            metadata_bonus += 0.05

    # === Cálculo final ===
    final_score = base_score + momentum_bonus + quality_bonus + category_bonus + metadata_bonus

    # Normalizar y redondear
    item.score = round(min(1.0, final_score), 3)
    return item


def rank_items(items: List[ContentItem], top_n: int = 20) -> List[ContentItem]:
    """
    Rankea los items por score y devuelve los mejores.
    """
    # Calculamos score para todos
    for item in items:
        calculate_score(item)

    # Ordenamos
    sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
    
    return sorted_items[:top_n]


def get_top_by_category(items: List[ContentItem], category: str, top_n: int = 5) -> List[ContentItem]:
    """Devuelve los mejores items de una categoría específica."""
    filtered = [item for item in items if category in item.categories]
    for item in filtered:
        calculate_score(item)
    
    return sorted(filtered, key=lambda x: x.score, reverse=True)[:top_n]