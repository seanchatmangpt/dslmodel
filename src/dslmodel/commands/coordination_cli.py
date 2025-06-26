"""Coordination CLI for managing swarm agents and work items."""

import typer
import json
import time
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, Type, Optional
from datetime import datetime
from enum import Enum

from dslmodel.agents.swarm import SwarmAgent


# Initialize CLI apps
app = typer.Typer(help="Agent coordination system")
work_app = typer.Typer(help="Work item management")
agent_app = typer.Typer(help="Run span-driven agents")

# Add sub-apps
app.add_typer(work_app, name="work")
app.add_typer(agent_app, name="agent")

# Configuration
ROOT = Path("~/s2s/agent_coordination").expanduser()
WORK_ITEMS = ROOT / "work_items.json"
SPAN_STREAM = ROOT / "telemetry_spans.jsonl"
AGENT_PACKAGE = "dslmodel.agents.examples"

# Work item types
class WorkType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    EPIC = "epic"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def log_span(name: str, attributes: Optional[Dict] = None):
    """Log a telemetry span to the JSONL stream."""
    ROOT.mkdir(parents=True, exist_ok=True)
    
    span = {
        "name": f"s2s.{name}",
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": attributes or {}
    }
    
    with SPAN_STREAM.open("a") as f:
        f.write(json.dumps(span) + "\n")


def load_work_items() -> Dict:
    """Load work items from JSON file."""
    if not WORK_ITEMS.exists():
        return {"items": {}, "next_id": 1}
    
    with WORK_ITEMS.open() as f:
        return json.load(f)


def save_work_items(data: Dict):
    """Save work items to JSON file."""
    ROOT.mkdir(parents=True, exist_ok=True)
    with WORK_ITEMS.open("w") as f:
        json.dump(data, f, indent=2)


# Work Commands
@work_app.command("claim")
def claim_work(
    work_type: WorkType,
    title: str,
    priority: Priority = Priority.MEDIUM,
    team: str = "default"
):
    """Claim a new work item."""
    data = load_work_items()
    work_id = f"WORK-{data['next_id']}"
    data["next_id"] += 1
    
    work_item = {
        "id": work_id,
        "type": work_type.value,
        "title": title,
        "priority": priority.value,
        "team": team,
        "status": "claimed",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data["items"][work_id] = work_item
    save_work_items(data)
    
    # Log span
    log_span("work.claim", {
        "work_id": work_id,
        "type": work_type.value,
        "priority": priority.value,
        "team": team
    })
    
    typer.echo(f"✅ Claimed {work_id}: {title}")
    return work_id


@work_app.command("list")
def list_work(
    team: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "table"
):
    """List work items with optional filters."""
    data = load_work_items()
    items = data.get("items", {}).values()
    
    # Filter items
    if team:
        items = [i for i in items if i.get("team") == team]
    if status:
        items = [i for i in items if i.get("status") == status]
    
    if format == "json":
        typer.echo(json.dumps(list(items), indent=2))
    else:
        if not items:
            typer.echo("No work items found.")
            return
        
        typer.echo("\nWork Items:")
        typer.echo("-" * 80)
        for item in items:
            typer.echo(
                f"{item['id']} | {item['type']:8} | {item['priority']:8} | "
                f"{item['status']:10} | {item['progress']:3}% | {item['title']}"
            )
    
    # Log span
    log_span("work.list", {"count": len(items), "team": team, "status": status})


@work_app.command("progress")
def update_progress(work_id: str, progress: int):
    """Update work item progress."""
    data = load_work_items()
    
    if work_id not in data["items"]:
        typer.echo(f"❌ Work item {work_id} not found.")
        raise typer.Exit(1)
    
    data["items"][work_id]["progress"] = min(100, max(0, progress))
    data["items"][work_id]["status"] = "in_progress"
    data["items"][work_id]["updated_at"] = datetime.now().isoformat()
    
    save_work_items(data)
    
    # Log span
    log_span("work.progress", {
        "work_id": work_id,
        "progress": progress
    })
    
    typer.echo(f"📊 Updated {work_id} progress to {progress}%")


@work_app.command("complete")
def complete_work(work_id: str, status: str = "success", score: int = 5):
    """Mark work item as complete."""
    data = load_work_items()
    
    if work_id not in data["items"]:
        typer.echo(f"❌ Work item {work_id} not found.")
        raise typer.Exit(1)
    
    data["items"][work_id]["status"] = "completed"
    data["items"][work_id]["progress"] = 100
    data["items"][work_id]["completion_status"] = status
    data["items"][work_id]["score"] = score
    data["items"][work_id]["completed_at"] = datetime.now().isoformat()
    data["items"][work_id]["updated_at"] = datetime.now().isoformat()
    
    save_work_items(data)
    
    # Log span
    log_span("work.complete", {
        "work_id": work_id,
        "status": status,
        "score": score
    })
    
    typer.echo(f"✅ Completed {work_id} with status: {status} (score: {score}/10)")


@work_app.command("stats")
def work_stats(team: Optional[str] = None):
    """Show work statistics."""
    data = load_work_items()
    items = list(data.get("items", {}).values())
    
    if team:
        items = [i for i in items if i.get("team") == team]
    
    total = len(items)
    completed = len([i for i in items if i.get("status") == "completed"])
    in_progress = len([i for i in items if i.get("status") == "in_progress"])
    claimed = len([i for i in items if i.get("status") == "claimed"])
    
    avg_score = 0
    if completed > 0:
        scores = [i.get("score", 5) for i in items if i.get("status") == "completed"]
        avg_score = sum(scores) / len(scores)
    
    typer.echo(f"\n📊 Work Statistics{f' for team {team}' if team else ''}:")
    typer.echo(f"   Total items: {total}")
    typer.echo(f"   Completed: {completed}")
    typer.echo(f"   In Progress: {in_progress}")
    typer.echo(f"   Claimed: {claimed}")
    if completed > 0:
        typer.echo(f"   Average Score: {avg_score:.1f}/10")
    
    # Log span
    log_span("work.stats", {
        "team": team,
        "total": total,
        "completed": completed
    })


# Agent Commands
def discover_agents() -> Dict[str, Type[SwarmAgent]]:
    """Discover all available agent classes."""
    agents: Dict[str, Type[SwarmAgent]] = {}
    
    try:
        pkg = importlib.import_module(AGENT_PACKAGE)
        
        for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
            if modname.startswith("_"):
                continue
                
            try:
                mod = importlib.import_module(f"{AGENT_PACKAGE}.{modname}")
                
                for name, cls in inspect.getmembers(mod, inspect.isclass):
                    if (issubclass(cls, SwarmAgent) and 
                        cls is not SwarmAgent and
                        hasattr(cls, "StateEnum") and 
                        hasattr(cls, "TRIGGER_MAP")):
                        
                        # Use module name without _agent suffix as key
                        key = modname.replace("_agent", "")
                        agents[key] = cls
                        
            except Exception as e:
                typer.echo(f"⚠️  Failed to load module {modname}: {e}")
                
    except Exception as e:
        typer.echo(f"⚠️  Failed to discover agents: {e}")
    
    return agents


# Cache discovered agents
_AGENT_REGISTRY = discover_agents()


@agent_app.command("list")
def list_agents():
    """List all available agents."""
    if not _AGENT_REGISTRY:
        typer.echo("No agents found. Make sure agent modules are in the correct location.")
        return
    
    typer.echo("\nAvailable Agents:")
    for name, cls in _AGENT_REGISTRY.items():
        typer.echo(f"  - {name}: {cls.__doc__.strip() if cls.__doc__ else 'No description'}")


@agent_app.command("run")
def run_agent(name: str):
    """Run a specific agent."""
    cls = _AGENT_REGISTRY.get(name)
    
    if not cls:
        typer.echo(f"❌ Unknown agent '{name}'. Available agents:")
        list_agents()
        raise typer.Exit(1)
    
    typer.echo(f"▶️  Running {name} agent (Ctrl+C to stop)...")
    
    try:
        # Initialize and run the agent
        agent = cls(
            root_dir=ROOT,
            cli_command=["python", __file__]  # Point back to this CLI
        )
        agent.run()
    except KeyboardInterrupt:
        typer.echo(f"\n⏹️  {name} agent stopped.")
    except Exception as e:
        typer.echo(f"❌ Agent error: {e}")
        raise typer.Exit(1)


@app.command("init")
def init_coordination():
    """Initialize the coordination environment."""
    ROOT.mkdir(parents=True, exist_ok=True)
    
    if not WORK_ITEMS.exists():
        save_work_items({"items": {}, "next_id": 1})
    
    if not SPAN_STREAM.exists():
        SPAN_STREAM.touch()
    
    typer.echo(f"✅ Initialized coordination environment at {ROOT}")


@app.command("reset")
def reset_coordination(
    confirm: bool = typer.Option(False, "--confirm", help="Confirm reset")
):
    """Reset the coordination environment."""
    if not confirm:
        typer.echo("⚠️  This will delete all work items and spans!")
        typer.echo("Use --confirm to proceed.")
        raise typer.Exit(1)
    
    if WORK_ITEMS.exists():
        WORK_ITEMS.unlink()
    
    if SPAN_STREAM.exists():
        SPAN_STREAM.unlink()
    
    init_coordination()
    typer.echo("♻️  Reset complete.")


if __name__ == "__main__":
    app()