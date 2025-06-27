"""Scrum-at-Scale delivery agent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class ScrumState(Enum):
    """Scrum sprint lifecycle states."""
    PLANNING = auto()
    EXECUTING = auto()
    REVIEW = auto()
    RETRO = auto()


class ScrumAgent(SwarmAgent):
    """
    Delivery agent implementing Scrum-at-Scale framework.
    
    Manages sprint planning, execution, reviews, and retrospectives.
    Integrates with optimization frameworks when KPIs indicate issues.
    """
    
    StateEnum = ScrumState
    LISTEN_FILTER = "swarmsh.scrum."
    TRIGGER_MAP = {
        "plan": "plan",
        "daily": "daily",
        "review": "review",
        "retro": "retro",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass
    
    @trigger(source=ScrumState.PLANNING, dest=ScrumState.EXECUTING)
    def plan(self, span: SpanData) -> Optional[NextCommand]:
        """
        Handle sprint planning phase.
        
        Transitions from PLANNING to EXECUTING state.
        """
        sprint_number = span.attributes.get("sprint_number", "1")
        team_id = span.attributes.get("team_id", "default")
        capacity = span.attributes.get("capacity", 40)  # story points
        
        self._transition(f"Planning sprint {sprint_number} for team {team_id} with capacity {capacity}", 
                        ScrumState.EXECUTING)
        
        # Could return command to populate sprint backlog
        return NextCommand(
            fq_name="swarmsh.scrum.backlog-populate",
            args=["--sprint", str(sprint_number), "--team", team_id, "--capacity", str(capacity)],
            description="Populate sprint backlog based on priorities"
        )
    
    def daily(self, span: SpanData) -> Optional[NextCommand]:
        """
        Handle daily standup events.
        
        No state change - dailies happen during EXECUTING state.
        """
        blockers = span.attributes.get("blockers", [])
        
        if blockers:
            # Could trigger escalation or help requests
            return NextCommand(
                fq_name="swarmsh.scrum.escalate-blockers",
                args=["--blockers", ",".join(blockers)],
                description="Escalate blockers to scrum of scrums"
            )
        
        return None
    
    @trigger(source=ScrumState.EXECUTING, dest=ScrumState.REVIEW)
    def review(self, span: SpanData) -> Optional[NextCommand]:
        """
        Handle sprint review phase.
        
        Analyzes KPIs and may trigger optimization if issues detected.
        """
        sprint_number = span.attributes.get("sprint_number")
        velocity = span.attributes.get("velocity", 0)
        defect_rate = span.attributes.get("defect_rate", 0)
        customer_satisfaction = span.attributes.get("customer_satisfaction", 0)
        
        self._transition(f"Reviewing sprint {sprint_number}: velocity={velocity}, defects={defect_rate}%", 
                        ScrumState.REVIEW)
        
        # If KPI gap detected, spawn Lean project
        if defect_rate > 3:  # 3% threshold
            return NextCommand(
                fq_name="swarmsh.lean.define",
                args=[
                    "--project-id", f"defect-sprint{sprint_number}",
                    "--problem-statement", f"Defect rate {defect_rate}% exceeds 3% threshold",
                    "--sponsor", "scrum-agent"
                ],
                description="Initiate Lean Six Sigma project for quality improvement"
            )
        
        return None
    
    @trigger(source=ScrumState.REVIEW, dest=ScrumState.RETRO)
    def retro(self, span: SpanData) -> Optional[NextCommand]:
        """
        Handle sprint retrospective phase.
        
        Captures lessons learned and improvement actions.
        """
        sprint_number = span.attributes.get("sprint_number")
        improvements = span.attributes.get("improvements", [])
        
        self._transition(f"Retrospective for sprint {sprint_number} with {len(improvements)} improvements", 
                        ScrumState.RETRO)
        
        if improvements:
            # Could create improvement backlog items
            return NextCommand(
                fq_name="swarmsh.scrum.improvement-backlog",
                args=["--sprint", str(sprint_number), "--items", ",".join(improvements)],
                description="Add retrospective improvements to backlog"
            )
        
        return None


if __name__ == "__main__":
    ScrumAgent().run()