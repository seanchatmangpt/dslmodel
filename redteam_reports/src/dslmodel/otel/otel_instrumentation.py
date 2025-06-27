"""OpenTelemetry instrumentation setup for swarm agents."""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import trace, metrics, baggage, context
from opentelemetry.trace import Status, StatusCode, Link
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Optional Prometheus exporter with fallback
try:
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    PrometheusMetricReader = None

from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider, Counter, Histogram, UpDownCounter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

# Global flag to prevent multiple TracerProvider setups
_otel_initialized = False

# Semantic conventions for swarm agents
class SwarmSpanAttributes:
    """Custom semantic conventions for swarm agents."""
    AGENT_NAME = "swarm.agent.name"
    AGENT_STATE = "swarm.agent.state"
    AGENT_TRANSITION = "swarm.agent.transition"
    SWARM_COMMAND = "swarm.command"
    SWARM_COMMAND_ARGS = "swarm.command.args"
    SWARM_FRAMEWORK = "swarm.framework"  # roberts, scrum, lean
    SWARM_PHASE = "swarm.phase"
    WORK_ID = "swarm.work.id"
    WORK_TYPE = "swarm.work.type"
    WORK_PRIORITY = "swarm.work.priority"
    WORK_TEAM = "swarm.work.team"


class OTelInstrumentation:
    """
    Centralized OpenTelemetry instrumentation for swarm agents.
    
    Provides:
    - Distributed tracing with OTLP export
    - Metrics collection (Prometheus + OTLP)
    - Structured logging with trace correlation
    - Context propagation across agents
    """
    
    def __init__(self, 
                 service_name: str = "swarm-agent",
                 service_version: str = "1.0.0",
                 otlp_endpoint: str = None,
                 prometheus_port: int = 8000,
                 enable_console_export: bool = False):
        """
        Initialize OpenTelemetry instrumentation.
        
        Args:
            service_name: Name of the service (agent)
            service_version: Version of the service
            otlp_endpoint: OTLP collector endpoint (default: localhost:4317)
            prometheus_port: Port for Prometheus metrics endpoint
            enable_console_export: Enable console span export for debugging
        """
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
        
        # Create resource
        self.resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "service.namespace": "swarmsh",
            "deployment.environment": os.getenv("DEPLOYMENT_ENV", "development"),
            "swarm.agent.type": service_name.replace("-agent", "")
        })
        
        # Setup components
        self._setup_tracing(enable_console_export)
        self._setup_metrics(prometheus_port)
        self._setup_logging()
        self._setup_propagation()
        
        # Get instrumentations
        self.tracer = trace.get_tracer(
            instrumenting_module_name=f"{service_name}.tracer",
            instrumenting_library_version=service_version
        )
        
        self.meter = metrics.get_meter(
            name=f"{service_name}.meter",
            version=service_version
        )
        
        # Create common metrics
        self._create_metrics()
    
    def _setup_tracing(self, enable_console: bool = False):
        """Setup distributed tracing with OTLP export."""
        global _otel_initialized
        
        # Only setup if not already initialized
        if _otel_initialized:
            return
            
        # Create OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.otlp_endpoint,
            insecure=True,  # Use TLS in production
            headers=(("api-key", os.getenv("OTLP_API_KEY", "")),) if os.getenv("OTLP_API_KEY") else None
        )
        
        # Create span processors
        processors = [BatchSpanProcessor(otlp_exporter)]
        if enable_console:
            processors.append(BatchSpanProcessor(ConsoleSpanExporter()))
        
        # Create and set tracer provider
        provider = TracerProvider(resource=self.resource)
        for processor in processors:
            provider.add_span_processor(processor)
        
        trace.set_tracer_provider(provider)
        _otel_initialized = True
    
    def _setup_metrics(self, prometheus_port: int):
        """Setup metrics with Prometheus and OTLP export."""
        # Create OTLP metric exporter
        otlp_metric_exporter = OTLPMetricExporter(
            endpoint=self.otlp_endpoint,
            insecure=True,
            headers=(("api-key", os.getenv("OTLP_API_KEY", "")),) if os.getenv("OTLP_API_KEY") else None
        )
        
        # Create metric readers
        metric_readers = [otlp_metric_exporter]
        
        # Add Prometheus reader if available
        if PROMETHEUS_AVAILABLE:
            try:
                prometheus_reader = PrometheusMetricReader(port=prometheus_port)
                metric_readers.append(prometheus_reader)
            except Exception as e:
                logging.warning(f"Failed to setup Prometheus metrics: {e}")
        else:
            logging.info("Prometheus metrics not available - install opentelemetry-exporter-prometheus for Prometheus support")
        
        # Create meter provider with readers
        provider = MeterProvider(
            resource=self.resource,
            metric_readers=metric_readers
        )
        
        metrics.set_meter_provider(provider)
    
    def _setup_logging(self):
        """Setup structured logging with OTLP export."""
        # Create OTLP log exporter
        otlp_log_exporter = OTLPLogExporter(
            endpoint=self.otlp_endpoint,
            insecure=True
        )
        
        # Create logger provider
        logger_provider = LoggerProvider(resource=self.resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(otlp_log_exporter)
        )
        
        # Create handler that emits to OpenTelemetry
        handler = LoggingHandler(
            level=logging.INFO,
            logger_provider=logger_provider
        )
        
        # Attach to root logger
        logging.getLogger().addHandler(handler)
        
        # Instrument logging to inject trace context
        LoggingInstrumentor().instrument()
    
    def _setup_propagation(self):
        """Setup context propagation for distributed tracing."""
        # Use W3C Trace Context for propagation
        set_global_textmap(TraceContextTextMapPropagator())
    
    def _create_metrics(self):
        """Create common metrics for swarm agents."""
        # Agent state transitions
        self.state_transitions = self.meter.create_counter(
            name="swarm.agent.state_transitions",
            description="Number of state transitions",
            unit="1"
        )
        
        # Commands executed
        self.commands_executed = self.meter.create_counter(
            name="swarm.agent.commands_executed",
            description="Number of CLI commands executed",
            unit="1"
        )
        
        # Active agents gauge
        self.active_agents = self.meter.create_up_down_counter(
            name="swarm.agent.active",
            description="Number of active agents",
            unit="1"
        )
        
        # Span processing duration
        self.span_processing_duration = self.meter.create_histogram(
            name="swarm.agent.span_processing_duration",
            description="Duration of span processing",
            unit="ms"
        )
        
        # Work items by status
        self.work_items_gauge = self.meter.create_up_down_counter(
            name="swarm.work.items",
            description="Number of work items by status",
            unit="1"
        )
    
    @contextmanager
    def trace_span(self, name: str, kind=trace.SpanKind.INTERNAL, attributes: Dict[str, Any] = None):
        """
        Context manager for creating spans with automatic error handling.
        
        Args:
            name: Span name
            kind: Span kind (INTERNAL, CLIENT, SERVER, etc.)
            attributes: Initial span attributes
        """
        with self.tracer.start_as_current_span(
            name=name,
            kind=kind,
            attributes=attributes or {}
        ) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            else:
                span.set_status(Status(StatusCode.OK))
    
    def create_span_link(self, trace_id: str, span_id: str, attributes: Dict[str, Any] = None) -> Link:
        """
        Create a span link for cross-agent correlation.
        
        Args:
            trace_id: Trace ID to link to
            span_id: Span ID to link to
            attributes: Link attributes
        """
        # Convert hex strings to proper format
        trace_id_int = int(trace_id, 16)
        span_id_int = int(span_id, 16)
        
        span_context = trace.SpanContext(
            trace_id=trace_id_int,
            span_id=span_id_int,
            is_remote=True,
            trace_flags=trace.TraceFlags(0x01),  # Sampled
            trace_state=trace.TraceState()
        )
        
        return Link(span_context, attributes or {})
    
    def inject_context(self, carrier: Dict[str, str]) -> Dict[str, str]:
        """
        Inject current trace context into carrier for propagation.
        
        Args:
            carrier: Dictionary to inject context into
            
        Returns:
            Updated carrier with trace context
        """
        from opentelemetry import propagate
        propagate.inject(carrier)
        return carrier
    
    def extract_context(self, carrier: Dict[str, str]):
        """
        Extract trace context from carrier and set as current.
        
        Args:
            carrier: Dictionary containing trace context
        """
        from opentelemetry import propagate
        ctx = propagate.extract(carrier)
        context.attach(ctx)
        return ctx
    
    def record_state_transition(self, agent_name: str, from_state: str, to_state: str, framework: str):
        """Record agent state transition metric."""
        self.state_transitions.add(
            1,
            attributes={
                SwarmSpanAttributes.AGENT_NAME: agent_name,
                "from_state": from_state,
                "to_state": to_state,
                SwarmSpanAttributes.SWARM_FRAMEWORK: framework
            }
        )
    
    def record_command_execution(self, agent_name: str, command: str, success: bool):
        """Record command execution metric."""
        self.commands_executed.add(
            1,
            attributes={
                SwarmSpanAttributes.AGENT_NAME: agent_name,
                SwarmSpanAttributes.SWARM_COMMAND: command,
                "success": str(success)
            }
        )
    
    def get_current_trace_context(self) -> Dict[str, str]:
        """Get current trace context as dictionary."""
        carrier = {}
        self.inject_context(carrier)
        return carrier


# Global instrumentation instance
_instrumentation: Optional[OTelInstrumentation] = None


def init_otel(service_name: str, **kwargs) -> OTelInstrumentation:
    """
    Initialize global OpenTelemetry instrumentation.
    
    Args:
        service_name: Name of the service/agent
        **kwargs: Additional arguments for OTelInstrumentation
        
    Returns:
        OTelInstrumentation instance
    """
    global _instrumentation
    _instrumentation = OTelInstrumentation(service_name=service_name, **kwargs)
    return _instrumentation


def get_otel() -> OTelInstrumentation:
    """Get global OpenTelemetry instrumentation instance."""
    if _instrumentation is None:
        raise RuntimeError("OTel not initialized. Call init_otel() first.")
    return _instrumentation