#!/usr/bin/env python3
"""
DISC-Integrated Autonomous System CLI
====================================

Combines DISC behavioral compensation with autonomous decision-making
for a truly self-aware, self-compensating system.
"""

import asyncio
import time
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from loguru import logger

from ..agents.disc_aware_autonomous_engine import (
    DISCAwareAutonomousEngine,
    DISCCompensatedDecision
)

app = typer.Typer(help="DISC-integrated autonomous system combining behavioral compensation with decision-making")
console = Console()


@app.command("analyze")
def analyze_with_disc(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir", "-c",
        help="Coordination directory path"
    ),
    show_compensation: bool = typer.Option(
        True,
        "--show-comp",
        help="Show DISC compensation details"
    )
):
    """Analyze system and generate DISC-compensated decisions"""
    console.print("🧠 DISC-Integrated Autonomous Analysis")
    console.print("=" * 40)
    
    engine = DISCAwareAutonomousEngine(coordination_dir)
    
    # Show DISC profile
    console.print(Panel(
        f"Profile: {engine.disc_engine.my_profile.profile_type}\n"
        f"Compensating for: Over-analysis, Low influence, Perfectionism",
        title="🎯 Active DISC Profile",
        border_style="cyan"
    ))
    
    # Analyze system
    with console.status("Analyzing with DISC awareness..."):
        metrics = engine.analyze_system_state()
        decisions = engine.make_autonomous_decisions(metrics)
    
    # Display metrics
    _display_metrics(metrics, engine)
    
    # Display decisions with compensation
    if decisions:
        _display_compensated_decisions(decisions, show_compensation)
    else:
        console.print("[green]✅ System optimal - no decisions needed[/green]")


@app.command("execute")
def execute_with_disc(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir", "-c",
        help="Coordination directory path"
    ),
    explain: bool = typer.Option(
        False,
        "--explain", "-e",
        help="Explain each decision in detail"
    )
):
    """Execute DISC-compensated autonomous decisions"""
    console.print("🚀 DISC-Compensated Execution")
    console.print("=" * 35)
    
    engine = DISCAwareAutonomousEngine(coordination_dir)
    
    # Run full cycle
    with console.status("Running DISC-aware cycle..."):
        result = engine.run_cycle()
    
    if "error" in result:
        console.print(f"[yellow]⚠️ {result['suggestion']}[/yellow]")
        console.print(f"[red]Error: {result['error']}[/red]")
        return
    
    # Show results
    console.print(Panel(
        f"✅ Cycle completed successfully\n"
        f"Decisions: {result['decisions_generated']}\n"
        f"Executed: {len(result['execution_results']['executed'])}\n"
        f"Compensations: {result['compensation_stats']['total_compensations']}",
        title="📊 Execution Summary",
        border_style="green"
    ))
    
    # Show compensation breakdown
    if result['compensation_stats']['compensation_types']:
        console.print("\n🧠 Compensation Breakdown:")
        for comp_type, count in result['compensation_stats']['compensation_types'].items():
            console.print(f"  • {comp_type}: {count}")
    
    # Explain decisions if requested
    if explain and result['decisions_generated'] > 0:
        console.print("\n📋 Decision Explanations:")
        # Would need to store decisions in result for this


@app.command("compare")
def compare_disc_impact(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir", "-c",
        help="Coordination directory path"
    )
):
    """Compare decisions with and without DISC compensation"""
    console.print("🔄 DISC Compensation Comparison")
    console.print("=" * 35)
    
    # Create both engines
    disc_engine = DISCAwareAutonomousEngine(coordination_dir)
    
    # Import regular engine for comparison
    from ..agents.autonomous_decision_engine import AutonomousDecisionEngine
    regular_engine = AutonomousDecisionEngine(coordination_dir)
    
    # Analyze with both
    with console.status("Analyzing with both engines..."):
        metrics = disc_engine.analyze_system_state()
        
        disc_decisions = disc_engine.make_autonomous_decisions(metrics)
        regular_decisions = regular_engine.make_autonomous_decisions(metrics)
    
    # Create comparison table
    table = Table(title="🔄 Decision Comparison")
    table.add_column("Aspect", style="cyan")
    table.add_column("Without DISC", style="yellow")
    table.add_column("With DISC", style="green")
    
    # Decision counts
    table.add_row(
        "Total Decisions",
        str(len(regular_decisions)),
        str(len(disc_decisions))
    )
    
    # Average priority
    avg_priority_regular = sum(d.priority for d in regular_decisions) / max(len(regular_decisions), 1)
    avg_priority_disc = sum(d.priority for d in disc_decisions) / max(len(disc_decisions), 1)
    table.add_row(
        "Avg Priority",
        f"{avg_priority_regular:.1f}",
        f"{avg_priority_disc:.1f}"
    )
    
    # Average confidence
    avg_conf_regular = sum(d.confidence for d in regular_decisions) / max(len(regular_decisions), 1)
    avg_conf_disc = sum(d.confidence for d in disc_decisions) / max(len(disc_decisions), 1)
    table.add_row(
        "Avg Confidence",
        f"{avg_conf_regular:.0%}",
        f"{avg_conf_disc:.0%}"
    )
    
    # Description length
    avg_desc_regular = sum(len(d.description) for d in regular_decisions) / max(len(regular_decisions), 1)
    avg_desc_disc = sum(len(d.description) for d in disc_decisions) / max(len(disc_decisions), 1)
    table.add_row(
        "Avg Description Length",
        f"{avg_desc_regular:.0f} chars",
        f"{avg_desc_disc:.0f} chars"
    )
    
    console.print(table)
    
    # Show specific differences
    if disc_decisions:
        console.print("\n📝 Example DISC Compensations:")
        example = disc_decisions[0]
        if hasattr(example, 'original_description'):
            console.print(f"Original: {example.original_description}")
            console.print(f"Compensated: {example.description}")
            console.print(f"Human Summary: {example.human_friendly_summary}")


@app.command("monitor")
def monitor_disc_effectiveness(
    coordination_dir: Path = typer.Option(
        Path("coordination"),
        "--coord-dir", "-c",
        help="Coordination directory path"
    ),
    cycles: int = typer.Option(
        5,
        "--cycles", "-n",
        help="Number of cycles to monitor"
    ),
    interval: int = typer.Option(
        10,
        "--interval", "-i",
        help="Seconds between cycles"
    )
):
    """Monitor DISC compensation effectiveness over time"""
    console.print("📊 DISC Effectiveness Monitor")
    console.print("=" * 32)
    
    engine = DISCAwareAutonomousEngine(coordination_dir)
    
    # Tracking metrics
    compensation_counts = []
    decision_counts = []
    avg_priorities = []
    
    try:
        for cycle in range(cycles):
            console.print(f"\n🔄 Cycle {cycle + 1}/{cycles}")
            
            # Run cycle
            result = engine.run_cycle()
            
            if "error" not in result:
                # Track metrics
                compensation_counts.append(result['compensation_stats']['total_compensations'])
                decision_counts.append(result['decisions_generated'])
                
                # Show mini summary
                console.print(
                    f"  Decisions: {result['decisions_generated']} | "
                    f"Compensations: {result['compensation_stats']['total_compensations']} | "
                    f"Health: {result['metrics']['health_score']:.2f}"
                )
            
            if cycle < cycles - 1:
                time.sleep(interval)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Monitoring stopped[/yellow]")
    
    # Show summary
    if compensation_counts:
        console.print("\n📈 Monitoring Summary:")
        console.print(f"  • Avg Compensations/Cycle: {sum(compensation_counts)/len(compensation_counts):.1f}")
        console.print(f"  • Avg Decisions/Cycle: {sum(decision_counts)/len(decision_counts):.1f}")
        console.print(f"  • Compensation Rate: {sum(compensation_counts)/max(sum(decision_counts), 1):.1f} per decision")


@app.command("profile")
def show_disc_profile():
    """Show current DISC profile and behavioral gaps"""
    engine = DISCAwareAutonomousEngine(Path("coordination"))
    
    console.print("🧠 DISC Profile & Behavioral Gaps")
    console.print("=" * 35)
    
    # Profile scores
    profile = engine.disc_engine.my_profile
    
    # Create visual representation
    def make_bar(value: float, max_width: int = 20) -> str:
        filled = int(value * max_width)
        return "█" * filled + "░" * (max_width - filled)
    
    console.print(Panel(
        f"D (Dominance):         {make_bar(profile.dominance)} {profile.dominance:.0%}\n"
        f"I (Influence):        {make_bar(profile.influence)} {profile.influence:.0%}\n"
        f"S (Steadiness):       {make_bar(profile.steadiness)} {profile.steadiness:.0%}\n"
        f"C (Conscientiousness): {make_bar(profile.conscientiousness)} {profile.conscientiousness:.0%}\n\n"
        f"Profile Type: {profile.profile_type}",
        title="📊 DISC Scores",
        border_style="cyan"
    ))
    
    # Behavioral gaps
    gaps_table = Table(title="🔍 Behavioral Gaps Being Compensated")
    gaps_table.add_column("Gap", style="yellow")
    gaps_table.add_column("Impact", style="red")
    gaps_table.add_column("Compensation", style="green")
    
    gap_info = [
        ("Over-analysis", "High", "Time-boxed decisions, quick actions"),
        ("Low influence", "Medium", "Human-friendly summaries, benefits"),
        ("Perfectionism", "High", "80% threshold, pragmatic risk"),
        ("Technical communication", "Medium", "Simplified descriptions"),
        ("Risk aversion", "Medium", "Increased confidence scores"),
        ("Rigidity", "Medium", "Alternative approaches provided")
    ]
    
    for gap, impact, comp in gap_info:
        gaps_table.add_row(gap, impact, comp)
    
    console.print(gaps_table)


# Helper functions
def _display_metrics(metrics, engine):
    """Display system metrics"""
    health_state = engine.decision_engine._get_health_state(metrics.health_score)
    health_color = {
        "critical": "red",
        "degraded": "yellow",
        "healthy": "green",
        "optimal": "bright_green"
    }.get(health_state.value, "white")
    
    metrics_panel = Panel(
        f"Health: [{health_color}]{health_state.value.upper()}[/{health_color}] ({metrics.health_score:.2f})\n"
        f"Agents: {metrics.active_agents} | Queue: {metrics.work_queue_size} | "
        f"Completion: {metrics.completion_rate:.0%}",
        title="📊 System Metrics",
        border_style=health_color
    )
    console.print(metrics_panel)


def _display_compensated_decisions(decisions: list, show_compensation: bool):
    """Display decisions with compensation details"""
    table = Table(title="🤖 DISC-Compensated Decisions")
    table.add_column("Pri", style="red", width=3)
    table.add_column("Type", style="cyan")
    table.add_column("Human Summary", style="green")
    table.add_column("Risk", style="yellow")
    
    if show_compensation:
        table.add_column("Compensations", style="blue")
    
    for decision in decisions[:5]:  # Show top 5
        row = [
            str(decision.priority),
            decision.type.value,
            decision.human_friendly_summary if hasattr(decision, 'human_friendly_summary') else decision.description[:40] + "...",
            decision.risk_assessment if hasattr(decision, 'risk_assessment') else "Unknown"
        ]
        
        if show_compensation and hasattr(decision, 'compensation_applied'):
            row.append(", ".join(decision.compensation_applied[:3]))
        
        table.add_row(*row)
    
    console.print(table)
    
    # Show alternatives for first decision
    if decisions and hasattr(decisions[0], 'alternative_approaches') and decisions[0].alternative_approaches:
        console.print("\n💡 Alternatives for top decision:")
        for alt in decisions[0].alternative_approaches:
            console.print(f"  • {alt}")


if __name__ == "__main__":
    app()