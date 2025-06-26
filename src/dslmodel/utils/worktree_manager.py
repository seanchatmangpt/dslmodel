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
    
    def remove_worktree(self, name: str, force: bool = False) -> bool:
        """Remove a worktree"""
        try:
            worktree_path = self.worktrees_dir / name
            
            cmd = ["git", "worktree", "remove"]
            if force:
                cmd.append("--force")
            cmd.append(str(worktree_path))
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Removed worktree: {name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove worktree {name}: {e}")
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
    
    def cleanup_stale_worktrees(self) -> List[str]:
        """Clean up stale/orphaned worktrees"""
        try:
            result = subprocess.run(
                ["git", "worktree", "prune", "-v"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            cleaned = result.stdout.strip().split('\n') if result.stdout.strip() else []
            logger.info(f"Cleaned {len(cleaned)} stale worktrees")
            return cleaned
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to cleanup worktrees: {e}")
            return []
    
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