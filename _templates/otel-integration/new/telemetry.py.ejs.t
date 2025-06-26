---
to: src/dslmodel/otel/<%= fileName %>.py
---
"""
<%= name %> Telemetry - <%= description %>

This module provides OpenTelemetry integration for <%= signal_type %> with
custom exporters and processors for the SwarmAgent ecosystem.
"""

import json
import time
from typing import Dict, Any, Optional, Sequence, List
from pathlib import Path
from contextlib import contextmanager

from opentelemetry import trace<% if (signal_type === 'metrics' || signal_type === 'all') { %>, metrics<% } %>
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Span, Status, StatusCode
<% if (signal_type === 'metrics' || signal_type === 'all') { %>from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult<% } %>
<% if (has_exporter) { %>

class <%= exporterName %>(SpanExporter):
    """Custom span exporter for <%= name %> telemetry."""
    
    def __init__(self, output_file: Optional[Path] = None):
        """Initialize the exporter.
        
        Args:
            output_file: Path to output file (defaults to telemetry_spans.jsonl)
        """
        self.output_file = output_file or Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
    
    def export(self, spans: Sequence[trace.ReadableSpan]) -> SpanExportResult:
        """Export spans to JSONL file.
        
        Args:
            spans: Sequence of spans to export
            
        Returns:
            Export result status
        """
        try:
            with self.output_file.open('a') as f:
                for span in spans:
                    span_dict = {
                        "name": span.name,
                        "trace_id": format(span.context.trace_id, '032x'),
                        "span_id": format(span.context.span_id, '016x'),
                        "parent_id": format(span.parent.span_id, '016x') if span.parent else None,
                        "timestamp": span.start_time / 1e9,
                        "duration": (span.end_time - span.start_time) / 1e9 if span.end_time else 0,
                        "attributes": dict(span.attributes) if span.attributes else {},
                        "status": {
                            "code": span.status.status_code.name,
                            "description": span.status.description
                        } if span.status else None,
                        "service": "<%= service_name %>"
                    }
                    f.write(json.dumps(span_dict) + '\n')
            
            return SpanExportResult.SUCCESS
            
        except Exception as e:
            print(f"Error exporting spans: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass
<% } %>
<% if (has_processor) { %>

class <%= processorName %>(SpanProcessor):
    """Custom span processor for <%= name %> telemetry."""
    
    def __init__(self):
        """Initialize the processor."""
        self.span_count = 0
        self.error_count = 0
        self.processing_times: List[float] = []
    
    def on_start(self, span: Span, parent_context: Optional[trace.Context] = None) -> None:
        """Called when a span is started.
        
        Args:
            span: The span that was started
            parent_context: Optional parent context
        """
        # Add default attributes
        span.set_attribute("processor.name", "<%= processorName %>")
        span.set_attribute("processor.version", "1.0.0")
        span.set_attribute("service.name", "<%= service_name %>")
        
        # Add custom processing
        if span.name.startswith("swarmsh."):
            span.set_attribute("swarm.enabled", True)
    
    def on_end(self, span: trace.ReadableSpan) -> None:
        """Called when a span is ended.
        
        Args:
            span: The span that was ended
        """
        self.span_count += 1
        
        # Track errors
        if span.status and span.status.status_code == StatusCode.ERROR:
            self.error_count += 1
        
        # Track processing time
        if span.end_time and span.start_time:
            duration = (span.end_time - span.start_time) / 1e9
            self.processing_times.append(duration)
        
        # Log significant spans
        if span.attributes and span.attributes.get("important", False):
            print(f"📊 Important span completed: {span.name} (duration: {duration:.3f}s)")
    
    def shutdown(self) -> None:
        """Shutdown the processor."""
        print(f"📈 Processor stats: {self.span_count} spans, {self.error_count} errors")
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending spans.
        
        Args:
            timeout_millis: Timeout in milliseconds
            
        Returns:
            Success status
        """
        return True
<% } %>

class <%= className %>:
    """<%= description %>"""
    
    def __init__(self, service_name: str = "<%= service_name %>", 
                 output_file: Optional[Path] = None):
        """Initialize telemetry.
        
        Args:
            service_name: Name of the service for telemetry
            output_file: Optional output file for spans
        """
        self.service_name = service_name
        self.output_file = output_file
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
<% if (signal_type === 'metrics' || signal_type === 'all') { %>        self.meter_provider: Optional[MeterProvider] = None
        self.meter: Optional[metrics.Meter] = None<% } %>
        
        self.setup()
    
    def setup(self):
        """Set up OpenTelemetry providers and instrumentation."""
        # Create resource
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python",
            "telemetry.type": "<%= signal_type %>"
        })
        
        # Set up tracing
        self.tracer_provider = TracerProvider(resource=resource)
<% if (has_processor) { %>        
        # Add custom processor
        processor = <%= processorName %>()
        self.tracer_provider.add_span_processor(processor)
<% } %>
<% if (has_exporter) { %>        
        # Add custom exporter
        exporter = <%= exporterName %>(output_file=self.output_file)
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(exporter)
        )
<% } %>        
        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)
<% if (signal_type === 'metrics' || signal_type === 'all') { %>        
        # Set up metrics
        self.meter_provider = MeterProvider(resource=resource)
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(__name__)
        
        # Create common metrics
        self.span_counter = self.meter.create_counter(
            name="<%= service_name %>.spans",
            description="Number of spans created",
            unit="1"
        )
        
        self.duration_histogram = self.meter.create_histogram(
            name="<%= service_name %>.duration",
            description="Span duration distribution",
            unit="ms"
        )
<% } %>    
    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a telemetry span context manager.
        
        Args:
            name: Span name
            attributes: Optional span attributes
            
        Yields:
            The created span
        """
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
<% if (signal_type === 'metrics' || signal_type === 'all') { %>            
            # Record metrics
            start_time = time.time()
            self.span_counter.add(1, {"span.name": name})
<% } %>            
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
<% if (signal_type === 'metrics' || signal_type === 'all') { %>            finally:
                # Record duration
                duration_ms = (time.time() - start_time) * 1000
                self.duration_histogram.record(duration_ms, {"span.name": name})
<% } %>    
    def emit_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Emit a telemetry event.
        
        Args:
            name: Event name
            attributes: Optional event attributes
        """
        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {})
        else:
            # Create a new span for the event
            with self.span(f"event.{name}", attributes):
                pass
    
    def shutdown(self):
        """Shutdown telemetry providers."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
<% if (signal_type === 'metrics' || signal_type === 'all') { %>        if self.meter_provider:
            self.meter_provider.shutdown()<% } %>
<% if (has_semantic_conventions) { %>

# Semantic conventions for <%= name %> telemetry
class <%= name %>Attributes:
    """Semantic convention attributes for <%= name %>."""
    
    # Service attributes
    SERVICE_NAME = "<%= service_name %>.service.name"
    SERVICE_VERSION = "<%= service_name %>.service.version"
    SERVICE_INSTANCE = "<%= service_name %>.service.instance"
    
    # Operation attributes
    OPERATION_TYPE = "<%= service_name %>.operation.type"
    OPERATION_STATUS = "<%= service_name %>.operation.status"
    OPERATION_DURATION = "<%= service_name %>.operation.duration"
    
    # Agent attributes
    AGENT_NAME = "<%= service_name %>.agent.name"
    AGENT_TYPE = "<%= service_name %>.agent.type"
    AGENT_STATE = "<%= service_name %>.agent.state"
    
    # Workflow attributes
    WORKFLOW_ID = "<%= service_name %>.workflow.id"
    WORKFLOW_STEP = "<%= service_name %>.workflow.step"
    WORKFLOW_STATUS = "<%= service_name %>.workflow.status"
<% } %>

# Example usage
if __name__ == "__main__":
    # Initialize telemetry
    telemetry = <%= className %>()
    
    # Example span with context manager
    with telemetry.span("example.operation", {"user": "test", "action": "demo"}) as span:
        print("📊 Executing operation...")
        time.sleep(0.1)
        
        # Add event
        telemetry.emit_event("operation.milestone", {"progress": 50})
        
        # Simulate work
        time.sleep(0.1)
        
        # Set custom attribute
        span.set_attribute("result", "success")
    
    print("✅ Telemetry demo complete")
    
    # Shutdown
    telemetry.shutdown()