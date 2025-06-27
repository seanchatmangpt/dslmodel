#!/usr/bin/env python3
"""
Agent Base Class for Worktree Coordination
Each agent operates in isolated worktree with OTEL communication
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    description: str
    feature_id: str
    requirements: Dict[str, Any]
    dependencies: List[str]
    expected_outputs: List[str]
    deadline: Optional[str]
    priority: str  # low, medium, high, critical

@dataclass
class AgentProgress:
    """Agent progress report"""
    agent_id: str
    task_id: str
    feature_id: str
    percentage: float
    status: str  # planning, working, testing, complete, blocked
    current_activity: str
    files_modified: List[str]
    needs_coordination: bool
    coordination_reason: Optional[str]
    timestamp: str

class AgentBase(ABC):
    """Base class for all agents in worktree coordination system"""
    
    def __init__(
        self, 
        agent_id: str,
        capabilities: List[str],
        worktree_coordinator: 'OTELWeaverCoordinator' = None
    ):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.coordinator = worktree_coordinator
        self.console = Console()
        
        # Agent state
        self.current_task: Optional[AgentTask] = None
        self.worktree_path: Optional[Path] = None
        self.current_feature: Optional[str] = None
        self.is_active = False
        
        # OTEL setup
        self.tracer = trace.get_tracer(f"agent.{agent_id}")
        
        # Progress tracking
        self.progress_callbacks: List[Callable] = []
    
    async def initialize_in_worktree(self, worktree_path: Path, feature_id: str):
        """Initialize agent in assigned worktree"""
        
        with self.tracer.start_as_current_span(
            "agent.worktree.initialize",
            attributes={
                "agent.id": self.agent_id,
                "feature.id": feature_id,
                "worktree.path": str(worktree_path)
            }
        ) as span:
            
            self.worktree_path = worktree_path
            self.current_feature = feature_id
            self.is_active = True
            
            # Set up agent workspace in worktree
            await self._setup_agent_workspace()
            
            span.add_event("agent_initialized_in_worktree", {
                "agent_id": self.agent_id,
                "workspace_ready": True
            })
            
            self.console.print(f"🤖 Agent {self.agent_id} initialized in worktree: {worktree_path}")
    
    async def _setup_agent_workspace(self):
        """Set up agent-specific workspace in worktree"""
        if not self.worktree_path:
            return
        
        # Create agent workspace directory
        agent_workspace = self.worktree_path / f".agent_{self.agent_id}"
        agent_workspace.mkdir(exist_ok=True)
        
        # Create agent configuration
        agent_config = {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "initialized_at": datetime.now().isoformat(),
            "feature_id": self.current_feature
        }
        
        config_file = agent_workspace / "agent_config.json"
        with open(config_file, 'w') as f:
            json.dump(agent_config, f, indent=2)
    
    async def accept_task(self, task: AgentTask) -> bool:
        """Accept a task if agent has required capabilities"""
        
        with self.tracer.start_as_current_span(
            "agent.task.accept",
            attributes={
                "agent.id": self.agent_id,
                "task.id": task.task_id,
                "feature.id": task.feature_id
            }
        ) as span:
            
            # Check if agent can handle this task
            can_handle = await self._can_handle_task(task)
            
            if can_handle:
                self.current_task = task
                span.set_attribute("task.accepted", True)
                span.add_event("task_accepted")
                
                self.console.print(f"✅ Agent {self.agent_id} accepted task: {task.description}")
                
                # Start work on task
                await self._start_task_work()
                
            else:
                span.set_attribute("task.accepted", False)
                span.add_event("task_rejected", {
                    "reason": "insufficient_capabilities"
                })
                
                self.console.print(f"❌ Agent {self.agent_id} cannot handle task: {task.description}")
            
            return can_handle
    
    async def _can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle the task"""
        # Check if task requirements match agent capabilities
        required_capabilities = task.requirements.get("capabilities", [])
        return all(cap in self.capabilities for cap in required_capabilities)
    
    async def _start_task_work(self):
        """Start working on accepted task"""
        if not self.current_task:
            return
        
        with self.tracer.start_as_current_span(
            "agent.task.start",
            attributes={
                "agent.id": self.agent_id,
                "task.id": self.current_task.task_id
            }
        ) as span:
            
            # Notify coordinator that work started
            if self.coordinator:
                await self.coordinator.agent_start_feature_work(
                    self.agent_id,
                    self.current_task.feature_id,
                    self.current_task.description
                )
            
            # Start actual work (implemented by subclasses)
            await self.execute_task()
            
            span.add_event("task_work_started")
    
    @abstractmethod
    async def execute_task(self):
        """Execute the assigned task - implemented by subclasses"""
        pass
    
    async def report_progress(self, percentage: float, status: str, activity: str, files_modified: List[str] = None):
        """Report progress to coordination layer"""
        
        progress = AgentProgress(
            agent_id=self.agent_id,
            task_id=self.current_task.task_id if self.current_task else "none",
            feature_id=self.current_feature or "none",
            percentage=percentage,
            status=status,
            current_activity=activity,
            files_modified=files_modified or [],
            needs_coordination=False,
            coordination_reason=None,
            timestamp=datetime.now().isoformat()
        )
        
        with self.tracer.start_as_current_span(
            "agent.progress.report",
            attributes={
                "agent.id": self.agent_id,
                "progress.percentage": percentage,
                "progress.status": status
            }
        ) as span:
            
            # Send to coordinator
            if self.coordinator:
                await self.coordinator.agent_report_progress(
                    self.agent_id,
                    self.current_feature,
                    asdict(progress)
                )
            
            # Call progress callbacks
            for callback in self.progress_callbacks:
                await callback(progress)
            
            span.add_event("progress_reported", asdict(progress))
            
            self.console.print(f"📊 {self.agent_id}: {percentage:.0f}% - {activity}")
    
    async def request_coordination(self, reason: str, coordination_data: Dict[str, Any]):
        """Request coordination with other agents"""
        
        with self.tracer.start_as_current_span(
            "agent.coordination.request",
            attributes={
                "agent.id": self.agent_id,
                "coordination.reason": reason
            }
        ) as span:
            
            progress_data = {
                "needs_coordination": True,
                "coordination_reason": reason,
                "coordination_data": coordination_data,
                "status": "waiting_for_coordination"
            }
            
            if self.coordinator:
                await self.coordinator.agent_report_progress(
                    self.agent_id,
                    self.current_feature,
                    progress_data
                )
            
            span.add_event("coordination_requested", {
                "reason": reason,
                "data": coordination_data
            })
            
            self.console.print(f"🔄 {self.agent_id} requesting coordination: {reason}")
    
    async def complete_task(self, completion_data: Dict[str, Any]):
        """Complete current task"""
        
        if not self.current_task:
            return
        
        with self.tracer.start_as_current_span(
            "agent.task.complete",
            attributes={
                "agent.id": self.agent_id,
                "task.id": self.current_task.task_id,
                "completion.status": completion_data.get("status", "success")
            }
        ) as span:
            
            # Final progress report
            await self.report_progress(100.0, "complete", "Task completed")
            
            # Notify coordinator
            if self.coordinator:
                await self.coordinator.agent_complete_feature(
                    self.agent_id,
                    self.current_feature,
                    completion_data
                )
            
            span.add_event("task_completed", completion_data)
            
            self.console.print(f"✅ {self.agent_id} completed task: {self.current_task.description}")
            
            # Clean up
            self.current_task = None
    
    async def run_command_in_worktree(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run command in agent's worktree"""
        if not self.worktree_path:
            raise RuntimeError("Agent not initialized in worktree")
        
        return subprocess.run(
            command,
            cwd=self.worktree_path,
            capture_output=True,
            text=True,
            check=True
        )
    
    async def read_file_in_worktree(self, file_path: str) -> str:
        """Read file from agent's worktree"""
        if not self.worktree_path:
            raise RuntimeError("Agent not initialized in worktree")
        
        full_path = self.worktree_path / file_path
        with open(full_path, 'r') as f:
            return f.read()
    
    async def write_file_in_worktree(self, file_path: str, content: str):
        """Write file to agent's worktree"""
        if not self.worktree_path:
            raise RuntimeError("Agent not initialized in worktree")
        
        full_path = self.worktree_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        # Track file modification
        await self.report_progress(
            self._calculate_progress(),
            "working",
            f"Modified {file_path}",
            [file_path]
        )
    
    def _calculate_progress(self) -> float:
        """Calculate current task progress - can be overridden by subclasses"""
        # Simple default implementation
        if not self.current_task:
            return 0.0
        
        # Basic progress based on time or other factors
        return 50.0  # Placeholder
    
    def add_progress_callback(self, callback: Callable):
        """Add callback for progress updates"""
        self.progress_callbacks.append(callback)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "current_feature": self.current_feature,
            "worktree_path": str(self.worktree_path) if self.worktree_path else None,
            "current_task": asdict(self.current_task) if self.current_task else None
        }