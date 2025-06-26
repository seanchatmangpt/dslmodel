"""
Evolution System Telemetry CLI Commands
Auto-generated from telemetry specification.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from loguru import logger

app = typer.Typer(help="Evolution System Telemetry commands")
console = Console()


@app.command()
def status():
    """Show current evolution_system status."""
    from .evolution_system import EvolutionSystem
    
    feature = EvolutionSystem()
    status = feature.get_status()
    
    console.print(f"[bold]Evolution System Telemetry Status[/bold]")
    for key, value in status.items():
        console.print(f"  {key}: {value}")


@app.command()
def run(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run evolution_system operations."""
    from .evolution_system import EvolutionSystem
    
    if verbose:
        logger.info(f"Running evolution_system with config: {config}")
    
    feature = EvolutionSystem()
    result = feature.run(config=config)
    
    if result["success"]:
        console.print(f"[green]✅ evolution_system completed successfully[/green]")
    else:
        console.print(f"[red]❌ evolution_system failed: {result.get('error')}[/red]")


if __name__ == "__main__":
    app()
