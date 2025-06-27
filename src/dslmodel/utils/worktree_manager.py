#!/usr/bin/env python3
"""
Git Worktree Manager for Feature Development
===========================================

Manages git worktrees for isolated feature development.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


@dataclass
class Worktree:
    """Represents a git worktree"""
    name: str
    path: Path
    branch: str
    bare: bool = False
    locked: bool = False
    created_at: Optional[datetime] = None


class WorktreeManager:
    """Manages git worktrees for feature development"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.worktrees_dir = repo_path / "worktrees"
        self.worktrees_dir.mkdir(exist_ok=True)
    
    def list_worktrees(self) -> List[Worktree]:
        """List all worktrees"""
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            worktrees = []
            current_worktree = {}
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    if current_worktree:
                        worktrees.append(self._parse_worktree(current_worktree))
                    current_worktree = {'path': line[9:]}  # Remove 'worktree '
                elif line.startswith('HEAD '):
                    current_worktree['head'] = line[5:]
                elif line.startswith('branch '):
                    current_worktree['branch'] = line[7:]
                elif line == 'bare':
                    current_worktree['bare'] = True
                elif line == 'locked':
                    current_worktree['locked'] = True
            
            # Add the last worktree
            if current_worktree:
                worktrees.append(self._parse_worktree(current_worktree))
            
            return worktrees
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list worktrees: {e}")
            return []
    
    def _parse_worktree(self, data: Dict[str, Any]) -> Worktree:
        """Parse worktree data into Worktree object"""
        path = Path(data['path'])
        name = path.name
        branch = data.get('branch', 'detached')
        
        return Worktree(
            name=name,
            path=path,
            branch=branch,
            bare=data.get('bare', False),
            locked=data.get('locked', False)
        )
    
    def create_worktree(self, name: str, base_branch: str = "main", 
                       create_branch: bool = True) -> Worktree:
        """Create a new worktree"""
        worktree_path = self.worktrees_dir / name
        
        # Clean up if exists
        if worktree_path.exists():
            self.remove_worktree(name)
        
        try:
            cmd = ["git", "worktree", "add"]
            
            if create_branch:
                # Create new branch
                branch_name = name.replace('/', '-')
                cmd.extend(["-b", branch_name])
            
            cmd.extend([str(worktree_path), base_branch])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Created worktree: {name}")
            
            return Worktree(
                name=name,
                path=worktree_path,
                branch=branch_name if create_branch else base_branch,
                created_at=datetime.now()
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worktree {name}: {e}")
            raise
    
    def remove_worktree(self, name: str, force: bool = False, max_retries: int = 3) -> bool:
        """Remove a worktree with retry logic and robust cleanup"""
        import time
        import shutil
        
        worktree_path = self.worktrees_dir / name
        
        for attempt in range(max_retries):
            try:
                # First attempt: Standard git worktree remove
                cmd = ["git", "worktree", "remove"]
                if force or attempt > 0:  # Use force on retries
                    cmd.append("--force")
                cmd.append(str(worktree_path))
                
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                logger.info(f"✅ Removed worktree: {name} (attempt {attempt + 1})")
                return True
                
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️  Attempt {attempt + 1} failed to remove worktree {name}: {e}")
                
                # On failure, try progressively more aggressive cleanup
                if attempt == 0:
                    # Attempt 1: Try unlocking first
                    try:
                        subprocess.run(
                            ["git", "worktree", "unlock", str(worktree_path)],
                            cwd=self.repo_path,
                            capture_output=True,
                            check=False  # Don't fail if already unlocked
                        )
                        logger.info(f"🔓 Unlocked worktree: {name}")
                    except Exception:
                        pass
                        
                elif attempt == 1:
                    # Attempt 2: Force prune and try again
                    try:
                        subprocess.run(
                            ["git", "worktree", "prune", "--force"],
                            cwd=self.repo_path,
                            capture_output=True,
                            check=False
                        )
                        logger.info(f"🧹 Pruned worktrees before retry")
                    except Exception:
                        pass
                        
                elif attempt == 2:
                    # Final attempt: Manual filesystem cleanup
                    try:
                        if worktree_path.exists():
                            # Remove read-only files on Windows
                            if worktree_path.is_dir():
                                def handle_remove_readonly(func, path, exc):
                                    import stat
                                    if exc[1].errno == 13:  # Permission denied
                                        Path(path).chmod(stat.S_IWRITE)
                                        func(path)
                                
                                shutil.rmtree(worktree_path, onerror=handle_remove_readonly)
                                logger.warning(f"🗑️  Manually removed worktree directory: {worktree_path}")
                            else:
                                worktree_path.unlink()
                                
                        # Also prune git's internal state
                        subprocess.run(
                            ["git", "worktree", "prune", "--force"],
                            cwd=self.repo_path,
                            capture_output=True,
                            check=False
                        )
                        
                        logger.info(f"🔧 Manual cleanup completed for: {name}")
                        return True
                        
                    except Exception as cleanup_error:
                        logger.error(f"❌ Manual cleanup failed for {name}: {cleanup_error}")
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        logger.error(f"❌ Failed to remove worktree {name} after {max_retries} attempts")
        return False
    
    def switch_worktree(self, name: str) -> bool:
        """Switch to a worktree (change directory)"""
        worktree_path = self.worktrees_dir / name
        
        if worktree_path.exists():
            # This would be used in shell scripts
            logger.info(f"Switch to worktree: {worktree_path}")
            return True
        else:
            logger.error(f"Worktree not found: {name}")
            return False
    
    def get_worktree(self, name: str) -> Optional[Worktree]:
        """Get specific worktree by name"""
        worktrees = self.list_worktrees()
        for worktree in worktrees:
            if worktree.name == name:
                return worktree
        return None
    
    def cleanup_stale_worktrees(self, max_retries: int = 2) -> List[str]:
        """Clean up stale/orphaned worktrees with retry logic"""
        import time
        
        cleaned_total = []
        
        for attempt in range(max_retries):
            try:
                # First pass: Standard prune
                result = subprocess.run(
                    ["git", "worktree", "prune", "-v"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                cleaned = result.stdout.strip().split('\n') if result.stdout.strip() else []
                cleaned_total.extend(cleaned)
                
                if attempt == 0 and cleaned:
                    logger.info(f"🧹 Standard prune cleaned {len(cleaned)} stale worktrees")
                elif attempt == 1:
                    # Second pass: Force prune to catch stubborn entries
                    force_result = subprocess.run(
                        ["git", "worktree", "prune", "--force", "-v"],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=False  # Don't fail if nothing to force clean
                    )
                    
                    force_cleaned = force_result.stdout.strip().split('\n') if force_result.stdout.strip() else []
                    cleaned_total.extend(force_cleaned)
                    
                    if force_cleaned:
                        logger.info(f"🔧 Force prune cleaned additional {len(force_cleaned)} stale worktrees")
                
                # Check for manually removable directories
                if self.worktrees_dir.exists():
                    for path in self.worktrees_dir.iterdir():
                        if path.is_dir():
                            # Check if this is a valid worktree
                            git_dir = path / ".git"
                            if not git_dir.exists():
                                try:
                                    import shutil
                                    shutil.rmtree(path)
                                    logger.warning(f"🗑️  Removed orphaned directory: {path.name}")
                                    cleaned_total.append(f"manual:{path.name}")
                                except Exception as e:
                                    logger.error(f"❌ Failed to remove orphaned directory {path}: {e}")
                
                if attempt > 0 or not cleaned:
                    break  # Exit early if nothing more to clean
                    
                # Wait between passes to allow filesystem to settle
                if attempt < max_retries - 1:
                    time.sleep(1)
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to cleanup worktrees (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return cleaned_total
        
        total_count = len(cleaned_total)
        if total_count > 0:
            logger.info(f"✅ Total cleanup: {total_count} stale worktrees removed")
        else:
            logger.info("✨ No stale worktrees found")
            
        return cleaned_total
    
    def merge_completed_feature(self, feature_name: str, target_branch: str = "main") -> bool:
        """Merge completed feature and cleanup worktree"""
        try:
            worktree = self.get_worktree(feature_name)
            if not worktree:
                logger.error(f"Worktree not found: {feature_name}")
                return False
            
            # Switch to target branch
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=self.repo_path,
                check=True
            )
            
            # Merge feature branch
            subprocess.run(
                ["git", "merge", worktree.branch],
                cwd=self.repo_path,
                check=True
            )
            
            # Remove worktree and branch
            self.remove_worktree(feature_name)
            subprocess.run(
                ["git", "branch", "-d", worktree.branch],
                cwd=self.repo_path,
                check=True
            )
            
            logger.info(f"Merged and cleaned up feature: {feature_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to merge feature {feature_name}: {e}")
            return False