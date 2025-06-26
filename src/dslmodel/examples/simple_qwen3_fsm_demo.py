"""
Simple Demo: Qwen3 + FSM Integration

Demonstrates AI-powered state transitions using Qwen3 with DSLModel and FSMMixin.
This is a simplified version without OpenTelemetry to focus on the AI integration.
"""
import asyncio
from enum import Enum
from typing import Optional
from loguru import logger

from pydantic import Field

# Initialize Qwen3 first
from dslmodel.utils.llm_init import init_qwen3
logger.info("Initializing Qwen3 for AI-powered state machines...")
lm = init_qwen3(temperature=0.3)

# Import DSLModel components
from dslmodel.dsl_models import DSLModel
from dslmodel.mixins.fsm_mixin import FSMMixin, trigger
from dslmodel.dspy_modules.fsm_trigger_module import fsm_trigger_call


class TaskState(str, Enum):
    """States for AI-assisted task management."""
    created = "created"
    analyzing = "analyzing"
    planning = "planning"
    executing = "executing"
    reviewing = "reviewing"
    completed = "completed"
    blocked = "blocked"
    cancelled = "cancelled"


class AITaskManager(DSLModel, FSMMixin):
    """
    AI-powered task manager that uses Qwen3 to make intelligent
    state transition decisions based on context.
    """
    
    # Task attributes
    task_id: str = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str = Field(description="Detailed task description")
    priority: str = Field(default="medium", description="Task priority: low/medium/high")
    
    # State tracking
    state: TaskState = Field(default=TaskState.created, description="Current task state")
    ai_reasoning: list[str] = Field(default_factory=list, description="AI reasoning history")
    context_data: dict = Field(default_factory=dict, description="Additional context")
    
    # Progress tracking
    completion_percentage: int = Field(default=0, description="Task completion percentage")
    blockers: list[str] = Field(default_factory=list, description="Current blockers")
    
    def model_post_init(self, __context):
        """Initialize the FSM after model creation."""
        super().model_post_init(__context)
        
        # Initialize FSMMixin attributes
        FSMMixin.__init__(self)
        
        # Setup FSM with task states
        self.setup_fsm(TaskState, initial=TaskState.created)
        
        # Ensure state is set correctly
        if self.state is None:
            self.state = TaskState.created
        
    # AI-powered state transitions
    
    @trigger(source=TaskState.created, dest=TaskState.analyzing)
    def start_analysis(self) -> bool:
        """Begin analyzing the task requirements."""
        logger.info(f"Starting analysis for task: {self.title}")
        
        # Use AI to analyze task complexity
        analysis_prompt = f"""
        Analyze this task for complexity and requirements:
        
        Title: {self.title}
        Description: {self.description}
        Priority: {self.priority}
        
        Provide a brief analysis of:
        1. Complexity level (Simple/Medium/Complex)
        2. Key requirements
        3. Potential challenges
        
        Keep response under 100 words.
        """
        
        try:
            import dspy
            analysis = dspy.settings.lm(analysis_prompt)
            self.ai_reasoning.append(f"Analysis: {analysis}")
            logger.info(f"AI Analysis complete: {analysis}")
            return True
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return False
            
    @trigger(source=TaskState.analyzing, dest=TaskState.planning)
    def create_plan(self) -> bool:
        """Create an execution plan using AI."""
        logger.info(f"Creating execution plan for: {self.title}")
        
        planning_prompt = f"""
        Create a simple execution plan for this task:
        
        Title: {self.title}
        Description: {self.description}
        Previous Analysis: {self.ai_reasoning[-1] if self.ai_reasoning else "None"}
        
        Provide 3-5 action steps in a numbered list.
        Keep it practical and actionable.
        """
        
        try:
            import dspy
            plan = dspy.settings.lm(planning_prompt)
            self.ai_reasoning.append(f"Plan: {plan}")
            logger.info(f"Execution plan created: {plan}")
            return True
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return False
            
    @trigger(source=TaskState.planning, dest=TaskState.executing)
    def begin_execution(self) -> bool:
        """Start executing the task."""
        logger.info(f"Beginning execution of: {self.title}")
        self.completion_percentage = 10
        return True
        
    @trigger(source=TaskState.executing, dest=TaskState.reviewing)
    def start_review(self) -> bool:
        """Move to review phase."""
        logger.info(f"Starting review for: {self.title}")
        self.completion_percentage = 90
        return True
        
    @trigger(source=TaskState.reviewing, dest=TaskState.completed)
    def complete_task(self) -> bool:
        """Mark task as completed."""
        logger.success(f"Task completed: {self.title}")
        self.completion_percentage = 100
        return True
        
    @trigger(source=[TaskState.analyzing, TaskState.planning, TaskState.executing], dest=TaskState.blocked)
    def block_task(self, blocker: str) -> bool:
        """Block the task due to an issue."""
        logger.warning(f"Task blocked: {blocker}")
        self.blockers.append(blocker)
        return True
        
    @trigger(source=TaskState.blocked, dest=TaskState.executing)
    def unblock_task(self, resolution: str) -> bool:
        """Unblock the task."""
        logger.info(f"Task unblocked: {resolution}")
        self.context_data["unblock_resolution"] = resolution
        return True
        
    @trigger(source="*", dest=TaskState.cancelled)
    def cancel_task(self, reason: str) -> bool:
        """Cancel the task."""
        logger.warning(f"Task cancelled: {reason}")
        self.context_data["cancellation_reason"] = reason
        return True
        
    def ai_next_action_suggestion(self, current_context: str) -> str:
        """Get AI suggestion for next action based on current context."""
        suggestion_prompt = f"""
        Task Status:
        - Title: {self.title}
        - Current State: {self.state}
        - Completion: {self.completion_percentage}%
        - Priority: {self.priority}
        
        Current Context: {current_context}
        
        Blockers: {', '.join(self.blockers) if self.blockers else 'None'}
        
        What should be the next action for this task?
        Provide a brief, actionable recommendation.
        """
        
        try:
            import dspy
            suggestion = dspy.settings.lm(suggestion_prompt)
            logger.info(f"AI Suggestion: {suggestion}")
            return str(suggestion)
        except Exception as e:
            logger.error(f"AI suggestion failed: {e}")
            return "Continue with current plan or seek human input."
            
    def get_smart_status_summary(self) -> str:
        """Get an AI-generated status summary."""
        summary_prompt = f"""
        Create a concise status summary for this task:
        
        Title: {self.title}
        State: {self.state}
        Progress: {self.completion_percentage}%
        Blockers: {len(self.blockers)} blockers
        AI Reasoning History: {len(self.ai_reasoning)} entries
        
        Provide a 1-2 sentence status update that would be useful for a project manager.
        """
        
        try:
            import dspy
            summary = dspy.settings.lm(summary_prompt)
            return str(summary)
        except Exception as e:
            logger.error(f"Status summary failed: {e}")
            return f"Task '{self.title}' is in {self.state} state with {self.completion_percentage}% completion."


async def demo_ai_task_workflow():
    """Demonstrate AI-powered task workflow."""
    
    # Create a complex task
    task = AITaskManager(
        task_id="TASK-2024-001",
        title="Implement User Authentication System",
        description="Build a secure user authentication system with JWT tokens, password hashing, and role-based access control for the web application.",
        priority="high",
        state=TaskState.created
    )
    
    logger.info(f"Created task: {task.title}")
    logger.info(f"Initial state: {task.state}")
    
    try:
        # Progress through AI-assisted workflow
        logger.info("\n=== AI Analysis Phase ===")
        task.start_analysis()
        await asyncio.sleep(1)  # Simulate processing time
        
        logger.info("\n=== AI Planning Phase ===")
        task.create_plan()
        await asyncio.sleep(1)
        
        logger.info("\n=== Execution Phase ===")
        task.begin_execution()
        
        # Simulate some progress
        logger.info("Simulating work progress...")
        task.completion_percentage = 45
        
        # Get AI suggestion for next steps
        logger.info("\n=== AI Next Action Suggestion ===")
        next_action = task.ai_next_action_suggestion(
            "Development team has implemented basic login/logout but needs to add password reset functionality"
        )
        
        # Continue workflow
        logger.info("\n=== Review Phase ===")
        task.start_review()
        
        logger.info("\n=== Completion ===")
        task.complete_task()
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        task.cancel_task(str(e))
        
    # Get final AI status summary
    logger.info("\n=== Final AI Status Summary ===")
    summary = task.get_smart_status_summary()
    logger.success(f"Summary: {summary}")
    
    # Show full task state (exclude FSM machine from serialization)
    logger.info("\n=== Final Task State ===")
    task_data = task.model_dump(exclude={'machine', 'states'})
    import json
    print(json.dumps(task_data, indent=2, default=str))
    
    return task


async def demo_blocked_task_recovery():
    """Demonstrate AI-assisted recovery from blocked state."""
    
    task = AITaskManager(
        task_id="TASK-2024-002",
        title="Database Migration", 
        description="Migrate user data from old database to new schema",
        priority="medium",
        state=TaskState.created
    )
    
    logger.info(f"\n=== Blocked Task Recovery Demo ===")
    logger.info(f"Task: {task.title}")
    
    # Progress to executing state
    task.start_analysis()
    task.create_plan()
    task.begin_execution()
    
    # Simulate a blocker
    logger.warning("Encountering a blocker...")
    task.block_task("Database connection timeout - need to increase timeout settings")
    
    logger.info(f"Task now blocked. Current state: {task.state}")
    
    # Get AI suggestion for resolution
    suggestion = task.ai_next_action_suggestion(
        "Database migration failing due to connection timeouts during large data transfer"
    )
    
    # Simulate resolution
    logger.info("Implementing suggested resolution...")
    task.unblock_task("Increased connection timeout and implemented batch processing")
    
    logger.info(f"Task unblocked. Current state: {task.state}")
    
    # Continue to completion
    task.start_review()
    task.complete_task()
    
    summary = task.get_smart_status_summary()
    logger.success(f"Recovery complete: {summary}")
    
    return task


async def main():
    """Run all demos."""
    logger.info("=== Qwen3 + FSM Integration Demo ===\n")
    
    # Demo 1: Normal workflow
    logger.info("1. Running normal AI-assisted workflow...")
    await demo_ai_task_workflow()
    
    # Demo 2: Blocked task recovery
    logger.info("\n2. Running blocked task recovery demo...")
    await demo_blocked_task_recovery()
    
    logger.info("\nDemo complete! Qwen3 successfully integrated with DSLModel FSM.")


if __name__ == "__main__":
    asyncio.run(main())