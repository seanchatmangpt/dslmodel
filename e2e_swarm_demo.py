#!/usr/bin/env python3
"""
End-to-End SwarmAgent Ecosystem Demonstration

This script demonstrates the complete SwarmAgent ecosystem from initialization
through multi-agent coordination with full OpenTelemetry integration.
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class E2ESwarmDemo:
    def __init__(self):
        self.span_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
        self.results = {}
        
    def run_command(self, cmd: str, description: str = None) -> Dict[str, Any]:
        """Execute command and capture results."""
        if description:
            console.print(f"[blue]▶[/blue] {description}")
            console.print(f"[dim]Running: {cmd}[/dim]")
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/Users/sac/dev/dslmodel"
            )
            
            success = result.returncode == 0
            if success:
                console.print(f"[green]✅ Success[/green]")
            else:
                console.print(f"[red]❌ Failed (exit code: {result.returncode})[/red]")
                if result.stderr:
                    console.print(f"[red]Error: {result.stderr[:200]}[/red]")
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            console.print(f"[red]❌ Exception: {e}[/red]")
            return {"success": False, "error": str(e)}
    
    def get_span_count(self) -> int:
        """Count spans in telemetry file."""
        if not self.span_file.exists():
            return 0
        
        count = 0
        try:
            with self.span_file.open() as f:
                for line in f:
                    if line.strip():
                        try:
                            json.loads(line)
                            count += 1
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        
        return count
    
    def display_spans(self, last_n: int = 5):
        """Display recent spans in a table."""
        if not self.span_file.exists():
            console.print("[yellow]No telemetry file found[/yellow]")
            return
        
        spans = []
        try:
            with self.span_file.open() as f:
                for line in f:
                    if line.strip():
                        try:
                            span = json.loads(line)
                            spans.append(span)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            console.print(f"[red]Error reading spans: {e}[/red]")
            return
        
        if not spans:
            console.print("[yellow]No spans found[/yellow]")
            return
        
        # Get last N spans
        recent_spans = spans[-last_n:] if len(spans) > last_n else spans
        
        table = Table(title=f"Last {len(recent_spans)} Telemetry Spans")
        table.add_column("Time", style="cyan")
        table.add_column("Span Name", style="green")
        table.add_column("Agent", style="blue")
        table.add_column("Trigger", style="yellow")
        table.add_column("Attributes", style="dim")
        
        for span in recent_spans:
            timestamp = span.get("timestamp", span.get("ts", ""))
            if isinstance(timestamp, (int, float)):
                time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            else:
                time_str = str(timestamp)[:8] if timestamp else "Unknown"
            
            name = span.get("name", "")
            attrs = span.get("attributes", span.get("attrs", {}))
            agent = attrs.get("swarm.agent", attrs.get("agent", ""))
            trigger = attrs.get("swarm.trigger", attrs.get("trigger", ""))
            
            # Format other attributes
            other_attrs = []
            for k, v in attrs.items():
                if k not in ["swarm.agent", "swarm.trigger", "agent", "trigger"]:
                    other_attrs.append(f"{k}={v}")
            
            attrs_str = ", ".join(other_attrs) if other_attrs else ""
            
            table.add_row(
                time_str,
                name,
                agent,
                trigger,
                attrs_str
            )
        
        console.print(table)
    
    def step_1_initialization(self):
        """Step 1: System initialization and validation."""
        console.print(Panel.fit(
            "[bold blue]STEP 1: SYSTEM INITIALIZATION[/bold blue]",
            border_style="blue"
        ))
        
        # Check CLI availability
        result = self.run_command(
            "python swarm_cli.py --help",
            "Verify SwarmAgent CLI is available"
        )
        self.results["cli_available"] = result["success"]
        
        # Show system status
        result = self.run_command(
            "python swarm_cli.py status",
            "Check system status"
        )
        self.results["system_status"] = result["success"]
        
        # List available agents
        result = self.run_command(
            "python swarm_cli.py list",
            "List available agent types"
        )
        self.results["agent_list"] = result["success"]
        
        console.print(f"[green]✅ Initialization: {sum([self.results['cli_available'], self.results['system_status'], self.results['agent_list']])}/3 checks passed[/green]\n")
    
    def step_2_agent_generation(self):
        """Step 2: Dynamic agent generation."""
        console.print(Panel.fit(
            "[bold green]STEP 2: DYNAMIC AGENT GENERATION[/bold green]",
            border_style="green"
        ))
        
        agent_name = f"E2ETestAgent_{int(time.time())}"
        
        result = self.run_command(
            f"python swarm_cli.py generate {agent_name} --states INIT,PROCESSING,COMPLETE --triggers start,process,finish",
            f"Generate new agent: {agent_name}"
        )
        
        self.results["agent_generation"] = result["success"]
        self.results["generated_agent"] = agent_name
        
        # Verify file creation
        expected_file = Path(f"/Users/sac/dev/dslmodel/{agent_name.lower()}_agent.py")
        file_exists = expected_file.exists()
        
        if file_exists:
            console.print(f"[green]✅ Agent file created: {expected_file}[/green]")
        else:
            console.print(f"[red]❌ Agent file not found: {expected_file}[/red]")
        
        self.results["agent_file_created"] = file_exists
        console.print(f"[green]✅ Agent Generation: {'Success' if result['success'] and file_exists else 'Failed'}[/green]\n")
    
    def step_3_telemetry_setup(self):
        """Step 3: Telemetry system setup."""
        console.print(Panel.fit(
            "[bold yellow]STEP 3: TELEMETRY SYSTEM SETUP[/bold yellow]",
            border_style="yellow"
        ))
        
        # Clean previous telemetry data
        initial_spans = self.get_span_count()
        console.print(f"[dim]Initial span count: {initial_spans}[/dim]")
        
        # Clear with cleanup span
        result = self.run_command(
            "python swarm_cli.py emit cleanup --agent system --trigger reset",
            "Clear telemetry data"
        )
        
        self.results["telemetry_cleanup"] = result["success"]
        
        # Verify telemetry file
        self.span_file.parent.mkdir(parents=True, exist_ok=True)
        
        telemetry_ready = self.span_file.exists()
        console.print(f"[green]✅ Telemetry Setup: {'Ready' if telemetry_ready else 'Failed'}[/green]\n")
        
        self.results["telemetry_ready"] = telemetry_ready
    
    def step_4_multi_agent_coordination(self):
        """Step 4: Multi-agent coordination workflow."""
        console.print(Panel.fit(
            "[bold magenta]STEP 4: MULTI-AGENT COORDINATION[/bold magenta]",
            border_style="magenta"
        ))
        
        pre_workflow_spans = self.get_span_count()
        
        # Execute complete governance workflow
        result = self.run_command(
            "python swarm_cli.py workflow governance",
            "Execute Roberts Rules governance workflow"
        )
        self.results["governance_workflow"] = result["success"]
        
        time.sleep(1)  # Allow file write
        
        # Execute sprint workflow
        result = self.run_command(
            "python swarm_cli.py workflow sprint", 
            "Execute Scrum sprint workflow"
        )
        self.results["sprint_workflow"] = result["success"]
        
        time.sleep(1)  # Allow file write
        
        # Execute improvement workflow
        result = self.run_command(
            "python swarm_cli.py workflow improvement",
            "Execute Lean improvement workflow"
        )
        self.results["improvement_workflow"] = result["success"]
        
        time.sleep(1)  # Allow file write
        
        post_workflow_spans = self.get_span_count()
        workflow_spans_created = post_workflow_spans - pre_workflow_spans
        
        console.print(f"[green]✅ Workflows: {sum([self.results['governance_workflow'], self.results['sprint_workflow'], self.results['improvement_workflow']])}/3 completed[/green]")
        console.print(f"[green]✅ Spans Created: {workflow_spans_created}[/green]\n")
        
        self.results["workflow_spans_created"] = workflow_spans_created
    
    def step_5_real_time_monitoring(self):
        """Step 5: Real-time telemetry monitoring."""
        console.print(Panel.fit(
            "[bold cyan]STEP 5: REAL-TIME MONITORING[/bold cyan]",
            border_style="cyan"
        ))
        
        # Test span watching
        result = self.run_command(
            "python swarm_cli.py watch --last 10",
            "Watch recent telemetry spans"
        )
        
        self.results["span_watching"] = result["success"]
        
        # Display spans in rich format
        console.print("[blue]Recent Telemetry Activity:[/blue]")
        self.display_spans(8)
        
        console.print(f"[green]✅ Monitoring: {'Active' if result['success'] else 'Failed'}[/green]\n")
    
    def step_6_poetry_integration(self):
        """Step 6: Poetry/poe integration validation."""
        console.print(Panel.fit(
            "[bold red]STEP 6: POETRY INTEGRATION[/bold red]",
            border_style="red"
        ))
        
        # Test poetry commands
        poetry_commands = [
            ("poetry run poe swarm", "SwarmAgent CLI help"),
            ("poetry run poe swarm-status", "System status via poetry"),
            ("poetry run poe swarm-demo", "Demo via poetry")
        ]
        
        poetry_results = []
        for cmd, desc in poetry_commands:
            result = self.run_command(cmd, desc)
            poetry_results.append(result["success"])
        
        self.results["poetry_integration"] = all(poetry_results)
        console.print(f"[green]✅ Poetry Integration: {sum(poetry_results)}/{len(poetry_results)} commands successful[/green]\n")
    
    def step_7_system_validation(self):
        """Step 7: Complete system validation."""
        console.print(Panel.fit(
            "[bold white]STEP 7: SYSTEM VALIDATION[/bold white]",
            border_style="white"
        ))
        
        # Final system check
        final_span_count = self.get_span_count()
        
        # Run comprehensive status
        result = self.run_command(
            "python swarm_cli.py status",
            "Final system status check"
        )
        
        self.results["final_validation"] = result["success"]
        self.results["final_span_count"] = final_span_count
        
        console.print(f"[green]✅ Final Validation: {'Passed' if result['success'] else 'Failed'}[/green]")
        console.print(f"[green]✅ Total Spans: {final_span_count}[/green]\n")
    
    def generate_summary(self):
        """Generate final demonstration summary."""
        console.print(Panel.fit(
            "[bold yellow]🎯 E2E DEMONSTRATION SUMMARY[/bold yellow]",
            border_style="yellow"
        ))
        
        # Count successes
        success_count = sum(1 for k, v in self.results.items() 
                          if isinstance(v, bool) and v)
        total_checks = sum(1 for k, v in self.results.items() 
                         if isinstance(v, bool))
        
        success_rate = (success_count / total_checks * 100) if total_checks > 0 else 0
        
        # Create summary table
        table = Table(title="Demonstration Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")
        
        table.add_row("CLI Availability", "✅" if self.results.get("cli_available") else "❌", "SwarmAgent CLI working")
        table.add_row("System Status", "✅" if self.results.get("system_status") else "❌", "Core system functional")
        table.add_row("Agent Generation", "✅" if self.results.get("agent_generation") else "❌", f"Created: {self.results.get('generated_agent', 'N/A')}")
        table.add_row("File Creation", "✅" if self.results.get("agent_file_created") else "❌", "Dynamic agent file generated")
        table.add_row("Telemetry Setup", "✅" if self.results.get("telemetry_ready") else "❌", "OTEL span streaming ready")
        table.add_row("Governance Workflow", "✅" if self.results.get("governance_workflow") else "❌", "Roberts Rules coordination")
        table.add_row("Sprint Workflow", "✅" if self.results.get("sprint_workflow") else "❌", "Scrum delivery process")
        table.add_row("Improvement Workflow", "✅" if self.results.get("improvement_workflow") else "❌", "Lean optimization cycle")
        table.add_row("Span Monitoring", "✅" if self.results.get("span_watching") else "❌", "Real-time telemetry watch")
        table.add_row("Poetry Integration", "✅" if self.results.get("poetry_integration") else "❌", "poe task runner working")
        table.add_row("Final Validation", "✅" if self.results.get("final_validation") else "❌", f"Total spans: {self.results.get('final_span_count', 0)}")
        
        console.print(table)
        
        # Overall result
        if success_rate >= 90:
            status_color = "green"
            status_icon = "🎉"
            status_text = "EXCELLENT"
        elif success_rate >= 75:
            status_color = "yellow"
            status_icon = "⚠️"
            status_text = "GOOD"
        else:
            status_color = "red"
            status_icon = "❌"
            status_text = "NEEDS WORK"
        
        console.print(f"\n[{status_color}]{status_icon} Overall Success Rate: {success_rate:.1f}% ({success_count}/{total_checks}) - {status_text}[/{status_color}]")
        
        # Key achievements
        console.print("\n[bold]🏆 Key Achievements:[/bold]")
        console.print("• Multi-agent coordination through OpenTelemetry spans")
        console.print("• Dynamic agent generation from templates")
        console.print("• Real-time telemetry monitoring and visualization")
        console.print("• Complete CLI integration (standalone + poetry)")
        console.print("• Roberts Rules → Scrum → Lean workflow orchestration")
        console.print("• Production-ready agent state machine patterns")
        
        return success_rate >= 90
    
    def run_complete_demo(self):
        """Execute the complete end-to-end demonstration."""
        console.print(Panel.fit(
            "[bold white]🚀 SWARMAGENT ECOSYSTEM E2E DEMONSTRATION[/bold white]",
            border_style="white"
        ))
        
        start_time = time.time()
        
        try:
            self.step_1_initialization()
            self.step_2_agent_generation()
            self.step_3_telemetry_setup()
            self.step_4_multi_agent_coordination()
            self.step_5_real_time_monitoring()
            self.step_6_poetry_integration()
            self.step_7_system_validation()
            
            duration = time.time() - start_time
            console.print(f"\n[dim]Total demonstration time: {duration:.2f} seconds[/dim]")
            
            success = self.generate_summary()
            return success
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Demonstration interrupted by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]Demonstration failed with error: {e}[/red]")
            return False


def main():
    """Main entry point for E2E demonstration."""
    demo = E2ESwarmDemo()
    success = demo.run_complete_demo()
    
    if success:
        console.print("\n[green]🎉 E2E Demonstration completed successfully![/green]")
        return 0
    else:
        console.print("\n[red]❌ E2E Demonstration encountered issues[/red]")
        return 1


if __name__ == "__main__":
    exit(main())