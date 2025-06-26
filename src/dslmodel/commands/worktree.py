#!/usr/bin/env python3
"""
Git Worktree CLI - Exclusive worktree-based development

This CLI enforces a worktree-only development workflow where each feature,
experiment, or task gets its own isolated worktree.

Philosophy: Never work directly on main branch, always use worktrees.
"""

import typer
from pathlib import Path
from typing import Optional, List
import subprocess
import json
from loguru import logger
from rich.table import Table
from rich.console import Console

from ..utils.json_output import json_command

app = typer.Typer(help="Git worktree management for exclusive worktree development")
console = Console()


def run_git_command(cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a git command and return the result"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {' '.join(cmd)}")
        logger.error(f"Error: {e.stderr}")
        raise typer.Exit(1)


def get_main_repo_path() -> Path:
    """Get the path to the main repository"""
    try:
        result = run_git_command(["rev-parse", "--git-dir"])
        git_dir = Path(result.stdout.strip())
        if git_dir.name == ".git":
            return git_dir.parent
        else:
            # This is likely a worktree, find the main repo
            result = run_git_command(["rev-parse", "--show-toplevel"])
            return Path(result.stdout.strip())
    except Exception:
        return Path.cwd()


def list_worktrees() -> List[dict]:
    """List all worktrees with details"""
    try:
        result = run_git_command(["worktree", "list", "--porcelain"])
        worktrees = []
        current_worktree = {}
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('worktree '):
                if current_worktree:
                    worktrees.append(current_worktree)
                current_worktree = {'path': line[9:]}
            elif line.startswith('HEAD '):
                current_worktree['commit'] = line[5:]
            elif line.startswith('branch '):
                current_worktree['branch'] = line[7:]
            elif line.startswith('bare'):
                current_worktree['bare'] = True
            elif line.startswith('detached'):
                current_worktree['detached'] = True
        
        if current_worktree:
            worktrees.append(current_worktree)
        
        return worktrees
    except Exception:
        return []


@app.command("list")
def list_command():
    """List all worktrees"""
    
    with json_command("worktree-list") as formatter:
        try:
            worktrees = list_worktrees()
            formatter.add_data("worktrees_count", len(worktrees))
            formatter.add_data("worktrees", worktrees)
            
            if worktrees:
                table = Table(title="Git Worktrees")
                table.add_column("Path", style="cyan")
                table.add_column("Branch", style="green")
                table.add_column("Status", style="yellow")
                table.add_column("Commit", style="blue")
                
                for wt in worktrees:
                    path = Path(wt['path']).name
                    branch = wt.get('branch', 'N/A')
                    if wt.get('bare'):
                        status = "📁 Bare"
                    elif wt.get('detached'):
                        status = "🔗 Detached"
                    else:
                        status = "✅ Active"
                    commit = wt.get('commit', 'N/A')[:8] if wt.get('commit') else 'N/A'
                    
                    table.add_row(path, branch, status, commit)
                
                console.print(table)
                formatter.print(f"\n📊 Total worktrees: {len(worktrees)}")
            else:
                formatter.print("No worktrees found")
        
        except Exception as e:
            formatter.add_error(f"Failed to list worktrees: {e}")
            formatter.print(f"❌ Failed to list worktrees: {e}")
            raise typer.Exit(1)


@app.command("create")
def create_worktree(
    branch_name: str = typer.Argument(..., help="Name of the branch/worktree"),
    base_branch: str = typer.Option("main", "--base", "-b", help="Base branch to create from"),
    feature_type: str = typer.Option("feature", "--type", "-t", help="Type of work (feature, bugfix, experiment, refactor)"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description of the work")
):
    """Create a new worktree for isolated development"""
    
    with json_command("worktree-create") as formatter:
        formatter.add_data("branch_name", branch_name)
        formatter.add_data("base_branch", base_branch)
        formatter.add_data("feature_type", feature_type)
        
        try:
            # Get main repo path
            main_repo = get_main_repo_path()
            
            # Create worktree directory structure
            worktrees_root = main_repo.parent / "worktrees"
            worktree_path = worktrees_root / f"{feature_type}_{branch_name}"
            
            # Ensure worktrees directory exists
            worktrees_root.mkdir(exist_ok=True)
            
            formatter.add_data("worktree_path", str(worktree_path))
            
            # Create the worktree
            formatter.print(f"🌳 Creating worktree: {feature_type}_{branch_name}")
            formatter.print(f"📁 Path: {worktree_path}")
            formatter.print(f"🔗 Base: {base_branch}")
            
            # Check if branch already exists
            try:
                run_git_command(["show-ref", "--verify", f"refs/heads/{branch_name}"], cwd=main_repo)
                # Branch exists, check it out
                run_git_command([
                    "worktree", "add", str(worktree_path), branch_name
                ], cwd=main_repo)
                formatter.print(f"✅ Checked out existing branch: {branch_name}")
            except subprocess.CalledProcessError:
                # Branch doesn't exist, create it
                run_git_command([
                    "worktree", "add", "-b", branch_name, str(worktree_path), base_branch
                ], cwd=main_repo)
                formatter.print(f"✅ Created new branch: {branch_name}")
            
            # Create a .worktree-info file
            info_file = worktree_path / ".worktree-info"
            info_data = {
                "branch_name": branch_name,
                "base_branch": base_branch,
                "feature_type": feature_type,
                "description": description,
                "created_at": "now",
                "main_repo": str(main_repo)
            }
            
            with open(info_file, 'w') as f:
                json.dump(info_data, f, indent=2)
            
            formatter.add_data("info_file", str(info_file))
            formatter.add_data("creation_successful", True)
            
            # Instructions
            formatter.print(f"\n🎯 Worktree created successfully!")
            formatter.print(f"Next steps:")
            formatter.print(f"  1. cd {worktree_path}")
            formatter.print(f"  2. Start development on {branch_name}")
            formatter.print(f"  3. Use 'dsl worktree status' to check progress")
            formatter.print(f"  4. Use 'dsl worktree remove {branch_name}' when done")
            
            # Add to shell command for easy switching
            formatter.print(f"\n💡 Quick switch command:")
            formatter.print(f"  cd {worktree_path}")
        
        except Exception as e:
            formatter.add_error(f"Failed to create worktree: {e}")
            formatter.print(f"❌ Failed to create worktree: {e}")
            raise typer.Exit(1)


@app.command("remove")
def remove_worktree(
    branch_name: str = typer.Argument(..., help="Name of the branch/worktree to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal even with uncommitted changes")
):
    """Remove a worktree and optionally its branch"""
    
    with json_command("worktree-remove") as formatter:
        formatter.add_data("branch_name", branch_name)
        formatter.add_data("force", force)
        
        try:
            # Find the worktree
            worktrees = list_worktrees()
            target_worktree = None
            
            for wt in worktrees:
                if wt.get('branch') == f"refs/heads/{branch_name}" or Path(wt['path']).name.endswith(branch_name):
                    target_worktree = wt
                    break
            
            if not target_worktree:
                formatter.print(f"❌ Worktree for branch '{branch_name}' not found")
                formatter.add_data("removal_successful", False)
                raise typer.Exit(1)
            
            worktree_path = Path(target_worktree['path'])
            formatter.add_data("worktree_path", str(worktree_path))
            
            # Remove the worktree
            formatter.print(f"🗑️  Removing worktree: {worktree_path}")
            
            cmd = ["worktree", "remove"]
            if force:
                cmd.append("--force")
            cmd.append(str(worktree_path))
            
            run_git_command(cmd)
            
            # Ask about branch removal
            if not force:
                remove_branch = typer.confirm(f"Also delete branch '{branch_name}'?")
                if remove_branch:
                    try:
                        run_git_command(["branch", "-d", branch_name])
                        formatter.print(f"✅ Deleted branch: {branch_name}")
                    except subprocess.CalledProcessError:
                        formatter.print(f"⚠️  Branch '{branch_name}' has unmerged changes")
                        force_delete = typer.confirm("Force delete anyway?")
                        if force_delete:
                            run_git_command(["branch", "-D", branch_name])
                            formatter.print(f"✅ Force deleted branch: {branch_name}")
            
            formatter.add_data("removal_successful", True)
            formatter.print(f"✅ Worktree removed successfully")
        
        except Exception as e:
            formatter.add_error(f"Failed to remove worktree: {e}")
            formatter.print(f"❌ Failed to remove worktree: {e}")
            raise typer.Exit(1)


@app.command("status")
def status():
    """Show status of all worktrees"""
    
    with json_command("worktree-status") as formatter:
        try:
            worktrees = list_worktrees()
            formatter.add_data("worktrees_count", len(worktrees))
            
            if not worktrees:
                formatter.print("No worktrees found")
                return
            
            formatter.print("🌳 Worktree Status Report")
            formatter.print("=" * 50)
            
            current_path = str(Path.cwd())
            
            for i, wt in enumerate(worktrees, 1):
                path = Path(wt['path'])
                is_current = str(path) == current_path
                
                formatter.print(f"\n{i}. {path.name}")
                formatter.print(f"   📁 Path: {path}")
                formatter.print(f"   🔗 Branch: {wt.get('branch', 'N/A')}")
                formatter.print(f"   📊 Status: {'🎯 CURRENT' if is_current else '💤 Inactive'}")
                
                # Check git status in this worktree
                try:
                    status_result = run_git_command(["status", "--porcelain"], cwd=path)
                    if status_result.stdout.strip():
                        lines = len(status_result.stdout.strip().split('\n'))
                        formatter.print(f"   ⚠️  Uncommitted changes: {lines} files")
                    else:
                        formatter.print(f"   ✅ Clean working directory")
                except Exception:
                    formatter.print(f"   ❓ Cannot check status")
                
                # Check for .worktree-info
                info_file = path / ".worktree-info"
                if info_file.exists():
                    try:
                        with open(info_file, 'r') as f:
                            info = json.load(f)
                        formatter.print(f"   🏷️  Type: {info.get('feature_type', 'unknown')}")
                        if info.get('description'):
                            formatter.print(f"   📝 Desc: {info['description']}")
                    except Exception:
                        pass
            
            # Summary
            formatter.print(f"\n📊 Summary: {len(worktrees)} worktrees")
            main_repo = get_main_repo_path()
            formatter.print(f"🏠 Main repo: {main_repo}")
            
        except Exception as e:
            formatter.add_error(f"Failed to get status: {e}")
            formatter.print(f"❌ Failed to get status: {e}")
            raise typer.Exit(1)


@app.command("switch")
def switch_worktree(
    branch_name: str = typer.Argument(..., help="Branch/worktree name to switch to")
):
    """Get the command to switch to a specific worktree"""
    
    with json_command("worktree-switch") as formatter:
        formatter.add_data("branch_name", branch_name)
        
        try:
            worktrees = list_worktrees()
            target_worktree = None
            
            for wt in worktrees:
                path_name = Path(wt['path']).name
                branch = wt.get('branch', '')
                if (branch_name in path_name or 
                    branch.endswith(f"/{branch_name}") or
                    branch == f"refs/heads/{branch_name}"):
                    target_worktree = wt
                    break
            
            if not target_worktree:
                formatter.print(f"❌ Worktree for '{branch_name}' not found")
                formatter.print("Available worktrees:")
                for wt in worktrees:
                    formatter.print(f"  - {Path(wt['path']).name}")
                formatter.add_data("switch_successful", False)
                raise typer.Exit(1)
            
            worktree_path = target_worktree['path']
            formatter.add_data("worktree_path", worktree_path)
            formatter.add_data("switch_successful", True)
            
            # Print the command to switch
            formatter.print(f"💡 To switch to worktree '{branch_name}':")
            formatter.print(f"cd {worktree_path}")
            
            # Also save to a temp file for easy sourcing
            switch_file = Path.home() / ".dsl_worktree_switch"
            with open(switch_file, 'w') as f:
                f.write(f"cd {worktree_path}\n")
            
            formatter.print(f"\n🔄 Or run: source ~/.dsl_worktree_switch")
        
        except Exception as e:
            formatter.add_error(f"Failed to switch: {e}")
            formatter.print(f"❌ Failed to switch: {e}")
            raise typer.Exit(1)


@app.command("init")
def init_worktree_workflow():
    """Initialize exclusive worktree development workflow"""
    
    with json_command("worktree-init") as formatter:
        try:
            main_repo = get_main_repo_path()
            worktrees_root = main_repo.parent / "worktrees"
            
            formatter.print("🌳 Initializing Exclusive Worktree Development")
            formatter.print("=" * 50)
            
            # Create worktrees directory
            worktrees_root.mkdir(exist_ok=True)
            formatter.print(f"📁 Created worktrees directory: {worktrees_root}")
            
            # Create initial development worktree
            current_branch = run_git_command(["branch", "--show-current"], cwd=main_repo).stdout.strip()
            
            if current_branch == "main":
                formatter.print("⚠️  You're on main branch - creating development worktree")
                
                # Create a dev worktree
                dev_path = worktrees_root / "feature_development"
                if not dev_path.exists():
                    run_git_command([
                        "worktree", "add", "-b", "development", str(dev_path), "main"
                    ], cwd=main_repo)
                    formatter.print(f"✅ Created development worktree: {dev_path}")
            
            # Create configuration
            config = {
                "worktree_root": str(worktrees_root),
                "main_repo": str(main_repo),
                "workflow": "exclusive_worktree",
                "auto_cleanup": True,
                "default_base": "main"
            }
            
            config_file = main_repo / ".worktree-config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            formatter.add_data("config", config)
            formatter.add_data("init_successful", True)
            
            # Instructions
            formatter.print("\n🎯 Worktree workflow initialized!")
            formatter.print("Best practices:")
            formatter.print("  1. Never work directly on main branch")
            formatter.print("  2. Create worktree for each feature: dsl worktree create <name>")
            formatter.print("  3. Switch between worktrees: dsl worktree switch <name>")
            formatter.print("  4. Clean up when done: dsl worktree remove <name>")
            
            formatter.print(f"\n📚 Commands:")
            formatter.print(f"  dsl worktree list        - Show all worktrees")
            formatter.print(f"  dsl worktree create      - Create new worktree")
            formatter.print(f"  dsl worktree status      - Show detailed status")
            formatter.print(f"  dsl worktree switch      - Get switch command")
            formatter.print(f"  dsl worktree remove      - Remove worktree")
        
        except Exception as e:
            formatter.add_error(f"Failed to initialize: {e}")
            formatter.print(f"❌ Failed to initialize: {e}")
            raise typer.Exit(1)


@app.command("clean")
def clean_worktrees():
    """Clean up merged/stale worktrees"""
    
    with json_command("worktree-clean") as formatter:
        try:
            formatter.print("🧹 Cleaning up worktrees...")
            
            # List worktrees
            worktrees = list_worktrees()
            cleaned = 0
            
            for wt in worktrees:
                path = Path(wt['path'])
                branch = wt.get('branch', '')
                
                # Skip main worktree
                if 'main' in str(path) or not branch:
                    continue
                
                # Check if branch is merged
                try:
                    branch_name = branch.replace('refs/heads/', '')
                    result = run_git_command(["branch", "--merged", "main"], cwd=path)
                    
                    if branch_name in result.stdout:
                        formatter.print(f"🗑️  Found merged branch: {branch_name}")
                        
                        # Check if working directory is clean
                        status_result = run_git_command(["status", "--porcelain"], cwd=path)
                        if not status_result.stdout.strip():
                            # Safe to remove
                            if typer.confirm(f"Remove merged worktree '{branch_name}'?"):
                                run_git_command(["worktree", "remove", str(path)])
                                run_git_command(["branch", "-d", branch_name])
                                formatter.print(f"✅ Removed: {branch_name}")
                                cleaned += 1
                        else:
                            formatter.print(f"⚠️  Skipping {branch_name} - has uncommitted changes")
                
                except Exception as e:
                    formatter.print(f"⚠️  Error checking {path}: {e}")
            
            formatter.add_data("worktrees_cleaned", cleaned)
            formatter.print(f"\n✅ Cleanup complete: {cleaned} worktrees removed")
        
        except Exception as e:
            formatter.add_error(f"Failed to clean: {e}")
            formatter.print(f"❌ Failed to clean: {e}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()