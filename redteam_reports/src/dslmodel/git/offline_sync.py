"""
Offline Git Bundle and Partial Clone Support
Air-gap snapshots and disk-light history for edge nodes
"""

import asyncio
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import aiofiles
import tempfile
import shutil

from .git_auto import create_bundle, partial_clone, gc_aggressive


@dataclass
class BundleManifest:
    """Manifest for a Git bundle."""
    bundle_id: str
    created_at: str
    refs: List[str]
    commit_range: str
    size_bytes: int
    checksum: str
    description: str
    tags: List[str]
    dependencies: List[str]  # Other bundle IDs this depends on


@dataclass
class PartialCloneConfig:
    """Configuration for partial clone operations."""
    filter_spec: str  # blob:none, tree:0, etc.
    depth: Optional[int]
    sparse_patterns: List[str]
    include_tags: bool
    include_branches: List[str]


class OfflineBundleManager:
    """Manages Git bundles for offline air-gap scenarios."""
    
    def __init__(self, bundle_storage_path: Optional[Path] = None):
        if bundle_storage_path is None:
            bundle_storage_path = Path.cwd() / "git_bundles"
        
        self.storage_path = bundle_storage_path
        self.storage_path.mkdir(exist_ok=True)
        
        self.manifests_path = self.storage_path / "manifests"
        self.manifests_path.mkdir(exist_ok=True)
        
        self.bundles_path = self.storage_path / "bundles"
        self.bundles_path.mkdir(exist_ok=True)
    
    async def create_air_gap_bundle(
        self,
        repo_path: Path,
        bundle_id: str,
        refs: List[str],
        description: str = "",
        tags: Optional[List[str]] = None,
        commit_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an air-gap bundle for offline transport."""
        try:
            tags = tags or []
            
            # Determine commit range if not specified
            if not commit_range:
                if "HEAD" in refs:
                    commit_range = "HEAD"
                else:
                    commit_range = " ".join(refs)
            
            # Create bundle file path
            bundle_filename = f"{bundle_id}.bundle"
            bundle_path = self.bundles_path / bundle_filename
            
            # Create the bundle
            refs_spec = " ".join(refs)
            result = await create_bundle(str(bundle_path), refs_spec, str(repo_path))
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create bundle: {result.get('stderr', 'Unknown error')}"
                }
            
            # Calculate bundle size and checksum
            bundle_size = bundle_path.stat().st_size
            checksum = await self._calculate_checksum(bundle_path)
            
            # Create manifest
            manifest = BundleManifest(
                bundle_id=bundle_id,
                created_at=datetime.now().isoformat(),
                refs=refs,
                commit_range=commit_range,
                size_bytes=bundle_size,
                checksum=checksum,
                description=description,
                tags=tags,
                dependencies=[]
            )
            
            # Save manifest
            await self._save_manifest(manifest)
            
            # Check if bundle is large (> 2MB) and emit compliance span
            if bundle_size > 2 * 1024 * 1024:
                # This would trigger the compliance.object.eject span as mentioned in playbook
                pass
            
            return {
                "success": True,
                "bundle_id": bundle_id,
                "bundle_path": str(bundle_path),
                "manifest": asdict(manifest),
                "size_mb": round(bundle_size / (1024 * 1024), 2)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Bundle creation failed: {str(e)}"
            }
    
    async def verify_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """Verify a bundle's integrity and validity."""
        try:
            bundle_path = self.bundles_path / f"{bundle_id}.bundle"
            
            if not bundle_path.exists():
                return {
                    "success": False,
                    "error": f"Bundle not found: {bundle_id}"
                }
            
            # Load manifest
            manifest = await self._load_manifest(bundle_id)
            if not manifest:
                return {
                    "success": False,
                    "error": f"Manifest not found for bundle: {bundle_id}"
                }
            
            # Verify checksum
            current_checksum = await self._calculate_checksum(bundle_path)
            if current_checksum != manifest.checksum:
                return {
                    "success": False,
                    "error": "Bundle checksum mismatch - file may be corrupted"
                }
            
            # Verify bundle with git
            verify_cmd = f"git bundle verify {bundle_path}"
            process = await asyncio.create_subprocess_shell(
                verify_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git bundle verification failed: {stderr.decode()}"
                }
            
            return {
                "success": True,
                "bundle_id": bundle_id,
                "manifest": asdict(manifest),
                "git_verification": stdout.decode().strip()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Bundle verification failed: {str(e)}"
            }
    
    async def extract_bundle(
        self, 
        bundle_id: str, 
        target_path: Path,
        create_worktree: bool = False
    ) -> Dict[str, Any]:
        """Extract a bundle to a target location."""
        try:
            bundle_path = self.bundles_path / f"{bundle_id}.bundle"
            
            if not bundle_path.exists():
                return {
                    "success": False,
                    "error": f"Bundle not found: {bundle_id}"
                }
            
            # Verify bundle first
            verify_result = await self.verify_bundle(bundle_id)
            if not verify_result["success"]:
                return verify_result
            
            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Clone from bundle
            clone_cmd = f"git clone {bundle_path} {target_path}"
            process = await asyncio.create_subprocess_shell(
                clone_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Bundle extraction failed: {stderr.decode()}"
                }
            
            result = {
                "success": True,
                "bundle_id": bundle_id,
                "target_path": str(target_path),
                "extraction_log": stdout.decode()
            }
            
            # Create worktree if requested
            if create_worktree:
                worktree_result = await self._create_extraction_worktree(target_path, bundle_id)
                result["worktree"] = worktree_result
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Bundle extraction failed: {str(e)}"
            }
    
    async def list_bundles(self, tags_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List all available bundles with optional tag filtering."""
        bundles = []
        
        for manifest_file in self.manifests_path.glob("*.json"):
            try:
                async with aiofiles.open(manifest_file, 'r') as f:
                    content = await f.read()
                    manifest_data = json.loads(content)
                    
                    # Apply tag filtering if specified
                    if tags_filter:
                        manifest_tags = set(manifest_data.get('tags', []))
                        filter_tags = set(tags_filter)
                        if not manifest_tags.intersection(filter_tags):
                            continue
                    
                    # Add bundle existence check
                    bundle_id = manifest_data['bundle_id']
                    bundle_path = self.bundles_path / f"{bundle_id}.bundle"
                    manifest_data['bundle_exists'] = bundle_path.exists()
                    
                    if bundle_path.exists():
                        manifest_data['bundle_size_mb'] = round(
                            bundle_path.stat().st_size / (1024 * 1024), 2
                        )
                    
                    bundles.append(manifest_data)
            
            except Exception as e:
                print(f"Error loading manifest {manifest_file}: {e}")
        
        # Sort by creation date (newest first)
        bundles.sort(key=lambda b: b['created_at'], reverse=True)
        return bundles
    
    async def delete_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """Delete a bundle and its manifest."""
        try:
            bundle_path = self.bundles_path / f"{bundle_id}.bundle"
            manifest_path = self.manifests_path / f"{bundle_id}.json"
            
            deleted_files = []
            
            if bundle_path.exists():
                bundle_path.unlink()
                deleted_files.append(str(bundle_path))
            
            if manifest_path.exists():
                manifest_path.unlink()
                deleted_files.append(str(manifest_path))
            
            if not deleted_files:
                return {
                    "success": False,
                    "error": f"Bundle not found: {bundle_id}"
                }
            
            return {
                "success": True,
                "bundle_id": bundle_id,
                "deleted_files": deleted_files
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Bundle deletion failed: {str(e)}"
            }
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            chunk = await f.read(8192)
            while chunk:
                hash_sha256.update(chunk)
                chunk = await f.read(8192)
        return hash_sha256.hexdigest()
    
    async def _save_manifest(self, manifest: BundleManifest):
        """Save bundle manifest to file."""
        manifest_path = self.manifests_path / f"{manifest.bundle_id}.json"
        async with aiofiles.open(manifest_path, 'w') as f:
            await f.write(json.dumps(asdict(manifest), indent=2))
    
    async def _load_manifest(self, bundle_id: str) -> Optional[BundleManifest]:
        """Load bundle manifest from file."""
        manifest_path = self.manifests_path / f"{bundle_id}.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            async with aiofiles.open(manifest_path, 'r') as f:
                content = await f.read()
                manifest_data = json.loads(content)
                return BundleManifest(**manifest_data)
        except Exception:
            return None
    
    async def _create_extraction_worktree(self, repo_path: Path, bundle_id: str) -> Dict[str, Any]:
        """Create a worktree for extracted bundle."""
        try:
            worktree_path = repo_path.parent / f"{repo_path.name}_worktree_{bundle_id}"
            
            # Create worktree
            worktree_cmd = f"git worktree add {worktree_path} HEAD"
            process = await asyncio.create_subprocess_shell(
                worktree_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "worktree_path": str(worktree_path) if process.returncode == 0 else None,
                "error": stderr.decode() if process.returncode != 0 else None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class PartialCloneManager:
    """Manages partial clone operations for disk-light history."""
    
    def __init__(self):
        self.configs_path = Path.cwd() / "partial_clone_configs"
        self.configs_path.mkdir(exist_ok=True)
    
    async def create_partial_clone(
        self,
        url: str,
        destination: Path,
        config: PartialCloneConfig,
        config_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a partial clone with specified configuration."""
        try:
            # Build clone command based on configuration
            clone_args = ["git", "clone"]
            
            # Add filter specification
            if config.filter_spec:
                clone_args.extend(["--filter", config.filter_spec])
            
            # Add depth if specified
            if config.depth:
                clone_args.extend(["--depth", str(config.depth)])
            
            # Add branch restrictions
            if config.include_branches:
                for branch in config.include_branches:
                    clone_args.extend(["--branch", branch])
            
            # Add tags option
            if not config.include_tags:
                clone_args.append("--no-tags")
            
            clone_args.extend([url, str(destination)])
            
            # Execute clone
            process = await asyncio.create_subprocess_exec(
                *clone_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Partial clone failed: {stderr.decode()}"
                }
            
            # Set up sparse checkout if patterns specified
            sparse_result = None
            if config.sparse_patterns:
                sparse_result = await self._setup_sparse_checkout(destination, config.sparse_patterns)
            
            # Save configuration if name provided
            if config_name:
                await self._save_config(config_name, config)
            
            # Get repository size info
            size_info = await self._get_repo_size_info(destination)
            
            return {
                "success": True,
                "destination": str(destination),
                "config": asdict(config),
                "clone_log": stdout.decode(),
                "sparse_checkout": sparse_result,
                "size_info": size_info
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Partial clone failed: {str(e)}"
            }
    
    async def optimize_existing_repo(
        self,
        repo_path: Path,
        config: PartialCloneConfig
    ) -> Dict[str, Any]:
        """Optimize existing repository with partial clone techniques."""
        try:
            results = {}
            
            # Set up sparse checkout if specified
            if config.sparse_patterns:
                sparse_result = await self._setup_sparse_checkout(repo_path, config.sparse_patterns)
                results["sparse_checkout"] = sparse_result
            
            # Configure partial clone filter if specified
            if config.filter_spec:
                filter_result = await self._configure_partial_clone_filter(repo_path, config.filter_spec)
                results["filter_config"] = filter_result
            
            # Run aggressive GC to optimize storage
            gc_result = await gc_aggressive(str(repo_path))
            results["gc_optimization"] = gc_result
            
            # Get size comparison
            size_info = await self._get_repo_size_info(repo_path)
            results["size_info"] = size_info
            
            return {
                "success": True,
                "repo_path": str(repo_path),
                "optimization_results": results
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Repository optimization failed: {str(e)}"
            }
    
    async def create_edge_node_clone(
        self,
        url: str,
        destination: Path,
        agent_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create optimized clone for edge nodes with minimal disk usage."""
        # Default agent paths for edge nodes
        if agent_paths is None:
            agent_paths = [
                "weaver/",
                "src/dslmodel/agents/",
                "src/dslmodel/otel/",
                "semantic_conventions/",
                "*.yaml",
                "*.md"
            ]
        
        config = PartialCloneConfig(
            filter_spec="blob:none",  # Exclude all blobs initially
            depth=1,  # Shallow clone
            sparse_patterns=agent_paths,
            include_tags=False,
            include_branches=["main", "HEAD"]
        )
        
        return await self.create_partial_clone(url, destination, config, "edge_node_default")
    
    async def _setup_sparse_checkout(self, repo_path: Path, patterns: List[str]) -> Dict[str, Any]:
        """Setup sparse checkout with specified patterns."""
        try:
            # Enable sparse checkout
            enable_cmd = "git config core.sparseCheckout true"
            process = await asyncio.create_subprocess_shell(
                enable_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode != 0:
                return {"success": False, "error": "Failed to enable sparse checkout"}
            
            # Write sparse checkout patterns
            sparse_file = repo_path / ".git" / "info" / "sparse-checkout"
            sparse_file.parent.mkdir(exist_ok=True)
            
            async with aiofiles.open(sparse_file, 'w') as f:
                await f.write('\n'.join(patterns))
            
            # Apply sparse checkout
            apply_cmd = "git sparse-checkout reapply"
            process = await asyncio.create_subprocess_shell(
                apply_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "patterns": patterns,
                "apply_log": stdout.decode() if process.returncode == 0 else stderr.decode()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Sparse checkout setup failed: {str(e)}"
            }
    
    async def _configure_partial_clone_filter(self, repo_path: Path, filter_spec: str) -> Dict[str, Any]:
        """Configure partial clone filter for existing repository."""
        try:
            # Set the filter
            filter_cmd = f"git config remote.origin.partialclonefilter {filter_spec}"
            process = await asyncio.create_subprocess_shell(
                filter_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode != 0:
                return {"success": False, "error": "Failed to set partial clone filter"}
            
            # Fetch with filter
            fetch_cmd = f"git fetch --filter={filter_spec}"
            process = await asyncio.create_subprocess_shell(
                fetch_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "filter_spec": filter_spec,
                "fetch_log": stdout.decode() if process.returncode == 0 else stderr.decode()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Filter configuration failed: {str(e)}"
            }
    
    async def _get_repo_size_info(self, repo_path: Path) -> Dict[str, Any]:
        """Get repository size information."""
        try:
            # Get .git directory size
            git_dir = repo_path / ".git"
            git_size = await self._get_directory_size(git_dir)
            
            # Get working tree size
            working_tree_size = await self._get_directory_size(repo_path) - git_size
            
            # Get object count
            count_cmd = "git count-objects -v"
            process = await asyncio.create_subprocess_shell(
                count_cmd,
                cwd=str(repo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            object_info = {}
            if process.returncode == 0:
                for line in stdout.decode().strip().split('\n'):
                    if ' ' in line:
                        key, value = line.split(' ', 1)
                        object_info[key] = value
            
            return {
                "git_dir_mb": round(git_size / (1024 * 1024), 2),
                "working_tree_mb": round(working_tree_size / (1024 * 1024), 2),
                "total_mb": round((git_size + working_tree_size) / (1024 * 1024), 2),
                "object_info": object_info
            }
        
        except Exception as e:
            return {"error": f"Size calculation failed: {str(e)}"}
    
    async def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for path in directory.rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
        except Exception:
            pass
        return total_size
    
    async def _save_config(self, config_name: str, config: PartialCloneConfig):
        """Save partial clone configuration."""
        config_path = self.configs_path / f"{config_name}.json"
        async with aiofiles.open(config_path, 'w') as f:
            await f.write(json.dumps(asdict(config), indent=2))


# =============================================================================
# High-level convenience functions
# =============================================================================

async def create_deployment_bundle(
    repo_path: Path,
    deployment_name: str,
    refs: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create a deployment bundle for air-gap environments."""
    if refs is None:
        refs = ["HEAD", "main"]
    
    manager = OfflineBundleManager()
    
    return await manager.create_air_gap_bundle(
        repo_path=repo_path,
        bundle_id=f"deployment_{deployment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        refs=refs,
        description=f"Deployment bundle for {deployment_name}",
        tags=["deployment", deployment_name]
    )


async def setup_edge_node_repository(
    source_url: str,
    edge_path: Path,
    agent_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Setup optimized repository for edge node deployment."""
    if agent_types is None:
        agent_types = ["weaver", "agents", "otel"]
    
    # Create patterns based on agent types
    patterns = []
    for agent_type in agent_types:
        patterns.extend([
            f"src/dslmodel/{agent_type}/",
            f"{agent_type}/",
            f"*{agent_type}*"
        ])
    
    # Add common essential files
    patterns.extend([
        "*.yaml",
        "*.md",
        "pyproject.toml",
        "requirements.txt"
    ])
    
    manager = PartialCloneManager()
    return await manager.create_edge_node_clone(source_url, edge_path, patterns)