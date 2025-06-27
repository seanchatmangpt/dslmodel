#!/usr/bin/env python3
"""
Git Auto CLI - Automated Git Operations with Smart DX
=====================================================

Provides automated git add, commit, and push with intelligent:
- Commit message generation
- Pre-commit validation
- Conflict detection and resolution
- Branch management
- Developer experience optimizations

80/20 Focus: Essential git operations with minimal friction
"""

import typer
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from datetime import datetime
import re

app = typer.Typer(name="git-auto", help="Automated git operations with smart DX")
console = Console()


class GitAutoManager:
    """Manages automated git operations with intelligent workflows"""
    
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.config = self._load_config()
        
    def _find_repo_root(self) -> Path:
        """Find git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load git auto configuration"""
        config_file = self.repo_root / ".git_auto_config.json"
        default_config = {
            "auto_commit_prefixes": ["feat:", "fix:", "docs:", "refactor:", "test:", "chore:"],
            "smart_commit_messages": True,
            "pre_commit_validation": True,
            "auto_push": False,
            "branch_protection": ["main", "master", "production"],
            "commit_template": "{type}: {scope} - {description}",
            "max_commit_length": 72,
            "include_file_stats": True
        }
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def _run_git_command(self, command: List[str], capture_output=True) -> subprocess.CompletedProcess:
        """Run git command with error handling"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            console.print(f"❌ Git command failed: {e}")
            raise typer.Exit(1)
    
    def get_repo_status(self) -> Dict[str, Any]:
        """Get comprehensive repository status"""
        # Get current branch
        branch_result = self._run_git_command(["branch", "--show-current"])
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get status
        status_result = self._run_git_command(["status", "--porcelain"])
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
        
        # Parse status
        staged_files = []
        unstaged_files = []
        untracked_files = []
        
        for line in status_lines:
            if len(line) >= 3:
                status_code = line[:2]
                filename = line[3:]
                
                if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                    staged_files.append(filename)
                if status_code[1] in ['M', 'D']:
                    unstaged_files.append(filename)
                if status_code == '??':
                    untracked_files.append(filename)
        
        # Get commit count ahead/behind origin
        ahead_behind = {"ahead": 0, "behind": 0}
        try:
            remote_result = self._run_git_command(["rev-list", "--count", "--left-right", f"origin/{current_branch}...HEAD"])
            if remote_result.returncode == 0:
                parts = remote_result.stdout.strip().split('\t')
                if len(parts) == 2:
                    ahead_behind["behind"] = int(parts[0])
                    ahead_behind["ahead"] = int(parts[1])
        except:
            pass
        
        return {
            "branch": current_branch,
            "staged_files": staged_files,
            "unstaged_files": unstaged_files,
            "untracked_files": untracked_files,
            "ahead_behind": ahead_behind,
            "is_clean": len(staged_files) == 0 and len(unstaged_files) == 0 and len(untracked_files) == 0
        }
    
    def generate_smart_commit_message(self, status: Dict[str, Any]) -> str:
        """Generate intelligent commit message based on changes"""
        if not self.config["smart_commit_messages"]:
            return ""
        
        changed_files = status["staged_files"] + status["unstaged_files"]
        
        # Analyze file patterns
        file_patterns = {
            "tests": [f for f in changed_files if "test" in f.lower() or f.endswith("_test.py")],
            "docs": [f for f in changed_files if f.endswith(".md") or "doc" in f.lower()],
            "config": [f for f in changed_files if f in ["pyproject.toml", "setup.py", "requirements.txt", ".gitignore"]],
            "cli": [f for f in changed_files if "cli" in f.lower() or "command" in f.lower()],
            "src": [f for f in changed_files if f.startswith("src/")],
            "examples": [f for f in changed_files if "example" in f.lower()],
        }
        
        # Determine commit type and scope
        commit_type = "feat"
        scope = ""
        
        if file_patterns["tests"]:
            commit_type = "test"
            scope = "validation"
        elif file_patterns["docs"]:
            commit_type = "docs"
            scope = "readme"
        elif file_patterns["config"]:
            commit_type = "chore"
            scope = "config"
        elif file_patterns["cli"]:
            commit_type = "feat"
            scope = "cli"
        elif file_patterns["examples"]:
            commit_type = "feat"
            scope = "examples"
        
        # Generate description based on file analysis
        descriptions = []
        
        if file_patterns["cli"]:
            descriptions.append("add automated git operations")
        if file_patterns["tests"]:
            descriptions.append("add validation tests")
        if file_patterns["docs"]:
            descriptions.append("update documentation")
        if file_patterns["config"]:
            descriptions.append("update configuration")
        if file_patterns["examples"]:
            descriptions.append("add demonstration examples")
        
        if not descriptions:
            descriptions.append("update implementation")
        
        description = ", ".join(descriptions)
        
        # Format commit message
        if scope:
            message = f"{commit_type}({scope}): {description}"
        else:
            message = f"{commit_type}: {description}"
        
        # Add file stats if enabled
        if self.config["include_file_stats"]:
            file_count = len(changed_files)
            if file_count > 0:
                message += f"\n\n- {file_count} files modified"
                if file_patterns["tests"]:
                    message += f"\n- {len(file_patterns['tests'])} test files"
                if file_patterns["docs"]:
                    message += f"\n- {len(file_patterns['docs'])} documentation files"
        
        # Ensure message length
        if len(message.split('\n')[0]) > self.config["max_commit_length"]:
            first_line = message.split('\n')[0]
            message = first_line[:self.config["max_commit_length"]-3] + "..."
        
        return message
    
    def validate_pre_commit(self) -> bool:
        """Run pre-commit validations"""
        if not self.config["pre_commit_validation"]:
            return True
        
        validations = []
        
        # Check for large files
        status = self.get_repo_status()
        large_files = []
        for file_path in status["staged_files"] + status["unstaged_files"]:
            try:
                file_size = (self.repo_root / file_path).stat().st_size
                if file_size > 10 * 1024 * 1024:  # 10MB
                    large_files.append((file_path, file_size))
            except:
                pass
        
        if large_files:
            console.print("⚠️ Large files detected:")
            for file_path, size in large_files:
                console.print(f"   📁 {file_path}: {size / 1024 / 1024:.1f}MB")
            if not Confirm.ask("Continue with large files?"):
                return False
        
        # Check for sensitive patterns
        sensitive_patterns = [
            r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        sensitive_found = False
        for file_path in status["staged_files"]:
            try:
                file_full_path = self.repo_root / file_path
                if file_full_path.suffix in ['.py', '.js', '.ts', '.json', '.yaml', '.yml']:
                    content = file_full_path.read_text()
                    for pattern in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            console.print(f"⚠️ Potential sensitive data in {file_path}")
                            sensitive_found = True
                            break
            except:
                pass
        
        if sensitive_found:
            if not Confirm.ask("Potential sensitive data found. Continue?"):
                return False
        
        return True


@app.command()
def status():
    """Show enhanced git status with auto-commit suggestions"""
    manager = GitAutoManager()
    status = manager.get_repo_status()
    
    # Create status table
    table = Table(title="🔍 Enhanced Git Status")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Count", style="bold")
    table.add_column("Files", style="dim")
    
    # Add status rows
    table.add_row("Branch", "1", f"📍 {status['branch']}")
    
    if status["staged_files"]:
        files_preview = ", ".join(status["staged_files"][:3])
        if len(status["staged_files"]) > 3:
            files_preview += f" (+{len(status['staged_files'])-3} more)"
        table.add_row("Staged", str(len(status["staged_files"])), f"✅ {files_preview}")
    
    if status["unstaged_files"]:
        files_preview = ", ".join(status["unstaged_files"][:3])
        if len(status["unstaged_files"]) > 3:
            files_preview += f" (+{len(status['unstaged_files'])-3} more)"
        table.add_row("Modified", str(len(status["unstaged_files"])), f"📝 {files_preview}")
    
    if status["untracked_files"]:
        files_preview = ", ".join(status["untracked_files"][:3])
        if len(status["untracked_files"]) > 3:
            files_preview += f" (+{len(status['untracked_files'])-3} more)"
        table.add_row("Untracked", str(len(status["untracked_files"])), f"❓ {files_preview}")
    
    ahead_behind = status["ahead_behind"]
    if ahead_behind["ahead"] > 0 or ahead_behind["behind"] > 0:
        sync_status = f"↑{ahead_behind['ahead']} ↓{ahead_behind['behind']}"
        table.add_row("Remote Sync", sync_status, "🔄 Need to sync")
    
    console.print(table)
    
    # Show smart commit suggestion
    if not status["is_clean"]:
        suggested_message = manager.generate_smart_commit_message(status)
        if suggested_message:
            console.print(Panel(
                f"💡 Suggested commit message:\n[bold green]{suggested_message}[/bold green]",
                title="Smart Commit",
                border_style="blue"
            ))


@app.command()
def add(
    files: Optional[List[str]] = typer.Argument(None, help="Files to add (default: all)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive file selection"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be added")
):
    """Smart git add with file filtering and validation"""
    manager = GitAutoManager()
    
    if not files:
        # Add all files by default
        git_add_cmd = ["add", "."]
    else:
        git_add_cmd = ["add"] + files
    
    if dry_run:
        console.print(f"🔍 Would run: git {' '.join(git_add_cmd)}")
        return
    
    if interactive:
        status = manager.get_repo_status()
        all_files = status["unstaged_files"] + status["untracked_files"]
        
        if not all_files:
            console.print("✅ No files to add")
            return
        
        selected_files = []
        for file_path in all_files:
            if Confirm.ask(f"Add {file_path}?"):
                selected_files.append(file_path)
        
        if selected_files:
            git_add_cmd = ["add"] + selected_files
        else:
            console.print("ℹ️ No files selected")
            return
    
    # Run git add
    with Progress(SpinnerColumn(), TextColumn("Adding files..."), console=console) as progress:
        task = progress.add_task("Adding...", total=1)
        result = manager._run_git_command(git_add_cmd)
        progress.update(task, completed=1)
    
    if result.returncode == 0:
        # Show what was added
        status = manager.get_repo_status()
        console.print(f"✅ Added {len(status['staged_files'])} files")
        
        # Show next step suggestion
        if status['staged_files']:
            console.print("💡 Next: [bold]dsl git-auto commit[/bold] or [bold]dsl git-auto auto[/bold]")
    else:
        console.print(f"❌ Git add failed: {result.stderr}")
        raise typer.Exit(1)


@app.command()
def commit(
    message: Optional[str] = typer.Option(None, "-m", "--message", help="Commit message"),
    auto_message: bool = typer.Option(True, "--auto-message/--no-auto-message", help="Generate smart commit message"),
    amend: bool = typer.Option(False, "--amend", help="Amend last commit"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Run pre-commit validation")
):
    """Smart git commit with generated messages and validation"""
    manager = GitAutoManager()
    status = manager.get_repo_status()
    
    # Check if there's anything to commit
    if not status["staged_files"] and not amend:
        console.print("⚠️ No staged files to commit")
        console.print("💡 Run [bold]dsl git-auto add[/bold] first")
        return
    
    # Run pre-commit validation
    if validate and not manager.validate_pre_commit():
        console.print("❌ Pre-commit validation failed")
        raise typer.Exit(1)
    
    # Generate or get commit message
    if not message and auto_message and not amend:
        message = manager.generate_smart_commit_message(status)
        
        if message:
            console.print(f"💡 Generated message: [bold]{message.split(chr(10))[0]}[/bold]")
            if not Confirm.ask("Use this message?"):
                message = Prompt.ask("Enter commit message")
        else:
            message = Prompt.ask("Enter commit message")
    elif not message and not amend:
        message = Prompt.ask("Enter commit message")
    
    # Build commit command
    commit_cmd = ["commit"]
    if message:
        commit_cmd.extend(["-m", message])
    if amend:
        commit_cmd.append("--amend")
        if not message:
            commit_cmd.append("--no-edit")
    
    # Run commit
    with Progress(SpinnerColumn(), TextColumn("Creating commit..."), console=console) as progress:
        task = progress.add_task("Committing...", total=1)
        result = manager._run_git_command(commit_cmd)
        progress.update(task, completed=1)
    
    if result.returncode == 0:
        # Get commit hash
        hash_result = manager._run_git_command(["rev-parse", "--short", "HEAD"])
        commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
        
        console.print(f"✅ Commit created: [bold green]{commit_hash}[/bold green]")
        
        # Show next step suggestion
        updated_status = manager.get_repo_status()
        if updated_status["ahead_behind"]["ahead"] > 0:
            console.print("💡 Next: [bold]dsl git-auto push[/bold] or [bold]dsl git-auto auto --push[/bold]")
    else:
        console.print(f"❌ Commit failed: {result.stderr}")
        raise typer.Exit(1)


@app.command()
def push(
    force: bool = typer.Option(False, "--force", help="Force push"),
    upstream: bool = typer.Option(False, "--set-upstream", "-u", help="Set upstream branch"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pushed")
):
    """Smart git push with branch protection and conflict detection"""
    manager = GitAutoManager()
    status = manager.get_repo_status()
    
    # Check branch protection
    if status["branch"] in manager.config["branch_protection"] and force:
        console.print(f"🛡️ Branch '{status['branch']}' is protected")
        if not Confirm.ask("Force push to protected branch?"):
            return
    
    # Check if there's anything to push
    if status["ahead_behind"]["ahead"] == 0:
        console.print("✅ Already up to date")
        return
    
    # Build push command
    push_cmd = ["push"]
    if force:
        push_cmd.append("--force-with-lease")
    if upstream:
        push_cmd.extend(["--set-upstream", "origin", status["branch"]])
    
    if dry_run:
        console.print(f"🔍 Would run: git {' '.join(push_cmd)}")
        console.print(f"📤 Would push {status['ahead_behind']['ahead']} commits")
        return
    
    # Run push
    with Progress(SpinnerColumn(), TextColumn("Pushing to remote..."), console=console) as progress:
        task = progress.add_task("Pushing...", total=1)
        result = manager._run_git_command(push_cmd)
        progress.update(task, completed=1)
    
    if result.returncode == 0:
        console.print(f"✅ Pushed {status['ahead_behind']['ahead']} commits to origin/{status['branch']}")
    else:
        if "rejected" in result.stderr:
            console.print("🔄 Push rejected - remote has newer commits")
            if Confirm.ask("Pull and retry?"):
                # Pull first
                pull_result = manager._run_git_command(["pull", "--rebase"])
                if pull_result.returncode == 0:
                    # Retry push
                    retry_result = manager._run_git_command(push_cmd)
                    if retry_result.returncode == 0:
                        console.print("✅ Push successful after pull")
                    else:
                        console.print(f"❌ Push still failed: {retry_result.stderr}")
                else:
                    console.print(f"❌ Pull failed: {pull_result.stderr}")
        else:
            console.print(f"❌ Push failed: {result.stderr}")
            raise typer.Exit(1)


@app.command()
def auto(
    push_after: bool = typer.Option(None, "--push/--no-push", help="Push after commit"),
    message: Optional[str] = typer.Option(None, "-m", "--message", help="Custom commit message")
):
    """Complete automated git workflow: add + commit + push"""
    manager = GitAutoManager()
    
    console.print("🤖 AUTOMATED GIT WORKFLOW")
    console.print("=" * 30)
    
    # Step 1: Add all files
    console.print("📁 Step 1: Adding files...")
    add_result = manager._run_git_command(["add", "."])
    if add_result.returncode != 0:
        console.print(f"❌ Add failed: {add_result.stderr}")
        raise typer.Exit(1)
    
    status = manager.get_repo_status()
    console.print(f"✅ Added {len(status['staged_files'])} files")
    
    if not status["staged_files"]:
        console.print("ℹ️ No changes to commit")
        return
    
    # Step 2: Validate
    console.print("🔍 Step 2: Pre-commit validation...")
    if not manager.validate_pre_commit():
        console.print("❌ Validation failed")
        raise typer.Exit(1)
    console.print("✅ Validation passed")
    
    # Step 3: Commit
    console.print("💾 Step 3: Creating commit...")
    if not message:
        message = manager.generate_smart_commit_message(status)
    
    if message:
        console.print(f"📝 Message: {message.split(chr(10))[0]}")
    
    commit_result = manager._run_git_command(["commit", "-m", message or "Auto commit"])
    if commit_result.returncode != 0:
        console.print(f"❌ Commit failed: {commit_result.stderr}")
        raise typer.Exit(1)
    
    # Get commit hash
    hash_result = manager._run_git_command(["rev-parse", "--short", "HEAD"])
    commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
    console.print(f"✅ Commit: {commit_hash}")
    
    # Step 4: Push (if requested or configured)
    should_push = push_after if push_after is not None else manager.config.get("auto_push", False)
    
    if should_push:
        console.print("📤 Step 4: Pushing to remote...")
        
        # Check if we need to set upstream
        upstream_result = manager._run_git_command(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
        needs_upstream = upstream_result.returncode != 0
        
        push_cmd = ["push"]
        if needs_upstream:
            push_cmd.extend(["--set-upstream", "origin", status["branch"]])
        
        push_result = manager._run_git_command(push_cmd)
        if push_result.returncode == 0:
            console.print(f"✅ Pushed to origin/{status['branch']}")
        else:
            console.print(f"❌ Push failed: {push_result.stderr}")
            # Don't exit on push failure - commit was successful
    
    console.print("🎉 Automated workflow completed!")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: Optional[str] = typer.Option(None, "--set", help="Set configuration key"),
    value: Optional[str] = typer.Option(None, "--value", help="Configuration value"),
    reset: bool = typer.Option(False, "--reset", help="Reset to defaults")
):
    """Manage git auto configuration"""
    manager = GitAutoManager()
    config_file = manager.repo_root / ".git_auto_config.json"
    
    if show:
        console.print("⚙️ Git Auto Configuration:")
        for key, val in manager.config.items():
            console.print(f"  {key}: {val}")
        return
    
    if reset:
        if config_file.exists():
            config_file.unlink()
        console.print("✅ Configuration reset to defaults")
        return
    
    if set_key and value:
        # Parse value as JSON if possible
        try:
            parsed_value = json.loads(value)
        except:
            parsed_value = value
        
        manager.config[set_key] = parsed_value
        
        # Save configuration
        with open(config_file, "w") as f:
            json.dump(manager.config, f, indent=2)
        
        console.print(f"✅ Set {set_key} = {parsed_value}")
        return
    
    console.print("Usage: --show, --set KEY --value VALUE, or --reset")


if __name__ == "__main__":
    app()