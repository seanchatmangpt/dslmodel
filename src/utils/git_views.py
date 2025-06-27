"""
Git Views Utility
================

Provides multiple representations of Git repository state for analysis.
Supports commit graph, mermaid sequence diagrams, and ref ledger views.
"""

import subprocess
import pathlib
import json
import re
import textwrap
from typing import List, Dict, Any


def commit_graph(limit: int = 30) -> str:
    """
    Generate ASCII commit graph using git log.
    
    Args:
        limit: Maximum number of commits to show
        
    Returns:
        ASCII graph representation of recent commits
    """
    cmd = ["git", "log", "--graph", "--decorate", "--oneline", f"-n{limit}"]
    try:
        return subprocess.check_output(cmd, cwd=pathlib.Path.cwd()).decode()
    except subprocess.CalledProcessError as e:
        return f"Error generating commit graph: {e}"


def mermaid_sequence() -> str:
    """
    Generate Mermaid sequence diagram from spans.jsonl.
    
    Returns:
        Mermaid markdown for Git-related spans
    """
    spans_file = pathlib.Path("spans.jsonl")
    
    if not spans_file.exists():
        return "```mermaid\nsequenceDiagram\n    Note: No spans.jsonl found\n```"
    
    edges = []
    try:
        lines = spans_file.read_text().splitlines()
        for ln in lines:
            if not ln.strip():
                continue
            jd = json.loads(ln)
            if jd.get("name", "").startswith("git."):
                # Extract agent and operation
                parts = jd["name"].split(".")
                if len(parts) >= 2:
                    operation = parts[1]
                    edges.append(f'    Cron->>Git: {operation}')
    except Exception as e:
        edges.append(f'    Note: Error parsing spans: {str(e)}')
    
    if not edges:
        edges.append('    Note: No Git operations found')
    
    return "```mermaid\nsequenceDiagram\n" + "\n".join(edges) + "\n```"


def ref_ledger() -> str:
    """
    Generate reference ledger showing all Git refs.
    
    Returns:
        Indented list of all Git references
    """
    try:
        out = subprocess.check_output(
            ["git", "for-each-ref", "--format=%(refname)"],
            cwd=pathlib.Path.cwd()
        ).decode()
        
        # Organize refs by type
        refs = out.strip().split('\n')
        organized = {
            'heads': [],
            'remotes': [],
            'tags': [],
            'other': []
        }
        
        for ref in refs:
            if ref.startswith('refs/heads/'):
                organized['heads'].append(ref.replace('refs/heads/', ''))
            elif ref.startswith('refs/remotes/'):
                organized['remotes'].append(ref.replace('refs/remotes/', ''))
            elif ref.startswith('refs/tags/'):
                organized['tags'].append(ref.replace('refs/tags/', ''))
            else:
                organized['other'].append(ref)
        
        # Format output
        output = []
        if organized['heads']:
            output.append("BRANCHES:")
            output.extend(f"  {b}" for b in organized['heads'])
        
        if organized['remotes']:
            output.append("\nREMOTES:")
            output.extend(f"  {r}" for r in organized['remotes'])
        
        if organized['tags']:
            output.append("\nTAGS:")
            output.extend(f"  {t}" for t in organized['tags'])
        
        if organized['other']:
            output.append("\nOTHER:")
            output.extend(f"  {o}" for o in organized['other'])
        
        return "\n".join(output) if output else "  No refs found"
        
    except subprocess.CalledProcessError as e:
        return f"  Error reading refs: {e}"


def get_recent_activity_summary() -> Dict[str, Any]:
    """
    Get a summary of recent Git activity for context.
    
    Returns:
        Dict with commit count, author info, and file changes
    """
    try:
        # Get commit count for last 7 days
        week_ago = subprocess.check_output(
            ["git", "log", "--since='7 days ago'", "--oneline"],
            cwd=pathlib.Path.cwd()
        ).decode().strip().split('\n')
        
        # Get unique authors
        authors = subprocess.check_output(
            ["git", "log", "--since='7 days ago'", "--format=%an"],
            cwd=pathlib.Path.cwd()
        ).decode().strip().split('\n')
        unique_authors = set(authors) - {''}
        
        # Get changed files
        changed_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~5..HEAD"],
            cwd=pathlib.Path.cwd()
        ).decode().strip().split('\n')
        
        return {
            "commits_last_week": len(week_ago) if week_ago[0] else 0,
            "active_authors": list(unique_authors),
            "recently_changed_files": len([f for f in changed_files if f]),
            "branch_count": len(subprocess.check_output(
                ["git", "branch", "-a"], cwd=pathlib.Path.cwd()
            ).decode().strip().split('\n'))
        }
    except:
        return {
            "commits_last_week": 0,
            "active_authors": [],
            "recently_changed_files": 0,
            "branch_count": 0
        }