from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from .workflow import Workflow
from ..connectors.outputs.telegram_logger import TelegramLogger


class Engine:
    """Orquestador central del Content & Intelligence Engine."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.logger = TelegramLogger()
        self.history = []

    def register_workflow(self, workflow: Workflow):
        self.workflows[workflow.name] = workflow
        print(f"📋 Workflow registrado: {workflow.name}")

    async def run_workflow(self, name: str, initial_context: Optional[Dict] = None) -> Dict:
        """Ejecuta un workflow registrado."""
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' no encontrado")

        context = initial_context or {}
        context["workflow_name"] = name
        context["started_at"] = datetime.utcnow()

        await self.logger.log_event("INFO", f"🚀 Iniciando workflow: {name}", context)

        try:
            result = await self.workflows[name].run(context)
            context["finished_at"] = datetime.utcnow()
            context["status"] = "success"
            
            await self.logger.log_event("SUCCESS", f"✅ Workflow completado: {name}", context)
            return result

        except Exception as e:
            context["status"] = "failed"
            context["error"] = str(e)
            await self.logger.log_event("ERROR", f"❌ Workflow falló: {name}", context)
            raise