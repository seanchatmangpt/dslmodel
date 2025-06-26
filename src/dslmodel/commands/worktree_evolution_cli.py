"""
Worktree Evolution CLI - Test the Weaver-first evolution system
Uses Git worktrees for isolated evolution experiments with OTEL coordination
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..evolution.worktree_evolution_engine import (
    WorktreeEvolutionEngine, 
    EvolutionStrategy
)
from ..utils.json_output import json_command

app = typer.Typer(help="Worktree-based evolution system")
console = Console()


@app.command("demo")
def run_evolution_demo(
    cycles: int = typer.Option(2, "--cycles", "-c", help="Number of evolution cycles"),
    population: int = typer.Option(3, "--population", "-p", help="Population size per generation"),
    strategy: str = typer.Option("coordination_improvement", "--strategy", "-s", help="Evolution strategy")
):
    """Run worktree evolution demo with Weaver models and OTEL coordination."""
    
    async def demo_async():
        with json_command("worktree-evolution-demo") as formatter:
            try:
                console.print(Panel(
                    "[bold cyan]🧬 Worktree Evolution Demo[/bold cyan]\n\n"
                    "[yellow]This demo showcases:[/yellow]\n"
                    "• Weaver-generated models from semantic conventions\n"
                    "• Git worktree isolation for evolution experiments\n"
                    "• OTEL coordination and telemetry validation\n"
                    "• AI-powered fitness evaluation and deployment",
                    title="🌟 Weaver-First Evolution",
                    border_style="cyan"
                ))
                
                # Parse strategy
                try:
                    evolution_strategy = EvolutionStrategy(strategy)
                except ValueError:
                    formatter.print(f"❌ Invalid strategy: {strategy}")
                    formatter.print(f"Available: {[s.value for s in EvolutionStrategy]}")
                    raise typer.Exit(1)
                
                # Initialize evolution engine
                formatter.print("🚀 Initializing WorktreeEvolutionEngine...")
                engine = WorktreeEvolutionEngine(
                    base_path="/Users/sac/dev/dslmodel-evolution-demo",
                    population_size=population,
                    mutation_rate=0.15
                )
                
                formatter.add_data("engine_initialized", True)
                formatter.add_data("strategy", strategy)
                formatter.add_data("cycles", cycles)
                formatter.add_data("population_size", population)
                
                # Run evolution cycles
                formatter.print(f"🧬 Running {cycles} evolution cycles...")
                
                results = await engine.run_evolution_cycles(
                    cycles=cycles,
                    strategy=evolution_strategy
                )
                
                # Display results
                _display_evolution_results(results, formatter)
                
                # Show final status
                status = engine.get_evolution_status()
                _display_evolution_status(status)
                
                formatter.add_data("demo_successful", True)
                formatter.add_data("final_status", status)
                formatter.print("✅ Worktree evolution demo completed!")
                
            except Exception as e:
                formatter.add_error(f"Demo failed: {e}")
                formatter.print(f"❌ Demo failed: {e}")
                import traceback
                traceback.print_exc()
                raise typer.Exit(1)
    
    asyncio.run(demo_async())


@app.command("test")
def test_single_generation(
    strategy: str = typer.Option("performance_optimization", "--strategy", "-s", help="Evolution strategy"),
    population: int = typer.Option(2, "--population", "-p", help="Population size")
):
    """Test a single evolution generation with worktrees."""
    
    async def test_async():
        with json_command("worktree-evolution-test") as formatter:
            try:
                console.print("🧪 Testing single evolution generation...")
                
                # Parse strategy
                try:
                    evolution_strategy = EvolutionStrategy(strategy)
                except ValueError:
                    formatter.print(f"❌ Invalid strategy: {strategy}")
                    raise typer.Exit(1)
                
                # Initialize engine
                engine = WorktreeEvolutionEngine(
                    base_path="/Users/sac/dev/dslmodel-evolution-test",
                    population_size=population
                )
                
                # Run single generation
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    
                    task = progress.add_task("Evolving generation...", total=None)
                    
                    generation = await engine.evolve_generation(evolution_strategy)
                    
                    progress.stop()
                
                # Display generation results
                console.print("\n📊 Generation Results:")
                
                results_table = Table()
                results_table.add_column("Metric", style="cyan")
                results_table.add_column("Value", style="green")
                
                results_table.add_row("Generation ID", generation.generation_id)
                results_table.add_row("Candidates Tested", str(len(generation.candidates)))
                results_table.add_row("Best Fitness", f"{generation.best_candidate.fitness_score:.3f}" if generation.best_candidate else "None")
                results_table.add_row("Fitness Improvement", f"{generation.fitness_improvement:.3f}")
                results_table.add_row("Deployed", "✅" if generation.deployed else "❌")
                
                console.print(results_table)
                
                # Show candidate details
                if generation.candidates:
                    console.print("\n🧬 Candidate Details:")
                    
                    candidate_table = Table()
                    candidate_table.add_column("Candidate ID", style="cyan")
                    candidate_table.add_column("Fitness", style="green")
                    candidate_table.add_column("Mutations", style="yellow")
                    candidate_table.add_column("Status", style="blue")
                    
                    for candidate in generation.candidates:
                        status = "✅ Best" if candidate == generation.best_candidate else "🔄 Tested"
                        candidate_table.add_row(
                            candidate.candidate_id,
                            f"{candidate.fitness_score:.3f}",
                            str(len(candidate.mutations)),
                            status
                        )
                    
                    console.print(candidate_table)
                
                formatter.add_data("generation", {
                    "generation_id": generation.generation_id,
                    "candidates_count": len(generation.candidates),
                    "best_fitness": generation.best_candidate.fitness_score if generation.best_candidate else 0.0,
                    "fitness_improvement": generation.fitness_improvement
                })
                
                formatter.print("✅ Single generation test completed!")
                
            except Exception as e:
                formatter.add_error(f"Test failed: {e}")
                formatter.print(f"❌ Test failed: {e}")
                raise typer.Exit(1)
    
    asyncio.run(test_async())


@app.command("status")
def show_evolution_status(
    base_path: Optional[str] = typer.Option(None, "--path", "-p", help="Evolution base path")
):
    """Show current evolution system status."""
    
    with json_command("worktree-evolution-status") as formatter:
        try:
            path = base_path or "/Users/sac/dev/dslmodel-evolution"
            
            # Check if evolution system exists
            evolution_path = Path(path)
            if not evolution_path.exists():
                formatter.print(f"❌ No evolution system found at: {path}")
                formatter.print("Run 'demo' or 'test' first to initialize")
                raise typer.Exit(1)
            
            # Initialize engine to get status
            engine = WorktreeEvolutionEngine(base_path=path)
            status = engine.get_evolution_status()
            
            _display_evolution_status(status)
            
            formatter.add_data("evolution_status", status)
            formatter.add_data("status_check_successful", True)
            
        except Exception as e:
            formatter.add_error(f"Status check failed: {e}")
            formatter.print(f"❌ Status check failed: {e}")
            raise typer.Exit(1)


@app.command("validate")
def validate_weaver_integration():
    """Validate Weaver model integration with evolution system."""
    
    with json_command("worktree-evolution-validate") as formatter:
        try:
            console.print("🔍 Validating Weaver integration...")
            
            # Test importing Weaver models
            try:
                from ..generated.models.evolution import (
                    Evolution,
                    EvolutionWorktree,
                    EvolutionValidation,
                    EvolutionDeployment
                )
                formatter.print("✅ Weaver models imported successfully")
            except ImportError as e:
                formatter.add_error(f"Weaver model import failed: {e}")
                formatter.print(f"❌ Weaver model import failed: {e}")
                raise typer.Exit(1)
            
            # Test creating model instances
            try:
                evolution_model = Evolution(
                    generation_id="test-gen-001",
                    strategy="coordination_improvement",
                    fitness_score=0.85,
                    experiment_id="test-exp-001",
                    worktree_path="/test/path"
                )
                
                worktree_model = EvolutionWorktree(
                    agent_id="test-agent-001",
                    branch="evolution/test-branch",
                    state="experimenting",
                    experiment_type="coordination_test"
                )
                
                validation_model = EvolutionValidation(
                    validation_type="integration_test",
                    validation_score=0.92,
                    tests_passed=23,
                    tests_total=25
                )
                
                deployment_model = EvolutionDeployment(
                    deployment_strategy="gradual_rollout",
                    deployment_success=True,
                    rollback_enabled=True,
                    fitness_improvement=15.3
                )
                
                formatter.print("✅ Model instances created successfully")
                
            except Exception as e:
                formatter.add_error(f"Model creation failed: {e}")
                formatter.print(f"❌ Model creation failed: {e}")
                raise typer.Exit(1)
            
            # Test telemetry emission
            try:
                trace_id = evolution_model.emit_telemetry()
                formatter.print(f"✅ Telemetry emission successful: {trace_id}")
                
            except Exception as e:
                formatter.add_error(f"Telemetry emission failed: {e}")
                formatter.print(f"❌ Telemetry emission failed: {e}")
                raise typer.Exit(1)
            
            # Test WorktreeEvolutionEngine
            try:
                engine = WorktreeEvolutionEngine(
                    base_path="/Users/sac/dev/dslmodel-evolution-validation",
                    population_size=1
                )
                formatter.print("✅ WorktreeEvolutionEngine initialization successful")
                
            except Exception as e:
                formatter.add_error(f"Engine initialization failed: {e}")
                formatter.print(f"❌ Engine initialization failed: {e}")
                raise typer.Exit(1)
            
            # Summary
            console.print(Panel(
                "✨ [bold green]Weaver Integration Validation Complete[/bold green] ✨\n\n"
                "🔹 Weaver models successfully imported\n"
                "🔹 Model instances created and validated\n"
                "🔹 OTEL telemetry emission working\n"
                "🔹 WorktreeEvolutionEngine operational\n\n"
                "[yellow]Ready for evolution experiments![/yellow]",
                title="🎯 Validation Results",
                border_style="green"
            ))
            
            formatter.add_data("validation_successful", True)
            formatter.print("✅ All validations passed!")
            
        except Exception as e:
            formatter.add_error(f"Validation failed: {e}")
            formatter.print(f"❌ Validation failed: {e}")
            raise typer.Exit(1)


def _display_evolution_results(results, formatter):
    """Display evolution cycle results."""
    
    console.print("\n📈 Evolution Cycle Results:")
    
    results_table = Table()
    results_table.add_column("Cycle", style="cyan")
    results_table.add_column("Generation ID", style="blue")
    results_table.add_column("Candidates", style="yellow")
    results_table.add_column("Best Fitness", style="green")
    results_table.add_column("Improvement", style="magenta")
    results_table.add_column("Deployed", style="white")
    
    for i, generation in enumerate(results):
        best_fitness = generation.best_candidate.fitness_score if generation.best_candidate else 0.0
        deployed_status = "✅" if generation.deployed else "❌"
        
        results_table.add_row(
            str(i + 1),
            generation.generation_id,
            str(len(generation.candidates)),
            f"{best_fitness:.3f}",
            f"{generation.fitness_improvement:+.3f}",
            deployed_status
        )
    
    console.print(results_table)
    
    # Add results to formatter
    formatter.add_data("evolution_results", [
        {
            "cycle": i + 1,
            "generation_id": gen.generation_id,
            "candidates_count": len(gen.candidates),
            "best_fitness": gen.best_candidate.fitness_score if gen.best_candidate else 0.0,
            "fitness_improvement": gen.fitness_improvement,
            "deployed": gen.deployed
        }
        for i, gen in enumerate(results)
    ])


def _display_evolution_status(status):
    """Display evolution system status."""
    
    console.print("\n📊 Evolution System Status:")
    
    status_panel = Panel(
        f"🧬 Current Generation: {status['current_generation']}\n"
        f"📈 Total Generations: {status['total_generations']}\n"
        f"🧪 Candidates Tested: {status['total_candidates_tested']}\n"
        f"🚀 Successful Deployments: {status['successful_deployments']}\n"
        f"💪 Best Fitness Score: {status['best_fitness_score']:.3f}\n"
        f"🔄 Active Candidates: {status['active_candidates']}\n"
        f"👥 Population Size: {status['population_size']}\n"
        f"🎲 Mutation Rate: {status['mutation_rate']:.2f}",
        title="🌟 Evolution Status",
        border_style="blue"
    )
    
    console.print(status_panel)


if __name__ == "__main__":
    app()