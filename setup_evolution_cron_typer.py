#!/usr/bin/env python3
"""
Setup Autonomous Evolution Cron Job (Typer Version)
Pure Typer CLI without Rich console for PyInstaller compatibility
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional

import typer

# Create app with minimal configuration for PyInstaller compatibility
app = typer.Typer(
    name="setup-evolution-cron",
    help="Setup autonomous evolution cron job",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    rich_markup_mode=None
)

# Disable rich console completely
os.environ["TERM"] = "dumb"


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
    if not script_path.exists():
        print(f"❌ Evolution script not found: {script_path}")
        return False
    
    # Make script executable
    run_command(f"chmod +x {script_path}")
    
    # Create cron job entry
    cron_entry = f"*/10 * * * * {script_path} >> /tmp/evolution.log 2>&1"
    
    # Get current crontab
    current_cron = get_current_crontab()
    
    # Check if entry already exists
    if cron_entry in current_cron:
        print("✅ Evolution cron job already installed")
        return True
    
    # Add new entry
    new_cron = current_cron + f"\n{cron_entry}\n" if current_cron else f"{cron_entry}\n"
    
    # Install new crontab
    try:
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)
        
        if process.returncode == 0:
            print("✅ Evolution cron job installed successfully")
            return True
        else:
            print("❌ Failed to install cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error installing cron job: {e}")
        return False


@app.command()
def install(
    project_path: Optional[str] = typer.Argument(None, help="Path to dslmodel project (default: current directory)")
):
    """Install the autonomous evolution cron job"""
    
    # Determine project path
    if project_path is None:
        path = Path.cwd()
    else:
        path = Path(project_path).expanduser().resolve()
    
    if not path.exists():
        print(f"❌ Project path does not exist: {path}")
        raise typer.Exit(1)
    
    print(f"🔧 Installing evolution cron job from: {path}")
    
    # Check if cron service is running
    if not check_cron_service():
        print("⚠️  Warning: Cron service may not be running")
        response = typer.prompt("Continue anyway? (y/n)", default="n")
        if response.lower() != 'y':
            raise typer.Exit(1)
    
    # Install the cron job
    if install_cron_job(path):
        print("🎯 Evolution cron job installation complete!")
        print("   The system will evolve every 10 minutes")
        print("   Check logs at: /tmp/evolution.log")
    else:
        print("❌ Installation failed")
        raise typer.Exit(1)


@app.command()
def status():
    """Show evolution cron job status"""
    
    print("🔍 Evolution Cron Job Status:")
    
    # Check cron service
    cron_running = check_cron_service()
    print(f"   Cron Service: {'✅ Running' if cron_running else '❌ Not Running'}")
    
    # Check cron job
    current_cron = get_current_crontab()
    has_evolution_job = "evolution_cron.sh" in current_cron
    print(f"   Evolution Job: {'✅ Installed' if has_evolution_job else '❌ Not Installed'}")
    
    # Show log file status
    log_file = Path("/tmp/evolution.log")
    if log_file.exists():
        size = log_file.stat().st_size
        mtime = time.ctime(log_file.stat().st_mtime)
        print(f"   Log File: ✅ {size} bytes, modified {mtime}")
    else:
        print("   Log File: ❌ Not found")
    
    # Overall status
    if cron_running and has_evolution_job:
        print("🎯 Evolution system is active!")
    else:
        print("⚠️  Evolution system needs attention")


@app.command()
def uninstall():
    """Remove the evolution cron job"""
    
    print("🗑️  Removing evolution cron job...")
    
    current_cron = get_current_crontab()
    if "evolution_cron.sh" not in current_cron:
        print("✅ No evolution cron job found")
        return
    
    # Remove evolution entries
    lines = current_cron.split('\n')
    new_lines = [line for line in lines if "evolution_cron.sh" not in line]
    new_cron = '\n'.join(new_lines)
    
    # Install new crontab
    try:
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)
        
        if process.returncode == 0:
            print("✅ Evolution cron job removed successfully")
        else:
            print("❌ Failed to remove cron job")
            
    except Exception as e:
        print(f"❌ Error removing cron job: {e}")


@app.command()
def test():
    """Test the evolution script manually"""
    
    print("🧪 Testing evolution script...")
    
    # Find evolution script
    script_path = Path.cwd() / "evolution_cron.sh"
    if not script_path.exists():
        print(f"❌ Evolution script not found: {script_path}")
        raise typer.Exit(1)
    
    # Run the script
    print(f"▶️  Executing: {script_path}")
    
    try:
        result = run_command(str(script_path), check=False)
        
        print(f"Exit Code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        if result.returncode == 0:
            print("✅ Evolution script executed successfully")
        else:
            print("❌ Evolution script failed")
            
    except Exception as e:
        print(f"❌ Error running script: {e}")


@app.command()
def logs():
    """Show recent evolution logs"""
    
    log_file = Path("/tmp/evolution.log")
    if not log_file.exists():
        print("❌ Evolution log file not found")
        return
    
    print("📋 Recent Evolution Logs:")
    print("=" * 50)
    
    try:
        # Show last 20 lines
        result = run_command(f"tail -20 {log_file}")
        print(result.stdout)
    except Exception as e:
        print(f"❌ Error reading logs: {e}")


if __name__ == "__main__":
    app()