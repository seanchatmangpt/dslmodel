"""
Autonomous Decision Engine - Telemetry Span Definitions (Standalone)
Each autonomous decision and system state change creates telemetry spans.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AttrType(str, Enum):
    """Attribute types supported by OpenTelemetry."""
    string = "string"
    int = "int"
    double = "double"
    boolean = "boolean"
    string_array = "string[]"


class Cardinality(str, Enum):
    """Requirement levels for attributes."""
    required = "required"
    recommended = "recommended"
    optional = "opt_in"


class SpanKind(str, Enum):
    """OpenTelemetry span kinds."""
    internal = "internal"
    server = "server"
    client = "client"


@dataclass
class Attribute:
    """Represents an attribute in a semantic convention."""
    name: str
    type: AttrType
    description: str
    cardinality: Cardinality = Cardinality.optional
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML generation."""
        return {
            "id": self.name,
            "type": self.type.value,
            "brief": self.description,
            "requirement_level": self.cardinality.value,
        }


@dataclass
class Span:
    """Represents a span definition in a semantic convention."""
    name: str
    brief: str
    kind: SpanKind = SpanKind.internal
    attributes: List[Attribute] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML generation."""
        result = {
            "id": self.name,
            "brief": self.brief,
            "type": "span",
            "span_kind": self.kind.value,
        }
        
        # Extract prefix from name
        parts = self.name.split(".")
        if len(parts) > 1:
            result["prefix"] = ".".join(parts[:-1])
                
        if self.attributes:
            result["attributes"] = [attr.to_dict() for attr in self.attributes]
            
        return result


@dataclass 
class ConventionSet:
    """Represents a set of semantic conventions."""
    title: str
    version: str
    spans: List[Span] = field(default_factory=list)
    
    def to_yaml_groups(self) -> List[Dict[str, Any]]:
        """Convert to YAML groups format expected by Weaver."""
        groups = []
        
        # Add span groups
        for span in self.spans:
            groups.append(span.to_dict())
            
        return groups


def get_convention_sets() -> List[ConventionSet]:
    """Autonomous decision engine telemetry conventions."""
    return [
        ConventionSet(
            title="Autonomous Decision Engine",
            version="0.1.0",
            spans=[
                Span(
                    name="swarmsh.autonomous.system_analysis",
                    brief="System state analysis and metric calculation",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="completion_rate",
                            type=AttrType.double,
                            cardinality=Cardinality.required,
                            description="Work completion rate (0.0-1.0)",
                        ),
                        Attribute(
                            name="active_agents",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of active agents",
                        ),
                        Attribute(
                            name="work_queue_size",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Size of work queue",
                        ),
                        Attribute(
                            name="health_score",
                            type=AttrType.double,
                            cardinality=Cardinality.required,
                            description="Overall system health score (0.0-1.0)",
                        ),
                        Attribute(
                            name="health_state",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="System health state (critical, degraded, healthy, optimal)",
                        ),
                    ]
                ),
                Span(
                    name="swarmsh.autonomous.decision_generation",
                    brief="Autonomous decision generation based on system state",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="decision_count",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of decisions generated",
                        ),
                        Attribute(
                            name="highest_priority",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Priority of highest priority decision",
                        ),
                        Attribute(
                            name="decision_types",
                            type=AttrType.string_array,
                            cardinality=Cardinality.recommended,
                            description="Types of decisions generated",
                        ),
                    ]
                ),
                Span(
                    name="swarmsh.autonomous.decision_execution",
                    brief="Execution of autonomous decisions",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="decision_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique decision identifier",
                        ),
                        Attribute(
                            name="decision_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of decision being executed",
                        ),
                        Attribute(
                            name="execution_result",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Result of decision execution",
                        ),
                        Attribute(
                            name="confidence",
                            type=AttrType.double,
                            cardinality=Cardinality.recommended,
                            description="Decision confidence score",
                        ),
                    ]
                ),
                Span(
                    name="swarmsh.autonomous.cycle_complete",
                    brief="Complete autonomous decision cycle",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="cycle_duration_ms",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Duration of complete cycle in milliseconds",
                        ),
                        Attribute(
                            name="decisions_executed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of decisions executed",
                        ),
                        Attribute(
                            name="decisions_failed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of decisions that failed",
                        ),
                        Attribute(
                            name="system_improvement",
                            type=AttrType.boolean,
                            cardinality=Cardinality.recommended,
                            description="Whether system improvement was achieved",
                        ),
                    ]
                ),
                Span(
                    name="swarmsh.autonomous.scaling_decision",
                    brief="Agent scaling decision (up or down)",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="scaling_direction",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Scaling direction (up, down)",
                        ),
                        Attribute(
                            name="current_agents",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Current number of agents",
                        ),
                        Attribute(
                            name="target_agents",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Target number of agents",
                        ),
                        Attribute(
                            name="trigger_reason",
                            type=AttrType.string,
                            cardinality=Cardinality.recommended,
                            description="Reason for scaling decision",
                        ),
                    ]
                ),
                Span(
                    name="swarmsh.autonomous.coordination_improvement",
                    brief="Coordination system improvement action",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="improvement_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of coordination improvement",
                        ),
                        Attribute(
                            name="queue_size_before",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Work queue size before improvement",
                        ),
                        Attribute(
                            name="queue_size_after",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Work queue size after improvement",
                        ),
                    ]
                ),
            ],
        )
    ]