"""
OpenTelemetry Semantic Conventions for Coordination System
Demonstrates proper usage of OTEL semantic conventions and context propagation
"""

from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass

###############################################################################
# Custom Semantic Conventions for Coordination Domain
###############################################################################

class CoordinationAttributes:
    """Custom semantic conventions for coordination operations"""
    
    # Work Item Attributes
    WORK_ID = "coordination.work.id"
    WORK_TYPE = "coordination.work.type"
    WORK_PRIORITY = "coordination.work.priority"
    WORK_STATUS = "coordination.work.status"
    WORK_STORY_POINTS = "coordination.work.story_points"
    WORK_TEAM = "coordination.work.team"
    WORK_ASSIGNEE = "coordination.work.assignee"
    WORK_CREATED_AT = "coordination.work.created_at"
    WORK_COMPLETED_AT = "coordination.work.completed_at"
    WORK_DURATION_SECONDS = "coordination.work.duration_seconds"
    WORK_BLOCKERS = "coordination.work.blockers"
    WORK_DEPENDENCIES = "coordination.work.dependencies"
    WORK_SCORE = "coordination.work.score"
    
    # Sprint Attributes
    SPRINT_ID = "coordination.sprint.id"
    SPRINT_NAME = "coordination.sprint.name"
    SPRINT_START_DATE = "coordination.sprint.start_date"
    SPRINT_END_DATE = "coordination.sprint.end_date"
    SPRINT_CAPACITY = "coordination.sprint.capacity"
    SPRINT_ALLOCATED_POINTS = "coordination.sprint.allocated_points"
    
    # Team Attributes
    TEAM_NAME = "coordination.team.name"
    TEAM_SIZE = "coordination.team.size"
    TEAM_CAPACITY = "coordination.team.capacity"
    TEAM_VELOCITY = "coordination.team.velocity"
    TEAM_WIP_LIMIT = "coordination.team.wip_limit"
    
    # Agent Attributes
    AGENT_ID = "coordination.agent.id"
    AGENT_NAME = "coordination.agent.name"
    AGENT_SKILLS = "coordination.agent.skills"
    AGENT_CAPACITY = "coordination.agent.capacity"
    AGENT_CURRENT_LOAD = "coordination.agent.current_load"
    
    # Operation Attributes
    OPERATION_TYPE = "coordination.operation.type"
    OPERATION_BATCH_SIZE = "coordination.operation.batch_size"
    OPERATION_CONCURRENCY = "coordination.operation.concurrency"
    OPERATION_RETRY_COUNT = "coordination.operation.retry_count"
    
    # Business Attributes
    BUSINESS_VALUE = "coordination.business.value"
    BUSINESS_PRIORITY = "coordination.business.priority"
    BUSINESS_RISK_LEVEL = "coordination.business.risk_level"
    BUSINESS_IMPACT = "coordination.business.impact"

class CoordinationSpanNames:
    """Standard span names for coordination operations"""
    
    # Work Item Operations
    WORK_CLAIM = "coordination.work.claim"
    WORK_UPDATE = "coordination.work.update"
    WORK_COMPLETE = "coordination.work.complete"
    WORK_PRIORITIZE = "coordination.work.prioritize"
    WORK_ASSIGN = "coordination.work.assign"
    
    # Sprint Operations
    SPRINT_PLAN = "coordination.sprint.plan"
    SPRINT_START = "coordination.sprint.start"
    SPRINT_COMPLETE = "coordination.sprint.complete"
    SPRINT_REVIEW = "coordination.sprint.review"
    
    # Team Operations
    TEAM_STANDUP = "coordination.team.standup"
    TEAM_RETROSPECTIVE = "coordination.team.retrospective"
    TEAM_CAPACITY_PLANNING = "coordination.team.capacity_planning"
    
    # Analysis Operations
    ANALYTICS_VELOCITY = "coordination.analytics.velocity"
    ANALYTICS_BURNDOWN = "coordination.analytics.burndown"
    ANALYTICS_CYCLE_TIME = "coordination.analytics.cycle_time"

class CoordinationMetricNames:
    """Standard metric names following OTEL conventions"""
    
    # Counters
    WORK_ITEMS_CREATED = "coordination.work_items.created"
    WORK_ITEMS_COMPLETED = "coordination.work_items.completed"
    WORK_ITEMS_BLOCKED = "coordination.work_items.blocked"
    SPRINT_CYCLES = "coordination.sprint.cycles"
    TEAM_RETROSPECTIVES = "coordination.team.retrospectives"
    
    # Histograms
    WORK_ITEM_DURATION = "coordination.work_item.duration"
    SPRINT_VELOCITY = "coordination.sprint.velocity"
    CYCLE_TIME = "coordination.cycle_time"
    API_LATENCY = "coordination.api.duration"
    
    # Gauges
    ACTIVE_WORK_ITEMS = "coordination.work_items.active"
    TEAM_CAPACITY_UTILIZATION = "coordination.team.capacity.utilization"
    WIP_LIMIT_USAGE = "coordination.wip.usage"
    BURNDOWN_REMAINING = "coordination.burndown.remaining"

###############################################################################
# Semantic Convention Helpers
###############################################################################

class WorkItemType(Enum):
    """Standard work item types"""
    BUG = "bug"
    FEATURE = "feature"
    REFACTOR = "refactor"
    TASK = "task"
    EPIC = "epic"
    STORY = "story"
    SPIKE = "spike"

class WorkItemPriority(Enum):
    """Standard priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class WorkItemStatus(Enum):
    """Standard work item statuses"""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"

@dataclass
class WorkItemContext:
    """Context for work item operations"""
    work_id: str
    work_type: WorkItemType
    priority: WorkItemPriority
    status: WorkItemStatus
    team: str
    assignee: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[int] = None
    dependencies: List[str] = None
    
    def to_span_attributes(self) -> Dict[str, Any]:
        """Convert to span attributes following semantic conventions"""
        attrs = {
            CoordinationAttributes.WORK_ID: self.work_id,
            CoordinationAttributes.WORK_TYPE: self.work_type.value,
            CoordinationAttributes.WORK_PRIORITY: self.priority.value,
            CoordinationAttributes.WORK_STATUS: self.status.value,
            CoordinationAttributes.WORK_TEAM: self.team,
        }
        
        if self.assignee:
            attrs[CoordinationAttributes.WORK_ASSIGNEE] = self.assignee
        if self.story_points:
            attrs[CoordinationAttributes.WORK_STORY_POINTS] = self.story_points
        if self.business_value:
            attrs[CoordinationAttributes.BUSINESS_VALUE] = self.business_value
        if self.dependencies:
            attrs[CoordinationAttributes.WORK_DEPENDENCIES] = ",".join(self.dependencies)
        
        return attrs
    
    def to_baggage(self) -> Dict[str, str]:
        """Convert to baggage for context propagation"""
        baggage_items = {
            "work.id": self.work_id,
            "work.type": self.work_type.value,
            "work.team": self.team,
            "work.priority": self.priority.value
        }
        
        if self.assignee:
            baggage_items["work.assignee"] = self.assignee
        
        return baggage_items