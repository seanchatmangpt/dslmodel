"""
OpenTelemetry Setup and Configuration
Provides setup utilities for OTEL with graceful fallbacks
"""

import os
from typing import Tuple, Optional

# OpenTelemetry imports (with fallbacks for when not installed)
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    
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
    OTLP_AVAILABLE = False
    
    # Mock classes for when OTEL is not available
    class MockTracer:
        def start_as_current_span(self, name, **kwargs):
            from contextlib import contextmanager
            @contextmanager
            def mock_context():
                yield MockSpan()
            return mock_context()
        
        def get_tracer(self, name, version=None):
            return self
    
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
# Setup Functions
###############################################################################

def setup_otel(service_name: str = "dslmodel-coordination") -> Tuple:
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

def create_tracer(service_name: str, version: str = "1.0.0"):
    """Create a tracer for the given service"""
    if OTEL_AVAILABLE:
        return trace.get_tracer(service_name, version)
    else:
        return MockTracer()

def create_meter(service_name: str, version: str = "1.0.0"):
    """Create a meter for the given service"""
    if OTEL_AVAILABLE:
        return metrics.get_meter(service_name, version)
    else:
        return MockMeter()

def is_otel_configured() -> bool:
    """Check if OTEL is properly configured"""
    return (
        OTEL_AVAILABLE and 
        (os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") is not None or 
         os.getenv("OTEL_SDK_DISABLED") != "true")
    )