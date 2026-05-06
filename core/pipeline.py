# core/pipeline.py
from typing import List
from models.content_item import ContentItem

from processors.classifier import classify_batch
from processors.scorer import rank_items
from processors.markdown_gen import save_all_files


def full_content_pipeline() -> List[ContentItem]:
    """
    Pipeline completo automático:
    Scrape → Normalize → Classify → Score → Export
    """
    from connectors.inputs.trending import get_trending_repos

    print("🚀 Iniciando Pipeline Completo...")

    # 1. Obtener datos crudos como ContentItem
    items = get_trending_repos()

    if not items:
        print("⚠️ No se obtuvieron items")
        return []

    # 2. Procesamiento completo
    items = classify_batch(items)
    items = rank_items(items, top_n=30)

    # 3. Exportar Markdown (manteniendo tu estética premium)
    save_all_files(items)

    print(f"✅ Pipeline completado: {len(items)} items procesados")
    return items