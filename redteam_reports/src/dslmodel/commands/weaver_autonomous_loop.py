#!/usr/bin/env python3
"""
Weaver Autonomous Loop CLI
=========================

CLI interface for the autonomous feature completion loop.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

from ..autonomous_loop.weaver_worktree_loop import WeaverWorktreeLoop, cron_cycle

app = typer.Typer(help="Weaver-driven autonomous feature completion loop")
console = Console()


@app.command("run")
def run_loop(
    cycles: Optional[int] = typer.Option(
        None,
        "--cycles", "-n",
        help="Number of cycles to run (default: infinite)"
    ),
    interval: int = typer.Option(
        600,
        "--interval", "-i", 
        help="Seconds between cycles (default: 600 = 10 minutes)"
    ),
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    )
):
    """Run the autonomous loop manually"""
    console.print("🚀 Starting Weaver Autonomous Loop")
    console.print("=" * 40)
    
    loop = WeaverWorktreeLoop(repo_path)
    
    # Override interval if provided
    if interval != 600:
        console.print(f"⏰ Using custom interval: {interval}s")
    
    asyncio.run(loop.run_continuous(cycles))


@app.command("cycle")
def run_single_cycle(
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Verbose output"
    )
):
    """Run a single cycle (used by cron)"""
    console.print("🔄 Running Single Autonomous Cycle")
    
    loop = WeaverWorktreeLoop(repo_path)
    
    async def run():
        return await loop.run_cycle()
    
    result = asyncio.run(run())
    
    if verbose:
        console.print_json(json.dumps(result, indent=2, default=str))
    
    # Exit code indicates success/failure
    if result.get("errors"):
        raise typer.Exit(1)


@app.command("status")
def show_status(
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    )
):
    """Show current loop status and metrics"""
    console.print("📊 Weaver Loop Status")
    console.print("=" * 25)
    
    loop = WeaverWorktreeLoop(repo_path)
    
    # Get current state
    worktrees = loop.worktree_manager.list_worktrees()
    
    # Feature discovery
    async def get_features():
        return await loop.discover_features()
    
    features = asyncio.run(get_features())
    
    # System status table
    status_table = Table(title="📊 Current Status")
    status_table.add_column("Metric", style="cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Active Worktrees", str(len(worktrees)))
    status_table.add_row("Features Discovered", str(len(features)))
    status_table.add_row("Features in Progress", str(len([f for f in features if f.completion_percentage > 0 and f.completion_percentage < 100])))
    status_table.add_row("80/20 Candidates", str(len([f for f in features if f.is_8020_candidate])))
    
    console.print(status_table)
    
    # Feature details
    if features:
        features_table = Table(title="🎯 Top Features")
        features_table.add_column("Name", style="cyan")
        features_table.add_column("Priority", style="red")
        features_table.add_column("Effort", style="yellow")
        features_table.add_column("Completion", style="green")
        features_table.add_column("80/20", style="blue")
        
        for feature in features[:10]:  # Top 10
            features_table.add_row(
                feature.name[:30] + "..." if len(feature.name) > 30 else feature.name,
                str(feature.priority),
                feature.estimated_effort,
                f"{feature.completion_percentage:.0f}%",
                "✅" if feature.is_8020_candidate else "❌"
            )
        
        console.print(features_table)
    
    # Worktree details
    if worktrees:
        worktree_table = Table(title="🌳 Active Worktrees")
        worktree_table.add_column("Name", style="cyan")
        worktree_table.add_column("Branch", style="yellow")
        worktree_table.add_column("Path", style="white")
        
        for worktree in worktrees:
            worktree_table.add_row(
                worktree.name,
                worktree.branch,
                str(worktree.path)[-50:]  # Last 50 chars
            )
        
        console.print(worktree_table)


@app.command("setup-cron")
def setup_cron(
    interval: int = typer.Option(
        10,
        "--interval", "-i",
        help="Minutes between runs"
    ),
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    ),
    python_path: str = typer.Option(
        "/usr/bin/python3",
        "--python",
        help="Python interpreter path"
    )
):
    """Setup cron job for autonomous loop"""
    console.print("⏰ Setting up Cron Job")
    console.print("=" * 25)
    
    # Create cron entry
    cron_command = f"*/{interval} * * * * {python_path} -m dslmodel.cli weaver-loop cycle --repo {repo_path}"
    
    # Show what would be added
    console.print(Panel(
        f"Cron Entry:\n{cron_command}\n\n"
        f"This will run every {interval} minutes",
        title="📅 Cron Configuration",
        border_style="yellow"
    ))
    
    # Create wrapper script for better logging
    script_path = Path.home() / "bin" / "dslmodel-autonomous-loop.sh"
    script_path.parent.mkdir(exist_ok=True)
    
    script_content = f'''#!/bin/bash
# DSLModel Autonomous Loop - Generated by dslmodel setup-cron
export PYTHONPATH="{repo_path}/src:$PYTHONPATH"
cd "{repo_path}"

# Log to file with timestamp
echo "$(date): Starting autonomous cycle" >> /tmp/dslmodel-loop.log

# Run cycle and log results
{python_path} -m dslmodel.cli weaver-loop cycle --repo {repo_path} >> /tmp/dslmodel-loop.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "$(date): Cycle completed successfully" >> /tmp/dslmodel-loop.log
else
    echo "$(date): Cycle failed" >> /tmp/dslmodel-loop.log
fi
'''
    
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    console.print(f"✅ Created wrapper script: {script_path}")
    
    # Updated cron command using wrapper
    cron_command = f"*/{interval} * * * * {script_path}"
    
    console.print("\n📋 To enable cron:")
    console.print(f"1. Run: crontab -e")
    console.print(f"2. Add line: {cron_command}")
    console.print(f"3. Save and exit")
    console.print(f"\n📝 Logs will be written to: /tmp/dslmodel-loop.log")
    
    # Offer to install automatically
    if typer.confirm("Install cron job automatically?"):
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
            
            # Check if already exists
            if "dslmodel-autonomous-loop" in current_cron:
                console.print("⚠️ Cron job already exists")
                return
            
            # Add new entry
            new_cron = current_cron + f"\n{cron_command}\n"
            
            # Install
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)
            
            if process.returncode == 0:
                console.print("✅ Cron job installed successfully!")
            else:
                console.print("❌ Failed to install cron job")
                
        except Exception as e:
            console.print(f"❌ Error installing cron job: {e}")


@app.command("features")
def list_features(
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    ),
    show_completed: bool = typer.Option(
        False,
        "--completed", "-c",
        help="Show completed features"
    )
):
    """List discoverable features"""
    console.print("🎯 Feature Discovery")
    console.print("=" * 20)
    
    loop = WeaverWorktreeLoop(repo_path)
    
    async def discover():
        return await loop.discover_features()
    
    features = asyncio.run(discover())
    
    if not features:
        console.print("📭 No features discovered")
        return
    
    # Filter by completion status
    if not show_completed:
        features = [f for f in features if f.completion_percentage < 100]
    
    table = Table(title="🎯 Discovered Features")
    table.add_column("Name", style="cyan")
    table.add_column("Priority", style="red", justify="center")
    table.add_column("Effort", style="yellow", justify="center")
    table.add_column("Completion", style="green", justify="center")
    table.add_column("80/20", style="blue", justify="center")
    table.add_column("Path", style="white")
    
    for feature in features:
        completion_color = "green" if feature.completion_percentage >= 80 else "yellow" if feature.completion_percentage >= 50 else "red"
        
        table.add_row(
            feature.name,
            str(feature.priority),
            feature.estimated_effort,
            f"[{completion_color}]{feature.completion_percentage:.0f}%[/{completion_color}]",
            "✅" if feature.is_8020_candidate else "❌",
            str(feature.worktree_path) if feature.worktree_path else "Not created"
        )
    
    console.print(table)
    
    # Summary
    console.print(f"\n📊 Summary:")
    console.print(f"  • Total features: {len(features)}")
    console.print(f"  • 80/20 candidates: {len([f for f in features if f.is_8020_candidate])}")
    console.print(f"  • In progress: {len([f for f in features if 0 < f.completion_percentage < 100])}")
    console.print(f"  • Ready to complete: {len([f for f in features if 50 <= f.completion_percentage < 100])}")


@app.command("test-cycle")
def test_cycle(
    repo_path: Path = typer.Option(
        Path("/Users/sac/dev/dslmodel"),
        "--repo", "-r",
        help="Repository path"
    )
):
    """Test a cycle with dry-run mode"""
    console.print("🧪 Testing Autonomous Cycle")
    console.print("=" * 30)
    
    # Create a test loop instance
    loop = WeaverWorktreeLoop(repo_path)
    
    with Live(console=console, refresh_per_second=2) as live:
        async def test():
            # Test feature discovery
            live.update("🔍 Testing feature discovery...")
            features = await loop.discover_features()
            
            live.update(f"📋 Found {len(features)} features")
            await asyncio.sleep(1)
            
            # Test feature selection
            if features:
                live.update("🎯 Testing feature selection...")
                selected = await loop.select_feature_8020(features)
                
                if selected:
                    live.update(f"✅ Selected: {selected.name}")
                    
                    # Test worktree setup (without actually creating)
                    live.update("🌳 Testing worktree setup...")
                    await asyncio.sleep(1)
                    
                    live.update("✅ Test completed successfully!")
                else:
                    live.update("⚠️ No feature selected")
            else:
                live.update("📭 No features to test with")
        
        asyncio.run(test())
    
    console.print(Panel(
        "Test completed! The system appears ready for autonomous operation.",
        title="🧪 Test Results",
        border_style="green"
    ))


if __name__ == "__main__":
    app()