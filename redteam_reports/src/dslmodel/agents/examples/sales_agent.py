"""Example sales agent implementation."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class SalesState(Enum):
    """States for the sales agent workflow."""
    INIT = auto()
    RESEARCH = auto()
    OUTREACH = auto()
    CLOSE = auto()
    DONE = auto()


class SalesAgent(SwarmAgent):
    """
    Example sales agent that progresses through a sales workflow
    based on work item telemetry spans.
    """
    
    StateEnum = SalesState
    TRIGGER_MAP = {
        "work.claim": "research",
        "work.progress": "outreach", 
        "work.complete": "close",
        "work.list": "check_pipeline"
    }
    
    def setup_triggers(self):
        """Define state transitions for sales workflow."""
        pass  # Triggers are defined as decorators on methods
    
    @trigger(source=SalesState.INIT, dest=SalesState.RESEARCH)
    def research(self, span: SpanData) -> Optional[NextCommand]:
        """
        Start research phase when work is claimed.
        Lists available work items to analyze.
        """
        print(f"🔍 Sales Agent: Starting research for {span.attributes.get('work_id', 'unknown')}")
        return NextCommand(
            path=["work", "list"],
            args=["--format", "json"] if "json" in str(self.cli_command) else [],
            description="List all work items to identify opportunities"
        )
    
    @trigger(source=SalesState.RESEARCH, dest=SalesState.OUTREACH)
    def outreach(self, span: SpanData) -> Optional[NextCommand]:
        """
        Progress to outreach when work progresses.
        Updates work item with sales activity.
        """
        work_id = span.attributes.get("work_id", "dummy")
        progress = span.attributes.get("progress", 50)
        
        print(f"📧 Sales Agent: Initiating outreach for {work_id} at {progress}%")
        return NextCommand(
            path=["work", "progress"],
            args=[work_id, str(min(progress + 25, 90))],
            description="Update progress with outreach activities"
        )
    
    @trigger(source=SalesState.OUTREACH, dest=SalesState.CLOSE)
    def close(self, span: SpanData) -> Optional[NextCommand]:
        """
        Close the deal when work is marked complete.
        Finalizes the work item with success metrics.
        """
        work_id = span.attributes.get("work_id", "dummy")
        print(f"🎯 Sales Agent: Closing deal for {work_id}")
        
        return NextCommand(
            path=["work", "complete"],
            args=[work_id, "success", "10"],  # work_id, status, score
            description="Mark work item as successfully closed"
        )
    
    @trigger(source=SalesState.CLOSE, dest=SalesState.DONE)
    def finalize(self, span: SpanData) -> Optional[NextCommand]:
        """Final state - no more actions."""
        print(f"✅ Sales Agent: Workflow complete for {span.attributes.get('work_id', 'unknown')}")
        return None
    
    def check_pipeline(self, span: SpanData) -> Optional[NextCommand]:
        """
        Check pipeline status without state change.
        Can be called from any state.
        """
        print("📊 Sales Agent: Checking sales pipeline")
        return NextCommand(
            path=["work", "stats"],
            args=["--team", "sales"],
            description="Get sales team statistics"
        )