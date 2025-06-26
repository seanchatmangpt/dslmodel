#!/usr/bin/env python3
"""
Agent Worktree Pipeline - Implementation using Generated Models
Built on weaver-generated semantic conventions for agent coordination
"""

import subprocess
import os
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
import time
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .generated.worktree_models import (
    WorktreeSpanFactory,
    AgentWorktreeCreateSpan,
    AgentWorktreeActivateSpan,
    AgentCoordinationRequestSpan,
    AgentCoordinationResponseSpan,
    AgentTaskStartSpan,
    AgentTaskProgressSpan,
    AgentTaskCompleteSpan,
    FeatureIntegrationStartSpan,
    FeatureIntegrationMergeSpan,
    FeatureIntegrationCompleteSpan,
    create_worktree_span,
    create_coordination_request,
    create_task_progress,
    create_integration_merge
)

class AgentWorktreePipeline:
    """
    Manages agent worktrees with full OTEL coordination
    Uses weaver-generated models for all telemetry
    """
    
    def __init__(self, base_repo_path: str, worktree_base: str = "worktrees"):
        self.base_repo_path = Path(base_repo_path)
        self.worktree_base = Path(worktree_base)
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.active_worktrees: Dict[str, Dict[str, Any]] = {}
        self.coordination_channels: Dict[str, List[str]] = {}
        
        # Ensure worktree directory exists
        self.worktree_base.mkdir(exist_ok=True)
    
    async def create_agent_worktree(self, agent_id: str, feature_id: str, branch_name: str) -> str:
        """Create isolated worktree for agent using generated telemetry"""
        worktree_path = self.worktree_base / f"{agent_id}_{feature_id}"
        
        # Create worktree with telemetry
        span_data = AgentWorktreeCreateSpan(
            agent_id=agent_id,
            worktree_path=str(worktree_path),
            feature_id=feature_id,
            branch_name=branch_name
        )
        
        span = span_data.start_span()
        start_time = time.time()
        
        try:
            # Create git worktree
            cmd = [
                "git", "worktree", "add", 
                str(worktree_path), 
                f"-b", branch_name
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.base_repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Calculate startup duration
            duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("worktree.startup.duration_ms", duration_ms)
            
            # Store worktree info
            self.active_worktrees[agent_id] = {
                "path": str(worktree_path),
                "feature_id": feature_id,
                "branch_name": branch_name,
                "created_at": datetime.now(),
                "span_id": span_data.span_id,
                "trace_id": span_data.trace_id
            }
            
            span_data.end_span(span, success=True)
            return str(worktree_path)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create worktree: {e.stderr}"
            span_data.end_span(span, success=False, error=error_msg)
            raise RuntimeError(error_msg)
    
    async def activate_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        """Activate agent in assigned worktree with telemetry"""
        if agent_id not in self.active_worktrees:
            raise ValueError(f"No worktree found for agent {agent_id}")
        
        worktree_info = self.active_worktrees[agent_id]
        
        # Create activation span
        span_data = AgentWorktreeActivateSpan(
            agent_id=agent_id,
            worktree_path=worktree_info["path"],
            capabilities=capabilities
        )
        
        span = span_data.start_span()
        
        try:
            # Store agent info
            self.active_agents[agent_id] = {
                "worktree_path": worktree_info["path"],
                "feature_id": worktree_info["feature_id"],
                "capabilities": capabilities,
                "activated_at": datetime.now(),
                "current_task": None,
                "span_id": span_data.span_id,
                "trace_id": span_data.trace_id
            }
            
            span_data.end_span(span, success=True)
            return True
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def assign_task(self, agent_id: str, task_id: str, task_description: str, estimated_duration_ms: float = None) -> bool:
        """Assign task to agent with telemetry tracking"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not activated")
        
        # Create task start span
        span_data = AgentTaskStartSpan(
            agent_id=agent_id,
            task_id=task_id,
            task_description=task_description,
            estimated_duration_ms=estimated_duration_ms
        )
        
        span = span_data.start_span()
        
        try:
            # Update agent state
            self.active_agents[agent_id]["current_task"] = {
                "task_id": task_id,
                "description": task_description,
                "started_at": datetime.now(),
                "estimated_duration_ms": estimated_duration_ms,
                "progress": 0.0,
                "span_id": span_data.span_id,
                "trace_id": span_data.trace_id
            }
            
            span_data.end_span(span, success=True)
            return True
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def report_progress(self, agent_id: str, task_id: str, percentage: float, current_activity: str, files_modified: List[str] = None) -> bool:
        """Agent reports task progress with telemetry"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not activated")
        
        # Create progress span
        span_data = AgentTaskProgressSpan(
            agent_id=agent_id,
            task_id=task_id,
            progress_percentage=percentage,
            current_activity=current_activity,
            files_modified=files_modified or []
        )
        
        span = span_data.start_span()
        
        try:
            # Update agent progress
            if self.active_agents[agent_id]["current_task"]:
                self.active_agents[agent_id]["current_task"]["progress"] = percentage
                self.active_agents[agent_id]["current_task"]["last_activity"] = current_activity
                self.active_agents[agent_id]["current_task"]["last_update"] = datetime.now()
            
            span_data.end_span(span, success=True)
            return True
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def request_coordination(self, requesting_agent: str, target_agents: List[str], reason: str) -> str:
        """Agent requests coordination with other agents"""
        coordination_id = str(uuid.uuid4())
        channel = f"coordination_{coordination_id}"
        
        # Create coordination request span
        span_data = AgentCoordinationRequestSpan(
            requesting_agent=requesting_agent,
            target_agents=target_agents,
            coordination_reason=reason,
            coordination_channel=channel
        )
        
        span = span_data.start_span()
        
        try:
            # Store coordination request
            self.coordination_channels[coordination_id] = {
                "requesting_agent": requesting_agent,
                "target_agents": target_agents,
                "reason": reason,
                "channel": channel,
                "created_at": datetime.now(),
                "responses": {},
                "span_id": span_data.span_id,
                "trace_id": span_data.trace_id
            }
            
            span_data.end_span(span, success=True)
            return coordination_id
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def respond_to_coordination(self, responding_agent: str, coordination_id: str, response_type: str) -> bool:
        """Agent responds to coordination request"""
        if coordination_id not in self.coordination_channels:
            raise ValueError(f"Unknown coordination request: {coordination_id}")
        
        coord_info = self.coordination_channels[coordination_id]
        requesting_agent = coord_info["requesting_agent"]
        
        # Create coordination response span
        span_data = AgentCoordinationResponseSpan(
            responding_agent=responding_agent,
            requesting_agent=requesting_agent,
            response_type=response_type
        )
        
        span = span_data.start_span()
        
        try:
            # Store response
            coord_info["responses"][responding_agent] = {
                "response_type": response_type,
                "responded_at": datetime.now(),
                "span_id": span_data.span_id,
                "trace_id": span_data.trace_id
            }
            
            span_data.end_span(span, success=True)
            return True
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def complete_task(self, agent_id: str, task_id: str, completion_status: str, files_created: List[str] = None) -> bool:
        """Agent completes assigned task"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not activated")
        
        task_info = self.active_agents[agent_id].get("current_task")
        if not task_info or task_info["task_id"] != task_id:
            raise ValueError(f"Task {task_id} not found for agent {agent_id}")
        
        # Calculate actual duration
        started_at = task_info["started_at"]
        actual_duration_ms = (datetime.now() - started_at).total_seconds() * 1000
        
        # Create task completion span
        span_data = AgentTaskCompleteSpan(
            agent_id=agent_id,
            task_id=task_id,
            completion_status=completion_status,
            actual_duration_ms=actual_duration_ms,
            files_created=files_created or []
        )
        
        span = span_data.start_span()
        
        try:
            # Update agent state
            self.active_agents[agent_id]["current_task"]["completed_at"] = datetime.now()
            self.active_agents[agent_id]["current_task"]["completion_status"] = completion_status
            self.active_agents[agent_id]["current_task"]["files_created"] = files_created or []
            
            # Commit work if successful
            if completion_status == "success":
                await self._commit_agent_work(agent_id)
            
            span_data.end_span(span, success=True)
            return True
            
        except Exception as e:
            span_data.end_span(span, success=False, error=str(e))
            raise
    
    async def integrate_feature(self, feature_id: str, contributing_agents: List[str], integration_strategy: str = "sequential") -> bool:
        """Integrate work from multiple agents into feature"""
        
        # Start integration process
        span_data = FeatureIntegrationStartSpan(
            feature_id=feature_id,
            contributing_agents=contributing_agents,
            integration_strategy=integration_strategy
        )
        
        integration_span = span_data.start_span()
        start_time = time.time()
        
        try:
            successful_agents = []
            failed_agents = []
            
            # Merge each agent's work
            for agent_id in contributing_agents:
                success = await self._merge_agent_work(agent_id, feature_id)
                if success:
                    successful_agents.append(agent_id)
                else:
                    failed_agents.append(agent_id)
            
            # Calculate integration duration
            integration_duration_ms = (time.time() - start_time) * 1000
            
            # Determine final status
            if not failed_agents:
                final_status = "success"
            elif successful_agents:
                final_status = "partial"
            else:
                final_status = "failed"
            
            # Complete integration
            completion_span_data = FeatureIntegrationCompleteSpan(
                feature_id=feature_id,
                integration_duration_ms=integration_duration_ms,
                agents_successful=successful_agents,
                agents_failed=failed_agents,
                final_status=final_status
            )
            
            completion_span = completion_span_data.start_span()
            completion_span_data.end_span(completion_span, success=(final_status != "failed"))
            
            span_data.end_span(integration_span, success=True)
            return final_status == "success"
            
        except Exception as e:
            span_data.end_span(integration_span, success=False, error=str(e))
            raise
    
    async def _commit_agent_work(self, agent_id: str) -> bool:
        """Commit agent's work in their worktree"""
        if agent_id not in self.active_worktrees:
            return False
        
        worktree_info = self.active_worktrees[agent_id]
        worktree_path = worktree_info["path"]
        
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=worktree_path, check=True)
            
            # Commit with agent info
            commit_msg = f"Agent {agent_id} completed task in feature {worktree_info['feature_id']}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg], 
                cwd=worktree_path, 
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    async def _merge_agent_work(self, agent_id: str, feature_id: str) -> bool:
        """Merge agent's worktree into main branch"""
        if agent_id not in self.active_worktrees:
            return False
        
        worktree_info = self.active_worktrees[agent_id]
        source_branch = worktree_info["branch_name"]
        target_branch = "main"
        
        # Create merge span
        span_data = FeatureIntegrationMergeSpan(
            agent_id=agent_id,
            source_branch=source_branch,
            target_branch=target_branch,
            merge_conflicts=0,
            merge_strategy="merge"
        )
        
        span = span_data.start_span()
        
        try:
            # Switch to main branch
            subprocess.run(
                ["git", "checkout", target_branch], 
                cwd=self.base_repo_path, 
                check=True
            )
            
            # Merge the feature branch
            result = subprocess.run(
                ["git", "merge", source_branch], 
                cwd=self.base_repo_path,
                capture_output=True,
                text=True
            )
            
            # Check for merge conflicts
            conflicts = 0
            if result.returncode != 0:
                # Count conflicts (simplified)
                conflicts = result.stderr.count("CONFLICT")
                span.set_attribute("merge.conflicts", conflicts)
            
            span_data.end_span(span, success=(result.returncode == 0))
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            span_data.end_span(span, success=False, error=str(e))
            return False
    
    async def cleanup_worktree(self, agent_id: str) -> bool:
        """Clean up agent's worktree after integration"""
        if agent_id not in self.active_worktrees:
            return False
        
        worktree_info = self.active_worktrees[agent_id]
        worktree_path = worktree_info["path"]
        
        try:
            # Remove git worktree
            subprocess.run(
                ["git", "worktree", "remove", worktree_path], 
                cwd=self.base_repo_path, 
                check=True
            )
            
            # Clean up tracking
            del self.active_worktrees[agent_id]
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
            
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of agent"""
        if agent_id not in self.active_agents:
            return None
        
        agent_info = self.active_agents[agent_id].copy()
        if agent_id in self.active_worktrees:
            agent_info.update(self.active_worktrees[agent_id])
        
        return agent_info
    
    def get_coordination_status(self, coordination_id: str) -> Optional[Dict[str, Any]]:
        """Get status of coordination request"""
        return self.coordination_channels.get(coordination_id)

# Example usage and testing functions
async def example_workflow():
    """Example workflow using the pipeline"""
    pipeline = AgentWorktreePipeline("/Users/sac/dev/dslmodel")
    
    # Create worktrees for multiple agents
    feature_id = "new_authentication_system"
    
    agent1_path = await pipeline.create_agent_worktree("agent_backend", feature_id, "auth_backend")
    agent2_path = await pipeline.create_agent_worktree("agent_frontend", feature_id, "auth_frontend")
    
    # Activate agents
    await pipeline.activate_agent("agent_backend", ["python", "fastapi", "authentication"])
    await pipeline.activate_agent("agent_frontend", ["react", "typescript", "ui"])
    
    # Assign tasks
    await pipeline.assign_task("agent_backend", "task_1", "Implement JWT authentication", 3600000)
    await pipeline.assign_task("agent_frontend", "task_2", "Create login UI components", 2400000)
    
    # Simulate progress updates
    await pipeline.report_progress("agent_backend", "task_1", 25.0, "Setting up JWT library", ["auth/jwt.py"])
    await pipeline.report_progress("agent_frontend", "task_2", 50.0, "Creating login form", ["components/Login.tsx"])
    
    # Request coordination between agents
    coord_id = await pipeline.request_coordination(
        "agent_backend", 
        ["agent_frontend"], 
        "Need to coordinate API endpoint structure"
    )
    
    # Frontend agent responds
    await pipeline.respond_to_coordination("agent_frontend", coord_id, "accept")
    
    # Complete tasks
    await pipeline.complete_task("agent_backend", "task_1", "success", ["auth/jwt.py", "auth/routes.py"])
    await pipeline.complete_task("agent_frontend", "task_2", "success", ["components/Login.tsx", "components/Register.tsx"])
    
    # Integrate feature
    success = await pipeline.integrate_feature(feature_id, ["agent_backend", "agent_frontend"])
    
    # Cleanup
    await pipeline.cleanup_worktree("agent_backend")
    await pipeline.cleanup_worktree("agent_frontend")
    
    return success

if __name__ == "__main__":
    # Run example workflow
    result = asyncio.run(example_workflow())
    print(f"Workflow completed successfully: {result}")