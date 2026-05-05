import asyncio
import typer
from rich.console import Console

from core.engine import Engine
from core.workflow import Workflow

app = typer.Typer(help="Stellar Content & Intelligence Engine CLI")
console = Console()

engine = Engine()

@app.command()
def run(workflow_name: str = "test"):
    """Ejecuta un workflow específico."""
    console.print(f"[bold cyan]Ejecutando workflow: {workflow_name}[/]")

    # Workflow de prueba
    if workflow_name == "test":
        test_workflow = Workflow(name="test")
        test_workflow.add_step("hello", lambda c: {**c, "message": "Hola desde el Engine!"})
        test_workflow.add_step("log", lambda c: (console.print(c["message"]), c)[1])
        
        engine.register_workflow(test_workflow)

    asyncio.run(engine.run_workflow(workflow_name))
    console.print("[bold green]✅ Workflow finalizado![/]")

@app.command()
def status():
    """Muestra estado del engine."""
    console.print("[bold]Stellar Content & Intelligence Engine[/]")
    console.print(f"Workflows registrados: {len(engine.workflows)}")

if __name__ == "__main__":
    app()