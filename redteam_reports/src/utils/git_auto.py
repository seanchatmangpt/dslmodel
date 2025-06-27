"""
Git Auto Operations
===================

Provides automated git operations with OTEL telemetry and
YAML-driven command configuration. Used by agents for
coordinated git workflows.
"""

import os
import yaml
import subprocess
import functools
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from .span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from .log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

# Load git registry configuration
REGISTRY_PATH = Path(__file__).parent.parent.parent / "etc" / "git_registry.yaml"

def load_git_registry() -> Dict[str, Dict[str, Any]]:
    """Load git command registry from YAML."""
    if not REGISTRY_PATH.exists():
        logger.warning(f"Git registry not found at {REGISTRY_PATH}")
        return {}
    
    try:
        with open(REGISTRY_PATH) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load git registry: {e}")
        return {}

# Global registry
GIT_REGISTRY = load_git_registry()

class GitOperationError(Exception):
    """Raised when git operations fail."""
    pass

@span("git_execute")
def execute_git_command(
    operation: str,
    cwd: Optional[str] = None,
    check: bool = True,
    capture_output: bool = True,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Execute a git command with OTEL telemetry.
    
    Args:
        operation: Git operation name from registry
        cwd: Working directory for command
        check: Whether to raise on non-zero exit
        capture_output: Whether to capture stdout/stderr
        **kwargs: Parameters for command formatting
        
    Returns:
        CompletedProcess result
    """
    if operation not in GIT_REGISTRY:
        raise GitOperationError(f"Unknown git operation: {operation}")
    
    config = GIT_REGISTRY[operation]
    cmd_template = config["cmd"]
    
    try:
        # Format command with provided kwargs
        cmd = cmd_template.format(**kwargs)
        
        # Handle special cases for git operations with messages
        if operation == "tag_annotate":
            cmd_parts = ["git", "tag", "-a", kwargs["name"], "-m", kwargs["message"]]
        elif operation == "notes_add":
            cmd_parts = ["git", "notes", f"--ref={kwargs['ref']}", "add", "-m", kwargs["message"], kwargs["target"]]
        else:
            cmd_parts = cmd.split()
        
        # Determine working directory
        working_dir = cwd
        if config.get("cwd_arg") and config["cwd_arg"] in kwargs:
            working_dir = kwargs[config["cwd_arg"]]
        
        logger.info(f"Executing git command: {operation} (cwd: {working_dir})")
        
        # Execute command
        result = subprocess.run(
            cmd_parts,
            cwd=working_dir,
            check=check,
            capture_output=capture_output,
            text=True
        )
        
        logger.debug(f"Git command completed: {cmd} (exit: {result.returncode})")
        return result
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {cmd} (exit: {e.returncode})")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        raise GitOperationError(f"Git {operation} failed: {e}")
    except Exception as e:
        logger.error(f"Git command error: {cmd} - {e}")
        raise GitOperationError(f"Git {operation} error: {e}")

def git_wrap(operation: str):
    """
    Decorator to wrap functions with git operations.
    
    The decorated function should accept git operation parameters
    and the decorator will execute the corresponding git command.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Extract git parameters from function arguments
                git_params = {}
                
                # Check if this is a simple git operation call
                if operation == "notes_add" and len(kwargs) >= 3:
                    # Special handling for notes operations
                    git_params = {
                        "ref": kwargs.get("ref"),
                        "message": kwargs.get("message"),
                        "target": kwargs.get("target")
                    }
                elif operation == "tag_annotate" and len(kwargs) >= 2:
                    git_params = {
                        "name": kwargs.get("name"),
                        "message": kwargs.get("message")
                    }
                elif operation == "commit" and len(kwargs) >= 1:
                    git_params = {
                        "msg": kwargs.get("msg") or kwargs.get("message")
                    }
                
                # Execute git operation if we have parameters
                if git_params and all(v is not None for v in git_params.values()):
                    result = execute_git_command(operation, **git_params)
                    # Call original function with git result
                    return func(*args, git_result=result, **kwargs)
                else:
                    # Call original function without git operation
                    return func(*args, **kwargs)
                    
            except GitOperationError:
                # Re-raise git errors
                raise
            except Exception as e:
                logger.error(f"Error in git_wrap({operation}): {e}")
                # Fall back to calling original function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Convenience functions for common git operations

@span("git_branch")
def branch(name: str, base: str = "HEAD", repo: Optional[str] = None) -> subprocess.CompletedProcess:
    """Create a git branch."""
    return execute_git_command("branch", name=name, base=base, cwd=repo)

@span("git_notes_add")
def notes_add(ref: str, target: str, message: str) -> subprocess.CompletedProcess:
    """Add a git note."""
    return execute_git_command("notes_add", ref=ref, target=target, message=message)

@span("git_commit")
def commit(msg: str) -> subprocess.CompletedProcess:
    """Create a git commit."""
    return execute_git_command("commit", msg=msg)

@span("git_tag_annotate") 
def tag(name: str, message: str) -> subprocess.CompletedProcess:
    """Create an annotated git tag."""
    return execute_git_command("tag_annotate", name=name, message=message)

@span("git_push")
def push(remote: str = "origin", refspec: str = "HEAD", repo_path: Optional[str] = None) -> subprocess.CompletedProcess:
    """Push to remote repository."""
    return execute_git_command("push", remote=remote, refspec=refspec, repo_path=repo_path)

@span("git_fetch")
def fetch(remote: str = "origin", ref: str = "", repo: Optional[str] = None) -> subprocess.CompletedProcess:
    """Fetch from remote repository."""
    return execute_git_command("fetch", remote=remote, ref=ref, repo=repo)

@span("git_merge")
def merge(branch: str, repo: Optional[str] = None) -> subprocess.CompletedProcess:
    """Merge a branch."""
    return execute_git_command("merge", branch=branch, repo=repo)

@span("git_worktree")
def worktree_add(path: str, sha: str) -> subprocess.CompletedProcess:
    """Add a git worktree."""
    return execute_git_command("worktree", path=path, sha=sha)

@span("git_clone")
def clone(repo_url: str, target_path: str) -> subprocess.CompletedProcess:
    """Clone a repository."""
    return execute_git_command("clone", repo_url=repo_url, target_path=target_path)

# Git state inspection utilities

@span("git_get_current_branch")
def get_current_branch(repo: Optional[str] = None) -> str:
    """Get the current branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

@span("git_get_commit_hash")
def get_commit_hash(ref: str = "HEAD", repo: Optional[str] = None) -> str:
    """Get commit hash for a reference."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

@span("git_get_status")
def get_status(repo: Optional[str] = None) -> Dict[str, List[str]]:
    """Get git status information."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": []
        }
        
        for line in result.stdout.splitlines():
            if not line:
                continue
            status_code = line[:2]
            filepath = line[3:]
            
            if status_code.startswith("M"):
                status["modified"].append(filepath)
            elif status_code.startswith("A"):
                status["added"].append(filepath)
            elif status_code.startswith("D"):
                status["deleted"].append(filepath)
            elif status_code.startswith("R"):
                status["renamed"].append(filepath)
            elif status_code.startswith("??"):
                status["untracked"].append(filepath)
        
        return status
    except subprocess.CalledProcessError:
        return {"error": ["Failed to get git status"]}

# Integration with OTEL and task system

@span("git_operation_with_task")
def execute_with_task_tracking(operation: str, task_id: Optional[str] = None, **kwargs) -> Any:
    """Execute git operation with task coordination tracking."""
    try:
        result = execute_git_command(operation, **kwargs)
        
        if task_id:
            # Update task with git operation result
            try:
                from .task_utils import complete_task
                complete_task(task_id, result={
                    "operation": operation,
                    "returncode": result.returncode,
                    "stdout": result.stdout[:1000] if result.stdout else "",
                    "stderr": result.stderr[:1000] if result.stderr else ""
                })
            except ImportError:
                logger.warning("Task coordination not available")
        
        return result
    except Exception as e:
        if task_id:
            try:
                from .task_utils import complete_task
                complete_task(task_id, error=str(e))
            except ImportError:
                pass
        raise