#!/usr/bin/env python3
"""
Full Cycle Generation Demo for DSLModel Swarm
Demonstrates end-to-end automated generation, execution, and evolution
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint

from .swarm import SwarmCoordinator

console = Console()
app = typer.Typer(help="Full cycle generation and automation demo")


class FullCycleDemo:
    """Orchestrates a complete swarm lifecycle demo"""
    
    def __init__(self):
        self.coordinator = SwarmCoordinator(data_dir="./full_cycle_data")
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


@app.command("run")
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


@app.command("status")
def show_demo_status():
    """Show status of full cycle demo data"""
    
    data_dir = Path("./full_cycle_data")
    if not data_dir.exists():
        rprint("[yellow]No demo data found. Run 'full-cycle run' first.[/yellow]")
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


@app.command("clean")
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