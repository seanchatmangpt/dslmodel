"""Pydantic models for swarm agents."""

from enum import Enum, auto
from typing import Dict, List, Optional, Any
from pydantic import Field

from dslmodel.agent_model import AgentModel


class SwarmState(str, Enum):
    """Base states for swarm agents."""
    INIT = "init"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class NextCommand(AgentModel):
    """Model for CLI commands that agents can execute."""
    path: List[str] = Field(default=None, description="Command path (e.g., ['work', 'list'])")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    description: Optional[str] = Field(None, description="Command description")
    fq_name: Optional[str] = Field(None, description="Fully qualified command name (alternative to path)")


class SpanData(AgentModel):
    """OpenTelemetry span data model."""
    name: str = Field(..., description="Span name")
    trace_id: str = Field(..., description="Trace ID")
    span_id: str = Field(..., description="Span ID")
    parent_span_id: Optional[str] = Field(None, description="Parent span ID")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Span attributes")
    timestamp: float = Field(..., description="Timestamp")
    duration_ms: Optional[float] = Field(None, description="Duration in milliseconds")


class SwarmAgentModel(AgentModel):
    """Base model for swarm agents."""
    name: str = Field(..., description="Agent name")
    state: str = Field(default=SwarmState.INIT, description="Current agent state")
    trigger_map: Dict[str, str] = Field(default_factory=dict, description="Mapping of triggers to handler methods")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Agent metadata")