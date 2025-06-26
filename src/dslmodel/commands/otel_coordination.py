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
from .coordination_cli import (
    log_span as basic_log_span, 
    load_work_items, 
    save_work_items,
    WorkType, 
    Priority,
    ROOT,
    WORK_ITEMS
)

# OpenTelemetry imports (with fallbacks for when not installed)
try:
    from opentelemetry import trace, metrics, baggage, context
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.semconv.trace import SpanAttributes
    from opentelemetry.propagate import inject, extract
    
    # Optional OTLP exporters
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        OTLP_AVAILABLE = True
    except ImportError:
        OTLP_AVAILABLE = False
    
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Mock classes for when OTEL is not available
    class MockTracer:
        @contextmanager
        def start_as_current_span(self, name, **kwargs):
            yield MockSpan()
    
    class MockSpan:
        def set_attribute(self, key, value): pass
        def set_attributes(self, attrs): pass
        def set_status(self, status): pass
        def record_exception(self, exception): pass
        def get_span_context(self): return MockSpanContext()
    
    class MockSpanContext:
        def __init__(self):
            self.trace_id = 123456789
            self.span_id = 987654321
    
    class MockMeter:
        def create_counter(self, *args, **kwargs): return MockCounter()
        def create_histogram(self, *args, **kwargs): return MockHistogram()
        def create_observable_gauge(self, *args, **kwargs): return MockGauge()
    
    class MockCounter:
        def add(self, value, attributes=None): pass
    
    class MockHistogram:
        def record(self, value, attributes=None): pass
    
    class MockGauge:
        def add_callback(self, callback): pass


###############################################################################
# OTEL Setup (only if available)
###############################################################################

def setup_otel(service_name: str = "dslmodel-coordination"):
    """Setup OpenTelemetry with fallback to console exporters"""
    if not OTEL_AVAILABLE:
        return MockTracer(), MockMeter()
    
    # Resource attributes
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.SERVICE_NAMESPACE: "dslmodel",
        "team.name": "platform"
    })
    
    # Setup trace provider
    trace_provider = TracerProvider(resource=resource)
    
    # Use OTLP if available, otherwise console
    if OTLP_AVAILABLE and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        trace_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            insecure=True
        )
    else:
        trace_exporter = ConsoleSpanExporter()
    
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)
    tracer = trace.get_tracer(service_name, "1.0.0")
    
    # Setup metrics provider
    if OTLP_AVAILABLE and os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        metric_exporter = OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            insecure=True
        )
    else:
        metric_exporter = ConsoleMetricExporter()
    
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=30000  # 30 seconds
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(service_name, "1.0.0")
    
    return tracer, meter


# Initialize OTEL
tracer, meter = setup_otel()

###############################################################################
# Enhanced Coordination Attributes
###############################################################################

class CoordinationAttributes:
    """Semantic conventions for coordination operations"""
    WORK_ID = "coordination.work.id"
    WORK_TYPE = "coordination.work.type"
    WORK_PRIORITY = "coordination.work.priority"
    WORK_TEAM = "coordination.work.team"
    WORK_STATUS = "coordination.work.status"
    WORK_PROGRESS = "coordination.work.progress"
    WORK_SCORE = "coordination.work.score"
    OPERATION_TYPE = "coordination.operation.type"

###############################################################################
# Enhanced CLI App
###############################################################################

app = typer.Typer(help="OTEL-enhanced coordination system")
work_app = typer.Typer(help="Work item management with telemetry")
otel_app = typer.Typer(help="OpenTelemetry operations")

app.add_typer(work_app, name="work")
app.add_typer(otel_app, name="otel")

# Metrics
work_items_created = meter.create_counter(
    name="dslmodel.coordination.work_items.created",
    description="Number of work items created",
    unit="1"
)

work_items_completed = meter.create_counter(
    name="dslmodel.coordination.work_items.completed",
    description="Number of work items completed", 
    unit="1"
)

work_item_duration = meter.create_histogram(
    name="dslmodel.coordination.work_item.duration",
    description="Duration of work items",
    unit="s"
)

api_latency = meter.create_histogram(
    name="dslmodel.coordination.api.latency",
    description="API operation latency",
    unit="ms"
)

###############################################################################
# Enhanced Context Manager
###############################################################################

@contextmanager
def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Enhanced tracing with metrics and context propagation"""
    with tracer.start_as_current_span(f"dslmodel.coordination.{name}") as span:
        if attributes:
            span.set_attributes(attributes)
        
        # Add standard attributes
        span.set_attribute(SpanAttributes.CODE_FUNCTION, name)
        span.set_attribute("service.component", "coordination")
        
        # Set baggage for downstream services
        if attributes:
            for key, value in attributes.items():
                if isinstance(value, str):
                    baggage.set_baggage(key.replace(".", "_"), value)
        
        start_time = time.time()
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        finally:
            duration = time.time() - start_time
            span.set_attribute("operation.duration_ms", duration * 1000)
            
            # Record API latency
            api_latency.record(duration * 1000, {"operation": name})

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
            "trace_id": format(span.get_span_context().trace_id, "032x"),
            "span_id": format(span.get_span_context().span_id, "016x")
        }
        
        # Save work item
        data["items"][work_id] = work_item
        save_work_items(data)
        
        # Record metrics
        work_items_created.add(1, {
            "work.type": work_type.value,
            "work.priority": priority.value,
            "work.team": team
        })
        
        # Enhanced logging with correlation
        span.set_attribute(CoordinationAttributes.WORK_ID, work_id)
        span.set_attribute("work.created", True)
        
        # Also log to existing span stream for backward compatibility
        basic_log_span("work.claim", {
            "work_id": work_id,
            "type": work_type.value,
            "priority": priority.value,
            "team": team,
            "trace_id": work_item["trace_id"]
        })
        
        typer.echo(f"✅ Claimed {work_id}: {title}")
        if OTEL_AVAILABLE:
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
            span.set_status(Status(StatusCode.ERROR, f"Work item {work_id} not found"))
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
        work_items_completed.add(1, {
            "work.type": work_item.get("type", "unknown"),
            "work.priority": work_item.get("priority", "medium"),
            "work.team": work_item.get("team", "default"),
            "completion.status": status
        })
        
        if duration_seconds:
            work_item_duration.record(duration_seconds, {
                "work.type": work_item.get("type", "unknown"),
                "work.priority": work_item.get("priority", "medium")
            })
            span.set_attribute("work.duration_seconds", duration_seconds)
        
        # Link to original creation trace if available
        if "trace_id" in work_item:
            span.set_attribute("work.original_trace_id", work_item["trace_id"])
        
        span.set_attributes({
            CoordinationAttributes.WORK_TYPE: work_item.get("type", "unknown"),
            CoordinationAttributes.WORK_PRIORITY: work_item.get("priority", "medium"),
            CoordinationAttributes.WORK_TEAM: work_item.get("team", "default"),
            "work.completed": True
        })
        
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
    typer.echo(f"  OTLP Available: {'✅' if OTLP_AVAILABLE else '❌'}")
    
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    typer.echo(f"  OTLP Endpoint: {endpoint or 'Not configured'}")
    
    service_name = os.getenv("OTEL_SERVICE_NAME", "dslmodel-coordination")
    typer.echo(f"  Service Name: {service_name}")
    
    if not OTEL_AVAILABLE:
        typer.echo("\n💡 To enable full OTEL support:")
        typer.echo("   pip install opentelemetry-api opentelemetry-sdk")
        typer.echo("   pip install opentelemetry-exporter-otlp")

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
        
        trace_id = format(span.get_span_context().trace_id, "032x")
        span_id = format(span.get_span_context().span_id, "016x")
        
        typer.echo(f"✅ Test trace generated")
        typer.echo(f"   Trace ID: {trace_id}")
        typer.echo(f"   Span ID: {span_id}")

@otel_app.command("export-spans")
def export_spans(limit: int = 10):
    """Export recent spans from the telemetry stream."""
    span_file = ROOT / "telemetry_spans.jsonl"
    
    if not span_file.exists():
        typer.echo("No span file found. Create some work items first.")
        return
    
    typer.echo(f"📊 Last {limit} spans:")
    typer.echo("-" * 80)
    
    with span_file.open() as f:
        lines = f.readlines()
        for line in lines[-limit:]:
            try:
                span_data = json.loads(line)
                timestamp = datetime.datetime.fromtimestamp(span_data["timestamp"]).strftime("%H:%M:%S")
                typer.echo(f"{timestamp} | {span_data['name']} | {span_data.get('attributes', {})}")
            except json.JSONDecodeError:
                continue

###############################################################################
# Integration with existing CLI
###############################################################################

# Re-export existing commands for compatibility
from .coordination_cli import (
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

if __name__ == "__main__":
    app()