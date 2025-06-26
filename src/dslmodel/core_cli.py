#!/usr/bin/env python3
"""
Core CLI - 80/20 approach
The essential 20% of commands that deliver 80% of value
"""

import typer
from pathlib import Path
from typing import Optional, List
from rich import print
from rich.console import Console
from rich.table import Table

# Core imports - just what we need
from dslmodel.utils.dspy_tools import init_lm
from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel

# Agent system
import sys
sys.path.append('/Users/sac/dev/dslmodel/src')
from dslmodel.agents.core_agent_system import CoreAgentSystem

app = typer.Typer(help="DSLModel Core CLI - Essential commands only")
console = Console()

# Global state
_system: Optional[CoreAgentSystem] = None

def get_system() -> CoreAgentSystem:
    """Get or create the core agent system"""
    global _system
    if _system is None:
        _system = CoreAgentSystem("/Users/sac/dev/dslmodel")
    return _system

@app.command("gen")
def generate(
    prompt: str = typer.Argument(..., help="What to generate"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory"),
    model: str = typer.Option("groq/llama-3.2-90b-text-preview", "--model", "-m", help="Model to use")
):
    """Generate DSLModel class from natural language"""
    
    try:
        init_lm(model=model)
        console.print(f"🔄 Generating: {prompt}")
        
        _, output_file = generate_and_save_dslmodel(prompt, Path(output), "py", None)
        
        console.print(f"✅ Generated: {output_file}", style="green")
        
    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("agent")
def agent_command(
    action: str = typer.Argument(..., help="Action: assign|progress|complete|status|list|cleanup"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID"),
    task: str = typer.Option(None, "--task", "-t", help="Task description"),
    progress: float = typer.Option(None, "--progress", "-p", help="Progress percentage (0-100)"),
    activity: str = typer.Option("Working", "--activity", help="Current activity"),
    files: str = typer.Option(None, "--files", help="Comma-separated list of files")
):
    """Manage agents with OTEL telemetry"""
    
    system = get_system()
    
    try:
        if action == "assign":
            if not agent_id or not task:
                console.print("❌ Need --agent and --task for assign", style="red")
                raise typer.Exit(1)
            
            path = system.assign_agent(agent_id, task)
            console.print(f"✅ Agent {agent_id} assigned to: {path}", style="green")
            
        elif action == "progress":
            if not agent_id or progress is None:
                console.print("❌ Need --agent and --progress for progress", style="red")
                raise typer.Exit(1)
            
            success = system.report_progress(agent_id, progress, activity)
            if success:
                console.print(f"✅ Progress {progress:.0f}% reported for {agent_id}", style="green")
            else:
                console.print(f"❌ Failed to report progress for {agent_id}", style="red")
                
        elif action == "complete":
            if not agent_id:
                console.print("❌ Need --agent for complete", style="red")
                raise typer.Exit(1)
            
            file_list = files.split(",") if files else []
            success = system.complete_work(agent_id, file_list)
            
            if success:
                console.print(f"✅ Work completed for {agent_id}", style="green")
            else:
                console.print(f"❌ Failed to complete work for {agent_id}", style="red")
                
        elif action == "status":
            if agent_id:
                status = system.get_agent_status(agent_id)
                if status:
                    console.print(f"Agent {agent_id}:")
                    console.print(f"  Task: {status['task']}")
                    console.print(f"  Progress: {status['progress']:.0f}%")
                    console.print(f"  Status: {status['status']}")
                else:
                    console.print(f"❌ Agent {agent_id} not found", style="red")
            else:
                console.print("❌ Need --agent for status", style="red")
                
        elif action == "list":
            agents = system.list_agents()
            if not agents:
                console.print("No active agents", style="yellow")
                return
                
            table = Table(title="Active Agents")
            table.add_column("Agent ID")
            table.add_column("Task")
            table.add_column("Progress")
            table.add_column("Status")
            
            for agent in agents:
                table.add_row(
                    agent['agent_id'],
                    agent['task'][:50] + "..." if len(agent['task']) > 50 else agent['task'],
                    f"{agent['progress']:.0f}%",
                    agent['status']
                )
            
            console.print(table)
            
        elif action == "cleanup":
            if not agent_id:
                console.print("❌ Need --agent for cleanup", style="red")
                raise typer.Exit(1)
            
            success = system.cleanup_agent(agent_id)
            if success:
                console.print(f"✅ Cleaned up {agent_id}", style="green")
            else:
                console.print(f"❌ Failed to cleanup {agent_id}", style="red")
                
        else:
            console.print(f"❌ Unknown action: {action}", style="red")
            console.print("Valid actions: assign, progress, complete, status, list, cleanup")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ Agent command failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("coord")
def coordinate(
    requesting: str = typer.Argument(..., help="Requesting agent ID"),
    targets: str = typer.Argument(..., help="Target agent IDs (comma-separated)"),
    message: str = typer.Option("Coordination request", "--message", "-m", help="Coordination message")
):
    """Coordinate between agents"""
    
    system = get_system()
    target_list = [t.strip() for t in targets.split(",")]
    
    try:
        success = system.coordinate_agents(requesting, target_list, message)
        if success:
            console.print(f"✅ Coordination sent from {requesting} to {targets}", style="green")
        else:
            console.print("❌ Coordination failed", style="red")
            
    except Exception as e:
        console.print(f"❌ Coordination failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("workflow")
def workflow(
    name: str = typer.Argument(..., help="Workflow name"),
    agents: str = typer.Option(None, "--agents", "-a", help="Agent IDs (comma-separated)"),
    tasks: str = typer.Option(None, "--tasks", "-t", help="Tasks (comma-separated, one per agent)"),
    simulate: bool = typer.Option(False, "--simulate", "-s", help="Simulate the workflow")
):
    """Run a complete agent workflow"""
    
    if not agents or not tasks:
        console.print("❌ Need --agents and --tasks", style="red")
        raise typer.Exit(1)
    
    agent_list = [a.strip() for a in agents.split(",")]
    task_list = [t.strip() for t in tasks.split(",")]
    
    if len(agent_list) != len(task_list):
        console.print("❌ Number of agents must match number of tasks", style="red")
        raise typer.Exit(1)
    
    system = get_system()
    
    try:
        console.print(f"🚀 Starting workflow: {name}")
        
        # Assign tasks
        for agent_id, task in zip(agent_list, task_list):
            path = system.assign_agent(agent_id, task)
            console.print(f"  ✅ {agent_id}: {task}")
        
        if simulate:
            # Simulate progress
            console.print("🔄 Simulating progress...")
            import time
            
            for progress in [25, 50, 75, 100]:
                for agent_id in agent_list:
                    system.report_progress(agent_id, progress, f"Step at {progress}%")
                    
                console.print(f"  📊 All agents at {progress}%")
                time.sleep(0.5)
            
            # Complete work
            console.print("🔄 Completing work...")
            for agent_id in agent_list:
                system.complete_work(agent_id, [f"{agent_id}_output.py"])
                console.print(f"  ✅ {agent_id} completed")
            
            # Coordinate
            if len(agent_list) > 1:
                console.print("🔄 Coordinating agents...")
                system.coordinate_agents(agent_list[0], agent_list[1:], "Workflow coordination")
                console.print("  ✅ Agents coordinated")
            
            # Cleanup
            console.print("🔄 Cleaning up...")
            for agent_id in agent_list:
                system.cleanup_agent(agent_id)
                console.print(f"  🧹 {agent_id} cleaned up")
        
        console.print(f"🎉 Workflow {name} completed successfully!", style="green")
        
    except Exception as e:
        console.print(f"❌ Workflow failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("validate")
def validate():
    """Validate the core system with OTEL telemetry"""
    
    try:
        console.print("🧪 Running core system validation...")
        
        # Import and run our validation
        from dslmodel.agents.core_validation import main as run_validation
        
        success = run_validation()
        
        if success:
            console.print("🎉 Core system validation passed!", style="green")
        else:
            console.print("❌ Core system validation failed", style="red")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"❌ Validation failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("demo")
def demo():
    """Run a quick demo of core capabilities"""
    
    console.print("🎬 Running Core System Demo")
    console.print("=" * 40)
    
    try:
        # Quick workflow demo
        system = get_system()
        
        console.print("\n1️⃣ Assigning agents...")
        system.assign_agent("demo_backend", "Implement API endpoints")
        system.assign_agent("demo_frontend", "Create UI components")
        
        console.print("\n2️⃣ Reporting progress...")
        import time
        for progress in [30, 60, 90]:
            system.report_progress("demo_backend", progress, f"API work at {progress}%")
            system.report_progress("demo_frontend", progress, f"UI work at {progress}%")
            console.print(f"  📊 Progress: {progress}%")
            time.sleep(0.3)
        
        console.print("\n3️⃣ Coordinating agents...")
        system.coordinate_agents("demo_backend", ["demo_frontend"], "API ready for UI integration")
        
        console.print("\n4️⃣ Completing work...")
        system.complete_work("demo_backend", ["api.py", "models.py"])
        system.complete_work("demo_frontend", ["components.tsx"])
        
        console.print("\n5️⃣ Agent status:")
        table = Table()
        table.add_column("Agent")
        table.add_column("Progress")
        table.add_column("Status")
        
        for agent_id in ["demo_backend", "demo_frontend"]:
            status = system.get_agent_status(agent_id)
            if status:
                table.add_row(
                    agent_id,
                    f"{status['progress']:.0f}%",
                    status['status']
                )
        
        console.print(table)
        
        console.print("\n6️⃣ Cleaning up...")
        system.cleanup_agent("demo_backend")
        system.cleanup_agent("demo_frontend")
        
        console.print("\n🎉 Demo completed successfully!", style="green")
        console.print("\nTry these commands:")
        console.print("  dslmodel-core gen 'user authentication system'")
        console.print("  dslmodel-core agent assign --agent backend --task 'implement auth'")
        console.print("  dslmodel-core agent progress --agent backend --progress 50")
        console.print("  dslmodel-core validate")
        
    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="red")
        raise typer.Exit(1)

@app.command("version")
def version():
    """Show version information"""
    console.print("DSLModel Core CLI v1.0.0")
    console.print("Essential commands for 80/20 productivity")

if __name__ == "__main__":
    app()