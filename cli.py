import asyncio
import typer
from rich.console import Console

from config.settings import settings
from core.engine import Engine
from core.workflow import Workflow

app = typer.Typer(help="Stellar Content & Intelligence Engine CLI")
console = Console()


@app.command()
def run(workflow_name: str = "test"):
    """Ejecuta un workflow específico."""
    settings.require_telegram("log")
    console.print(f"[bold cyan]Ejecutando workflow: {workflow_name}[/]")

    # Workflow de prueba
    if workflow_name == "test":
        test_workflow = Workflow(name="test")
        test_workflow.add_step("hello", lambda c: {**c, "message": "Hola desde el Engine!"})
        test_workflow.add_step("log", lambda c: (console.print(c["message"]), c)[1])
        
        engine = Engine()
        engine.register_workflow(test_workflow)
    else:
        engine = Engine()

    asyncio.run(engine.run_workflow(workflow_name))
    console.print("[bold green]✅ Workflow finalizado![/]")

@app.command()
def status():
    """Muestra estado del engine."""
    console.print("[bold]Stellar Content & Intelligence Engine[/]")
    try:
        engine = Engine()
    except ValueError as exc:
        console.print(f"[yellow]Configuración incompleta: {exc}[/]")
        return
    console.print(f"Workflows registrados: {len(engine.workflows)}")

if __name__ == "__main__":
    app()