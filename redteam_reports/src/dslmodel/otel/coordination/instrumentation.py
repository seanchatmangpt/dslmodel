"""
OpenTelemetry instrumentation utilities for coordination system
"""

import time
from contextlib import contextmanager
from typing import Optional, Dict, Any
from ..ecosystem.setup import OTEL_AVAILABLE

if OTEL_AVAILABLE:
    from opentelemetry import trace, baggage
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.semconv.trace import SpanAttributes
else:
    # Mock implementations
    class MockStatus:
        def __init__(self, status_code, description=""):
            pass
    
    class MockStatusCode:
        ERROR = "error"
        OK = "ok"
    
    Status = MockStatus
    StatusCode = MockStatusCode

###############################################################################
# Enhanced Context Manager
###############################################################################

@contextmanager
def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Enhanced tracing with metrics and context propagation"""
    if OTEL_AVAILABLE:
        tracer = trace.get_tracer("dslmodel.coordination")
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
    else:
        # Mock span for when OTEL is not available
        class MockSpan:
            def set_attribute(self, key, value): pass
            def set_attributes(self, attrs): pass
            def set_status(self, status): pass
            def set_status_error(self, message): pass
            def record_exception(self, exception): pass
            def get_span_context(self): 
                class MockContext:
                    trace_id = 123456789
                    span_id = 987654321
                return MockContext()
        
        yield MockSpan()

###############################################################################
# Instrumentation Helper Class
###############################################################################

class CoordinationInstrumentation:
    """Helper class for consistent instrumentation"""
    
    def __init__(self, tracer, meter):
        self.tracer = tracer
        self.meter = meter
        
        if OTEL_AVAILABLE:
            # Create metrics
            self.work_items_created = meter.create_counter(
                name="dslmodel.coordination.work_items.created",
                description="Number of work items created",
                unit="1"
            )
            
            self.work_items_completed = meter.create_counter(
                name="dslmodel.coordination.work_items.completed",
                description="Number of work items completed", 
                unit="1"
            )
            
            self.work_item_duration = meter.create_histogram(
                name="dslmodel.coordination.work_item.duration",
                description="Duration of work items",
                unit="s"
            )
            
            self.api_latency = meter.create_histogram(
                name="dslmodel.coordination.api.latency",
                description="API operation latency",
                unit="ms"
            )
        else:
            # Mock metrics
            class MockMetric:
                def add(self, value, attributes=None): pass
                def record(self, value, attributes=None): pass
            
            self.work_items_created = MockMetric()
            self.work_items_completed = MockMetric()
            self.work_item_duration = MockMetric()
            self.api_latency = MockMetric()
    
    def record_work_created(self, work_type: str, priority: str, team: str):
        """Record work item creation metrics"""
        labels = {
            "work.type": work_type,
            "work.priority": priority,
            "work.team": team
        }
        self.work_items_created.add(1, labels)
    
    def record_work_completed(self, work_type: str, priority: str, team: str, 
                            status: str, duration_seconds: Optional[float] = None):
        """Record work item completion metrics"""
        labels = {
            "work.type": work_type,
            "work.priority": priority,
            "work.team": team,
            "completion.status": status
        }
        
        self.work_items_completed.add(1, labels)
        
        if duration_seconds:
            duration_labels = {
                "work.type": work_type,
                "work.priority": priority
            }
            self.work_item_duration.record(duration_seconds, duration_labels)
    
    def record_api_call(self, operation: str, duration_ms: float, status: str = "success"):
        """Record API call metrics"""
        labels = {
            "operation": operation,
            "status": status
        }
        self.api_latency.record(duration_ms, labels)