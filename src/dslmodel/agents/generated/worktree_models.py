#!/usr/bin/env python3
"""
Agent Worktree Models - Generated from Semantic Conventions
Auto-generated from semantic conventions using weaver forge approach
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Initialize tracer
tracer = trace.get_tracer(__name__)

@dataclass
class AgentWorktreeCreateSpan:
    """Create isolated agent worktree for feature development"""
    
    # Creates git worktree for agent to work in isolation
    
    # Span attributes
    agent_id: str
    worktree_path: str
    feature_id: str
    branch_name: str
    worktree_startup_duration_ms: float = None
    
    # Span metadata
    span_name: str = "agent.worktree.create"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.worktree_path is not None:
            span.set_attribute("worktree.path", self.worktree_path)
        if self.feature_id is not None:
            span.set_attribute("feature.id", self.feature_id)
        if self.branch_name is not None:
            span.set_attribute("branch.name", self.branch_name)
        if self.worktree_startup_duration_ms is not None:
            span.set_attribute("worktree.startup.duration_ms", self.worktree_startup_duration_ms)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentWorktreeCreateSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "worktree_path" in kwargs:
            valid_attrs["worktree_path"] = kwargs["worktree_path"]
        if "feature_id" in kwargs:
            valid_attrs["feature_id"] = kwargs["feature_id"]
        if "branch_name" in kwargs:
            valid_attrs["branch_name"] = kwargs["branch_name"]
        if "worktree_startup_duration_ms" in kwargs:
            valid_attrs["worktree_startup_duration_ms"] = kwargs["worktree_startup_duration_ms"]
        
        return cls(**valid_attrs)

@dataclass
class AgentWorktreeActivateSpan:
    """Activate agent in assigned worktree"""
    
    # Agent begins work in isolated worktree environment
    
    # Span attributes
    agent_id: str
    worktree_path: str
    capabilities: List[str] = None
    
    # Span metadata
    span_name: str = "agent.worktree.activate"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.worktree_path is not None:
            span.set_attribute("worktree.path", self.worktree_path)
        if self.capabilities is not None:
            span.set_attribute("capabilities", self.capabilities)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentWorktreeActivateSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "worktree_path" in kwargs:
            valid_attrs["worktree_path"] = kwargs["worktree_path"]
        if "capabilities" in kwargs:
            valid_attrs["capabilities"] = kwargs["capabilities"]
        
        return cls(**valid_attrs)

@dataclass
class AgentCoordinationRequestSpan:
    """Agent requests coordination with other agents"""
    
    # Coordinates work between agents on shared features
    
    # Span attributes
    requesting_agent: str
    target_agents: List[str]
    coordination_reason: str
    coordination_channel: str
    
    # Span metadata
    span_name: str = "agent.coordination.request"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.requesting_agent is not None:
            span.set_attribute("requesting.agent", self.requesting_agent)
        if self.target_agents is not None:
            span.set_attribute("target.agents", self.target_agents)
        if self.coordination_reason is not None:
            span.set_attribute("coordination.reason", self.coordination_reason)
        if self.coordination_channel is not None:
            span.set_attribute("coordination.channel", self.coordination_channel)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentCoordinationRequestSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "requesting_agent" in kwargs:
            valid_attrs["requesting_agent"] = kwargs["requesting_agent"]
        if "target_agents" in kwargs:
            valid_attrs["target_agents"] = kwargs["target_agents"]
        if "coordination_reason" in kwargs:
            valid_attrs["coordination_reason"] = kwargs["coordination_reason"]
        if "coordination_channel" in kwargs:
            valid_attrs["coordination_channel"] = kwargs["coordination_channel"]
        
        return cls(**valid_attrs)

@dataclass
class AgentCoordinationResponseSpan:
    """Agent responds to coordination request"""
    
    # Response to coordination from other agents
    
    # Span attributes
    responding_agent: str
    requesting_agent: str
    response_type: str  # accept, modify, reject
    
    # Span metadata
    span_name: str = "agent.coordination.response"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.responding_agent is not None:
            span.set_attribute("responding.agent", self.responding_agent)
        if self.requesting_agent is not None:
            span.set_attribute("requesting.agent", self.requesting_agent)
        if self.response_type is not None:
            span.set_attribute("response.type", self.response_type)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentCoordinationResponseSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "responding_agent" in kwargs:
            valid_attrs["responding_agent"] = kwargs["responding_agent"]
        if "requesting_agent" in kwargs:
            valid_attrs["requesting_agent"] = kwargs["requesting_agent"]
        if "response_type" in kwargs:
            valid_attrs["response_type"] = kwargs["response_type"]
        
        return cls(**valid_attrs)

@dataclass
class AgentTaskStartSpan:
    """Agent starts work on assigned task"""
    
    # Tracks when agent begins task execution
    
    # Span attributes
    agent_id: str
    task_id: str
    task_description: str = None
    estimated_duration_ms: float = None
    
    # Span metadata
    span_name: str = "agent.task.start"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.task_id is not None:
            span.set_attribute("task.id", self.task_id)
        if self.task_description is not None:
            span.set_attribute("task.description", self.task_description)
        if self.estimated_duration_ms is not None:
            span.set_attribute("estimated.duration_ms", self.estimated_duration_ms)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentTaskStartSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "task_id" in kwargs:
            valid_attrs["task_id"] = kwargs["task_id"]
        if "task_description" in kwargs:
            valid_attrs["task_description"] = kwargs["task_description"]
        if "estimated_duration_ms" in kwargs:
            valid_attrs["estimated_duration_ms"] = kwargs["estimated_duration_ms"]
        
        return cls(**valid_attrs)

@dataclass
class AgentTaskProgressSpan:
    """Agent reports task progress"""
    
    # Periodic progress updates from working agents
    
    # Span attributes
    agent_id: str
    task_id: str
    progress_percentage: float
    current_activity: str = None
    files_modified: List[str] = None
    
    # Span metadata
    span_name: str = "agent.task.progress"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.task_id is not None:
            span.set_attribute("task.id", self.task_id)
        if self.progress_percentage is not None:
            span.set_attribute("progress.percentage", self.progress_percentage)
        if self.current_activity is not None:
            span.set_attribute("current.activity", self.current_activity)
        if self.files_modified is not None:
            span.set_attribute("files.modified", self.files_modified)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentTaskProgressSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "task_id" in kwargs:
            valid_attrs["task_id"] = kwargs["task_id"]
        if "progress_percentage" in kwargs:
            valid_attrs["progress_percentage"] = kwargs["progress_percentage"]
        if "current_activity" in kwargs:
            valid_attrs["current_activity"] = kwargs["current_activity"]
        if "files_modified" in kwargs:
            valid_attrs["files_modified"] = kwargs["files_modified"]
        
        return cls(**valid_attrs)

@dataclass
class AgentTaskCompleteSpan:
    """Agent completes assigned task"""
    
    # Marks task completion and commits work
    
    # Span attributes
    agent_id: str
    task_id: str
    completion_status: str  # success, partial, failed
    actual_duration_ms: float = None
    files_created: List[str] = None
    
    # Span metadata
    span_name: str = "agent.task.complete"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.task_id is not None:
            span.set_attribute("task.id", self.task_id)
        if self.completion_status is not None:
            span.set_attribute("completion.status", self.completion_status)
        if self.actual_duration_ms is not None:
            span.set_attribute("actual.duration_ms", self.actual_duration_ms)
        if self.files_created is not None:
            span.set_attribute("files.created", self.files_created)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "AgentTaskCompleteSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "task_id" in kwargs:
            valid_attrs["task_id"] = kwargs["task_id"]
        if "completion_status" in kwargs:
            valid_attrs["completion_status"] = kwargs["completion_status"]
        if "actual_duration_ms" in kwargs:
            valid_attrs["actual_duration_ms"] = kwargs["actual_duration_ms"]
        if "files_created" in kwargs:
            valid_attrs["files_created"] = kwargs["files_created"]
        
        return cls(**valid_attrs)

@dataclass
class FeatureIntegrationStartSpan:
    """Start integrating agent work into feature"""
    
    # Begins process of merging agent work
    
    # Span attributes
    feature_id: str
    contributing_agents: List[str]
    integration_strategy: str  # sequential, parallel, staged
    
    # Span metadata
    span_name: str = "feature.integration.start"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.feature_id is not None:
            span.set_attribute("feature.id", self.feature_id)
        if self.contributing_agents is not None:
            span.set_attribute("contributing.agents", self.contributing_agents)
        if self.integration_strategy is not None:
            span.set_attribute("integration.strategy", self.integration_strategy)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "FeatureIntegrationStartSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "feature_id" in kwargs:
            valid_attrs["feature_id"] = kwargs["feature_id"]
        if "contributing_agents" in kwargs:
            valid_attrs["contributing_agents"] = kwargs["contributing_agents"]
        if "integration_strategy" in kwargs:
            valid_attrs["integration_strategy"] = kwargs["integration_strategy"]
        
        return cls(**valid_attrs)

@dataclass
class FeatureIntegrationMergeSpan:
    """Merge agent worktree into main branch"""
    
    # Git merge operation for agent's work
    
    # Span attributes
    agent_id: str
    source_branch: str
    target_branch: str
    merge_conflicts: int = None
    merge_strategy: str = None  # merge, rebase, squash
    
    # Span metadata
    span_name: str = "feature.integration.merge"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.agent_id is not None:
            span.set_attribute("agent.id", self.agent_id)
        if self.source_branch is not None:
            span.set_attribute("source.branch", self.source_branch)
        if self.target_branch is not None:
            span.set_attribute("target.branch", self.target_branch)
        if self.merge_conflicts is not None:
            span.set_attribute("merge.conflicts", self.merge_conflicts)
        if self.merge_strategy is not None:
            span.set_attribute("merge.strategy", self.merge_strategy)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "FeatureIntegrationMergeSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "agent_id" in kwargs:
            valid_attrs["agent_id"] = kwargs["agent_id"]
        if "source_branch" in kwargs:
            valid_attrs["source_branch"] = kwargs["source_branch"]
        if "target_branch" in kwargs:
            valid_attrs["target_branch"] = kwargs["target_branch"]
        if "merge_conflicts" in kwargs:
            valid_attrs["merge_conflicts"] = kwargs["merge_conflicts"]
        if "merge_strategy" in kwargs:
            valid_attrs["merge_strategy"] = kwargs["merge_strategy"]
        
        return cls(**valid_attrs)

@dataclass
class FeatureIntegrationCompleteSpan:
    """Complete feature integration process"""
    
    # Final step of feature integration with all agents
    
    # Span attributes
    feature_id: str
    final_status: str  # success, partial, failed
    integration_duration_ms: float = None
    agents_successful: List[str] = None
    agents_failed: List[str] = None
    
    # Span metadata
    span_name: str = "feature.integration.complete"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    def start_span(self) -> trace.Span:
        """Start OpenTelemetry span with attributes"""
        span = tracer.start_span(self.span_name)
        
        # Set span attributes
        if self.feature_id is not None:
            span.set_attribute("feature.id", self.feature_id)
        if self.integration_duration_ms is not None:
            span.set_attribute("integration.duration_ms", self.integration_duration_ms)
        if self.agents_successful is not None:
            span.set_attribute("agents.successful", self.agents_successful)
        if self.agents_failed is not None:
            span.set_attribute("agents.failed", self.agents_failed)
        if self.final_status is not None:
            span.set_attribute("final.status", self.final_status)
        
        # Store span context
        span_context = span.get_span_context()
        self.trace_id = f"{span_context.trace_id:032x}"
        self.span_id = f"{span_context.span_id:016x}"
        
        return span
    
    def end_span(self, span: trace.Span, success: bool = True, error: Optional[str] = None):
        """End span with status"""
        if success:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, error or "Operation failed"))
            if error:
                span.record_exception(Exception(error))
        
        span.end()
    
    @classmethod
    def from_attributes(cls, **kwargs) -> "FeatureIntegrationCompleteSpan":
        """Create span from attribute dictionary"""
        # Filter to only valid attributes
        valid_attrs = {}
        if "feature_id" in kwargs:
            valid_attrs["feature_id"] = kwargs["feature_id"]
        if "integration_duration_ms" in kwargs:
            valid_attrs["integration_duration_ms"] = kwargs["integration_duration_ms"]
        if "agents_successful" in kwargs:
            valid_attrs["agents_successful"] = kwargs["agents_successful"]
        if "agents_failed" in kwargs:
            valid_attrs["agents_failed"] = kwargs["agents_failed"]
        if "final_status" in kwargs:
            valid_attrs["final_status"] = kwargs["final_status"]
        
        return cls(**valid_attrs)

# Span factory for creating spans by name
class WorktreeSpanFactory:
    """Factory for creating worktree coordination spans"""
    
    _span_classes = {
        "agent.worktree.create": AgentWorktreeCreateSpan,
        "agent.worktree.activate": AgentWorktreeActivateSpan,
        "agent.coordination.request": AgentCoordinationRequestSpan,
        "agent.coordination.response": AgentCoordinationResponseSpan,
        "agent.task.start": AgentTaskStartSpan,
        "agent.task.progress": AgentTaskProgressSpan,
        "agent.task.complete": AgentTaskCompleteSpan,
        "feature.integration.start": FeatureIntegrationStartSpan,
        "feature.integration.merge": FeatureIntegrationMergeSpan,
        "feature.integration.complete": FeatureIntegrationCompleteSpan,
    }
    
    @classmethod
    def create_span(cls, span_name: str, **attributes) -> Any:
        """Create span instance by name"""
        if span_name not in cls._span_classes:
            raise ValueError(f"Unknown span type: {span_name}")
        
        span_class = cls._span_classes[span_name]
        return span_class.from_attributes(**attributes)
    
    @classmethod
    def get_available_spans(cls) -> List[str]:
        """Get list of available span types"""
        return list(cls._span_classes.keys())

# Convenience functions for common operations
def create_worktree_span(agent_id: str, worktree_path: str, feature_id: str, branch_name: str) -> trace.Span:
    """Create agent worktree with telemetry"""
    span_data = AgentWorktreeCreateSpan(
        agent_id=agent_id,
        worktree_path=worktree_path,
        feature_id=feature_id,
        branch_name=branch_name,
        worktree_startup_duration_ms=0.0  # Will be updated
    )
    return span_data.start_span()

def create_coordination_request(requesting_agent: str, target_agents: List[str], reason: str, channel: str) -> trace.Span:
    """Create coordination request with telemetry"""
    span_data = AgentCoordinationRequestSpan(
        requesting_agent=requesting_agent,
        target_agents=target_agents,
        coordination_reason=reason,
        coordination_channel=channel
    )
    return span_data.start_span()

def create_task_progress(agent_id: str, task_id: str, percentage: float, activity: str, files: List[str] = None) -> trace.Span:
    """Create task progress update with telemetry"""
    span_data = AgentTaskProgressSpan(
        agent_id=agent_id,
        task_id=task_id,
        progress_percentage=percentage,
        current_activity=activity,
        files_modified=files or []
    )
    return span_data.start_span()

def create_integration_merge(agent_id: str, source_branch: str, target_branch: str, conflicts: int = 0) -> trace.Span:
    """Create integration merge with telemetry"""
    span_data = FeatureIntegrationMergeSpan(
        agent_id=agent_id,
        source_branch=source_branch,
        target_branch=target_branch,
        merge_conflicts=conflicts,
        merge_strategy="merge"
    )
    return span_data.start_span()

# Export all span classes
__all__ = [
    "WorktreeSpanFactory",
    "AgentWorktreeCreateSpan",
    "AgentWorktreeActivateSpan",
    "AgentCoordinationRequestSpan",
    "AgentCoordinationResponseSpan",
    "AgentTaskStartSpan",
    "AgentTaskProgressSpan",
    "AgentTaskCompleteSpan",
    "FeatureIntegrationStartSpan",
    "FeatureIntegrationMergeSpan",
    "FeatureIntegrationCompleteSpan",
    "create_worktree_span",
    "create_coordination_request", 
    "create_task_progress",
    "create_integration_merge",
]