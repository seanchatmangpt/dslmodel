"""
AUTOGENERATED-FROM-THESIS
------------------------------------------------------------
Telemetry as the Foundation of Computation: The SwarmSH Inversion
Each semantic assertion is encoded as an OTEL span so that
Forge can produce CLI commands, docs, and shell templates.
"""

from dslmodel.weaver import ConventionSet, Span, Attribute
from dslmodel.weaver.enums import AttrType, Cardinality, SpanKind


def _span(name: str, brief: str) -> Span:
    """Factory to avoid repetition."""
    return Span(
        name=name,
        kind=SpanKind.internal,
        brief=brief,
        attributes=[
            Attribute(
                name="detail",
                type=AttrType.string,
                cardinality=Cardinality.recommended,
                description="Free-form note or JSON blob",
            )
        ],
    )


def get_convention_sets() -> list[ConventionSet]:
    """Entry-point called by Weaver Forge loader."""
    return [
        ConventionSet(
            title="Telemetry-Inversion Thesis",
            version="0.1.0",
            spans=[
                _span(
                    "swarmsh.thesis.telemetry_as_system",
                    "Telemetry is the foundational substrate of all behaviour.",
                ),
                _span(
                    "swarmsh.thesis.span_drives_code",
                    "Spans define code artifacts (CLI, shell, Rust).",
                ),
                _span(
                    "swarmsh.thesis.trace_to_prompt_emergence",
                    "Traces synthesize LLM prompts; prompts are not hand-written.",
                ),
                _span(
                    "swarmsh.thesis.telemetry_communication_channel",
                    "Spans serve as the inter-agent communication medium.",
                ),
                _span(
                    "swarmsh.thesis.belief_inversion",
                    "Matrix contrasting traditional assumptions with SwarmSH inversions.",
                ),
                _span(
                    "swarmsh.thesis.scaling_with_certainty",
                    "Auditability and convergence guarantees rooted in spans.",
                ),
                _span(
                    "swarmsh.thesis.system_models_itself",
                    "System trace is a live self-model accessible to humans and agents.",
                ),
            ],
        )
    ]