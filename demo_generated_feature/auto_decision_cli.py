"""
Autonomous Decision Engine CLI Commands
Auto-generated from telemetry specification.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from loguru import logger

app = typer.Typer(help="Autonomous Decision Engine commands")
console = Console()


@app.command()
def status():
    """Show current auto_decision status."""
    from .auto_decision import AutoDecision
    
    feature = AutoDecision()
    status = feature.get_status()
    
    console.print(f"[bold]Autonomous Decision Engine Status[/bold]")
    for key, value in status.items():
        console.print(f"  {key}: {value}")


@app.command()
def run(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run auto_decision operations."""
    from .auto_decision import AutoDecision
    
    if verbose:
        logger.info(f"Running auto_decision with config: {config}")
    
    feature = AutoDecision()
    result = feature.run(config=config)
    
    if result["success"]:
        console.print(f"[green]✅ auto_decision completed successfully[/green]")
    else:
        console.print(f"[red]❌ auto_decision failed: {result.get('error')}[/red]")


if __name__ == "__main__":
    app()
