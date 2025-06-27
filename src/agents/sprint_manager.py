"""
Sprint Manager - Git-native Sprint lifecycle management
======================================================

Manages sprints using annotated Git tags for perfect traceability.
Sprint state is immutable and distributed through Git.
"""

import sys
import json
import datetime
import subprocess
from typing import Optional, Dict, Any

try:
    from span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from utils.git_auto import git_wrap
except ImportError:
    def git_wrap(operation):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Direct implementation
                if operation == "tag_annotate":
                    name = kwargs.get('name')
                    message = kwargs.get('message')
                    cmd = ["git", "tag", "-a", name, "-m", message]
                    subprocess.run(cmd, check=True)
                return None
            return wrapper
        return decorator

try:
    from generated.python.scrum_sprint_cycle import scrum_sprint_cycle_span
except ImportError:
    pass


@git_wrap("tag_annotate")
def tag(name: str, message: str):
    """Create annotated Git tag for sprint events."""
    pass  # Handled by decorator


def get_current_sprint_id() -> str:
    """Generate sprint ID based on current week."""
    now = datetime.date.today()
    year, week, _ = now.isocalendar()
    return f"SPR-{year}-W{week:02d}"


def sprint_exists(sid: str) -> bool:
    """Check if a sprint has already been started."""
    try:
        subprocess.run(
            ["git", "rev-parse", f"sprint/{sid}/open"],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


@span("scrum_sprint_cycle")
def start_sprint(capacity_pts: int = 40, sprint_goal: str = "") -> str:
    """
    Start a new sprint with specified capacity.
    
    Args:
        capacity_pts: Total story points capacity for sprint
        sprint_goal: Optional sprint goal description
        
    Returns:
        Sprint ID
    """
    sid = get_current_sprint_id()
    
    # Check if sprint already exists
    if sprint_exists(sid):
        print(f"⚠️  Sprint {sid} already started")
        return sid
    
    # Create sprint metadata
    metadata = {
        "sprint_id": sid,
        "capacity": capacity_pts,
        "start_date": datetime.datetime.now().isoformat(),
        "goal": sprint_goal,
        "state": "started"
    }
    
    # Create annotated tag
    message = json.dumps(metadata, indent=2)
    tag(name=f"sprint/{sid}/open", message=message)
    
    print(f"🚀 Started sprint {sid} with capacity {capacity_pts} points")
    if sprint_goal:
        print(f"   Goal: {sprint_goal}")
    
    return sid


@span("scrum_sprint_cycle")
def close_sprint(sid: str, velocity: int, retrospective_notes: str = "") -> Dict[str, Any]:
    """
    Close an existing sprint and record velocity.
    
    Args:
        sid: Sprint ID to close
        velocity: Actual story points completed
        retrospective_notes: Optional retrospective summary
        
    Returns:
        Sprint summary
    """
    # Verify sprint was started
    if not sprint_exists(sid):
        raise ValueError(f"Sprint {sid} was never started")
    
    # Check if already closed
    try:
        subprocess.run(
            ["git", "rev-parse", f"sprint/{sid}/close"],
            check=True,
            capture_output=True
        )
        print(f"⚠️  Sprint {sid} already closed")
        return {"sprint_id": sid, "status": "already_closed"}
    except subprocess.CalledProcessError:
        pass  # Sprint not closed yet, proceed
    
    # Get sprint start metadata
    try:
        start_tag = subprocess.check_output(
            ["git", "tag", "-l", "-n100", f"sprint/{sid}/open"]
        ).decode()
        
        # Extract JSON from tag message
        json_start = start_tag.find('{')
        if json_start > 0:
            start_metadata = json.loads(start_tag[json_start:])
        else:
            start_metadata = {"capacity": 0}
    except:
        start_metadata = {"capacity": 0}
    
    # Calculate sprint metrics
    capacity = start_metadata.get("capacity", 0)
    performance = (velocity / capacity * 100) if capacity > 0 else 0
    
    # Create close metadata
    metadata = {
        "sprint_id": sid,
        "velocity": velocity,
        "capacity": capacity,
        "performance_pct": round(performance, 1),
        "close_date": datetime.datetime.now().isoformat(),
        "retrospective": retrospective_notes,
        "state": "completed"
    }
    
    # Create closing tag
    message = json.dumps(metadata, indent=2)
    tag(name=f"sprint/{sid}/close", message=message)
    
    print(f"🏁 Closed sprint {sid}")
    print(f"   Velocity: {velocity}/{capacity} points ({performance:.1f}%)")
    
    if performance < 80:
        print(f"   ⚠️  Under-delivered by {100-performance:.1f}%")
    elif performance > 120:
        print(f"   ⚠️  Over-delivered by {performance-100:.1f}% - check estimates")
    else:
        print(f"   ✅ On track!")
    
    return metadata


@span("scrum_sprint_cycle")
def sprint_status(sid: Optional[str] = None) -> Dict[str, Any]:
    """
    Get status of a sprint or current sprint.
    
    Args:
        sid: Sprint ID (defaults to current)
        
    Returns:
        Sprint status information
    """
    if not sid:
        sid = get_current_sprint_id()
    
    status = {
        "sprint_id": sid,
        "exists": sprint_exists(sid),
        "state": "not_started"
    }
    
    if not status["exists"]:
        return status
    
    # Check if closed
    try:
        subprocess.run(
            ["git", "rev-parse", f"sprint/{sid}/close"],
            check=True,
            capture_output=True
        )
        status["state"] = "completed"
        
        # Get close metadata
        close_tag = subprocess.check_output(
            ["git", "tag", "-l", "-n100", f"sprint/{sid}/close"]
        ).decode()
        json_start = close_tag.find('{')
        if json_start > 0:
            close_data = json.loads(close_tag[json_start:])
            status.update(close_data)
    except subprocess.CalledProcessError:
        status["state"] = "active"
        
        # Get open metadata
        try:
            open_tag = subprocess.check_output(
                ["git", "tag", "-l", "-n100", f"sprint/{sid}/open"]
            ).decode()
            json_start = open_tag.find('{')
            if json_start > 0:
                open_data = json.loads(open_tag[json_start:])
                status.update(open_data)
        except:
            pass
    
    return status


def list_sprints(limit: int = 10) -> list:
    """List recent sprints."""
    try:
        # Get all sprint tags
        tags = subprocess.check_output(
            ["git", "tag", "-l", "sprint/*/open", "--sort=-creatordate"]
        ).decode().strip().split('\n')
        
        sprints = []
        for tag in tags[:limit]:
            if tag:
                sid = tag.split('/')[1]
                status = sprint_status(sid)
                sprints.append(status)
        
        return sprints
    except:
        return []


def main():
    """CLI interface for sprint manager."""
    if len(sys.argv) < 2:
        print("Usage: sprint_manager.py <command> [args...]")
        print("Commands:")
        print("  open [capacity] [goal]     - Start new sprint")
        print("  close <sprint_id> <velocity> [notes]")
        print("  status [sprint_id]         - Show sprint status")
        print("  list                       - List recent sprints")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "open":
        capacity = int(sys.argv[2]) if len(sys.argv) > 2 else 40
        goal = sys.argv[3] if len(sys.argv) > 3 else ""
        sid = start_sprint(capacity, goal)
        print(f"Sprint ID: {sid}")
        
    elif command == "close":
        if len(sys.argv) < 4:
            print("Usage: sprint_manager.py close <sprint_id> <velocity> [notes]")
            sys.exit(1)
        
        sid = sys.argv[2]
        velocity = int(sys.argv[3])
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        
        close_sprint(sid, velocity, notes)
        
    elif command == "status":
        sid = sys.argv[2] if len(sys.argv) > 2 else None
        status = sprint_status(sid)
        
        print(f"\n📊 Sprint Status: {status['sprint_id']}")
        print(f"   State: {status['state']}")
        if status.get('capacity'):
            print(f"   Capacity: {status['capacity']} points")
        if status.get('velocity'):
            print(f"   Velocity: {status['velocity']} points")
            print(f"   Performance: {status['performance_pct']}%")
            
    elif command == "list":
        sprints = list_sprints()
        print(f"\n📅 Recent Sprints ({len(sprints)} total):")
        for sprint in sprints:
            state_icon = "🏁" if sprint['state'] == "completed" else "🚀"
            print(f"  {state_icon} {sprint['sprint_id']} - {sprint['state']}")
            if sprint.get('performance_pct'):
                print(f"     Performance: {sprint['performance_pct']}%")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()