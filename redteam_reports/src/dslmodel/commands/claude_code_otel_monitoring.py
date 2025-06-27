#!/usr/bin/env python3
"""
Claude Code OTEL Monitoring & Gap Detection
===========================================

80/20 approach: Instrument the critical 20% of operations that provide 
80% of the observability value for Claude Code health monitoring.

Key instrumentation areas:
1. CLI command execution spans
2. Validation pipeline performance
3. Multi-layer validation telemetry
4. Feedback application tracking
5. Real-time health monitoring
"""

import asyncio
import json
import time
import functools
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager, contextmanager
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from loguru import logger

# Optional OpenTelemetry imports - graceful fallback if not available
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    OTEL_DEPS_AVAILABLE = True
    
    # Optional advanced exporters
    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        JAEGER_AVAILABLE = True
    except ImportError:
        JAEGER_AVAILABLE = False
        
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        INSTRUMENTATION_AVAILABLE = True
    except ImportError:
        INSTRUMENTATION_AVAILABLE = False
        
except ImportError:
    OTEL_DEPS_AVAILABLE = False
    JAEGER_AVAILABLE = False
    INSTRUMENTATION_AVAILABLE = False
    
    # Mock trace module for fallback
    class MockTracer:
        def start_as_current_span(self, name, **kwargs):
            return MockSpan()
    
    class MockSpan:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def set_attribute(self, *args): pass
        def get_span_context(self): return MockSpanContext()
    
    class MockSpanContext:
        span_id = "mock_span_id"
    
    trace = type('MockTrace', (), {
        'set_tracer_provider': lambda x: None,
        'get_tracer': lambda x: MockTracer(),
        'get_tracer_provider': lambda: None
    })()

from ..utils.json_output import json_command

app = typer.Typer(help="🔍 Claude Code OTEL monitoring and gap detection")
console = Console()

# Initialize OTEL for Claude Code
if OTEL_DEPS_AVAILABLE:
    resource = Resource.create({
        "service.name": "claude-code-cli",
        "service.version": "2.0.0", 
        "deployment.environment": "development"
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)

    # Configure exporters if available
    if JAEGER_AVAILABLE:
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        except Exception as e:
            logger.warning(f"Jaeger exporter configuration failed: {e}")

    # Auto-instrument common libraries if available
    if INSTRUMENTATION_AVAILABLE:
        RequestsInstrumentor().instrument()
        LoggingInstrumentor().instrument()
else:
    tracer = trace.get_tracer(__name__)


class CLIOperation(Enum):
    """CLI operations to monitor"""
    VALIDATION = "validation"
    GENERATION = "generation"
    WEAVER = "weaver"
    HEALTH_CHECK = "health_check" 
    FEEDBACK = "feedback"
    AUTONOMOUS = "autonomous"


class HealthStatus(Enum):
    """Health status indicators"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class OTELGap:
    """Represents an observability gap"""
    gap_id: str
    description: str
    impact_level: str  # "high", "medium", "low"
    affected_operations: List[str]
    detection_time: datetime
    closed: bool = False
    fix_applied: Optional[str] = None


@dataclass
class CLIMetrics:
    """CLI operation metrics"""
    operation: CLIOperation
    command: str
    start_time: datetime
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    span_count: int = 0
    validation_score: Optional[float] = None
    feedback_applied: int = 0


class ClaudeCodeOTELMonitor:
    """Main OTEL monitoring system for Claude Code"""
    
    def __init__(self):
        self.gaps_detected: List[OTELGap] = []
        self.cli_metrics: List[CLIMetrics] = []
        self.session_id = f"claude_code_{int(time.time() * 1000)}"
        self.health_status = HealthStatus.UNKNOWN
        
    @contextmanager 
    def monitor_cli_operation(self, operation: CLIOperation, command: str):
        """Context manager to monitor CLI operations with OTEL"""
        
        with tracer.start_as_current_span(
            f"claude_code.cli.{operation.value}",
            attributes={
                "cli.operation": operation.value,
                "cli.command": command,
                "cli.session": self.session_id,
                "system.component": "claude_code_cli"
            }
        ) as span:
            
            start_time = datetime.utcnow()
            metrics = CLIMetrics(
                operation=operation,
                command=command,
                start_time=start_time
            )
            
            try:
                span.set_attribute("operation.status", "started")
                yield span, metrics
                
                # Mark as successful
                metrics.success = True
                span.set_attribute("operation.status", "completed")
                span.set_attribute("operation.success", True)
                
            except Exception as e:
                # Mark as failed
                metrics.success = False
                metrics.error_message = str(e)
                span.set_attribute("operation.status", "failed")
                span.set_attribute("operation.success", False)
                span.set_attribute("error.message", str(e))
                raise
                
            finally:
                # Calculate duration
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds() * 1000
                metrics.duration_ms = int(duration)
                
                span.set_attribute("operation.duration_ms", metrics.duration_ms)
                self.cli_metrics.append(metrics)
                
                # Check for performance gaps
                self._detect_performance_gaps(metrics)
    
    def _detect_performance_gaps(self, metrics: CLIMetrics):
        """Detect performance-related OTEL gaps"""
        
        # Gap 1: Slow CLI operations (>5 seconds)
        if metrics.duration_ms and metrics.duration_ms > 5000:
            gap = OTELGap(
                gap_id=f"perf_slow_{metrics.operation.value}",
                description=f"Slow {metrics.operation.value} operation: {metrics.duration_ms}ms",
                impact_level="high",
                affected_operations=[metrics.command],
                detection_time=datetime.utcnow()
            )
            self.gaps_detected.append(gap)
            
        # Gap 2: High failure rate
        recent_operations = [m for m in self.cli_metrics[-10:] 
                           if m.operation == metrics.operation]
        if len(recent_operations) >= 3:
            failure_rate = sum(1 for m in recent_operations if not m.success) / len(recent_operations)
            if failure_rate > 0.3:  # >30% failure rate
                gap = OTELGap(
                    gap_id=f"reliability_{metrics.operation.value}",
                    description=f"High failure rate for {metrics.operation.value}: {failure_rate:.1%}",
                    impact_level="high", 
                    affected_operations=[metrics.command],
                    detection_time=datetime.utcnow()
                )
                self.gaps_detected.append(gap)
    
    def add_validation_telemetry(self, validation_result: Dict[str, Any]):
        """Add telemetry for validation results"""
        
        with tracer.start_as_current_span(
            "claude_code.validation.result",
            attributes={
                "validation.session": self.session_id,
                "validation.layers_successful": validation_result.get("successful_layers", 0),
                "validation.total_layers": validation_result.get("total_layers", 0), 
                "validation.overall_score": validation_result.get("overall_score", 0),
                "validation.feedback_items": validation_result.get("feedback_items", 0),
                "validation.feedback_applied": validation_result.get("feedback_applied", 0)
            }
        ) as span:
            
            # Update latest CLI metrics with validation data
            if self.cli_metrics:
                latest = self.cli_metrics[-1]
                latest.validation_score = validation_result.get("overall_score", 0)
                latest.feedback_applied = validation_result.get("feedback_applied", 0)
                latest.span_count = validation_result.get("total_validations", 0)
                
            # Detect validation gaps
            overall_score = validation_result.get("overall_score", 0)
            if overall_score < 0.7:
                gap = OTELGap(
                    gap_id="validation_low_score",
                    description=f"Low validation score: {overall_score:.1%}",
                    impact_level="medium",
                    affected_operations=["validation"],
                    detection_time=datetime.utcnow()
                )
                self.gaps_detected.append(gap)
                
            feedback_effectiveness = validation_result.get("feedback_applied", 0) / max(validation_result.get("feedback_items", 1), 1)
            if feedback_effectiveness < 0.5:
                gap = OTELGap(
                    gap_id="feedback_low_effectiveness", 
                    description=f"Low feedback effectiveness: {feedback_effectiveness:.1%}",
                    impact_level="medium",
                    affected_operations=["feedback"],
                    detection_time=datetime.utcnow()
                )
                self.gaps_detected.append(gap)
    
    def calculate_health_status(self) -> HealthStatus:
        """Calculate overall health status based on metrics and gaps"""
        
        if not self.cli_metrics:
            return HealthStatus.UNKNOWN
            
        # Check recent operations (last 10)
        recent_ops = self.cli_metrics[-10:]
        success_rate = sum(1 for op in recent_ops if op.success) / len(recent_ops)
        
        # Check for critical gaps
        critical_gaps = [g for g in self.gaps_detected if g.impact_level == "high" and not g.closed]
        high_gaps = [g for g in self.gaps_detected if g.impact_level == "medium" and not g.closed]
        
        # Determine health status
        if critical_gaps or success_rate < 0.5:
            self.health_status = HealthStatus.CRITICAL
        elif high_gaps or success_rate < 0.8:
            self.health_status = HealthStatus.DEGRADED  
        else:
            self.health_status = HealthStatus.HEALTHY
            
        return self.health_status
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for monitoring dashboard"""
        
        recent_ops = self.cli_metrics[-20:] if self.cli_metrics else []
        
        # Performance metrics
        avg_duration = sum(op.duration_ms for op in recent_ops if op.duration_ms) / len(recent_ops) if recent_ops else 0
        success_rate = sum(1 for op in recent_ops if op.success) / len(recent_ops) if recent_ops else 0
        
        # Validation metrics
        validation_ops = [op for op in recent_ops if op.operation == CLIOperation.VALIDATION]
        avg_validation_score = sum(op.validation_score for op in validation_ops if op.validation_score) / len(validation_ops) if validation_ops else 0
        
        # Gap metrics
        open_gaps = [g for g in self.gaps_detected if not g.closed]
        critical_gaps = len([g for g in open_gaps if g.impact_level == "high"])
        
        return {
            "health_status": self.health_status.value,
            "total_operations": len(self.cli_metrics),
            "recent_operations": len(recent_ops),
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "avg_validation_score": avg_validation_score,
            "open_gaps": len(open_gaps),
            "critical_gaps": critical_gaps,
            "session_id": self.session_id,
            "last_updated": datetime.utcnow().isoformat()
        }


# Global monitor instance - shared across CLI invocations
_global_monitor = None

def get_monitor():
    """Get or create the global monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ClaudeCodeOTELMonitor()
    return _global_monitor

# Convenience alias
monitor = get_monitor()


def otel_instrumented(operation: CLIOperation):
    """Decorator to automatically instrument CLI functions with OTEL"""
    
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            command_name = func.__name__
            
            with monitor.monitor_cli_operation(operation, command_name) as (span, metrics):
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                result = func(*args, **kwargs)
                
                # Add result metadata if available
                if isinstance(result, dict):
                    if "success" in result:
                        span.set_attribute("result.success", result["success"])
                    if "score" in result:
                        span.set_attribute("result.score", result["score"])
                        
                return result
                
        return wrapper
    return decorator


@app.command("monitor")
def start_real_time_monitoring(
    interval: int = typer.Option(5, "--interval", "-i", help="Update interval in seconds"),
    duration: int = typer.Option(60, "--duration", "-d", help="Monitoring duration in seconds")
):
    """Start real-time OTEL monitoring dashboard for Claude Code"""
    
    console.print("🔍 Starting Claude Code OTEL Real-Time Monitoring")
    console.print(f"Session: {monitor.session_id}")
    console.print("=" * 60)
    
    start_time = time.time()
    
    with Live(console=console, refresh_per_second=1) as live:
        while time.time() - start_time < duration:
            
            # Get current metrics
            metrics = monitor.get_real_time_metrics()
            health = monitor.calculate_health_status()
            
            # Create monitoring table
            table = Table(title="🔍 Claude Code OTEL Health Dashboard")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", style="yellow")
            
            # Health status
            health_color = {
                "healthy": "green",
                "degraded": "yellow", 
                "critical": "red",
                "unknown": "dim"
            }.get(health.value, "dim")
            
            table.add_row("Health Status", health.value.title(), f"[{health_color}]●[/{health_color}]")
            table.add_row("Session ID", monitor.session_id, "📊")
            table.add_row("Total Operations", str(metrics["total_operations"]), "🔄")
            table.add_row("Success Rate", f"{metrics['success_rate']:.1%}", "✅" if metrics['success_rate'] > 0.8 else "⚠️")
            table.add_row("Avg Duration", f"{metrics['avg_duration_ms']:.0f}ms", "⏱️")
            table.add_row("Avg Validation Score", f"{metrics['avg_validation_score']:.1%}", "🎯")
            table.add_row("Open Gaps", str(metrics["open_gaps"]), "🔍")
            table.add_row("Critical Gaps", str(metrics["critical_gaps"]), "🚨" if metrics["critical_gaps"] > 0 else "✅")
            
            # Gap details
            if monitor.gaps_detected:
                gap_panel = Panel(
                    "\n".join([
                        f"• {gap.description} ({gap.impact_level})" + (" [CLOSED]" if gap.closed else "")
                        for gap in monitor.gaps_detected[-5:]  # Show last 5 gaps
                    ]),
                    title="🔍 Recent OTEL Gaps Detected",
                    border_style="yellow" if metrics["critical_gaps"] > 0 else "green"
                )
            else:
                gap_panel = Panel("No gaps detected", title="🔍 OTEL Gaps", border_style="green")
            
            # Update display
            display = Panel.fit(table, title=f"⏰ Updated: {datetime.now().strftime('%H:%M:%S')}")
            live.update([display, gap_panel])
            
            time.sleep(interval)
    
    console.print("\n✅ Real-time monitoring completed")


@app.command("gaps") 
def show_detected_gaps(
    show_closed: bool = typer.Option(False, "--closed", help="Show closed gaps"),
    gap_type: Optional[str] = typer.Option(None, "--type", help="Filter by gap type")
):
    """Show detected OTEL gaps and their status"""
    
    gaps = monitor.gaps_detected
    
    if not show_closed:
        gaps = [g for g in gaps if not g.closed]
    
    if gap_type:
        gaps = [g for g in gaps if gap_type.lower() in g.gap_id.lower()]
    
    table = Table(title="🔍 Claude Code OTEL Gaps")
    table.add_column("Gap ID", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Impact", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Detected", style="dim")
    
    for gap in gaps:
        status = "🔒 CLOSED" if gap.closed else "🔍 OPEN"
        impact_color = {"high": "red", "medium": "yellow", "low": "green"}.get(gap.impact_level, "white")
        
        table.add_row(
            gap.gap_id,
            gap.description,
            f"[{impact_color}]{gap.impact_level.upper()}[/{impact_color}]",
            status,
            gap.detection_time.strftime("%H:%M:%S")
        )
    
    console.print(table)
    
    if not gaps:
        console.print("✅ No OTEL gaps detected!")


@app.command("close-gap")
def close_detected_gap(
    gap_id: str = typer.Argument(..., help="Gap ID to close"),
    fix_description: Optional[str] = typer.Option(None, "--fix", help="Description of fix applied")
):
    """Close a detected OTEL gap"""
    
    for gap in monitor.gaps_detected:
        if gap.gap_id == gap_id:
            gap.closed = True
            gap.fix_applied = fix_description or "Manual closure"
            
            console.print(f"✅ Closed gap: {gap_id}")
            console.print(f"Fix applied: {gap.fix_applied}")
            return
    
    console.print(f"❌ Gap not found: {gap_id}")
    raise typer.Exit(1)


@app.command("instrument-command")
def instrument_cli_command(
    command: str = typer.Argument(..., help="CLI command to instrument"),
    operation_type: str = typer.Option("validation", help="Operation type")
):
    """Manually instrument a CLI command with OTEL"""
    
    operation = CLIOperation(operation_type)
    
    with monitor.monitor_cli_operation(operation, command) as (span, metrics):
        console.print(f"🔍 Instrumenting command: {command}")
        span.set_attribute("manual_instrumentation", True)
        
        # Simulate command execution
        time.sleep(1)
        
        console.print(f"✅ Command instrumented with span: {span.get_span_context().span_id}")


@app.command("status")
def show_monitoring_status():
    """Show Claude Code OTEL monitoring status"""
    
    metrics = monitor.get_real_time_metrics()
    health = monitor.calculate_health_status()
    
    status_panel = Panel(
        f"""🔍 **Claude Code OTEL Monitor Status**

📊 **Metrics**:
   • Health: {health.value.title()}
   • Total Operations: {metrics['total_operations']}
   • Success Rate: {metrics['success_rate']:.1%}
   • Avg Duration: {metrics['avg_duration_ms']:.0f}ms
   • Validation Score: {metrics['avg_validation_score']:.1%}

🔍 **Gaps**:
   • Open Gaps: {metrics['open_gaps']}
   • Critical: {metrics['critical_gaps']}

🎯 **Session**: {monitor.session_id}
⏰ **Updated**: {metrics['last_updated']}""",
        title="🔍 OTEL Monitoring Status",
        border_style="green" if health == HealthStatus.HEALTHY else "yellow"
    )
    
    console.print(status_panel)


@app.command("export-traces")
def export_traces(
    output_file: Path = typer.Option(Path("claude_code_traces.json"), "--output", "-o"),
    format_type: str = typer.Option("json", "--format", help="Export format")
):
    """Export collected traces and metrics"""
    
    export_data = {
        "session_id": monitor.session_id,
        "export_timestamp": datetime.utcnow().isoformat(),
        "health_status": monitor.health_status.value,
        "cli_metrics": [
            {
                "operation": m.operation.value,
                "command": m.command,
                "start_time": m.start_time.isoformat(),
                "duration_ms": m.duration_ms,
                "success": m.success,
                "validation_score": m.validation_score,
                "feedback_applied": m.feedback_applied
            }
            for m in monitor.cli_metrics
        ],
        "gaps_detected": [
            {
                "gap_id": g.gap_id,
                "description": g.description,
                "impact_level": g.impact_level,
                "affected_operations": g.affected_operations,
                "detection_time": g.detection_time.isoformat(),
                "closed": g.closed,
                "fix_applied": g.fix_applied
            }
            for g in monitor.gaps_detected
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    console.print(f"✅ Traces exported to: {output_file}")
    console.print(f"📊 Exported {len(monitor.cli_metrics)} operations and {len(monitor.gaps_detected)} gaps")


if __name__ == "__main__":
    app()