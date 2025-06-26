"""Swarm coordination commands for DSLModel CLI."""

import json
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

# Initialize console and CLI app
console = Console()
app = typer.Typer(help="SwarmSH-inspired agent coordination")

# Data directory configuration
DATA_DIR = Path("./swarm_data")


class SwarmCoordinator:
    """Core swarm coordination functionality"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Core JSON files
        self.agents_file = self.data_dir / "agents.json"
        self.work_file = self.data_dir / "work_queue.json"
        self.teams_file = self.data_dir / "teams.json"
        self.telemetry_file = self.data_dir / "telemetry.json"
        
        # Initialize files if not exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files with empty structures"""
        for file, default in [
            (self.agents_file, {}),
            (self.work_file, []),
            (self.teams_file, {}),
            (self.telemetry_file, [])
        ]:
            if not file.exists():
                self._write_json(file, default)
    
    def _read_json(self, file: Path) -> Any:
        """Atomic read with error handling"""
        try:
            return json.loads(file.read_text())
        except:
            return {} if file == self.agents_file or file == self.teams_file else []
    
    def _write_json(self, file: Path, data: Any):
        """Atomic write with backup"""
        backup = file.with_suffix('.bak')
        if file.exists():
            file.rename(backup)
        file.write_text(json.dumps(data, indent=2))
        if backup.exists():
            backup.unlink()  # Remove backup after successful write
    
    def create_agent(self, name: str, team: Optional[str] = None) -> str:
        """Create a new agent with nanosecond-precision ID"""
        agent_id = f"agent_{int(time.time_ns())}"
        agents = self._read_json(self.agents_file)
        
        agents[agent_id] = {
            "name": name,
            "team": team or "default",
            "status": "idle",
            "created": datetime.now().isoformat(),
            "work_completed": 0
        }
        
        self._write_json(self.agents_file, agents)
        self._log_telemetry("agent_created", {"agent_id": agent_id, "name": name})
        return agent_id
    
    def assign_work(self, description: str, priority: str = "medium", team: Optional[str] = None) -> str:
        """Add work to the queue"""
        work_id = f"work_{uuid.uuid4().hex[:8]}"
        work_queue = self._read_json(self.work_file)
        
        work_item = {
            "id": work_id,
            "description": description,
            "priority": priority,
            "team": team,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "assigned_to": None
        }
        
        work_queue.append(work_item)
        self._write_json(self.work_file, work_queue)
        self._log_telemetry("work_created", {"work_id": work_id})
        return work_id
    
    def process_work(self) -> Dict[str, int]:
        """Simple work processing - assign pending work to idle agents"""
        agents = self._read_json(self.agents_file)
        work_queue = self._read_json(self.work_file)
        
        idle_agents = [aid for aid, agent in agents.items() if agent["status"] == "idle"]
        pending_work = [w for w in work_queue if w["status"] == "pending"]
        
        assigned = 0
        for work in pending_work[:len(idle_agents)]:
            agent_id = idle_agents[assigned]
            work["status"] = "in_progress"
            work["assigned_to"] = agent_id
            agents[agent_id]["status"] = "working"
            assigned += 1
        
        self._write_json(self.agents_file, agents)
        self._write_json(self.work_file, work_queue)
        
        return {"assigned": assigned, "pending": len(pending_work) - assigned}
    
    def get_status(self) -> Dict[str, Any]:
        """Get swarm status overview"""
        agents = self._read_json(self.agents_file)
        work_queue = self._read_json(self.work_file)
        
        return {
            "agents": {
                "total": len(agents),
                "idle": sum(1 for a in agents.values() if a["status"] == "idle"),
                "working": sum(1 for a in agents.values() if a["status"] == "working")
            },
            "work": {
                "total": len(work_queue),
                "pending": sum(1 for w in work_queue if w["status"] == "pending"),
                "in_progress": sum(1 for w in work_queue if w["status"] == "in_progress"),
                "completed": sum(1 for w in work_queue if w["status"] == "completed")
            }
        }
    
    def complete_work(self, work_id: str) -> bool:
        """Mark work as completed"""
        work_queue = self._read_json(self.work_file)
        agents = self._read_json(self.agents_file)
        
        for work in work_queue:
            if work["id"] == work_id:
                work["status"] = "completed"
                work["completed"] = datetime.now().isoformat()
                
                # Free up agent
                if work.get("assigned_to"):
                    if work["assigned_to"] in agents:
                        agents[work["assigned_to"]]["status"] = "idle"
                        agents[work["assigned_to"]]["work_completed"] += 1
                
                self._write_json(self.work_file, work_queue)
                self._write_json(self.agents_file, agents)
                self._log_telemetry("work_completed", {"work_id": work_id})
                return True
        return False
    
    def _log_telemetry(self, event: str, data: Dict[str, Any]):
        """Log telemetry events"""
        telemetry = self._read_json(self.telemetry_file)
        telemetry.append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        })
        # Keep last 1000 events
        if len(telemetry) > 1000:
            telemetry = telemetry[-1000:]
        self._write_json(self.telemetry_file, telemetry)


class FullCycleDemo:
    """Orchestrates a complete swarm lifecycle demo"""
    
    def __init__(self):
        self.coordinator = SwarmCoordinator(data_dir=Path("./full_cycle_data"))
        self.generation_count = 0
        self.cycle_metrics = {
            "agents_generated": 0,
            "work_items_created": 0,
            "work_completed": 0,
            "cycles_executed": 0,
            "efficiency_score": 0.0,
            "evolution_events": 0
        }
        self.start_time = datetime.now()
    
    def generate_domain_models(self) -> List[str]:
        """Phase 1: Generate domain models using DSL"""
        rprint("\n[bold blue]📋 Phase 1: Domain Model Generation[/bold blue]")
        
        domains = [
            "E-commerce order processing system",
            "Healthcare patient management platform", 
            "Financial trading and risk management",
            "Supply chain optimization network",
            "Customer support automation system"
        ]
        
        selected_domain = random.choice(domains)
        rprint(f"[cyan]Selected Domain:[/cyan] {selected_domain}")
        
        # Simulate model generation
        models = []
        model_types = ["User", "Order", "Product", "Payment", "Analytics"]
        
        for model_type in model_types:
            with console.status(f"[bold green]Generating {model_type} model..."):
                time.sleep(0.5)  # Simulate generation time
                model_name = f"{model_type}Model"
                models.append(model_name)
                rprint(f"  ✓ Generated {model_name}")
        
        return models
    
    def generate_agents(self, models: List[str]) -> List[str]:
        """Phase 1: Generate specialized agents based on models"""
        rprint("\n[bold blue]🤖 Phase 1: Agent Generation[/bold blue]")
        
        agent_roles = [
            ("ProcessorAgent", "Handles core business logic"),
            ("ValidatorAgent", "Validates data integrity"),
            ("MonitorAgent", "Monitors system performance"),
            ("OptimizerAgent", "Optimizes workflows"),
            ("ReporterAgent", "Generates analytics reports")
        ]
        
        generated_agents = []
        
        for role, description in agent_roles:
            agent_id = self.coordinator.create_agent(role, team=f"auto_gen_{role[:3].lower()}")
            generated_agents.append(agent_id)
            self.cycle_metrics["agents_generated"] += 1
            rprint(f"  ✓ Generated {role}: {description}")
            time.sleep(0.3)
        
        return generated_agents
    
    def generate_work_items(self, models: List[str]) -> List[str]:
        """Phase 1: Generate work items based on domain models"""
        rprint("\n[bold blue]📋 Phase 1: Work Generation[/bold blue]")
        
        work_templates = [
            ("Process {model} validation", "high"),
            ("Optimize {model} performance", "medium"),
            ("Generate {model} analytics", "medium"),
            ("Implement {model} monitoring", "low"),
            ("Create {model} documentation", "low")
        ]
        
        generated_work = []
        
        for model in models[:3]:  # Use first 3 models
            for template, priority in work_templates:
                description = template.format(model=model)
                work_id = self.coordinator.assign_work(description, priority)
                generated_work.append(work_id)
                self.cycle_metrics["work_items_created"] += 1
                rprint(f"  ✓ Created: {description} [{priority}]")
                time.sleep(0.2)
        
        return generated_work
    
    def initialize_monitoring(self):
        """Phase 2: Set up telemetry and monitoring"""
        rprint("\n[bold blue]📊 Phase 2: Monitoring Initialization[/bold blue]")
        
        # Simulate telemetry setup
        monitoring_components = [
            "Performance metrics collector",
            "Error tracking system", 
            "Resource utilization monitor",
            "Work queue analytics",
            "Agent health checker"
        ]
        
        for component in monitoring_components:
            with console.status(f"[bold green]Initializing {component}..."):
                time.sleep(0.3)
                rprint(f"  ✓ {component} online")
        
        # Log telemetry initialization
        self.coordinator._log_telemetry("monitoring_initialized", {
            "components": len(monitoring_components),
            "timestamp": datetime.now().isoformat()
        })
    
    def execute_work_cycles(self, cycles: int = 3):
        """Phase 3: Execute multiple work processing cycles"""
        rprint(f"\n[bold blue]⚡ Phase 3: Work Execution ({cycles} cycles)[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True
        ) as progress:
            
            cycle_task = progress.add_task("Processing cycles...", total=cycles)
            
            for cycle in range(cycles):
                progress.update(cycle_task, description=f"Executing cycle {cycle + 1}")
                
                # Process work
                result = self.coordinator.process_work()
                rprint(f"  Cycle {cycle + 1}: Assigned {result['assigned']} items, {result['pending']} pending")
                
                # Simulate work completion
                work_queue = self.coordinator._read_json(self.coordinator.work_file)
                completed_this_cycle = 0
                
                for work in work_queue:
                    if work["status"] == "in_progress" and random.random() > 0.3:
                        success = self.coordinator.complete_work(work["id"])
                        if success:
                            completed_this_cycle += 1
                            self.cycle_metrics["work_completed"] += 1
                
                rprint(f"  → Completed {completed_this_cycle} items this cycle")
                
                # Log cycle telemetry
                self.coordinator._log_telemetry("cycle_completed", {
                    "cycle": cycle + 1,
                    "assigned": result["assigned"],
                    "completed": completed_this_cycle,
                    "efficiency": completed_this_cycle / max(result["assigned"], 1)
                })
                
                self.cycle_metrics["cycles_executed"] += 1
                progress.advance(cycle_task)
                time.sleep(1)
    
    def analyze_and_evolve(self):
        """Phase 4: System analysis and evolution"""
        rprint("\n[bold blue]🧬 Phase 4: System Evolution[/bold blue]")
        
        # Calculate metrics
        total_time = (datetime.now() - self.start_time).total_seconds()
        efficiency = self.cycle_metrics["work_completed"] / max(self.cycle_metrics["work_items_created"], 1)
        throughput = self.cycle_metrics["work_completed"] / max(total_time / 60, 1)  # per minute
        
        # Update efficiency score
        self.cycle_metrics["efficiency_score"] = efficiency * 100
        
        # Display analysis
        analysis_table = Table(title="System Performance Analysis")
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Value", style="green")
        analysis_table.add_column("Assessment", style="yellow")
        
        analysis_table.add_row("Efficiency Rate", f"{efficiency:.1%}", "✓ Good" if efficiency > 0.6 else "⚠ Needs Improvement")
        analysis_table.add_row("Throughput", f"{throughput:.1f} items/min", "✓ Optimal" if throughput > 2 else "⚠ Could Optimize")
        analysis_table.add_row("Agent Utilization", f"{len(self.coordinator._read_json(self.coordinator.agents_file))}", "✓ Adequate")
        analysis_table.add_row("Cycle Time", f"{total_time:.1f}s", "✓ Fast")
        
        console.print(analysis_table)
        
        # Generate evolution suggestions
        evolution_suggestions = []
        if efficiency < 0.7:
            evolution_suggestions.append("Increase agent specialization")
        if throughput < 3:
            evolution_suggestions.append("Implement parallel processing")
        if self.cycle_metrics["cycles_executed"] < 3:
            evolution_suggestions.append("Add more work cycles")
        
        if evolution_suggestions:
            rprint("\n[bold yellow]🎯 Evolution Suggestions:[/bold yellow]")
            for suggestion in evolution_suggestions:
                rprint(f"  • {suggestion}")
                self.cycle_metrics["evolution_events"] += 1
        else:
            rprint("\n[bold green]🎯 System is performing optimally![/bold green]")
    
    def generate_final_report(self):
        """Phase 5: Generate comprehensive report"""
        rprint("\n[bold blue]📊 Phase 5: Final Report Generation[/bold blue]")
        
        # Create comprehensive report
        report = {
            "demo_id": f"full_cycle_{int(time.time())}",
            "execution_time": (datetime.now() - self.start_time).total_seconds(),
            "metrics": self.cycle_metrics,
            "system_state": self.coordinator.get_status(),
            "telemetry_events": len(self.coordinator._read_json(self.coordinator.telemetry_file)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report
        report_path = self.coordinator.data_dir / f"report_{report['demo_id']}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        summary_panel = Panel(
            f"""[bold green]Full Cycle Demo Complete![/bold green]
            
[cyan]Generated:[/cyan]
• {self.cycle_metrics['agents_generated']} specialized agents
• {self.cycle_metrics['work_items_created']} work items
• {self.cycle_metrics['cycles_executed']} execution cycles

[cyan]Performance:[/cyan]
• {self.cycle_metrics['work_completed']} tasks completed
• {self.cycle_metrics['efficiency_score']:.1f}% efficiency score
• {self.cycle_metrics['evolution_events']} evolution events

[cyan]Report saved to:[/cyan] {report_path}""",
            title="🎉 Demo Summary",
            border_style="green"
        )
        
        console.print(summary_panel)
    
    def cleanup(self):
        """Clean up demo data"""
        rprint("\n[bold blue]🧹 Cleanup[/bold blue]")
        
        if self.coordinator.data_dir.exists():
            # Keep reports but clean working data
            for file in ["agents.json", "work_queue.json", "telemetry.json"]:
                file_path = self.coordinator.data_dir / file
                if file_path.exists():
                    file_path.unlink()
            rprint("  ✓ Cleaned working data (reports preserved)")


# CLI Commands
@app.command("create-agent")
def create_agent(
    name: str = typer.Argument(..., help="Agent name"),
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Team assignment")
):
    """Create a new agent"""
    coordinator = SwarmCoordinator()
    agent_id = coordinator.create_agent(name, team)
    rprint(f"[green]✓[/green] Created agent: {agent_id} ({name})")


@app.command("assign")
def assign_work(
    description: str = typer.Argument(..., help="Work description"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority level"),
    team: Optional[str] = typer.Option(None, "--team", "-t", help="Assign to specific team")
):
    """Assign new work to the swarm"""
    coordinator = SwarmCoordinator()
    work_id = coordinator.assign_work(description, priority, team)
    rprint(f"[green]✓[/green] Created work: {work_id}")


@app.command("process")
def process_work():
    """Process work queue - assign work to agents"""
    coordinator = SwarmCoordinator()
    result = coordinator.process_work()
    rprint(f"[blue]→[/blue] Assigned {result['assigned']} work items")
    rprint(f"[yellow]⏳[/yellow] {result['pending']} items remaining in queue")


@app.command("complete")
def complete_work(
    work_id: str = typer.Argument(..., help="Work ID to complete")
):
    """Mark work as completed"""
    coordinator = SwarmCoordinator()
    if coordinator.complete_work(work_id):
        rprint(f"[green]✓[/green] Completed work: {work_id}")
    else:
        rprint(f"[red]✗[/red] Work not found: {work_id}")


@app.command("status")
def show_status():
    """Show swarm status"""
    coordinator = SwarmCoordinator()
    status = coordinator.get_status()
    
    # Create status table
    table = Table(title="Swarm Status")
    table.add_column("Category", style="cyan")
    table.add_column("Metric", style="magenta")
    table.add_column("Value", style="green")
    
    # Add agent stats
    table.add_row("Agents", "Total", str(status["agents"]["total"]))
    table.add_row("", "Idle", str(status["agents"]["idle"]))
    table.add_row("", "Working", str(status["agents"]["working"]))
    
    # Add work stats
    table.add_row("Work", "Total", str(status["work"]["total"]))
    table.add_row("", "Pending", str(status["work"]["pending"]))
    table.add_row("", "In Progress", str(status["work"]["in_progress"]))
    table.add_row("", "Completed", str(status["work"]["completed"]))
    
    console.print(table)


@app.command("dashboard")
def show_dashboard():
    """Show live dashboard (simplified)"""
    coordinator = SwarmCoordinator()
    
    rprint("[bold blue]Swarm Dashboard[/bold blue]")
    rprint("=" * 50)
    
    # Simulate processing loop
    for _ in track(range(5), description="Processing..."):
        status = coordinator.get_status()
        coordinator.process_work()
        time.sleep(1)
    
    # Show final status
    show_status()


@app.command("telemetry")
def show_telemetry(
    last: int = typer.Option(10, "--last", "-n", help="Number of events to show")
):
    """Show telemetry events"""
    coordinator = SwarmCoordinator()
    telemetry_data = coordinator._read_json(coordinator.telemetry_file)
    
    table = Table(title=f"Last {last} Telemetry Events")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Event", style="magenta") 
    table.add_column("Data", style="green")
    
    for event in telemetry_data[-last:]:
        table.add_row(
            event["timestamp"][:19],  # Trim microseconds
            event["event"],
            json.dumps(event["data"])
        )
    
    console.print(table)


@app.command("demo")
def run_demo():
    """Run a demo showing swarm coordination"""
    rprint("[bold cyan]🚀 SwarmSH Demo[/bold cyan]")
    rprint("=" * 50)
    
    coordinator = SwarmCoordinator()
    
    # Create agents
    rprint("\n[yellow]Creating agents...[/yellow]")
    for i in range(3):
        agent_id = coordinator.create_agent(f"agent_{i}", "alpha_team")
        rprint(f"  → Created {agent_id}")
    
    # Create work
    rprint("\n[yellow]Creating work items...[/yellow]")
    work_items = [
        "Analyze system logs",
        "Generate performance report",
        "Optimize database queries",
        "Update documentation",
        "Review code changes"
    ]
    
    for work in work_items:
        work_id = coordinator.assign_work(work, priority="medium")
        rprint(f"  → Created work: {work}")
    
    # Process work
    rprint("\n[yellow]Processing work queue...[/yellow]")
    result = coordinator.process_work()
    rprint(f"  → Assigned {result['assigned']} items")
    
    # Show status
    rprint("\n[yellow]Current status:[/yellow]")
    show_status()
    
    # Complete some work
    rprint("\n[yellow]Completing work...[/yellow]")
    work_queue = coordinator._read_json(coordinator.work_file)
    for work in work_queue[:2]:
        if work["status"] == "in_progress":
            coordinator.complete_work(work["id"])
            rprint(f"  → Completed: {work['description']}")
    
    # Final status
    rprint("\n[yellow]Final status:[/yellow]")
    show_status()


@app.command("clean")
def clean_data():
    """Clean swarm data directory"""
    import shutil
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
        rprint(f"[green]✓[/green] Cleaned data directory: {DATA_DIR}")
    else:
        rprint(f"[yellow]⚠[/yellow] Data directory does not exist: {DATA_DIR}")


@app.command("init")
def initialize_swarm():
    """Initialize swarm with sample agents and work"""
    coordinator = SwarmCoordinator()
    
    rprint("[bold blue]Initializing Swarm[/bold blue]")
    rprint("=" * 30)
    
    # Create agents
    agents = [
        ("Agent_Alpha", "alpha"),
        ("Agent_Beta", "beta"), 
        ("Agent_Gamma", "gamma")
    ]
    
    for name, team in agents:
        agent_id = coordinator.create_agent(name, team)
        rprint(f"[green]✓[/green] Created {name} ({team} team)")
    
    # Create work items
    work_items = [
        ("Analyze telemetry data", "high"),
        ("Generate performance report", "medium"),
        ("Update documentation", "low")
    ]
    
    for desc, priority in work_items:
        work_id = coordinator.assign_work(desc, priority)
        rprint(f"[blue]→[/blue] Created work: {desc} [{priority}]")
    
    rprint("\n[yellow]Initialization complete![/yellow]")
    show_status()


@app.command("full-cycle")
def run_full_cycle(
    cycles: int = typer.Option(3, "--cycles", "-c", help="Number of execution cycles"),
    cleanup: bool = typer.Option(True, "--cleanup/--no-cleanup", help="Clean up after demo"),
    domain: str = typer.Option("auto", "--domain", "-d", help="Domain to generate models for")
):
    """Run the complete full cycle generation demo"""
    
    rprint("[bold cyan]🚀 Full Cycle Generation Demo[/bold cyan]")
    rprint("=" * 60)
    rprint("Demonstrating end-to-end automated generation, execution, and evolution")
    rprint()
    
    demo = FullCycleDemo()
    
    try:
        # Execute all phases
        models = demo.generate_domain_models()
        agents = demo.generate_agents(models)
        work_items = demo.generate_work_items(models)
        
        demo.initialize_monitoring()
        demo.execute_work_cycles(cycles)
        demo.analyze_and_evolve()
        demo.generate_final_report()
        
        if cleanup:
            demo.cleanup()
            
    except KeyboardInterrupt:
        rprint("\n[yellow]Demo interrupted by user[/yellow]")
        demo.generate_final_report()
        if cleanup:
            demo.cleanup()
    except Exception as e:
        rprint(f"\n[red]Demo failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("full-cycle-status")
def show_demo_status():
    """Show status of full cycle demo data"""
    
    data_dir = Path("./full_cycle_data")
    if not data_dir.exists():
        rprint("[yellow]No demo data found. Run 'dsl swarm full-cycle' first.[/yellow]")
        return
    
    # Show available reports
    reports = list(data_dir.glob("report_*.json"))
    
    if reports:
        table = Table(title="Full Cycle Demo Reports")
        table.add_column("Report ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Efficiency", style="yellow")
        table.add_column("Tasks Completed", style="magenta")
        
        for report_path in sorted(reports, reverse=True)[:5]:
            try:
                with open(report_path) as f:
                    report = json.load(f)
                
                table.add_row(
                    report["demo_id"],
                    report["timestamp"][:19],
                    f"{report['metrics']['efficiency_score']:.1f}%",
                    str(report["metrics"]["work_completed"])
                )
            except:
                pass
        
        console.print(table)
    else:
        rprint("[yellow]No reports found in demo data directory.[/yellow]")


@app.command("full-cycle-clean")
def clean_demo_data():
    """Clean all full cycle demo data"""
    
    data_dir = Path("./full_cycle_data")
    if data_dir.exists():
        import shutil
        shutil.rmtree(data_dir)
        rprint("[green]✓ Cleaned full cycle demo data[/green]")
    else:
        rprint("[yellow]No demo data to clean[/yellow]")


if __name__ == "__main__":
    app()