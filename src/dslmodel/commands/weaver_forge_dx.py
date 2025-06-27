#!/usr/bin/env python3
"""
Weaver Forge DX Command - CLI Interface for Git Agent Auto DX Loop

Provides command-line interface for managing the Weaver Forge Git Agent
and automating developer experience workflows.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..weaver_forge_git_agent import WeaverForgeGitAgent, WeaverForgeConfig, DXLoopPhase, GitAgentAction

app = typer.Typer(help="Weaver Forge Git Agent Auto DX Loop Commands")
console = Console()

@app.command()
def start(
    duration: int = typer.Option(60, "--duration", "-d", help="Duration in minutes"),
    auto_commit: bool = typer.Option(True, "--auto-commit/--no-auto-commit", help="Enable auto-commit"),
    auto_push: bool = typer.Option(False, "--auto-push/--no-auto-push", help="Enable auto-push"),
    auto_merge: bool = typer.Option(False, "--auto-merge/--no-auto-merge", help="Enable auto-merge"),
    min_confidence: float = typer.Option(0.8, "--min-confidence", "-c", help="Minimum confidence threshold"),
    max_commits: int = typer.Option(50, "--max-commits", help="Maximum daily commits"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Start the Weaver Forge Git Agent Auto DX Loop"""
    
    console.print(Panel("🚀 Starting Weaver Forge Git Agent Auto DX Loop", style="bold cyan"))
    
    # Create configuration
    config = WeaverForgeConfig(
        auto_commit=auto_commit,
        auto_push=auto_push,
        auto_merge=auto_merge,
        min_confidence=min_confidence,
        max_daily_commits=max_commits,
        dx_optimization_enabled=True
    )
    
    # Display configuration
    if verbose:
        _display_config(config)
    
    # Create and start agent
    agent = WeaverForgeGitAgent(config)
    
    try:
        asyncio.run(agent.start_auto_dx_loop(duration_minutes=duration))
    except KeyboardInterrupt:
        console.print("[yellow]🛑 Auto DX Loop stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]💥 Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def status():
    """Show current status of Weaver Forge Git Agent"""
    
    console.print(Panel("📊 Weaver Forge Git Agent Status", style="bold blue"))
    
    # Check for existing reports
    report_file = Path("weaver_forge_git_agent_report.json")
    feedback_file = Path("weaver_forge_dx_feedback.json")
    
    if report_file.exists():
        with open(report_file, 'r') as f:
            report = json.load(f)
        _display_status_report(report)
    else:
        console.print("[yellow]⚠️ No previous runs found[/yellow]")
    
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            feedback_history = json.load(f)
        _display_feedback_summary(feedback_history)
    
    # Show semantic conventions status
    _display_semconv_status()

@app.command()
def analyze():
    """Analyze repository for DX opportunities"""
    
    console.print(Panel("🔍 Repository DX Analysis", style="bold yellow"))
    
    async def run_analysis():
        config = WeaverForgeConfig(auto_commit=False, auto_push=False)
        agent = WeaverForgeGitAgent(config)
        
        # Initialize agent
        await agent._initialize_weaver_forge()
        
        # Run analysis phases
        opportunities = await agent._detect_git_opportunities()
        state = await agent._analyze_repository_state()
        
        # Display results
        _display_opportunities(opportunities)
        _display_repository_state(state)
        
        # Generate recommendations
        recommendations = agent._generate_recommendations()
        _display_recommendations(recommendations)
    
    try:
        asyncio.run(run_analysis())
    except Exception as e:
        console.print(f"[red]💥 Analysis failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def configure(
    auto_commit: Optional[bool] = typer.Option(None, "--auto-commit/--no-auto-commit"),
    auto_push: Optional[bool] = typer.Option(None, "--auto-push/--no-auto-push"),
    auto_merge: Optional[bool] = typer.Option(None, "--auto-merge/--no-auto-merge"),
    min_confidence: Optional[float] = typer.Option(None, "--min-confidence", "-c"),
    max_commits: Optional[int] = typer.Option(None, "--max-commits"),
    save: bool = typer.Option(False, "--save", help="Save configuration to file")
):
    """Configure Weaver Forge Git Agent settings"""
    
    console.print(Panel("⚙️ Weaver Forge Git Agent Configuration", style="bold magenta"))
    
    # Load existing config or create new
    config_file = Path("weaver_forge_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        config = WeaverForgeConfig(**config_data)
    else:
        config = WeaverForgeConfig()
    
    # Update configuration with provided values
    if auto_commit is not None:
        config.auto_commit = auto_commit
    if auto_push is not None:
        config.auto_push = auto_push
    if auto_merge is not None:
        config.auto_merge = auto_merge
    if min_confidence is not None:
        config.min_confidence = min_confidence
    if max_commits is not None:
        config.max_daily_commits = max_commits
    
    # Display current configuration
    _display_config(config)
    
    # Save if requested
    if save:
        config_dict = {
            "auto_commit": config.auto_commit,
            "auto_push": config.auto_push,
            "auto_merge": config.auto_merge,
            "min_confidence": config.min_confidence,
            "max_daily_commits": config.max_daily_commits,
            "git_hooks_enabled": config.git_hooks_enabled,
            "dx_optimization_enabled": config.dx_optimization_enabled
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        console.print(f"[green]✅ Configuration saved to {config_file}[/green]")

@app.command()
def metrics():
    """Display DX metrics and analytics"""
    
    console.print(Panel("📈 Developer Experience Metrics", style="bold green"))
    
    # Load feedback history for metrics
    feedback_file = Path("weaver_forge_dx_feedback.json")
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            feedback_history = json.load(f)
        
        _display_metrics_analytics(feedback_history)
    else:
        console.print("[yellow]⚠️ No metrics data available. Run the agent first.[/yellow]")

@app.command()
def validate():
    """Validate Weaver Forge Git Agent setup and semantic conventions"""
    
    console.print(Panel("✅ Weaver Forge Validation", style="bold blue"))
    
    async def run_validation():
        # Create agent for validation
        config = WeaverForgeConfig()
        agent = WeaverForgeGitAgent(config)
        
        validation_results = {
            "semantic_conventions": False,
            "git_repository": False,
            "otel_integration": False,
            "weaver_system": False
        }
        
        try:
            # Validate semantic conventions
            semconv_file = Path("semconv_layers/git_agent_operations.yaml")
            if semconv_file.exists():
                validation_results["semantic_conventions"] = True
                console.print("[green]✅ Git agent semantic conventions found[/green]")
            else:
                console.print("[red]❌ Git agent semantic conventions missing[/red]")
            
            # Validate git repository
            import subprocess
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                validation_results["git_repository"] = True
                console.print("[green]✅ Git repository accessible[/green]")
            else:
                console.print("[red]❌ Not in a git repository[/red]")
            
            # Validate weaver system
            try:
                await agent._initialize_weaver_forge()
                validation_results["weaver_system"] = True
                console.print("[green]✅ Weaver system initialized[/green]")
            except Exception as e:
                console.print(f"[red]❌ Weaver system error: {e}[/red]")
            
            # Validate OTEL integration
            try:
                agent.otel_monitor.start_monitoring()
                agent.otel_monitor.stop_monitoring()
                validation_results["otel_integration"] = True
                console.print("[green]✅ OTEL integration working[/green]")
            except Exception as e:
                console.print(f"[red]❌ OTEL integration error: {e}[/red]")
            
        except Exception as e:
            console.print(f"[red]💥 Validation error: {e}[/red]")
        
        # Display validation summary
        _display_validation_summary(validation_results)
        
        # Return exit code based on validation
        if all(validation_results.values()):
            console.print("[bold green]🎉 All validations passed![/bold green]")
            return 0
        else:
            console.print("[bold red]❌ Some validations failed[/bold red]")
            return 1
    
    try:
        exit_code = asyncio.run(run_validation())
        if exit_code != 0:
            raise typer.Exit(exit_code)
    except Exception as e:
        console.print(f"[red]💥 Validation failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent entries to show"),
    phase: Optional[str] = typer.Option(None, "--phase", help="Filter by DX loop phase"),
    action: Optional[str] = typer.Option(None, "--action", help="Filter by git agent action")
):
    """Show history of git agent decisions and actions"""
    
    console.print(Panel("📜 Git Agent Decision History", style="bold yellow"))
    
    feedback_file = Path("weaver_forge_dx_feedback.json")
    if not feedback_file.exists():
        console.print("[yellow]⚠️ No history available. Run the agent first.[/yellow]")
        return
    
    with open(feedback_file, 'r') as f:
        feedback_history = json.load(f)
    
    # Filter and display history
    _display_decision_history(feedback_history, limit, phase, action)

def _display_config(config: WeaverForgeConfig):
    """Display configuration in a table"""
    table = Table(title="Weaver Forge Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Description", style="dim")
    
    settings = [
        ("Auto Commit", str(config.auto_commit), "Automatically commit changes"),
        ("Auto Push", str(config.auto_push), "Automatically push commits"),
        ("Auto Merge", str(config.auto_merge), "Automatically merge branches"),
        ("Min Confidence", f"{config.min_confidence:.1f}", "Minimum confidence for actions"),
        ("Max Daily Commits", str(config.max_daily_commits), "Maximum commits per day"),
        ("Git Hooks", str(config.git_hooks_enabled), "Enable git hooks"),
        ("DX Optimization", str(config.dx_optimization_enabled), "Enable DX optimization")
    ]
    
    for setting, value, description in settings:
        table.add_row(setting, value, description)
    
    console.print(table)

def _display_status_report(report: dict):
    """Display status report"""
    table = Table(title="Last Run Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    metrics = [
        ("Execution Time", f"{report.get('execution_time', 0):.1f}s"),
        ("Loop Iterations", str(report.get('loop_iterations', 0))),
        ("Decisions Made", str(report.get('decisions_made', 0))),
        ("Success Rate", f"{report.get('success_rate', 0):.1%}"),
        ("DX Improvement", f"{report.get('dx_improvement', 0):.1%}")
    ]
    
    if 'final_metrics' in report:
        final_metrics = report['final_metrics']
        metrics.extend([
            ("Commit Frequency", f"{final_metrics.get('commit_frequency', 0):.2f}/hr"),
            ("Automation Efficiency", f"{final_metrics.get('automation_efficiency', 0):.1%}"),
            ("Branch Health", f"{final_metrics.get('branch_health', 0):.1%}")
        ])
    
    for metric, value in metrics:
        table.add_row(metric, value)
    
    console.print(table)

def _display_feedback_summary(feedback_history: List[dict]):
    """Display feedback summary"""
    if not feedback_history:
        return
    
    latest = feedback_history[-1]
    total_runs = len(feedback_history)
    avg_success_rate = sum(f.get('success_rate', 0) for f in feedback_history) / total_runs
    
    console.print(f"\n[bold]Feedback Summary:[/bold]")
    console.print(f"• Total Runs: {total_runs}")
    console.print(f"• Average Success Rate: {avg_success_rate:.1%}")
    console.print(f"• Latest DX Improvement: {latest.get('dx_improvement', 0):.1%}")

def _display_semconv_status():
    """Display semantic conventions status"""
    semconv_file = Path("semconv_layers/git_agent_operations.yaml")
    status = "✅ Available" if semconv_file.exists() else "❌ Missing"
    console.print(f"\n[bold]Semantic Conventions:[/bold] {status}")

def _display_opportunities(opportunities: List[dict]):
    """Display detected opportunities"""
    if not opportunities:
        console.print("[green]✅ No immediate opportunities detected[/green]")
        return
    
    table = Table(title="Detected Opportunities")
    table.add_column("Type", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Action", style="magenta")
    table.add_column("Details", style="dim")
    
    for opp in opportunities:
        details = ""
        if "files" in opp:
            details = f"{opp['files']} files"
        elif "commits" in opp:
            details = f"{opp['commits']} commits"
        elif "branches" in opp:
            details = f"{opp['branches']} branches"
        
        table.add_row(
            opp["type"].replace("_", " ").title(),
            opp["priority"].title(),
            opp["action"].value.title(),
            details
        )
    
    console.print(table)

def _display_repository_state(state: dict):
    """Display repository state"""
    table = Table(title="Repository State")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    for key, value in state.items():
        formatted_key = key.replace("_", " ").title()
        table.add_row(formatted_key, str(value))
    
    console.print(table)

def _display_recommendations(recommendations: List[str]):
    """Display recommendations"""
    if not recommendations:
        console.print("[green]✅ No specific recommendations at this time[/green]")
        return
    
    console.print("\n[bold yellow]🎯 Recommendations:[/bold yellow]")
    for i, rec in enumerate(recommendations, 1):
        console.print(f"  {i}. {rec}")

def _display_metrics_analytics(feedback_history: List[dict]):
    """Display metrics analytics"""
    if not feedback_history:
        return
    
    # Calculate trends
    recent_runs = feedback_history[-5:] if len(feedback_history) >= 5 else feedback_history
    avg_improvement = sum(f.get('dx_improvement', 0) for f in recent_runs) / len(recent_runs)
    avg_success_rate = sum(f.get('success_rate', 0) for f in recent_runs) / len(recent_runs)
    
    console.print(f"[bold]Analytics (Last {len(recent_runs)} runs):[/bold]")
    console.print(f"• Average DX Improvement: {avg_improvement:.1%}")
    console.print(f"• Average Success Rate: {avg_success_rate:.1%}")
    console.print(f"• Total Decisions: {sum(f.get('decisions_made', 0) for f in recent_runs)}")

def _display_validation_summary(results: dict):
    """Display validation summary"""
    table = Table(title="Validation Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    
    for component, status in results.items():
        status_text = "✅ PASS" if status else "❌ FAIL"
        formatted_component = component.replace("_", " ").title()
        table.add_row(formatted_component, status_text)
    
    console.print(table)

def _display_decision_history(feedback_history: List[dict], limit: int, phase_filter: str, action_filter: str):
    """Display decision history"""
    # Flatten decision history from feedback
    all_decisions = []
    for feedback in feedback_history:
        decisions_made = feedback.get('decisions_made', 0)
        all_decisions.append({
            'timestamp': feedback.get('loop_iteration', 0),
            'decisions_count': decisions_made,
            'success_rate': feedback.get('success_rate', 0)
        })
    
    # Apply filters and limit
    filtered_decisions = all_decisions[-limit:]
    
    table = Table(title="Decision History")
    table.add_column("Iteration", style="cyan")
    table.add_column("Decisions", style="magenta")
    table.add_column("Success Rate", style="green")
    
    for decision in filtered_decisions:
        table.add_row(
            str(decision['timestamp']),
            str(decision['decisions_count']),
            f"{decision['success_rate']:.1%}"
        )
    
    console.print(table)

if __name__ == "__main__":
    app()