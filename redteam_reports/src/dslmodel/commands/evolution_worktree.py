"""
Worktree-Based Evolution CLI Commands
Built using weaver forge semantic conventions with proper OTEL telemetry
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional, List
import json
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from ..evolution_weaver.evolution_engine import WorktreeEvolutionEngine

app = typer.Typer(help="Worktree-based autonomous evolution system")
console = Console()

@app.command("start")
def start_evolution(
    strategy: str = typer.Option(
        "quality",
        "--strategy", "-s",
        help="Evolution strategy: performance, security, quality, features, architecture"
    ),
    base_path: Path = typer.Option(
        Path.cwd(),
        "--path", "-p",
        help="Base path for evolution (default: current directory)"
    ),
    population: int = typer.Option(
        8,
        "--population",
        help="Population size for evolution"
    ),
    generations: int = typer.Option(
        15,
        "--generations",
        help="Maximum generations"
    ),
    monitor: bool = typer.Option(
        False,
        "--monitor",
        help="Monitor deployed evolution"
    )
):
    """Start worktree-based evolution cycle"""
    
    console.print(Panel.fit(
        f"[bold cyan]🧬 Starting Worktree Evolution[/bold cyan]\n"
        f"Strategy: [yellow]{strategy}[/yellow]\n"
        f"Base Path: [green]{base_path}[/green]\n"
        f"Population: [blue]{population}[/blue] | Generations: [blue]{generations}[/blue]",
        title="Evolution Engine"
    ))
    
    async def run_evolution():
        # Initialize evolution engine
        engine = WorktreeEvolutionEngine(
            base_path=base_path,
            strategies=[strategy]
        )
        
        # Update strategy parameters
        if strategy in engine.strategies:
            engine.strategies[strategy].population_size = population
            engine.strategies[strategy].max_generations = generations
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running evolution cycle...", total=None)
            
            # Run evolution cycle
            result = await engine.start_evolution_cycle(strategy)
            
            progress.stop()
        
        # Display results
        console.print("\n" + "=" * 60)
        console.print("[bold green]🎯 EVOLUTION RESULTS[/bold green]")
        console.print("=" * 60)
        
        console.print(f"Evolution ID: [cyan]{result['evolution_id']}[/cyan]")
        console.print(f"Strategy: [yellow]{result['strategy']}[/yellow]")
        console.print(f"Generations: [blue]{result['generations_run']}[/blue]")
        console.print(f"Best Fitness: [green]{result['best_fitness']:.3f}[/green]")
        console.print(f"Experiments: [blue]{result['experiments_total']}[/blue]")
        console.print(f"Merge Success: [{'green' if result['merge_success'] else 'red'}]{result['merge_success']}[/{'green' if result['merge_success'] else 'red'}]")
        
        # Show generation progress
        if result['generation_results']:
            console.print("\n[bold]Generation Progress:[/bold]")
            table = Table()
            table.add_column("Generation", style="cyan")
            table.add_column("Population", style="blue")
            table.add_column("Best Fitness", style="green")
            table.add_column("Avg Fitness", style="yellow")
            
            for gen_result in result['generation_results']:
                table.add_row(
                    str(gen_result['generation']),
                    str(gen_result['population_size']),
                    f"{gen_result['best_fitness']:.3f}",
                    f"{gen_result['avg_fitness']:.3f}"
                )
            
            console.print(table)
        
        # Monitor if requested
        if monitor and result['merge_success']:
            console.print(f"\n[yellow]📊 Starting monitoring for 30 minutes...[/yellow]")
            monitoring_result = await engine.monitor_deployed_evolution(
                result['evolution_id'], 
                duration_minutes=30
            )
            
            console.print(f"[green]✅ Monitoring complete - Performance improved by {monitoring_result['performance_improvement']:.1f}%[/green]")
        
        return result
    
    # Run the evolution
    result = asyncio.run(run_evolution())
    
    if result['merge_success']:
        console.print(Panel(
            f"[green]🚀 Evolution successful![/green]\n"
            f"Fitness improved to {result['best_fitness']:.3f}\n"
            f"Changes merged to main branch",
            title="✨ Success",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[yellow]⚠️ Evolution completed[/yellow]\n"
            f"Best fitness: {result['best_fitness']:.3f}\n"
            f"No improvements met merge criteria",
            title="ℹ️ Complete",
            border_style="yellow"
        ))

@app.command("status")
def show_status():
    """Show evolution engine status"""
    
    engine = WorktreeEvolutionEngine(base_path=Path.cwd())
    status = engine.get_evolution_status()
    
    console.print("[bold cyan]🧬 Evolution Engine Status[/bold cyan]")
    
    # Status table
    table = Table(title="Engine Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")
    
    table.add_row(
        "Active Experiments", 
        f"🔵 {status['active_experiments']}", 
        "Currently running experiments"
    )
    table.add_row(
        "Available Strategies", 
        f"🟢 {len(status['available_strategies'])}", 
        ", ".join(status['available_strategies'])
    )
    table.add_row(
        "Evolution History", 
        f"📊 {status['evolution_history_count']}", 
        "Completed evolution cycles"
    )
    table.add_row(
        "Worktree Base", 
        "📁 Ready", 
        str(status['worktree_base'])
    )
    table.add_row(
        "OTEL Telemetry", 
        f"{'🟢 Enabled' if status['otel_enabled'] else '🟡 Mock'}", 
        "OpenTelemetry integration"
    )
    
    console.print(table)

@app.command("strategies")
def list_strategies():
    """List available evolution strategies"""
    
    engine = WorktreeEvolutionEngine(base_path=Path.cwd())
    
    console.print("[bold cyan]🎯 Available Evolution Strategies[/bold cyan]")
    
    table = Table()
    table.add_column("Strategy", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Mutation Rate", style="yellow")
    table.add_column("Population", style="blue")
    table.add_column("Generations", style="green")
    
    for name, strategy in engine.strategies.items():
        table.add_row(
            name.title(),
            strategy.description,
            f"{strategy.mutation_rate:.2f}",
            str(strategy.population_size),
            str(strategy.max_generations)
        )
    
    console.print(table)

@app.command("history")
def show_history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent evolutions to show")
):
    """Show evolution history"""
    
    engine = WorktreeEvolutionEngine(base_path=Path.cwd())
    
    if not engine.evolution_history:
        console.print("[yellow]No evolution history found[/yellow]")
        return
    
    console.print(f"[bold cyan]📚 Evolution History (Last {limit})[/bold cyan]")
    
    table = Table()
    table.add_column("Evolution ID", style="cyan")
    table.add_column("Strategy", style="yellow")
    table.add_column("Generations", style="blue")
    table.add_column("Best Fitness", style="green")
    table.add_column("Merged", style="white")
    table.add_column("Date", style="dim")
    
    recent_history = engine.evolution_history[-limit:]
    
    for evolution in recent_history:
        table.add_row(
            evolution['evolution_id'][:12],
            evolution['strategy'],
            str(evolution['generations_run']),
            f"{evolution['best_fitness']:.3f}",
            "✅" if evolution['merge_success'] else "❌",
            evolution['duration'][:19]  # Date part only
        )
    
    console.print(table)

@app.command("experiment")
def run_experiment(
    strategy: str = typer.Argument(..., help="Evolution strategy to test"),
    mutations: int = typer.Option(3, "--mutations", help="Number of mutations to apply"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't actually apply changes")
):
    """Run a single evolution experiment"""
    
    console.print(f"[bold cyan]🧪 Running Evolution Experiment[/bold cyan]")
    console.print(f"Strategy: [yellow]{strategy}[/yellow]")
    console.print(f"Mutations: [blue]{mutations}[/blue]")
    console.print(f"Dry Run: [{'green' if dry_run else 'red'}]{dry_run}[/{'green' if dry_run else 'red'}]")
    
    async def run_single_experiment():
        engine = WorktreeEvolutionEngine(base_path=Path.cwd())
        
        if strategy not in engine.strategies:
            console.print(f"[red]❌ Unknown strategy: {strategy}[/red]")
            console.print(f"Available: {', '.join(engine.strategies.keys())}")
            return
        
        # Create single experiment
        evolution_id = f"experiment_{strategy}"
        experiment = await engine._create_experiment(
            evolution_id, 
            engine.strategies[strategy], 
            0
        )
        
        if not experiment:
            console.print("[red]❌ Failed to create experiment[/red]")
            return
        
        console.print(f"[green]✅ Created experiment: {experiment.experiment_id}[/green]")
        console.print(f"Worktree: [cyan]{experiment.worktree_path}[/cyan]")
        console.print(f"Branch: [yellow]{experiment.branch_name}[/yellow]")
        
        # Evaluate fitness
        fitness = await engine._evaluate_experiment_fitness(experiment)
        console.print(f"Fitness Score: [green]{fitness:.3f}[/green]")
        
        if not dry_run and fitness > 0.8:
            merge_success = await engine._merge_experiment(experiment, fitness)
            console.print(f"Merge Success: [{'green' if merge_success else 'red'}]{merge_success}[/{'green' if merge_success else 'red'}]")
        
        # Cleanup
        await engine._cleanup_experiments([experiment])
        console.print("[dim]Experiment cleaned up[/dim]")
    
    asyncio.run(run_single_experiment())

@app.command("monitor")
def monitor_evolution(
    evolution_id: str = typer.Argument(..., help="Evolution ID to monitor"),
    duration: int = typer.Option(30, "--duration", help="Monitoring duration in minutes")
):
    """Monitor deployed evolution"""
    
    console.print(f"[bold cyan]📊 Monitoring Evolution[/bold cyan]")
    console.print(f"Evolution ID: [yellow]{evolution_id}[/yellow]")
    console.print(f"Duration: [blue]{duration} minutes[/blue]")
    
    async def run_monitoring():
        engine = WorktreeEvolutionEngine(base_path=Path.cwd())
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Monitoring for {duration} minutes...", total=None)
            
            result = await engine.monitor_deployed_evolution(evolution_id, duration)
            
            progress.stop()
        
        console.print("\n[bold green]📈 Monitoring Results[/bold green]")
        console.print(f"Status: [green]{result['status']}[/green]")
        console.print(f"Performance Improvement: [cyan]{result['performance_improvement']:.1f}%[/cyan]")
        console.print(f"Deployment ID: [yellow]{result['deployment_id']}[/yellow]")
    
    asyncio.run(run_monitoring())

@app.command("cleanup")
def cleanup_worktrees(
    force: bool = typer.Option(False, "--force", help="Force cleanup without confirmation")
):
    """Clean up evolution worktrees"""
    
    engine = WorktreeEvolutionEngine(base_path=Path.cwd())
    worktree_base = engine.worktree_base
    
    if not worktree_base.exists():
        console.print("[green]✅ No worktrees to clean up[/green]")
        return
    
    worktree_dirs = [d for d in worktree_base.iterdir() if d.is_dir()]
    
    if not worktree_dirs:
        console.print("[green]✅ No worktrees to clean up[/green]")
        return
    
    console.print(f"[yellow]Found {len(worktree_dirs)} worktree directories:[/yellow]")
    for d in worktree_dirs:
        console.print(f"  - {d.name}")
    
    if not force:
        if not typer.confirm("\nClean up these worktrees?"):
            console.print("[yellow]Cleanup cancelled[/yellow]")
            return
    
    # Cleanup worktrees
    import subprocess
    import shutil
    
    cleaned = 0
    for worktree_dir in worktree_dirs:
        try:
            # Try to remove worktree properly
            subprocess.run([
                "git", "worktree", "remove", str(worktree_dir)
            ], cwd=engine.base_path, check=True, capture_output=True)
            cleaned += 1
        except subprocess.CalledProcessError:
            # Force remove if git worktree fails
            try:
                shutil.rmtree(worktree_dir)
                cleaned += 1
                console.print(f"[yellow]Force removed: {worktree_dir.name}[/yellow]")
            except Exception as e:
                console.print(f"[red]Failed to remove {worktree_dir.name}: {e}[/red]")
    
    console.print(f"[green]✅ Cleaned up {cleaned}/{len(worktree_dirs)} worktrees[/green]")

if __name__ == "__main__":
    app()