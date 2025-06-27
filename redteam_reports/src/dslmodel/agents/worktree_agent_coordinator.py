#!/usr/bin/env python3
"""
Worktree Agent Coordinator - Agents use worktrees with OTEL Weaver communication

This module implements distributed agent coordination where each agent claims an 
exclusive worktree and uses OpenTelemetry spans for communication and status updates.
"""

import asyncio
import json
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..utils.dspy_tools import init_lm


class AgentState(Enum):
    """Agent states for worktree coordination"""
    IDLE = "idle"
    CLAIMING = "claiming"
    WORKING = "working"
    VALIDATING = "validating"
    SUBMITTING = "submitting"
    FINISHED = "finished"
    ERROR = "error"


class WorktreeStatus(Enum):
    """Worktree status for coordination"""
    AVAILABLE = "available"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    READY_TO_MERGE = "ready_to_merge"
    MERGED = "merged"
    ABANDONED = "abandoned"


@dataclass
class FeatureSpec:
    """Specification for a feature to be developed"""
    name: str
    description: str
    requirements: List[str]
    acceptance_criteria: List[str]
    estimated_effort: int  # Story points
    priority: str = "medium"
    assigned_agent: Optional[str] = None
    worktree_path: Optional[Path] = None
    branch_name: Optional[str] = None


@dataclass
class AgentCapability:
    """Agent capabilities and preferences"""
    agent_id: str
    languages: List[str]
    frameworks: List[str]
    expertise_areas: List[str]
    max_concurrent_features: int = 1
    preferred_complexity: str = "medium"  # low, medium, high


@dataclass
class WorktreeAgent:
    """Agent working in an exclusive worktree"""
    agent_id: str
    state: AgentState
    current_feature: Optional[FeatureSpec]
    worktree_path: Optional[Path]
    branch_name: Optional[str]
    last_activity: float
    capabilities: AgentCapability
    communication_trace_id: str
    telemetry_spans: List[str]


class WorktreeAgentCoordinator:
    """Coordinates agents using exclusive worktrees and OTEL communication"""
    
    def __init__(self, base_repo_path: Path, coordination_dir: Path = None):
        self.base_repo_path = base_repo_path
        self.coordination_dir = coordination_dir or base_repo_path / "coordination"
        self.coordination_dir.mkdir(exist_ok=True)
        
        # Agent management
        self.agents: Dict[str, WorktreeAgent] = {}
        self.worktrees: Dict[str, WorktreeStatus] = {}
        self.feature_queue: List[FeatureSpec] = []
        self.active_features: Dict[str, FeatureSpec] = {}
        self.completed_features: List[FeatureSpec] = []
        
        # OTEL setup
        self.tracer = trace.get_tracer(__name__)
        self.communication_spans: Dict[str, Any] = {}
        
        # Coordination state files
        self.state_file = self.coordination_dir / "agent_coordination_state.json"
        self.telemetry_file = self.coordination_dir / "worktree_telemetry.jsonl"
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        logger.info(f"WorktreeAgentCoordinator initialized at {base_repo_path}")
    
    def register_agent(self, capabilities: AgentCapability) -> str:
        """Register a new agent with capabilities"""
        agent_id = capabilities.agent_id
        
        with self.tracer.start_as_current_span("agent_registration") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("languages", ",".join(capabilities.languages))
            span.set_attribute("frameworks", ",".join(capabilities.frameworks))
            span.set_attribute("max_concurrent", capabilities.max_concurrent_features)
            
            agent = WorktreeAgent(
                agent_id=agent_id,
                state=AgentState.IDLE,
                current_feature=None,
                worktree_path=None,
                branch_name=None,
                last_activity=time.time(),
                capabilities=capabilities,
                communication_trace_id=str(uuid.uuid4()),
                telemetry_spans=[]
            )
            
            self.agents[agent_id] = agent
            
            # Emit registration telemetry
            self._emit_agent_telemetry(agent, "agent_registered")
            
            span.set_attribute("registration_success", True)
            logger.info(f"Agent {agent_id} registered with capabilities: {capabilities.expertise_areas}")
            
            return agent_id
    
    def add_feature_request(self, feature: FeatureSpec) -> str:
        """Add a feature request to the development queue"""
        feature_id = f"feature_{uuid.uuid4().hex[:8]}"
        feature.name = feature_id if not feature.name else feature.name
        
        with self.tracer.start_as_current_span("feature_request_added") as span:
            span.set_attribute("feature_id", feature_id)
            span.set_attribute("feature_name", feature.name)
            span.set_attribute("priority", feature.priority)
            span.set_attribute("estimated_effort", feature.estimated_effort)
            
            self.feature_queue.append(feature)
            
            logger.info(f"Feature request added: {feature.name} (priority: {feature.priority})")
            
            return feature_id
    
    def create_feature_worktree(self, feature: FeatureSpec, agent_id: str) -> Tuple[Path, str]:
        """Create an exclusive worktree for a feature"""
        branch_name = f"feature/{feature.name.lower().replace(' ', '-')}-{agent_id}"
        worktree_name = f"worktree-{agent_id}-{uuid.uuid4().hex[:6]}"
        worktree_path = self.base_repo_path.parent / "worktrees" / worktree_name
        
        with self.tracer.start_as_current_span("worktree_creation") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("feature_name", feature.name)
            span.set_attribute("branch_name", branch_name)
            span.set_attribute("worktree_path", str(worktree_path))
            
            try:
                # Ensure worktrees directory exists
                worktree_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create worktree with new branch
                self._run_git_command([
                    "worktree", "add", "-b", branch_name, 
                    str(worktree_path), "main"
                ])
                
                # Update tracking
                self.worktrees[str(worktree_path)] = WorktreeStatus.CLAIMED
                feature.worktree_path = worktree_path
                feature.branch_name = branch_name
                feature.assigned_agent = agent_id
                
                span.set_attribute("worktree_created", True)
                logger.info(f"Worktree created: {worktree_path} for agent {agent_id}")
                
                return worktree_path, branch_name
                
            except subprocess.CalledProcessError as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to create worktree: {e}")
                raise
    
    def assign_feature_to_agent(self, agent_id: str) -> Optional[FeatureSpec]:
        """Assign the best matching feature to an available agent"""
        if agent_id not in self.agents:
            logger.warning(f"Unknown agent: {agent_id}")
            return None
            
        agent = self.agents[agent_id]
        
        if agent.state != AgentState.IDLE:
            logger.warning(f"Agent {agent_id} is not idle (state: {agent.state})")
            return None
        
        # Find best matching feature based on agent capabilities
        best_feature = self._find_best_feature_match(agent.capabilities)
        
        if not best_feature:
            logger.info(f"No suitable features for agent {agent_id}")
            return None
        
        with self.tracer.start_as_current_span("feature_assignment") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("feature_name", best_feature.name)
            
            # Remove from queue and create worktree
            self.feature_queue.remove(best_feature)
            worktree_path, branch_name = self.create_feature_worktree(best_feature, agent_id)
            
            # Update agent state
            agent.state = AgentState.CLAIMING
            agent.current_feature = best_feature
            agent.worktree_path = worktree_path
            agent.branch_name = branch_name
            agent.last_activity = time.time()
            
            # Track active feature
            self.active_features[best_feature.name] = best_feature
            
            # Emit assignment telemetry
            self._emit_agent_telemetry(agent, "feature_assigned", {
                "feature_name": best_feature.name,
                "worktree_path": str(worktree_path),
                "branch_name": branch_name
            })
            
            span.set_attribute("assignment_success", True)
            logger.info(f"Feature '{best_feature.name}' assigned to agent {agent_id}")
            
            return best_feature
    
    def agent_start_work(self, agent_id: str) -> bool:
        """Agent starts working on assigned feature"""
        if agent_id not in self.agents:
            return False
            
        agent = self.agents[agent_id]
        
        if agent.state != AgentState.CLAIMING or not agent.current_feature:
            logger.warning(f"Agent {agent_id} cannot start work (state: {agent.state})")
            return False
        
        with self.tracer.start_as_current_span("agent_start_work") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("feature_name", agent.current_feature.name)
            
            agent.state = AgentState.WORKING
            agent.last_activity = time.time()
            
            # Update worktree status
            if agent.worktree_path:
                self.worktrees[str(agent.worktree_path)] = WorktreeStatus.IN_PROGRESS
            
            # Emit work start telemetry
            self._emit_agent_telemetry(agent, "work_started")
            
            span.set_attribute("work_started", True)
            logger.info(f"Agent {agent_id} started work on {agent.current_feature.name}")
            
            return True
    
    def agent_submit_work(self, agent_id: str, validation_results: Dict[str, Any] = None) -> bool:
        """Agent submits completed work for validation"""
        if agent_id not in self.agents:
            return False
            
        agent = self.agents[agent_id]
        
        if agent.state != AgentState.WORKING or not agent.current_feature:
            logger.warning(f"Agent {agent_id} cannot submit work (state: {agent.state})")
            return False
        
        with self.tracer.start_as_current_span("agent_submit_work") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("feature_name", agent.current_feature.name)
            
            agent.state = AgentState.VALIDATING
            agent.last_activity = time.time()
            
            # Update worktree status
            if agent.worktree_path:
                self.worktrees[str(agent.worktree_path)] = WorktreeStatus.VALIDATING
            
            # Run validation
            validation_success = self._validate_agent_work(agent, validation_results or {})
            
            if validation_success:
                agent.state = AgentState.SUBMITTING
                self.worktrees[str(agent.worktree_path)] = WorktreeStatus.READY_TO_MERGE
                span.set_attribute("validation_passed", True)
            else:
                agent.state = AgentState.WORKING  # Back to work for fixes
                self.worktrees[str(agent.worktree_path)] = WorktreeStatus.IN_PROGRESS
                span.set_attribute("validation_passed", False)
            
            # Emit submission telemetry
            self._emit_agent_telemetry(agent, "work_submitted", {
                "validation_success": validation_success,
                "validation_results": validation_results
            })
            
            logger.info(f"Agent {agent_id} submitted work - validation {'passed' if validation_success else 'failed'}")
            
            return validation_success
    
    def complete_feature(self, agent_id: str) -> bool:
        """Complete feature and clean up worktree"""
        if agent_id not in self.agents:
            return False
            
        agent = self.agents[agent_id]
        
        if agent.state != AgentState.SUBMITTING or not agent.current_feature:
            logger.warning(f"Agent {agent_id} cannot complete feature (state: {agent.state})")
            return False
        
        with self.tracer.start_as_current_span("feature_completion") as span:
            span.set_attribute("agent_id", agent_id)
            span.set_attribute("feature_name", agent.current_feature.name)
            
            # Move to completed features
            completed_feature = agent.current_feature
            self.completed_features.append(completed_feature)
            
            # Clean up active tracking
            if completed_feature.name in self.active_features:
                del self.active_features[completed_feature.name]
            
            # Update worktree status
            if agent.worktree_path:
                self.worktrees[str(agent.worktree_path)] = WorktreeStatus.MERGED
            
            # Reset agent state
            agent.state = AgentState.FINISHED
            agent.current_feature = None
            agent.last_activity = time.time()
            
            # Emit completion telemetry
            self._emit_agent_telemetry(agent, "feature_completed", {
                "feature_name": completed_feature.name,
                "completion_time": time.time()
            })
            
            span.set_attribute("feature_completed", True)
            logger.info(f"Feature '{completed_feature.name}' completed by agent {agent_id}")
            
            # Agent returns to idle for next assignment
            agent.state = AgentState.IDLE
            
            return True
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get comprehensive coordination status"""
        with self.tracer.start_as_current_span("coordination_status") as span:
            active_agents = [a for a in self.agents.values() if a.state != AgentState.IDLE]
            idle_agents = [a for a in self.agents.values() if a.state == AgentState.IDLE]
            
            status = {
                "total_agents": len(self.agents),
                "active_agents": len(active_agents),
                "idle_agents": len(idle_agents),
                "features_in_queue": len(self.feature_queue),
                "features_in_progress": len(self.active_features),
                "features_completed": len(self.completed_features),
                "total_worktrees": len(self.worktrees),
                "agents_by_state": {},
                "worktrees_by_status": {},
                "coordination_health": self._calculate_coordination_health()
            }
            
            # Group agents by state
            for agent in self.agents.values():
                state_name = agent.state.value
                if state_name not in status["agents_by_state"]:
                    status["agents_by_state"][state_name] = 0
                status["agents_by_state"][state_name] += 1
            
            # Group worktrees by status
            for wt_status in self.worktrees.values():
                status_name = wt_status.value
                if status_name not in status["worktrees_by_status"]:
                    status["worktrees_by_status"][status_name] = 0
                status["worktrees_by_status"][status_name] += 1
            
            span.set_attribute("coordination_health", status["coordination_health"])
            
            return status
    
    def run_coordination_cycle(self) -> Dict[str, Any]:
        """Run one coordination cycle - assign work, check progress"""
        with self.tracer.start_as_current_span("coordination_cycle") as span:
            cycle_start = time.time()
            
            # Check for idle agents and assign work
            assignments_made = 0
            for agent_id, agent in self.agents.items():
                if agent.state == AgentState.IDLE and self.feature_queue:
                    if self.assign_feature_to_agent(agent_id):
                        assignments_made += 1
            
            # Check agent activity and handle timeouts
            timeouts_handled = self._check_agent_timeouts()
            
            # Update coordination state
            self._save_coordination_state()
            
            cycle_duration = int((time.time() - cycle_start) * 1000)
            
            result = {
                "assignments_made": assignments_made,
                "timeouts_handled": timeouts_handled,
                "cycle_duration_ms": cycle_duration,
                "timestamp": time.time()
            }
            
            span.set_attribute("assignments_made", assignments_made)
            span.set_attribute("cycle_duration_ms", cycle_duration)
            
            # Emit cycle telemetry
            self._emit_coordination_telemetry("coordination_cycle", result)
            
            return result
    
    def _find_best_feature_match(self, capabilities: AgentCapability) -> Optional[FeatureSpec]:
        """Find the best feature match for agent capabilities"""
        if not self.feature_queue:
            return None
        
        # Simple scoring based on priority and estimated effort
        scored_features = []
        
        for feature in self.feature_queue:
            score = 0
            
            # Priority scoring
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            score += priority_scores.get(feature.priority, 1)
            
            # Effort preference
            if capabilities.preferred_complexity == "low" and feature.estimated_effort <= 3:
                score += 2
            elif capabilities.preferred_complexity == "medium" and 3 <= feature.estimated_effort <= 8:
                score += 2
            elif capabilities.preferred_complexity == "high" and feature.estimated_effort >= 8:
                score += 2
            
            scored_features.append((score, feature))
        
        # Return highest scored feature
        scored_features.sort(key=lambda x: x[0], reverse=True)
        return scored_features[0][1] if scored_features else None
    
    def _validate_agent_work(self, agent: WorktreeAgent, validation_results: Dict[str, Any]) -> bool:
        """Validate agent's work in worktree"""
        if not agent.worktree_path or not agent.worktree_path.exists():
            return False
        
        try:
            # Basic validation - check for changes
            status_result = self._run_git_command(
                ["status", "--porcelain"], 
                cwd=agent.worktree_path
            )
            
            has_changes = bool(status_result.stdout.strip())
            
            # Additional validation from results
            validation_passed = validation_results.get("validation_passed", has_changes)
            
            return validation_passed
            
        except subprocess.CalledProcessError:
            return False
    
    def _check_agent_timeouts(self) -> int:
        """Check for agent timeouts and handle them"""
        timeout_threshold = 3600  # 1 hour
        current_time = time.time()
        timeouts_handled = 0
        
        for agent in self.agents.values():
            if (agent.state in [AgentState.WORKING, AgentState.VALIDATING] and 
                current_time - agent.last_activity > timeout_threshold):
                
                logger.warning(f"Agent {agent.agent_id} timed out in state {agent.state}")
                
                # Return feature to queue if needed
                if agent.current_feature:
                    self.feature_queue.append(agent.current_feature)
                    if agent.current_feature.name in self.active_features:
                        del self.active_features[agent.current_feature.name]
                
                # Clean up worktree
                if agent.worktree_path:
                    self.worktrees[str(agent.worktree_path)] = WorktreeStatus.ABANDONED
                
                # Reset agent
                agent.state = AgentState.ERROR
                agent.current_feature = None
                
                # Emit timeout telemetry
                self._emit_agent_telemetry(agent, "agent_timeout")
                
                timeouts_handled += 1
        
        return timeouts_handled
    
    def _calculate_coordination_health(self) -> float:
        """Calculate overall coordination health (0.0-1.0)"""
        if not self.agents:
            return 0.0
        
        # Factors for health calculation
        active_ratio = len([a for a in self.agents.values() if a.state in [AgentState.WORKING, AgentState.VALIDATING]]) / len(self.agents)
        queue_efficiency = max(0.0, 1.0 - (len(self.feature_queue) / max(len(self.agents) * 2, 1)))
        completion_rate = len(self.completed_features) / max(len(self.completed_features) + len(self.active_features), 1)
        
        health = (active_ratio * 0.4 + queue_efficiency * 0.3 + completion_rate * 0.3)
        
        return min(1.0, max(0.0, health))
    
    def _emit_agent_telemetry(self, agent: WorktreeAgent, event_type: str, additional_data: Dict[str, Any] = None):
        """Emit OTEL telemetry for agent events"""
        with self.tracer.start_as_current_span(f"agent.{event_type}") as span:
            span.set_attribute("agent_id", agent.agent_id)
            span.set_attribute("agent_state", agent.state.value)
            span.set_attribute("event_type", event_type)
            
            if agent.current_feature:
                span.set_attribute("feature_name", agent.current_feature.name)
            
            if agent.worktree_path:
                span.set_attribute("worktree_path", str(agent.worktree_path))
            
            if additional_data:
                for key, value in additional_data.items():
                    span.set_attribute(key, str(value))
            
            # Store span ID for agent communication
            agent.telemetry_spans.append(span.get_span_context().span_id)
    
    def _emit_coordination_telemetry(self, event_type: str, data: Dict[str, Any]):
        """Emit coordination-level telemetry"""
        with self.tracer.start_as_current_span(f"coordination.{event_type}") as span:
            span.set_attribute("event_type", event_type)
            
            for key, value in data.items():
                span.set_attribute(key, str(value))
    
    def _run_git_command(self, cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
        """Run git command with error handling"""
        return subprocess.run(
            ["git"] + cmd,
            cwd=cwd or self.base_repo_path,
            capture_output=True,
            text=True,
            check=True
        )
    
    def _save_coordination_state(self):
        """Save coordination state to disk"""
        state = {
            "agents": {
                agent_id: {
                    "agent_id": agent.agent_id,
                    "state": agent.state.value,
                    "current_feature": agent.current_feature.name if agent.current_feature else None,
                    "worktree_path": str(agent.worktree_path) if agent.worktree_path else None,
                    "branch_name": agent.branch_name,
                    "last_activity": agent.last_activity
                }
                for agent_id, agent in self.agents.items()
            },
            "feature_queue": [
                {
                    "name": f.name,
                    "description": f.description,
                    "priority": f.priority,
                    "estimated_effort": f.estimated_effort
                }
                for f in self.feature_queue
            ],
            "active_features": list(self.active_features.keys()),
            "completed_features": [f.name for f in self.completed_features],
            "timestamp": time.time()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)


# Demo and example usage functions
def create_demo_agents() -> List[AgentCapability]:
    """Create demo agents with different capabilities"""
    return [
        AgentCapability(
            agent_id="agent-python-001",
            languages=["python"],
            frameworks=["fastapi", "django", "flask"],
            expertise_areas=["backend", "api", "data-processing"],
            max_concurrent_features=2,
            preferred_complexity="medium"
        ),
        AgentCapability(
            agent_id="agent-frontend-001",
            languages=["typescript", "javascript"],
            frameworks=["react", "vue", "svelte"],
            expertise_areas=["frontend", "ui", "components"],
            max_concurrent_features=1,
            preferred_complexity="low"
        ),
        AgentCapability(
            agent_id="agent-fullstack-001",
            languages=["python", "typescript"],
            frameworks=["fastapi", "react", "postgresql"],
            expertise_areas=["fullstack", "database", "devops"],
            max_concurrent_features=1,
            preferred_complexity="high"
        )
    ]


def create_demo_features() -> List[FeatureSpec]:
    """Create demo feature specifications"""
    return [
        FeatureSpec(
            name="user-authentication",
            description="Implement JWT-based user authentication system",
            requirements=[
                "User registration with email validation",
                "JWT token generation and validation",
                "Password hashing and security",
                "API endpoints for auth operations"
            ],
            acceptance_criteria=[
                "Users can register with valid email",
                "Users can login and receive JWT token",
                "Protected endpoints validate tokens",
                "Tokens expire after configured time"
            ],
            estimated_effort=5,
            priority="high"
        ),
        FeatureSpec(
            name="dashboard-ui",
            description="Create responsive dashboard interface",
            requirements=[
                "Responsive layout with sidebar navigation",
                "Data visualization components",
                "Real-time status updates",
                "Mobile-friendly design"
            ],
            acceptance_criteria=[
                "Dashboard loads within 2 seconds",
                "All components responsive on mobile",
                "Real-time data updates without refresh",
                "Accessible design standards met"
            ],
            estimated_effort=8,
            priority="medium"
        ),
        FeatureSpec(
            name="api-rate-limiting",
            description="Add rate limiting to API endpoints",
            requirements=[
                "Configurable rate limits per endpoint",
                "User-based and IP-based limiting",
                "Rate limit headers in responses",
                "Admin override capabilities"
            ],
            acceptance_criteria=[
                "Rate limits enforced correctly",
                "Proper HTTP status codes returned",
                "Configuration via environment variables",
                "Monitoring and alerting integration"
            ],
            estimated_effort=3,
            priority="low"
        )
    ]


async def run_coordination_demo():
    """Run a complete coordination demo"""
    # Initialize coordinator
    base_repo = Path.cwd()
    coordinator = WorktreeAgentCoordinator(base_repo)
    
    # Register demo agents
    demo_agents = create_demo_agents()
    for agent_capability in demo_agents:
        coordinator.register_agent(agent_capability)
    
    # Add demo features
    demo_features = create_demo_features()
    for feature in demo_features:
        coordinator.add_feature_request(feature)
    
    # Run several coordination cycles
    logger.info("Starting coordination demo...")
    
    for cycle in range(5):
        logger.info(f"Running coordination cycle {cycle + 1}")
        
        result = coordinator.run_coordination_cycle()
        logger.info(f"Cycle result: {result}")
        
        # Simulate agent work
        for agent_id, agent in coordinator.agents.items():
            if agent.state == AgentState.CLAIMING:
                coordinator.agent_start_work(agent_id)
            elif agent.state == AgentState.WORKING:
                # Simulate work completion
                if cycle >= 2:  # After a few cycles
                    coordinator.agent_submit_work(agent_id, {"validation_passed": True})
            elif agent.state == AgentState.SUBMITTING:
                coordinator.complete_feature(agent_id)
        
        # Show status
        status = coordinator.get_coordination_status()
        logger.info(f"Coordination status: {status}")
        
        await asyncio.sleep(1)  # Brief pause between cycles
    
    logger.info("Coordination demo completed!")
    return coordinator


if __name__ == "__main__":
    # Run demo
    asyncio.run(run_coordination_demo())