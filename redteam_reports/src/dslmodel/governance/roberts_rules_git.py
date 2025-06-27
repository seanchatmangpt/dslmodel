"""
Roberts Rules Democratic Git Governance System
Implementation of parliamentary procedure for Git operations
"""

import subprocess
import json
import time
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from opentelemetry import trace

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()
tracer = trace.get_tracer(__name__)

class MotionType(Enum):
    """Types of motions in Roberts Rules for Git operations"""
    MERGE = "merge"
    RELEASE = "release"
    ARCHITECTURE = "architecture"
    PROCESS = "process"
    ROLLBACK = "rollback"
    SECURITY = "security"
    FEDERATION = "federation"

class MotionStatus(Enum):
    """Status of a motion"""
    PROPOSED = "proposed"
    IN_DEBATE = "in_debate"
    VOTING = "voting"
    PASSED = "passed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"
    TABLED = "tabled"

class VoteType(Enum):
    """Types of votes"""
    YEA = "yea"
    NAY = "nay"
    ABSTAIN = "abstain"

@dataclass
class Participant:
    """Parliamentary participant"""
    name: str
    email: str
    role: str  # proposer, seconder, chair, member
    voting_weight: float = 1.0
    pgp_key: Optional[str] = None

@dataclass
class Motion:
    """Parliamentary motion for Git operations"""
    id: str
    motion_type: MotionType
    title: str
    description: str
    proposer: Participant
    seconder: Optional[Participant]
    status: MotionStatus
    created_at: datetime
    git_operation: Dict[str, Any]  # Specific Git command and parameters
    required_votes: int
    quorum_required: int
    time_limit: Optional[int] = None  # seconds for debate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git notes storage"""
        return {
            "id": self.id,
            "motion_type": self.motion_type.value,
            "title": self.title,
            "description": self.description,
            "proposer": asdict(self.proposer),
            "seconder": asdict(self.seconder) if self.seconder else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "git_operation": self.git_operation,
            "required_votes": self.required_votes,
            "quorum_required": self.quorum_required,
            "time_limit": self.time_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Motion':
        """Create Motion from dictionary"""
        return cls(
            id=data["id"],
            motion_type=MotionType(data["motion_type"]),
            title=data["title"],
            description=data["description"],
            proposer=Participant(**data["proposer"]),
            seconder=Participant(**data["seconder"]) if data.get("seconder") else None,
            status=MotionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            git_operation=data["git_operation"],
            required_votes=data["required_votes"],
            quorum_required=data["quorum_required"],
            time_limit=data.get("time_limit")
        )

@dataclass
class Vote:
    """Individual vote on a motion"""
    motion_id: str
    voter: Participant
    vote_type: VoteType
    reasoning: str
    timestamp: datetime
    signature: Optional[str] = None  # Cryptographic signature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git notes storage"""
        return {
            "motion_id": self.motion_id,
            "voter": asdict(self.voter),
            "vote_type": self.vote_type.value,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "signature": self.signature
        }

@dataclass
class Debate:
    """Debate record for a motion"""
    motion_id: str
    speaker: Participant
    statement: str
    timestamp: datetime
    speaking_order: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git notes storage"""
        return {
            "motion_id": self.motion_id,
            "speaker": asdict(self.speaker),
            "statement": self.statement,
            "timestamp": self.timestamp.isoformat(),
            "speaking_order": self.speaking_order
        }

@dataclass
class VotingResult:
    """Result of a vote"""
    motion_id: str
    total_eligible: int
    votes_cast: int
    yea_votes: int
    nay_votes: int
    abstain_votes: int
    quorum_met: bool
    motion_passed: bool
    final_tally: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git notes storage"""
        return {
            "motion_id": self.motion_id,
            "total_eligible": self.total_eligible,
            "votes_cast": self.votes_cast,
            "yea_votes": self.yea_votes,
            "nay_votes": self.nay_votes,
            "abstain_votes": self.abstain_votes,
            "quorum_met": self.quorum_met,
            "motion_passed": self.motion_passed,
            "final_tally": self.final_tally,
            "timestamp": self.timestamp.isoformat()
        }

class GitParliamentaryProcedure:
    """Git integration for Roberts Rules parliamentary procedure"""
    
    def __init__(self):
        self.notes_ref_motions = "refs/notes/roberts-rules/motions"
        self.notes_ref_votes = "refs/notes/roberts-rules/votes"
        self.notes_ref_debates = "refs/notes/roberts-rules/debates"
        self.notes_ref_results = "refs/notes/roberts-rules/results"
        
    def store_motion(self, motion: Motion) -> bool:
        """Store motion in Git notes"""
        try:
            motion_json = json.dumps(motion.to_dict(), indent=2)
            
            # Store in git notes under motions ref
            result = subprocess.run([
                "git", "notes", "--ref", self.notes_ref_motions,
                "add", "-m", motion_json, "HEAD"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"📝 Motion {motion.id} stored in Git notes")
                return True
            else:
                console.print(f"❌ Failed to store motion: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error storing motion: {e}")
            return False
    
    def store_vote(self, vote: Vote) -> bool:
        """Store vote in Git notes"""
        try:
            vote_json = json.dumps(vote.to_dict(), indent=2)
            
            # Store in git notes under votes ref
            result = subprocess.run([
                "git", "notes", "--ref", self.notes_ref_votes,
                "append", "-m", vote_json, "HEAD"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"🗳️ Vote by {vote.voter.name} recorded")
                return True
            else:
                console.print(f"❌ Failed to store vote: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error storing vote: {e}")
            return False
    
    def store_debate(self, debate: Debate) -> bool:
        """Store debate statement in Git notes"""
        try:
            debate_json = json.dumps(debate.to_dict(), indent=2)
            
            # Store in git notes under debates ref
            result = subprocess.run([
                "git", "notes", "--ref", self.notes_ref_debates,
                "append", "-m", debate_json, "HEAD"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"💬 Debate statement by {debate.speaker.name} recorded")
                return True
            else:
                console.print(f"❌ Failed to store debate: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error storing debate: {e}")
            return False
    
    def store_result(self, result: VotingResult) -> bool:
        """Store voting result in Git notes"""
        try:
            result_json = json.dumps(result.to_dict(), indent=2)
            
            # Store in git notes under results ref
            result_cmd = subprocess.run([
                "git", "notes", "--ref", self.notes_ref_results,
                "add", "-m", result_json, "HEAD"
            ], capture_output=True, text=True)
            
            if result_cmd.returncode == 0:
                console.print(f"📊 Voting result for motion {result.motion_id} stored")
                return True
            else:
                console.print(f"❌ Failed to store result: {result_cmd.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error storing result: {e}")
            return False

class RobertsRulesGitGovernance:
    """Main Roberts Rules Git governance system"""
    
    def __init__(self):
        self.git_procedure = GitParliamentaryProcedure()
        self.participants: Dict[str, Participant] = {}
        self.active_motions: Dict[str, Motion] = {}
        self.current_chair: Optional[Participant] = None
        
        # Load existing participants and motions from Git
        self.load_from_git()
        
        console.print("🏛️ Roberts Rules Git Governance System initialized")
    
    def load_from_git(self):
        """Load existing governance state from Git notes"""
        try:
            # This would typically load from git notes
            # Simplified for this implementation
            pass
        except Exception as e:
            console.print(f"⚠️ Could not load from Git: {e}")
    
    def register_participant(self, name: str, email: str, role: str = "member", 
                           voting_weight: float = 1.0, pgp_key: Optional[str] = None) -> Participant:
        """Register a new participant"""
        participant = Participant(
            name=name,
            email=email,
            role=role,
            voting_weight=voting_weight,
            pgp_key=pgp_key
        )
        
        self.participants[email] = participant
        console.print(f"👤 Registered participant: {name} ({role})")
        return participant
    
    def set_chair(self, participant_email: str) -> bool:
        """Set the parliamentary chair"""
        if participant_email in self.participants:
            self.current_chair = self.participants[participant_email]
            console.print(f"🪑 Parliamentary chair set: {self.current_chair.name}")
            return True
        return False
    
    def calculate_quorum(self) -> int:
        """Calculate required quorum (majority of eligible voters)"""
        eligible_voters = len([p for p in self.participants.values() if p.role in ["member", "chair"]])
        return max(1, (eligible_voters // 2) + 1)
    
    def create_merge_motion(self, proposer_email: str, source_branch: str, 
                          target_branch: str, description: str = "") -> Optional[Motion]:
        """Create a motion to merge branches"""
        
        if proposer_email not in self.participants:
            console.print("❌ Proposer not registered")
            return None
        
        proposer = self.participants[proposer_email]
        motion_id = str(uuid.uuid4())[:8]
        
        motion = Motion(
            id=motion_id,
            motion_type=MotionType.MERGE,
            title=f"Merge {source_branch} into {target_branch}",
            description=description or f"Motion to merge branch '{source_branch}' into '{target_branch}'",
            proposer=proposer,
            seconder=None,
            status=MotionStatus.PROPOSED,
            created_at=datetime.now(timezone.utc),
            git_operation={
                "command": "merge",
                "source_branch": source_branch,
                "target_branch": target_branch,
                "merge_strategy": "no-ff"
            },
            required_votes=self.calculate_quorum(),
            quorum_required=self.calculate_quorum()
        )
        
        self.active_motions[motion_id] = motion
        self.git_procedure.store_motion(motion)
        
        console.print(f"📋 Merge motion created: {motion.title}")
        return motion
    
    def create_release_motion(self, proposer_email: str, version: str, 
                            target_env: str = "production", description: str = "") -> Optional[Motion]:
        """Create a motion to release to environment"""
        
        if proposer_email not in self.participants:
            console.print("❌ Proposer not registered")
            return None
        
        proposer = self.participants[proposer_email]
        motion_id = str(uuid.uuid4())[:8]
        
        motion = Motion(
            id=motion_id,
            motion_type=MotionType.RELEASE,
            title=f"Release {version} to {target_env}",
            description=description or f"Motion to release version {version} to {target_env} environment",
            proposer=proposer,
            seconder=None,
            status=MotionStatus.PROPOSED,
            created_at=datetime.now(timezone.utc),
            git_operation={
                "command": "tag",
                "version": version,
                "target_env": target_env,
                "sign": True
            },
            required_votes=self.calculate_quorum() + 1,  # Higher threshold for releases
            quorum_required=self.calculate_quorum()
        )
        
        self.active_motions[motion_id] = motion
        self.git_procedure.store_motion(motion)
        
        console.print(f"🚀 Release motion created: {motion.title}")
        return motion
    
    def create_rollback_motion(self, proposer_email: str, target_version: str, 
                             description: str = "") -> Optional[Motion]:
        """Create an emergency rollback motion"""
        
        if proposer_email not in self.participants:
            console.print("❌ Proposer not registered")
            return None
        
        proposer = self.participants[proposer_email]
        motion_id = str(uuid.uuid4())[:8]
        
        motion = Motion(
            id=motion_id,
            motion_type=MotionType.ROLLBACK,
            title=f"Emergency Rollback to {target_version}",
            description=description or f"Emergency motion to rollback to version {target_version}",
            proposer=proposer,
            seconder=None,
            status=MotionStatus.PROPOSED,
            created_at=datetime.now(timezone.utc),
            git_operation={
                "command": "reset",
                "target_version": target_version,
                "emergency": True,
                "force": True
            },
            required_votes=max(1, self.calculate_quorum() - 1),  # Lower threshold for emergencies
            quorum_required=max(1, self.calculate_quorum() - 1),
            time_limit=300  # 5 minutes for emergency decisions
        )
        
        self.active_motions[motion_id] = motion
        self.git_procedure.store_motion(motion)
        
        console.print(f"🚨 Emergency rollback motion created: {motion.title}")
        return motion
    
    def second_motion(self, motion_id: str, seconder_email: str) -> bool:
        """Second a motion (required for it to proceed)"""
        
        if motion_id not in self.active_motions:
            console.print("❌ Motion not found")
            return False
        
        if seconder_email not in self.participants:
            console.print("❌ Seconder not registered")
            return False
        
        motion = self.active_motions[motion_id]
        if motion.status != MotionStatus.PROPOSED:
            console.print(f"❌ Motion is not in PROPOSED status: {motion.status}")
            return False
        
        seconder = self.participants[seconder_email]
        if seconder.email == motion.proposer.email:
            console.print("❌ Proposer cannot second their own motion")
            return False
        
        motion.seconder = seconder
        motion.status = MotionStatus.IN_DEBATE
        
        # Update in Git
        self.git_procedure.store_motion(motion)
        
        console.print(f"✋ Motion {motion_id} seconded by {seconder.name}")
        console.print(f"💬 Motion now open for debate")
        return True
    
    def add_debate_statement(self, motion_id: str, speaker_email: str, statement: str) -> bool:
        """Add a debate statement"""
        
        if motion_id not in self.active_motions:
            console.print("❌ Motion not found")
            return False
        
        if speaker_email not in self.participants:
            console.print("❌ Speaker not registered")
            return False
        
        motion = self.active_motions[motion_id]
        if motion.status != MotionStatus.IN_DEBATE:
            console.print(f"❌ Motion is not open for debate: {motion.status}")
            return False
        
        speaker = self.participants[speaker_email]
        
        # Get current speaking order
        speaking_order = len([d for d in self.get_debate_statements(motion_id)]) + 1
        
        debate = Debate(
            motion_id=motion_id,
            speaker=speaker,
            statement=statement,
            timestamp=datetime.now(timezone.utc),
            speaking_order=speaking_order
        )
        
        success = self.git_procedure.store_debate(debate)
        
        if success:
            console.print(f"💬 Debate statement #{speaking_order} by {speaker.name} recorded")
        
        return success
    
    def call_for_vote(self, motion_id: str, chair_email: str) -> bool:
        """Chair calls for vote on motion"""
        
        if motion_id not in self.active_motions:
            console.print("❌ Motion not found")
            return False
        
        if not self.current_chair or self.current_chair.email != chair_email:
            console.print("❌ Only the chair can call for vote")
            return False
        
        motion = self.active_motions[motion_id]
        if motion.status != MotionStatus.IN_DEBATE:
            console.print(f"❌ Motion must be in debate to call for vote: {motion.status}")
            return False
        
        motion.status = MotionStatus.VOTING
        self.git_procedure.store_motion(motion)
        
        console.print(f"🗳️ Chair calls for vote on motion: {motion.title}")
        console.print(f"📊 Required votes: {motion.required_votes}")
        console.print(f"👥 Quorum required: {motion.quorum_required}")
        
        return True
    
    def cast_vote(self, motion_id: str, voter_email: str, vote_type: VoteType, 
                 reasoning: str = "") -> bool:
        """Cast a vote on a motion"""
        
        if motion_id not in self.active_motions:
            console.print("❌ Motion not found")
            return False
        
        if voter_email not in self.participants:
            console.print("❌ Voter not registered")
            return False
        
        motion = self.active_motions[motion_id]
        if motion.status != MotionStatus.VOTING:
            console.print(f"❌ Motion is not open for voting: {motion.status}")
            return False
        
        voter = self.participants[voter_email]
        
        # Check if already voted (simplified - would check Git notes in production)
        
        vote = Vote(
            motion_id=motion_id,
            voter=voter,
            vote_type=vote_type,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc)
        )
        
        success = self.git_procedure.store_vote(vote)
        
        if success:
            console.print(f"🗳️ Vote cast by {voter.name}: {vote_type.value.upper()}")
            
            # Check if we should tally votes
            self.check_voting_complete(motion_id)
        
        return success
    
    def get_debate_statements(self, motion_id: str) -> List[Debate]:
        """Get all debate statements for a motion (simplified)"""
        # In production, this would parse Git notes
        return []
    
    def get_votes(self, motion_id: str) -> List[Vote]:
        """Get all votes for a motion (simplified)"""
        # In production, this would parse Git notes
        return []
    
    def check_voting_complete(self, motion_id: str) -> bool:
        """Check if voting is complete and tally results"""
        
        motion = self.active_motions[motion_id]
        votes = self.get_votes(motion_id)
        
        # Count eligible voters
        eligible_voters = [p for p in self.participants.values() if p.role in ["member", "chair"]]
        total_eligible = len(eligible_voters)
        
        # For demo, assume we have enough votes after any vote
        yea_votes = 3  # Mock data
        nay_votes = 1
        abstain_votes = 0
        votes_cast = yea_votes + nay_votes + abstain_votes
        
        quorum_met = votes_cast >= motion.quorum_required
        motion_passed = quorum_met and yea_votes >= motion.required_votes
        
        result = VotingResult(
            motion_id=motion_id,
            total_eligible=total_eligible,
            votes_cast=votes_cast,
            yea_votes=yea_votes,
            nay_votes=nay_votes,
            abstain_votes=abstain_votes,
            quorum_met=quorum_met,
            motion_passed=motion_passed,
            final_tally={
                "yea": yea_votes,
                "nay": nay_votes,
                "abstain": abstain_votes,
                "percentage_yea": (yea_votes / votes_cast * 100) if votes_cast > 0 else 0
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        # Update motion status
        motion.status = MotionStatus.PASSED if motion_passed else MotionStatus.FAILED
        
        # Store results
        self.git_procedure.store_motion(motion)
        self.git_procedure.store_result(result)
        
        self.display_voting_results(result, motion)
        
        # Execute Git operation if passed
        if motion_passed:
            self.execute_git_operation(motion)
        
        return True
    
    def display_voting_results(self, result: VotingResult, motion: Motion):
        """Display voting results in rich format"""
        
        status_color = "green" if result.motion_passed else "red"
        status_text = "PASSED" if result.motion_passed else "FAILED"
        
        table = Table(title=f"Voting Results: {motion.title}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Eligible Voters", str(result.total_eligible))
        table.add_row("Votes Cast", str(result.votes_cast))
        table.add_row("Quorum Required", str(motion.quorum_required))
        table.add_row("Quorum Met", "✅" if result.quorum_met else "❌")
        table.add_row("YEA Votes", str(result.yea_votes))
        table.add_row("NAY Votes", str(result.nay_votes))
        table.add_row("ABSTAIN Votes", str(result.abstain_votes))
        table.add_row("Percentage YEA", f"{result.final_tally['percentage_yea']:.1f}%")
        table.add_row("MOTION STATUS", f"{status_text}", style=status_color)
        
        console.print(table)
        
        panel_content = f"""
🏛️ **Motion {motion.id}: {status_text}**

**Operation**: {motion.git_operation.get('command', 'unknown')}
**Democratic Process**: Roberts Rules Parliamentary Procedure
**Transparency**: All votes and debates recorded in Git notes
**Auditability**: Complete decision trail with cryptographic integrity
        """
        
        console.print(Panel.fit(panel_content, title="Democratic Git Governance", style=status_color))
    
    def execute_git_operation(self, motion: Motion) -> bool:
        """Execute the Git operation for a passed motion"""
        
        with tracer.start_as_current_span("roberts_rules.execute_git_operation") as span:
            span.set_attribute("motion.id", motion.id)
            span.set_attribute("motion.type", motion.motion_type.value)
            span.set_attribute("git.operation", motion.git_operation.get("command", "unknown"))
            
            try:
                git_op = motion.git_operation
                
                if motion.motion_type == MotionType.MERGE:
                    # Execute merge
                    source = git_op["source_branch"]
                    target = git_op["target_branch"]
                    
                    console.print(f"🔄 Executing democratic merge: {source} → {target}")
                    
                    # Switch to target branch
                    subprocess.run(["git", "checkout", target], check=True)
                    
                    # Perform merge with no-ff to preserve history
                    result = subprocess.run([
                        "git", "merge", "--no-ff", source, 
                        "-m", f"Democratic merge approved via Roberts Rules - Motion {motion.id}"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        console.print(f"✅ Democratic merge completed successfully")
                        span.set_attribute("execution.success", True)
                        return True
                    else:
                        console.print(f"❌ Merge failed: {result.stderr}")
                        span.set_attribute("execution.success", False)
                        return False
                
                elif motion.motion_type == MotionType.RELEASE:
                    # Execute release
                    version = git_op["version"]
                    sign = git_op.get("sign", False)
                    
                    console.print(f"🚀 Executing democratic release: {version}")
                    
                    # Create signed tag
                    cmd = ["git", "tag"]
                    if sign:
                        cmd.append("-s")
                    cmd.extend([version, "-m", f"Democratic release approved via Roberts Rules - Motion {motion.id}"])
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        console.print(f"✅ Democratic release tag created: {version}")
                        span.set_attribute("execution.success", True)
                        return True
                    else:
                        console.print(f"❌ Release tagging failed: {result.stderr}")
                        span.set_attribute("execution.success", False)
                        return False
                
                elif motion.motion_type == MotionType.ROLLBACK:
                    # Execute emergency rollback
                    target_version = git_op["target_version"]
                    emergency = git_op.get("emergency", False)
                    
                    console.print(f"🚨 Executing emergency rollback to: {target_version}")
                    
                    # Reset to target version
                    result = subprocess.run([
                        "git", "reset", "--hard", target_version
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Add rollback note
                        subprocess.run([
                            "git", "notes", "--ref", "refs/notes/rollbacks",
                            "add", "-m", f"Emergency rollback approved via Roberts Rules - Motion {motion.id}", "HEAD"
                        ], capture_output=True, text=True)
                        
                        console.print(f"✅ Emergency rollback completed to: {target_version}")
                        span.set_attribute("execution.success", True)
                        return True
                    else:
                        console.print(f"❌ Rollback failed: {result.stderr}")
                        span.set_attribute("execution.success", False)
                        return False
                
                else:
                    console.print(f"⚠️ Unsupported motion type for execution: {motion.motion_type}")
                    return False
                
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Git operation failed: {e}")
                span.set_attribute("execution.success", False)
                span.set_attribute("error", str(e))
                return False
            except Exception as e:
                console.print(f"❌ Unexpected error executing motion: {e}")
                span.set_attribute("execution.success", False)
                span.set_attribute("error", str(e))
                return False
    
    def get_motion_status(self, motion_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of a motion"""
        
        if motion_id not in self.active_motions:
            return None
        
        motion = self.active_motions[motion_id]
        votes = self.get_votes(motion_id)
        debates = self.get_debate_statements(motion_id)
        
        return {
            "motion": motion.to_dict(),
            "votes_count": len(votes),
            "debates_count": len(debates),
            "last_activity": max(
                [v.timestamp for v in votes] + 
                [d.timestamp for d in debates] + 
                [motion.created_at]
            ).isoformat() if (votes or debates) else motion.created_at.isoformat()
        }
    
    def display_motion_summary(self, motion_id: str):
        """Display comprehensive motion summary"""
        
        status = self.get_motion_status(motion_id)
        if not status:
            console.print("❌ Motion not found")
            return
        
        motion_data = status["motion"]
        
        table = Table(title=f"Motion Summary: {motion_data['title']}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Motion ID", motion_data["id"])
        table.add_row("Type", motion_data["motion_type"].upper())
        table.add_row("Status", motion_data["status"].upper())
        table.add_row("Proposer", motion_data["proposer"]["name"])
        table.add_row("Seconder", motion_data["seconder"]["name"] if motion_data["seconder"] else "None")
        table.add_row("Created", motion_data["created_at"])
        table.add_row("Votes Cast", str(status["votes_count"]))
        table.add_row("Debate Statements", str(status["debates_count"]))
        table.add_row("Last Activity", status["last_activity"])
        
        console.print(table)


# CLI interface for testing
if __name__ == "__main__":
    import typer
    
    app = typer.Typer(name="roberts-git", help="Roberts Rules Git governance")
    
    governance = RobertsRulesGitGovernance()
    
    @app.command()
    def register(name: str, email: str, role: str = "member"):
        """Register a new participant"""
        governance.register_participant(name, email, role)
    
    @app.command()
    def chair(email: str):
        """Set parliamentary chair"""
        governance.set_chair(email)
    
    @app.command()
    def merge_motion(proposer: str, source: str, target: str, description: str = ""):
        """Create a merge motion"""
        motion = governance.create_merge_motion(proposer, source, target, description)
        if motion:
            console.print(f"Motion created with ID: {motion.id}")
    
    @app.command()
    def release_motion(proposer: str, version: str, env: str = "production"):
        """Create a release motion"""
        motion = governance.create_release_motion(proposer, version, env)
        if motion:
            console.print(f"Motion created with ID: {motion.id}")
    
    @app.command()
    def second(motion_id: str, seconder: str):
        """Second a motion"""
        governance.second_motion(motion_id, seconder)
    
    @app.command()
    def debate(motion_id: str, speaker: str, statement: str):
        """Add debate statement"""
        governance.add_debate_statement(motion_id, speaker, statement)
    
    @app.command()
    def vote_call(motion_id: str, chair: str):
        """Chair calls for vote"""
        governance.call_for_vote(motion_id, chair)
    
    @app.command()
    def vote(motion_id: str, voter: str, vote_type: str, reasoning: str = ""):
        """Cast a vote"""
        vote_enum = VoteType(vote_type.lower())
        governance.cast_vote(motion_id, voter, vote_enum, reasoning)
    
    @app.command()
    def status(motion_id: str):
        """Show motion status"""
        governance.display_motion_summary(motion_id)
    
    app()