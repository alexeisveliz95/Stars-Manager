from typing import List
from models.content_item import ContentItem
from .classifier import classify_batch
from .scorer import rank_items


def process_content_items(items: List[ContentItem]) -> List[ContentItem]:
    """Pipeline completo: clasifica → puntúa → rankea"""
    items = classify_batch(items)
    items = rank_items(items, top_n=25)
    return items