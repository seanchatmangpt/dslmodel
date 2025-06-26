#!/usr/bin/env python3
"""
Evolution CLI - Control automatic evolution system
"""

import asyncio
import typer
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .evolution_engine import AutomaticEvolutionEngine, EvolutionMetric, EvolutionPattern, EvolutionAction
from .worktree_coordinator import OTELWeaverCoordinator

app = typer.Typer(
    name="evolution",
    help="[bold cyan]Automatic Evolution System[/bold cyan] - Self-improving agent coordination",
    rich_markup_mode="rich"
)

console = Console()

# Global evolution engine instance
evolution_engine: Optional[AutomaticEvolutionEngine] = None

def get_evolution_engine() -> AutomaticEvolutionEngine:
    """Get or create evolution engine instance"""
    global evolution_engine
    if not evolution_engine:
        project_root = Path.cwd()
        coordinator = OTELWeaverCoordinator(project_root)
        evolution_engine = AutomaticEvolutionEngine(project_root, coordinator)
    return evolution_engine

@app.command("start")
def start_evolution(
    continuous: bool = typer.Option(True, help="Run continuous evolution"),
    cycle_interval: int = typer.Option(24, help="Evolution cycle interval in hours"),
    confidence_threshold: float = typer.Option(0.7, help="Minimum confidence for actions")
):
    """🧬 Start automatic evolution system"""
    
    console.print("🧬 [bold green]Starting Automatic Evolution System[/bold green]")
    
    engine = get_evolution_engine()
    
    # Update configuration
    engine.evolution_config.update({
        "cycle_interval_hours": cycle_interval,
        "confidence_threshold": confidence_threshold
    })
    
    if continuous:
        console.print("🔄 Starting continuous evolution...")
        try:
            asyncio.run(engine.start_continuous_evolution())
        except KeyboardInterrupt:
            console.print("\n⏹️ Evolution system stopped by user")
    else:
        console.print("⚡ Running single evolution cycle...")
        result = asyncio.run(engine.run_evolution_cycle())
        _display_cycle_result(result)

@app.command("cycle")
def run_evolution_cycle():
    """⚡ Run single evolution cycle"""
    
    console.print("⚡ [bold cyan]Running Evolution Cycle[/bold cyan]")
    
    engine = get_evolution_engine()
    result = asyncio.run(engine.run_evolution_cycle())
    
    _display_cycle_result(result)

@app.command("status")
def evolution_status():
    """📊 Show evolution system status"""
    
    console.print("📊 [bold cyan]Evolution System Status[/bold cyan]")
    
    engine = get_evolution_engine()
    status = engine.get_evolution_status()
    
    # Status panel
    status_panel = Panel(
        f"""
[bold]Cycles Completed:[/bold] {status['cycles_completed']}
[bold]Current Metrics:[/bold] {len(status['current_metrics'])}
[bold]System Status:[/bold] {"Active" if status['cycles_completed'] > 0 else "Inactive"}
        """.strip(),
        title="[bold green]Evolution Engine Status[/bold green]",
        border_style="green"
    )
    
    console.print(status_panel)
    
    # Current metrics table
    if status['current_metrics']:
        metrics_table = Table(title="Current Evolution Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Current", style="green")
        metrics_table.add_column("Target", style="yellow")
        metrics_table.add_column("Trend", style="magenta")
        metrics_table.add_column("Importance", style="blue")
        
        for metric in status['current_metrics']:
            trend_color = "green" if metric['trend'] == "improving" else "red" if metric['trend'] == "declining" else "yellow"
            
            metrics_table.add_row(
                metric['metric_name'],
                f"{metric['current_value']:.3f}",
                f"{metric['target_value']:.3f}",
                f"[{trend_color}]{metric['trend']}[/{trend_color}]",
                f"{metric['importance']:.1%}"
            )
        
        console.print(metrics_table)
    
    # Last cycle info
    if status['last_cycle']:
        last_cycle = status['last_cycle']
        
        cycle_panel = Panel(
            f"""
[bold]Cycle Number:[/bold] {last_cycle['cycle_number']}
[bold]Data Points:[/bold] {last_cycle['telemetry_data_points']}
[bold]Patterns:[/bold] {last_cycle['patterns_discovered']}
[bold]Actions:[/bold] {last_cycle['actions_executed']}/{last_cycle['actions_generated']}
[bold]Success Rate:[/bold] {last_cycle['validation_results']['successful_executions']}/{last_cycle['actions_executed']}
            """.strip(),
            title="[bold blue]Last Evolution Cycle[/bold blue]",
            border_style="blue"
        )
        
        console.print(cycle_panel)

@app.command("history")
def evolution_history(
    limit: int = typer.Option(10, help="Number of recent cycles to show")
):
    """📚 Show evolution history"""
    
    console.print("📚 [bold cyan]Evolution History[/bold cyan]")
    
    engine = get_evolution_engine()
    
    if not engine.evolution_history:
        console.print("ℹ️ No evolution cycles completed yet")
        return
    
    # History table
    history_table = Table(title=f"Last {limit} Evolution Cycles", box=box.ROUNDED)
    history_table.add_column("Cycle", style="cyan")
    history_table.add_column("Start Time", style="green")
    history_table.add_column("Data Points", style="yellow")
    history_table.add_column("Patterns", style="magenta")
    history_table.add_column("Actions", style="blue")
    history_table.add_column("Success", style="red")
    
    recent_cycles = engine.evolution_history[-limit:]
    
    for cycle in recent_cycles:
        start_time = cycle['start_time'].split('T')[1][:8]  # Show time only
        actions_str = f"{cycle['actions_executed']}/{cycle['actions_generated']}"
        success_str = f"{cycle['validation_results']['successful_executions']}/{cycle['actions_executed']}"
        
        history_table.add_row(
            str(cycle['cycle_number']),
            start_time,
            str(cycle['telemetry_data_points']),
            str(cycle['patterns_discovered']),
            actions_str,
            success_str
        )
    
    console.print(history_table)

@app.command("analyze")
def analyze_telemetry():
    """🔍 Analyze current telemetry for evolution insights"""
    
    console.print("🔍 [bold cyan]Analyzing Telemetry for Evolution[/bold cyan]")
    
    engine = get_evolution_engine()
    
    async def run_analysis():
        # Collect telemetry
        telemetry_data = await engine._collect_telemetry_data()
        
        # Analyze patterns
        patterns = await engine.telemetry_analyzer.analyze_coordination_patterns(telemetry_data)
        
        # Generate actions
        actions = await engine.optimizer.generate_optimization_actions(patterns, engine.current_metrics)
        
        return telemetry_data, patterns, actions
    
    telemetry_data, patterns, actions = asyncio.run(run_analysis())
    
    # Display analysis results
    analysis_panel = Panel(
        f"""
[bold]Telemetry Data Points:[/bold] {len(telemetry_data)}
[bold]Patterns Discovered:[/bold] {len(patterns)}
[bold]Optimization Actions:[/bold] {len(actions)}
        """.strip(),
        title="[bold green]Telemetry Analysis Results[/bold green]",
        border_style="green"
    )
    
    console.print(analysis_panel)
    
    # Patterns table
    if patterns:
        patterns_table = Table(title="Discovered Patterns", box=box.ROUNDED)
        patterns_table.add_column("Pattern ID", style="cyan")
        patterns_table.add_column("Description", style="green")
        patterns_table.add_column("Frequency", style="yellow")
        patterns_table.add_column("Success Rate", style="magenta")
        patterns_table.add_column("Confidence", style="blue")
        
        for pattern in patterns:
            patterns_table.add_row(
                pattern.pattern_id,
                pattern.description[:50] + "...",
                str(pattern.frequency),
                f"{pattern.success_rate:.1%}",
                f"{pattern.confidence:.1%}"
            )
        
        console.print(patterns_table)
    
    # Actions table
    if actions:
        actions_table = Table(title="Suggested Optimization Actions", box=box.ROUNDED)
        actions_table.add_column("Action Type", style="cyan")
        actions_table.add_column("Description", style="green")
        actions_table.add_column("Target", style="yellow")
        actions_table.add_column("Improvement", style="magenta")
        actions_table.add_column("Risk", style="blue")
        
        for action in actions:
            risk_color = "green" if action.risk_level == "low" else "yellow" if action.risk_level == "medium" else "red"
            
            actions_table.add_row(
                action.action_type,
                action.description[:40] + "...",
                action.target_component,
                f"{action.expected_improvement:.1%}",
                f"[{risk_color}]{action.risk_level}[/{risk_color}]"
            )
        
        console.print(actions_table)

@app.command("config")
def show_config():
    """⚙️ Show evolution configuration"""
    
    console.print("⚙️ [bold cyan]Evolution Configuration[/bold cyan]")
    
    engine = get_evolution_engine()
    config = engine.evolution_config
    
    config_table = Table(title="Evolution Engine Configuration", box=box.ROUNDED)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Description", style="yellow")
    
    config_descriptions = {
        "cycle_interval_hours": "Hours between evolution cycles",
        "min_telemetry_data_points": "Minimum data points required for analysis",
        "confidence_threshold": "Minimum confidence for executing actions",
        "max_actions_per_cycle": "Maximum actions executed per cycle",
        "rollback_on_degradation": "Whether to rollback on performance degradation"
    }
    
    for key, value in config.items():
        description = config_descriptions.get(key, "Configuration setting")
        config_table.add_row(
            key.replace("_", " ").title(),
            str(value),
            description
        )
    
    console.print(config_table)

@app.command("demo")
def evolution_demo():
    """🎪 Run evolution system demonstration"""
    
    console.print("🎪 [bold cyan]Evolution System Demo[/bold cyan]")
    console.print("🧬 Demonstrating automatic evolution capabilities")
    console.print("=" * 60)
    
    engine = get_evolution_engine()
    
    async def run_demo():
        # Step 1: Show initial status
        console.print("\n📊 [bold]Step 1: Initial System Status[/bold]")
        console.print("💡 Before evolution - baseline metrics")
        
        # Step 2: Run analysis
        console.print("\n🔍 [bold]Step 2: Telemetry Analysis[/bold]")
        telemetry_data = await engine._collect_telemetry_data()
        patterns = await engine.telemetry_analyzer.analyze_coordination_patterns(telemetry_data)
        console.print(f"📈 Analyzed {len(telemetry_data)} telemetry data points")
        console.print(f"🔍 Discovered {len(patterns)} coordination patterns")
        
        # Step 3: Generate optimizations
        console.print("\n⚡ [bold]Step 3: Generate Optimizations[/bold]")
        actions = await engine.optimizer.generate_optimization_actions(patterns, engine.current_metrics)
        console.print(f"🚀 Generated {len(actions)} optimization actions")
        
        for action in actions[:3]:  # Show top 3 actions
            console.print(f"  • {action.description} ({action.expected_improvement:.1%} improvement)")
        
        # Step 4: Simulate execution
        console.print("\n🔧 [bold]Step 4: Execute Optimizations[/bold]")
        console.print("⚡ Simulating optimization execution...")
        
        # Simulate some execution results
        execution_results = [
            {"status": "success", "action_id": action.action_id, "improvement": action.expected_improvement}
            for action in actions[:2]
        ]
        
        console.print(f"✅ Successfully executed {len(execution_results)} optimizations")
        
        # Step 5: Show results
        console.print("\n📈 [bold]Step 5: Evolution Results[/bold]")
        total_improvement = sum(r["improvement"] for r in execution_results)
        console.print(f"🎯 Total system improvement: {total_improvement:.1%}")
        console.print("🧬 System automatically evolved to better performance")
        
        console.print(f"\n🎉 [bold green]Evolution Demo Complete![/bold green]")
        console.print("✨ Key capabilities demonstrated:")
        console.print("  • Automatic telemetry analysis")
        console.print("  • Pattern recognition and optimization")
        console.print("  • Self-improving coordination system")
        console.print("  • Zero-human-intervention evolution")
    
    asyncio.run(run_demo())

def _display_cycle_result(result: dict):
    """Display evolution cycle result"""
    
    if result.get("status") == "insufficient_data":
        console.print("⚠️ [yellow]Insufficient telemetry data for evolution cycle[/yellow]")
        return
    
    result_panel = Panel(
        f"""
[bold]Cycle Number:[/bold] {result['cycle_number']}
[bold]Duration:[/bold] {result['start_time']} - {result['end_time']}
[bold]Telemetry Data Points:[/bold] {result['telemetry_data_points']}
[bold]Patterns Discovered:[/bold] {result['patterns_discovered']}
[bold]Actions Generated:[/bold] {result['actions_generated']}
[bold]Actions Executed:[/bold] {result['actions_executed']}
[bold]Success Rate:[/bold] {result['validation_results']['successful_executions']}/{result['actions_executed']}
        """.strip(),
        title="[bold green]🧬 Evolution Cycle Complete[/bold green]",
        border_style="green"
    )
    
    console.print(result_panel)

if __name__ == "__main__":
    app()