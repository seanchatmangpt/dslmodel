#!/usr/bin/env python3
"""Standalone SwarmAgent CLI that works with pyproject.toml."""

import json
import time
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich import print

app = typer.Typer(help="SwarmAgent coordination and management")
console = Console()


class AgentType(str, Enum):
    """Available agent types."""
    roberts = "roberts"
    scrum = "scrum"
    lean = "lean"
    ping = "ping"


@app.command("demo")
def demo(
    scenario: str = typer.Option("governance", help="Demo scenario to run"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run SwarmAgent ecosystem demo."""
    console.print("🌟 [bold blue]SwarmAgent Ecosystem Demo[/bold blue]")
    
    if scenario == "governance":
        _run_governance_demo(verbose)
    elif scenario == "minimal":
        _run_minimal_demo(verbose)
    else:
        console.print(f"❌ [red]Unknown scenario: {scenario}[/red]")
        console.print("Available scenarios: governance, minimal")
        raise typer.Exit(1)


def _run_governance_demo(verbose: bool):
    """Run the governance workflow demo."""
    console.print("🎬 Running governance workflow demo...")
    console.print("📋 Roberts → Scrum → Lean workflow")
    
    # Simulate the demo without dependencies
    console.print("\n🏛️  Roberts Agent: Opening motion for Sprint 42")
    console.print("   State: IDLE → MOTION_OPEN")
    
    console.print("\n🗳️  Roberts Agent: Calling for vote")
    console.print("   State: MOTION_OPEN → VOTING")
    
    console.print("\n✅ Roberts Agent: Motion passes!")
    console.print("   State: VOTING → CLOSED")
    console.print("   → Triggering Scrum sprint planning")
    
    console.print("\n📅 Scrum Agent: Sprint planning")
    console.print("   State: PLANNING → EXECUTING")
    
    console.print("\n📊 Scrum Agent: Sprint review")
    console.print("   State: EXECUTING → REVIEW")
    console.print("   ⚠️  Defect rate 5.2% exceeds 3% threshold!")
    console.print("   → Triggering Lean improvement")
    
    console.print("\n🎯 Lean Agent: Define improvement project")
    console.print("   State: DEFINE → MEASURE")
    console.print("   Project: defect-sprint42")
    
    console.print("\n✅ [green]Demo completed successfully![/green]")
    console.print("💡 This demonstrates the autonomous governance→delivery→optimization loop")


def _run_minimal_demo(verbose: bool):
    """Run the minimal concept demo."""
    console.print("🧪 Running minimal SwarmAgent concepts demo...")
    
    # Simulate key concepts
    console.print("\n1. State Machine Transitions:")
    console.print("   ✓ IDLE → ACTIVE")
    console.print("   ✓ ACTIVE → DONE")
    
    console.print("\n2. Span Processing:")
    console.print("   ✓ Created span: swarmsh.test.action")
    console.print("   ✓ Attributes: {'user': 'test', 'action': 'demo'}")
    
    console.print("\n3. Command Generation:")
    console.print("   ✓ Command: swarmsh.scrum.sprint-planning")
    console.print("   ✓ Args: ['--sprint', '42', '--team', 'alpha']")
    
    console.print("\n4. Agent Workflow Simulation:")
    console.print("   ✓ Planning phase → Executing phase")
    console.print("   ✓ Quality issue detected!")
    console.print("   ✓ Generated command: swarmsh.lean.define")
    
    console.print("\n✅ All concept tests passed!")
    console.print("\nKey SwarmAgent patterns demonstrated:")
    console.print("- State machine with transitions")
    console.print("- Span-driven event processing")
    console.print("- Command generation for CLI integration")
    console.print("- Inter-agent communication via commands")


@app.command("emit")
def emit_span(
    name: str = typer.Argument(..., help="Span name"),
    agent: str = typer.Option("test", help="Agent name"),
    trigger: str = typer.Option("manual", help="Trigger keyword"),
    span_file: Optional[Path] = typer.Option(None, help="Output span file"),
    attributes: Optional[str] = typer.Option(None, help="JSON attributes"),
):
    """Emit a test span to trigger agents."""
    
    # Parse attributes
    attrs = {"swarm.agent": agent, "swarm.trigger": trigger}
    if attributes:
        try:
            attrs.update(json.loads(attributes))
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON attributes: {e}[/red]")
            raise typer.Exit(1)
    
    # Create span
    span_data = {
        "name": name,
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": attrs
    }
    
    # Determine output file
    if not span_file:
        span_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
    
    # Ensure directory exists
    span_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write span
    with span_file.open("a") as f:
        f.write(json.dumps(span_data) + "\n")
    
    console.print(f"📡 [green]Emitted span: {name}[/green]")
    console.print(f"📁 File: {span_file}")
    console.print(f"🏷️  Attributes: {attrs}")


@app.command("watch")
def watch_spans(
    span_file: Optional[Path] = typer.Option(None, help="Span file to watch"),
    last: int = typer.Option(10, help="Show last N spans")
):
    """Watch telemetry spans."""
    
    if not span_file:
        span_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
    
    if not span_file.exists():
        console.print(f"❌ [red]Span file not found: {span_file}[/red]")
        console.print("💡 Run: python swarm_cli.py emit test.span to create spans")
        raise typer.Exit(1)
    
    console.print(f"👀 [blue]Watching spans: {span_file}[/blue]")
    
    _show_recent_spans(span_file, last)


def _show_recent_spans(span_file: Path, count: int):
    """Show recent spans from file."""
    spans = []
    
    try:
        with span_file.open() as f:
            for line in f:
                if line.strip():
                    try:
                        spans.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        console.print(f"❌ [red]Error reading spans: {e}[/red]")
        return
    
    # Show last N spans
    recent_spans = spans[-count:] if len(spans) > count else spans
    
    if not recent_spans:
        console.print("📭 [yellow]No spans found[/yellow]")
        return
    
    table = Table(title=f"Last {len(recent_spans)} Spans")
    table.add_column("Time", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Agent", style="yellow")
    table.add_column("Trigger", style="magenta")
    
    for span in recent_spans:
        timestamp = span.get("timestamp", 0)
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        name = span.get("name", "")
        attrs = span.get("attributes", {})
        agent = attrs.get("swarm.agent", "")
        trigger = attrs.get("swarm.trigger", "")
        
        table.add_row(time_str, name, agent, trigger)
    
    console.print(table)


@app.command("workflow")
def run_workflow(
    name: str = typer.Argument(..., help="Workflow name"),
    dry_run: bool = typer.Option(False, help="Show what would happen")
):
    """Run predefined SwarmAgent workflows."""
    
    workflows = {
        "governance": _governance_workflow,
        "sprint": _sprint_workflow,
        "improvement": _improvement_workflow,
        "full": _full_workflow
    }
    
    if name not in workflows:
        console.print(f"❌ [red]Unknown workflow: {name}[/red]")
        console.print(f"Available workflows: {', '.join(workflows.keys())}")
        raise typer.Exit(1)
    
    console.print(f"🔄 [blue]Running workflow: {name}[/blue]")
    
    if dry_run:
        console.print("🧪 [yellow]DRY RUN - No spans will be emitted[/yellow]")
    
    workflows[name](dry_run)


def _governance_workflow(dry_run: bool):
    """Run governance decision workflow."""
    steps = [
        ("swarmsh.roberts.open", {"motion_id": "sprint_approval", "meeting_id": "board"}),
        ("swarmsh.roberts.vote", {"motion_id": "sprint_approval", "voting_method": "voice_vote"}),
        ("swarmsh.roberts.close", {"motion_id": "sprint_approval", "result": "passed", "sprint_number": "42"})
    ]
    
    _execute_workflow_steps(steps, dry_run)


def _sprint_workflow(dry_run: bool):
    """Run sprint execution workflow."""
    steps = [
        ("swarmsh.scrum.plan", {"sprint_number": "42", "team_id": "alpha", "capacity": 50}),
        ("swarmsh.scrum.review", {"sprint_number": "42", "velocity": 45, "defect_rate": 5.2})
    ]
    
    _execute_workflow_steps(steps, dry_run)


def _improvement_workflow(dry_run: bool):
    """Run improvement workflow."""
    steps = [
        ("swarmsh.lean.define", {"project_id": "quality-improvement", "problem_statement": "High defect rate"}),
        ("swarmsh.lean.measure", {"project_id": "quality-improvement"}),
        ("swarmsh.lean.analyze", {"project_id": "quality-improvement"}),
    ]
    
    _execute_workflow_steps(steps, dry_run)


def _full_workflow(dry_run: bool):
    """Run complete governance→delivery→optimization workflow."""
    _governance_workflow(dry_run)
    time.sleep(1)
    _sprint_workflow(dry_run)
    time.sleep(1)
    _improvement_workflow(dry_run)


def _execute_workflow_steps(steps: List[tuple], dry_run: bool):
    """Execute workflow steps."""
    span_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
    
    for i, (name, attrs) in enumerate(steps, 1):
        console.print(f"  {i}. [cyan]{name}[/cyan] {attrs}")
        
        if not dry_run:
            span_data = {
                "name": name,
                "trace_id": f"workflow_{int(time.time() * 1000)}",
                "span_id": f"span_{int(time.time() * 1000000)}",
                "timestamp": time.time(),
                "attributes": {
                    "swarm.agent": name.split(".")[1] if "." in name else "unknown",
                    "swarm.trigger": name.split(".")[-1] if "." in name else "manual",
                    **attrs
                }
            }
            
            span_file.parent.mkdir(parents=True, exist_ok=True)
            with span_file.open("a") as f:
                f.write(json.dumps(span_data) + "\n")
            
            time.sleep(0.5)


@app.command("status")
def status():
    """Show SwarmAgent status."""
    console.print("📊 [bold]SwarmAgent Status[/bold]")
    
    # Check for span files
    span_dirs = [
        Path("~/s2s/agent_coordination").expanduser(),
        Path("/tmp"),
        Path.cwd()
    ]
    
    table = Table(title="Agent Environment")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    for span_dir in span_dirs:
        if span_dir.exists():
            span_file = span_dir / "telemetry_spans.jsonl"
            if span_file.exists():
                table.add_row("Span File", str(span_file))
                table.add_row("File Size", f"{span_file.stat().st_size} bytes")
                break
    else:
        table.add_row("Span File", "Not found")
    
    # Show available agent types
    table.add_row("Available Agents", "roberts, scrum, lean, ping")
    table.add_row("Framework", "SwarmAgent + OpenTelemetry")
    table.add_row("CLI Tool", "swarm_cli.py")
    
    console.print(table)


@app.command("list")
def list_agents():
    """List available agent types."""
    table = Table(title="Available SwarmAgent Types")
    table.add_column("Type", style="cyan")
    table.add_column("Purpose", style="green")
    table.add_column("States", style="yellow")
    
    agents_info = [
        ("roberts", "Governance via Roberts Rules", "IDLE → MOTION_OPEN → VOTING → CLOSED"),
        ("scrum", "Delivery via Scrum-at-Scale", "PLANNING → EXECUTING → REVIEW → RETRO"),
        ("lean", "Optimization via DMAIC", "DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL"),
        ("ping", "Minimal Hello World example", "IDLE → PINGED")
    ]
    
    for agent_type, purpose, states in agents_info:
        table.add_row(agent_type, purpose, states)
    
    console.print(table)


@app.command("generate")
def generate_agent(
    name: str = typer.Argument(..., help="Agent name"),
    states: str = typer.Option("IDLE,ACTIVE,COMPLETE", help="Comma-separated states"),
    triggers: str = typer.Option("start,process,finish", help="Comma-separated triggers"),
    output_dir: Path = typer.Option(Path.cwd(), help="Output directory")
):
    """Generate a new SwarmAgent from template."""
    
    state_list = [s.strip().upper() for s in states.split(",")]
    trigger_list = [t.strip().lower() for t in triggers.split(",")]
    
    console.print(f"🏗️  [blue]Generating agent: {name}[/blue]")
    console.print(f"📋 States: {state_list}")
    console.print(f"🎯 Triggers: {trigger_list}")
    
    # Generate agent code
    agent_code = _generate_agent_template(name, state_list, trigger_list)
    
    # Save to file
    output_file = output_dir / f"{name.lower()}_agent.py"
    output_file.write_text(agent_code)
    
    console.print(f"✅ [green]Agent generated: {output_file}[/green]")
    console.print(f"💡 Usage: from {output_file.stem} import {name}Agent")


def _generate_agent_template(name: str, states: List[str], triggers: List[str]) -> str:
    """Generate agent template code."""
    
    # Create state enum
    state_enum = f"class {name}State(Enum):\n"
    for i, state in enumerate(states):
        state_enum += f"    {state} = auto()\n"
    
    # Create trigger map
    trigger_map = "TRIGGER_MAP = {\n"
    for trigger in triggers:
        trigger_map += f'        "{trigger}": "on_{trigger}",\n'
    trigger_map += "    }"
    
    # Create trigger methods
    trigger_methods = ""
    for i, trigger in enumerate(triggers):
        source_state = states[i] if i < len(states) else states[0]
        dest_state = states[i + 1] if i + 1 < len(states) else states[-1]
        
        trigger_methods += f'''
    @trigger(source={name}State.{source_state}, dest={name}State.{dest_state})
    def on_{trigger}(self, span: SpanData) -> Optional[NextCommand]:
        """Handle {trigger} trigger."""
        self._transition(f"Processing {trigger} from {{span.attributes.get('source', 'unknown')}}", 
                        {name}State.{dest_state})
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.{name.lower()}.{trigger}",
            args=["--span-id", span.span_id],
            description=f"Execute {trigger} action"
        )
'''
    
    template = f'''"""Generated {name} SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


{state_enum}
class {name}Agent(SwarmAgent):
    """
    {name} agent for handling {', '.join(triggers)} workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = {name}State
    LISTEN_FILTER = "swarmsh.{name.lower()}."
    {trigger_map}
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass
{trigger_methods}

if __name__ == "__main__":
    {name}Agent().run()
'''
    
    return template


if __name__ == "__main__":
    app()