"""Concurrent OpenTelemetry validation command for SwarmAgent."""

import asyncio
import json
from pathlib import Path
from typing import Optional, List
import time

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from loguru import logger

from ..validation.concurrent_otel_validator import (
    ConcurrentOTELValidator, 
    TestScenario,
    ValidationStatus
)

# Initialize CLI app
app = typer.Typer(help="Concurrent OpenTelemetry validation and testing")
console = Console()


@app.command("check")
def validate_spans(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory containing telemetry spans"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit number of spans to validate"
    ),
    concurrent: bool = typer.Option(
        True,
        "--concurrent/--sequential",
        help="Run validations concurrently or sequentially"
    ),
    max_workers: int = typer.Option(
        10,
        "--workers", "-w",
        help="Maximum concurrent workers"
    )
):
    """Validate existing telemetry spans against SwarmAgent schemas."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    if not coord_dir.exists():
        rprint(f"[red]Coordination directory not found: {coord_dir}[/red]")
        raise typer.Exit(1)
    
    validator = ConcurrentOTELValidator(coord_dir, max_workers=max_workers)
    
    # Load spans
    spans = validator.load_spans(limit=limit)
    rprint(f"[cyan]Loading spans from: {coord_dir}[/cyan]")
    rprint(f"[green]Found {len(spans)} spans to validate[/green]")
    
    if not spans:
        rprint("[yellow]No spans found to validate[/yellow]")
        return
    
    # Run validation
    rprint("\n[bold]Starting validation...[/bold]")
    
    async def run_validation():
        return await validator.run_validation_suite()
    
    summary = asyncio.run(run_validation())
    
    # Display results
    validator.display_results(summary)
    
    # Exit with error if validations failed
    if summary["failed"] > 0:
        raise typer.Exit(1)


@app.command("test")
def run_test_scenarios(
    scenario: Optional[str] = typer.Option(
        None,
        "--scenario", "-s",
        help="Specific test scenario to run"
    ),
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    )
):
    """Run predefined test scenarios for agent coordination."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    validator = ConcurrentOTELValidator(coord_dir)
    
    # Define test scenarios
    all_scenarios = {
        "governance": TestScenario(
            name="governance_flow",
            description="Test complete governance workflow",
            spans_to_emit=[
                {
                    "name": "swarmsh.roberts.open",
                    "attributes": {
                        "motion_id": f"test_motion_{int(time.time())}",
                        "meeting_id": "test_meeting"
                    }
                },
                {
                    "name": "swarmsh.roberts.vote",
                    "attributes": {
                        "motion_id": f"test_motion_{int(time.time())}",
                        "voting_method": "ballot"
                    }
                },
                {
                    "name": "swarmsh.roberts.close",
                    "attributes": {
                        "motion_id": f"test_motion_{int(time.time())}",
                        "vote_result": "passed",
                        "votes_yes": 8,
                        "votes_no": 2
                    }
                }
            ],
            expected_outcomes=["motion_passed", "sprint_triggered"]
        ),
        "quality": TestScenario(
            name="quality_optimization",
            description="Test quality issue triggering optimization",
            spans_to_emit=[
                {
                    "name": "swarmsh.scrum.plan",
                    "attributes": {
                        "sprint_number": "test_99",
                        "team_id": "alpha"
                    }
                },
                {
                    "name": "swarmsh.scrum.review",
                    "attributes": {
                        "sprint_number": "test_99",
                        "defect_rate": 5.5,
                        "velocity": 32
                    }
                },
                {
                    "name": "swarmsh.lean.define",
                    "attributes": {
                        "project_id": "quality_improvement_99",
                        "problem_statement": "Defect rate above 3%"
                    }
                }
            ],
            expected_outcomes=["quality_issue_detected", "lean_project_created"]
        ),
        "full_cycle": TestScenario(
            name="full_coordination_cycle",
            description="Test complete governance→delivery→optimization cycle",
            spans_to_emit=[
                # Governance
                {"name": "swarmsh.roberts.open", "attributes": {"motion_id": "cycle_test", "meeting_id": "board"}},
                {"name": "swarmsh.roberts.vote", "attributes": {"motion_id": "cycle_test", "voting_method": "voice_vote"}},
                {"name": "swarmsh.roberts.close", "attributes": {"motion_id": "cycle_test", "vote_result": "passed", "sprint_number": "100"}},
                # Delivery
                {"name": "swarmsh.scrum.plan", "attributes": {"sprint_number": "100", "team_id": "alpha", "capacity": 50}},
                {"name": "swarmsh.scrum.review", "attributes": {"sprint_number": "100", "defect_rate": 4.2, "velocity": 48}},
                # Optimization
                {"name": "swarmsh.lean.define", "attributes": {"project_id": "opt_100", "problem_statement": "High defect rate"}},
                {"name": "swarmsh.lean.measure", "attributes": {"project_id": "opt_100"}},
                {"name": "swarmsh.lean.analyze", "attributes": {"project_id": "opt_100"}}
            ],
            expected_outcomes=["full_cycle_complete", "all_agents_activated"]
        )
    }
    
    # Select scenarios to run
    scenarios_to_run = []
    if scenario:
        if scenario in all_scenarios:
            scenarios_to_run.append(all_scenarios[scenario])
        else:
            rprint(f"[red]Unknown scenario: {scenario}[/red]")
            rprint(f"Available scenarios: {', '.join(all_scenarios.keys())}")
            raise typer.Exit(1)
    else:
        scenarios_to_run = list(all_scenarios.values())
    
    # Run test scenarios
    rprint(f"\n[bold]Running {len(scenarios_to_run)} test scenarios...[/bold]")
    
    async def run_tests():
        return await validator.run_validation_suite(test_scenarios=scenarios_to_run)
    
    summary = asyncio.run(run_tests())
    
    # Display results
    validator.display_results(summary)
    
    # Show scenario-specific results
    if summary.get("checks_by_type", {}).get("scenario"):
        scenario_stats = summary["checks_by_type"]["scenario"]
        
        panel = Panel(
            f"Test Scenarios: {scenario_stats['passed']}/{scenario_stats['total']} passed",
            title="🧪 Test Results",
            border_style="green" if scenario_stats['failed'] == 0 else "red"
        )
        console.print(panel)


@app.command("benchmark")
def benchmark_validation(
    spans_count: int = typer.Option(
        1000,
        "--spans", "-n",
        help="Number of spans to generate for benchmark"
    ),
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    )
):
    """Benchmark concurrent validation performance."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    validator = ConcurrentOTELValidator(coord_dir)
    
    rprint(f"[bold]Running validation benchmark with {spans_count} spans...[/bold]")
    
    # Generate test spans
    test_spans = []
    agent_types = ["roberts", "scrum", "lean"]
    triggers = {
        "roberts": ["open", "vote", "close"],
        "scrum": ["plan", "review"],
        "lean": ["define", "measure", "analyze"]
    }
    
    for i in range(spans_count):
        agent = agent_types[i % len(agent_types)]
        trigger = triggers[agent][i % len(triggers[agent])]
        
        span = {
            "name": f"swarmsh.{agent}.{trigger}",
            "trace_id": f"bench_trace_{i}",
            "span_id": f"bench_span_{i}",
            "timestamp": time.time() + i,
            "attributes": {
                "test_id": f"benchmark_{i}",
                "agent": agent
            }
        }
        
        # Add agent-specific attributes
        if agent == "roberts" and trigger == "open":
            span["attributes"].update({"motion_id": f"motion_{i}", "meeting_id": "bench"})
        elif agent == "scrum" and trigger == "plan":
            span["attributes"].update({"sprint_number": str(i), "team_id": "bench"})
        elif agent == "lean" and trigger == "define":
            span["attributes"].update({"project_id": f"proj_{i}", "problem_statement": "test"})
        
        test_spans.append(span)
    
    # Write test spans to temporary file
    temp_file = coord_dir / "benchmark_spans.jsonl"
    with open(temp_file, 'w') as f:
        for span in test_spans:
            f.write(json.dumps(span) + '\n')
    
    # Run benchmark
    start_time = time.time()
    
    async def run_benchmark():
        # Override load_spans to use our test data
        original_load = validator.load_spans
        validator.load_spans = lambda limit=None: test_spans[:limit] if limit else test_spans
        
        try:
            return await validator.run_validation_suite()
        finally:
            validator.load_spans = original_load
    
    summary = asyncio.run(run_benchmark())
    total_time = time.time() - start_time
    
    # Display benchmark results
    table = Table(title="🚀 Validation Benchmark Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Spans", str(spans_count))
    table.add_row("Total Validations", str(summary["total_checks"]))
    table.add_row("Total Duration", f"{total_time:.2f} seconds")
    table.add_row("Validations/Second", f"{summary['total_checks'] / total_time:.1f}")
    table.add_row("Avg Validation Time", f"{summary['performance_stats']['avg_duration_ms']:.1f}ms")
    table.add_row("Max Validation Time", f"{summary['performance_stats']['max_duration_ms']:.1f}ms")
    table.add_row("Min Validation Time", f"{summary['performance_stats']['min_duration_ms']:.1f}ms")
    
    console.print(table)
    
    # Clean up
    if temp_file.exists():
        temp_file.unlink()


@app.command("monitor")
def monitor_realtime(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    ),
    interval: int = typer.Option(
        5,
        "--interval", "-i",
        help="Validation interval in seconds"
    )
):
    """Monitor and validate spans in real-time."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    validator = ConcurrentOTELValidator(coord_dir)
    
    rprint("[bold]Starting real-time validation monitor...[/bold]")
    rprint(f"Checking every {interval} seconds. Press Ctrl+C to stop.\n")
    
    last_span_count = 0
    
    try:
        while True:
            # Get current spans
            spans = validator.load_spans()
            new_spans = len(spans) - last_span_count
            
            if new_spans > 0:
                rprint(f"\n[green]Found {new_spans} new spans[/green]")
                
                # Run validation on new spans
                async def validate_new():
                    # Create a custom validator that only checks new spans
                    temp_validator = ConcurrentOTELValidator(coord_dir)
                    temp_validator.load_spans = lambda limit=None: spans[-new_spans:]
                    return await temp_validator.run_validation_suite()
                
                summary = asyncio.run(validate_new())
                
                # Display compact results
                status = "✅" if summary["failed"] == 0 else "❌"
                rprint(f"{status} Validation: {summary['passed']}/{summary['total_checks']} passed")
                
                if summary["failed"] > 0:
                    rprint("[red]Failed checks:[/red]")
                    for check in summary["failed_checks"][:3]:  # Show first 3
                        rprint(f"  - {check['check']}: {check['message']}")
                
                last_span_count = len(spans)
            else:
                rprint(f"[dim]No new spans (total: {len(spans)})[/dim]", end='\r')
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        rprint("\n[yellow]Monitoring stopped[/yellow]")


@app.command("report")
def generate_report(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for report"
    ),
    format: str = typer.Option(
        "json",
        "--format", "-f",
        help="Report format (json, markdown)"
    )
):
    """Generate comprehensive validation report."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    validator = ConcurrentOTELValidator(coord_dir)
    
    rprint("[bold]Generating validation report...[/bold]")
    
    # Run full validation
    async def run_full_validation():
        return await validator.run_validation_suite()
    
    summary = asyncio.run(run_full_validation())
    
    # Generate report content
    if format == "markdown":
        report = f"""# SwarmAgent Validation Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Checks**: {summary['total_checks']}
- **Passed**: {summary['passed']} ({summary['passed']/summary['total_checks']*100:.1f}%)
- **Failed**: {summary['failed']} ({summary['failed']/summary['total_checks']*100:.1f}%)
- **Errors**: {summary['errors']}
- **Duration**: {summary['duration_seconds']:.2f} seconds

## Performance

- **Average Check Time**: {summary['performance_stats']['avg_duration_ms']:.1f}ms
- **Maximum Check Time**: {summary['performance_stats']['max_duration_ms']:.1f}ms
- **Minimum Check Time**: {summary['performance_stats']['min_duration_ms']:.1f}ms

## Results by Type

"""
        for check_type, stats in summary['checks_by_type'].items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report += f"### {check_type.title()}\n"
            report += f"- Total: {stats['total']}\n"
            report += f"- Passed: {stats['passed']}\n"
            report += f"- Failed: {stats['failed']}\n"
            report += f"- Success Rate: {success_rate:.1f}%\n\n"
        
        if summary['failed_checks']:
            report += "## Failed Checks\n\n"
            for check in summary['failed_checks']:
                report += f"- **{check['check']}**: {check['message']}\n"
                if check.get('details'):
                    report += f"  - Details: `{check['details']}`\n"
    else:
        # JSON format
        report = json.dumps(summary, indent=2)
    
    # Save or display report
    if output:
        output.write_text(report)
        rprint(f"[green]Report saved to: {output}[/green]")
    else:
        console.print(report)


if __name__ == "__main__":
    app()