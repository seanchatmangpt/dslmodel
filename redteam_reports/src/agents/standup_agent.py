"""
Standup Agent - Git-native daily standup tracking
=================================================

Records daily standup entries as Git notes on sprint tags,
enabling distributed async standups with full history.
"""

import sys
import os
import datetime
import subprocess
import json
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
                if operation == "notes_add":
                    ref = kwargs.get('ref')
                    target = kwargs.get('target')
                    message = kwargs.get('message')
                    cmd = ["git", "notes", f"--ref={ref}", "add", "-m", message, target]
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                    except subprocess.CalledProcessError:
                        # Note might already exist, try append
                        cmd = ["git", "notes", f"--ref={ref}", "append", "-m", message, target]
                        subprocess.run(cmd, check=True)
                return None
            return wrapper
        return decorator

try:
    from generated.python.scrum_standup_entry import scrum_standup_entry_span
except ImportError:
    pass


@git_wrap("notes_add")
def note(ref: str, target: str, message: str):
    """Add or append a Git note."""
    pass  # Handled by decorator


def get_author_info() -> Dict[str, str]:
    """Get current Git author information."""
    try:
        name = subprocess.check_output(
            ["git", "config", "user.name"]
        ).decode().strip()
        email = subprocess.check_output(
            ["git", "config", "user.email"]
        ).decode().strip()
        return {"name": name, "email": email}
    except:
        return {"name": os.environ.get("USER", "unknown"), "email": "unknown@localhost"}


@span("scrum_standup_entry")
def post(sprint_id: str, yesterday: str, today: str, blockers: str = "none") -> Dict[str, Any]:
    """
    Post daily standup entry as Git note.
    
    Args:
        sprint_id: Sprint ID (e.g., SPR-2025-W27)
        yesterday: What was accomplished yesterday
        today: What will be worked on today
        blockers: Any blockers (default: "none")
        
    Returns:
        Standup entry details
    """
    tag = f"sprint/{sprint_id}/open"
    
    # Verify sprint exists
    try:
        subprocess.run(
            ["git", "rev-parse", tag],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        raise ValueError(f"Sprint {sprint_id} not found. Has it been started?")
    
    # Create standup entry
    author = get_author_info()
    entry = {
        "date": datetime.date.today().isoformat(),
        "time": datetime.datetime.now().isoformat(),
        "author": author["name"],
        "email": author["email"],
        "yesterday": yesterday,
        "today": today,
        "blockers": blockers
    }
    
    # Format as JSON for note
    payload = json.dumps(entry, indent=2)
    
    # Add note to sprint tag
    note(ref="standup", target=tag, message=payload)
    
    print(f"✅ Posted standup for {sprint_id}")
    print(f"   Author: {author['name']}")
    print(f"   Yesterday: {yesterday[:50]}...")
    print(f"   Today: {today[:50]}...")
    if blockers != "none":
        print(f"   🚧 Blockers: {blockers}")
    
    return entry


@span("scrum_standup_entry")
def get_standups(sprint_id: str, author_filter: Optional[str] = None) -> list:
    """
    Get all standup entries for a sprint.
    
    Args:
        sprint_id: Sprint ID
        author_filter: Optional author name to filter by
        
    Returns:
        List of standup entries
    """
    tag = f"sprint/{sprint_id}/open"
    
    try:
        # Get notes for sprint tag
        notes_output = subprocess.check_output(
            ["git", "notes", "--ref=standup", "show", tag]
        ).decode()
    except subprocess.CalledProcessError:
        return []  # No standups yet
    
    # Parse JSON entries (multiple may be concatenated)
    entries = []
    current_json = ""
    brace_count = 0
    
    for line in notes_output.split('\n'):
        current_json += line + '\n'
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and current_json.strip():
            try:
                entry = json.loads(current_json)
                if not author_filter or entry.get('author') == author_filter:
                    entries.append(entry)
                current_json = ""
            except json.JSONDecodeError:
                # Skip malformed entries
                current_json = ""
    
    # Sort by date/time
    entries.sort(key=lambda x: x.get('time', ''))
    
    return entries


def generate_standup_report(sprint_id: str) -> str:
    """Generate a formatted standup report for the sprint."""
    entries = get_standups(sprint_id)
    
    if not entries:
        return f"No standup entries found for sprint {sprint_id}"
    
    # Group by date
    by_date = {}
    for entry in entries:
        date = entry.get('date', 'unknown')
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(entry)
    
    # Format report
    report = f"# Daily Standup Report - {sprint_id}\n\n"
    
    for date in sorted(by_date.keys(), reverse=True):
        report += f"## {date}\n\n"
        
        for entry in by_date[date]:
            report += f"### {entry.get('author', 'Unknown')}\n"
            report += f"**Yesterday:** {entry.get('yesterday', 'N/A')}\n"
            report += f"**Today:** {entry.get('today', 'N/A')}\n"
            
            blockers = entry.get('blockers', 'none')
            if blockers != 'none':
                report += f"**🚧 Blockers:** {blockers}\n"
            
            report += "\n"
        
        report += "---\n\n"
    
    return report


def main():
    """CLI interface for standup agent."""
    if len(sys.argv) < 2:
        print("Usage: standup_agent.py <command> [args...]")
        print("Commands:")
        print("  post <sprint_id> <yesterday> <today> [blockers]")
        print("  list <sprint_id> [author]")
        print("  report <sprint_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "post":
        if len(sys.argv) < 5:
            print("Usage: standup_agent.py post <sprint_id> <yesterday> <today> [blockers]")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        yesterday = sys.argv[3]
        today = sys.argv[4]
        blockers = sys.argv[5] if len(sys.argv) > 5 else "none"
        
        post(sprint_id, yesterday, today, blockers)
        
    elif command == "list":
        if len(sys.argv) < 3:
            print("Usage: standup_agent.py list <sprint_id> [author]")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        author_filter = sys.argv[3] if len(sys.argv) > 3 else None
        
        entries = get_standups(sprint_id, author_filter)
        
        print(f"\n📢 Standup Entries for {sprint_id} ({len(entries)} total):")
        for entry in entries:
            date = entry.get('date', 'unknown')
            author = entry.get('author', 'Unknown')
            print(f"\n  {date} - {author}:")
            print(f"    Yesterday: {entry.get('yesterday', 'N/A')[:60]}...")
            print(f"    Today: {entry.get('today', 'N/A')[:60]}...")
            
            blockers = entry.get('blockers', 'none')
            if blockers != 'none':
                print(f"    🚧 Blockers: {blockers[:60]}...")
                
    elif command == "report":
        if len(sys.argv) < 3:
            print("Usage: standup_agent.py report <sprint_id>")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        report = generate_standup_report(sprint_id)
        print(report)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()