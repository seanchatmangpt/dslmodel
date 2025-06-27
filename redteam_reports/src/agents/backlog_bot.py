"""
Backlog Bot - Git-native Scrum backlog management
=================================================

Manages backlog items as files in the backlog/ directory,
committed to Git with proper metadata and traceability.
"""

import sys
import json
import uuid
import pathlib
import datetime
import subprocess
from typing import Optional, Dict, Any

# Handle imports gracefully
try:
    from utils.task_utils import create_task
except ImportError:
    def create_task(agent: str, args: list, priority: int = 50):
        print(f"[TASK] Would create: {agent} with args {args} (priority: {priority})")

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
                # Fallback implementation
                return func(*args, **kwargs)
            return wrapper
        return decorator

try:
    from generated.python.scrum_backlog_item import scrum_backlog_item_span
except ImportError:
    pass


@git_wrap("notes_add")
def add_note(ref: str, target: str, message: str):
    """Add a Git note to track backlog updates."""
    cmd = ["git", "notes", f"--ref={ref}", "add", "-m", message, target]
    subprocess.run(cmd, check=True)


BACKLOG = pathlib.Path("backlog")
BACKLOG.mkdir(exist_ok=True)


@span("scrum_backlog_item")
def new_item(title: str, points: int, description: str = "", acceptance_criteria: Optional[list] = None) -> str:
    """
    Create a new backlog item as a Markdown file.
    
    Args:
        title: Story title
        points: Story points estimate
        description: Detailed description
        acceptance_criteria: List of acceptance criteria
        
    Returns:
        Backlog item ID
    """
    bi_id = f"BI-{uuid.uuid4().hex[:6]}"
    fname = BACKLOG / f"{bi_id}.md"
    
    # Create Markdown content
    content = f"# {title}\n\n"
    content += f"**ID:** {bi_id}\n"
    content += f"**Points:** {points}\n"
    content += f"**Created:** {datetime.datetime.now().isoformat()}\n"
    content += f"**Status:** Ready\n\n"
    
    if description:
        content += f"## Description\n\n{description}\n\n"
    
    if acceptance_criteria:
        content += "## Acceptance Criteria\n\n"
        for criterion in acceptance_criteria:
            content += f"- [ ] {criterion}\n"
        content += "\n"
    
    # Write file
    fname.write_text(content)
    
    # Git operations
    subprocess.run(["git", "add", str(fname)], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat(backlog): {bi_id} {title} [{points} pts]"],
        check=True
    )
    
    print(f"✅ Created backlog item: {bi_id}")
    return bi_id


@span("scrum_backlog_item")
def update_item(bi_id: str, status: Optional[str] = None, points: Optional[int] = None) -> Dict[str, Any]:
    """
    Update an existing backlog item.
    
    Args:
        bi_id: Backlog item ID
        status: New status (Ready, In Progress, Done, etc.)
        points: Updated story points
        
    Returns:
        Update summary
    """
    fname = BACKLOG / f"{bi_id}.md"
    
    if not fname.exists():
        raise ValueError(f"Backlog item {bi_id} not found")
    
    # Read current content
    content = fname.read_text()
    lines = content.split('\n')
    
    # Update fields
    updates = {}
    for i, line in enumerate(lines):
        if status and line.startswith("**Status:**"):
            lines[i] = f"**Status:** {status}"
            updates['status'] = status
        elif points and line.startswith("**Points:**"):
            lines[i] = f"**Points:** {points}"
            updates['points'] = points
    
    # Write updated content
    fname.write_text('\n'.join(lines))
    
    # Commit changes
    subprocess.run(["git", "add", str(fname)], check=True)
    update_msg = f"update(backlog): {bi_id}"
    if updates:
        update_msg += f" - {', '.join(f'{k}={v}' for k, v in updates.items())}"
    subprocess.run(["git", "commit", "-m", update_msg], check=True)
    
    # Add note for update tracking
    commit_hash = subprocess.check_output(
        ["git", "rev-parse", "HEAD"]
    ).decode().strip()
    
    note_data = json.dumps({
        "event": "updated",
        "timestamp": datetime.datetime.now().isoformat(),
        "updates": updates
    })
    
    try:
        add_note(ref="backlog", target=commit_hash, message=note_data)
    except:
        print(f"⚠️  Could not add Git note (might already exist)")
    
    print(f"✅ Updated {bi_id}: {updates}")
    return updates


@span("scrum_backlog_item")
def list_items(status_filter: Optional[str] = None) -> list:
    """
    List all backlog items.
    
    Args:
        status_filter: Optional status to filter by
        
    Returns:
        List of backlog items
    """
    items = []
    
    for fname in sorted(BACKLOG.glob("BI-*.md")):
        content = fname.read_text()
        
        # Parse basic fields
        item = {"id": fname.stem}
        
        for line in content.split('\n'):
            if line.startswith("**Points:**"):
                try:
                    points_str = line.split(':', 1)[1].strip()
                    # Remove any trailing asterisks
                    points_str = points_str.rstrip('*').strip()
                    item['points'] = int(points_str)
                except (ValueError, IndexError):
                    item['points'] = 0
            elif line.startswith("**Status:**"):
                item['status'] = line.split(':', 1)[1].strip()
            elif line.startswith("# "):
                item['title'] = line[2:].strip()
        
        # Apply filter if specified
        if status_filter and item.get('status') != status_filter:
            continue
            
        items.append(item)
    
    return items


def main():
    """CLI interface for backlog bot."""
    if len(sys.argv) < 2:
        print("Usage: backlog_bot.py <command> [args...]")
        print("Commands:")
        print("  new <title> <points> [description]")
        print("  update <id> <status|points> <value>")
        print("  list [status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "new":
        if len(sys.argv) < 4:
            print("Usage: backlog_bot.py new <title> <points> [description]")
            sys.exit(1)
        
        title = sys.argv[2]
        points = int(sys.argv[3])
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        
        bi_id = new_item(title, points, description)
        print(f"Created: {bi_id}")
        
    elif command == "update":
        if len(sys.argv) < 5:
            print("Usage: backlog_bot.py update <id> <field> <value>")
            sys.exit(1)
        
        bi_id = sys.argv[2]
        field = sys.argv[3]
        value = sys.argv[4]
        
        if field == "status":
            update_item(bi_id, status=value)
        elif field == "points":
            update_item(bi_id, points=int(value))
        else:
            print(f"Unknown field: {field}")
            
    elif command == "list":
        status_filter = sys.argv[2] if len(sys.argv) > 2 else None
        items = list_items(status_filter)
        
        print(f"\n📋 Backlog Items ({len(items)} total):")
        for item in items:
            print(f"  {item['id']}: {item['title']} [{item['points']} pts] - {item['status']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()