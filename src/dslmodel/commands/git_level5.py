"""
Git Level-5 Operations for Rich-Git Substrate
Implements advanced Git primitives for federation-ready AHI cells
"""

import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from opentelemetry import trace
from opentelemetry.trace import Span
import typer
from rich.console import Console
from rich.table import Table

from dslmodel.utils.source_tools import git_wrap
from dslmodel.core.weaver_engine import WeaverEngine

console = Console()
tracer = trace.get_tracer(__name__)

class GitLevel5:
    """Advanced Git operations for Level-5 AHI cell substrate"""
    
    def __init__(self, registry_path: str = "git_registry.yaml"):
        self.registry_path = registry_path
        self.registry = self._load_registry()
        self.weaver = WeaverEngine()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load Git registry configuration"""
        try:
            with open(self.registry_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            console.print(f"[yellow]Registry {self.registry_path} not found, using defaults[/yellow]")
            return {}
    
    def _emit_span(self, span_name: str, attributes: Dict[str, Any]) -> str:
        """Emit telemetry span for Git operation"""
        with tracer.start_as_current_span(span_name) as span:
            for key, value in attributes.items():
                span.set_attribute(key, value)
            return span.get_span_context().trace_id

    # Data-layer superpowers
    @git_wrap("worktree")
    def add_worktree(self, path: str, sha: str = "HEAD") -> bool:
        """Add worktree for tick isolation and WASI builds"""
        try:
            result = subprocess.run(
                ["git", "worktree", "add", path, sha],
                capture_output=True, text=True, check=True
            )
            
            self._emit_span("git.worktree.lifecycle", {
                "git.worktree.path": path,
                "git.worktree.sha": sha,
                "git.worktree.operation": "add"
            })
            
            console.print(f"✅ Worktree created at {path}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Worktree creation failed: {e}")
            return False

    @git_wrap("sparse_checkout")
    def enable_sparse_checkout(self, patterns: List[str]) -> bool:
        """Enable sparse checkout for agent clone optimization"""
        try:
            # Enable sparse checkout
            subprocess.run(["git", "config", "core.sparseCheckout", "true"], check=True)
            
            # Write patterns to sparse-checkout file
            sparse_file = Path(".git/info/sparse-checkout")
            sparse_file.parent.mkdir(exist_ok=True)
            sparse_file.write_text("\n".join(patterns))
            
            # Apply sparse checkout
            subprocess.run(["git", "read-tree", "-m", "-u", "HEAD"], check=True)
            
            self._emit_span("git.checkout", {
                "git.checkout.sparse": True,
                "git.checkout.patterns": patterns
            })
            
            console.print(f"✅ Sparse checkout enabled with patterns: {patterns}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Sparse checkout failed: {e}")
            return False

    @git_wrap("partial_clone")
    def partial_clone(self, url: str, dst: str, depth: int = 1) -> bool:
        """Perform partial clone for edge node optimization"""
        try:
            result = subprocess.run([
                "git", "clone", "--filter=blob:none", f"--depth={depth}", url, dst
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.clone", {
                "git.clone.url": url,
                "git.clone.destination": dst,
                "git.clone.shallow": True,
                "git.clone.filter": "blob:none",
                "git.clone.depth": depth
            })
            
            console.print(f"✅ Partial clone completed: {url} → {dst}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Partial clone failed: {e}")
            return False

    # Collaboration & federation
    @git_wrap("submodule_add")
    def add_domain_pack(self, url: str, name: str, path: Optional[str] = None) -> bool:
        """Add domain pack as submodule for federation"""
        if not path:
            path = f"domain_packs/{name}"
            
        try:
            result = subprocess.run([
                "git", "submodule", "add", url, path
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.submodule.update", {
                "git.submodule.url": url,
                "git.submodule.path": path,
                "git.submodule.operation": "add",
                "federation.domain_pack": name
            })
            
            console.print(f"✅ Domain pack added: {name} at {path}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Domain pack addition failed: {e}")
            return False

    @git_wrap("submodule_update")
    def update_submodules(self, recursive: bool = True) -> bool:
        """Update all submodules for federation sync"""
        try:
            cmd = ["git", "submodule", "update", "--init"]
            if recursive:
                cmd.append("--recursive")
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self._emit_span("git.submodule.update", {
                "git.submodule.operation": "update",
                "git.submodule.recursive": recursive
            })
            
            console.print("✅ Submodules updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Submodule update failed: {e}")
            return False

    @git_wrap("remote_add")
    def add_federation_remote(self, name: str, url: str) -> bool:
        """Add federation remote for multi-org collaboration"""
        try:
            result = subprocess.run([
                "git", "remote", "add", name, url
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.remote", {
                "git.remote.name": name,
                "git.remote.url": url,
                "git.remote.operation": "add",
                "federation.peer": True
            })
            
            console.print(f"✅ Federation remote added: {name}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Remote addition failed: {e}")
            return False

    # Workflow & history manipulation
    @git_wrap("cherry_pick")
    def promote_agent_patch(self, commit: str, target_branch: str = "main") -> bool:
        """Cherry-pick agent patch to hot-fix branch"""
        try:
            # Switch to target branch
            subprocess.run(["git", "checkout", target_branch], check=True)
            
            # Cherry-pick the commit
            result = subprocess.run([
                "git", "cherry-pick", commit
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.merge", {
                "git.merge.strategy": "cherry-pick",
                "git.merge.commit": commit,
                "git.merge.target_branch": target_branch
            })
            
            console.print(f"✅ Agent patch promoted: {commit} → {target_branch}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Cherry-pick failed: {e}")
            return False

    @git_wrap("rebase_merges")
    def linearize_merge_oracle(self, onto: str) -> bool:
        """Rebase with merge preservation for MergeOracle output"""
        try:
            result = subprocess.run([
                "git", "rebase", "--rebase-merges", onto
            ], capture_output=True, text=True, check=True)
            
            # Count commits in rebase
            commits_result = subprocess.run([
                "git", "rev-list", "--count", f"{onto}..HEAD"
            ], capture_output=True, text=True, check=True)
            commits_replayed = int(commits_result.stdout.strip())
            
            self._emit_span("git.rebase", {
                "git.rebase.strategy": "rebase-merges",
                "git.rebase.onto_sha": onto,
                "git.rebase.commits_replayed": commits_replayed,
                "git.rebase.merge_oracle_optimized": True
            })
            
            console.print(f"✅ MergeOracle output linearized onto {onto}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Rebase failed: {e}")
            return False

    @git_wrap("reset_keep")
    def sandbox_rollback(self, sha: str) -> bool:
        """Rollback to safe state while preserving working tree"""
        try:
            # Get current SHA for logging
            current_result = subprocess.run([
                "git", "rev-parse", "HEAD"
            ], capture_output=True, text=True, check=True)
            from_sha = current_result.stdout.strip()
            
            result = subprocess.run([
                "git", "reset", "--keep", sha
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.reset", {
                "git.reset.mode": "keep",
                "git.reset.to_sha": sha,
                "git.reset.from_sha": from_sha,
                "git.reset.reason": "sandbox_failure",
                "sandbox.failure_recovery": True,
                "git.reset.preserve_working_tree": True
            })
            
            console.print(f"✅ Sandbox rolled back to {sha}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Reset failed: {e}")
            return False

    # Security & provenance  
    def sign_commit(self, message: str, key_id: Optional[str] = None) -> bool:
        """Create GPG-signed commit for provenance"""
        try:
            cmd = ["git", "commit", "-S"]
            if key_id:
                cmd.extend(["-u", key_id])
            cmd.extend(["-m", message])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self._emit_span("compliance.gpg.signature", {
                "compliance.signature.type": "commit",
                "compliance.signature.message": message,
                "compliance.signature.key_id": key_id
            })
            
            console.print(f"✅ Signed commit created: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Signed commit failed: {e}")
            return False

    def sign_tag(self, tag: str, message: str, key_id: Optional[str] = None) -> bool:
        """Create GPG-signed tag for release provenance"""
        try:
            cmd = ["git", "tag", "-s", tag]
            if key_id:
                cmd.extend(["-u", key_id])
            cmd.extend(["-m", message])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self._emit_span("compliance.gpg.signature", {
                "compliance.signature.type": "tag",
                "compliance.signature.tag": tag,
                "compliance.signature.message": message,
                "compliance.signature.key_id": key_id
            })
            
            console.print(f"✅ Signed tag created: {tag}")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Signed tag failed: {e}")
            return False

    # Maintenance & performance
    def nightly_maintenance(self) -> bool:
        """Run aggressive GC for nightly repo optimization"""
        try:
            result = subprocess.run([
                "git", "gc", "--aggressive", "--prune=now"
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.gc", {
                "git.gc.aggressive": True,
                "git.gc.prune": True,
                "git.gc.scheduled": True
            })
            
            console.print("✅ Nightly maintenance completed")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Maintenance failed: {e}")
            return False

    def optimize_federation(self) -> bool:
        """Optimize repository for federation peer access"""
        try:
            result = subprocess.run([
                "git", "repack", "-adb", "--write-bitmaps"
            ], capture_output=True, text=True, check=True)
            
            self._emit_span("git.gc", {
                "git.gc.bitmaps": True,
                "git.gc.federation_optimized": True
            })
            
            console.print("✅ Federation optimization completed")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Federation optimization failed: {e}")
            return False

    # Installation and validation hooks
    def install_validation_hook(self, hook_type: str, script_content: str) -> bool:
        """Install Git hook for validation pipeline"""
        try:
            hook_path = Path(f".git/hooks/{hook_type}")
            hook_path.write_text(script_content)
            hook_path.chmod(0o755)
            
            self._emit_span("git.hook.run", {
                "git.hook.type": hook_type,
                "git.hook.operation": "install",
                "git.hook.validation_type": "forge"
            })
            
            console.print(f"✅ Validation hook installed: {hook_type}")
            return True
            
        except Exception as e:
            console.print(f"❌ Hook installation failed: {e}")
            return False

    def run_validation_hook(self, hook_type: str) -> bool:
        """Execute validation hook and emit telemetry"""
        hook_path = Path(f".git/hooks/{hook_type}")
        if not hook_path.exists():
            console.print(f"❌ Hook not found: {hook_type}")
            return False
            
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run([str(hook_path)], capture_output=True, text=True)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            self._emit_span("git.hook.run", {
                "git.hook.type": hook_type,
                "git.hook.exit_code": result.returncode,
                "git.hook.duration_ms": duration_ms,
                "git.hook.validation_type": "automated"
            })
            
            if result.returncode == 0:
                console.print(f"✅ Hook executed successfully: {hook_type}")
                return True
            else:
                console.print(f"❌ Hook failed: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Hook execution failed: {e}")
            return False

    # Status and reporting
    def federation_status(self) -> Dict[str, Any]:
        """Get comprehensive federation status"""
        status = {
            "remotes": [],
            "submodules": [],
            "worktrees": [],
            "hooks": []
        }
        
        try:
            # Get remotes
            remotes_result = subprocess.run([
                "git", "remote", "-v"
            ], capture_output=True, text=True)
            if remotes_result.returncode == 0:
                for line in remotes_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            status["remotes"].append({
                                "name": parts[0],
                                "url": parts[1]
                            })
            
            # Get submodules
            submodules_result = subprocess.run([
                "git", "submodule", "status"
            ], capture_output=True, text=True)
            if submodules_result.returncode == 0:
                for line in submodules_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            status["submodules"].append({
                                "sha": parts[0].lstrip('+-'),
                                "path": parts[1]
                            })
            
            # Get worktrees
            worktrees_result = subprocess.run([
                "git", "worktree", "list"
            ], capture_output=True, text=True)
            if worktrees_result.returncode == 0:
                for line in worktrees_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            status["worktrees"].append({
                                "path": parts[0],
                                "branch": parts[1] if len(parts) > 1 else "detached"
                            })
            
            # Check hooks
            hooks_dir = Path(".git/hooks")
            if hooks_dir.exists():
                for hook_file in hooks_dir.glob("*"):
                    if hook_file.is_file() and hook_file.stat().st_mode & 0o111:
                        status["hooks"].append(hook_file.name)
                        
        except Exception as e:
            console.print(f"⚠️ Error gathering federation status: {e}")
            
        return status

    def display_federation_status(self):
        """Display rich federation status table"""
        status = self.federation_status()
        
        # Remotes table
        if status["remotes"]:
            remotes_table = Table(title="Federation Remotes")
            remotes_table.add_column("Name", style="cyan")
            remotes_table.add_column("URL", style="green")
            
            for remote in status["remotes"]:
                remotes_table.add_row(remote["name"], remote["url"])
            
            console.print(remotes_table)
        
        # Submodules table
        if status["submodules"]:
            submodules_table = Table(title="Domain Packs (Submodules)")
            submodules_table.add_column("Path", style="cyan")
            submodules_table.add_column("SHA", style="yellow")
            
            for submodule in status["submodules"]:
                submodules_table.add_row(submodule["path"], submodule["sha"][:8])
            
            console.print(submodules_table)
        
        # Worktrees table
        if status["worktrees"]:
            worktrees_table = Table(title="Active Worktrees")
            worktrees_table.add_column("Path", style="cyan")
            worktrees_table.add_column("Branch", style="green")
            
            for worktree in status["worktrees"]:
                worktrees_table.add_row(worktree["path"], worktree["branch"])
            
            console.print(worktrees_table)
        
        # Hooks summary
        if status["hooks"]:
            console.print(f"\n✅ Active Hooks: {', '.join(status['hooks'])}")
        else:
            console.print("\n⚠️ No validation hooks installed")


# CLI interface
app = typer.Typer(name="git-level5", help="Git Level-5 operations for rich-git substrate")
git_l5 = GitLevel5()

@app.command()
def status():
    """Show federation and Level-5 Git status"""
    git_l5.display_federation_status()

@app.command()
def add_domain_pack(url: str, name: str, path: Optional[str] = None):
    """Add domain pack as submodule"""
    git_l5.add_domain_pack(url, name, path)

@app.command()
def install_hooks():
    """Install standard validation hooks"""
    pre_commit_script = """#!/bin/bash
set -e
echo "🔧 Running forge validation..."
forge validate || exit 1
echo "🎯 Running ruff checks..."
ruff check --fix . || exit 1
echo "✅ Pre-commit validation passed"
"""
    
    pre_push_script = """#!/bin/bash
set -e
echo "🔧 Running Weaver validation..."
weaver registry check || exit 1
echo "🎯 Running health analysis..."
dsl health-8020 analyze || exit 1
echo "✅ Pre-push validation passed"
"""
    
    git_l5.install_validation_hook("pre-commit", pre_commit_script)
    git_l5.install_validation_hook("pre-push", pre_push_script)

@app.command()
def maintenance():
    """Run nightly maintenance and optimization"""
    git_l5.nightly_maintenance()
    git_l5.optimize_federation()

if __name__ == "__main__":
    app()