#!/usr/bin/env python3
"""
Agent Coordination CLI v2.0 - Python/Typer Implementation
80/20 Principle: Core 20% features that provide 80% value

Core Features:
- Atomic work claiming with nanosecond IDs
- Work progress tracking
- Work completion with velocity tracking
- Fast-path optimizations
- Basic dashboard view
"""

import json
import time
import fcntl
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer(help="Agent Coordination CLI - 80/20 Implementation")
console = Console()

# Configuration
COORDINATION_DIR = Path(os.environ.get("COORDINATION_DIR", "/Users/sac/dev/ai-self-sustaining-system/agent_coordination"))
WORK_CLAIMS_FILE = COORDINATION_DIR / "work_claims.json"
AGENT_STATUS_FILE = COORDINATION_DIR / "agent_status.json"
COORDINATION_LOG_FILE = COORDINATION_DIR / "coordination_log.json"
FAST_CLAIMS_FILE = COORDINATION_DIR / "work_claims_fast.jsonl"

# Enums
class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class WorkStatus(str, Enum):
    active = "active"
    in_progress = "in_progress"
    completed = "completed"

# Utility functions
def generate_agent_id() -> str:
    """Generate unique nanosecond-based agent ID"""
    return f"agent_{int(time.time() * 1e9)}"

def generate_work_id() -> str:
    """Generate unique nanosecond-based work ID"""
    return f"work_{int(time.time() * 1e9)}"

def ensure_coordination_dir():
    """Ensure coordination directory exists"""
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)

def atomic_json_update(filepath: Path, update_func):
    """Atomically update a JSON file with locking"""
    lock_file = filepath.with_suffix('.json.lock')
    
    # Try to acquire lock
    try:
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        console.print("⚠️  Another process is updating, please retry", style="yellow")
        return False
    
    try:
        # Initialize file if doesn't exist
        if not filepath.exists():
            filepath.write_text("[]")
        
        # Read current data
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Apply update
        new_data = update_func(data)
        
        # Write atomically
        temp_file = filepath.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(new_data, f, indent=2)
        
        # Atomic move
        temp_file.replace(filepath)
        return True
        
    finally:
        os.close(lock_fd)
        lock_file.unlink()

# Core Commands
@app.command()
def claim(
    work_type: str = typer.Argument(..., help="Type of work (e.g., feature, bug, task)"),
    description: str = typer.Argument(..., help="Work description"),
    priority: Priority = typer.Option(Priority.medium, help="Work priority"),
    team: str = typer.Option("autonomous_team", help="Team assignment"),
    fast: bool = typer.Option(True, help="Use fast-path optimization")
):
    """Claim work atomically with nanosecond-precision ID"""
    ensure_coordination_dir()
    
    agent_id = os.environ.get("AGENT_ID", generate_agent_id())
    work_id = generate_work_id()
    
    console.print(f"🤖 Agent {agent_id} claiming work: {work_id}")
    
    if fast:
        # Fast-path: Append to JSONL file
        claim_entry = {
            "work_item_id": work_id,
            "agent_id": agent_id,
            "claimed_at": datetime.now().isoformat() + "Z",
            "work_type": work_type,
            "description": description,
            "priority": priority.value,
            "status": WorkStatus.active.value,
            "team": team
        }
        
        # Simple append operation
        with open(FAST_CLAIMS_FILE, 'a') as f:
            f.write(json.dumps(claim_entry) + '\n')
        
        console.print(f"✅ [green]SUCCESS[/green]: Fast-path claimed {work_id}")
        console.print(f"   Type: {work_type}, Priority: {priority.value}, Team: {team}")
        
        # Set environment for subsequent commands
        os.environ["CURRENT_WORK_ITEM"] = work_id
        os.environ["AGENT_ID"] = agent_id
        
    else:
        # Regular path with full JSON
        claim_data = {
            "work_item_id": work_id,
            "agent_id": agent_id,
            "claimed_at": datetime.now().isoformat() + "Z",
            "work_type": work_type,
            "description": description,
            "priority": priority.value,
            "status": WorkStatus.active.value,
            "team": team,
            "progress": 0
        }
        
        def add_claim(data):
            data.append(claim_data)
            return data
        
        if atomic_json_update(WORK_CLAIMS_FILE, add_claim):
            console.print(f"✅ [green]SUCCESS[/green]: Claimed {work_id}")
            os.environ["CURRENT_WORK_ITEM"] = work_id
            os.environ["AGENT_ID"] = agent_id

@app.command()
def progress(
    work_id: Optional[str] = typer.Argument(None, help="Work item ID"),
    percent: int = typer.Argument(..., help="Progress percentage (0-100)"),
    status: WorkStatus = typer.Option(WorkStatus.in_progress, help="Work status")
):
    """Update work progress"""
    work_id = work_id or os.environ.get("CURRENT_WORK_ITEM")
    if not work_id:
        console.print("❌ No work item ID specified", style="red")
        raise typer.Exit(1)
    
    def update_progress(data):
        updated = False
        for item in data:
            if item.get("work_item_id") == work_id:
                item["progress"] = percent
                item["status"] = status.value
                item["last_update"] = datetime.now().isoformat() + "Z"
                updated = True
        return data
    
    if atomic_json_update(WORK_CLAIMS_FILE, update_progress):
        console.print(f"📈 Updated {work_id} to {percent}% ({status.value})")

@app.command()
def complete(
    work_id: Optional[str] = typer.Argument(None, help="Work item ID"),
    result: str = typer.Option("success", help="Completion result"),
    velocity: int = typer.Option(5, help="Velocity points")
):
    """Complete work and update velocity"""
    work_id = work_id or os.environ.get("CURRENT_WORK_ITEM")
    if not work_id:
        console.print("❌ No work item ID specified", style="red")
        raise typer.Exit(1)
    
    completion_time = datetime.now().isoformat() + "Z"
    
    # Update work claims
    def mark_complete(data):
        for item in data:
            if item.get("work_item_id") == work_id:
                item["status"] = WorkStatus.completed.value
                item["completed_at"] = completion_time
                item["result"] = result
                item["velocity_points"] = velocity
        return data
    
    # Log completion
    def log_completion(data):
        data.append({
            "work_item_id": work_id,
            "completed_at": completion_time,
            "agent_id": os.environ.get("AGENT_ID", "unknown"),
            "result": result,
            "velocity_points": velocity
        })
        return data
    
    if atomic_json_update(WORK_CLAIMS_FILE, mark_complete):
        atomic_json_update(COORDINATION_LOG_FILE, log_completion)
        console.print(f"✅ Completed {work_id} ({result}) - {velocity} points")
        if "CURRENT_WORK_ITEM" in os.environ:
            del os.environ["CURRENT_WORK_ITEM"]

@app.command()
def dashboard(fast: bool = typer.Option(True, help="Use fast-path dashboard")):
    """Show coordination dashboard"""
    console.print("🚀 [bold]COORDINATION DASHBOARD[/bold]")
    console.print("=" * 50)
    
    if fast and FAST_CLAIMS_FILE.exists():
        # Fast-path: Count lines in JSONL
        with open(FAST_CLAIMS_FILE, 'r') as f:
            fast_items = [json.loads(line) for line in f if line.strip()]
        
        active_fast = [item for item in fast_items if item.get("status") == "active"]
        
        console.print(f"\n⚡ Fast-path active items: {len(active_fast)}")
        
        # Show recent items
        if active_fast:
            table = Table(title="Recent Active Work (Fast-Path)")
            table.add_column("Work ID", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Priority", style="yellow")
            table.add_column("Team", style="blue")
            
            for item in active_fast[-5:]:  # Last 5 items
                table.add_row(
                    item["work_item_id"],
                    item["work_type"],
                    item["priority"],
                    item["team"]
                )
            
            console.print(table)
    
    # Regular dashboard
    if WORK_CLAIMS_FILE.exists():
        with open(WORK_CLAIMS_FILE, 'r') as f:
            claims = json.load(f)
        
        active_items = [c for c in claims if c.get("status") != "completed"]
        completed_items = [c for c in claims if c.get("status") == "completed"]
        
        console.print(f"\n📊 Work Summary:")
        console.print(f"   Active: {len(active_items)}")
        console.print(f"   Completed: {len(completed_items)}")
        
        # Calculate velocity
        if COORDINATION_LOG_FILE.exists():
            with open(COORDINATION_LOG_FILE, 'r') as f:
                log_data = json.load(f)
            total_velocity = sum(item.get("velocity_points", 0) for item in log_data)
            console.print(f"   Total Velocity: {total_velocity} points")

@app.command()
def list_work(
    team: Optional[str] = typer.Option(None, help="Filter by team"),
    status: Optional[WorkStatus] = typer.Option(None, help="Filter by status")
):
    """List work items with filters"""
    if not WORK_CLAIMS_FILE.exists():
        console.print("No work items found")
        return
    
    with open(WORK_CLAIMS_FILE, 'r') as f:
        claims = json.load(f)
    
    # Apply filters
    filtered = claims
    if team:
        filtered = [c for c in filtered if c.get("team") == team]
    if status:
        filtered = [c for c in filtered if c.get("status") == status.value]
    
    if not filtered:
        console.print("No matching work items")
        return
    
    # Display table
    table = Table(title="Work Items")
    table.add_column("ID", style="cyan", width=20)
    table.add_column("Type", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Status", style="blue")
    table.add_column("Progress", style="magenta")
    table.add_column("Agent", style="white")
    
    for item in filtered:
        table.add_row(
            item["work_item_id"][:20] + "...",
            item["work_type"],
            item["priority"],
            item["status"],
            f"{item.get('progress', 0)}%",
            item["agent_id"][:15] + "..."
        )
    
    console.print(table)

@app.command()
def optimize():
    """Archive completed work for performance (80/20 optimization)"""
    if not WORK_CLAIMS_FILE.exists():
        console.print("No work claims to optimize")
        return
    
    with open(WORK_CLAIMS_FILE, 'r') as f:
        claims = json.load(f)
    
    completed = [c for c in claims if c.get("status") == "completed"]
    active = [c for c in claims if c.get("status") != "completed"]
    
    if not completed:
        console.print("No completed items to archive")
        return
    
    # Archive completed items
    archive_dir = COORDINATION_DIR / "archived_claims"
    archive_dir.mkdir(exist_ok=True)
    
    archive_file = archive_dir / f"completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(archive_file, 'w') as f:
        json.dump(completed, f, indent=2)
    
    # Keep only active items
    with open(WORK_CLAIMS_FILE, 'w') as f:
        json.dump(active, f, indent=2)
    
    console.print(f"✅ Archived {len(completed)} completed items")
    console.print(f"   Archive: {archive_file}")
    console.print(f"   Active items: {len(active)}")

if __name__ == "__main__":
    app()