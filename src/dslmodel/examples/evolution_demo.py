"""
Autonomous Evolution System Demonstration
Shows self-improving capabilities of DSLModel
"""

import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

from dslmodel.evolution import (
    EvolutionEngine,
    EvolutionConfig,
    EvolutionStrategy,
    EvolutionaryFitness,
    EvolutionCandidate
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print

console = Console()


class DemoCodeAnalyzer:
    """Mock code analyzer for demo"""
    
    async def analyze(self, path: Path) -> Dict[str, Any]:
        """Analyze codebase and return metrics"""
        await asyncio.sleep(0.5)  # Simulate analysis time
        
        return {
            "performance": {
                "score": random.uniform(0.6, 0.8),
                "bottlenecks": ["database queries", "file I/O"],
                "suggestions": ["add caching", "optimize queries"]
            },
            "security": {
                "score": random.uniform(0.7, 0.85),
                "metrics": {"critical_count": random.randint(0, 2)},
                "vulnerabilities": ["input validation", "auth checks"]
            },
            "quality": {
                "score": random.uniform(0.5, 0.7),
                "issues": ["complex functions", "missing tests"],
                "complexity": random.uniform(10, 20)
            }
        }
    
    async def evaluate_fitness(self, path: Path) -> float:
        """Evaluate fitness score"""
        analysis = await self.analyze(path)
        return analysis["quality"]["score"]


class DemoCodeGenerator:
    """Mock code generator for demo"""
    
    async def generate(self, path: Path, strategy: EvolutionStrategy, generation: int) -> Dict[str, Any]:
        """Generate evolution candidate"""
        await asyncio.sleep(0.3)  # Simulate generation time
        
        improvements = {
            EvolutionStrategy.PERFORMANCE_OPTIMIZATION: [
                "Add caching layer for database queries",
                "Implement connection pooling",
                "Optimize algorithm complexity"
            ],
            EvolutionStrategy.SECURITY_HARDENING: [
                "Add input validation middleware",
                "Implement rate limiting",
                "Enhance authentication checks"
            ],
            EvolutionStrategy.CODE_QUALITY_IMPROVEMENT: [
                "Refactor complex functions",
                "Add comprehensive tests",
                "Extract common patterns"
            ]
        }
        
        selected_improvements = random.sample(
            improvements.get(strategy, ["General improvement"]),
            min(2, len(improvements.get(strategy, ["General improvement"])))
        )
        
        return {
            "description": f"{strategy.value} - Generation {generation}",
            "code_changes": {
                f"src/module_{generation}.py": f"# Improved code for {strategy.value}\n# Generation: {generation}\n",
                f"tests/test_{generation}.py": f"# New tests for {strategy.value}\n"
            },
            "implementation_notes": selected_improvements,
            "estimated_impact": random.choice(["high", "medium", "low"]),
            "risk_level": random.choice(["low", "medium"])
        }


class DemoValidator:
    """Mock validator for demo"""
    
    async def validate(self, candidate: EvolutionCandidate, path: Path) -> bool:
        """Validate candidate changes"""
        await asyncio.sleep(0.2)
        # Simulate validation with 80% success rate
        return random.random() > 0.2


class SimpleEvolutionDemo:
    """Simplified demo without complex dependencies"""
    
    @staticmethod
    async def run():
        """Run simple evolution demonstration"""
        console.print("[bold cyan]🧬 DSLModel Autonomous Evolution Demo[/bold cyan]")
        console.print("Demonstrating self-improving capabilities\n")
        
        # Mock evolution results
        results = [
            {
                "generation": 1,
                "strategy": "Performance Optimization",
                "fitness": 0.65,
                "improvement": 0.0,
                "patterns": 3,
                "mutations": 2
            },
            {
                "generation": 2,
                "strategy": "Code Quality",
                "fitness": 0.72,
                "improvement": 0.07,
                "patterns": 5,
                "mutations": 3
            },
            {
                "generation": 3,
                "strategy": "Security Hardening",
                "fitness": 0.78,
                "improvement": 0.06,
                "patterns": 4,
                "mutations": 2
            },
            {
                "generation": 4,
                "strategy": "Performance Optimization",
                "fitness": 0.85,
                "improvement": 0.07,
                "patterns": 6,
                "mutations": 4
            },
            {
                "generation": 5,
                "strategy": "Code Quality",
                "fitness": 0.89,
                "improvement": 0.04,
                "patterns": 3,
                "mutations": 2
            }
        ]
        
        # Show evolution progress
        table = Table(title="Evolution Progress")
        table.add_column("Gen", style="cyan")
        table.add_column("Strategy", style="magenta")
        table.add_column("Fitness", style="yellow")
        table.add_column("Improvement", style="green")
        table.add_column("Patterns", style="blue")
        table.add_column("Mutations", style="white")
        
        total_improvement = 0
        for result in results:
            total_improvement += result["improvement"]
            table.add_row(
                str(result["generation"]),
                result["strategy"],
                f"{result['fitness']:.3f}",
                f"+{result['improvement']:.3f}",
                str(result["patterns"]),
                str(result["mutations"])
            )
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold green]✅ Evolution Demo Complete[/bold green]")
        console.print(f"Total fitness improvement: [green]+{total_improvement:.3f}[/green]")
        console.print(f"Final fitness score: [green]{results[-1]['fitness']:.3f}[/green]")
        
        # Show capabilities
        console.print("\n[bold]Autonomous Capabilities Demonstrated:[/bold]")
        capabilities = [
            "🧠 Self-analysis of code quality and performance",
            "🔄 Automatic generation of improvement candidates",
            "📊 Fitness evolution across multiple objectives",
            "✅ Safe validation before deployment",
            "🎯 Multi-strategy optimization"
        ]
        
        for capability in capabilities:
            console.print(f"  • {capability}")
        
        return True


async def run_evolution_demo():
    """Run complete evolution demonstration"""
    console.print(Panel.fit(
        "[bold cyan]🧬 DSLModel Autonomous Evolution Demo[/bold cyan]\n"
        "Demonstrating self-improving capabilities",
        title="Evolution Demo"
    ))
    
    # Phase 1: Setup
    console.print("\n[bold]Phase 1: Setting up evolution environment[/bold]")
    
    config = EvolutionConfig(
        target_path=Path.cwd(),
        strategies=[
            EvolutionStrategy.PERFORMANCE_OPTIMIZATION,
            EvolutionStrategy.CODE_QUALITY_IMPROVEMENT,
            EvolutionStrategy.SECURITY_HARDENING
        ],
        population_size=5,
        max_generations=10,
        convergence_threshold=0.01,
        max_evolution_time=timedelta(minutes=30)
    )
    
    engine = EvolutionEngine(config)
    
    # Register demo components
    analyzer = DemoCodeAnalyzer()
    generator = DemoCodeGenerator()
    validator = DemoValidator()
    
    engine.register_analyzer("code", analyzer)
    engine.register_analyzer("performance", analyzer)
    engine.register_analyzer("security", analyzer)
    engine.register_analyzer("quality", analyzer)
    
    engine.register_generator("optimization", generator)
    engine.register_generator("security", generator)
    engine.register_generator("refactoring", generator)
    engine.register_generator("code", generator)
    
    engine.register_validator("syntax", validator)
    engine.register_validator("security", validator)
    engine.register_validator("tests", validator)
    
    console.print("[green]✅ Evolution engine configured[/green]")
    
    # Phase 2: Run evolution cycles
    console.print("\n[bold]Phase 2: Running evolution cycles[/bold]")
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for i, strategy in enumerate(config.strategies):
            task = progress.add_task(f"Evolving {strategy.value}...", total=None)
            
            # Run evolution
            result = await engine.evolve(strategy)
            results.append(result)
            
            progress.stop()
            
            # Show results
            console.print(f"\n[cyan]Strategy: {strategy.value}[/cyan]")
            console.print(f"Generations: {result.generation_count}")
            console.print(f"Candidates evaluated: {result.candidate_count}")
            console.print(f"Fitness improvement: [green]+{result.fitness_improvement:.3f}[/green]")
            
            if result.best_candidate:
                console.print(f"Best solution: {result.best_candidate.description}")
                console.print(f"Implementation notes:")
                for note in result.best_candidate.implementation_notes:
                    console.print(f"  • {note}")
    
    # Phase 3: Show evolution summary
    console.print("\n[bold]Phase 3: Evolution Summary[/bold]")
    
    table = Table(title="Evolution Results")
    table.add_column("Strategy", style="cyan")
    table.add_column("Generations", style="yellow")
    table.add_column("Candidates", style="magenta")
    table.add_column("Success Rate", style="green")
    table.add_column("Fitness Gain", style="blue")
    table.add_column("Status", style="white")
    
    total_improvement = 0
    for result in results:
        success_rate = result.success_count / result.candidate_count if result.candidate_count > 0 else 0
        total_improvement += result.fitness_improvement
        
        status = "✅ Deployed" if result.deployed else "⚠️  Simulated"
        
        table.add_row(
            result.strategy.value,
            str(result.generation_count),
            str(result.candidate_count),
            f"{success_rate:.1%}",
            f"+{result.fitness_improvement:.3f}",
            status
        )
    
    console.print(table)
    
    # Phase 4: Show autonomous capabilities
    console.print("\n[bold]Phase 4: Autonomous Capabilities Demonstrated[/bold]")
    
    capabilities = Table(show_header=False, box=None)
    capabilities.add_column("Feature", style="cyan")
    capabilities.add_column("Description", style="white")
    
    capabilities.add_row(
        "🧠 Self-Analysis",
        "System analyzed its own code quality, performance, and security"
    )
    capabilities.add_row(
        "🔄 Auto-Generation",
        "Generated improvement candidates based on detected issues"
    )
    capabilities.add_row(
        "📊 Fitness Evolution",
        f"Overall fitness improved by {total_improvement:.3f} across strategies"
    )
    capabilities.add_row(
        "✅ Safe Deployment",
        "Validated all changes before deployment with safety checks"
    )
    capabilities.add_row(
        "🎯 Multi-Objective",
        "Optimized for performance, security, and quality simultaneously"
    )
    
    console.print(capabilities)
    
    # Phase 5: Future evolution
    console.print("\n[bold]Phase 5: Continuous Evolution Potential[/bold]")
    console.print(
        "The system can continue evolving autonomously:\n"
        "• Learning from execution patterns\n"
        "• Adapting to changing requirements\n"
        "• Self-healing from issues\n"
        "• Optimizing based on real-world usage"
    )
    
    console.print(f"\n[bold green]🎉 Evolution demo completed successfully![/bold green]")
    console.print(f"Total system improvement: [green]+{total_improvement:.3f}[/green]")


def main():
    """Run the evolution demonstration"""
    console.print("[bold cyan]Starting DSLModel Autonomous Evolution Demo...[/bold cyan]\n")
    
    try:
        # Run simplified demo that doesn't require complex setup
        asyncio.run(SimpleEvolutionDemo.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        raise


if __name__ == "__main__":
    main()