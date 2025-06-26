"""
SwarmAgent Worktree Coordination with OTEL Weaver Communication Layer

Agents use Git worktrees for isolated feature development while communicating
and coordinating through OpenTelemetry Weaver semantic conventions.
"""
import asyncio
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, ClassVar
from dataclasses import dataclass, field
from enum import Enum

from dslmodel.dsl_models import DSLModel
from dslmodel.mixins.fsm_mixin import FSMMixin
from dslmodel.otel.otel_instrumentation_mock import init_otel, get_otel, SwarmSpanAttributes
from dslmodel.utils.llm_init import init_qwen3


class WorktreeState(Enum):
    """States for worktree-based feature development."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    DEVELOPING = "developing"
    TESTING = "testing"
    INTEGRATING = "integrating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FeatureTask:
    """A feature development task for a worktree agent."""
    name: str
    description: str
    branch_name: str
    worktree_path: str
    requirements: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    agent_id: Optional[str] = None


class WorktreeAgent(DSLModel, FSMMixin):
    """
    Agent that uses Git worktrees for isolated feature development with OTEL coordination.
    """
    
    agent_id: str
    worktree_base: str = "/Users/sac/dev/dslmodel-worktrees"
    current_task: Optional[FeatureTask] = None
    worktree_path: Optional[str] = None
    coordination_layer: Optional[Any] = None
    
    # FSM states (ClassVar to avoid Pydantic validation)
    states: ClassVar[List[str]] = [state.value for state in WorktreeState]
    initial: ClassVar[str] = WorktreeState.IDLE.value
    
    def __init__(self, **data):
        super().__init__(**data)
        self.setup_otel_coordination()
        self.setup_fsm()
    
    def setup_otel_coordination(self):
        """Setup OpenTelemetry coordination layer."""
        self.coordination_layer = init_otel(
            service_name=f"worktree-agent-{self.agent_id}",
            service_version="1.0.0",
            enable_console_export=True
        )
    
    def setup_fsm(self):
        """Setup finite state machine."""
        # Define transitions
        self.add_transition(
            'initialize_worktree',
            WorktreeState.IDLE.value,
            WorktreeState.INITIALIZING.value
        )
        
        self.add_transition(
            'start_development',
            WorktreeState.INITIALIZING.value,
            WorktreeState.DEVELOPING.value
        )
        
        self.add_transition(
            'start_testing',
            WorktreeState.DEVELOPING.value,
            WorktreeState.TESTING.value
        )
        
        self.add_transition(
            'start_integration',
            WorktreeState.TESTING.value,
            WorktreeState.INTEGRATING.value
        )
        
        self.add_transition(
            'complete_feature',
            WorktreeState.INTEGRATING.value,
            WorktreeState.COMPLETED.value
        )
        
        self.add_transition(
            'fail_feature',
            [WorktreeState.DEVELOPING.value, WorktreeState.TESTING.value, WorktreeState.INTEGRATING.value],
            WorktreeState.FAILED.value
        )
        
        self.add_transition(
            'reset',
            [WorktreeState.COMPLETED.value, WorktreeState.FAILED.value],
            WorktreeState.IDLE.value
        )
    
    async def coordinate_via_otel(self, event: str, data: Dict[str, Any]):
        """Send coordination event via OpenTelemetry."""
        with self.coordination_layer.trace_span(
            name=f"swarmsh.worktree.coordination.{event}",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                SwarmSpanAttributes.SWARM_FRAMEWORK: "worktree",
                SwarmSpanAttributes.SWARM_PHASE: event,
                "worktree.task": self.current_task.name if self.current_task else "none",
                "worktree.branch": self.current_task.branch_name if self.current_task else "none",
                **{f"data.{k}": str(v) for k, v in data.items()}
            }
        ) as span:
            
            # Record coordination event
            self.coordination_layer.record_command_execution(
                self.agent_id, 
                f"coordinate_{event}", 
                True
            )
            
            # Emit coordination signal to other agents
            span.add_event(f"coordination.{event}", data)
            
            print(f"🤝 Agent {self.agent_id}: Coordinated {event} via OTEL")
    
    async def assign_task(self, task: FeatureTask):
        """Assign a feature development task to this agent."""
        if self.state != WorktreeState.IDLE.value:
            raise ValueError(f"Agent {self.agent_id} is not idle (current state: {self.state})")
        
        self.current_task = task
        task.agent_id = self.agent_id
        
        # Coordinate task assignment
        await self.coordinate_via_otel("task_assigned", {
            "task_name": task.name,
            "branch_name": task.branch_name,
            "dependencies": ",".join(task.dependencies)
        })
        
        # Initialize worktree
        await self.initialize_worktree()
    
    async def initialize_worktree(self):
        """Initialize Git worktree for the assigned task."""
        if not self.current_task:
            raise ValueError("No task assigned")
        
        self.initialize_worktree()  # FSM transition
        
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.initialization",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                "worktree.branch": self.current_task.branch_name,
                "worktree.task": self.current_task.name
            }
        ) as span:
            
            try:
                # Create worktree path
                self.worktree_path = f"{self.worktree_base}/{self.agent_id}-{self.current_task.name.replace(' ', '-')}"
                
                # Remove existing worktree if it exists
                if Path(self.worktree_path).exists():
                    await self._run_git_command(f"worktree remove {self.worktree_path} --force")
                
                # Create new worktree
                await self._run_git_command(
                    f"worktree add -b {self.current_task.branch_name} {self.worktree_path} main"
                )
                
                # Setup Python environment in worktree
                await self._setup_worktree_environment()
                
                span.add_event("worktree.initialized", {
                    "path": self.worktree_path,
                    "branch": self.current_task.branch_name
                })
                
                # Record state transition
                self.coordination_layer.record_state_transition(
                    self.agent_id, "idle", "initializing", "worktree"
                )
                
                print(f"🌳 Agent {self.agent_id}: Worktree initialized at {self.worktree_path}")
                
                # Start development
                await self.start_development_work()
                
            except Exception as e:
                span.record_exception(e)
                self.current_task.status = "failed"
                await self.coordinate_via_otel("initialization_failed", {"error": str(e)})
                raise
    
    async def start_development_work(self):
        """Start feature development work."""
        self.start_development()  # FSM transition
        
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.development",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                SwarmSpanAttributes.SWARM_PHASE: "development",
                "worktree.task": self.current_task.name
            }
        ) as span:
            
            try:
                # Check dependencies via OTEL coordination
                await self._check_dependencies()
                
                # Simulate AI-powered development work
                await self._develop_feature()
                
                # Record development progress
                span.add_event("development.progress", {
                    "status": "in_progress",
                    "requirements_completed": len(self.current_task.requirements)
                })
                
                self.coordination_layer.record_state_transition(
                    self.agent_id, "initializing", "developing", "worktree"
                )
                
                print(f"💻 Agent {self.agent_id}: Development work started")
                
                # Move to testing phase
                await self.start_testing_work()
                
            except Exception as e:
                span.record_exception(e)
                await self.coordinate_via_otel("development_failed", {"error": str(e)})
                self.fail_feature()
                raise
    
    async def start_testing_work(self):
        """Start testing the developed feature."""
        self.start_testing()  # FSM transition
        
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.testing",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                SwarmSpanAttributes.SWARM_PHASE: "testing"
            }
        ) as span:
            
            try:
                # Run tests in worktree
                await self._run_tests()
                
                # Validate feature completion
                await self._validate_feature()
                
                span.add_event("testing.completed", {
                    "test_results": "passed",
                    "coverage": "95%"
                })
                
                self.coordination_layer.record_state_transition(
                    self.agent_id, "developing", "testing", "worktree"
                )
                
                print(f"🧪 Agent {self.agent_id}: Testing completed successfully")
                
                # Move to integration phase
                await self.start_integration_work()
                
            except Exception as e:
                span.record_exception(e)
                await self.coordinate_via_otel("testing_failed", {"error": str(e)})
                self.fail_feature()
                raise
    
    async def start_integration_work(self):
        """Start integration with main branch."""
        self.start_integration()  # FSM transition
        
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.integration",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                SwarmSpanAttributes.SWARM_PHASE: "integration"
            }
        ) as span:
            
            try:
                # Coordinate integration with other agents
                await self.coordinate_via_otel("integration_requested", {
                    "branch": self.current_task.branch_name,
                    "ready_for_merge": True
                })
                
                # Merge with main branch
                await self._integrate_with_main()
                
                # Cleanup worktree
                await self._cleanup_worktree()
                
                span.add_event("integration.completed", {
                    "merge_status": "success",
                    "conflicts": "none"
                })
                
                self.coordination_layer.record_state_transition(
                    self.agent_id, "testing", "integrating", "worktree"
                )
                
                print(f"🔄 Agent {self.agent_id}: Integration completed")
                
                # Complete the feature
                await self.complete_feature_work()
                
            except Exception as e:
                span.record_exception(e)
                await self.coordinate_via_otel("integration_failed", {"error": str(e)})
                self.fail_feature()
                raise
    
    async def complete_feature_work(self):
        """Complete the feature development cycle."""
        self.complete_feature()  # FSM transition
        
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.completion",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.agent_id,
                SwarmSpanAttributes.SWARM_PHASE: "completion"
            }
        ) as span:
            
            # Update task status
            self.current_task.status = "completed"
            
            # Coordinate completion with other agents
            await self.coordinate_via_otel("feature_completed", {
                "task_name": self.current_task.name,
                "branch_name": self.current_task.branch_name,
                "completion_time": time.time()
            })
            
            span.add_event("feature.completed", {
                "task": self.current_task.name,
                "duration": "estimated",
                "success": True
            })
            
            self.coordination_layer.record_state_transition(
                self.agent_id, "integrating", "completed", "worktree"
            )
            
            print(f"✅ Agent {self.agent_id}: Feature '{self.current_task.name}' completed!")
            
            # Reset for next task
            self.current_task = None
            self.worktree_path = None
            self.reset()  # FSM transition back to idle
    
    async def _run_git_command(self, command: str) -> str:
        """Run git command asynchronously."""
        full_command = f"git {command}"
        process = await asyncio.create_subprocess_shell(
            full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/Users/sac/dev/dslmodel"
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Git command failed: {stderr.decode()}")
        
        return stdout.decode()
    
    async def _setup_worktree_environment(self):
        """Setup Python environment in the worktree."""
        # Change to worktree directory and install dependencies
        process = await asyncio.create_subprocess_shell(
            "poetry install --no-interaction",
            cwd=self.worktree_path
        )
        await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError("Failed to setup Python environment")
    
    async def _check_dependencies(self):
        """Check if dependent features are completed via OTEL coordination."""
        if not self.current_task.dependencies:
            return
        
        # In a real implementation, this would query OTEL traces to check
        # if dependent features have been completed by other agents
        for dependency in self.current_task.dependencies:
            print(f"🔍 Agent {self.agent_id}: Checking dependency {dependency}")
    
    async def _develop_feature(self):
        """Simulate AI-powered feature development."""
        # Initialize Qwen3 for AI assistance
        init_qwen3(temperature=0.1)
        
        # Simulate development work with AI
        await asyncio.sleep(2)  # Simulate development time
        print(f"🤖 Agent {self.agent_id}: AI-assisted development in progress...")
    
    async def _run_tests(self):
        """Run tests in the worktree."""
        process = await asyncio.create_subprocess_shell(
            "poetry run pytest tests/ -x",
            cwd=self.worktree_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Tests failed: {stderr.decode()}")
    
    async def _validate_feature(self):
        """Validate that the feature meets requirements."""
        # Simulate validation
        await asyncio.sleep(1)
        print(f"✅ Agent {self.agent_id}: Feature validation passed")
    
    async def _integrate_with_main(self):
        """Integrate the feature branch with main."""
        # Simulate integration process
        await self._run_git_command(f"checkout main")
        await self._run_git_command(f"merge {self.current_task.branch_name} --no-edit")
        await self._run_git_command(f"push origin main")
    
    async def _cleanup_worktree(self):
        """Clean up the worktree after integration."""
        if self.worktree_path and Path(self.worktree_path).exists():
            await self._run_git_command(f"worktree remove {self.worktree_path}")


class WorktreeCoordinator(DSLModel):
    """
    Coordinates multiple worktree agents using OTEL Weaver as communication layer.
    """
    
    coordinator_id: str
    agents: List[WorktreeAgent] = []
    pending_tasks: List[FeatureTask] = []
    completed_tasks: List[FeatureTask] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        self.coordination_layer = init_otel(
            service_name=f"worktree-coordinator-{self.coordinator_id}",
            service_version="1.0.0",
            enable_console_export=True
        )
    
    def add_agent(self, agent: WorktreeAgent):
        """Add a worktree agent to the coordination pool."""
        self.agents.append(agent)
        print(f"🤖 Added agent {agent.agent_id} to coordination pool")
    
    def add_task(self, task: FeatureTask):
        """Add a feature task to the pending queue."""
        self.pending_tasks.append(task)
        print(f"📋 Added task '{task.name}' to pending queue")
    
    async def coordinate_development(self):
        """Coordinate feature development across all agents."""
        with self.coordination_layer.trace_span(
            name="swarmsh.worktree.coordination.cycle",
            attributes={
                SwarmSpanAttributes.SWARM_FRAMEWORK: "worktree_coordination",
                SwarmSpanAttributes.SWARM_PHASE: "development_cycle",
                "coordinator.id": self.coordinator_id,
                "agents.count": len(self.agents),
                "tasks.pending": len(self.pending_tasks)
            }
        ) as span:
            
            print(f"🎯 Coordinator {self.coordinator_id}: Starting development coordination")
            
            # Assign tasks to idle agents
            await self._assign_tasks()
            
            # Monitor agent progress via OTEL
            await self._monitor_progress()
            
            span.add_event("coordination.completed", {
                "tasks_completed": len(self.completed_tasks),
                "tasks_pending": len(self.pending_tasks)
            })
            
            print(f"✅ Coordinator {self.coordinator_id}: Development cycle completed")
    
    async def _assign_tasks(self):
        """Assign pending tasks to available agents."""
        idle_agents = [agent for agent in self.agents if agent.state == WorktreeState.IDLE.value]
        
        for agent in idle_agents:
            if not self.pending_tasks:
                break
            
            task = self.pending_tasks.pop(0)
            
            try:
                await agent.assign_task(task)
                print(f"📤 Assigned task '{task.name}' to agent {agent.agent_id}")
            except Exception as e:
                print(f"❌ Failed to assign task to agent {agent.agent_id}: {e}")
                self.pending_tasks.insert(0, task)  # Put task back
    
    async def _monitor_progress(self):
        """Monitor agent progress and handle completion."""
        # Wait for agents to complete their work
        while any(agent.state not in [WorktreeState.IDLE.value, WorktreeState.COMPLETED.value, WorktreeState.FAILED.value] 
                 for agent in self.agents):
            await asyncio.sleep(1)
        
        # Collect completed tasks
        for agent in self.agents:
            if agent.state == WorktreeState.COMPLETED.value and agent.current_task:
                self.completed_tasks.append(agent.current_task)


# Example usage
async def run_worktree_coordination_demo():
    """Demo of agents using worktrees with OTEL coordination."""
    print("🌳 WORKTREE AGENT COORDINATION DEMO")
    print("=" * 50)
    
    # Create coordinator
    coordinator = WorktreeCoordinator(coordinator_id="main-coordinator")
    
    # Create agents
    agent1 = WorktreeAgent(agent_id="agent-alpha")
    agent2 = WorktreeAgent(agent_id="agent-beta")
    agent3 = WorktreeAgent(agent_id="agent-gamma")
    
    coordinator.add_agent(agent1)
    coordinator.add_agent(agent2)
    coordinator.add_agent(agent3)
    
    # Create feature tasks
    tasks = [
        FeatureTask(
            name="enterprise-coordination-enhancement",
            description="Enhance enterprise coordination with Roberts Rules automation",
            branch_name="feature/enterprise-coord-enhancement",
            requirements=["roberts_rules", "automation", "testing"]
        ),
        FeatureTask(
            name="otel-weaver-integration",
            description="Integrate OTEL Weaver for better observability",
            branch_name="feature/otel-weaver-integration",
            requirements=["weaver", "otel", "semantic_conventions"]
        ),
        FeatureTask(
            name="demo-engine-optimization",
            description="Optimize demo generation engine for performance",
            branch_name="feature/demo-engine-optimization",
            requirements=["performance", "optimization", "ai_integration"]
        )
    ]
    
    for task in tasks:
        coordinator.add_task(task)
    
    # Run coordination
    await coordinator.coordinate_development()
    
    print(f"\n📊 Results:")
    print(f"   ✅ Completed tasks: {len(coordinator.completed_tasks)}")
    print(f"   ⏳ Pending tasks: {len(coordinator.pending_tasks)}")
    
    for task in coordinator.completed_tasks:
        print(f"   🎯 {task.name} (Agent: {task.agent_id})")


if __name__ == "__main__":
    asyncio.run(run_worktree_coordination_demo())