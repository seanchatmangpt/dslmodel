#!/usr/bin/env python3
"""
Core Agent System - 80/20 approach
The essential 20% of capabilities that deliver 80% of value
"""

import subprocess
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Essential OTEL - just what we need
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Setup OTEL once
if not hasattr(trace, '_initialized'):
    resource = Resource(attributes={SERVICE_NAME: "agent-core-system"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(console_processor)
    trace._initialized = True

tracer = trace.get_tracer(__name__)

@dataclass
class AgentWork:
    """Simple agent work tracking"""
    agent_id: str
    task: str
    worktree_path: str
    progress: float = 0.0
    status: str = "active"  # active, completed, failed
    
class CoreAgentSystem:
    """
    Core agent system - just the essentials
    Agents work in isolated worktrees with OTEL observability
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.agents: Dict[str, AgentWork] = {}
        self.worktree_base = Path("agent_worktrees")
        self.worktree_base.mkdir(exist_ok=True)
    
    def assign_agent(self, agent_id: str, task: str) -> str:
        """Assign task to agent with isolated worktree - core capability #1"""
        
        with tracer.start_as_current_span("agent.assign") as span:
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("task", task)
            
            try:
                # Create isolated worktree
                worktree_path = self.worktree_base / f"{agent_id}_{int(time.time())}"
                branch_name = f"agent-{agent_id}-{int(time.time())}"
                
                # Git worktree creation
                subprocess.run([
                    "git", "worktree", "add", 
                    str(worktree_path), 
                    "-b", branch_name
                ], cwd=self.repo_path, check=True, capture_output=True)
                
                # Track agent
                self.agents[agent_id] = AgentWork(
                    agent_id=agent_id,
                    task=task,
                    worktree_path=str(worktree_path)
                )
                
                span.set_attribute("worktree.path", str(worktree_path))
                span.set_attribute("branch.name", branch_name)
                
                return str(worktree_path)
                
            except Exception as e:
                span.record_exception(e)
                raise
    
    def report_progress(self, agent_id: str, progress: float, activity: str = "") -> bool:
        """Agent reports progress - core capability #2"""
        
        with tracer.start_as_current_span("agent.progress") as span:
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("progress", progress)
            span.set_attribute("activity", activity)
            
            if agent_id not in self.agents:
                span.record_exception(ValueError(f"Unknown agent: {agent_id}"))
                return False
            
            # Update progress
            self.agents[agent_id].progress = progress
            
            return True
    
    def complete_work(self, agent_id: str, files_changed: List[str] = None) -> bool:
        """Agent completes work and commits - core capability #3"""
        
        with tracer.start_as_current_span("agent.complete") as span:
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("files.count", len(files_changed or []))
            
            if agent_id not in self.agents:
                span.record_exception(ValueError(f"Unknown agent: {agent_id}"))
                return False
            
            agent = self.agents[agent_id]
            worktree_path = agent.worktree_path
            
            try:
                # Commit work
                subprocess.run(["git", "add", "."], cwd=worktree_path, check=True)
                
                commit_msg = f"Agent {agent_id}: {agent.task}"
                subprocess.run([
                    "git", "commit", "-m", commit_msg
                ], cwd=worktree_path, check=True)
                
                # Update status
                agent.status = "completed"
                agent.progress = 100.0
                
                span.set_attribute("commit.message", commit_msg)
                
                return True
                
            except subprocess.CalledProcessError as e:
                agent.status = "failed"
                span.record_exception(e)
                return False
    
    def coordinate_agents(self, requesting_agent: str, target_agents: List[str], message: str) -> bool:
        """Simple agent coordination - core capability #4"""
        
        with tracer.start_as_current_span("agent.coordinate") as span:
            span.set_attribute("requesting.agent", requesting_agent)
            span.set_attribute("target.agents", target_agents)
            span.set_attribute("message", message)
            
            # Simple coordination - just log it
            # In practice, this would send messages/notifications
            
            coordination_id = f"coord_{int(time.time())}"
            span.set_attribute("coordination.id", coordination_id)
            
            return True
    
    def merge_agent_work(self, agent_id: str, target_branch: str = "main") -> bool:
        """Merge completed agent work"""
        
        with tracer.start_as_current_span("agent.merge") as span:
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("target.branch", target_branch)
            
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            if agent.status != "completed":
                return False
            
            try:
                # Get the branch name from worktree
                result = subprocess.run([
                    "git", "branch", "--show-current"
                ], cwd=agent.worktree_path, capture_output=True, text=True, check=True)
                
                branch_name = result.stdout.strip()
                
                # Switch to target branch and merge
                subprocess.run([
                    "git", "checkout", target_branch
                ], cwd=self.repo_path, check=True)
                
                subprocess.run([
                    "git", "merge", branch_name
                ], cwd=self.repo_path, check=True)
                
                span.set_attribute("source.branch", branch_name)
                
                return True
                
            except subprocess.CalledProcessError as e:
                span.record_exception(e)
                return False
    
    def cleanup_agent(self, agent_id: str) -> bool:
        """Clean up agent worktree"""
        
        with tracer.start_as_current_span("agent.cleanup") as span:
            span.set_attribute("agent.id", agent_id)
            
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            try:
                # Remove worktree
                subprocess.run([
                    "git", "worktree", "remove", agent.worktree_path
                ], cwd=self.repo_path, check=True)
                
                # Remove from tracking
                del self.agents[agent_id]
                
                return True
                
            except subprocess.CalledProcessError as e:
                span.record_exception(e)
                return False
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "task": agent.task,
            "progress": agent.progress,
            "status": agent.status,
            "worktree_path": agent.worktree_path
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [self.get_agent_status(agent_id) for agent_id in self.agents.keys()]

# Simple usage example
def example_usage():
    """Example of core agent system usage"""
    
    # Initialize system
    system = CoreAgentSystem("/Users/sac/dev/dslmodel")
    
    # Assign work to agents
    path1 = system.assign_agent("backend_agent", "Implement auth API")
    path2 = system.assign_agent("frontend_agent", "Create login UI")
    
    print(f"Backend agent working in: {path1}")
    print(f"Frontend agent working in: {path2}")
    
    # Simulate work with progress updates
    system.report_progress("backend_agent", 25.0, "Setting up API structure")
    system.report_progress("frontend_agent", 30.0, "Creating login form")
    
    # Simple coordination
    system.coordinate_agents(
        "backend_agent", 
        ["frontend_agent"], 
        "API endpoints ready for integration"
    )
    
    # More progress
    system.report_progress("backend_agent", 75.0, "Implementing JWT")
    system.report_progress("frontend_agent", 80.0, "Connecting to API")
    
    # Complete work
    system.complete_work("backend_agent", ["auth/api.py", "auth/models.py"])
    system.complete_work("frontend_agent", ["components/Login.tsx"])
    
    # Check status
    for agent in system.list_agents():
        print(f"Agent {agent['agent_id']}: {agent['progress']:.0f}% - {agent['status']}")
    
    # Merge work
    system.merge_agent_work("backend_agent")
    system.merge_agent_work("frontend_agent")
    
    # Cleanup
    system.cleanup_agent("backend_agent")
    system.cleanup_agent("frontend_agent")
    
    print("✓ Core agent workflow completed")

if __name__ == "__main__":
    example_usage()