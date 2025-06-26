"""SwarmAgent Validation Loop CLI - Continuous monitoring and auto-remediation."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from loguru import logger

from ..validation.swarm_validation_loop import (
    SwarmValidationLoop, 
    LoopStatus,
    slack_alert_handler,
    email_alert_handler,
    pagerduty_alert_handler
)

# Initialize CLI app
app = typer.Typer(help="SwarmAgent validation loop with continuous monitoring")
console = Console()


@app.command("start")
def start_validation_loop(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory containing telemetry spans"
    ),
    convention: str = typer.Option(
        "swarm_agent",
        "--convention", "-c",
        help="Weaver semantic convention to use"
    ),
    interval: float = typer.Option(
        2.0,
        "--interval", "-i",
        help="Validation interval in seconds"
    ),
    auto_remediation: bool = typer.Option(
        True,
        "--auto-remediation/--no-auto-remediation",
        help="Enable automatic remediation of validation failures"
    ),
    max_attempts: int = typer.Option(
        3,
        "--max-attempts", "-m",
        help="Maximum remediation attempts per span"
    ),
    alerts: bool = typer.Option(
        False,
        "--alerts/--no-alerts",
        help="Enable alert handlers (Slack, email, PagerDuty)"
    ),
    live_display: bool = typer.Option(
        True,
        "--live/--no-live",
        help="Show live dashboard display"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output final metrics as JSON"
    )
):
    """Start the SwarmAgent validation loop with continuous monitoring."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    if not coord_dir.exists():
        console.print(f"[red]Coordination directory not found: {coord_dir}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold green]🚀 Starting SwarmAgent Validation Loop[/bold green]")
    console.print(f"[cyan]Convention:[/cyan] {convention}")
    console.print(f"[cyan]Directory:[/cyan] {coord_dir}")
    console.print(f"[cyan]Interval:[/cyan] {interval}s")
    console.print(f"[cyan]Auto-remediation:[/cyan] {'✅ Enabled' if auto_remediation else '❌ Disabled'}")
    
    # Create validation loop
    loop = SwarmValidationLoop(
        coordination_dir=coord_dir,
        convention_name=convention,
        validation_interval=interval,
        max_remediation_attempts=max_attempts,
        enable_auto_remediation=auto_remediation
    )
    
    # Add alert handlers if enabled
    if alerts:
        console.print("[yellow]📢 Adding alert handlers...[/yellow]")
        loop.add_alert_handler(slack_alert_handler)
        loop.add_alert_handler(email_alert_handler)
        loop.add_alert_handler(pagerduty_alert_handler)
    
    # Start the loop
    try:
        asyncio.run(loop.start_loop(display_live=live_display))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Validation loop interrupted[/yellow]")
    
    finally:
        # Display final metrics
        summary = loop.get_metrics_summary()
        
        if json_output:
            console.print(json.dumps(summary, indent=2))
        else:
            _display_summary(summary)


@app.command("status")
def show_status(
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    )
):
    """Show current validation loop status and metrics."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    # Check if spans file exists and get basic stats
    spans_file = coord_dir / "telemetry_spans.jsonl"
    
    if not spans_file.exists():
        console.print(f"[red]No telemetry spans found at: {spans_file}[/red]")
        return
    
    # Count spans and analyze
    total_spans = 0
    new_format_spans = 0
    legacy_format_spans = 0
    span_types = set()
    
    try:
        with open(spans_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        span = json.loads(line)
                        total_spans += 1
                        
                        if "ts" in span and "attrs" in span:
                            legacy_format_spans += 1
                        else:
                            new_format_spans += 1
                        
                        span_types.add(span.get("name", "unknown"))
                        
                    except json.JSONDecodeError:
                        continue
    
    except Exception as e:
        console.print(f"[red]Error reading spans file: {e}[/red]")
        return
    
    # Display status
    status_panel = Panel(f"""📊 SwarmAgent Telemetry Status

📂 Coordination Directory: {coord_dir}
📄 Spans File: {spans_file}

📈 Span Statistics:
   Total Spans: {total_spans}
   New Format: {new_format_spans}
   Legacy Format: {legacy_format_spans}
   Unique Types: {len(span_types)}

🔍 Span Types Found:
{chr(10).join(f"   • {span_type}" for span_type in sorted(span_types))}

💡 Next Steps:
   • Run: dsl validation-loop start
   • Monitor: dsl validation-loop start --live
   • Auto-fix: dsl validation-loop start --auto-remediation""", 
        title="🔄 Validation Loop Status",
        border_style="blue"
    )
    
    console.print(status_panel)


@app.command("test")
def test_validation_loop(
    duration: int = typer.Option(
        30,
        "--duration", "-t",
        help="Test duration in seconds"
    ),
    coordination_dir: Optional[Path] = typer.Option(
        None,
        "--dir", "-d",
        help="Coordination directory"
    ),
    convention: str = typer.Option(
        "swarm_agent",
        "--convention", "-c",
        help="Weaver semantic convention"
    )
):
    """Run validation loop test for specified duration."""
    
    coord_dir = coordination_dir or Path("/Users/sac/s2s/agent_coordination")
    
    console.print(f"[bold]🧪 Testing validation loop for {duration} seconds[/bold]")
    
    # Create test loop with faster interval
    loop = SwarmValidationLoop(
        coordination_dir=coord_dir,
        convention_name=convention,
        validation_interval=0.5,  # Faster for testing
        enable_auto_remediation=True
    )
    
    async def run_test():
        # Start loop in background
        loop_task = asyncio.create_task(loop.start_loop(display_live=False))
        
        # Wait for test duration
        await asyncio.sleep(duration)
        
        # Stop loop
        loop.stop_loop()
        
        # Wait for graceful shutdown
        try:
            await asyncio.wait_for(loop_task, timeout=5.0)
        except asyncio.TimeoutError:
            loop_task.cancel()
    
    try:
        asyncio.run(run_test())
        
        # Display test results
        summary = loop.get_metrics_summary()
        _display_summary(summary, is_test=True)
        
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("demo")
def demo_validation_loop():
    """Run a demonstration of the validation loop with sample data."""
    
    console.print("[bold]🎯 SwarmAgent Validation Loop Demo[/bold]")
    console.print("=" * 50)
    
    # Create demo spans
    demo_spans = [
        {
            "name": "swarmsh.roberts.open",
            "trace_id": "demo_trace_001",
            "span_id": "demo_span_001", 
            "timestamp": 1234567890.123,
            "attributes": {
                "swarm.agent": "roberts",
                "swarm.trigger": "open",
                "motion_id": "demo_motion_001"
            }
        },
        {
            "name": "swarmsh.scrum.plan",
            "trace_id": "demo_trace_002",
            "span_id": "demo_span_002",
            "timestamp": 1234567891.456,
            "attributes": {
                "swarm.agent": "scrum", 
                "swarm.trigger": "plan",
                "sprint_number": "demo_sprint"
            }
        },
        # Intentionally broken span for remediation demo
        {
            "name": "swarmsh.lean.define",
            "trace_id": "demo_trace_003",
            "span_id": "demo_span_003",
            # Missing timestamp and some attributes
            "attributes": {
                "project_id": "demo_project"
                # Missing swarm.agent and swarm.trigger
            }
        }
    ]
    
    # Write demo spans to temporary file
    demo_dir = Path("/tmp/swarm_demo")
    demo_dir.mkdir(exist_ok=True)
    demo_spans_file = demo_dir / "telemetry_spans.jsonl"
    
    with open(demo_spans_file, 'w') as f:
        for span in demo_spans:
            f.write(json.dumps(span) + '\n')
    
    console.print(f"[green]📝 Created demo spans at: {demo_spans_file}[/green]")
    
    # Run demo loop
    console.print("\n[cyan]🚀 Starting demo validation loop...[/cyan]")
    
    loop = SwarmValidationLoop(
        coordination_dir=demo_dir,
        convention_name="swarm_agent",
        validation_interval=1.0,
        enable_auto_remediation=True
    )
    
    async def run_demo():
        # Start loop for 10 seconds
        loop_task = asyncio.create_task(loop.start_loop(display_live=True))
        await asyncio.sleep(10)
        loop.stop_loop()
        
        try:
            await asyncio.wait_for(loop_task, timeout=5.0)
        except asyncio.TimeoutError:
            loop_task.cancel()
    
    try:
        asyncio.run(run_demo())
        
        # Show demo results
        summary = loop.get_metrics_summary()
        console.print("\n[bold]📊 Demo Results:[/bold]")
        _display_summary(summary, is_test=True)
        
        console.print("\n[green]✨ Demo completed successfully![/green]")
        console.print("[dim]💡 Try running with your own telemetry data using: dsl validation-loop start[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    
    finally:
        # Cleanup demo files
        if demo_spans_file.exists():
            demo_spans_file.unlink()
        if demo_dir.exists():
            demo_dir.rmdir()


def _display_summary(summary: dict, is_test: bool = False):
    """Display metrics summary."""
    metrics = summary["metrics"]
    config = summary["configuration"]
    
    title = "🧪 Test Results" if is_test else "📊 Final Metrics"
    
    summary_panel = Panel(f"""{title}

🔢 Validation Metrics:
   Spans Processed: {metrics['total_spans_processed']}
   Total Validations: {metrics['total_validations']}
   ✅ Passed: {metrics['passed_validations']}
   ❌ Failed: {metrics['failed_validations']}
   ⚠️  Errors: {metrics['error_validations']}
   Success Rate: {metrics['success_rate_percent']:.1f}%

🔧 Auto-Remediation:
   Attempts: {metrics['auto_remediations']}
   Successful: {metrics['successful_remediations']}
   Success Rate: {metrics['remediation_rate_percent']:.1f}%

⚡ Performance:
   Avg Validation: {metrics['avg_validation_time_ms']:.1f}ms
   Peak Throughput: {metrics['peak_throughput']:.1f}/s
   Uptime: {metrics['uptime_seconds']:.0f}s

⚙️  Configuration:
   Convention: {config['convention_name']}
   Interval: {config['validation_interval']}s
   Auto-Remediation: {'✅' if config['enable_auto_remediation'] else '❌'}""",
        title=f"🔄 SwarmAgent Validation Loop",
        border_style="green" if metrics['success_rate_percent'] > 80 else "yellow"
    )
    
    console.print(summary_panel)


if __name__ == "__main__":
    app()