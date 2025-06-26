"""Roberts Rules of Order governance agent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class RorState(Enum):
    """Roberts Rules meeting states."""
    IDLE = auto()
    MOTION_OPEN = auto()
    VOTING = auto()
    CLOSED = auto()


class RobertsAgent(SwarmAgent):
    """
    Governance agent implementing Roberts Rules of Order.
    
    Manages formal meeting procedures, motions, and voting processes.
    Integrates with delivery frameworks when decisions are made.
    """
    
    StateEnum = RorState
    LISTEN_FILTER = "swarmsh.roberts."
    TRIGGER_MAP = {
        "open": "open_motion",
        "vote": "call_vote",
        "close": "adjourn",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass
    
    @trigger(source=RorState.IDLE, dest=RorState.MOTION_OPEN)
    def open_motion(self, span: SpanData) -> Optional[NextCommand]:
        """
        Open a new motion for consideration.
        
        Transitions to MOTION_OPEN state and calls meeting to order.
        """
        motion_id = span.attributes.get("motion_id", "unknown")
        meeting_id = span.attributes.get("meeting_id", "board")
        
        self._transition(f"Opening motion {motion_id} in meeting {meeting_id}", 
                        RorState.MOTION_OPEN)
        
        return NextCommand(
            fq_name="swarmsh.roberts.call-to-order",
            args=["--meeting-id", meeting_id, "--motion-id", motion_id],
            description="Call meeting to order for new motion"
        )
    
    @trigger(source=RorState.MOTION_OPEN, dest=RorState.VOTING)
    def call_vote(self, span: SpanData) -> Optional[NextCommand]:
        """
        Call for a vote on the open motion.
        
        Transitions to VOTING state and initiates voting process.
        """
        motion_id = span.attributes.get("motion_id", "sprint42")
        voting_method = span.attributes.get("voting_method", "ballot")
        
        self._transition(f"Calling vote on motion {motion_id} via {voting_method}", 
                        RorState.VOTING)
        
        return NextCommand(
            fq_name="swarmsh.roberts.voting",
            args=["--motion-id", motion_id, "--voting-method", voting_method],
            description=f"Initiate {voting_method} vote on motion"
        )
    
    @trigger(source=RorState.VOTING, dest=RorState.CLOSED)
    def adjourn(self, span: SpanData) -> Optional[NextCommand]:
        """
        Close the meeting after vote completion.
        
        If vote passes, can trigger downstream delivery processes.
        """
        motion_id = span.attributes.get("motion_id")
        vote_result = span.attributes.get("result", "unknown")
        votes_yes = span.attributes.get("votes_yes", 0)
        votes_no = span.attributes.get("votes_no", 0)
        
        self._transition(f"Adjourning after vote on {motion_id}: {vote_result}", 
                        RorState.CLOSED)
        
        # If vote passed and it's a sprint motion, trigger Scrum planning
        if vote_result == "passed" and "sprint" in str(motion_id).lower():
            sprint_number = span.attributes.get("sprint_number", "42")
            team_id = span.attributes.get("team_id", "alpha")
            
            return NextCommand(
                fq_name="swarmsh.scrum.sprint-planning",
                args=["--sprint-number", str(sprint_number), "--team-id", team_id],
                description="Initiate sprint planning after governance approval"
            )
        
        return None


if __name__ == "__main__":
    RobertsAgent().run()