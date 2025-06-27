#!/usr/bin/env python3
"""
Liquid Democracy Implementation for Swarm SH 5-ONE
================================================

Cross-repo vote refs with weighted delegation support.
MergeOracle provides O(1) vote tallying.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx

from loguru import logger


@dataclass
class Delegation:
    """Vote delegation in liquid democracy"""
    delegator: str
    delegate: str
    weight: float = 1.0
    topics: List[str] = field(default_factory=list)  # Empty = all topics
    expires: Optional[datetime] = None
    ref_path: Optional[str] = None


@dataclass
class CrossRepoVote:
    """Vote that spans multiple Git repositories"""
    voter: str
    motion_id: str
    vote: str
    repo_origin: str
    weight: float = 1.0
    delegation_chain: List[str] = field(default_factory=list)


class LiquidDemocracy:
    """Liquid democracy with Git refs and weighted delegation"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.delegation_graph = nx.DiGraph()
        self._load_delegations()
    
    def delegate_vote(self, delegation: Delegation) -> str:
        """Create delegation as Git ref"""
        ref_path = f"refs/democracy/delegations/{delegation.delegator}-to-{delegation.delegate}"
        
        delegation_data = {
            "delegator": delegation.delegator,
            "delegate": delegation.delegate,
            "weight": delegation.weight,
            "topics": delegation.topics,
            "expires": delegation.expires.isoformat() if delegation.expires else None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = subprocess.run(
            ["git", "update-ref", ref_path, "HEAD", "-m", json.dumps(delegation_data)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            delegation.ref_path = ref_path
            self.delegation_graph.add_edge(
                delegation.delegator,
                delegation.delegate,
                weight=delegation.weight,
                data=delegation_data
            )
            logger.info(f"🤝 Created delegation: {delegation.delegator} → {delegation.delegate}")
            return ref_path
        else:
            raise RuntimeError(f"Failed to create delegation: {result.stderr}")
    
    def _load_delegations(self):
        """Load all delegations from Git refs"""
        result = subprocess.run(
            ["git", "for-each-ref", "refs/democracy/delegations/"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line:
                ref_parts = line.split()
                if len(ref_parts) >= 2:
                    ref_name = ref_parts[1]
                    # Extract delegation from ref name
                    parts = ref_name.split('/')[-1].split('-to-')
                    if len(parts) == 2:
                        self.delegation_graph.add_edge(parts[0], parts[1])
    
    def resolve_vote_weight(self, voter: str, motion_id: str) -> Tuple[str, float, List[str]]:
        """Resolve final voter and weight through delegation chain"""
        visited = set()
        current = voter
        weight = 1.0
        chain = [voter]
        
        while current in self.delegation_graph and current not in visited:
            visited.add(current)
            delegates = list(self.delegation_graph.successors(current))
            
            if delegates:
                # Follow first delegation (could be enhanced with topic matching)
                next_delegate = delegates[0]
                edge_data = self.delegation_graph[current][next_delegate]
                weight *= edge_data.get('weight', 1.0)
                current = next_delegate
                chain.append(current)
            else:
                break
        
        return current, weight, chain
    
    def cast_liquid_vote(self, voter: str, motion_id: str, vote: str, repo_origin: str = "local") -> str:
        """Cast vote with liquid democracy resolution"""
        # Resolve delegation chain
        final_voter, weight, chain = self.resolve_vote_weight(voter, motion_id)
        
        # Create cross-repo vote
        cross_vote = CrossRepoVote(
            voter=final_voter,
            motion_id=motion_id,
            vote=vote,
            repo_origin=repo_origin,
            weight=weight,
            delegation_chain=chain
        )
        
        # Store as Git ref
        vote_id = f"{motion_id}-{voter}-liquid-{int(datetime.utcnow().timestamp())}"
        ref_path = f"refs/democracy/votes/{vote_id}"
        
        vote_data = {
            "voter": cross_vote.voter,
            "original_voter": voter,
            "motion_id": cross_vote.motion_id,
            "vote": cross_vote.vote,
            "weight": cross_vote.weight,
            "delegation_chain": cross_vote.delegation_chain,
            "repo_origin": cross_vote.repo_origin,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = subprocess.run(
            ["git", "update-ref", ref_path, "HEAD", "-m", json.dumps(vote_data)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"💧 Liquid vote cast: {voter} → {final_voter} (weight: {weight:.2f})")
            return ref_path
        else:
            raise RuntimeError(f"Failed to cast liquid vote: {result.stderr}")
    
    def merge_oracle_tally(self, motion_id: str) -> Dict[str, float]:
        """O(1) vote tallying using MergeOracle pattern"""
        # Pre-computed tally stored as merge commit message
        oracle_ref = f"refs/democracy/oracle/{motion_id}"
        
        # Check if oracle exists
        result = subprocess.run(
            ["git", "rev-parse", oracle_ref],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Read pre-computed tally
            tally_result = subprocess.run(
                ["git", "log", "-1", "--format=%B", oracle_ref],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            try:
                return json.loads(tally_result.stdout)
            except json.JSONDecodeError:
                pass
        
        # Compute tally if oracle doesn't exist
        return self._compute_tally(motion_id)
    
    def _compute_tally(self, motion_id: str) -> Dict[str, float]:
        """Compute weighted vote tally"""
        tally = {"yes": 0.0, "no": 0.0, "abstain": 0.0}
        voters_seen = set()
        
        # Get all votes for this motion
        result = subprocess.run(
            ["git", "for-each-ref", f"refs/democracy/votes/*{motion_id}*", "--format=%(refname) %(contents)"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line and motion_id in line:
                # Extract vote data from ref log
                log_result = subprocess.run(
                    ["git", "reflog", "show", line.split()[0], "-n", "1"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                # Parse vote data from commit message
                try:
                    # Extract JSON from reflog message
                    msg_start = log_result.stdout.find('{')
                    if msg_start != -1:
                        vote_data = json.loads(log_result.stdout[msg_start:])
                        voter = vote_data.get('voter', vote_data.get('original_voter'))
                        
                        # Prevent double counting
                        if voter not in voters_seen:
                            voters_seen.add(voter)
                            vote_type = vote_data.get('vote', 'abstain').lower()
                            weight = vote_data.get('weight', 1.0)
                            
                            if vote_type in tally:
                                tally[vote_type] += weight
                except json.JSONDecodeError:
                    continue
        
        # Store result in oracle for O(1) future access
        self._create_oracle(motion_id, tally)
        
        return tally
    
    def _create_oracle(self, motion_id: str, tally: Dict[str, float]):
        """Create MergeOracle ref with pre-computed tally"""
        oracle_ref = f"refs/democracy/oracle/{motion_id}"
        
        subprocess.run(
            ["git", "update-ref", oracle_ref, "HEAD", "-m", json.dumps(tally)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        logger.info(f"🔮 Created MergeOracle for {motion_id}: {tally}")
    
    def prune_vote_refs(self, motion_id: str, keep_oracle: bool = True) -> int:
        """Prune vote refs after decision to prevent unbounded growth"""
        pruned_count = 0
        
        # Get all vote refs for this motion
        result = subprocess.run(
            ["git", "for-each-ref", f"refs/democracy/votes/*{motion_id}*", "--format=%(refname)"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for ref_line in result.stdout.strip().split('\n'):
            if ref_line and motion_id in ref_line:
                # Delete the ref
                subprocess.run(
                    ["git", "update-ref", "-d", ref_line],
                    cwd=self.repo_path,
                    capture_output=True
                )
                pruned_count += 1
        
        # Emit pruning span
        from datetime import datetime
        prune_span = {
            "name": "git.prune",
            "attributes": {
                "motion.id": motion_id,
                "refs.pruned": pruned_count,
                "oracle.preserved": keep_oracle
            },
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": 10
        }
        
        logger.info(f"🗑️ Pruned {pruned_count} vote refs for {motion_id}")
        return pruned_count
    
    def federate_vote(self, remote_repo: str, motion_id: str) -> List[CrossRepoVote]:
        """Federate votes from remote repository"""
        # Fetch remote refs
        subprocess.run(
            ["git", "fetch", remote_repo, "refs/democracy/votes/*:refs/democracy/federated/*"],
            cwd=self.repo_path,
            capture_output=True
        )
        
        # Import federated votes
        federated_votes = []
        result = subprocess.run(
            ["git", "for-each-ref", f"refs/democracy/federated/*{motion_id}*"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            if line:
                # Process federated vote
                ref_name = line.split()[1]
                logger.info(f"🌐 Imported federated vote: {ref_name}")
                federated_votes.append(ref_name)
        
        return federated_votes