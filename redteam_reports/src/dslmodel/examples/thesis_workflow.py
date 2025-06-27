"""
thesis_workflow.py
───────────────────────────────────────────────────────────────────────────────
Advanced SwarmSH thesis workflow using DSLModel's workflow system
• Demonstrates AI-powered thesis extension
• Shows workflow-based thesis validation
• Integrates with OTEL generation pipeline
"""

from typing import List, Optional
from pydantic import Field

from dslmodel import DSLModel, init_instant
from dslmodel.workflow import Workflow, Job, Action, Condition, ScheduleType

from thesis_complete import (
    ThesisComplete, SpanSpec, InversionPair, 
    TRIZMap, FeedbackLoopStep, FeedbackLoopPhase
)


class ThesisExtension(DSLModel):
    """Extension point for AI-generated thesis additions"""
    category: str = Field(..., description="Category: span_claim, inversion, triz_mapping")
    prompt: str = Field(..., description="Prompt for generating new thesis element")
    context: Optional[str] = Field(None, description="Additional context for generation")
    

class ThesisValidation(DSLModel):
    """Validation result for thesis completeness"""
    is_complete: bool = Field(..., description="Whether thesis meets all criteria")
    missing_elements: List[str] = Field(default_factory=list, description="Missing elements")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class ThesisWorkflowConfig(DSLModel):
    """Configuration for thesis generation and validation workflow"""
    
    thesis_path: str = Field("thesis_complete.json", description="Path to save thesis")
    generate_otel: bool = Field(True, description="Generate OTEL semantic conventions")
    generate_rust: bool = Field(True, description="Generate Rust code")
    validate_completeness: bool = Field(True, description="Run completeness validation")
    ai_extend: bool = Field(False, description="Use AI to suggest extensions")
    extensions: List[ThesisExtension] = Field(
        default_factory=list,
        description="AI extension prompts"
    )


def create_thesis_workflow() -> Workflow:
    """Create a workflow for thesis generation, extension, and validation"""
    
    workflow = Workflow(
        name="swarmsh_thesis_pipeline",
        description="Complete thesis generation and validation pipeline",
        
        # Global context available to all jobs
        context={
            "thesis_version": "1.0.0",
            "output_dir": "./thesis_output"
        },
        
        jobs=[
            Job(
                name="generate_thesis",
                description="Generate the base thesis bundle",
                actions=[
                    Action(
                        name="create_thesis",
                        type="code",
                        code="""
from thesis_complete import ThesisComplete
thesis = ThesisComplete.create_default_thesis()
thesis.to_json(file_path=context.get('output_dir') + '/thesis.json')
thesis.to_yaml(file_path=context.get('output_dir') + '/thesis.yaml')
print(f"Generated thesis with {len(thesis.span_claims)} claims")
""",
                        description="Create and save thesis bundle"
                    )
                ]
            ),
            
            Job(
                name="generate_artifacts",
                description="Generate OTEL and Rust artifacts",
                depends_on=["generate_thesis"],
                actions=[
                    Action(
                        name="generate_otel",
                        type="code",
                        code="""
from thesis_complete import ThesisComplete
thesis = ThesisComplete.from_json(file_path=context.get('output_dir') + '/thesis.json')
otel_yaml = thesis.generate_otel_yaml()
with open(context.get('output_dir') + '/thesis_semconv.yaml', 'w') as f:
    f.write(otel_yaml)
print("Generated OTEL semantic conventions")
""",
                        description="Generate OTEL YAML"
                    ),
                    Action(
                        name="generate_rust",
                        type="code", 
                        code="""
from thesis_complete import ThesisComplete
thesis = ThesisComplete.from_json(file_path=context.get('output_dir') + '/thesis.json')
rust_code = thesis.generate_forge_rust()
with open(context.get('output_dir') + '/thesis_spans.rs', 'w') as f:
    f.write(rust_code)
print("Generated Rust span code")
""",
                        description="Generate Rust implementation"
                    )
                ],
                conditions=[
                    Condition(
                        name="check_generation_enabled",
                        expression="config.generate_otel or config.generate_rust",
                        description="Only run if artifact generation is enabled"
                    )
                ]
            ),
            
            Job(
                name="validate_thesis",
                description="Validate thesis completeness",
                depends_on=["generate_thesis"],
                actions=[
                    Action(
                        name="validate_completeness",
                        type="code",
                        code="""
from thesis_complete import ThesisComplete

thesis = ThesisComplete.from_json(file_path=context.get('output_dir') + '/thesis.json')

# Validation logic
validation = {
    'is_complete': True,
    'missing_elements': [],
    'suggestions': []
}

# Check minimum requirements
if len(thesis.span_claims) < 5:
    validation['missing_elements'].append(f"Need at least 5 span claims (have {len(thesis.span_claims)})")
    validation['is_complete'] = False

if len(thesis.inversion_matrix) < 5:
    validation['missing_elements'].append(f"Need at least 5 inversions (have {len(thesis.inversion_matrix)})")
    validation['is_complete'] = False
    
if len(thesis.triz_mapping) < 10:
    validation['missing_elements'].append(f"Need at least 10 TRIZ mappings (have {len(thesis.triz_mapping)})")
    validation['is_complete'] = False

# Check feedback loop
if len(thesis.auto_triz_feedback_loop) != 5:
    validation['missing_elements'].append("Feedback loop must have exactly 5 phases")
    validation['is_complete'] = False

# Suggestions
if len(thesis.triz_mapping) < 20:
    validation['suggestions'].append(f"Consider mapping more TRIZ principles (currently {len(thesis.triz_mapping)}/40)")

print(f"Validation complete: {'PASS' if validation['is_complete'] else 'FAIL'}")
for missing in validation['missing_elements']:
    print(f"  Missing: {missing}")
for suggestion in validation['suggestions']:
    print(f"  Suggestion: {suggestion}")
""",
                        description="Validate thesis meets all requirements"
                    )
                ]
            ),
            
            Job(
                name="ai_extend_thesis",
                description="Use AI to suggest thesis extensions",
                depends_on=["validate_thesis"],
                actions=[
                    Action(
                        name="generate_extensions",
                        type="code",
                        code="""
# This would use DSLModel's AI capabilities
# Placeholder for demonstration
print("AI extension requires init_instant() or init_lm()")
print("Example extensions that could be generated:")
print("- New span claim: swarmsh.thesis.adaptive_governance")
print("- New inversion: Traditional: Static rules | SwarmSH: Dynamic span-based rules")
print("- New TRIZ mapping: Principle 17 (Another Dimension) -> Multi-dimensional trace analysis")
""",
                        description="Generate AI-powered extensions"
                    )
                ],
                conditions=[
                    Condition(
                        name="check_ai_enabled",
                        expression="config.ai_extend",
                        description="Only run if AI extension is enabled"
                    )
                ]
            )
        ],
        
        schedule=ScheduleType.NONE  # Run on demand
    )
    
    return workflow


class ThesisGenerator(DSLModel):
    """High-level thesis generator using DSLModel patterns"""
    
    config: ThesisWorkflowConfig = Field(
        default_factory=ThesisWorkflowConfig,
        description="Workflow configuration"
    )
    
    workflow: Optional[Workflow] = Field(None, description="Generated workflow")
    
    def generate(self) -> ThesisComplete:
        """Generate thesis using configured workflow"""
        # For simple generation without workflow
        thesis = ThesisComplete.create_default_thesis()
        
        if self.config.generate_otel:
            otel_yaml = thesis.generate_otel_yaml()
            # Save or process OTEL YAML
            
        if self.config.generate_rust:
            rust_code = thesis.generate_forge_rust()
            # Save or process Rust code
            
        return thesis
    
    @classmethod
    def from_extensions(cls, extensions: List[ThesisExtension]) -> 'ThesisGenerator':
        """Create generator with AI extensions"""
        config = ThesisWorkflowConfig(
            ai_extend=True,
            extensions=extensions
        )
        return cls(config=config)


# Example: Using AI to extend thesis
def demo_ai_extension():
    """Demo of using AI to extend the thesis"""
    
    # This would work with init_instant() enabled
    extensions = [
        ThesisExtension(
            category="span_claim",
            prompt="Create a span claim about distributed consensus through traces",
            context="Focus on how agents achieve consensus without explicit coordination"
        ),
        ThesisExtension(
            category="triz_mapping", 
            prompt="Map TRIZ principle 'Asymmetry' to SwarmSH architecture",
            context="Consider how SwarmSH uses asymmetric agent roles"
        )
    ]
    
    generator = ThesisGenerator.from_extensions(extensions)
    thesis = generator.generate()
    
    return thesis


if __name__ == "__main__":
    # Create workflow
    workflow = create_thesis_workflow()
    
    # Save workflow definition
    workflow.to_yaml(file_path="thesis_workflow.yaml")
    
    # Simple generation
    generator = ThesisGenerator()
    thesis = generator.generate()
    print(f"Generated thesis with {len(thesis.span_claims)} claims")