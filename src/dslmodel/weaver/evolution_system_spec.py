#!/usr/bin/env python3
"""
Evolution System Semantic Conventions
=====================================

Defines semantic conventions for the DSLModel automatic evolution system
using the proper Weaver Forge format with ConventionSet, Span, and Attribute objects.
"""

from dslmodel.weaver import ConventionSet, Span, Attribute
from dslmodel.weaver.enums import AttrType, Cardinality, SpanKind


def get_convention_sets() -> list[ConventionSet]:
    """Entry-point called by Weaver Forge loader."""
    return [
        ConventionSet(
            title="Evolution System Telemetry",
            version="0.1.0",
            spans=[
                # Analysis Phase
                Span(
                    name="dslmodel.evolution.analyze",
                    brief="Evolution system analysis phase - detecting improvement opportunities",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.analysis_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of analysis being performed (test_failures, performance_metrics, code_quality, full_analysis)",
                        ),
                        Attribute(
                            name="evolution.issues_found",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of issues discovered during analysis",
                        ),
                        Attribute(
                            name="evolution.analysis_duration_ms",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Duration of analysis phase in milliseconds",
                        ),
                        Attribute(
                            name="evolution.repository_path",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="Path to the repository being analyzed",
                        ),
                    ]
                ),
                
                # Generation Phase
                Span(
                    name="dslmodel.evolution.generate",
                    brief="Evolution improvement generation - creating improvement recommendations",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.improvement_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the generated improvement",
                        ),
                        Attribute(
                            name="evolution.improvement_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of improvement (performance_optimization, code_fix, refactoring, security_fix, dependency_update)",
                        ),
                        Attribute(
                            name="evolution.confidence_score",
                            type=AttrType.double,
                            cardinality=Cardinality.required,
                            description="Confidence score for the improvement (0.0 to 1.0)",
                        ),
                        Attribute(
                            name="evolution.estimated_effort_hours",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Estimated effort to implement the improvement in hours",
                        ),
                        Attribute(
                            name="evolution.priority",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Priority level (critical, high, medium, low)",
                        ),
                        Attribute(
                            name="evolution.target_files",
                            type=AttrType.string_array,
                            cardinality=Cardinality.optional,
                            description="Files that would be affected by this improvement",
                        ),
                    ]
                ),
                
                # Application Phase
                Span(
                    name="dslmodel.evolution.apply",
                    brief="Evolution improvement application - implementing improvements",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.improvement_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the applied improvement",
                        ),
                        Attribute(
                            name="evolution.application_mode",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Mode of improvement application (automatic, manual, dry_run, assisted)",
                        ),
                        Attribute(
                            name="evolution.application_result",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Result of the improvement application (success, failed, partial, skipped)",
                        ),
                        Attribute(
                            name="evolution.files_modified",
                            type=AttrType.string_array,
                            cardinality=Cardinality.optional,
                            description="List of files modified during improvement application",
                        ),
                        Attribute(
                            name="evolution.application_duration_ms",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Duration of improvement application in milliseconds",
                        ),
                        Attribute(
                            name="evolution.worktree_path",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="Path to worktree used for isolated testing",
                        ),
                    ]
                ),
                
                # Learning Phase
                Span(
                    name="dslmodel.evolution.learn",
                    brief="Evolution system learning phase - updating patterns from historical data",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.patterns_analyzed",
                            type=AttrType.int,
                            cardinality=Cardinality.required,
                            description="Number of historical patterns analyzed",
                        ),
                        Attribute(
                            name="evolution.success_rate",
                            type=AttrType.double,
                            cardinality=Cardinality.required,
                            description="Overall success rate from historical data (0.0 to 1.0)",
                        ),
                        Attribute(
                            name="evolution.patterns_updated",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Number of improvement patterns updated based on learning",
                        ),
                        Attribute(
                            name="evolution.confidence_adjustments",
                            type=AttrType.int,
                            cardinality=Cardinality.optional,
                            description="Number of confidence score adjustments made",
                        ),
                        Attribute(
                            name="evolution.learning_model_version",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="Version of the learning model used",
                        ),
                    ]
                ),
                
                # Validation Phase
                Span(
                    name="dslmodel.evolution.validate",
                    brief="Evolution improvement validation - verifying improvement effectiveness",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.improvement_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the validated improvement",
                        ),
                        Attribute(
                            name="evolution.validation_type",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Type of validation (test_execution, performance_benchmark, security_scan, integration_test, user_acceptance)",
                        ),
                        Attribute(
                            name="evolution.validation_result",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Result of the validation (passed, failed, warning, inconclusive)",
                        ),
                        Attribute(
                            name="evolution.metrics_before",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="JSON string of metrics before improvement",
                        ),
                        Attribute(
                            name="evolution.metrics_after",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="JSON string of metrics after improvement",
                        ),
                        Attribute(
                            name="evolution.performance_improvement",
                            type=AttrType.double,
                            cardinality=Cardinality.optional,
                            description="Percentage improvement in performance (e.g., 0.25 for 25% improvement)",
                        ),
                    ]
                ),
                
                # Worktree Coordination
                Span(
                    name="dslmodel.evolution.worktree",
                    brief="Evolution worktree coordination - managing isolated testing environments",
                    kind=SpanKind.internal,
                    attributes=[
                        Attribute(
                            name="evolution.session_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the evolution session",
                        ),
                        Attribute(
                            name="evolution.worktree_id",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Unique identifier for the worktree",
                        ),
                        Attribute(
                            name="evolution.worktree_action",
                            type=AttrType.string,
                            cardinality=Cardinality.required,
                            description="Worktree action (create, test, validate, cleanup, merge)",
                        ),
                        Attribute(
                            name="evolution.branch_name",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="Git branch name for the worktree",
                        ),
                        Attribute(
                            name="evolution.test_results",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="JSON string of test execution results",
                        ),
                        Attribute(
                            name="evolution.isolation_level",
                            type=AttrType.string,
                            cardinality=Cardinality.optional,
                            description="Level of isolation (full, partial, none)",
                        ),
                    ]
                ),
            ],
        )
    ]


if __name__ == "__main__":
    # Test the convention sets
    convention_sets = get_convention_sets()
    print(f"Evolution System Convention Sets: {len(convention_sets)}")
    
    for conv_set in convention_sets:
        print(f"\nConvention Set: {conv_set.title} v{conv_set.version}")
        print(f"Spans: {len(conv_set.spans)}")
        
        for span in conv_set.spans:
            print(f"  - {span.name}: {len(span.attributes)} attributes")
        
        # Test YAML generation
        yaml_output = conv_set.to_yaml_groups()
        print(f"\nGenerated YAML length: {len(yaml_output)} characters")