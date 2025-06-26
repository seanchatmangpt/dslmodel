#!/usr/bin/env python3
"""
Agent Coordination Telemetry Specification

Defines OpenTelemetry semantic conventions for agent coordination using worktrees.
This specification enables agents to communicate and coordinate through telemetry spans.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

# Import Weaver types for semantic convention generation
try:
    from weaver.schema.semantic_convention import SemanticConventionSet, SemanticConvention, Attribute
    from weaver.schema.attribute import AttrType, Cardinality
    WEAVER_AVAILABLE = True
except ImportError:
    # Fallback types for when Weaver isn't available
    WEAVER_AVAILABLE = False
    
    class AttrType(Enum):
        string = "string"
        int = "int"
        double = "double"
        boolean = "boolean"
        string_array = "string[]"
    
    class Cardinality(Enum):
        required = "required"
        recommended = "recommended"
        optional = "optional"
    
    @dataclass
    class Attribute:
        name: str
        type: AttrType
        cardinality: Cardinality
        description: str
        examples: Optional[List[str]] = None
    
    @dataclass 
    class SemanticConvention:
        name: str
        brief: str
        attributes: List[Attribute]
        description: Optional[str] = None
    
    @dataclass
    class SemanticConventionSet:
        title: str
        version: str
        conventions: List[SemanticConvention]


def get_agent_coordination_conventions() -> SemanticConventionSet:
    """Get semantic conventions for agent coordination telemetry"""
    
    return SemanticConventionSet(
        title="Agent Coordination with Worktrees",
        version="1.0.0",
        conventions=[
            
            # Agent registration and lifecycle
            SemanticConvention(
                name="agent.registration",
                brief="Agent registration with coordinator",
                description="Tracks when agents register with the coordination system",
                attributes=[
                    Attribute(
                        name="agent.id",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Unique identifier for the agent",
                        examples=["agent-python-001", "agent-frontend-002"]
                    ),
                    Attribute(
                        name="agent.languages",
                        type=AttrType.string_array,
                        cardinality=Cardinality.recommended,
                        description="Programming languages the agent supports",
                        examples=["python,typescript", "rust,go"]
                    ),
                    Attribute(
                        name="agent.frameworks",
                        type=AttrType.string_array,
                        cardinality=Cardinality.recommended,
                        description="Frameworks the agent is proficient with",
                        examples=["fastapi,django", "react,vue"]
                    ),
                    Attribute(
                        name="agent.expertise_areas",
                        type=AttrType.string_array,
                        cardinality=Cardinality.recommended,
                        description="Areas of expertise for the agent",
                        examples=["backend,api", "frontend,ui"]
                    ),
                    Attribute(
                        name="agent.max_concurrent_features",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Maximum number of features agent can work on simultaneously",
                        examples=["1", "2", "3"]
                    ),
                    Attribute(
                        name="agent.preferred_complexity",
                        type=AttrType.string,
                        cardinality=Cardinality.optional,
                        description="Preferred complexity level for assignments",
                        examples=["low", "medium", "high"]
                    )
                ]
            ),
            
            # Feature assignment coordination
            SemanticConvention(
                name="agent.feature_assignment",
                brief="Feature assignment to agent",
                description="Tracks when features are assigned to agents for development",
                attributes=[
                    Attribute(
                        name="agent.id",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent receiving the assignment"
                    ),
                    Attribute(
                        name="feature.name",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Name of the assigned feature"
                    ),
                    Attribute(
                        name="feature.description",
                        type=AttrType.string,
                        cardinality=Cardinality.recommended,
                        description="Detailed description of the feature"
                    ),
                    Attribute(
                        name="feature.priority",
                        type=AttrType.string,
                        cardinality=Cardinality.recommended,
                        description="Priority level of the feature",
                        examples=["high", "medium", "low"]
                    ),
                    Attribute(
                        name="feature.estimated_effort",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Estimated effort in story points"
                    ),
                    Attribute(
                        name="assignment.match_score",
                        type=AttrType.double,
                        cardinality=Cardinality.optional,
                        description="How well the feature matches agent capabilities (0.0-1.0)"
                    ),
                    Attribute(
                        name="assignment.timestamp",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="ISO timestamp of assignment"
                    )
                ]
            ),
            
            # Worktree lifecycle management
            SemanticConvention(
                name="worktree.lifecycle",
                brief="Worktree creation and management",
                description="Tracks worktree creation, usage, and cleanup for agent isolation",
                attributes=[
                    Attribute(
                        name="worktree.path",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="File system path to the worktree"
                    ),
                    Attribute(
                        name="worktree.branch_name",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Git branch name for the worktree"
                    ),
                    Attribute(
                        name="worktree.base_branch",
                        type=AttrType.string,
                        cardinality=Cardinality.recommended,
                        description="Base branch the worktree was created from",
                        examples=["main", "develop", "staging"]
                    ),
                    Attribute(
                        name="worktree.status",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Current status of the worktree",
                        examples=["claimed", "in_progress", "validating", "ready_to_merge", "merged", "abandoned"]
                    ),
                    Attribute(
                        name="worktree.agent_id",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent currently using this worktree"
                    ),
                    Attribute(
                        name="worktree.feature_name",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Feature being developed in this worktree"
                    ),
                    Attribute(
                        name="worktree.creation_timestamp",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="ISO timestamp when worktree was created"
                    )
                ]
            ),
            
            # Agent work progress tracking
            SemanticConvention(
                name="agent.work_progress",
                brief="Agent work progress updates",
                description="Tracks agent progress on assigned features through worktree development",
                attributes=[
                    Attribute(
                        name="agent.id",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent reporting progress"
                    ),
                    Attribute(
                        name="agent.state",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Current state of the agent",
                        examples=["idle", "claiming", "working", "validating", "submitting", "finished", "error"]
                    ),
                    Attribute(
                        name="work.progress_percentage",
                        type=AttrType.double,
                        cardinality=Cardinality.optional,
                        description="Estimated progress completion (0.0-100.0)"
                    ),
                    Attribute(
                        name="work.files_modified",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Number of files modified in this work session"
                    ),
                    Attribute(
                        name="work.lines_added",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Lines of code added"
                    ),
                    Attribute(
                        name="work.lines_removed",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Lines of code removed"
                    ),
                    Attribute(
                        name="work.commit_count",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Number of commits made in this session"
                    ),
                    Attribute(
                        name="work.duration_ms",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Duration of work session in milliseconds"
                    )
                ]
            ),
            
            # Validation and quality assurance
            SemanticConvention(
                name="agent.validation",
                brief="Agent work validation",
                description="Tracks validation of agent work before submission",
                attributes=[
                    Attribute(
                        name="agent.id",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent whose work is being validated"
                    ),
                    Attribute(
                        name="validation.type",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Type of validation performed",
                        examples=["lint_check", "unit_tests", "integration_tests", "security_scan", "manual_review"]
                    ),
                    Attribute(
                        name="validation.result",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Result of validation",
                        examples=["passed", "failed", "warning", "skipped"]
                    ),
                    Attribute(
                        name="validation.issues_found",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Number of issues found during validation"
                    ),
                    Attribute(
                        name="validation.test_coverage",
                        type=AttrType.double,
                        cardinality=Cardinality.optional,
                        description="Test coverage percentage (0.0-100.0)"
                    ),
                    Attribute(
                        name="validation.execution_time_ms",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Time taken to run validation in milliseconds"
                    ),
                    Attribute(
                        name="validation.tools_used",
                        type=AttrType.string_array,
                        cardinality=Cardinality.optional,
                        description="Validation tools used",
                        examples=["pytest,black", "eslint,jest"]
                    )
                ]
            ),
            
            # Coordination system health
            SemanticConvention(
                name="coordination.system_health",
                brief="Overall coordination system health",
                description="Tracks health and performance of the agent coordination system",
                attributes=[
                    Attribute(
                        name="coordination.total_agents",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Total number of registered agents"
                    ),
                    Attribute(
                        name="coordination.active_agents",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Number of agents currently working"
                    ),
                    Attribute(
                        name="coordination.idle_agents",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Number of idle agents available for work"
                    ),
                    Attribute(
                        name="coordination.features_in_queue",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Number of features waiting for assignment"
                    ),
                    Attribute(
                        name="coordination.features_in_progress",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Number of features currently being developed"
                    ),
                    Attribute(
                        name="coordination.features_completed",
                        type=AttrType.int,
                        cardinality=Cardinality.required,
                        description="Total number of completed features"
                    ),
                    Attribute(
                        name="coordination.health_score",
                        type=AttrType.double,
                        cardinality=Cardinality.required,
                        description="Overall system health score (0.0-1.0)"
                    ),
                    Attribute(
                        name="coordination.avg_feature_completion_time_ms",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Average time to complete features in milliseconds"
                    ),
                    Attribute(
                        name="coordination.total_worktrees",
                        type=AttrType.int,
                        cardinality=Cardinality.recommended,
                        description="Total number of managed worktrees"
                    )
                ]
            ),
            
            # Inter-agent communication
            SemanticConvention(
                name="agent.communication",
                brief="Communication between agents",
                description="Tracks communication and coordination messages between agents",
                attributes=[
                    Attribute(
                        name="communication.from_agent",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent sending the communication"
                    ),
                    Attribute(
                        name="communication.to_agent",
                        type=AttrType.string,
                        cardinality=Cardinality.optional,
                        description="Target agent for communication (if direct message)"
                    ),
                    Attribute(
                        name="communication.message_type",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Type of communication message",
                        examples=["status_update", "request_help", "share_knowledge", "coordination_request", "error_report"]
                    ),
                    Attribute(
                        name="communication.channel",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Communication channel used",
                        examples=["telemetry_spans", "coordination_files", "direct_message", "broadcast"]
                    ),
                    Attribute(
                        name="communication.related_feature",
                        type=AttrType.string,
                        cardinality=Cardinality.optional,
                        description="Feature related to the communication"
                    ),
                    Attribute(
                        name="communication.urgency",
                        type=AttrType.string,
                        cardinality=Cardinality.optional,
                        description="Urgency level of the communication",
                        examples=["low", "medium", "high", "critical"]
                    ),
                    Attribute(
                        name="communication.response_required",
                        type=AttrType.boolean,
                        cardinality=Cardinality.optional,
                        description="Whether this communication requires a response"
                    )
                ]
            ),
            
            # Feature merge coordination
            SemanticConvention(
                name="coordination.feature_merge",
                brief="Feature merge coordination",
                description="Tracks coordination of feature merges and conflicts resolution",
                attributes=[
                    Attribute(
                        name="merge.source_branch",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Source branch being merged"
                    ),
                    Attribute(
                        name="merge.target_branch",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Target branch for the merge"
                    ),
                    Attribute(
                        name="merge.strategy",
                        type=AttrType.string,
                        cardinality=Cardinality.recommended,
                        description="Merge strategy used",
                        examples=["merge", "squash", "rebase"]
                    ),
                    Attribute(
                        name="merge.conflicts_detected",
                        type=AttrType.boolean,
                        cardinality=Cardinality.required,
                        description="Whether merge conflicts were detected"
                    ),
                    Attribute(
                        name="merge.conflicts_resolved",
                        type=AttrType.int,
                        cardinality=Cardinality.optional,
                        description="Number of conflicts resolved"
                    ),
                    Attribute(
                        name="merge.coordinating_agent",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Agent coordinating the merge"
                    ),
                    Attribute(
                        name="merge.feature_name",
                        type=AttrType.string,
                        cardinality=Cardinality.required,
                        description="Feature being merged"
                    ),
                    Attribute(
                        name="merge.pr_number",
                        type=AttrType.string,
                        cardinality=Cardinality.optional,
                        description="Pull request number if applicable"
                    ),
                    Attribute(
                        name="merge.success",
                        type=AttrType.boolean,
                        cardinality=Cardinality.required,
                        description="Whether the merge was successful"
                    )
                ]
            )
        ]
    )


def generate_weaver_registry():
    """Generate Weaver registry files for agent coordination"""
    conventions = get_agent_coordination_conventions()
    
    # This would be used by Weaver to generate actual semantic convention files
    # For now, we return the structure that can be used for telemetry generation
    return {
        "version": conventions.version,
        "title": conventions.title,
        "groups": [
            {
                "id": f"agent_coordination.{conv.name}",
                "type": "span",
                "brief": conv.brief,
                "note": conv.description,
                "attributes": [
                    {
                        "id": attr.name,
                        "type": attr.type.value,
                        "requirement_level": attr.cardinality.value,
                        "brief": attr.description,
                        "examples": attr.examples or []
                    }
                    for attr in conv.attributes
                ]
            }
            for conv in conventions.conventions
        ]
    }


if __name__ == "__main__":
    # Generate and display the semantic conventions
    import json
    registry = generate_weaver_registry()
    print(json.dumps(registry, indent=2))