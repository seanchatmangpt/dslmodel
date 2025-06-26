#!/usr/bin/env python3
"""
DSLModel 80/20 Examples - Coordination System Integration
Demonstrates core DSLModel functionality with practical use cases
"""

from typing import List, Optional, Dict
from pydantic import Field
from enum import Enum, auto
import json
import time
from datetime import datetime

# Mock imports - replace with actual imports when dslmodel is installed
try:
    from dslmodel import DSLModel, init_lm
    from dslmodel.utils.model_tools import run_dsls
    from dslmodel.workflow import Workflow, Job, Action, Condition
    from dslmodel.mixins import FSMMixin, trigger
except ImportError:
    print("⚠️  DSLModel not installed. Install with: pip install dslmodel")
    print("📝 Showing example code structure...")
    
    # Mock classes for demonstration
    class DSLModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        @classmethod
        def from_prompt(cls, prompt, **kwargs):
            return cls(**kwargs)
        
        def to_yaml(self):
            return "# YAML output would go here"
    
    class FSMMixin:
        def __init__(self):
            self.state = None
        
        def setup_fsm(self, state_enum, initial):
            self.state = initial
    
    def trigger(source, dest):
        def decorator(func):
            return func
        return decorator
    
    def init_lm():
        print("🤖 LM initialized (mock)")
    
    def run_dsls(tasks, max_workers=5):
        return [f"Result for {task[1]}" for task in tasks]
    
    class Workflow:
        def __init__(self, name, **kwargs):
            self.name = name
    
    class Job:
        def __init__(self, name, steps):
            self.name = name
            self.steps = steps
    
    class Action:
        def __init__(self, name, code, cond=None):
            self.name = name
    
    class Condition:
        def __init__(self, expr):
            self.expr = expr


# 1. CORE MODELS (80% use case: defining work items and agents)
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkItem(DSLModel):
    """Represents a work item in the coordination system"""
    work_id: str = Field("{{ 'work_' + timestamp }}", description="Unique work ID")
    title: str = Field(..., description="Title of the work item")
    description: str = Field(..., description="Detailed description")
    priority: Priority = Field(Priority.MEDIUM, description="Priority level")
    assignee: Optional[str] = Field(None, description="Assigned agent ID")
    status: str = Field("pending", description="Current status")
    created_at: str = Field("{{ now_iso() }}", description="Creation timestamp")
    story_points: int = Field(5, description="Estimated effort in story points")


class Agent(DSLModel):
    """Represents an agent in the system"""
    agent_id: str = Field("{{ 'agent_' + timestamp }}", description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    skills: List[str] = Field(..., description="List of agent skills")
    capacity: int = Field(10, description="Max story points per sprint")
    current_load: int = Field(0, description="Current story points assigned")


class Sprint(DSLModel):
    """Represents a sprint with work items"""
    sprint_id: str = Field("{{ 'sprint_' + timestamp }}", description="Sprint ID")
    name: str = Field(..., description="Sprint name")
    work_items: List[WorkItem] = Field([], description="Work items in sprint")
    agents: List[Agent] = Field([], description="Agents in sprint")
    start_date: str = Field(..., description="Sprint start date")
    end_date: str = Field(..., description="Sprint end date")


# 2. CONCURRENT EXECUTION (80% use case: processing multiple items)
def demo_concurrent_work_creation():
    """Create multiple work items concurrently"""
    print("\n📋 Creating work items concurrently...")
    
    # Define tasks for concurrent execution
    work_prompts = [
        (WorkItem, "Create a bug fix for authentication module"),
        (WorkItem, "Create a feature for dark mode UI"),
        (WorkItem, "Create a refactoring task for database layer"),
        (WorkItem, "Create a performance optimization task"),
        (WorkItem, "Create a documentation task for API")
    ]
    
    # Mock concurrent execution
    init_lm()
    results = run_dsls(work_prompts, max_workers=5)
    
    print(f"✅ Created {len(results)} work items concurrently")
    return results


# 3. STATE MACHINE (80% use case: work item lifecycle)
class WorkState(Enum):
    BACKLOG = auto()
    TODO = auto()
    IN_PROGRESS = auto()
    REVIEW = auto()
    DONE = auto()


class WorkItemFSM(FSMMixin):
    """Work item with state machine for lifecycle management"""
    
    def __init__(self, work_item: WorkItem):
        super().__init__()
        self.work_item = work_item
        self.setup_fsm(state_enum=WorkState, initial=WorkState.BACKLOG)
    
    @trigger(source=WorkState.BACKLOG, dest=WorkState.TODO)
    def add_to_sprint(self):
        print(f"📌 {self.work_item.title} added to sprint")
        self.work_item.status = "todo"
    
    @trigger(source=WorkState.TODO, dest=WorkState.IN_PROGRESS)
    def start_work(self, agent_id: str):
        print(f"🚀 {agent_id} started {self.work_item.title}")
        self.work_item.assignee = agent_id
        self.work_item.status = "in_progress"
    
    @trigger(source=WorkState.IN_PROGRESS, dest=WorkState.REVIEW)
    def submit_for_review(self):
        print(f"👀 {self.work_item.title} submitted for review")
        self.work_item.status = "review"
    
    @trigger(source=WorkState.REVIEW, dest=WorkState.DONE)
    def complete(self):
        print(f"✅ {self.work_item.title} completed")
        self.work_item.status = "done"


# 4. WORKFLOW (80% use case: sprint planning automation)
def create_sprint_workflow():
    """Create a workflow for sprint planning"""
    
    # Define conditions
    has_capacity = Condition(expr="sum(w.story_points for w in work_items) <= total_capacity")
    
    # Define actions
    action1 = Action(
        name="Collect Work Items",
        code="""
work_items = [
    WorkItem(title="Fix login bug", priority="high", story_points=3),
    WorkItem(title="Add user profile", priority="medium", story_points=5),
    WorkItem(title="Optimize queries", priority="low", story_points=8)
]
print(f"Collected {len(work_items)} work items")
"""
    )
    
    action2 = Action(
        name="Assign to Agents",
        code="""
agents = [
    Agent(name="Alice", skills=["backend", "database"], capacity=10),
    Agent(name="Bob", skills=["frontend", "ui"], capacity=8)
]
total_capacity = sum(a.capacity for a in agents)
print(f"Total team capacity: {total_capacity} points")
""",
        cond=has_capacity
    )
    
    action3 = Action(
        name="Create Sprint",
        code="""
sprint = Sprint(
    name="Sprint 2024-W1",
    work_items=work_items,
    agents=agents,
    start_date="2024-01-01",
    end_date="2024-01-14"
)
print(f"Created {sprint.name} with {len(sprint.work_items)} items")
"""
    )
    
    # Create job
    job = Job(
        name="Plan Sprint",
        steps=[action1, action2, action3]
    )
    
    # Create workflow
    workflow = Workflow(
        name="Sprint Planning Workflow",
        jobs=[job],
        context={"work_items": [], "agents": [], "total_capacity": 0}
    )
    
    return workflow


# 5. TEMPLATE-BASED GENERATION (80% use case: dynamic content)
def demo_template_generation():
    """Generate meeting notes from template"""
    print("\n📝 Generating sprint retrospective from template...")
    
    retro_template = """
Sprint Retrospective for {{ sprint_name }}
Date: {{ meeting_date }}

Team Members Present:
{% for agent in agents %}
- {{ agent.name }} (Capacity: {{ agent.capacity }} points)
{% endfor %}

Completed Work Items:
{% for item in completed_items %}
- {{ item.title }} ({{ item.story_points }} points) - {{ item.priority }} priority
{% endfor %}

Key Metrics:
- Total Story Points Completed: {{ total_points }}
- Team Velocity: {{ velocity }}
- Sprint Success Rate: {{ success_rate }}%

Action Items:
- Improve estimation accuracy
- Reduce review cycle time
- Increase automated testing coverage
"""
    
    # Mock data
    agents = [
        Agent(name="Alice", skills=["backend"], capacity=10),
        Agent(name="Bob", skills=["frontend"], capacity=8)
    ]
    
    completed_items = [
        WorkItem(title="Fix login bug", priority="high", story_points=3, status="done"),
        WorkItem(title="Add user profile", priority="medium", story_points=5, status="done")
    ]
    
    class SprintRetro(DSLModel):
        """Sprint retrospective document"""
        content: str = Field(..., description="Retrospective content")
        sprint_name: str = Field(..., description="Sprint name")
        meeting_date: str = Field(..., description="Meeting date")
        total_points: int = Field(..., description="Total points completed")
        velocity: float = Field(..., description="Team velocity")
        success_rate: float = Field(..., description="Success rate percentage")
    
    # Generate retrospective
    retro = SprintRetro.from_prompt(
        retro_template,
        sprint_name="Sprint 2024-W1",
        meeting_date=datetime.now().strftime("%Y-%m-%d"),
        agents=agents,
        completed_items=completed_items,
        total_points=sum(item.story_points for item in completed_items),
        velocity=8.0,
        success_rate=80.0
    )
    
    print("✅ Generated sprint retrospective")
    return retro


# MAIN: Demonstrate 80/20 functionality
def main():
    """Run all 80/20 examples"""
    print("🚀 DSLModel 80/20 Examples - Coordination System")
    print("=" * 50)
    
    # 1. Concurrent work item creation
    work_items = demo_concurrent_work_creation()
    
    # 2. State machine for work item lifecycle
    print("\n🔄 Work Item State Machine Demo:")
    work = WorkItem(title="Implement OAuth", priority="high")
    fsm = WorkItemFSM(work)
    
    fsm.add_to_sprint()
    fsm.start_work("agent_123")
    fsm.submit_for_review()
    fsm.complete()
    
    # 3. Workflow execution
    print("\n⚙️  Sprint Planning Workflow:")
    workflow = create_sprint_workflow()
    print(f"Created workflow: {workflow.name}")
    # workflow.execute()  # Would execute in real scenario
    
    # 4. Template-based generation
    retro = demo_template_generation()
    
    print("\n✨ Summary: DSLModel 80/20 Features Demonstrated")
    print("1. ✅ Dynamic model creation with DSLModel")
    print("2. ✅ Concurrent execution with run_dsls")
    print("3. ✅ State machines with FSMMixin")
    print("4. ✅ Workflow automation")
    print("5. ✅ Template-based content generation")
    
    print("\n📊 These features cover 80% of coordination use cases!")


if __name__ == "__main__":
    main()