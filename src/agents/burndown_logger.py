"""
Burndown Logger - Git-native sprint burndown tracking
====================================================

Tracks remaining story points daily as Git notes on sprint tags,
enabling burndown chart generation from Git history alone.
"""

import sys
import json
import datetime
import subprocess
import re
from typing import Dict, Any, List, Tuple

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
                        # Note might already exist for today, update it
                        cmd = ["git", "notes", f"--ref={ref}", "append", "-m", f"\n{message}", target]
                        subprocess.run(cmd, check=True)
                return None
            return wrapper
        return decorator

try:
    from generated.python.scrum_burndown_metric import scrum_burndown_metric_span
except ImportError:
    pass


@git_wrap("notes_add")
def note(ref: str, target: str, message: str):
    """Add or append a Git note."""
    pass  # Handled by decorator


def remaining_points() -> Tuple[int, Dict[str, int]]:
    """
    Calculate remaining story points in backlog.
    
    Returns:
        Tuple of (total_remaining, breakdown_by_status)
    """
    try:
        # Search for all story point declarations in backlog
        out = subprocess.check_output(
            ["git", "grep", "-h", r"^\*\*Points:\*\*\|^Points:", "HEAD:backlog/"],
            cwd="."
        ).decode()
    except subprocess.CalledProcessError:
        # No backlog files or no matches
        return 0, {}
    
    total_by_status = {
        "Ready": 0,
        "In Progress": 0,
        "Done": 0,
        "Unknown": 0
    }
    
    # Parse each backlog file to get points and status
    backlog_files = subprocess.check_output(
        ["git", "ls-files", "backlog/BI-*.md"]
    ).decode().strip().split('\n')
    
    for fname in backlog_files:
        if not fname:
            continue
            
        try:
            content = subprocess.check_output(
                ["git", "show", f"HEAD:{fname}"]
            ).decode()
            
            # Extract points
            points_match = re.search(r'\*\*Points:\*\*\s*(\d+)', content)
            points = int(points_match.group(1)) if points_match else 0
            
            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
            status = status_match.group(1) if status_match else "Unknown"
            
            if status not in total_by_status:
                total_by_status[status] = 0
            total_by_status[status] += points
            
        except:
            continue
    
    # Calculate remaining (exclude Done items)
    remaining = sum(points for status, points in total_by_status.items() 
                   if status != "Done")
    
    return remaining, total_by_status


@span("scrum_burndown_metric")
def log_metric(sprint_id: str) -> Dict[str, Any]:
    """
    Log daily burndown metric as Git note.
    
    Args:
        sprint_id: Sprint ID (e.g., SPR-2025-W27)
        
    Returns:
        Burndown metric data
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
    
    # Calculate metrics
    today = datetime.date.today()
    day_of_week = today.weekday()  # 0 = Monday
    remaining, breakdown = remaining_points()
    
    # Create burndown entry
    metric = {
        "date": today.isoformat(),
        "day_index": day_of_week,
        "day_name": today.strftime("%A"),
        "remaining_points": remaining,
        "breakdown": breakdown,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Log as note
    payload = json.dumps(metric, indent=2)
    note(ref="burndown", target=tag, message=payload)
    
    print(f"📉 Logged burndown for {sprint_id} - Day {day_of_week} ({today.strftime('%A')})")
    print(f"   Remaining: {remaining} points")
    print(f"   Breakdown:")
    for status, points in breakdown.items():
        if points > 0:
            print(f"     {status}: {points} pts")
    
    return metric


def get_burndown_data(sprint_id: str) -> List[Dict[str, Any]]:
    """
    Get all burndown metrics for a sprint.
    
    Args:
        sprint_id: Sprint ID
        
    Returns:
        List of burndown metrics ordered by date
    """
    tag = f"sprint/{sprint_id}/open"
    
    try:
        # Get burndown notes
        notes_output = subprocess.check_output(
            ["git", "notes", "--ref=burndown", "show", tag]
        ).decode()
    except subprocess.CalledProcessError:
        return []  # No burndown data yet
    
    # Parse JSON entries
    metrics = []
    current_json = ""
    brace_count = 0
    
    for line in notes_output.split('\n'):
        current_json += line + '\n'
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and current_json.strip():
            try:
                metric = json.loads(current_json)
                metrics.append(metric)
                current_json = ""
            except json.JSONDecodeError:
                current_json = ""
    
    # Sort by date
    metrics.sort(key=lambda x: x.get('date', ''))
    
    return metrics


def generate_burndown_chart(sprint_id: str) -> str:
    """
    Generate ASCII burndown chart for sprint.
    
    Args:
        sprint_id: Sprint ID
        
    Returns:
        ASCII chart as string
    """
    metrics = get_burndown_data(sprint_id)
    
    if not metrics:
        return f"No burndown data available for sprint {sprint_id}"
    
    # Get sprint capacity from tag
    try:
        tag_info = subprocess.check_output(
            ["git", "tag", "-l", "-n100", f"sprint/{sprint_id}/open"]
        ).decode()
        json_start = tag_info.find('{')
        if json_start > 0:
            sprint_data = json.loads(tag_info[json_start:])
            capacity = sprint_data.get('capacity', 0)
        else:
            capacity = 0
    except:
        capacity = 0
    
    # Prepare chart data
    chart = f"# Burndown Chart - {sprint_id}\n\n"
    chart += f"Capacity: {capacity} points\n\n"
    
    # Create simple ASCII chart
    max_points = max(capacity, max(m['remaining_points'] for m in metrics))
    chart_height = 10
    
    chart += "Points\n"
    
    # Y-axis and chart
    for i in range(chart_height, -1, -1):
        points_at_line = int(max_points * i / chart_height)
        chart += f"{points_at_line:4d} |"
        
        # Plot points
        for day in range(5):  # Mon-Fri
            day_metric = next((m for m in metrics if m['day_index'] == day), None)
            
            if day_metric:
                metric_height = int(day_metric['remaining_points'] * chart_height / max_points)
                if i == metric_height:
                    chart += " * "
                elif i < metric_height:
                    chart += " | "
                else:
                    chart += "   "
            else:
                chart += "   "
        
        # Ideal line
        ideal_points = capacity * (4 - i * 4 / chart_height) / 4
        if abs(points_at_line - ideal_points) < max_points / (2 * chart_height):
            chart += " /"
        
        chart += "\n"
    
    # X-axis
    chart += "     +---------------/\n"
    chart += "      Mon Tue Wed Thu Fri\n\n"
    
    # Summary
    if metrics:
        latest = metrics[-1]
        chart += f"Latest: {latest['remaining_points']} points remaining ({latest['day_name']})\n"
        
        if capacity > 0:
            burn_rate = (capacity - latest['remaining_points']) / (latest['day_index'] + 1)
            projected_completion = capacity / burn_rate if burn_rate > 0 else 999
            chart += f"Burn rate: {burn_rate:.1f} pts/day\n"
            
            if projected_completion <= 5:
                chart += f"✅ On track to complete\n"
            else:
                chart += f"⚠️  At risk - projected {projected_completion:.1f} days to complete\n"
    
    return chart


def main():
    """CLI interface for burndown logger."""
    if len(sys.argv) < 2:
        print("Usage: burndown_logger.py <command> [args...]")
        print("Commands:")
        print("  log <sprint_id>      - Log current burndown metric")
        print("  show <sprint_id>     - Show burndown data")
        print("  chart <sprint_id>    - Generate burndown chart")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Usage: burndown_logger.py log <sprint_id>")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        log_metric(sprint_id)
        
    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: burndown_logger.py show <sprint_id>")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        metrics = get_burndown_data(sprint_id)
        
        print(f"\n📊 Burndown Data for {sprint_id}:")
        for metric in metrics:
            date = metric.get('date', 'unknown')
            remaining = metric.get('remaining_points', 0)
            day = metric.get('day_name', '')
            print(f"  {date} ({day}): {remaining} points remaining")
            
    elif command == "chart":
        if len(sys.argv) < 3:
            print("Usage: burndown_logger.py chart <sprint_id>")
            sys.exit(1)
        
        sprint_id = sys.argv[2]
        chart = generate_burndown_chart(sprint_id)
        print(chart)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()