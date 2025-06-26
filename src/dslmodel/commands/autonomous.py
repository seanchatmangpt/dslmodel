"""Autonomous Decision Engine CLI commands."""

import json
import time
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from ..agents.autonomous_decision_engine import AutonomousDecisionEngine, SystemHealth

app = typer.Typer(help="Autonomous Decision Engine commands")
console = Console()


@app.command()
def analyze(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir",
        "-c",
        help="Coordination directory path"
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json)"
    )
):
    """Analyze system state and generate autonomous decisions."""
    
    engine = AutonomousDecisionEngine(coordination_dir)
    
    # Analyze system state
    with console.status("Analyzing system state..."):
        metrics = engine.analyze_system_state()
    
    # Generate decisions
    with console.status("Generating autonomous decisions..."):
        decisions = engine.make_autonomous_decisions(metrics)
    
    if output_format == "json":
        # JSON output for programmatic use
        result = {
            "metrics": {
                "completion_rate": metrics.completion_rate,
                "active_agents": metrics.active_agents,
                "work_queue_size": metrics.work_queue_size,
                "health_score": metrics.health_score,
                "health_state": engine.decision_engine._get_health_state(metrics.health_score).value
            },
            "decisions": [
                {
                    "id": d.id,
                    "type": d.type.value,
                    "priority": d.priority,
                    "description": d.description,
                    "confidence": d.confidence
                }
                for d in decisions
            ]
        }
        console.print_json(json.dumps(result, indent=2))
    else:
        # Rich table output for human use
        _display_analysis_results(metrics, decisions, engine)


@app.command()
def status(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir",
        "-c",
        help="Coordination directory path"
    )
):
    """Show current system status without making changes."""
    
    engine = AutonomousDecisionEngine(coordination_dir)
    status_data = engine.status()
    
    # Create status display
    health_state = status_data["health_state"]
    metrics = status_data["metrics"]
    
    # Color code based on health
    health_colors = {
        "critical": "red",
        "degraded": "yellow",
        "healthy": "green",
        "optimal": "bright_green"
    }
    health_color = health_colors.get(health_state, "white")
    
    # Status panel
    status_text = f"""
[bold]System Health:[/bold] [{health_color}]{health_state.upper()}[/{health_color}]
[bold]Health Score:[/bold] {metrics['health_score']:.2f}/1.0
[bold]Active Agents:[/bold] {metrics['active_agents']}
[bold]Work Queue:[/bold] {metrics['work_queue_size']} items
[bold]Completion Rate:[/bold] {metrics['completion_rate']:.1%}
[bold]Telemetry Volume:[/bold] {metrics['telemetry_volume']} items
[bold]Last Updated:[/bold] {metrics['timestamp']}
"""
    
    console.print(Panel(
        status_text,
        title="🤖 Autonomous System Status",
        border_style=health_color
    ))


@app.command()
def execute(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir",
        "-c",
        help="Coordination directory path"
    ),
    max_decisions: int = typer.Option(
        3,
        "--max",
        "-m",
        help="Maximum decisions to execute per cycle"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be executed without actually doing it"
    )
):
    """Execute autonomous decisions."""
    
    engine = AutonomousDecisionEngine(coordination_dir)
    
    with console.status("Running autonomous decision cycle..."):
        cycle_result = engine.run_cycle()
    
    if "error" in cycle_result:
        console.print(f"[red]❌ Cycle failed: {cycle_result['error']}[/red]")
        raise typer.Exit(1)
    
    # Display execution results
    execution_results = cycle_result["execution_results"]
    
    console.print(f"[green]✅ Autonomous cycle completed[/green]")
    console.print(f"[bold]Trace ID:[/bold] {cycle_result['trace_id']}")
    console.print(f"[bold]Decisions Generated:[/bold] {cycle_result['decisions_generated']}")
    console.print(f"[bold]Executed:[/bold] {len(execution_results['executed'])}")
    console.print(f"[bold]Failed:[/bold] {len(execution_results['failed'])}")
    console.print(f"[bold]Skipped:[/bold] {execution_results['skipped']}")
    
    # Show executed decisions
    if execution_results["executed"]:
        table = Table(title="Executed Decisions")
        table.add_column("Type", style="cyan")
        table.add_column("Result", style="green")
        
        for exec_result in execution_results["executed"]:
            table.add_row(
                exec_result["type"],
                str(exec_result["result"])
            )
        
        console.print(table)
    
    # Show failed decisions
    if execution_results["failed"]:
        console.print("\n[red]Failed Executions:[/red]")
        for failed in execution_results["failed"]:
            console.print(f"  [red]❌ {failed['error']}[/red]")


@app.command()
def loop(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir",
        "-c",
        help="Coordination directory path"
    ),
    interval: int = typer.Option(
        30,
        "--interval",
        "-i",
        help="Loop interval in seconds"
    ),
    max_cycles: int = typer.Option(
        0,
        "--max-cycles",
        help="Maximum cycles to run (0 = infinite)"
    )
):
    """Run autonomous decision engine in continuous loop."""
    
    console.print(f"[yellow]🔄 Starting autonomous loop (interval: {interval}s)[/yellow]")
    
    engine = AutonomousDecisionEngine(coordination_dir)
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            
            console.print(f"\n[bold]--- Cycle {cycle_count} ---[/bold]")
            
            # Run cycle
            cycle_result = engine.run_cycle()
            
            if "error" in cycle_result:
                console.print(f"[red]❌ Cycle {cycle_count} failed: {cycle_result['error']}[/red]")
            else:
                # Show brief results
                metrics = cycle_result["metrics"]
                execution_results = cycle_result["execution_results"]
                
                health_score = metrics["health_score"]
                health_state = "optimal" if health_score > 0.9 else "healthy" if health_score > 0.6 else "degraded" if health_score > 0.3 else "critical"
                
                console.print(f"[bold]Health:[/bold] {health_state} ({health_score:.2f})")
                console.print(f"[bold]Executed:[/bold] {len(execution_results['executed'])} decisions")
            
            # Check if we should stop
            if max_cycles > 0 and cycle_count >= max_cycles:
                console.print(f"[yellow]🏁 Completed {max_cycles} cycles[/yellow]")
                break
            
            # Wait for next cycle
            console.print(f"[dim]Waiting {interval}s for next cycle...[/dim]")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print(f"\n[yellow]🛑 Autonomous loop stopped after {cycle_count} cycles[/yellow]")


def _display_analysis_results(metrics, decisions, engine):
    """Display analysis results in rich format."""
    
    # System metrics table
    metrics_table = Table(title="📊 System Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="white")
    metrics_table.add_column("Status", style="green")
    
    health_state = engine.decision_engine._get_health_state(metrics.health_score)
    
    metrics_table.add_row("Health Score", f"{metrics.health_score:.2f}", health_state.value)
    metrics_table.add_row("Active Agents", str(metrics.active_agents), "✅" if metrics.active_agents >= 2 else "⚠️")
    metrics_table.add_row("Work Queue", str(metrics.work_queue_size), "✅" if metrics.work_queue_size < 10 else "⚠️")
    metrics_table.add_row("Completion Rate", f"{metrics.completion_rate:.1%}", "✅" if metrics.completion_rate > 0.7 else "⚠️")
    metrics_table.add_row("Telemetry Volume", str(metrics.telemetry_volume), "📊")
    
    console.print(metrics_table)
    
    # Decisions table
    if decisions:
        decisions_table = Table(title="🤖 Autonomous Decisions")
        decisions_table.add_column("Priority", style="red")
        decisions_table.add_column("Type", style="cyan")
        decisions_table.add_column("Description", style="white")
        decisions_table.add_column("Confidence", style="green")
        
        for decision in decisions:
            decisions_table.add_row(
                str(decision.priority),
                decision.type.value,
                decision.description,
                f"{decision.confidence:.1%}"
            )
        
        console.print(decisions_table)
    else:
        console.print("[green]✅ No autonomous actions needed - system is optimal[/green]")


if __name__ == "__main__":
    app()