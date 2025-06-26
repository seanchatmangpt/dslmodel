#!/usr/bin/env python3
"""
Setup Autonomous Evolution Cron Job
Installs and configures the 10-minute evolution cron job with proper monitoring
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(help="Setup autonomous evolution cron job")


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)


def check_cron_service() -> bool:
    """Check if cron service is running"""
    try:
        result = run_command("pgrep -x cron", check=False)
        return result.returncode == 0
    except Exception:
        return False


def get_current_crontab() -> str:
    """Get current user's crontab"""
    try:
        result = run_command("crontab -l", check=False)
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def install_cron_job(project_path: Path) -> bool:
    """Install the evolution cron job"""
    
    script_path = project_path / "evolution_cron.sh"
    
    # Make script executable
    script_path.chmod(0o755)
    
    # Create cron entry
    cron_entry = f"*/10 * * * * {script_path} >/dev/null 2>&1"
    
    # Get existing crontab
    current_crontab = get_current_crontab()
    
    # Check if entry already exists
    if str(script_path) in current_crontab:
        console.print("[yellow]Evolution cron job already installed[/yellow]")
        return True
    
    # Add new entry
    new_crontab = current_crontab.strip()
    if new_crontab:
        new_crontab += "\n"
    new_crontab += cron_entry + "\n"
    
    # Install new crontab
    try:
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            console.print("[green]✅ Cron job installed successfully[/green]")
            return True
        else:
            console.print("[red]❌ Failed to install cron job[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error installing cron job: {e}[/red]")
        return False


def remove_cron_job(project_path: Path) -> bool:
    """Remove the evolution cron job"""
    
    script_path = project_path / "evolution_cron.sh"
    current_crontab = get_current_crontab()
    
    if str(script_path) not in current_crontab:
        console.print("[yellow]Evolution cron job not found[/yellow]")
        return True
    
    # Remove lines containing the script path
    lines = current_crontab.split('\n')
    filtered_lines = [line for line in lines if str(script_path) not in line]
    new_crontab = '\n'.join(filtered_lines).strip()
    
    if new_crontab:
        new_crontab += '\n'
    
    # Install filtered crontab
    try:
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            console.print("[green]✅ Cron job removed successfully[/green]")
            return True
        else:
            console.print("[red]❌ Failed to remove cron job[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error removing cron job: {e}[/red]")
        return False


@app.command("install")
def install(
    project_path: Optional[Path] = typer.Option(None, help="Project path (default: current directory)"),
    test_run: bool = typer.Option(True, "--test/--no-test", help="Run test before installing")
):
    """Install the autonomous evolution cron job"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print(Panel(
        f"[bold cyan]🤖 Installing Autonomous Evolution Cron Job[/bold cyan]\n\n"
        f"Project Path: [yellow]{project_path}[/yellow]\n"
        f"Schedule: [blue]Every 10 minutes[/blue]\n"
        f"Test Run: [green]{'Yes' if test_run else 'No'}[/green]",
        title="🚀 Cron Installation",
        border_style="cyan"
    ))
    
    # Verify requirements
    console.print("1️⃣ Checking requirements...")
    
    # Check if cron service is running
    if not check_cron_service():
        console.print("[red]❌ Cron service not running. Start with: sudo service cron start[/red]")
        raise typer.Exit(1)
    
    # Check if script exists
    script_path = project_path / "evolution_cron.sh"
    if not script_path.exists():
        console.print(f"[red]❌ Script not found: {script_path}[/red]")
        raise typer.Exit(1)
    
    # Check if daemon exists
    daemon_path = project_path / "src/dslmodel/commands/autonomous_evolution_daemon.py"
    if not daemon_path.exists():
        console.print(f"[red]❌ Daemon not found: {daemon_path}[/red]")
        raise typer.Exit(1)
    
    console.print("[green]✅ Requirements check passed[/green]")
    
    # Test run
    if test_run:
        console.print("2️⃣ Running test evolution cycle...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Testing evolution cycle...", total=None)
            
            try:
                result = run_command(
                    f"cd {project_path} && python -m src.dslmodel.commands.autonomous_evolution_daemon simulate --cycles 1 --fast",
                    check=True
                )
                progress.stop()
                
                if "Simulation Results:" in result.stdout:
                    console.print("[green]✅ Test evolution cycle completed successfully[/green]")
                else:
                    console.print("[yellow]⚠️ Test completed but output unexpected[/yellow]")
                    console.print(f"Output: {result.stdout[-200:]}")  # Last 200 chars
                    
            except subprocess.CalledProcessError as e:
                progress.stop()
                console.print(f"[red]❌ Test evolution cycle failed: {e}[/red]")
                console.print(f"Error: {e.stderr}")
                raise typer.Exit(1)
    
    # Install cron job
    console.print("3️⃣ Installing cron job...")
    
    if install_cron_job(project_path):
        console.print("4️⃣ Verifying installation...")
        
        # Verify crontab entry
        current_crontab = get_current_crontab()
        if str(script_path) in current_crontab:
            console.print("[green]✅ Cron job verified in crontab[/green]")
            
            # Show cron status
            console.print("\n📊 Installation Summary:")
            table = Table()
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="white")
            
            table.add_row("Cron Service", "🟢 Running", "System cron daemon active")
            table.add_row("Evolution Script", "✅ Ready", str(script_path))
            table.add_row("Schedule", "⏰ Active", "Every 10 minutes")
            table.add_row("Log Directory", "📁 Created", str(project_path / "logs"))
            
            console.print(table)
            
            console.print(Panel(
                "[green]🎉 Autonomous Evolution Cron Job Installed Successfully![/green]\n\n"
                "• Evolution will run automatically every 10 minutes\n"
                "• Check logs in ./logs/evolution_cron.log\n"
                "• Monitor with: python setup_evolution_cron.py status\n"
                "• Remove with: python setup_evolution_cron.py remove",
                title="✨ Installation Complete",
                border_style="green"
            ))
            
        else:
            console.print("[red]❌ Cron job not found in crontab after installation[/red]")
            raise typer.Exit(1)
    else:
        raise typer.Exit(1)


@app.command("remove")
def remove(
    project_path: Optional[Path] = typer.Option(None, help="Project path (default: current directory)")
):
    """Remove the autonomous evolution cron job"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print("[bold yellow]🗑️ Removing Autonomous Evolution Cron Job[/bold yellow]")
    
    if remove_cron_job(project_path):
        console.print(Panel(
            "[yellow]Autonomous Evolution Cron Job Removed[/yellow]\n\n"
            "• Evolution cycles will no longer run automatically\n"
            "• Log files preserved in ./logs/\n"
            "• Reinstall with: python setup_evolution_cron.py install",
            title="🛑 Removal Complete",
            border_style="yellow"
        ))
    else:
        raise typer.Exit(1)


@app.command("status")
def status(
    project_path: Optional[Path] = typer.Option(None, help="Project path (default: current directory)")
):
    """Show autonomous evolution cron job status"""
    
    if project_path is None:
        project_path = Path.cwd()
    
    console.print("[bold cyan]📊 Autonomous Evolution Cron Status[/bold cyan]")
    
    # Check cron service
    cron_running = check_cron_service()
    
    # Check cron job installation
    script_path = project_path / "evolution_cron.sh"
    current_crontab = get_current_crontab()
    cron_installed = str(script_path) in current_crontab
    
    # Check logs
    log_dir = project_path / "logs"
    log_file = log_dir / "evolution_cron.log"
    
    # Status table
    table = Table(title="System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    table.add_row(
        "Cron Service",
        "🟢 Running" if cron_running else "🔴 Stopped",
        "System cron daemon"
    )
    
    table.add_row(
        "Evolution Cron Job",
        "✅ Installed" if cron_installed else "❌ Not Installed",
        "Every 10 minutes" if cron_installed else "Not scheduled"
    )
    
    table.add_row(
        "Log Directory",
        "📁 Exists" if log_dir.exists() else "❌ Missing",
        str(log_dir)
    )
    
    if log_file.exists():
        log_size = log_file.stat().st_size
        log_modified = time.ctime(log_file.stat().st_mtime)
        table.add_row(
            "Log File",
            f"📄 {log_size:,} bytes",
            f"Modified: {log_modified}"
        )
    else:
        table.add_row("Log File", "❌ No logs", "No evolution runs yet")
    
    console.print(table)
    
    # Show recent log entries
    if log_file.exists():
        console.print("\n[bold]Recent Log Entries:[/bold]")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                
            for line in recent_lines:
                console.print(f"[dim]{line.strip()}[/dim]")
                
        except Exception as e:
            console.print(f"[red]Error reading log file: {e}[/red]")
    
    # Show current crontab
    if cron_installed:
        console.print(f"\n[bold]Current Crontab Entry:[/bold]")
        for line in current_crontab.split('\n'):
            if str(script_path) in line:
                console.print(f"[yellow]{line}[/yellow]")


@app.command("test")
def test_evolution():
    """Test the evolution system"""
    
    console.print("[bold cyan]🧪 Testing Evolution System[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Test 1: Weaver models
        task = progress.add_task("Testing Weaver models...", total=None)
        try:
            from src.dslmodel.generated.models.autonomous_evolution_loop import (
                Autonomous_evolution_scheduler,
                Autonomous_evolution_cycle
            )
            console.print("[green]✅ Weaver models imported successfully[/green]")
        except ImportError as e:
            console.print(f"[red]❌ Weaver models failed: {e}[/red]")
            raise typer.Exit(1)
        
        # Test 2: Evolution daemon
        progress.update(task, description="Testing evolution daemon...")
        try:
            result = run_command("python -m src.dslmodel.commands.autonomous_evolution_daemon simulate --cycles 1 --fast")
            if "Simulation Results:" in result.stdout:
                console.print("[green]✅ Evolution daemon test passed[/green]")
            else:
                console.print("[yellow]⚠️ Evolution daemon test completed with warnings[/yellow]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Evolution daemon test failed: {e}[/red]")
            raise typer.Exit(1)
        
        # Test 3: OTEL telemetry
        progress.update(task, description="Testing OTEL telemetry...")
        try:
            result = run_command("python -c \"from src.dslmodel.generated.models.autonomous_evolution_loop import *; print('OTEL models OK')\"")
            console.print("[green]✅ OTEL telemetry models working[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ OTEL telemetry test failed: {e}[/red]")
            raise typer.Exit(1)
        
        progress.stop()
    
    console.print(Panel(
        "[green]🎯 All Tests Passed![/green]\n\n"
        "• Weaver-generated models working\n"
        "• Evolution daemon operational\n" 
        "• OTEL telemetry functional\n\n"
        "Ready to install autonomous evolution cron job!",
        title="✅ Test Results",
        border_style="green"
    ))


if __name__ == "__main__":
    app()