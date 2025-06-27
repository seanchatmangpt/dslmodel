"""
thesis_complete.py
───────────────────────────────────────────────────────────────────────────────
SwarmSH Thesis Complete Model using DSLModel
• Extends telemetry_inversion_spec.py with every remaining claim & mapping
• Provides machine-readable thesis artifacts using DSLModel patterns
• Integrates with DSLModel's AI generation and serialization capabilities
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pydantic import Field

from dslmodel import DSLModel, init_instant


class SpanSpec(DSLModel):
    """OpenTelemetry span specification for thesis claims"""
    name: str = Field(..., description="Span name following OTEL conventions")
    brief: str = Field(..., description="Brief description of what this span represents")
    attributes: Dict[str, str] = Field(
        default_factory=dict, 
        description="Additional span attributes as key-value pairs"
    )


class InversionPair(DSLModel):
    """Belief inversion pair contrasting traditional vs SwarmSH approaches"""
    traditional: str = Field(..., description="Traditional approach or belief")
    swarmsh: str = Field(..., description="SwarmSH inverted approach")


class TRIZMap(DSLModel):
    """TRIZ principle mapping to SwarmSH implementation"""
    principle: int = Field(..., description="TRIZ principle number (1-40)")
    name: str = Field(..., description="TRIZ principle name")
    swarmsh_mapping: str = Field(..., description="How SwarmSH implements this principle")


class FeedbackLoopPhase(str, Enum):
    """Phases in the auto-TRIZ feedback loop"""
    PERCEPTION = "telemetry_as_perception"
    RESOLUTION = "llm_resolves_contradiction"
    GENERATION = "weaverforge_generates"
    REALISATION = "wave_coordination_executes"
    VALIDATION = "telemetry_validates"


class FeedbackLoopStep(DSLModel):
    """Single step in the auto-TRIZ feedback loop"""
    phase: FeedbackLoopPhase = Field(..., description="Phase of the feedback loop")
    description: str = Field(..., description="What happens in this phase")


class ThesisComplete(DSLModel):
    """Complete SwarmSH thesis bundle with all claims, inversions, and mappings"""
    
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this bundle was generated"
    )
    
    span_claims: List[SpanSpec] = Field(
        ...,
        description="Core thesis claims as OTEL span specifications"
    )
    
    inversion_matrix: List[InversionPair] = Field(
        ...,
        description="Belief inversions contrasting traditional vs SwarmSH"
    )
    
    triz_mapping: List[TRIZMap] = Field(
        ...,
        description="TRIZ principles mapped to SwarmSH implementations"
    )
    
    auto_triz_feedback_loop: List[FeedbackLoopStep] = Field(
        ...,
        description="The 5-phase auto-TRIZ self-improvement loop"
    )
    
    @classmethod
    def create_default_thesis(cls) -> 'ThesisComplete':
        """Create the default thesis with all narrative content"""
        return cls(
            span_claims=[
                SpanSpec(
                    name="swarmsh.thesis.telemetry_as_system",
                    brief="Telemetry is the system, not an add-on."
                ),
                SpanSpec(
                    name="swarmsh.thesis.span_drives_code",
                    brief="Spans generate code & CLI."
                ),
                SpanSpec(
                    name="swarmsh.thesis.trace_to_prompt_emergence",
                    brief="Traces → LLM prompts (emergent)."
                ),
                SpanSpec(
                    name="swarmsh.thesis.telemetry_communication_channel",
                    brief="Spans are the agent messaging bus."
                ),
                SpanSpec(
                    name="swarmsh.thesis.system_models_itself",
                    brief="Trace graph is a live self-model."
                ),
            ],
            
            inversion_matrix=[
                InversionPair(
                    traditional="Telemetry is optional debugging aid",
                    swarmsh="Telemetry is the system"
                ),
                InversionPair(
                    traditional="Code drives behaviour",
                    swarmsh="Spans drive code"
                ),
                InversionPair(
                    traditional="Prompts are handcrafted",
                    swarmsh="Prompts emerge from spans"
                ),
                InversionPair(
                    traditional="Agents talk via explicit messages",
                    swarmsh="Agents talk via structured trace"
                ),
                InversionPair(
                    traditional="Governance added manually",
                    swarmsh="Governance encoded in spans"
                ),
                InversionPair(
                    traditional="Self-knowledge is external",
                    swarmsh="Trace graph is self-model"
                ),
            ],
            
            triz_mapping=[
                TRIZMap(
                    principle=1,
                    name="Segmentation",
                    swarmsh_mapping="Semantic conventions isolate atomic functions"
                ),
                TRIZMap(
                    principle=2,
                    name="Taking Out",
                    swarmsh_mapping="DLSS 80/20 extracts high-value features"
                ),
                TRIZMap(
                    principle=3,
                    name="Local Quality",
                    swarmsh_mapping="Role-specific agents & context-local spans"
                ),
                TRIZMap(
                    principle=5,
                    name="Merging",
                    swarmsh_mapping="OTEL + shell + Rust unified via code-gen"
                ),
                TRIZMap(
                    principle=10,
                    name="Preliminary Action",
                    swarmsh_mapping="Pre-emit spans before error points"
                ),
                TRIZMap(
                    principle=13,
                    name="The Other Way Around",
                    swarmsh_mapping="Start from telemetry → generate code"
                ),
                TRIZMap(
                    principle=15,
                    name="Dynamics",
                    swarmsh_mapping="Telemetry mutates execution plans (waves)"
                ),
                TRIZMap(
                    principle=24,
                    name="Intermediary",
                    swarmsh_mapping="Traces broker CLI ⇄ LLM ⇄ shell"
                ),
                TRIZMap(
                    principle=25,
                    name="Self-Service",
                    swarmsh_mapping="Agents trigger self-healing via span patterns"
                ),
                TRIZMap(
                    principle=28,
                    name="Mechanics Substitution",
                    swarmsh_mapping="Replace imperative logic with trace-based decisions"
                ),
                TRIZMap(
                    principle=35,
                    name="Parameter Change",
                    swarmsh_mapping="DLSS tunes conventions per load/context"
                ),
                TRIZMap(
                    principle=40,
                    name="Composite Materials",
                    swarmsh_mapping="Multi-layer CLI from WeaverForge (Rust+Shell+LLM)"
                ),
            ],
            
            auto_triz_feedback_loop=[
                FeedbackLoopStep(
                    phase=FeedbackLoopPhase.PERCEPTION,
                    description="Telemetry captures contradictions (conflicts, retries, slow spans)"
                ),
                FeedbackLoopStep(
                    phase=FeedbackLoopPhase.RESOLUTION,
                    description="LLM analyses span data and proposes semantic-spec patches"
                ),
                FeedbackLoopStep(
                    phase=FeedbackLoopPhase.GENERATION,
                    description="WeaverForge regenerates CLI & templates from updated specs"
                ),
                FeedbackLoopStep(
                    phase=FeedbackLoopPhase.REALISATION,
                    description="Wave coordination deploys changes across agents"
                ),
                FeedbackLoopStep(
                    phase=FeedbackLoopPhase.VALIDATION,
                    description="New spans confirm whether contradiction resolved; loop repeats"
                ),
            ]
        )
    
    def generate_otel_yaml(self) -> str:
        """Generate OTEL semantic convention YAML from span claims"""
        yaml_lines = [
            "groups:",
            "  - id: swarmsh.thesis",
            "    type: span",
            "    prefix: swarmsh.thesis",
            "    brief: 'SwarmSH thesis claims as telemetry'",
            "    attributes:"
        ]
        
        for i, span in enumerate(self.span_claims):
            attr_name = span.name.split('.')[-1]
            yaml_lines.extend([
                f"      - id: {attr_name}",
                f"        type: boolean",
                f"        brief: '{span.brief}'",
                f"        requirement_level: recommended"
            ])
        
        return '\n'.join(yaml_lines)
    
    def generate_forge_rust(self) -> str:
        """Generate Rust code for WeaverForge integration"""
        rust_lines = [
            "// Auto-generated from thesis_complete.py",
            "use opentelemetry::{trace::Tracer, KeyValue};",
            "",
            "pub fn emit_thesis_spans(tracer: &dyn Tracer) {",
        ]
        
        for span in self.span_claims:
            span_var = span.name.replace('.', '_')
            rust_lines.extend([
                f"    let {span_var} = tracer",
                f"        .span_builder(\"{span.name}\")",
                f"        .with_attributes(vec![",
                f"            KeyValue::new(\"brief\", \"{span.brief}\"),",
                f"        ])",
                f"        .start(tracer);",
                f"    {span_var}.end();",
                ""
            ])
        
        rust_lines.append("}")
        return '\n'.join(rust_lines)


# Example usage functions
def demo_thesis_usage():
    """Demonstrate various ways to use the thesis model"""
    
    # Create default thesis
    thesis = ThesisComplete.create_default_thesis()
    
    # Save to various formats
    thesis.to_json(file_path="thesis.json")
    thesis.to_yaml(file_path="thesis.yaml")
    
    # Generate OTEL conventions
    otel_yaml = thesis.generate_otel_yaml()
    with open("thesis_semconv.yaml", "w") as f:
        f.write(otel_yaml)
    
    # Generate Rust code
    rust_code = thesis.generate_forge_rust()
    with open("thesis_spans.rs", "w") as f:
        f.write(rust_code)
    
    # Access specific data
    print(f"Total thesis claims: {len(thesis.span_claims)}")
    print(f"TRIZ principles covered: {len(thesis.triz_mapping)}")
    print(f"Feedback loop phases: {len(thesis.auto_triz_feedback_loop)}")
    
    # AI-powered extension (requires init_instant() or init_lm())
    # new_claim = SpanSpec.from_prompt(
    #     "Create a span spec for: System automatically scales based on trace patterns"
    # )
    # thesis.span_claims.append(new_claim)


if __name__ == "__main__":
    # Create and save the default thesis
    thesis = ThesisComplete.create_default_thesis()
    
    # Output JSON to stdout (compatible with original usage)
    print(thesis.to_json())
    
    # Also save to file for convenience
    thesis.to_json(file_path="thesis_dslmodel.json")
    thesis.to_yaml(file_path="thesis_dslmodel.yaml")