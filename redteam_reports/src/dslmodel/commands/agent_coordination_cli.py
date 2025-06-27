#!/usr/bin/env python3
"""
Agent Coordination CLI - Agents use worktrees with OTEL Weaver communication

CLI interface for managing distributed agent coordination with exclusive worktrees
and OpenTelemetry-based communication.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from ..utils.json_output import json_command
from ..agents.worktree_agent_coordinator import (
    WorktreeAgentCoordinator,
    AgentCapability,
    FeatureSpec,
    AgentState,
    WorktreeStatus,
    create_demo_agents,
    create_demo_features
)

app = typer.Typer(help="Agent coordination with worktrees and OTEL communication")
console = Console()


@app.command("init")
def init_coordination_system(
    repo_path: Path = typer.Option(Path.cwd(), "--repo", "-r", help="Base repository path"),
    coordination_dir: Optional[Path] = typer.Option(None, "--coord-dir", "-c", help="Coordination directory")
):
    """Initialize agent coordination system"""
    with json_command("agent-coordination-init") as formatter:
        try:
            coordinator = WorktreeAgentCoordinator(repo_path, coordination_dir)
            
            formatter.add_data("repo_path", str(repo_path))
            formatter.add_data("coordination_dir", str(coordinator.coordination_dir))
            formatter.add_data("init_successful", True)
            
            formatter.print("🤖 Agent Coordination System Initialized")
            formatter.print(f"📁 Repository: {repo_path}")
            formatter.print(f"🗂️ Coordination: {coordinator.coordination_dir}")
            formatter.print("✅ Ready for agent registration and feature assignment")
            
        except Exception as e:
            formatter.add_error(f"Initialization failed: {e}")
            formatter.print(f"❌ Initialization failed: {e}")
            raise typer.Exit(1)


@app.command("register-agent")
def register_agent(
    agent_id: str = typer.Argument(..., help="Unique agent identifier"),
    languages: str = typer.Option("python", "--langs", help="Comma-separated languages"),
    frameworks: str = typer.Option("", "--frameworks", help="Comma-separated frameworks"),
    expertise: str = typer.Option("general", "--expertise", help="Comma-separated expertise areas"),
    max_concurrent: int = typer.Option(1, "--max-concurrent", help="Max concurrent features"),
    complexity: str = typer.Option("medium", "--complexity", help="Preferred complexity")
):
    """Register a new agent with capabilities"""
    with json_command("register-agent") as formatter:
        try:
            # Parse capabilities
            languages_list = [lang.strip() for lang in languages.split(",")]
            frameworks_list = [fw.strip() for fw in frameworks.split(",") if fw.strip()]
            expertise_list = [exp.strip() for exp in expertise.split(",")]
            
            capability = AgentCapability(
                agent_id=agent_id,
                languages=languages_list,
                frameworks=frameworks_list,
                expertise_areas=expertise_list,
                max_concurrent_features=max_concurrent,
                preferred_complexity=complexity
            )
            
            # Initialize coordinator and register agent
            coordinator = WorktreeAgentCoordinator(Path.cwd())
            registered_id = coordinator.register_agent(capability)
            
            formatter.add_data("agent_id", registered_id)
            formatter.add_data("languages", languages_list)
            formatter.add_data("frameworks", frameworks_list)
            formatter.add_data("expertise_areas", expertise_list)
            formatter.add_data("registration_successful", True)
            
            formatter.print(f"🤖 Agent {registered_id} registered successfully")
            formatter.print(f"💻 Languages: {', '.join(languages_list)}")
            formatter.print(f"🔧 Frameworks: {', '.join(frameworks_list)}")
            formatter.print(f"🎯 Expertise: {', '.join(expertise_list)}")
            formatter.print(f"⚡ Max Concurrent: {max_concurrent}")
            
        except Exception as e:
            formatter.add_error(f"Agent registration failed: {e}")
            formatter.print(f"❌ Agent registration failed: {e}")
            raise typer.Exit(1)


@app.command("add-feature")
def add_feature_request(
    name: str = typer.Argument(..., help="Feature name"),
    description: str = typer.Option("", "--desc", help="Feature description"),
    priority: str = typer.Option("medium", "--priority", help="Priority level"),
    effort: int = typer.Option(5, "--effort", help="Estimated effort (story points)"),
    requirements_file: Optional[Path] = typer.Option(None, "--req-file", help="Requirements JSON file")
):
    """Add a feature request to the development queue"""
    with json_command("add-feature") as formatter:
        try:
            # Load requirements from file if provided
            requirements = []
            acceptance_criteria = []
            
            if requirements_file and requirements_file.exists():
                with open(requirements_file) as f:
                    req_data = json.load(f)
                    requirements = req_data.get("requirements", [])
                    acceptance_criteria = req_data.get("acceptance_criteria", [])
            
            feature = FeatureSpec(
                name=name,
                description=description or f"Implementation of {name}",
                requirements=requirements,
                acceptance_criteria=acceptance_criteria,
                estimated_effort=effort,
                priority=priority
            )
            
            # Add to coordinator
            coordinator = WorktreeAgentCoordinator(Path.cwd())
            feature_id = coordinator.add_feature_request(feature)
            
            formatter.add_data("feature_id", feature_id)
            formatter.add_data("feature_name", name)
            formatter.add_data("priority", priority)
            formatter.add_data("estimated_effort", effort)
            formatter.add_data("request_successful", True)
            
            formatter.print(f"📋 Feature request added: {name}")
            formatter.print(f"🎯 Priority: {priority}")
            formatter.print(f"📊 Effort: {effort} story points")
            formatter.print(f"🆔 Feature ID: {feature_id}")
            
        except Exception as e:
            formatter.add_error(f"Feature request failed: {e}")
            formatter.print(f"❌ Feature request failed: {e}")
            raise typer.Exit(1)


@app.command("assign-work")
def assign_work_to_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to assign work to"),
    auto_start: bool = typer.Option(True, "--auto-start", help="Automatically start work")
):
    """Assign best matching feature to an agent"""
    with json_command("assign-work") as formatter:
        try:
            coordinator = WorktreeAgentCoordinator(Path.cwd())
            
            # Load existing state if available
            if coordinator.state_file.exists():
                with open(coordinator.state_file) as f:
                    state_data = json.load(f)
                    # Would restore state here in production
            
            feature = coordinator.assign_feature_to_agent(agent_id)
            
            if feature:
                formatter.add_data("agent_id", agent_id)
                formatter.add_data("feature_name", feature.name)
                formatter.add_data("worktree_path", str(feature.worktree_path))
                formatter.add_data("branch_name", feature.branch_name)
                formatter.add_data("assignment_successful", True)
                
                formatter.print(f"🎯 Feature assigned to agent {agent_id}")
                formatter.print(f"📋 Feature: {feature.name}")
                formatter.print(f"🌿 Branch: {feature.branch_name}")
                formatter.print(f"📁 Worktree: {feature.worktree_path}")
                
                if auto_start:
                    started = coordinator.agent_start_work(agent_id)
                    if started:
                        formatter.print("🚀 Agent started work automatically")
                    else:
                        formatter.print("⚠️ Could not auto-start work")
                        
            else:
                formatter.add_data("assignment_successful", False)
                formatter.print(f"❌ No suitable features available for agent {agent_id}")
                
        except Exception as e:
            formatter.add_error(f"Work assignment failed: {e}")
            formatter.print(f"❌ Work assignment failed: {e}")
            raise typer.Exit(1)


@app.command("agent-status")
def show_agent_status(
    agent_id: Optional[str] = typer.Option(None, "--agent", help="Specific agent ID"),
    show_details: bool = typer.Option(False, "--details", help="Show detailed information")
):
    """Show status of agents in the coordination system"""
    with json_command("agent-status") as formatter:
        try:
            coordinator = WorktreeAgentCoordinator(Path.cwd())
            
            if agent_id:
                # Show specific agent
                if agent_id in coordinator.agents:
                    agent = coordinator.agents[agent_id]
                    
                    formatter.add_data("agent_id", agent_id)
                    formatter.add_data("state", agent.state.value)
                    formatter.add_data("current_feature", agent.current_feature.name if agent.current_feature else None)
                    formatter.add_data("worktree_path", str(agent.worktree_path) if agent.worktree_path else None)
                    
                    formatter.print(f"🤖 Agent: {agent_id}")
                    formatter.print(f"📊 State: {agent.state.value}")
                    if agent.current_feature:
                        formatter.print(f"📋 Feature: {agent.current_feature.name}")
                        formatter.print(f"🌿 Branch: {agent.branch_name}")
                        formatter.print(f"📁 Worktree: {agent.worktree_path}")
                    
                    if show_details:
                        formatter.print(f"💻 Languages: {', '.join(agent.capabilities.languages)}")
                        formatter.print(f"🔧 Frameworks: {', '.join(agent.capabilities.frameworks)}")
                        formatter.print(f"🎯 Expertise: {', '.join(agent.capabilities.expertise_areas)}")
                        
                else:
                    formatter.add_error(f"Agent {agent_id} not found")
                    formatter.print(f"❌ Agent {agent_id} not found")
                    
            else:
                # Show all agents
                status = coordinator.get_coordination_status()
                
                formatter.add_data("coordination_status", status)
                
                # Create table for agents
                table = Table(title="Agent Coordination Status")
                table.add_column("Agent ID", style="cyan")
                table.add_column("State", style="yellow")
                table.add_column("Feature", style="green")
                table.add_column("Worktree", style="blue")
                
                for agent_id, agent in coordinator.agents.items():
                    feature_name = agent.current_feature.name if agent.current_feature else "-"
                    worktree_name = agent.worktree_path.name if agent.worktree_path else "-"
                    
                    table.add_row(
                        agent_id,
                        agent.state.value,
                        feature_name,
                        worktree_name
                    )
                
                console.print(table)
                
                # Summary panel
                summary = Panel(
                    f"Total Agents: {status['total_agents']}\n"
                    f"Active: {status['active_agents']} | Idle: {status['idle_agents']}\n"
                    f"Features in Queue: {status['features_in_queue']}\n"
                    f"Features in Progress: {status['features_in_progress']}\n" 
                    f"Features Completed: {status['features_completed']}\n"
                    f"Coordination Health: {status['coordination_health']:.2f}",
                    title="System Summary",
                    expand=False
                )
                console.print(summary)
                
        except Exception as e:
            formatter.add_error(f"Status check failed: {e}")
            formatter.print(f"❌ Status check failed: {e}")
            raise typer.Exit(1)


@app.command("coordination-cycle")
def run_coordination_cycle(
    continuous: bool = typer.Option(False, "--continuous", help="Run continuous coordination"),
    interval: int = typer.Option(30, "--interval", help="Interval between cycles (seconds)"),
    max_cycles: int = typer.Option(0, "--max-cycles", help="Maximum cycles (0 = unlimited)")
):
    """Run coordination cycle(s) to assign work and monitor progress"""
    
    async def run_cycles():
        coordinator = WorktreeAgentCoordinator(Path.cwd())
        cycle_count = 0
        
        with json_command("coordination-cycle") as formatter:
            try:
                if continuous:
                    formatter.print("🔄 Starting continuous coordination...")
                    
                    while max_cycles == 0 or cycle_count < max_cycles:
                        cycle_count += 1
                        
                        with console.status(f"[bold green]Running cycle {cycle_count}..."):
                            result = coordinator.run_coordination_cycle()
                        
                        console.print(f"📊 Cycle {cycle_count}: {result['assignments_made']} assignments, "
                                    f"{result['timeouts_handled']} timeouts, "
                                    f"{result['cycle_duration_ms']}ms")
                        
                        if max_cycles > 0 and cycle_count >= max_cycles:
                            break
                            
                        await asyncio.sleep(interval)
                        
                else:
                    # Single cycle
                    result = coordinator.run_coordination_cycle()
                    
                    formatter.add_data("cycle_result", result)
                    formatter.print("🔄 Coordination cycle completed")
                    formatter.print(f"📊 Assignments: {result['assignments_made']}")
                    formatter.print(f"⏱️ Duration: {result['cycle_duration_ms']}ms")
                    formatter.print(f"🔧 Timeouts handled: {result['timeouts_handled']}")
                    
            except KeyboardInterrupt:
                formatter.print("\n⏹️ Coordination stopped by user")
            except Exception as e:
                formatter.add_error(f"Coordination cycle failed: {e}")
                formatter.print(f"❌ Coordination cycle failed: {e}")
                raise typer.Exit(1)
    
    # Run async function
    asyncio.run(run_cycles())


@app.command("demo")
def run_coordination_demo(
    agent_count: int = typer.Option(3, "--agents", help="Number of demo agents"),
    feature_count: int = typer.Option(3, "--features", help="Number of demo features"),
    cycles: int = typer.Option(5, "--cycles", help="Number of coordination cycles")
):
    """Run complete agent coordination demonstration"""
    
    async def demo():
        with json_command("coordination-demo") as formatter:
            try:
                console.print(Panel("🚀 Agent Coordination with Worktrees Demo", expand=False))
                
                # Initialize coordinator
                with console.status("[bold blue]Initializing coordination system..."):
                    coordinator = WorktreeAgentCoordinator(Path.cwd())
                
                console.print("✅ Coordination system initialized")
                
                # Register demo agents
                with console.status("[bold blue]Registering demo agents..."):
                    demo_agents = create_demo_agents()[:agent_count]
                    for agent_capability in demo_agents:
                        coordinator.register_agent(agent_capability)
                
                console.print(f"✅ {len(demo_agents)} agents registered")
                
                # Add demo features
                with console.status("[bold blue]Adding demo features..."):
                    demo_features = create_demo_features()[:feature_count]
                    for feature in demo_features:
                        coordinator.add_feature_request(feature)
                
                console.print(f"✅ {len(demo_features)} features added to queue")
                
                # Run coordination cycles
                console.print(f"\n🔄 Running {cycles} coordination cycles...")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    
                    task = progress.add_task("Running cycles...", total=cycles)
                    
                    for cycle in range(cycles):
                        result = coordinator.run_coordination_cycle()
                        
                        # Simulate agent work progression
                        for agent_id, agent in coordinator.agents.items():
                            if agent.state == AgentState.CLAIMING:
                                coordinator.agent_start_work(agent_id)
                            elif agent.state == AgentState.WORKING and cycle >= 2:
                                coordinator.agent_submit_work(agent_id, {"validation_passed": True})
                            elif agent.state == AgentState.SUBMITTING:
                                coordinator.complete_feature(agent_id)
                        
                        progress.update(task, advance=1)
                        await asyncio.sleep(0.5)
                
                # Final status
                final_status = coordinator.get_coordination_status()
                
                formatter.add_data("demo_results", final_status)
                formatter.add_data("demo_successful", True)
                
                console.print("\n🎯 Demo Results:")
                console.print(f"📊 Features Completed: {final_status['features_completed']}")
                console.print(f"🔄 Features in Progress: {final_status['features_in_progress']}")
                console.print(f"📋 Features in Queue: {final_status['features_in_queue']}")
                console.print(f"🤖 Active Agents: {final_status['active_agents']}")
                console.print(f"💚 Coordination Health: {final_status['coordination_health']:.2f}")
                
                console.print("\n✅ Agent coordination demo completed!")
                console.print("🎯 This demonstrates:")
                console.print("   • Agents working in exclusive worktrees")
                console.print("   • OTEL telemetry-based communication")
                console.print("   • Automatic feature assignment and coordination")
                console.print("   • Production-ready distributed development patterns")
                
            except Exception as e:
                formatter.add_error(f"Demo failed: {e}")
                console.print(f"❌ Demo failed: {e}")
                raise typer.Exit(1)
    
    # Run async demo
    asyncio.run(demo())


@app.command("worktree-status")
def show_worktree_status():
    """Show status of all managed worktrees"""
    with json_command("worktree-status") as formatter:
        try:
            coordinator = WorktreeAgentCoordinator(Path.cwd())
            
            if not coordinator.worktrees:
                formatter.print("📂 No managed worktrees found")
                return
            
            # Create table for worktrees
            table = Table(title="Managed Worktrees")
            table.add_column("Path", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Agent", style="green")
            table.add_column("Feature", style="blue")
            
            worktree_data = []
            for worktree_path, status in coordinator.worktrees.items():
                # Find associated agent and feature
                agent_id = "-"
                feature_name = "-"
                
                for aid, agent in coordinator.agents.items():
                    if agent.worktree_path and str(agent.worktree_path) == worktree_path:
                        agent_id = aid
                        feature_name = agent.current_feature.name if agent.current_feature else "-"
                        break
                
                table.add_row(
                    Path(worktree_path).name,
                    status.value,
                    agent_id,
                    feature_name
                )
                
                worktree_data.append({
                    "path": worktree_path,
                    "status": status.value,
                    "agent_id": agent_id,
                    "feature_name": feature_name
                })
            
            formatter.add_data("worktrees", worktree_data)
            console.print(table)
            
        except Exception as e:
            formatter.add_error(f"Worktree status check failed: {e}")
            formatter.print(f"❌ Worktree status check failed: {e}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()