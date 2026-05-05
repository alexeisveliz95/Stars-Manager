from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass, field
import asyncio

@dataclass
class WorkflowStep:
    name: str
    func: Callable
    description: str = ""
    continue_on_error: bool = False
    retry: int = 0

@dataclass
class Workflow:
    name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, name: str, func: Callable, **kwargs):
        self.steps.append(WorkflowStep(name=name, func=func, **kwargs))
        return self

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el workflow paso a paso."""
        print(f"🚀 Iniciando workflow: {self.name}")
        
        for step in self.steps:
            try:
                print(f"   ⏳ Ejecutando: {step.name}")
                if asyncio.iscoroutinefunction(step.func):
                    context = await step.func(context)
                else:
                    context = step.func(context)
            except Exception as e:
                print(f"   ❌ Error en {step.name}: {e}")
                if not step.continue_on_error:
                    raise
        return context