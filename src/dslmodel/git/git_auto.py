"""
Git Auto - Level-5 Git-Native Substrate
Advanced Git operations with OTEL spans and autonomous capabilities
"""

import subprocess
import asyncio
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json
import tempfile
import os
from functools import wraps

try:
    from ..otel.otel_instrumentation_mock import SwarmSpanAttributes
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    SwarmSpanAttributes = None


@dataclass
class GitOperation:
    """Represents a Git operation from the registry."""
    name: str
    cmd: str
    span: str
    attributes: Dict[str, Any]
    cwd_arg: Optional[str] = None


class GitRegistry:
    """Git operation registry loader and manager."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            registry_path = Path(__file__).parent.parent.parent.parent / "weaver" / "git_registry.yaml"
        
        self.registry_path = registry_path
        self.operations: Dict[str, GitOperation] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load Git operations from YAML registry."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Git registry not found at {self.registry_path}")
        
        with open(self.registry_path, 'r') as f:
            registry_data = yaml.safe_load(f)
        
        for op_name, op_config in registry_data.items():
            if isinstance(op_config, dict) and 'cmd' in op_config:
                self.operations[op_name] = GitOperation(
                    name=op_name,
                    cmd=op_config['cmd'],
                    span=op_config.get('span', 'git.operation'),
                    attributes=op_config.get('attributes', {}),
                    cwd_arg=op_config.get('cwd_arg')
                )
    
    def get_operation(self, name: str) -> Optional[GitOperation]:
        """Get a Git operation by name."""
        return self.operations.get(name)
    
    def list_operations(self) -> List[str]:
        """List all available operations."""
        return list(self.operations.keys())


def git_wrap(operation_name: str, registry: Optional[GitRegistry] = None):
    """Decorator to wrap functions with Git operation execution and OTEL spans."""
    if registry is None:
        registry = GitRegistry()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            operation = registry.get_operation(operation_name)
            if not operation:
                raise ValueError(f"Git operation '{operation_name}' not found in registry")
            
            # Extract parameters from function arguments
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            params = bound_args.arguments
            
            # Format command with parameters
            try:
                formatted_cmd = operation.cmd.format(**params)
            except KeyError as e:
                raise ValueError(f"Missing parameter for Git operation '{operation_name}': {e}")
            
            # Set working directory
            cwd = params.get('cwd', os.getcwd())
            if operation.cwd_arg:
                cwd = params.get(operation.cwd_arg, cwd)
            
            # Execute with OTEL span if available
            if OTEL_AVAILABLE and SwarmSpanAttributes:
                return await execute_with_span(
                    formatted_cmd, 
                    operation.span, 
                    operation.attributes, 
                    cwd,
                    params
                )
            else:
                return await execute_git_command(formatted_cmd, cwd)
        
        return wrapper
    return decorator


async def execute_with_span(cmd: str, span_name: str, attributes: Dict, cwd: str, params: Dict) -> Dict[str, Any]:
    """Execute Git command with OTEL span tracking."""
    span_attrs = SwarmSpanAttributes()
    
    # Set base attributes
    span_attrs.set_attribute("git.command", cmd)
    span_attrs.set_attribute("git.working_directory", cwd)
    
    # Set operation-specific attributes
    for key, value in attributes.items():
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            # Replace parameter placeholders
            param_name = value[1:-1]
            if param_name in params:
                span_attrs.set_attribute(f"git.{key}", params[param_name])
        else:
            span_attrs.set_attribute(f"git.{key}", value)
    
    # Execute command
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        span_attrs.set_attribute("git.exit_code", process.returncode)
        
        result = {
            "success": process.returncode == 0,
            "exit_code": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "command": cmd,
            "cwd": cwd
        }
        
        if not result["success"]:
            span_attrs.set_attribute("git.error", result["stderr"])
        
        return result
        
    except Exception as e:
        span_attrs.set_attribute("git.error", str(e))
        span_attrs.set_attribute("git.exit_code", -1)
        raise


async def execute_git_command(cmd: str, cwd: str) -> Dict[str, Any]:
    """Execute Git command without OTEL (fallback)."""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "exit_code": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "command": cmd,
            "cwd": cwd
        }
        
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "command": cmd,
            "cwd": cwd
        }


# =============================================================================
# Level-5 Git Wrapper Functions
# =============================================================================

# Initialize registry
_registry = GitRegistry()

# Data-layer superpowers
@git_wrap("worktree_add", _registry)
async def add_worktree(path: str, sha: str, cwd: Optional[str] = None):
    """Add a new worktree for tick isolation."""
    pass

@git_wrap("worktree_remove", _registry)
async def remove_worktree(path: str, cwd: Optional[str] = None):
    """Remove a worktree."""
    pass

@git_wrap("sparse_checkout_set", _registry)
async def set_sparse_checkout(patterns: str, cwd: Optional[str] = None):
    """Set sparse checkout patterns for speed optimization."""
    pass

@git_wrap("partial_clone", _registry)
async def partial_clone(url: str, dst: str, cwd: Optional[str] = None):
    """Clone with blob filtering for disk efficiency."""
    pass

@git_wrap("bundle_create", _registry)
async def create_bundle(bundle_file: str, refs: str, cwd: Optional[str] = None):
    """Create Git bundle for offline air-gap snapshots."""
    pass

# Collaboration & federation
@git_wrap("submodule_add", _registry)
async def add_submodule(url: str, path: str, cwd: Optional[str] = None):
    """Add submodule for domain pack mounting."""
    pass

@git_wrap("submodule_update", _registry)
async def update_submodules(cwd: Optional[str] = None):
    """Update all submodules recursively."""
    pass

@git_wrap("remote_add", _registry)
async def add_remote(name: str, url: str, cwd: Optional[str] = None):
    """Add remote for multi-org federation."""
    pass

@git_wrap("notes_add", _registry)
async def add_notes(ref: str, message: str, commit: str, cwd: Optional[str] = None):
    """Add notes for debate arguments and DMAIC data."""
    pass

# Workflow / history manipulation
@git_wrap("cherry_pick", _registry)
async def cherry_pick_commit(commit: str, cwd: Optional[str] = None):
    """Cherry-pick commit for promoting agent patches."""
    pass

@git_wrap("rebase_preserve_merges", _registry)
async def rebase_preserve_merges(base: str, cwd: Optional[str] = None):
    """Rebase with merge preservation for MergeOracle output."""
    pass

@git_wrap("reset_keep", _registry)
async def reset_keep(commit: str, cwd: Optional[str] = None):
    """Reset with --keep for instant sandbox rollback."""
    pass

@git_wrap("bisect_start", _registry)
async def start_bisect(cwd: Optional[str] = None):
    """Start bisect for autonomic root-cause search."""
    pass

# Security & provenance
@git_wrap("commit_signed", _registry)
async def commit_signed(message: str, cwd: Optional[str] = None):
    """Create signed commit with GPG."""
    pass

@git_wrap("tag_signed", _registry)
async def tag_signed(tag_name: str, message: str, cwd: Optional[str] = None):
    """Create signed tag with GPG."""
    pass

@git_wrap("notes_attestation_add", _registry)
async def add_sbom_attestation(sbom_hash: str, commit: str, cwd: Optional[str] = None):
    """Add SBOM attestation as Git note."""
    pass

# Maintenance & performance
@git_wrap("gc_aggressive", _registry)
async def gc_aggressive(cwd: Optional[str] = None):
    """Run aggressive garbage collection."""
    pass

@git_wrap("repack_bitmaps", _registry)
async def repack_with_bitmaps(cwd: Optional[str] = None):
    """Repack with bitmaps for federation performance."""
    pass

@git_wrap("prune_refs", _registry)
async def prune_remote_refs(remote: str, cwd: Optional[str] = None):
    """Prune remote references."""
    pass


# =============================================================================
# High-level Domain Operations
# =============================================================================

async def add_domain_pack(url: str, name: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Add a domain pack as a submodule."""
    domain_path = f"domain_packs/{name}"
    result = await add_submodule(url, domain_path, cwd)
    
    if result["success"]:
        # Update submodules after adding
        await update_submodules(cwd)
    
    return result


async def create_agent_worktree(agent_id: str, base_sha: str = "HEAD", cwd: Optional[str] = None) -> Dict[str, Any]:
    """Create isolated worktree for agent work."""
    worktree_path = f"agent_worktrees/{agent_id}"
    return await add_worktree(worktree_path, base_sha, cwd)


async def setup_sparse_agent_clone(url: str, dst: str, agent_paths: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Setup sparse checkout clone optimized for agent work."""
    # First, do partial clone
    clone_result = await partial_clone(url, dst, cwd)
    
    if clone_result["success"]:
        # Then set up sparse checkout
        patterns = "\n".join(agent_paths)
        sparse_result = await set_sparse_checkout(patterns, dst)
        return sparse_result
    
    return clone_result


async def emergency_rollback(target_sha: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Emergency rollback preserving working tree changes."""
    return await reset_keep(target_sha, cwd)


async def federation_sync(remote_name: str, remote_url: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Setup and sync with federation remote."""
    # Add remote if it doesn't exist
    add_result = await add_remote(remote_name, remote_url, cwd)
    
    if add_result["success"] or "already exists" in add_result["stderr"]:
        # Fetch from remote
        fetch_cmd = f"git fetch {remote_name}"
        process = await asyncio.create_subprocess_shell(
            fetch_cmd,
            cwd=cwd or os.getcwd(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "exit_code": process.returncode,
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "command": fetch_cmd,
            "cwd": cwd or os.getcwd()
        }
    
    return add_result


# =============================================================================
# Registry Management
# =============================================================================

def get_registry() -> GitRegistry:
    """Get the global Git registry instance."""
    return _registry


def reload_registry():
    """Reload the Git registry from disk."""
    global _registry
    _registry = GitRegistry()


def list_git_operations() -> List[str]:
    """List all available Git operations."""
    return _registry.list_operations()


def get_operation_info(operation_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific Git operation."""
    operation = _registry.get_operation(operation_name)
    if operation:
        return {
            "name": operation.name,
            "command": operation.cmd,
            "span": operation.span,
            "attributes": operation.attributes,
            "cwd_arg": operation.cwd_arg
        }
    return None