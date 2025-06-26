"""
Hyper-Advanced Weaver CLI Commands

Demonstrates revolutionary decorators for telemetry-driven development.
"""

import asyncio
import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import time

from ..weaver.hyper_examples import (
    generate_semantic_conventions,
    generate_telemetry_code,
    batch_generate_conventions,
    validate_generated_code,
    orchestrate_full_weaver_pipeline,
    demo_hyper_decorators
)
from ..weaver.hyper_decorators import (
    _hyper_registry,
    SemanticAwareness,
    ExecutionMode
)

app = typer.Typer(help="Hyper-Advanced Weaver Commands")
console = Console()


@app.command("demo")
def run_demo():
    """Run comprehensive demo of hyper-advanced decorators"""
    
    console.print(Panel.fit(
        "🚀 [bold blue]Hyper-Advanced Weaver Decorators Demo[/bold blue]\n"
        "Revolutionary AI-driven telemetry development",
        border_style="blue"
    ))
    
    # Run the async demo
    asyncio.run(demo_hyper_decorators())


@app.command("generate")
def generate_with_ai(
    span_type: str = typer.Argument(..., help="Type of span to generate (e.g., http, database)"),
    complexity: str = typer.Option("standard", help="Complexity level: minimal, standard, extended"),
    languages: List[str] = typer.Option(["python"], help="Target languages"),
    ai_mode: bool = typer.Option(True, help="Enable AI optimization"),
    evolution: bool = typer.Option(True, help="Enable semantic evolution tracking")
):
    """Generate semantic conventions with AI optimization and evolution"""
    
    console.print(f"🧠 [bold blue]AI-Generating Semantic Conventions[/bold blue]")
    console.print(f"Span Type: [cyan]{span_type}[/cyan]")
    console.print(f"Complexity: [yellow]{complexity}[/yellow]")
    console.print(f"Languages: [green]{', '.join(languages)}[/green]")
    console.print(f"AI Mode: [magenta]{'Enabled' if ai_mode else 'Disabled'}[/magenta]")
    
    start_time = time.time()
    
    try:
        # Generate with AI optimization
        convention = generate_semantic_conventions(
            span_type=span_type,
            complexity_level=complexity,
            target_languages=languages
        )
        
        duration = time.time() - start_time
        
        # Display results
        console.print(f"\n✅ [green]Generation completed in {duration:.2f}s[/green]")
        
        # Show convention details
        group = convention["groups"][0]
        
        details_table = Table(title="Generated Convention Details")
        details_table.add_column("Property", style="cyan")
        details_table.add_column("Value", style="yellow")
        
        details_table.add_row("Group ID", group["id"])
        details_table.add_row("Type", group["type"])
        details_table.add_row("Attributes", str(len(group["attributes"])))
        details_table.add_row("AI Generated", str(convention.get("ai_generated", False)))
        details_table.add_row("Complexity", convention.get("complexity_level", "unknown"))
        
        console.print(details_table)
        
        # Show attributes
        console.print(f"\n📋 [bold]Generated Attributes:[/bold]")
        for attr in group["attributes"][:5]:  # Show first 5
            console.print(f"  • [cyan]{attr['id']}[/cyan]: {attr['brief']}")
        
        if len(group["attributes"]) > 5:
            console.print(f"  ... and {len(group['attributes']) - 5} more")
        
        # Show AI insights
        if ai_mode:
            console.print(f"\n🤖 [bold]AI Insights:[/bold]")
            console.print(f"  • Performance Profile: {convention.get('performance_profile', {})}")
            console.print(f"  • Target Languages: {convention.get('target_languages', [])}")
        
    except Exception as e:
        console.print(f"❌ [red]Generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("batch")
def batch_generate(
    span_types: List[str] = typer.Option(["http", "database"], help="Span types to generate"),
    languages: List[str] = typer.Option(["python", "rust"], help="Target languages"),
    output_dir: Path = typer.Option(Path("./hyper_generated"), help="Output directory"),
    parallel: bool = typer.Option(True, help="Use parallel processing"),
    ai_scheduling: bool = typer.Option(True, help="Use AI-driven scheduling")
):
    """Batch generate conventions with parallel processing and AI optimization"""
    
    console.print(Panel.fit(
        "⚡ [bold blue]Batch Generation with AI Optimization[/bold blue]\n"
        f"Span Types: {', '.join(span_types)}\n"
        f"Languages: {', '.join(languages)}\n"
        f"Parallel: {'Enabled' if parallel else 'Disabled'}\n"
        f"AI Scheduling: {'Enabled' if ai_scheduling else 'Disabled'}",
        border_style="blue"
    ))
    
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Generating conventions...", total=None)
        
        try:
            # Use the hyper-decorated batch function
            results = batch_generate_conventions(
                span_types=span_types,
                target_languages=languages,
                output_dir=output_dir
            )
            
            duration = time.time() - start_time
            progress.update(task, description=f"✅ Completed in {duration:.2f}s")
            
        except Exception as e:
            progress.update(task, description=f"❌ Failed: {e}")
            raise typer.Exit(1)
    
    # Display results
    console.print(f"\n📊 [bold]Batch Generation Results:[/bold]")
    
    results_table = Table()
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Count", style="yellow")
    results_table.add_column("Status", style="green")
    
    results_table.add_row("Files Generated", str(len(results["generated"])), "✅")
    results_table.add_row("Failures", str(len(results["failed"])), "❌" if results["failed"] else "✅")
    results_table.add_row("Total Duration", f"{duration:.2f}s", "⏱️")
    
    console.print(results_table)
    
    # Show generated files
    if results["generated"]:
        console.print(f"\n📄 [bold]Generated Files:[/bold]")
        for file_path in results["generated"][:10]:  # Show first 10
            console.print(f"  • [green]{file_path}[/green]")
        
        if len(results["generated"]) > 10:
            console.print(f"  ... and {len(results['generated']) - 10} more")
    
    # Show failures
    if results["failed"]:
        console.print(f"\n⚠️ [bold]Failures:[/bold]")
        for failure in results["failed"]:
            console.print(f"  • [red]{failure}[/red]")


@app.command("orchestrate")
def orchestrate_pipeline(
    input_file: Path = typer.Option(Path("pipeline_specs.json"), help="Input specifications file"),
    output_dir: Path = typer.Option(Path("./orchestrated_output"), help="Output directory"),
    quality_threshold: float = typer.Option(0.8, help="Quality threshold for validation"),
    ai_mode: bool = typer.Option(True, help="Enable full AI optimization"),
    evolution: bool = typer.Option(True, help="Enable self-evolution")
):
    """Orchestrate full pipeline with all hyper-advanced features"""
    
    console.print(Panel.fit(
        "🎯 [bold blue]Full Pipeline Orchestration[/bold blue]\n"
        "AI-Driven • Self-Evolving • Contradiction-Aware\n"
        f"Quality Threshold: {quality_threshold}\n"
        f"AI Mode: {'Enabled' if ai_mode else 'Disabled'}",
        border_style="blue"
    ))
    
    # Load input specifications
    try:
        if input_file.exists():
            with open(input_file) as f:
                input_specs = json.load(f)
        else:
            # Create default specs
            input_specs = [
                {
                    "span_type": "http",
                    "complexity": "extended",
                    "languages": ["python", "rust"]
                },
                {
                    "span_type": "database", 
                    "complexity": "standard",
                    "languages": ["python", "go"]
                },
                {
                    "span_type": "messaging",
                    "complexity": "minimal",
                    "languages": ["rust", "typescript"]
                }
            ]
            console.print(f"[yellow]Using default specifications (no {input_file} found)[/yellow]")
    
    except Exception as e:
        console.print(f"❌ [red]Failed to load specifications: {e}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n📋 [bold]Processing {len(input_specs)} specifications...[/bold]")
    
    # Run orchestration
    async def run_orchestration():
        return await orchestrate_full_weaver_pipeline(
            input_specs=input_specs,
            output_config={
                "output_dir": str(output_dir),
                "format": "files",
                "validation": True
            },
            quality_gates={
                "semantic_compliance": quality_threshold,
                "performance_score": 0.7,
                "maintainability": 0.75
            }
        )
    
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Orchestrating pipeline...", total=None)
        
        try:
            result = asyncio.run(run_orchestration())
            duration = time.time() - start_time
            
            progress.update(task, description=f"✅ Pipeline completed in {duration:.2f}s")
            
        except Exception as e:
            progress.update(task, description=f"❌ Pipeline failed: {e}")
            console.print(f"[red]Pipeline orchestration failed: {e}[/red]")
            raise typer.Exit(1)
    
    # Display comprehensive results
    _display_orchestration_results(result, duration)


@app.command("status")
def show_status():
    """Show status of hyper-advanced decorator system"""
    
    console.print(Panel.fit(
        "📊 [bold blue]Hyper Weaver System Status[/bold blue]\n"
        "AI Registry • Performance Analytics • Evolution Tracking",
        border_style="blue"
    ))
    
    # Execution history
    history_count = len(_hyper_registry.execution_history)
    console.print(f"\n📈 [bold]Execution History:[/bold] {history_count} recorded executions")
    
    if history_count > 0:
        # Performance patterns
        console.print(f"\n⚡ [bold]Performance Patterns:[/bold]")
        patterns_table = Table()
        patterns_table.add_column("Function", style="cyan")
        patterns_table.add_column("Executions", style="yellow")
        patterns_table.add_column("Avg Duration (s)", style="green")
        patterns_table.add_column("Last Mode", style="magenta")
        
        for func_name, durations in _hyper_registry.performance_patterns.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                last_execution = next(
                    (e for e in reversed(_hyper_registry.execution_history) if e.function_name == func_name),
                    None
                )
                last_mode = last_execution.mode.name if last_execution else "Unknown"
                
                patterns_table.add_row(
                    func_name,
                    str(len(durations)),
                    f"{avg_duration:.3f}",
                    last_mode
                )
        
        console.print(patterns_table)
        
        # AI insights
        if _hyper_registry.ai_insights:
            console.print(f"\n🤖 [bold]AI Insights:[/bold] {len(_hyper_registry.ai_insights)} patterns learned")
            for insight_type, data in list(_hyper_registry.ai_insights.items())[:3]:
                console.print(f"  • [cyan]{insight_type}[/cyan]: {str(data)[:100]}...")
        
        # Contradiction patterns
        contradiction_count = sum(len(contras) for contras in _hyper_registry.contradiction_patterns.values())
        if contradiction_count > 0:
            console.print(f"\n⚠️ [bold]Contradictions Detected:[/bold] {contradiction_count} total")
            for func_name, contradictions in _hyper_registry.contradiction_patterns.items():
                if contradictions:
                    console.print(f"  • [yellow]{func_name}[/yellow]: {len(contradictions)} contradictions")
        
        # Evolution metrics
        if _hyper_registry.evolution_metrics:
            console.print(f"\n🔄 [bold]Evolution Tracking:[/bold] {len(_hyper_registry.evolution_metrics)} functions evolving")
    
    else:
        console.print("\n[dim]No execution history available. Run some commands to see analytics.[/dim]")


@app.command("benchmark")
def run_benchmark(
    iterations: int = typer.Option(10, help="Number of iterations to run"),
    span_types: List[str] = typer.Option(["http", "database", "messaging"], help="Span types to test"),
    measure_evolution: bool = typer.Option(True, help="Measure evolution effects"),
    ai_comparison: bool = typer.Option(True, help="Compare AI vs non-AI modes")
):
    """Run performance benchmark of hyper-advanced decorators"""
    
    console.print(Panel.fit(
        "🏁 [bold blue]Hyper Weaver Benchmark[/bold blue]\n"
        f"Iterations: {iterations}\n"
        f"Span Types: {', '.join(span_types)}\n"
        f"Evolution Tracking: {'Enabled' if measure_evolution else 'Disabled'}",
        border_style="blue"
    ))
    
    benchmark_results = {
        "iterations": iterations,
        "span_types": span_types,
        "timings": [],
        "quality_scores": [],
        "evolution_data": []
    }
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Running {iterations} benchmark iterations...", total=iterations)
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                # Test generation for each span type
                for span_type in span_types:
                    # Generate semantic convention
                    convention = generate_semantic_conventions(
                        span_type=span_type,
                        complexity_level="standard",
                        target_languages=["python"]
                    )
                    
                    # Generate code
                    code = generate_telemetry_code(
                        semantic_convention=convention,
                        target_language="python",
                        framework="pydantic"
                    )
                    
                    # Validate
                    validation = validate_generated_code(
                        code=code,
                        target_language="python",
                        semantic_convention=convention
                    )
                    
                    benchmark_results["quality_scores"].append(validation["overall_quality"])
                
                iteration_time = time.time() - iteration_start
                benchmark_results["timings"].append(iteration_time)
                
                progress.update(task, advance=1, description=f"Iteration {i+1}/{iterations} ({iteration_time:.2f}s)")
                
            except Exception as e:
                console.print(f"[red]Benchmark iteration {i+1} failed: {e}[/red]")
                benchmark_results["timings"].append(float('inf'))
    
    # Display benchmark results
    _display_benchmark_results(benchmark_results)


def _display_orchestration_results(result: dict, duration: float):
    """Display comprehensive orchestration results"""
    
    console.print(f"\n🎯 [bold green]Pipeline Orchestration Complete![/bold green]")
    console.print(f"Total Duration: [yellow]{duration:.2f}s[/yellow]")
    
    # Summary metrics
    summary_table = Table(title="Pipeline Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    summary_table.add_column("Status", style="green")
    
    summary_table.add_row("Specs Processed", str(result["processed_specs"]), "📊")
    summary_table.add_row("Conventions Generated", str(len(result["generated_conventions"])), "🏷️")
    summary_table.add_row("Code Files Generated", str(len(result["generated_code"])), "📄")
    summary_table.add_row("Validations Performed", str(len(result["validation_results"])), "🧪")
    
    console.print(summary_table)
    
    # Quality metrics
    if result.get("quality_metrics"):
        console.print(f"\n📈 [bold]Quality Metrics:[/bold]")
        quality = result["quality_metrics"]
        
        quality_table = Table()
        quality_table.add_column("Metric", style="cyan")
        quality_table.add_column("Score", style="yellow")
        quality_table.add_column("Grade", style="green")
        
        for metric, score in quality.items():
            if isinstance(score, (int, float)):
                grade = "A" if score > 0.9 else "B" if score > 0.8 else "C" if score > 0.7 else "D"
                quality_table.add_row(metric.replace("_", " ").title(), f"{score:.3f}", grade)
        
        console.print(quality_table)
    
    # Performance metrics
    if result.get("performance_metrics"):
        console.print(f"\n⚡ [bold]Performance Metrics:[/bold]")
        perf = result["performance_metrics"]
        for metric, value in perf.items():
            console.print(f"  • [cyan]{metric.replace('_', ' ').title()}[/cyan]: [yellow]{value}[/yellow]")
    
    # Error summary
    if result.get("errors"):
        console.print(f"\n⚠️ [bold]Errors Encountered:[/bold]")
        for error in result["errors"][:5]:  # Show first 5
            console.print(f"  • [red]{error}[/red]")
        
        if len(result["errors"]) > 5:
            console.print(f"  ... and {len(result['errors']) - 5} more errors")


def _display_benchmark_results(benchmark_results: dict):
    """Display benchmark results"""
    
    timings = [t for t in benchmark_results["timings"] if t != float('inf')]
    quality_scores = benchmark_results["quality_scores"]
    
    console.print(f"\n🏁 [bold green]Benchmark Complete![/bold green]")
    
    # Performance statistics
    if timings:
        avg_time = sum(timings) / len(timings)
        min_time = min(timings)
        max_time = max(timings)
        
        perf_table = Table(title="Performance Statistics")
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="yellow")
        perf_table.add_column("Unit", style="green")
        
        perf_table.add_row("Average Time", f"{avg_time:.3f}", "seconds")
        perf_table.add_row("Min Time", f"{min_time:.3f}", "seconds")
        perf_table.add_row("Max Time", f"{max_time:.3f}", "seconds")
        perf_table.add_row("Successful Iterations", str(len(timings)), "count")
        
        console.print(perf_table)
    
    # Quality statistics
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)
        
        quality_table = Table(title="Quality Statistics")
        quality_table.add_column("Metric", style="cyan")
        quality_table.add_column("Score", style="yellow")
        quality_table.add_column("Grade", style="green")
        
        quality_table.add_row("Average Quality", f"{avg_quality:.3f}", _score_to_grade(avg_quality))
        quality_table.add_row("Min Quality", f"{min_quality:.3f}", _score_to_grade(min_quality))
        quality_table.add_row("Max Quality", f"{max_quality:.3f}", _score_to_grade(max_quality))
        
        console.print(quality_table)


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade"""
    if score >= 0.9:
        return "A"
    elif score >= 0.8:
        return "B"
    elif score >= 0.7:
        return "C"
    elif score >= 0.6:
        return "D"
    else:
        return "F"


if __name__ == "__main__":
    app()