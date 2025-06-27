#!/usr/bin/env python3
"""
Consensus Failure Path Handler
Handles edge cases in governance: ties, lost quorum, conflicts
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from loguru import logger


class ConflictType(Enum):
    """Types of governance conflicts"""
    TIE_VOTE = "tie_vote"
    LOST_QUORUM = "lost_quorum"
    INVALID_MOTION = "invalid_motion"
    PROCEDURAL_ERROR = "procedural_error"
    DEADLOCK = "deadlock"


class ResolutionOutcome(Enum):
    """Possible resolution outcomes"""
    DEFERRED = "deferred"
    ESCALATED = "escalated"
    RETRIED = "retried"
    ABANDONED = "abandoned"
    CHAIR_DECISION = "chair_decision"


@dataclass
class ConflictResolution:
    """Resolution for a governance conflict"""
    conflict_type: ConflictType
    motion_id: str
    outcome: ResolutionOutcome
    resolution_method: str
    chair_review_required: bool = False
    retry_deadline: Optional[datetime] = None
    escalation_path: Optional[str] = None
    span_data: Dict = None


class ConsensusFailureHandler:
    """Handle consensus failures and governance edge cases"""
    
    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path
        self.quorum_threshold = float(os.getenv('SWARMSH_QUORUM_THRESHOLD', '0.5'))
        self.chair_email = os.getenv('SWARMSH_GOVERNANCE_CHAIR', 'governance@example.com')
    
    def detect_conflict(self, motion_id: str, vote_tally: Dict[str, float], 
                       eligible_voters: int) -> Optional[ConflictType]:
        """Detect if there's a governance conflict"""
        total_votes = sum(vote_tally.values())
        
        # Check quorum
        if total_votes < (eligible_voters * self.quorum_threshold):
            return ConflictType.LOST_QUORUM
        
        # Check for tie
        yes_votes = vote_tally.get('yes', 0)
        no_votes = vote_tally.get('no', 0)
        
        if yes_votes == no_votes and yes_votes > 0:
            return ConflictType.TIE_VOTE
        
        # Check for procedural errors (no clear majority)
        abstain_votes = vote_tally.get('abstain', 0)
        if abstain_votes > (yes_votes + no_votes):
            return ConflictType.PROCEDURAL_ERROR
        
        return None
    
    def resolve_conflict(self, conflict_type: ConflictType, motion_id: str, 
                        vote_tally: Dict[str, float]) -> ConflictResolution:
        """Resolve a governance conflict"""
        
        if conflict_type == ConflictType.TIE_VOTE:
            return self._handle_tie_vote(motion_id, vote_tally)
        elif conflict_type == ConflictType.LOST_QUORUM:
            return self._handle_lost_quorum(motion_id, vote_tally)
        elif conflict_type == ConflictType.PROCEDURAL_ERROR:
            return self._handle_procedural_error(motion_id, vote_tally)
        else:
            return self._handle_generic_conflict(conflict_type, motion_id, vote_tally)
    
    def _handle_tie_vote(self, motion_id: str, vote_tally: Dict[str, float]) -> ConflictResolution:
        """Handle tie vote scenarios"""
        # Create follow-up task for chair review
        task_ref = self._create_follow_up_task(
            motion_id, 
            "Tie vote requires chair decision",
            priority="high"
        )
        
        # Emit governance conflict span
        span_data = {
            "name": "governance.conflict.resolve",
            "attributes": {
                "motion.id": motion_id,
                "conflict.type": ConflictType.TIE_VOTE.value,
                "outcome": ResolutionOutcome.DEFERRED.value,
                "chair.review_required": True,
                "yes_votes": vote_tally.get('yes', 0),
                "no_votes": vote_tally.get('no', 0)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": 15
        }
        
        logger.warning(f"⚖️ Tie vote on {motion_id}, deferring to chair review")
        
        return ConflictResolution(
            conflict_type=ConflictType.TIE_VOTE,
            motion_id=motion_id,
            outcome=ResolutionOutcome.DEFERRED,
            resolution_method="chair_review",
            chair_review_required=True,
            span_data=span_data
        )
    
    def _handle_lost_quorum(self, motion_id: str, vote_tally: Dict[str, float]) -> ConflictResolution:
        """Handle lost quorum scenarios"""
        # Reschedule vote with extended deadline
        retry_deadline = datetime.utcnow() + timedelta(days=3)
        
        # Create notification task
        task_ref = self._create_follow_up_task(
            motion_id,
            f"Quorum not met, rescheduled until {retry_deadline.isoformat()}",
            priority="medium"
        )
        
        span_data = {
            "name": "governance.conflict.resolve",
            "attributes": {
                "motion.id": motion_id,
                "conflict.type": ConflictType.LOST_QUORUM.value,
                "outcome": ResolutionOutcome.RETRIED.value,
                "retry_deadline": retry_deadline.isoformat(),
                "total_votes": sum(vote_tally.values()),
                "required_quorum": self.quorum_threshold
            },
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": 12
        }
        
        logger.warning(f"📊 Lost quorum on {motion_id}, rescheduling vote")
        
        return ConflictResolution(
            conflict_type=ConflictType.LOST_QUORUM,
            motion_id=motion_id,
            outcome=ResolutionOutcome.RETRIED,
            resolution_method="reschedule_vote",
            retry_deadline=retry_deadline,
            span_data=span_data
        )
    
    def _handle_procedural_error(self, motion_id: str, vote_tally: Dict[str, float]) -> ConflictResolution:
        """Handle procedural errors"""
        # Escalate to governance committee
        task_ref = self._create_follow_up_task(
            motion_id,
            "Procedural error in voting process",
            priority="high"
        )
        
        span_data = {
            "name": "governance.conflict.resolve", 
            "attributes": {
                "motion.id": motion_id,
                "conflict.type": ConflictType.PROCEDURAL_ERROR.value,
                "outcome": ResolutionOutcome.ESCALATED.value,
                "abstain_votes": vote_tally.get('abstain', 0),
                "total_votes": sum(vote_tally.values())
            },
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": 8
        }
        
        logger.error(f"⚠️ Procedural error on {motion_id}, escalating")
        
        return ConflictResolution(
            conflict_type=ConflictType.PROCEDURAL_ERROR,
            motion_id=motion_id,
            outcome=ResolutionOutcome.ESCALATED,
            resolution_method="committee_review",
            chair_review_required=True,
            escalation_path="governance_committee",
            span_data=span_data
        )
    
    def _handle_generic_conflict(self, conflict_type: ConflictType, motion_id: str, 
                                vote_tally: Dict[str, float]) -> ConflictResolution:
        """Handle other conflict types"""
        span_data = {
            "name": "governance.conflict.resolve",
            "attributes": {
                "motion.id": motion_id,
                "conflict.type": conflict_type.value,
                "outcome": ResolutionOutcome.ABANDONED.value,
                "vote_tally": json.dumps(vote_tally)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": 5
        }
        
        return ConflictResolution(
            conflict_type=conflict_type,
            motion_id=motion_id,
            outcome=ResolutionOutcome.ABANDONED,
            resolution_method="automatic_abandonment",
            span_data=span_data
        )
    
    def _create_follow_up_task(self, motion_id: str, description: str, 
                              priority: str = "medium") -> str:
        """Create follow-up task as Git ref"""
        task_id = f"task-{motion_id}-{int(datetime.utcnow().timestamp())}"
        ref_path = f"refs/governance/tasks/{task_id}"
        
        task_data = {
            "motion_id": motion_id,
            "description": description,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
            "assignee": self.chair_email
        }
        
        result = subprocess.run(
            ["git", "update-ref", ref_path, "HEAD", "-m", json.dumps(task_data)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"📋 Created follow-up task: {task_id}")
            return task_id
        else:
            logger.error(f"Failed to create task: {result.stderr}")
            return None
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending governance tasks"""
        tasks = []
        
        result = subprocess.run(
            ["git", "for-each-ref", "refs/governance/tasks/", "--format=%(refname)"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for ref_line in result.stdout.strip().split('\n'):
            if ref_line:
                # Get task data from reflog
                log_result = subprocess.run(
                    ["git", "reflog", "show", ref_line, "-n", "1"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                # Extract JSON from commit message
                try:
                    msg_start = log_result.stdout.find('{')
                    if msg_start != -1:
                        task_data = json.loads(log_result.stdout[msg_start:])
                        task_data['ref'] = ref_line
                        tasks.append(task_data)
                except json.JSONDecodeError:
                    continue
        
        return tasks
    
    def emit_conflict_span(self, resolution: ConflictResolution):
        """Emit telemetry span for conflict resolution"""
        if resolution.span_data:
            # In production, this would emit to OTEL collector
            logger.info(f"📊 Conflict span: {json.dumps(resolution.span_data, indent=2)}")


import os  # Add missing import