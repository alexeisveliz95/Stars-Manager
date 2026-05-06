from typing import List, Callable
from models.content_item import ContentItem
from processors.pipeline import process_content_items


class PipelineRunner:
    """Motor simple pero potente para ejecutar pipelines."""

    def __init__(self):
        self.steps: List[Callable] = []

    def add_step(self, step: Callable):
        self.steps.append(step)
        return self

    def run(self, items: List[ContentItem]) -> List[ContentItem]:
        """Ejecuta todo el pipeline."""
        print(f"🚀 Ejecutando pipeline con {len(items)} items...")

        for step in self.steps:
            items = step(items)

        return items


# Pipeline por defecto recomendado
def create_default_pipeline() -> PipelineRunner:
    runner = PipelineRunner()
    runner.add_step(process_content_items)
    return runner