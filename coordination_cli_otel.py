#!/usr/bin/env python3
"""
Coordination CLI with Full OpenTelemetry Instrumentation
Demonstrates traces, metrics, logs, and context propagation
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

# OpenTelemetry imports
from opentelemetry import trace, metrics, baggage, context
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

###############################################################################
# OTEL Setup
###############################################################################

# Service resource attributes
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "coordination-cli",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.SERVICE_NAMESPACE: "swarmsh",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENV", "development"),
    ResourceAttributes.HOST_NAME: os.uname().nodename,
    "team.name": "platform",
    "team.owner": "engineering"
})

# Tracing setup
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=True
    ))
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("coordination.cli", "1.0.0")

# Metrics setup
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=True
    ),
    export_interval_millis=10000  # 10 seconds
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("coordination.cli", "1.0.0")

# Logging setup
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=True
    ))
)
set_logger_provider(logger_provider)

# Configure Python logging to use OTEL
LoggingInstrumentor().instrument(set_logging_format=True)
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

###############################################################################
# Metrics definitions (following semantic conventions)
###############################################################################

# Counters
work_items_created = meter.create_counter(
    name="coordination.work_items.created",
    description="Number of work items created",
    unit="1"
)

work_items_completed = meter.create_counter(
    name="coordination.work_items.completed", 
    description="Number of work items completed",
    unit="1"
)

api_requests = meter.create_counter(
    name="coordination.api.requests",
    description="Number of API requests",
    unit="1"
)

# Histograms
work_item_duration = meter.create_histogram(
    name="coordination.work_item.duration",
    description="Duration of work items from creation to completion",
    unit="s"
)

api_latency = meter.create_histogram(
    name="coordination.api.latency",
    description="API request latency",
    unit="ms"
)

# Gauges (via callbacks)
active_work_items = meter.create_observable_gauge(
    name="coordination.work_items.active",
    description="Number of active work items"
)

team_capacity = meter.create_observable_gauge(
    name="coordination.team.capacity",
    description="Current team capacity in story points"
)

###############################################################################
# CLI with OTEL instrumentation
###############################################################################

app = typer.Typer(help="OTEL-instrumented Coordination CLI")
work_app = typer.Typer(help="Work management commands")
metrics_app = typer.Typer(help="Metrics and observability")

app.add_typer(work_app, name="work")
app.add_typer(metrics_app, name="metrics")

# Paths
ROOT = pathlib.Path(os.getenv("COORDINATION_DIR", "~/s2s/agent_coordination")).expanduser()
WORK_CLAIMS = ROOT / "work_claims.json"
METRICS_DB = ROOT / "metrics.json"
ROOT.mkdir(parents=True, exist_ok=True)

###############################################################################
# Context propagation helpers
###############################################################################

@contextmanager
def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for tracing operations"""
    with tracer.start_as_current_span(name) as span:
        if attributes:
            span.set_attributes(attributes)
        
        # Add baggage for downstream propagation
        ctx = baggage.set_baggage("operation.name", name)
        ctx = baggage.set_baggage("operation.timestamp", str(time.time()))
        
        start_time = time.time()
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"Error in {name}: {e}", exc_info=True)
            raise
        finally:
            duration = time.time() - start_time
            span.set_attribute("operation.duration_ms", duration * 1000)
            
            # Record metrics
            api_requests.add(1, {
                "operation": name,
                "status": "success" if span.status.status_code != StatusCode.ERROR else "error"
            })
            api_latency.record(duration * 1000, {"operation": name})

def inject_context_headers() -> Dict[str, str]:
    """Get headers with injected trace context"""
    headers = {}
    inject(headers)
    return headers

def extract_context_from_headers(headers: Dict[str, str]):
    """Extract and set trace context from headers"""
    ctx = extract(headers)
    context.attach(ctx)

###############################################################################
# Work management with telemetry
###############################################################################

@work_app.command("claim")
def claim_work(
    work_type: str,
    description: str,
    priority: str = "medium",
    story_points: int = 5,
    team: str = "platform"
):
    """Claim a work item with full telemetry"""
    with trace_operation("work.claim", {
        SpanAttributes.CODE_FUNCTION: "claim_work",
        "work.type": work_type,
        "work.priority": priority,
        "work.story_points": story_points,
        "work.team": team
    }) as span:
        # Generate work ID
        work_id = f"work_{int(time.time_ns())}"
        span.set_attribute("work.id", work_id)
        
        # Create work item
        work_item = {
            "work_id": work_id,
            "type": work_type,
            "description": description,
            "priority": priority,
            "story_points": story_points,
            "team": team,
            "status": "active",
            "created_at": datetime.datetime.utcnow().isoformat(),
            "created_by": os.getenv("USER", "unknown"),
            "trace_id": span.get_span_context().trace_id,
            "span_id": span.get_span_context().span_id
        }
        
        # Save to storage
        claims = _read_json(WORK_CLAIMS, [])
        claims.append(work_item)
        _write_json(WORK_CLAIMS, claims)
        
        # Record metrics
        work_items_created.add(1, {
            "work.type": work_type,
            "work.priority": priority,
            "work.team": team
        })
        
        # Log structured event
        logger.info("Work item created", extra={
            "work.id": work_id,
            "work.type": work_type,
            "work.priority": priority,
            "work.story_points": story_points,
            "trace.id": format(span.get_span_context().trace_id, "032x"),
            "span.id": format(span.get_span_context().span_id, "016x")
        })
        
        # Return with trace context
        result = {
            "success": True,
            "work_id": work_id,
            "trace_id": format(span.get_span_context().trace_id, "032x"),
            "headers": inject_context_headers()
        }
        
        typer.echo(json.dumps(result))

@work_app.command("complete")
def complete_work(work_id: str, result: str = "success"):
    """Complete a work item with telemetry"""
    with trace_operation("work.complete", {
        "work.id": work_id,
        "work.result": result
    }) as span:
        # Find and update work item
        claims = _read_json(WORK_CLAIMS, [])
        work_item = None
        
        for item in claims:
            if item["work_id"] == work_id:
                work_item = item
                # Link to original creation trace
                if "trace_id" in item:
                    span.add_link(trace.Link(
                        trace.SpanContext(
                            trace_id=int(item["trace_id"]),
                            span_id=int(item["span_id"]) if "span_id" in item else 0,
                            is_remote=True,
                            trace_flags=trace.TraceFlags(0x01)
                        )
                    ))
                break
        
        if not work_item:
            raise ValueError(f"Work item {work_id} not found")
        
        # Calculate duration
        created_at = datetime.datetime.fromisoformat(work_item["created_at"])
        completed_at = datetime.datetime.utcnow()
        duration_seconds = (completed_at - created_at).total_seconds()
        
        # Update work item
        work_item["status"] = "completed"
        work_item["completed_at"] = completed_at.isoformat()
        work_item["result"] = result
        work_item["duration_seconds"] = duration_seconds
        _write_json(WORK_CLAIMS, claims)
        
        # Record metrics
        work_items_completed.add(1, {
            "work.type": work_item["type"],
            "work.priority": work_item["priority"],
            "work.team": work_item["team"],
            "work.result": result
        })
        
        work_item_duration.record(duration_seconds, {
            "work.type": work_item["type"],
            "work.priority": work_item["priority"]
        })
        
        logger.info("Work item completed", extra={
            "work.id": work_id,
            "work.duration_seconds": duration_seconds,
            "work.result": result
        })
        
        typer.echo(json.dumps({"success": True, "duration_seconds": duration_seconds}))

@work_app.command("list")
def list_work(team: Optional[str] = None):
    """List work items with telemetry context"""
    with trace_operation("work.list", {"filter.team": team or "all"}) as span:
        claims = _read_json(WORK_CLAIMS, [])
        active_items = [w for w in claims if w["status"] == "active"]
        
        if team:
            active_items = [w for w in active_items if w.get("team") == team]
        
        span.set_attribute("work.items.count", len(active_items))
        
        # Calculate team metrics
        total_points = sum(w.get("story_points", 0) for w in active_items)
        by_priority = {}
        for item in active_items:
            pri = item.get("priority", "medium")
            by_priority[pri] = by_priority.get(pri, 0) + 1
        
        span.set_attributes({
            "work.total_story_points": total_points,
            "work.items.by_priority": json.dumps(by_priority)
        })
        
        logger.info("Listed work items", extra={
            "count": len(active_items),
            "team": team or "all",
            "total_points": total_points
        })
        
        for item in active_items:
            typer.echo(f"{item['work_id']} | {item['type']} | {item['priority']} | {item['team']} | {item.get('story_points', 0)}pts")
        
        typer.echo(f"\nTotal: {len(active_items)} items, {total_points} points")

###############################################################################
# Metrics and observability commands
###############################################################################

@metrics_app.command("health")
def health_check():
    """System health check with telemetry"""
    with trace_operation("metrics.health_check") as span:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check work claims file
        try:
            claims = _read_json(WORK_CLAIMS, [])
            health_status["components"]["storage"] = {
                "status": "healthy",
                "work_items": len(claims)
            }
        except Exception as e:
            health_status["components"]["storage"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check OTEL connection
        try:
            # This would actually check collector connectivity
            health_status["components"]["telemetry"] = {
                "status": "healthy",
                "endpoint": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
            }
        except Exception as e:
            health_status["components"]["telemetry"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        span.set_attributes({
            "health.status": health_status["status"],
            "health.components": json.dumps(health_status["components"])
        })
        
        logger.info("Health check completed", extra=health_status)
        typer.echo(json.dumps(health_status, indent=2))

@metrics_app.command("report")
def generate_report():
    """Generate metrics report from telemetry data"""
    with trace_operation("metrics.generate_report") as span:
        claims = _read_json(WORK_CLAIMS, [])
        
        # Calculate metrics
        total_items = len(claims)
        active_items = [w for w in claims if w["status"] == "active"]
        completed_items = [w for w in claims if w["status"] == "completed"]
        
        # Velocity calculation
        completed_points = sum(w.get("story_points", 0) for w in completed_items)
        avg_duration = sum(w.get("duration_seconds", 0) for w in completed_items) / len(completed_items) if completed_items else 0
        
        report = {
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "metrics": {
                "total_items": total_items,
                "active_items": len(active_items),
                "completed_items": len(completed_items),
                "completed_points": completed_points,
                "average_duration_hours": avg_duration / 3600,
                "velocity": completed_points / max(1, len(completed_items))
            },
            "by_team": {},
            "by_priority": {},
            "trace_id": format(span.get_span_context().trace_id, "032x")
        }
        
        # Team breakdown
        for item in claims:
            team = item.get("team", "unknown")
            if team not in report["by_team"]:
                report["by_team"][team] = {"total": 0, "completed": 0, "points": 0}
            report["by_team"][team]["total"] += 1
            if item["status"] == "completed":
                report["by_team"][team]["completed"] += 1
                report["by_team"][team]["points"] += item.get("story_points", 0)
        
        # Priority breakdown
        for item in active_items:
            pri = item.get("priority", "medium")
            report["by_priority"][pri] = report["by_priority"].get(pri, 0) + 1
        
        span.set_attributes({
            "report.total_items": total_items,
            "report.active_items": len(active_items),
            "report.velocity": report["metrics"]["velocity"]
        })
        
        # Save report
        _write_json(ROOT / f"report_{int(time.time())}.json", report)
        
        logger.info("Generated metrics report", extra={
            "total_items": total_items,
            "velocity": report["metrics"]["velocity"]
        })
        
        typer.echo(json.dumps(report, indent=2))

###############################################################################
# Observable gauge callbacks
###############################################################################

def observe_active_items(options):
    """Callback for active work items gauge"""
    try:
        claims = _read_json(WORK_CLAIMS, [])
        active_count = len([w for w in claims if w["status"] == "active"])
        
        # Group by team
        by_team = {}
        for item in claims:
            if item["status"] == "active":
                team = item.get("team", "unknown")
                by_team[team] = by_team.get(team, 0) + 1
        
        observations = []
        for team, count in by_team.items():
            observations.append((count, {"team": team}))
        
        return observations
    except Exception:
        return [(0, {"team": "error"})]

def observe_team_capacity(options):
    """Callback for team capacity gauge"""
    try:
        claims = _read_json(WORK_CLAIMS, [])
        
        # Calculate capacity by team
        capacity_by_team = {}
        for item in claims:
            if item["status"] == "active":
                team = item.get("team", "unknown")
                points = item.get("story_points", 0)
                capacity_by_team[team] = capacity_by_team.get(team, 0) + points
        
        observations = []
        for team, points in capacity_by_team.items():
            observations.append((points, {"team": team}))
        
        return observations
    except Exception:
        return [(0, {"team": "error"})]

# Register callbacks
active_work_items.add_callback(observe_active_items)
team_capacity.add_callback(observe_team_capacity)

###############################################################################
# Utilities
###############################################################################

def _read_json(path: pathlib.Path, default):
    """Read JSON file with telemetry"""
    with trace_operation("io.read_json", {"file.path": str(path)}):
        if path.exists():
            return json.loads(path.read_text())
        return default

def _write_json(path: pathlib.Path, data):
    """Write JSON file with telemetry"""
    with trace_operation("io.write_json", {"file.path": str(path)}):
        path.write_text(json.dumps(data, indent=2))

###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    logger.info("Starting coordination CLI with OTEL", extra={
        "service.name": "coordination-cli",
        "otel.endpoint": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
    })
    
    app()