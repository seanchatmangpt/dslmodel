"""
E2E Automation Specification - Weaver Forge Feature Development
Automatically generates complete features from telemetry specifications.
"""

from typing import List
from .models import ConventionSet, Span, Attribute, AttrType, Cardinality, SpanKind


def get_convention_sets() -> List[ConventionSet]:
    """E2E automation conventions for feature development."""
    return [
        ConventionSet(
            title="E2E Feature Automation",
            version="0.1.0",
            spans=[
                # Feature Planning Phase
                Span(
                    name="swarmsh.e2e.feature_planning",
                    brief="Automated feature planning from telemetry specs",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="feature_name",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Name of the feature being generated",
                        ),
                        Attribute(
                            name="spec_source",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Source telemetry specification module",
                        ),
                        Attribute(
                            name="generated_components",
                            type=AttrType.string_array,
                            cardinality=Cardinality.recommended,
                            description="List of components to be generated",
                        ),
                        Attribute(
                            name="planning_duration_ms",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Time taken for planning phase",
                        ),
                    ]
                ),
                
                # Code Generation Phase
                Span(
                    name="swarmsh.e2e.code_generation",
                    brief="Automatic code generation from telemetry",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="generation_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of code being generated (cli, api, model, test)",
                        ),
                        Attribute(
                            name="target_file",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Target file path for generated code",
                        ),
                        Attribute(
                            name="spans_implemented",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Number of telemetry spans implemented",
                        ),
                        Attribute(
                            name="model_used",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="LLM model used for generation",
                        ),
                    ]
                ),
                
                # Validation Phase
                Span(
                    name="swarmsh.e2e.validation",
                    brief="Validation of generated feature implementation",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="validation_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of validation (syntax, semantic, telemetry)",
                        ),
                        Attribute(
                            name="validation_result",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Result of validation (passed, failed, warnings)",
                        ),
                        Attribute(
                            name="errors",
                            type=AttrType.string_array,
                            cardinality=Cardinality.optional,
                            description="List of validation errors if any",
                        ),
                        Attribute(
                            name="otel_compliant",
                            type=AttrType.boolean,
                            cardinality=Cardinality.recommended,
                            description="Whether generated code is OTEL compliant",
                        ),
                    ]
                ),
                
                # Integration Phase
                Span(
                    name="swarmsh.e2e.integration",
                    brief="Integration of generated feature into codebase",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="integration_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of integration (cli, api, module)",
                        ),
                        Attribute(
                            name="files_modified",
                            type=AttrType.int,
                            cardinality=Cardinality.recommended,
                            description="Number of files modified during integration",
                        ),
                        Attribute(
                            name="tests_added",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Number of tests added",
                        ),
                        Attribute(
                            name="documentation_updated",
                            type=AttrType.boolean,
                            cardinality=Cardinality.optional,
                            description="Whether documentation was updated",
                        ),
                    ]
                ),
                
                # Testing Phase
                Span(
                    name="swarmsh.e2e.testing",
                    brief="Automated testing of generated feature",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="test_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of test (unit, integration, e2e)",
                        ),
                        Attribute(
                            name="tests_passed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of tests that passed",
                        ),
                        Attribute(
                            name="tests_failed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of tests that failed",
                        ),
                        Attribute(
                            name="coverage_percent",
                            type=AttrType.double,
                            cardinality=Cardinality.optional,
                            description="Code coverage percentage",
                        ),
                    ]
                ),
                
                # Deployment Phase
                Span(
                    name="swarmsh.e2e.deployment",
                    brief="Feature deployment and activation",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="deployment_status",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Status of deployment (success, failed, partial)",
                        ),
                        Attribute(
                            name="feature_enabled",
                            type=AttrType.boolean,
                            cardinality=Cardinality.required,
                            description="Whether feature is enabled after deployment",
                        ),
                        Attribute(
                            name="telemetry_active",
                            type=AttrType.boolean,
                            cardinality=Cardinality.required,
                            description="Whether telemetry is being emitted",
                        ),
                        Attribute(
                            name="rollback_available",
                            type=AttrType.boolean,
                            cardinality=Cardinality.optional,
                            description="Whether rollback is available",
                        ),
                    ]
                ),
                
                # Complete E2E Cycle
                Span(
                    name="swarmsh.e2e.complete_cycle",
                    brief="Complete E2E feature development cycle",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="feature_name",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Name of the completed feature",
                        ),
                        Attribute(
                            name="total_duration_ms",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Total time for E2E cycle",
                        ),
                        Attribute(
                            name="phases_completed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of phases completed successfully",
                        ),
                        Attribute(
                            name="automation_success",
                            type=AttrType.boolean,
                            cardinality=Cardinality.required,
                            description="Whether E2E automation succeeded",
                        ),
                        Attribute(
                            name="human_intervention_required",
                            type=AttrType.boolean,
                            cardinality=Cardinality.optional,
                            description="Whether human intervention was needed",
                        ),
                    ]
                ),
            ],
        )
    ]