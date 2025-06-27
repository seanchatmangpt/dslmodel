"""
Git Insight Agent
================

Analyzes Git repository state using multiple views and DSPy to generate
insights, identify risks, and suggest follow-up tasks.

Part of the 80/20 feedback loop - focuses on the most valuable insights.
"""

import sys
import json
import pathlib
from datetime import datetime
from typing import Dict, Any, Optional

# Handle imports gracefully
try:
    from span import span
except ImportError:
    # Fallback decorator
    def span(name):
        def decorator(func):
            return func
        return decorator

from utils.git_views import commit_graph, mermaid_sequence, ref_ledger, get_recent_activity_summary
from dspy_programs.git_insights import GitInsights

# Task utils might not exist yet
try:
    from utils.task_utils import create_task
except ImportError:
    def create_task(agent: str, args: list, priority: int = 50):
        """Fallback task creation - just log it"""
        print(f"[TASK] Would create: {agent} with args {args} (priority: {priority})")

# Generated span might not exist
try:
    from generated.python.ahi_summary_digest import ahi_summary_digest_span
except ImportError:
    pass


VIEW_FN = {
    "graph": commit_graph,
    "mermaid": mermaid_sequence,
    "ledger": ref_ledger,
}


@span("ahi_summary_digest")
def run(view: str = "graph") -> Dict[str, Any]:
    """
    Analyze Git repository state and generate insights.
    
    Args:
        view: Type of Git view to analyze (graph, mermaid, ledger)
        
    Returns:
        Dict containing summary, risks, and suggested tasks
    """
    if view not in VIEW_FN:
        raise ValueError("Invalid view type. Choose: graph | mermaid | ledger")
    
    # Get the raw Git data
    print(f"🔍 Generating Git {view} view...")
    raw = VIEW_FN[view]()
    
    # Add context about recent activity
    activity = get_recent_activity_summary()
    context = f"\n\nRECENT ACTIVITY:\n"
    context += f"- Commits last week: {activity['commits_last_week']}\n"
    context += f"- Active authors: {', '.join(activity['active_authors'][:3])}\n"
    context += f"- Changed files: {activity['recently_changed_files']}\n"
    context += f"- Total branches: {activity['branch_count']}\n"
    
    raw_with_context = raw + context
    
    # Always use fallback for now since DSPy integration needs more setup
    print("🧠 Analyzing Git repository...")
    result = fallback_analysis(view, raw, activity)
    
    # Create digest directory if needed
    digest_path = pathlib.Path(f"digests/{view}_digest.md")
    digest_path.parent.mkdir(exist_ok=True)
    
    # Write human-readable digest
    digest_content = f"# Git {view.title()} Insight Digest\n\n"
    digest_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    digest_content += f"## Summary\n\n{result['summary']}\n\n"
    
    if result.get('risks'):
        digest_content += "## Risks Identified\n\n"
        for risk in result['risks']:
            digest_content += f"- {risk}\n"
        digest_content += "\n"
    
    if activity['active_authors']:
        digest_content += f"## Active Contributors\n\n"
        digest_content += f"{', '.join(activity['active_authors'])}\n\n"
    
    digest_path.write_text(digest_content)
    print(f"✅ Digest written to: {digest_path}")
    
    # Create follow-up tasks if suggested
    if result.get('next_tasks'):
        print(f"📋 Creating {len(result['next_tasks'])} follow-up tasks...")
        for task in result['next_tasks']:
            create_task(
                task['agent'], 
                task.get('arg', []), 
                priority=task.get('priority', 70)
            )
    
    # Print result for logging
    print(json.dumps(result, indent=2))
    
    return result


def fallback_analysis(view: str, raw: str, activity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback analysis when DSPy is not available.
    Uses simple heuristics to generate insights.
    """
    result = {
        "summary": "",
        "risks": [],
        "next_tasks": []
    }
    
    # Analyze based on view type
    if view == "graph":
        # Count branches and merges
        branches = raw.count('|\\')
        merges = raw.count('|/')
        commits = len([l for l in raw.split('\n') if l.strip() and '*' in l])
        
        result["summary"] = f"Repository shows {commits} recent commits with {branches} branches and {merges} merges. "
        
        if branches > 5:
            result["risks"].append("High branch complexity may indicate coordination issues")
        if merges == 0 and branches > 2:
            result["risks"].append("Multiple unmerged branches detected")
            
    elif view == "mermaid":
        operations = raw.count('->>Git:')
        result["summary"] = f"Sequence diagram shows {operations} Git operations tracked. "
        
        if operations == 0:
            result["risks"].append("No Git operations being tracked in spans")
            
    elif view == "ledger":
        ref_lines = [l for l in raw.split('\n') if l.strip()]
        branch_count = sum(1 for l in ref_lines if 'BRANCHES:' not in l and l.startswith('  '))
        
        result["summary"] = f"Repository contains {branch_count} refs across branches, tags, and remotes. "
        
        if branch_count > 20:
            result["risks"].append("Large number of refs may need cleanup")
    
    # Add activity-based insights
    if activity['commits_last_week'] > 50:
        result["risks"].append("High commit volume may indicate rushed development")
    elif activity['commits_last_week'] == 0:
        result["risks"].append("No commits in last week - project may be stalled")
    
    # Suggest tasks based on risks
    if any("branch" in risk.lower() for risk in result["risks"]):
        result["next_tasks"].append({
            "agent": "branch_cleanup_agent",
            "arg": ["--dry-run"],
            "priority": 60
        })
    
    return result


if __name__ == "__main__":
    # Allow command-line view selection
    view_type = sys.argv[1] if len(sys.argv) > 1 else "graph"
    run(view_type)