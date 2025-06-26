---
to: src/dslmodel/weaver/<%= modelFileName %>.py
skip_if: <%= !generate_models %>
---
"""
<%= domain.charAt(0).toUpperCase() + domain.slice(1) %> Semantic Convention Models

Auto-generated Pydantic models for <%= domain.toLowerCase() %> semantic conventions.
These models provide type-safe access to telemetry attributes and ensure
consistency across the SwarmAgent ecosystem.

Generated from: semconv_registry/<%= registryFileName %>
Version: <%= version %>
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanKind(str, Enum):
    """Span kind enumeration for <%= domain.toLowerCase() %> operations."""
    CLIENT = "client"
    SERVER = "server"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>OperationResult(str, Enum):
    """Operation result enumeration."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes(BaseModel):
    """Core <%= domain.toLowerCase() %> attributes model."""
    
<% attributes.forEach(function(attr) { %>    <%= attr %>: Optional[str] = Field(
        None,
        description="<%= attr.charAt(0).toUpperCase() + attr.slice(1).replace(/_/g, ' ') %>",
        example="example_<%= attr %>"
    )
<% }); %>    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes(<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes):
    """Span-specific <%= domain.toLowerCase() %> attributes."""
    
    span_kind: <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanKind = Field(
        <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanKind.INTERNAL,
        description="Type of span operation"
    )
    
    operation_name: str = Field(
        ...,
        description="Name of the operation being performed",
        example="process"
    )
    
    operation_result: Optional[<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>OperationResult] = Field(
        None,
        description="Result status of the operation"
    )
    
    def to_otel_attributes(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry span attributes.
        
        Returns:
            Dictionary of attributes for OTEL spans
        """
        attrs = {}
        
        # Add core attributes with prefix
<% attributes.forEach(function(attr) { %>        if self.<%= attr %> is not None:
            attrs["<%= prefix %>.<%= attr %>"] = self.<%= attr %>
<% }); %>        
        # Add span-specific attributes
        attrs["<%= prefix %>.span.kind"] = self.span_kind
        attrs["<%= prefix %>.operation.name"] = self.operation_name
        
        if self.operation_result:
            attrs["<%= prefix %>.operation.result"] = self.operation_result
        
        return attrs


class SwarmAgent<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes(BaseModel):
    """SwarmAgent-specific <%= domain.toLowerCase() %> attributes."""
    
    agent_name: str = Field(
        ...,
        description="Name of the SwarmAgent handling this operation",
        example="<%= domain.toLowerCase() %>_agent"
    )
    
    agent_state: Optional[str] = Field(
        None,
        description="Current state of the SwarmAgent",
        example="PROCESSING"
    )
    
    trigger_name: Optional[str] = Field(
        None,
        description="Name of the trigger that activated this operation",
        example="start"
    )
    
    workflow_id: Optional[str] = Field(
        None,
        description="Identifier for the workflow this operation belongs to",
        example="workflow_123"
    )
    
    coordination_step: Optional[int] = Field(
        None,
        description="Step number in multi-agent coordination",
        example=1
    )
    
    def to_otel_attributes(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry span attributes.
        
        Returns:
            Dictionary of SwarmAgent attributes for OTEL spans
        """
        attrs = {
            "swarm.<%= prefix %>.agent.name": self.agent_name
        }
        
        if self.agent_state:
            attrs["swarm.<%= prefix %>.agent.state"] = self.agent_state
        
        if self.trigger_name:
            attrs["swarm.<%= prefix %>.trigger.name"] = self.trigger_name
            
        if self.workflow_id:
            attrs["swarm.<%= prefix %>.workflow.id"] = self.workflow_id
            
        if self.coordination_step:
            attrs["swarm.<%= prefix %>.coordination.step"] = self.coordination_step
        
        return attrs

<% if (has_metrics) { %>
class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Metrics(BaseModel):
    """Metrics model for <%= domain.toLowerCase() %> operations."""
    
<% metrics.forEach(function(metric, index) { %>    <%= metric.split('.').pop().replace(/[.-]/g, '_') %>: Optional[Union[int, float]] = Field(
        None,
        description="<%= metric.split('.').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') %>",
        example=<% if (metric.includes('duration')) { %>100.5<% } else { %>1<% } %>
    )
<% }); %>    
    def to_metric_data(self) -> Dict[str, Dict[str, Any]]:
        """Convert to metric export format.
        
        Returns:
            Dictionary of metric data for exporters
        """
        metrics = {}
        
<% metrics.forEach(function(metric) { %>        if self.<%= metric.split('.').pop().replace(/[.-]/g, '_') %> is not None:
            metrics["<%= metric %>"] = {
                "value": self.<%= metric.split('.').pop().replace(/[.-]/g, '_') %>,
                "type": "<% if (metric.includes('histogram')) { %>histogram<% } else if (metric.includes('gauge')) { %>gauge<% } else { %>counter<% } %>",
                "unit": "<% if (metric.includes('duration')) { %>ms<% } else { %>1<% } %>",
                "timestamp": datetime.now().isoformat()
            }
<% }); %>        
        return metrics
<% } %>

<% if (has_events) { %>
class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Event(BaseModel):
    """Event model for <%= domain.toLowerCase() %> operations."""
    
    name: str = Field(
        ...,
        description="Event name",
        example="<%= prefix %>.operation.started"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Event timestamp"
    )
    
    attributes: <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes = Field(
        default_factory=<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes,
        description="Event attributes"
    )
    
    def to_otel_event(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry event format.
        
        Returns:
            Dictionary formatted for OTEL event emission
        """
        return {
            "name": self.name,
            "timestamp": int(self.timestamp.timestamp() * 1e9),  # nanoseconds
            "attributes": {
                **self.attributes.dict(exclude_none=True),
                "event.timestamp": int(self.timestamp.timestamp())
            }
        }


# Predefined event types
<% events.forEach(function(event) { %>class <%= event.split('.').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('') %>Event(<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Event):
    """<%= event.split('.').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') %> event."""
    
    name: str = Field(
        default="<%= event %>",
        description="Event name",
        const=True
    )

<% }); %><% } %>

class <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>ResourceAttributes(BaseModel):
    """Resource-level attributes for <%= domain.toLowerCase() %> services."""
    
    service_name: str = Field(
        ...,
        description="Name of the <%= domain.toLowerCase() %> service",
        example="<%= domain.toLowerCase() %>_processor"
    )
    
    service_version: Optional[str] = Field(
        None,
        description="Version of the <%= domain.toLowerCase() %> service",
        example="1.0.0"
    )
    
    service_instance_id: Optional[str] = Field(
        None,
        description="Instance identifier for the service",
        example="instance_001"
    )
    
    def to_otel_resource(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry resource attributes.
        
        Returns:
            Dictionary of resource attributes
        """
        attrs = {
            "<%= prefix %>.resource.service.name": self.service_name
        }
        
        if self.service_version:
            attrs["<%= prefix %>.resource.service.version"] = self.service_version
            
        if self.service_instance_id:
            attrs["<%= prefix %>.resource.service.instance.id"] = self.service_instance_id
        
        return attrs


class Complete<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Context(BaseModel):
    """Complete context model combining all <%= domain.toLowerCase() %> telemetry."""
    
    span_attributes: <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes = Field(
        default_factory=<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes,
        description="Span-level attributes"
    )
    
    swarm_attributes: Optional[SwarmAgent<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes] = Field(
        None,
        description="SwarmAgent-specific attributes"
    )
    
<% if (has_metrics) { %>    metrics: Optional[<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Metrics] = Field(
        None,
        description="Metrics data"
    )
<% } %>    
    resource_attributes: <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>ResourceAttributes = Field(
        default_factory=<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>ResourceAttributes,
        description="Resource-level attributes"
    )
    
    def to_complete_otel_context(self) -> Dict[str, Any]:
        """Generate complete OpenTelemetry context.
        
        Returns:
            Dictionary with all telemetry context
        """
        context = {
            "span_attributes": self.span_attributes.to_otel_attributes(),
            "resource_attributes": self.resource_attributes.to_otel_resource()
        }
        
        if self.swarm_attributes:
            context["swarm_attributes"] = self.swarm_attributes.to_otel_attributes()
        
<% if (has_metrics) { %>        if self.metrics:
            context["metrics"] = self.metrics.to_metric_data()
<% } %>        
        return context


# Convenience functions
def create_<%= domain.toLowerCase() %>_span_attributes(
    operation_name: str,
<% attributes.forEach(function(attr) { %>    <%= attr %>: Optional[str] = None,
<% }); %>    **kwargs
) -> <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes:
    """Create <%= domain.toLowerCase() %> span attributes with validation.
    
    Args:
        operation_name: Name of the operation
<% attributes.forEach(function(attr) { %>        <%= attr %>: <%= attr.charAt(0).toUpperCase() + attr.slice(1).replace(/_/g, ' ') %>
<% }); %>        **kwargs: Additional attributes
        
    Returns:
        Validated span attributes
    """
    return <%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes(
        operation_name=operation_name,
<% attributes.forEach(function(attr) { %>        <%= attr %>=<%= attr %>,
<% }); %>        **kwargs
    )


def create_swarm_<%= domain.toLowerCase() %>_context(
    agent_name: str,
    operation_name: str,
    service_name: str,
    **kwargs
) -> Complete<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Context:
    """Create complete SwarmAgent <%= domain.toLowerCase() %> context.
    
    Args:
        agent_name: Name of the SwarmAgent
        operation_name: Name of the operation
        service_name: Name of the service
        **kwargs: Additional context attributes
        
    Returns:
        Complete telemetry context
    """
    return Complete<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Context(
        span_attributes=<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes(
            operation_name=operation_name,
            **{k: v for k, v in kwargs.items() if k in ['<%= attributes.join("', '") %>']}
        ),
        swarm_attributes=SwarmAgent<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes(
            agent_name=agent_name,
            **{k: v for k, v in kwargs.items() if k in ['agent_state', 'trigger_name', 'workflow_id', 'coordination_step']}
        ),
        resource_attributes=<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>ResourceAttributes(
            service_name=service_name,
            **{k: v for k, v in kwargs.items() if k in ['service_version', 'service_instance_id']}
        )
    )


# Export all models
__all__ = [
    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanKind",
    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>OperationResult",
    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes",
    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>SpanAttributes",
    "SwarmAgent<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Attributes",
<% if (has_metrics) { %>    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Metrics",<% } %>
<% if (has_events) { %>    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Event",<% } %>
    "<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>ResourceAttributes",
    "Complete<%= domain.charAt(0).toUpperCase() + domain.slice(1) %>Context",
    "create_<%= domain.toLowerCase() %>_span_attributes",
    "create_swarm_<%= domain.toLowerCase() %>_context"
]