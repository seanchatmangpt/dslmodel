"""
Autonomous Decision Engine - Telemetry Span Definitions
Each autonomous decision and system state change creates telemetry spans.
"""

from dslmodel.weaver import ConventionSet, Span, Attribute
from dslmodel.weaver.enums import AttrType, Cardinality, SpanKind


def get_convention_sets() -> list[ConventionSet]:
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