#!/usr/bin/env python3
"""
Agent Worktree Coordinator
Uses git worktrees for feature isolation with OTEL weaver coordination
"""

import asyncio
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

@dataclass
class AgentWorktree:
    """Agent-specific git worktree"""
    agent_id: str
    feature_name: str
    worktree_path: Path
    branch_name: str
    status: str  # active, working, complete, merged, failed
    created_at: str
    last_activity: str
    coordination_span_id: str
    telemetry_context: Dict[str, Any]

@dataclass
class FeatureCoordination:
    """Feature coordination metadata"""
    feature_id: str
    description: str
    assigned_agents: List[str]
    worktrees: List[AgentWorktree]
    coordination_channel: str  # OTEL span name for coordination
    status: str  # planning, active, integration, complete
    created_at: str
    deadline: Optional[str]
    dependencies: List[str]

class OTELWeaverCoordinator:
    """OTEL-based coordination layer for agent worktrees"""
    
    def __init__(self, project_root: Path, coordination_service: str = "agent-worktree-coordinator"):
        self.project_root = project_root
        self.coordination_service = coordination_service
        self.console = Console()
        
        # Initialize OTEL
        self._init_telemetry()
        self.tracer = trace.get_tracer(__name__)
        
        # Coordination state
        self.active_features: Dict[str, FeatureCoordination] = {}
        self.agent_worktrees: Dict[str, List[AgentWorktree]] = {}
        
        # Semantic conventions for coordination
        self.coordination_conventions = {
            "agent.worktree.create": "Create isolated agent worktree",
            "agent.worktree.activate": "Activate agent in worktree",
            "agent.feature.start": "Agent starts feature work",
            "agent.feature.progress": "Agent reports feature progress", 
            "agent.feature.complete": "Agent completes feature work",
            "agent.coordination.sync": "Cross-agent coordination sync",
            "feature.integration.start": "Start feature integration",
            "feature.integration.complete": "Complete feature integration"
        }
    
    def _init_telemetry(self):
        """Initialize OpenTelemetry for agent coordination"""
        resource = Resource.create({
            "service.name": self.coordination_service,
            "service.version": "1.0.0",
            "deployment.environment": "development"
        })
        
        provider = TracerProvider(resource=resource)
        
        # Console exporter for development
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        trace.set_tracer_provider(provider)
    
    async def create_feature_coordination(
        self, 
        feature_id: str, 
        description: str,
        agent_assignments: List[str],
        dependencies: List[str] = None
    ) -> FeatureCoordination:
        """Create new feature with agent coordination"""
        
        with self.tracer.start_as_current_span(
            "feature.coordination.create",
            attributes={
                "feature.id": feature_id,
                "feature.description": description,
                "agents.count": len(agent_assignments),
                "coordination.method": "otel_weaver"
            }
        ) as span:
            
            coordination = FeatureCoordination(
                feature_id=feature_id,
                description=description,
                assigned_agents=agent_assignments,
                worktrees=[],
                coordination_channel=f"feature.{feature_id}.coordination",
                status="planning",
                created_at=datetime.now().isoformat(),
                deadline=None,
                dependencies=dependencies or []
            )
            
            self.active_features[feature_id] = coordination
            
            # Create worktrees for each agent
            for agent_id in agent_assignments:
                worktree = await self._create_agent_worktree(
                    agent_id, feature_id, coordination
                )
                coordination.worktrees.append(worktree)
                
                if agent_id not in self.agent_worktrees:
                    self.agent_worktrees[agent_id] = []
                self.agent_worktrees[agent_id].append(worktree)
            
            coordination.status = "active"
            
            span.set_attribute("worktrees.created", len(coordination.worktrees))
            span.add_event("feature_coordination_created", {
                "feature_id": feature_id,
                "agents": agent_assignments
            })
            
            self.console.print(f"🚀 Created feature coordination: {feature_id}")
            self.console.print(f"👥 Agents: {', '.join(agent_assignments)}")
            
            return coordination
    
    async def _create_agent_worktree(
        self, 
        agent_id: str, 
        feature_id: str,
        coordination: FeatureCoordination
    ) -> AgentWorktree:
        """Create isolated git worktree for agent"""
        
        with self.tracer.start_as_current_span(
            "agent.worktree.create",
            attributes={
                "agent.id": agent_id,
                "feature.id": feature_id,
                "worktree.isolation": "git_worktree"
            }
        ) as span:
            
            # Generate branch and worktree names
            branch_name = f"feature/{feature_id}/{agent_id}"
            worktree_name = f"worktree-{agent_id}-{feature_id}"
            worktree_path = self.project_root / "worktrees" / worktree_name
            
            # Create git worktree
            try:
                # Ensure worktrees directory exists
                worktree_path.parent.mkdir(exist_ok=True)
                
                # Create new branch from main
                subprocess.run([
                    "git", "checkout", "-b", branch_name, "main"
                ], cwd=self.project_root, check=True, capture_output=True)
                
                # Create worktree
                subprocess.run([
                    "git", "worktree", "add", str(worktree_path), branch_name
                ], cwd=self.project_root, check=True, capture_output=True)
                
                worktree = AgentWorktree(
                    agent_id=agent_id,
                    feature_name=feature_id,
                    worktree_path=worktree_path,
                    branch_name=branch_name,
                    status="active",
                    created_at=datetime.now().isoformat(),
                    last_activity=datetime.now().isoformat(),
                    coordination_span_id=span.get_span_context().span_id,
                    telemetry_context={
                        "coordination_channel": coordination.coordination_channel,
                        "feature_id": feature_id
                    }
                )
                
                span.set_attribute("worktree.path", str(worktree_path))
                span.set_attribute("branch.name", branch_name)
                span.add_event("agent_worktree_created")
                
                self.console.print(f"  📁 Created worktree for {agent_id}: {worktree_path}")
                
                return worktree
                
            except subprocess.CalledProcessError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                raise RuntimeError(f"Failed to create worktree for {agent_id}: {e}")
    
    async def agent_start_feature_work(
        self, 
        agent_id: str, 
        feature_id: str,
        work_description: str
    ):
        """Agent starts work on feature in isolated worktree"""
        
        with self.tracer.start_as_current_span(
            "agent.feature.start",
            attributes={
                "agent.id": agent_id,
                "feature.id": feature_id,
                "work.description": work_description
            }
        ) as span:
            
            # Find agent's worktree
            worktree = self._find_agent_worktree(agent_id, feature_id)
            if not worktree:
                raise ValueError(f"No worktree found for agent {agent_id} on feature {feature_id}")
            
            # Update worktree status
            worktree.status = "working"
            worktree.last_activity = datetime.now().isoformat()
            
            # Create coordination context
            coordination_context = {
                "agent_id": agent_id,
                "feature_id": feature_id,
                "work_description": work_description,
                "worktree_path": str(worktree.worktree_path),
                "coordination_channel": worktree.telemetry_context["coordination_channel"]
            }
            
            span.add_event("agent_work_started", coordination_context)
            
            self.console.print(f"🔧 Agent {agent_id} started work on {feature_id}")
            self.console.print(f"📍 Worktree: {worktree.worktree_path}")
            
            return coordination_context
    
    async def agent_report_progress(
        self,
        agent_id: str,
        feature_id: str,
        progress_data: Dict[str, Any]
    ):
        """Agent reports progress through OTEL coordination layer"""
        
        with self.tracer.start_as_current_span(
            "agent.feature.progress",
            attributes={
                "agent.id": agent_id,
                "feature.id": feature_id,
                "progress.percentage": progress_data.get("percentage", 0),
                "progress.status": progress_data.get("status", "unknown")
            }
        ) as span:
            
            worktree = self._find_agent_worktree(agent_id, feature_id)
            if worktree:
                worktree.last_activity = datetime.now().isoformat()
            
            # Emit coordination event
            coordination_event = {
                "agent_id": agent_id,
                "feature_id": feature_id,
                "timestamp": datetime.now().isoformat(),
                "progress": progress_data
            }
            
            span.add_event("agent_progress_reported", coordination_event)
            
            # Check for cross-agent coordination needs
            await self._check_coordination_triggers(feature_id, progress_data)
            
            self.console.print(f"📊 Progress from {agent_id}: {progress_data.get('status', 'working')}")
    
    async def agent_complete_feature(
        self,
        agent_id: str,
        feature_id: str,
        completion_data: Dict[str, Any]
    ):
        """Agent completes feature work"""
        
        with self.tracer.start_as_current_span(
            "agent.feature.complete",
            attributes={
                "agent.id": agent_id,
                "feature.id": feature_id,
                "completion.status": completion_data.get("status", "success")
            }
        ) as span:
            
            worktree = self._find_agent_worktree(agent_id, feature_id)
            if not worktree:
                raise ValueError(f"No worktree found for agent {agent_id}")
            
            # Update worktree status
            worktree.status = "complete"
            worktree.last_activity = datetime.now().isoformat()
            
            # Commit and push changes
            await self._commit_agent_work(worktree, completion_data)
            
            span.add_event("agent_feature_completed", {
                "agent_id": agent_id,
                "feature_id": feature_id,
                "completion_data": completion_data
            })
            
            # Check if all agents completed
            await self._check_feature_integration_ready(feature_id)
            
            self.console.print(f"✅ Agent {agent_id} completed work on {feature_id}")
    
    async def _commit_agent_work(self, worktree: AgentWorktree, completion_data: Dict[str, Any]):
        """Commit agent's work in their worktree"""
        
        try:
            # Add all changes
            subprocess.run([
                "git", "add", "."
            ], cwd=worktree.worktree_path, check=True)
            
            # Commit with coordination metadata
            commit_message = f"""Agent {worktree.agent_id}: {completion_data.get('summary', 'Feature work completed')}

Feature: {worktree.feature_name}
Agent: {worktree.agent_id}
Status: {completion_data.get('status', 'success')}
Coordination-Span-ID: {worktree.coordination_span_id}

🤖 Generated with Agent Worktree Coordinator
"""
            
            subprocess.run([
                "git", "commit", "-m", commit_message
            ], cwd=worktree.worktree_path, check=True)
            
            # Push to remote
            subprocess.run([
                "git", "push", "origin", worktree.branch_name
            ], cwd=worktree.worktree_path, check=True)
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Failed to commit work for {worktree.agent_id}: {e}")
            raise
    
    async def _check_coordination_triggers(self, feature_id: str, progress_data: Dict[str, Any]):
        """Check if coordination between agents is needed"""
        
        if progress_data.get("needs_coordination"):
            with self.tracer.start_as_current_span(
                "agent.coordination.sync",
                attributes={
                    "feature.id": feature_id,
                    "coordination.trigger": progress_data.get("coordination_reason", "unspecified")
                }
            ) as span:
                
                coordination = self.active_features.get(feature_id)
                if coordination:
                    # Notify all agents in feature
                    span.add_event("cross_agent_coordination_triggered", {
                        "feature_id": feature_id,
                        "agents": coordination.assigned_agents,
                        "reason": progress_data.get("coordination_reason")
                    })
                    
                    self.console.print(f"🔄 Cross-agent coordination triggered for {feature_id}")
    
    async def _check_feature_integration_ready(self, feature_id: str):
        """Check if feature is ready for integration"""
        
        coordination = self.active_features.get(feature_id)
        if not coordination:
            return
        
        # Check if all agents completed
        completed_agents = [
            w.agent_id for w in coordination.worktrees 
            if w.status == "complete"
        ]
        
        if len(completed_agents) == len(coordination.assigned_agents):
            await self.start_feature_integration(feature_id)
    
    async def start_feature_integration(self, feature_id: str):
        """Start integration of completed agent work"""
        
        with self.tracer.start_as_current_span(
            "feature.integration.start",
            attributes={
                "feature.id": feature_id,
                "integration.method": "git_merge"
            }
        ) as span:
            
            coordination = self.active_features[feature_id]
            coordination.status = "integration"
            
            self.console.print(f"🔀 Starting integration for feature {feature_id}")
            
            # Create integration branch
            integration_branch = f"integration/{feature_id}"
            
            try:
                subprocess.run([
                    "git", "checkout", "-b", integration_branch, "main"
                ], cwd=self.project_root, check=True, capture_output=True)
                
                # Merge each agent's work
                for worktree in coordination.worktrees:
                    if worktree.status == "complete":
                        subprocess.run([
                            "git", "merge", "--no-ff", worktree.branch_name,
                            "-m", f"Integrate {worktree.agent_id} work for {feature_id}"
                        ], cwd=self.project_root, check=True, capture_output=True)
                        
                        self.console.print(f"  ✅ Merged {worktree.agent_id}'s work")
                
                span.add_event("feature_integration_completed")
                coordination.status = "complete"
                
                self.console.print(f"🎉 Feature {feature_id} integration complete!")
                
            except subprocess.CalledProcessError as e:
                span.record_exception(e)
                coordination.status = "integration_failed"
                self.console.print(f"❌ Integration failed for {feature_id}: {e}")
    
    def _find_agent_worktree(self, agent_id: str, feature_id: str) -> Optional[AgentWorktree]:
        """Find agent's worktree for specific feature"""
        agent_worktrees = self.agent_worktrees.get(agent_id, [])
        for worktree in agent_worktrees:
            if worktree.feature_name == feature_id:
                return worktree
        return None
    
    async def cleanup_feature_worktrees(self, feature_id: str):
        """Clean up worktrees after feature completion"""
        
        with self.tracer.start_as_current_span(
            "feature.worktrees.cleanup",
            attributes={"feature.id": feature_id}
        ) as span:
            
            coordination = self.active_features.get(feature_id)
            if not coordination:
                return
            
            for worktree in coordination.worktrees:
                try:
                    # Remove worktree
                    subprocess.run([
                        "git", "worktree", "remove", str(worktree.worktree_path)
                    ], cwd=self.project_root, check=True, capture_output=True)
                    
                    # Delete branch
                    subprocess.run([
                        "git", "branch", "-D", worktree.branch_name
                    ], cwd=self.project_root, check=True, capture_output=True)
                    
                    self.console.print(f"🗑️ Cleaned up worktree for {worktree.agent_id}")
                    
                except subprocess.CalledProcessError as e:
                    self.console.print(f"⚠️ Cleanup warning for {worktree.agent_id}: {e}")
            
            # Remove from active features
            del self.active_features[feature_id]
            
            span.add_event("feature_worktrees_cleaned")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""
        
        status = {
            "active_features": len(self.active_features),
            "total_agents": len(self.agent_worktrees),
            "total_worktrees": sum(len(wt) for wt in self.agent_worktrees.values()),
            "features": {}
        }
        
        for feature_id, coordination in self.active_features.items():
            status["features"][feature_id] = {
                "status": coordination.status,
                "agents": coordination.assigned_agents,
                "worktrees_status": [
                    {"agent": wt.agent_id, "status": wt.status}
                    for wt in coordination.worktrees
                ]
            }
        
        return status
    
    def display_coordination_dashboard(self):
        """Display real-time coordination dashboard"""
        
        self.console.print("\n🎯 [bold cyan]Agent Worktree Coordination Dashboard[/bold cyan]")
        
        status = self.get_coordination_status()
        
        # Summary panel
        summary_panel = Panel(
            f"""
[bold]Active Features:[/bold] {status['active_features']}
[bold]Total Agents:[/bold] {status['total_agents']}
[bold]Active Worktrees:[/bold] {status['total_worktrees']}
            """.strip(),
            title="[bold green]Coordination Status[/bold green]",
            border_style="green"
        )
        
        self.console.print(summary_panel)
        
        # Features table
        if status["features"]:
            features_table = Table(title="Active Features", box=box.ROUNDED)
            features_table.add_column("Feature ID", style="cyan")
            features_table.add_column("Status", style="green")
            features_table.add_column("Agents", style="yellow")
            features_table.add_column("Worktree Status", style="magenta")
            
            for feature_id, feature_data in status["features"].items():
                agents_str = ", ".join(feature_data["agents"])
                worktree_status = " | ".join([
                    f"{wt['agent']}:{wt['status']}" 
                    for wt in feature_data["worktrees_status"]
                ])
                
                features_table.add_row(
                    feature_id,
                    feature_data["status"],
                    agents_str,
                    worktree_status
                )
            
            self.console.print(features_table)
        else:
            self.console.print("ℹ️ No active features")