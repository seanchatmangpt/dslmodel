"""
Roberts Rules Parliament - Git-native Parliamentary Governance
==============================================================

Implements Roberts Rules of Order using pure git primitives for
automated governance and decision making in software development.
"""

import json
import datetime
import subprocess
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from ..utils.span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from ..utils.git_auto import execute_git_command, notes_add, tag
except ImportError:
    def execute_git_command(op, **kwargs):
        print(f"[GIT] Would execute: {op} with {kwargs}")
        return type('Result', (), {'returncode': 0, 'stdout': 'success'})()
    def notes_add(ref, target, message):
        print(f"[GIT] Would add note: {ref} -> {target}: {message}")
    def tag(name, message):
        print(f"[GIT] Would create tag: {name} with {message}")

try:
    from ..utils.log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

class MotionState(Enum):
    """Parliamentary motion states."""
    PROPOSED = "proposed"
    SECONDED = "seconded"
    ON_FLOOR = "on_floor"
    DEBATING = "debating"
    VOTING = "voting"
    PASSED = "passed"
    FAILED = "failed"
    TABLED = "tabled"
    WITHDRAWN = "withdrawn"

class VoteType(Enum):
    """Types of parliamentary votes."""
    SIMPLE_MAJORITY = "simple_majority"
    TWO_THIRDS = "two_thirds"
    UNANIMOUS = "unanimous"
    PLURALITY = "plurality"

@dataclass
class Motion:
    """Represents a parliamentary motion."""
    id: str
    title: str
    description: str
    proposer: str
    seconder: Optional[str]
    state: MotionState
    vote_type: VoteType
    created_at: str
    git_issue_number: Optional[int] = None
    git_tag: Optional[str] = None

@dataclass
class Vote:
    """Represents a vote on a motion."""
    motion_id: str
    voter: str
    position: str  # for, against, abstain
    timestamp: str
    git_commit: str

class RobertsParliament:
    """Git-native implementation of Roberts Rules of Order."""
    
    def __init__(self):
        self.session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        self.motions: Dict[str, Motion] = {}
        self.votes: Dict[str, List[Vote]] = {}
        self.quorum_size = 5  # Minimum members for valid session
        self.members = self._load_members()
    
    def _load_members(self) -> List[str]:
        """Load parliament members from git contributors."""
        try:
            result = subprocess.run(
                ["git", "log", "--format=%ae", "--since=3.months", "HEAD"],
                capture_output=True, text=True, check=True
            )
            contributors = list(set(result.stdout.strip().split('\n')))
            return [c for c in contributors if c and '@' in c][:20]  # Limit to 20 recent contributors
        except subprocess.CalledProcessError:
            return ["system@parliament.gov"]  # Fallback member
    
    @span("roberts_propose_motion")
    def propose_motion(
        self,
        title: str,
        description: str,
        proposer: str,
        vote_type: VoteType = VoteType.SIMPLE_MAJORITY
    ) -> str:
        """Propose a new motion using git issue."""
        
        motion_id = f"MOT-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create git issue for the motion
        issue_body = f"""
## Parliamentary Motion {motion_id}

**Proposer:** {proposer}
**Vote Type:** {vote_type.value}
**Session:** {self.session_id}

### Motion Text
{description}

### Parliamentary Status
- [ ] Requires Second
- [ ] Ready for Floor
- [ ] Open for Debate
- [ ] Ready for Vote
- [ ] Decision Recorded

### Voting Instructions
To vote on this motion, use git commands:
```bash
# Vote FOR
git tag -a vote-{motion_id}-for-{{your_email}} -m "Vote FOR motion {motion_id}"

# Vote AGAINST  
git tag -a vote-{motion_id}-against-{{your_email}} -m "Vote AGAINST motion {motion_id}"

# Abstain
git tag -a vote-{motion_id}-abstain-{{your_email}} -m "ABSTAIN from motion {motion_id}"
```
"""
        
        motion = Motion(
            id=motion_id,
            title=title,
            description=description,
            proposer=proposer,
            seconder=None,
            state=MotionState.PROPOSED,
            vote_type=vote_type,
            created_at=datetime.datetime.now().isoformat(),
            git_issue_number=None,  # Would be set by actual git issue creation
            git_tag=f"motion/{motion_id}/proposed"
        )
        
        # Create git tag for motion tracking
        tag_message = json.dumps({
            "motion_id": motion_id,
            "title": title,
            "proposer": proposer,
            "state": motion.state.value,
            "parliamentary_session": self.session_id,
            "roberts_rules_compliance": True
        }, indent=2)
        
        tag(motion.git_tag, tag_message)
        
        self.motions[motion_id] = motion
        
        # Record in parliamentary minutes
        minutes_entry = f"Motion {motion_id} proposed by {proposer}: {title}"
        notes_add("parliamentary_minutes", motion.git_tag, minutes_entry)
        
        logger.info(f"📋 Motion proposed: {motion_id} - {title}")
        return motion_id
    
    @span("roberts_second_motion")
    def second_motion(self, motion_id: str, seconder: str) -> bool:
        """Second a motion following Roberts Rules."""
        
        if motion_id not in self.motions:
            logger.error(f"Motion {motion_id} not found")
            return False
        
        motion = self.motions[motion_id]
        
        if motion.state != MotionState.PROPOSED:
            logger.error(f"Motion {motion_id} is not in PROPOSED state")
            return False
        
        if motion.proposer == seconder:
            logger.error("Proposer cannot second their own motion")
            return False
        
        # Update motion state
        motion.seconder = seconder
        motion.state = MotionState.SECONDED
        
        # Create git tag for seconded state
        seconded_tag = f"motion/{motion_id}/seconded"
        tag_message = json.dumps({
            "motion_id": motion_id,
            "seconder": seconder,
            "state": motion.state.value,
            "ready_for_floor": True
        }, indent=2)
        
        tag(seconded_tag, tag_message)
        
        # Record in minutes
        minutes_entry = f"Motion {motion_id} seconded by {seconder}. Motion is now on the floor."
        notes_add("parliamentary_minutes", seconded_tag, minutes_entry)
        
        logger.info(f"✋ Motion seconded: {motion_id} by {seconder}")
        return True
    
    @span("roberts_open_floor") 
    def open_floor(self, motion_id: str, chair: str) -> bool:
        """Open floor for debate on a motion."""
        
        motion = self.motions.get(motion_id)
        if not motion or motion.state != MotionState.SECONDED:
            logger.error(f"Motion {motion_id} not ready for floor")
            return False
        
        motion.state = MotionState.ON_FLOOR
        
        # Create floor tag
        floor_tag = f"motion/{motion_id}/floor"
        tag_message = json.dumps({
            "motion_id": motion_id,
            "chair": chair,
            "state": motion.state.value,
            "debate_opened": datetime.datetime.now().isoformat()
        }, indent=2)
        
        tag(floor_tag, tag_message)
        
        # Record in minutes
        minutes_entry = f"Chair {chair} opens floor for debate on motion {motion_id}"
        notes_add("parliamentary_minutes", floor_tag, minutes_entry)
        
        logger.info(f"🗣️  Floor opened for motion: {motion_id}")
        return True
    
    @span("roberts_call_vote")
    def call_vote(self, motion_id: str, chair: str) -> bool:
        """Call for vote on a motion."""
        
        motion = self.motions.get(motion_id)
        if not motion or motion.state not in [MotionState.ON_FLOOR, MotionState.DEBATING]:
            logger.error(f"Motion {motion_id} not ready for vote")
            return False
        
        motion.state = MotionState.VOTING
        
        # Create voting tag
        vote_tag = f"motion/{motion_id}/voting"
        tag_message = json.dumps({
            "motion_id": motion_id,
            "chair": chair,
            "state": motion.state.value,
            "vote_called": datetime.datetime.now().isoformat(),
            "vote_type": motion.vote_type.value,
            "voting_instructions": f"Use git tags: vote-{motion_id}-[for|against|abstain]-{{email}}"
        }, indent=2)
        
        tag(vote_tag, tag_message)
        
        # Record in minutes
        minutes_entry = f"Chair {chair} calls for vote on motion {motion_id} ({motion.vote_type.value})"
        notes_add("parliamentary_minutes", vote_tag, minutes_entry)
        
        logger.info(f"🗳️  Vote called for motion: {motion_id}")
        return True
    
    @span("roberts_tally_votes")
    def tally_votes(self, motion_id: str) -> Dict[str, Any]:
        """Tally votes for a motion from git tags."""
        
        motion = self.motions.get(motion_id)
        if not motion:
            return {"error": "Motion not found"}
        
        # Get all vote tags for this motion
        try:
            result = subprocess.run(
                ["git", "tag", "-l", f"vote-{motion_id}-*"],
                capture_output=True, text=True, check=True
            )
            vote_tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            vote_tags = []
        
        votes = {"for": 0, "against": 0, "abstain": 0}
        voters = set()
        vote_details = []
        
        for tag_name in vote_tags:
            if not tag_name:
                continue
                
            # Parse vote tag: vote-{motion_id}-{position}-{voter_email}
            parts = tag_name.split('-')
            if len(parts) >= 4:
                position = parts[2]
                voter = '-'.join(parts[3:])
                
                if voter not in voters:  # Prevent double voting
                    voters.add(voter)
                    if position in votes:
                        votes[position] += 1
                        vote_details.append({
                            "voter": voter,
                            "position": position,
                            "tag": tag_name
                        })
        
        total_votes = sum(votes.values())
        
        # Determine if motion passes based on vote type
        passed = False
        if motion.vote_type == VoteType.SIMPLE_MAJORITY:
            passed = votes["for"] > votes["against"]
        elif motion.vote_type == VoteType.TWO_THIRDS:
            passed = votes["for"] >= (total_votes * 2 / 3)
        elif motion.vote_type == VoteType.UNANIMOUS:
            passed = votes["for"] == total_votes and votes["against"] == 0
        
        result = {
            "motion_id": motion_id,
            "votes": votes,
            "total_votes": total_votes,
            "voters": list(voters),
            "vote_details": vote_details,
            "passed": passed,
            "vote_type": motion.vote_type.value,
            "quorum_met": total_votes >= self.quorum_size
        }
        
        logger.info(f"📊 Vote tally for {motion_id}: {votes} (passed: {passed})")
        return result
    
    @span("roberts_finalize_motion")
    def finalize_motion(self, motion_id: str, chair: str) -> bool:
        """Finalize a motion with vote results."""
        
        vote_result = self.tally_votes(motion_id)
        motion = self.motions.get(motion_id)
        
        if not motion or not vote_result.get("quorum_met"):
            logger.error(f"Cannot finalize motion {motion_id} - no quorum")
            return False
        
        # Update motion state
        motion.state = MotionState.PASSED if vote_result["passed"] else MotionState.FAILED
        
        # Create final decision tag
        final_tag = f"motion/{motion_id}/final"
        tag_message = json.dumps({
            "motion_id": motion_id,
            "chair": chair,
            "final_state": motion.state.value,
            "vote_result": vote_result,
            "finalized_at": datetime.datetime.now().isoformat(),
            "roberts_rules_compliant": True
        }, indent=2)
        
        tag(final_tag, tag_message)
        
        # Record final minutes
        status = "PASSED" if vote_result["passed"] else "FAILED"
        minutes_entry = f"Motion {motion_id} {status}. Votes: {vote_result['votes']}. Chair {chair} declares motion {status.lower()}."
        notes_add("parliamentary_minutes", final_tag, minutes_entry)
        
        logger.info(f"⚖️  Motion finalized: {motion_id} - {status}")
        return True
    
    @span("roberts_generate_session_report")
    def generate_session_report(self) -> Dict[str, Any]:
        """Generate complete parliamentary session report."""
        
        report = {
            "session_id": self.session_id,
            "generated_at": datetime.datetime.now().isoformat(),
            "members": self.members,
            "quorum_size": self.quorum_size,
            "motions": {},
            "statistics": {
                "total_motions": len(self.motions),
                "passed_motions": 0,
                "failed_motions": 0,
                "pending_motions": 0
            }
        }
        
        for motion_id, motion in self.motions.items():
            motion_data = {
                "title": motion.title,
                "proposer": motion.proposer,
                "seconder": motion.seconder,
                "state": motion.state.value,
                "vote_type": motion.vote_type.value,
                "created_at": motion.created_at
            }
            
            if motion.state in [MotionState.PASSED, MotionState.FAILED]:
                motion_data["vote_result"] = self.tally_votes(motion_id)
                if motion.state == MotionState.PASSED:
                    report["statistics"]["passed_motions"] += 1
                else:
                    report["statistics"]["failed_motions"] += 1
            else:
                report["statistics"]["pending_motions"] += 1
            
            report["motions"][motion_id] = motion_data
        
        return report

# Convenience functions for common parliamentary procedures

def create_parliament() -> RobertsParliament:
    """Create a new parliamentary session."""
    return RobertsParliament()

@span("roberts_propose_release")
def propose_release_motion(parliament: RobertsParliament, version: str, proposer: str) -> str:
    """Propose a release approval motion."""
    return parliament.propose_motion(
        title=f"Approve Release {version}",
        description=f"Motion to approve the release of version {version} to production. This includes all testing, security, and quality gates.",
        proposer=proposer,
        vote_type=VoteType.TWO_THIRDS
    )

@span("roberts_propose_feature")
def propose_feature_motion(parliament: RobertsParliament, feature: str, proposer: str) -> str:
    """Propose a feature approval motion."""
    return parliament.propose_motion(
        title=f"Approve Feature: {feature}",
        description=f"Motion to approve development of feature '{feature}' and allocation of necessary resources.",
        proposer=proposer,
        vote_type=VoteType.SIMPLE_MAJORITY
    )

@span("roberts_emergency_motion")
def propose_emergency_motion(parliament: RobertsParliament, issue: str, proposer: str) -> str:
    """Propose an emergency motion (requires unanimous approval)."""
    return parliament.propose_motion(
        title=f"Emergency: {issue}",
        description=f"Emergency motion to address critical issue: {issue}. Requires immediate action.",
        proposer=proposer,
        vote_type=VoteType.UNANIMOUS
    )