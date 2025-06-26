"""Weaver-first OpenTelemetry validation commands for SwarmAgent.

80/20 refactor CLI using Weaver-generated semantic conventions.
"""

import asyncio
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from loguru import logger

from ..validation.weaver_otel_validator import WeaverOTELValidator

# Initialize CLI app
app = typer.Typer(help="Weaver-first OpenTelemetry validation and testing")
console = Console()


@app.command("check")
def validate_weaver_spans(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory containing telemetry spans"
    ),
    convention: str = typer.Option(
        "swarm_agent",
        "--convention", "-c",
        help="Weaver semantic convention to use for validation"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit number of spans to validate"
    ),
    max_workers: int = typer.Option(
        20,
        "--workers", "-w",
        help="Maximum concurrent workers for validation"
    )
):
    """Validate telemetry spans using Weaver-generated semantic conventions."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    if not coord_dir.exists():
        console.print(f"[red]Coordination directory not found: {coord_dir}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]🔧 Starting Weaver validation with convention: {convention}[/cyan]")
    
    # Create Weaver validator
    validator = WeaverOTELValidator(
        coordination_dir=coord_dir,
        convention_name=convention,
        max_workers=max_workers
    )
    
    # Load spans with limit
    spans = validator.load_spans(limit=limit)
    console.print(f"[green]Found {len(spans)} spans to validate[/green]")
    
    if not spans:
        console.print("[yellow]No spans found to validate[/yellow]")
        return
    
    # Run Weaver validation
    console.print("\\n[bold]Starting Weaver-powered validation...[/bold]")
    
    async def run_validation():
        return await validator.run_weaver_validation_suite()
    
    summary = asyncio.run(run_validation())
    
    # Show performance summary
    panel = Panel(
        f"""Weaver Validation Complete!

🔧 Convention: {summary['weaver_convention']}
📊 Validations: {summary['total_validations']}
✅ Passed: {summary['passed']}
❌ Failed: {summary['failed']}
⚠️  Errors: {summary['errors']}

🚀 Performance:
   Throughput: {summary['throughput_per_second']:.1f} validations/sec
   Duration: {summary['duration_seconds']:.2f} seconds
   Avg Check: {summary['performance_stats']['avg_duration_ms']:.1f}ms""",
        title="🎯 Weaver Validation Results",
        border_style="green" if summary['failed'] == 0 else "red"
    )
    console.print(panel)
    
    # Exit with error if validations failed
    if summary['failed'] > 0:
        raise typer.Exit(1)


@app.command("benchmark")
def benchmark_weaver_validation(
    spans_count: int = typer.Option(
        500,
        "--spans", "-n",
        help="Number of spans to generate for benchmark"
    ),
    convention: str = typer.Option(
        "swarm_agent",
        "--convention", "-c",
        help="Weaver semantic convention for benchmark"
    ),
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    )
):
    """Benchmark Weaver validation performance."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    console.print(f"[bold]🚀 Running Weaver validation benchmark with {spans_count} spans...[/bold]")
    console.print(f"[cyan]Convention: {convention}[/cyan]")
    
    # Create validator
    validator = WeaverOTELValidator(
        coordination_dir=coord_dir,
        convention_name=convention,
        max_workers=50  # Higher concurrency for benchmark
    )
    
    # Generate test spans following Weaver conventions
    test_spans = []
    span_types = [
        ("swarmsh.roberts.open", {"motion_id": "bench_motion", "swarm.agent": "roberts", "swarm.trigger": "open"}),
        ("swarmsh.roberts.vote", {"motion_id": "bench_motion", "swarm.agent": "roberts", "swarm.trigger": "vote"}),
        ("swarmsh.roberts.close", {"motion_id": "bench_motion", "swarm.agent": "roberts", "swarm.trigger": "close"}),
        ("swarmsh.scrum.plan", {"sprint_number": "bench_sprint", "swarm.agent": "scrum", "swarm.trigger": "plan"}),
        ("swarmsh.scrum.review", {"sprint_number": "bench_sprint", "swarm.agent": "scrum", "swarm.trigger": "review"}),
        ("swarmsh.lean.define", {"project_id": "bench_project", "swarm.agent": "lean", "swarm.trigger": "define"}),
        ("swarmsh.lean.measure", {"project_id": "bench_project", "swarm.agent": "lean", "swarm.trigger": "measure"}),
        ("swarmsh.lean.analyze", {"project_id": "bench_project", "swarm.agent": "lean", "swarm.trigger": "analyze"})
    ]
    
    for i in range(spans_count):
        span_type, base_attrs = span_types[i % len(span_types)]
        
        # Add unique identifiers
        attrs = base_attrs.copy()
        attrs.update({
            "benchmark_id": f"bench_{i}",
            "iteration": i
        })
        
        span = {
            "name": span_type,
            "trace_id": f"bench_trace_{i}",
            "span_id": f"bench_span_{i}",
            "timestamp": time.time() + i * 0.001,  # Stagger timestamps
            "attributes": attrs
        }
        test_spans.append(span)
    
    # Override load_spans for benchmark
    original_load = validator.load_spans
    validator.load_spans = lambda limit=None: test_spans[:limit] if limit else test_spans
    
    # Run benchmark
    start_time = time.time()
    
    async def run_benchmark():
        return await validator.run_weaver_validation_suite()
    
    try:
        summary = asyncio.run(run_benchmark())
        total_time = time.time() - start_time
        
        # Display benchmark results
        from rich.table import Table
        
        table = Table(title="🔧 Weaver Validation Benchmark Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Convention", convention)
        table.add_row("Test Spans", str(spans_count))
        table.add_row("Total Validations", str(summary["total_validations"]))
        table.add_row("Total Duration", f"{total_time:.2f} seconds")
        table.add_row("Throughput", f"{summary['total_validations'] / total_time:.1f} validations/sec")
        table.add_row("Avg Validation Time", f"{summary['performance_stats']['avg_duration_ms']:.1f}ms")
        table.add_row("Success Rate", f"{summary['passed'] / summary['total_validations'] * 100:.1f}%")
        table.add_row("Weaver Rules", str(summary["validation_rules"]))
        
        console.print(table)
        
        if summary["passed"] == summary["total_validations"]:
            console.print("\\n[green]🎯 All validations passed! Weaver conventions working perfectly.[/green]")
        else:
            console.print(f"\\n[yellow]⚠️  {summary['failed']} validations failed - check span compliance[/yellow]")
    
    finally:
        # Restore original method
        validator.load_spans = original_load


@app.command("compare")
def compare_validators(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    ),
    limit: int = typer.Option(
        100,
        "--limit", "-l",
        help="Number of spans to compare"
    )
):
    """Compare Weaver validator vs legacy validator performance."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    console.print("[bold]🔧 Comparing Weaver vs Legacy Validation[/bold]")
    
    # Test Weaver validator
    console.print("\\n[cyan]Testing Weaver Validator...[/cyan]")
    weaver_validator = WeaverOTELValidator(coord_dir, max_workers=20)
    
    start_time = time.time()
    async def run_weaver():
        spans = weaver_validator.load_spans(limit=limit)
        return await weaver_validator.run_concurrent_validation(spans)
    
    weaver_results = asyncio.run(run_weaver())
    weaver_time = time.time() - start_time
    
    # Test legacy validator
    console.print("[cyan]Testing Legacy Validator...[/cyan]")
    from ..validation.concurrent_otel_validator import ConcurrentOTELValidator
    
    legacy_validator = ConcurrentOTELValidator(coord_dir, max_workers=20)
    
    start_time = time.time()
    async def run_legacy():
        return await legacy_validator.run_validation_suite()
    
    legacy_summary = asyncio.run(run_legacy())
    legacy_time = time.time() - start_time
    
    # Comparison results
    from rich.table import Table
    
    table = Table(title="🔧 Validator Performance Comparison")
    table.add_column("Metric", style="cyan")
    table.add_column("Weaver Validator", style="green")
    table.add_column("Legacy Validator", style="yellow")
    table.add_column("Improvement", style="blue")
    
    weaver_passed = sum(1 for r in weaver_results if r.status.value == "passed")
    weaver_failed = sum(1 for r in weaver_results if r.status.value == "failed")
    
    improvement_time = ((legacy_time - weaver_time) / legacy_time * 100) if legacy_time > 0 else 0
    improvement_throughput = (len(weaver_results) / weaver_time) / (legacy_summary["total_checks"] / legacy_time) if legacy_time > 0 and weaver_time > 0 else 1
    
    table.add_row("Total Validations", str(len(weaver_results)), str(legacy_summary["total_checks"]), "")
    table.add_row("Duration", f"{weaver_time:.2f}s", f"{legacy_time:.2f}s", f"{improvement_time:.1f}% faster" if improvement_time > 0 else "slower")
    table.add_row("Throughput", f"{len(weaver_results)/weaver_time:.1f}/s", f"{legacy_summary['total_checks']/legacy_time:.1f}/s", f"{improvement_throughput:.1f}x")
    table.add_row("Passed", str(weaver_passed), str(legacy_summary["passed"]), "")
    table.add_row("Failed", str(weaver_failed), str(legacy_summary["failed"]), "")
    table.add_row("Schema Source", "Weaver Convention", "Hardcoded Rules", "🎯 Maintainable")
    
    console.print(table)
    
    console.print("\\n[green]✨ Weaver advantages:[/green]")
    console.print("  • Schema-driven validation from semantic conventions")
    console.print("  • Legacy format auto-normalization")
    console.print("  • Better span type analysis")
    console.print("  • Convention-based rule generation")
    console.print("  • Enhanced telemetry with Weaver metadata")


@app.command("init")
def init_weaver_validation():
    """Initialize Weaver validation with semantic conventions."""
    
    console.print("[bold]🔧 Initializing Weaver Validation System[/bold]")
    
    # Check if Weaver conventions exist
    from ..core.weaver_engine import WeaverEngine
    
    try:
        engine = WeaverEngine()
        conventions = engine.list_conventions()
        
        if "swarm_agent" in conventions:
            console.print("[green]✅ SwarmAgent convention found[/green]")
        else:
            console.print("[yellow]⚠️  SwarmAgent convention not found, using fallback rules[/yellow]")
        
        console.print(f"Available conventions: {', '.join(conventions)}")
        
        # Test validation
        validator = WeaverOTELValidator(convention_name="swarm_agent")
        console.print(f"[green]✅ Weaver validator initialized with {len(validator.validation_cache)} rules[/green]")
        
        console.print("\\n[cyan]Next steps:[/cyan]")
        console.print("  • Run: dsl validate-weaver check")
        console.print("  • Benchmark: dsl validate-weaver benchmark")
        console.print("  • Compare: dsl validate-weaver compare")
        
    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()