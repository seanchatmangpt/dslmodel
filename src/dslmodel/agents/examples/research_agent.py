"""Research agent that analyzes work items and gathers information."""

from enum import Enum, auto
from typing import Optional
import random

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class ResearchState(Enum):
    """States for the research agent workflow."""
    IDLE = auto()
    ANALYZING = auto()
    RESEARCHING = auto()
    DOCUMENTING = auto()
    COMPLETE = auto()


class ResearchAgent(SwarmAgent):
    """
    Research agent that analyzes work items and performs background research.
    
    This agent monitors work claims and automatically starts research tasks
    to support the team with relevant information.
    """
    
    StateEnum = ResearchState
    TRIGGER_MAP = {
        "work.claim": "start_analysis",
        "work.list": "analyze_workload",
        "work.progress": "update_research",
        "work.stats": "generate_report"
    }
    
    def setup_triggers(self):
        """Define state transitions for research workflow."""
        pass  # Triggers defined as decorators
    
    @trigger(source=ResearchState.IDLE, dest=ResearchState.ANALYZING)
    def start_analysis(self, span: SpanData) -> Optional[NextCommand]:
        """
        Start analyzing when new work is claimed.
        """
        work_type = span.attributes.get("type", "unknown")
        priority = span.attributes.get("priority", "medium")
        
        print(f"🔬 Research Agent: Analyzing new {work_type} (priority: {priority})")
        
        # Simulate different research paths based on work type
        if work_type == "bug":
            return NextCommand(
                path=["work", "list"],
                args=["--status", "completed", "--format", "json"],
                description="Research similar completed bugs"
            )
        else:
            return NextCommand(
                path=["work", "stats"],
                args=["--team", span.attributes.get("team", "default")],
                description="Analyze team workload and capacity"
            )
    
    @trigger(source=ResearchState.ANALYZING, dest=ResearchState.RESEARCHING)
    def analyze_workload(self, span: SpanData) -> Optional[NextCommand]:
        """
        Analyze team workload and determine research priorities.
        """
        count = span.attributes.get("count", 0)
        print(f"📈 Research Agent: Found {count} related items to analyze")
        
        # Simulate research decision
        if count > 5:
            print("   ⚠️  High workload detected - prioritizing automation research")
        
        return None  # Could trigger external research APIs here
    
    @trigger(source=ResearchState.RESEARCHING, dest=ResearchState.DOCUMENTING)
    def update_research(self, span: SpanData) -> Optional[NextCommand]:
        """
        Update research based on work progress.
        """
        progress = span.attributes.get("progress", 0)
        work_id = span.attributes.get("work_id", "unknown")
        
        print(f"📚 Research Agent: Work {work_id} at {progress}% - updating research docs")
        
        # Could trigger document generation or knowledge base updates
        return None
    
    @trigger(source=[ResearchState.ANALYZING, ResearchState.RESEARCHING], 
             dest=ResearchState.DOCUMENTING)
    def generate_report(self, span: SpanData) -> Optional[NextCommand]:
        """
        Generate research report based on statistics.
        """
        total = span.attributes.get("total", 0)
        completed = span.attributes.get("completed", 0)
        
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"📊 Research Agent: Team completion rate: {completion_rate:.1f}%")
            
            # Provide insights based on data
            if completion_rate < 50:
                print("   💡 Recommendation: Consider task prioritization workshop")
            elif completion_rate > 80:
                print("   🎯 Excellent progress! Team is highly effective")
        
        return None