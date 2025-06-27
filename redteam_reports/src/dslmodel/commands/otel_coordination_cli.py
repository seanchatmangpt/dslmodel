"""OpenTelemetry-enabled coordination CLI for swarm agents."""

import typer
import json
import time
import os
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum
from contextlib import contextmanager

from opentelemetry import trace, metrics, baggage, context
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.propagate import extract, inject

from dslmodel.otel.otel_instrumentation import (
    OTelInstrumentation,
    SwarmSpanAttributes,
    init_otel,
    get_otel
)

# Initialize CLI apps
app = typer.Typer(help="OTel-enabled agent coordination system")
work_app = typer.Typer(help="Work item management with distributed tracing")
agent_app = typer.Typer(help="Run OTel-instrumented agents")

# Add sub-apps
app.add_typer(work_app, name="work")
app.add_typer(agent_app, name="agent")

# Configuration
ROOT = Path("~/s2s/agent_coordination").expanduser()
WORK_ITEMS = ROOT / "work_items.json"

# Work item types
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


# Initialize OTel for CLI
_otel: Optional[OTelInstrumentation] = None


def get_cli_otel() -> OTelInstrumentation:
    """Get or initialize OTel for CLI."""
    global _otel
    if _otel is None:
        _otel = init_otel(
            service_name="coordination-cli",
            service_version="1.0.0",
            otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
        )
    return _otel


@contextmanager
def trace_cli_operation(operation: str, attributes: Dict[str, Any] = None):
    """Context manager for tracing CLI operations."""
    otel = get_cli_otel()
    
    # Extract parent context from environment (if running as subprocess)
    carrier = {k: v for k, v in os.environ.items() if k.startswith("traceparent") or k.startswith("tracestate")}
    if carrier:
        parent_ctx = extract(carrier)
        context.attach(parent_ctx)
    
    with otel.trace_span(
        name=f"cli.{operation}",
        kind=SpanKind.CLIENT,
        attributes=attributes or {}
    ) as span:
        yield span


def load_work_items() -> Dict:
    """Load work items from JSON file."""
    if not WORK_ITEMS.exists():
        return {"items": {}, "next_id": 1}
    
    with WORK_ITEMS.open() as f:
        return json.load(f)


def save_work_items(data: Dict):
    """Save work items to JSON file."""
    ROOT.mkdir(parents=True, exist_ok=True)
    with WORK_ITEMS.open("w") as f:
        json.dump(data, f, indent=2)


# Work Commands with OTel instrumentation
@work_app.command("claim")
def claim_work(
    work_type: WorkType,
    title: str,
    priority: Priority = Priority.MEDIUM,
    team: str = "default"
):
    """Claim a new work item with distributed tracing."""
    otel = get_cli_otel()
    
    with trace_cli_operation(
        "work.claim",
        attributes={
            SwarmSpanAttributes.WORK_TYPE: work_type.value,
            SwarmSpanAttributes.WORK_PRIORITY: priority.value,
            SwarmSpanAttributes.WORK_TEAM: team,
            "work.title": title
        }
    ) as span:
        # Load and update work items
        data = load_work_items()
        work_id = f"WORK-{data['next_id']}"
        data["next_id"] += 1
        
        work_item = {
            "id": work_id,
            "type": work_type.value,
            "title": title,
            "priority": priority.value,
            "team": team,
            "status": "claimed",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "trace_id": format(span.get_span_context().trace_id, '032x'),
            "span_id": format(span.get_span_context().span_id, '016x')
        }
        
        data["items"][work_id] = work_item
        save_work_items(data)
        
        # Set span attributes
        span.set_attribute(SwarmSpanAttributes.WORK_ID, work_id)
        span.set_attribute("work.created", True)
        
        # Set baggage for downstream propagation
        baggage.set_baggage("work.id", work_id)
        baggage.set_baggage("work.team", team)
        
        # Update metrics
        otel.work_items_gauge.add(
            1,
            attributes={
                "status": "claimed",
                "type": work_type.value,
                "team": team
            }
        )
        
        # Create event span for agents to consume
        with otel.trace_span(
            name="swarmsh.work.claim",
            kind=SpanKind.PRODUCER,
            attributes={
                SwarmSpanAttributes.WORK_ID: work_id,
                SwarmSpanAttributes.WORK_TYPE: work_type.value,
                SwarmSpanAttributes.WORK_PRIORITY: priority.value,
                SwarmSpanAttributes.WORK_TEAM: team,
                "event.type": "work.claimed"
            }
        ) as event_span:
            # This span will be consumed by agents
            event_span.add_event(
                name="work_claimed",
                attributes={
                    "work_id": work_id,
                    "title": title
                }
            )
        
        typer.echo(f"✅ Claimed {work_id}: {title}")
        typer.echo(f"   Trace ID: {work_item['trace_id']}")
        return work_id


@work_app.command("list")
def list_work(
    team: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "table"
):
    """List work items with tracing context."""
    with trace_cli_operation(
        "work.list",
        attributes={
            "filter.team": team or "all",
            "filter.status": status or "all",
            "format": format
        }
    ) as span:
        data = load_work_items()
        items = list(data.get("items", {}).values())
        
        # Filter items
        if team:
            items = [i for i in items if i.get("team") == team]
        if status:
            items = [i for i in items if i.get("status") == status]
        
        span.set_attribute("result.count", len(items))
        
        if format == "json":
            typer.echo(json.dumps(items, indent=2))
        else:
            if not items:
                typer.echo("No work items found.")
                return
            
            typer.echo("\nWork Items:")
            typer.echo("-" * 100)
            typer.echo(f"{'ID':^10} | {'Type':^8} | {'Priority':^8} | {'Status':^10} | {'Progress':^8} | Title")
            typer.echo("-" * 100)
            
            for item in items:
                typer.echo(
                    f"{item['id']:^10} | {item['type']:^8} | {item['priority']:^8} | "
                    f"{item['status']:^10} | {item['progress']:>3}% | {item['title']}"
                )
                
                # Show trace info if verbose
                if os.getenv("OTEL_VERBOSE"):
                    typer.echo(f"              Trace: {item.get('trace_id', 'N/A')}")
        
        # Emit list event
        with get_cli_otel().trace_span(
            name="swarmsh.work.list",
            kind=SpanKind.PRODUCER,
            attributes={
                "count": len(items),
                "filter.team": team,
                "filter.status": status
            }
        ):
            pass


@work_app.command("progress")
def update_progress(work_id: str, progress: int):
    """Update work item progress with tracing."""
    otel = get_cli_otel()
    
    with trace_cli_operation(
        "work.progress",
        attributes={
            SwarmSpanAttributes.WORK_ID: work_id,
            "progress.new": progress
        }
    ) as span:
        data = load_work_items()
        
        if work_id not in data["items"]:
            span.set_status(Status(StatusCode.ERROR, f"Work item {work_id} not found"))
            typer.echo(f"❌ Work item {work_id} not found.")
            raise typer.Exit(1)
        
        old_progress = data["items"][work_id]["progress"]
        data["items"][work_id]["progress"] = min(100, max(0, progress))
        data["items"][work_id]["status"] = "in_progress"
        data["items"][work_id]["updated_at"] = datetime.now().isoformat()
        
        save_work_items(data)
        
        span.set_attribute("progress.old", old_progress)
        span.set_attribute("progress.delta", progress - old_progress)
        
        # Emit progress event with parent trace context
        parent_trace_id = data["items"][work_id].get("trace_id")
        if parent_trace_id:
            # Create link to original work item trace
            link = otel.create_span_link(
                trace_id=parent_trace_id,
                span_id=data["items"][work_id].get("span_id", "0" * 16),
                attributes={"link.type": "work_item_origin"}
            )
            span.add_link(link)
        
        with otel.trace_span(
            name="swarmsh.work.progress",
            kind=SpanKind.PRODUCER,
            attributes={
                SwarmSpanAttributes.WORK_ID: work_id,
                "progress": progress,
                "progress.delta": progress - old_progress
            }
        ):
            pass
        
        typer.echo(f"📊 Updated {work_id} progress to {progress}%")


@work_app.command("complete")
def complete_work(work_id: str, status: str = "success", score: int = 5):
    """Mark work item as complete with full tracing."""
    otel = get_cli_otel()
    
    with trace_cli_operation(
        "work.complete",
        attributes={
            SwarmSpanAttributes.WORK_ID: work_id,
            "completion.status": status,
            "completion.score": score
        }
    ) as span:
        data = load_work_items()
        
        if work_id not in data["items"]:
            span.set_status(Status(StatusCode.ERROR, f"Work item {work_id} not found"))
            typer.echo(f"❌ Work item {work_id} not found.")
            raise typer.Exit(1)
        
        work_item = data["items"][work_id]
        old_status = work_item["status"]
        
        work_item["status"] = "completed"
        work_item["progress"] = 100
        work_item["completion_status"] = status
        work_item["score"] = score
        work_item["completed_at"] = datetime.now().isoformat()
        work_item["updated_at"] = datetime.now().isoformat()
        
        # Calculate duration
        created_at = datetime.fromisoformat(work_item["created_at"])
        completed_at = datetime.fromisoformat(work_item["completed_at"])
        duration_hours = (completed_at - created_at).total_seconds() / 3600
        work_item["duration_hours"] = duration_hours
        
        save_work_items(data)
        
        span.set_attribute("work.duration_hours", duration_hours)
        span.set_attribute("work.old_status", old_status)
        
        # Update metrics
        otel.work_items_gauge.add(
            -1,
            attributes={
                "status": old_status,
                "type": work_item["type"],
                "team": work_item["team"]
            }
        )
        
        otel.work_items_gauge.add(
            1,
            attributes={
                "status": "completed",
                "type": work_item["type"],
                "team": work_item["team"]
            }
        )
        
        # Emit completion event
        with otel.trace_span(
            name="swarmsh.work.complete",
            kind=SpanKind.PRODUCER,
            attributes={
                SwarmSpanAttributes.WORK_ID: work_id,
                "status": status,
                "score": score,
                "duration_hours": duration_hours
            }
        ):
            pass
        
        typer.echo(f"✅ Completed {work_id} with status: {status} (score: {score}/10)")
        typer.echo(f"   Duration: {duration_hours:.1f} hours")


# Agent commands
@agent_app.command("run")
def run_agent(
    agent_type: str,
    otlp_endpoint: Optional[str] = None,
    console_export: bool = False
):
    """Run an OTel-instrumented agent."""
    # Import agent classes
    from dslmodel.otel.otel_swarm_agent import OTelRobertsAgent
    
    # Agent registry (extend as needed)
    agents = {
        "roberts": OTelRobertsAgent,
        # Add more agents here
    }
    
    agent_class = agents.get(agent_type)
    if not agent_class:
        typer.echo(f"❌ Unknown agent type: {agent_type}")
        typer.echo(f"Available agents: {', '.join(agents.keys())}")
        raise typer.Exit(1)
    
    typer.echo(f"🚀 Starting {agent_type} agent with OTel instrumentation...")
    typer.echo(f"   OTLP Endpoint: {otlp_endpoint or 'localhost:4317'}")
    
    # Run agent
    import asyncio
    agent = agent_class(
        otlp_endpoint=otlp_endpoint,
        enable_console_export=console_export
    )
    
    try:
        asyncio.run(agent.arun())
    except KeyboardInterrupt:
        typer.echo(f"\n⏹️  {agent_type} agent stopped.")


@app.command("init")
def init_coordination():
    """Initialize the coordination environment with OTel."""
    with trace_cli_operation("init") as span:
        ROOT.mkdir(parents=True, exist_ok=True)
        
        if not WORK_ITEMS.exists():
            save_work_items({"items": {}, "next_id": 1})
            span.set_attribute("work_items.created", True)
        
        typer.echo(f"✅ Initialized OTel coordination environment at {ROOT}")
        
        # Test OTel connectivity
        otel = get_cli_otel()
        with otel.trace_span("test.connectivity") as test_span:
            test_span.add_event("init_complete")
        
        typer.echo("✅ OTel connectivity verified")


if __name__ == "__main__":
    app()