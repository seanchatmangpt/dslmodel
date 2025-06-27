"""Mock OpenTelemetry instrumentation for testing without dependencies."""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass

# Mock OTEL classes for testing
class MockSpan:
    def __init__(self, name: str, attributes: Dict[str, Any] = None):
        self.name = name
        self.attributes = attributes or {}
        
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        
    def set_status(self, status):
        pass
        
    def record_exception(self, exception):
        pass
        
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        pass
        
    def add_link(self, link):
        pass
        
    def get_span_context(self):
        return MockSpanContext()

class MockSpanContext:
    def __init__(self):
        self.trace_id = 12345678901234567890123456789012
        self.span_id = 1234567890123456

class MockTracer:
    @contextmanager
    def start_as_current_span(self, name: str, kind=None, attributes: Dict[str, Any] = None):
        yield MockSpan(name, attributes)

class MockMeter:
    def create_counter(self, name: str, description: str = "", unit: str = "1"):
        return MockCounter()
        
    def create_up_down_counter(self, name: str, description: str = "", unit: str = "1"):
        return MockUpDownCounter()
        
    def create_histogram(self, name: str, description: str = "", unit: str = "ms"):
        return MockHistogram()

class MockCounter:
    def add(self, amount: int, attributes: Dict[str, Any] = None):
        pass

class MockUpDownCounter:
    def add(self, amount: int, attributes: Dict[str, Any] = None):
        pass

class MockHistogram:
    def record(self, amount: float, attributes: Dict[str, Any] = None):
        pass

class MockLink:
    def __init__(self, span_context, attributes: Dict[str, Any] = None):
        self.span_context = span_context
        self.attributes = attributes or {}

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

class MockStatus:
    def __init__(self, status_code, description=""):
        self.status_code = status_code
        self.description = description

class MockStatusCode:
    OK = "OK"
    ERROR = "ERROR"

class OTelInstrumentation:
    """
    Mock OpenTelemetry instrumentation for testing without dependencies.
    """
    
    def __init__(self, 
                 service_name: str = "swarm-agent",
                 service_version: str = "1.0.0",
                 otlp_endpoint: str = None,
                 prometheus_port: int = 8000,
                 enable_console_export: bool = False):
        """
        Initialize mock OpenTelemetry instrumentation.
        """
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint or "localhost:4317"
        
        # Mock instrumentations
        self.tracer = MockTracer()
        self.meter = MockMeter()
        
        # Create mock metrics
        self._create_metrics()
    
    def _create_metrics(self):
        """Create mock metrics for swarm agents."""
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
    def trace_span(self, name: str, kind=None, attributes: Dict[str, Any] = None):
        """
        Context manager for creating mock spans.
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
                span.set_status(MockStatus(MockStatusCode.ERROR, str(e)))
                raise
            else:
                span.set_status(MockStatus(MockStatusCode.OK))
    
    def create_span_link(self, trace_id: str, span_id: str, attributes: Dict[str, Any] = None) -> MockLink:
        """
        Create a mock span link.
        """
        span_context = MockSpanContext()
        return MockLink(span_context, attributes or {})
    
    def inject_context(self, carrier: Dict[str, str]) -> Dict[str, str]:
        """
        Mock context injection.
        """
        carrier["traceparent"] = "00-12345678901234567890123456789012-1234567890123456-01"
        return carrier
    
    def extract_context(self, carrier: Dict[str, str]):
        """
        Mock context extraction.
        """
        return None
    
    def record_state_transition(self, agent_name: str, from_state: str, to_state: str, framework: str):
        """Record mock state transition metric."""
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
        """Record mock command execution metric."""
        self.commands_executed.add(
            1,
            attributes={
                SwarmSpanAttributes.AGENT_NAME: agent_name,
                SwarmSpanAttributes.SWARM_COMMAND: command,
                "success": str(success)
            }
        )
    
    def get_current_trace_context(self) -> Dict[str, str]:
        """Get mock trace context as dictionary."""
        return {"traceparent": "00-12345678901234567890123456789012-1234567890123456-01"}

# Global mock instrumentation instance
_instrumentation: Optional[OTelInstrumentation] = None

def init_otel(service_name: str, **kwargs) -> OTelInstrumentation:
    """
    Initialize mock OpenTelemetry instrumentation.
    """
    global _instrumentation
    _instrumentation = OTelInstrumentation(service_name=service_name, **kwargs)
    return _instrumentation

def get_otel() -> OTelInstrumentation:
    """Get mock OpenTelemetry instrumentation instance."""
    if _instrumentation is None:
        raise RuntimeError("OTel not initialized. Call init_otel() first.")
    return _instrumentation