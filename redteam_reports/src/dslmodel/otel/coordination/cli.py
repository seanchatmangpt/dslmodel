"""
OpenTelemetry Enhanced Coordination CLI
Integrates OTEL observability with the existing DSLModel CLI structure
"""

import os
import json
import time
import datetime
import pathlib
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import typer
from enum import Enum

# Import existing coordination components
try:
    from dslmodel.commands.coordination_cli import (
        log_span as basic_log_span, 
        load_work_items, 
        save_work_items,
        WorkType, 
        Priority,
        ROOT,
        WORK_ITEMS
    )
except ImportError:
    # Fallback definitions if coordination_cli not available
    from pathlib import Path
    ROOT = Path("~/s2s/agent_coordination").expanduser()
    WORK_ITEMS = ROOT / "work_items.json"
    
    class WorkType(str, Enum):
        BUG = "bug"
        FEATURE = "feature"
        TASK = "task"
        EPIC = "epic"
    
    class Priority(str, Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    def load_work_items():
        if not WORK_ITEMS.exists():
            return {"items": {}, "next_id": 1}
        with WORK_ITEMS.open() as f:
            return json.load(f)
    
    def save_work_items(data):
        ROOT.mkdir(parents=True, exist_ok=True)
        with WORK_ITEMS.open("w") as f:
            json.dump(data, f, indent=2)
    
    def basic_log_span(name, attrs=None):
        pass

# Import OTEL setup utilities
from ..ecosystem.setup import setup_otel, OTEL_AVAILABLE
from ..semantic_conventions.coordination import CoordinationAttributes
from .instrumentation import trace_operation, CoordinationInstrumentation

# Initialize OTEL
tracer, meter = setup_otel()

###############################################################################
# Enhanced CLI App
###############################################################################

app = typer.Typer(help="OTEL-enhanced coordination system")
work_app = typer.Typer(help="Work item management with telemetry")
otel_app = typer.Typer(help="OpenTelemetry operations")

app.add_typer(work_app, name="work")
app.add_typer(otel_app, name="otel")

# Initialize instrumentation
instrumentation = CoordinationInstrumentation(tracer, meter)

###############################################################################
# Enhanced Work Commands
###############################################################################

@work_app.command("claim")
def claim_work_otel(
    work_type: WorkType,
    title: str,
    priority: Priority = Priority.MEDIUM,
    team: str = "default",
    story_points: int = typer.Option(3, help="Story points estimate")
):
    """Claim a work item with full OTEL instrumentation."""
    with trace_operation("work.claim", {
        CoordinationAttributes.WORK_TYPE: work_type.value,
        CoordinationAttributes.WORK_PRIORITY: priority.value,
        CoordinationAttributes.WORK_TEAM: team,
        "work.story_points": story_points
    }) as span:
        
        # Load work items
        data = load_work_items()
        work_id = f"WORK-{data['next_id']}"
        data["next_id"] += 1
        
        # Create work item with enhanced attributes
        work_item = {
            "id": work_id,
            "type": work_type.value,
            "title": title,
            "priority": priority.value,
            "team": team,
            "story_points": story_points,
            "status": "claimed",
            "progress": 0,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
        }
        
        if OTEL_AVAILABLE:
            work_item.update({
                "trace_id": format(span.get_span_context().trace_id, "032x"),
                "span_id": format(span.get_span_context().span_id, "016x")
            })
        
        # Save work item
        data["items"][work_id] = work_item
        save_work_items(data)
        
        # Record metrics
        instrumentation.record_work_created(work_type.value, priority.value, team)
        
        # Enhanced logging with correlation
        span.set_attribute(CoordinationAttributes.WORK_ID, work_id)
        span.set_attribute("work.created", True)
        
        # Also log to existing span stream for backward compatibility
        basic_log_span("work.claim", {
            "work_id": work_id,
            "type": work_type.value,
            "priority": priority.value,
            "team": team,
            "trace_id": work_item.get("trace_id", "")
        })
        
        typer.echo(f"✅ Claimed {work_id}: {title}")
        if OTEL_AVAILABLE and "trace_id" in work_item:
            typer.echo(f"🔍 Trace ID: {work_item['trace_id']}")
        
        return work_id

@work_app.command("complete")
def complete_work_otel(
    work_id: str, 
    status: str = "success", 
    score: int = typer.Option(5, min=1, max=10, help="Quality score 1-10")
):
    """Complete a work item with telemetry tracking."""
    with trace_operation("work.complete", {
        CoordinationAttributes.WORK_ID: work_id,
        "completion.status": status,
        CoordinationAttributes.WORK_SCORE: score
    }) as span:
        
        # Load work items
        data = load_work_items()
        
        if work_id not in data["items"]:
            span.set_status_error(f"Work item {work_id} not found")
            typer.echo(f"❌ Work item {work_id} not found.")
            raise typer.Exit(1)
        
        work_item = data["items"][work_id]
        
        # Calculate duration if work was created with trace
        duration_seconds = None
        if "created_at" in work_item:
            created_at = datetime.datetime.fromisoformat(work_item["created_at"])
            completed_at = datetime.datetime.now()
            duration_seconds = (completed_at - created_at).total_seconds()
        
        # Update work item
        work_item.update({
            "status": "completed",
            "progress": 100,
            "completion_status": status,
            "score": score,
            "completed_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        })
        
        if duration_seconds:
            work_item["duration_seconds"] = duration_seconds
        
        save_work_items(data)
        
        # Record metrics
        instrumentation.record_work_completed(
            work_item.get("type", "unknown"),
            work_item.get("priority", "medium"),
            work_item.get("team", "default"),
            status,
            duration_seconds
        )
        
        # Link to original creation trace if available
        if "trace_id" in work_item:
            span.set_attribute("work.original_trace_id", work_item["trace_id"])
        
        span.set_attributes({
            CoordinationAttributes.WORK_TYPE: work_item.get("type", "unknown"),
            CoordinationAttributes.WORK_PRIORITY: work_item.get("priority", "medium"),
            CoordinationAttributes.WORK_TEAM: work_item.get("team", "default"),
            "work.completed": True
        })
        
        if duration_seconds:
            span.set_attribute("work.duration_seconds", duration_seconds)
        
        # Backward compatibility logging
        basic_log_span("work.complete", {
            "work_id": work_id,
            "status": status,
            "score": score,
            "duration_seconds": duration_seconds
        })
        
        typer.echo(f"✅ Completed {work_id} with status: {status} (score: {score}/10)")
        if duration_seconds:
            typer.echo(f"⏱️  Duration: {duration_seconds:.1f} seconds")

@work_app.command("list")
def list_work_otel(
    team: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "table",
    show_traces: bool = typer.Option(False, help="Show trace IDs")
):
    """List work items with optional trace information."""
    with trace_operation("work.list", {
        "filter.team": team or "all",
        "filter.status": status or "all",
        "output.format": format
    }) as span:
        
        data = load_work_items()
        items = list(data.get("items", {}).values())
        
        # Apply filters
        if team:
            items = [i for i in items if i.get("team") == team]
        if status:
            items = [i for i in items if i.get("status") == status]
        
        span.set_attribute("work.items.count", len(items))
        
        if format == "json":
            typer.echo(json.dumps(items, indent=2))
        else:
            if not items:
                typer.echo("No work items found.")
                return
            
            typer.echo("\nWork Items:")
            header = "ID | Type | Priority | Status | Progress | Team"
            if show_traces:
                header += " | Trace ID"
            header += " | Title"
            
            typer.echo("-" * 100)
            typer.echo(header)
            typer.echo("-" * 100)
            
            for item in items:
                line = (f"{item['id']:10} | {item.get('type', 'N/A'):8} | "
                       f"{item.get('priority', 'N/A'):8} | {item.get('status', 'N/A'):10} | "
                       f"{item.get('progress', 0):3}% | {item.get('team', 'N/A'):10}")
                
                if show_traces and "trace_id" in item:
                    line += f" | {item['trace_id'][:16]}..."
                elif show_traces:
                    line += " | No trace"
                
                line += f" | {item.get('title', 'N/A')}"
                typer.echo(line)
        
        # Log telemetry
        basic_log_span("work.list", {
            "count": len(items), 
            "team": team, 
            "status": status,
            "show_traces": show_traces
        })

###############################################################################
# OTEL Operations
###############################################################################

@otel_app.command("status")
def otel_status():
    """Show OpenTelemetry configuration status."""
    typer.echo("🔍 OpenTelemetry Status:")
    typer.echo(f"  OTEL Available: {'✅' if OTEL_AVAILABLE else '❌'}")
    
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    typer.echo(f"  OTLP Endpoint: {endpoint or 'Not configured'}")
    
    service_name = os.getenv("OTEL_SERVICE_NAME", "dslmodel-coordination")
    typer.echo(f"  Service Name: {service_name}")
    
    if not OTEL_AVAILABLE:
        typer.echo("\n💡 To enable full OTEL support:")
        typer.echo("   pip install dslmodel[otel]")

@otel_app.command("test-trace")
def test_trace():
    """Generate a test trace for verification."""
    with trace_operation("test.trace", {
        "test.type": "verification",
        "test.timestamp": datetime.datetime.now().isoformat()
    }) as span:
        typer.echo("🧪 Generating test trace...")
        
        # Simulate some work
        time.sleep(0.1)
        
        span.set_attribute("test.completed", True)
        span.set_attribute("test.result", "success")
        
        if OTEL_AVAILABLE:
            trace_id = format(span.get_span_context().trace_id, "032x")
            span_id = format(span.get_span_context().span_id, "016x")
            
            typer.echo(f"✅ Test trace generated")
            typer.echo(f"   Trace ID: {trace_id}")
            typer.echo(f"   Span ID: {span_id}")
        else:
            typer.echo(f"✅ Test trace generated (mock mode)")

# Re-export existing commands for compatibility
try:
    from dslmodel.commands.coordination_cli import (
        init_coordination,
        reset_coordination,
        work_stats,
        update_progress,
        list_agents,
        run_agent
    )
    
    # Add existing commands to our app
    app.command("init")(init_coordination)
    app.command("reset")(reset_coordination)
    work_app.command("stats")(work_stats)
    work_app.command("progress")(update_progress)
    
    # Add agent commands
    agent_app = typer.Typer(help="Agent management")
    app.add_typer(agent_app, name="agent")
    agent_app.command("list")(list_agents)
    agent_app.command("run")(run_agent)
    
except ImportError:
    # Basic commands if coordination_cli not available
    @app.command("init")
    def init_coordination():
        """Initialize the coordination environment."""
        ROOT.mkdir(parents=True, exist_ok=True)
        typer.echo(f"✅ Initialized coordination environment at {ROOT}")

if __name__ == "__main__":
    app()