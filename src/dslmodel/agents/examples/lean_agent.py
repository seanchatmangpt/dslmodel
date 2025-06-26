"""DFLSS (Design for Lean Six Sigma) optimization agent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class LeanState(Enum):
    """DMAIC phases for Lean Six Sigma."""
    DEFINE = auto()
    MEASURE = auto()
    ANALYZE = auto()
    IMPROVE = auto()
    CONTROL = auto()


class LeanAgent(SwarmAgent):
    """
    Optimization agent implementing DFLSS (Design for Lean Six Sigma).
    
    Manages DMAIC projects to improve processes based on KPI gaps.
    Integrates with governance for permanent process changes.
    """
    
    StateEnum = LeanState
    LISTEN_FILTER = "swarmsh.lean."
    TRIGGER_MAP = {
        "define": "define",
        "measure": "measure",
        "analyze": "analyze",
        "improve": "improve",
        "control": "control",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass
    
    @trigger(source=LeanState.DEFINE, dest=LeanState.MEASURE)
    def define(self, span: SpanData) -> Optional[NextCommand]:
        """
        Define phase - establish project charter and scope.
        
        Triggered when KPI gaps are detected by other agents.
        """
        project_id = span.attributes.get("project_id", "lean-001")
        problem_statement = span.attributes.get("problem_statement", "Unknown issue")
        sponsor = span.attributes.get("sponsor", "management")
        
        self._transition(f"Defining project {project_id}: {problem_statement}", 
                        LeanState.MEASURE)
        
        # Create project charter
        return NextCommand(
            fq_name="swarmsh.lean.create-charter",
            args=[
                "--project-id", project_id,
                "--problem", problem_statement,
                "--sponsor", sponsor,
                "--target-completion", "30-days"
            ],
            description="Create Lean Six Sigma project charter"
        )
    
    @trigger(source=LeanState.MEASURE, dest=LeanState.ANALYZE)
    def measure(self, span: SpanData) -> Optional[NextCommand]:
        """
        Measure phase - collect baseline data and metrics.
        
        Establishes current state performance.
        """
        project_id = span.attributes.get("project_id")
        metrics = span.attributes.get("metrics", {})
        
        self._transition(f"Measuring baseline for {project_id}", 
                        LeanState.ANALYZE)
        
        # Collect process metrics
        return NextCommand(
            fq_name="swarmsh.lean.collect-metrics",
            args=[
                "--project-id", project_id,
                "--duration", "7-days",
                "--metrics", ",".join(metrics.keys()) if metrics else "all"
            ],
            description="Collect baseline process metrics"
        )
    
    @trigger(source=LeanState.ANALYZE, dest=LeanState.IMPROVE)
    def analyze(self, span: SpanData) -> Optional[NextCommand]:
        """
        Analyze phase - identify root causes and improvement opportunities.
        
        Uses statistical analysis and process mapping.
        """
        project_id = span.attributes.get("project_id")
        root_causes = span.attributes.get("root_causes", [])
        
        self._transition(f"Analyzing root causes for {project_id}: {root_causes}", 
                        LeanState.IMPROVE)
        
        # Run root cause analysis
        return NextCommand(
            fq_name="swarmsh.lean.root-cause-analysis",
            args=[
                "--project-id", project_id,
                "--method", "fishbone",
                "--participants", "cross-functional-team"
            ],
            description="Conduct root cause analysis session"
        )
    
    @trigger(source=LeanState.IMPROVE, dest=LeanState.CONTROL)
    def improve(self, span: SpanData) -> Optional[NextCommand]:
        """
        Improve phase - implement and validate solutions.
        
        Pilots improvements and measures results.
        """
        project_id = span.attributes.get("project_id")
        improvements = span.attributes.get("improvements", [])
        pilot_results = span.attributes.get("pilot_results", {})
        
        self._transition(f"Implementing improvements for {project_id}", 
                        LeanState.CONTROL)
        
        # If pilot successful, prepare for control phase
        if pilot_results.get("success", False):
            return NextCommand(
                fq_name="swarmsh.lean.prepare-control-plan",
                args=[
                    "--project-id", project_id,
                    "--improvements", ",".join(improvements),
                    "--savings", str(pilot_results.get("savings", 0))
                ],
                description="Prepare control plan for sustained improvements"
            )
        
        return None
    
    @trigger(source=LeanState.CONTROL, dest=LeanState.DEFINE)
    def control(self, span: SpanData) -> Optional[NextCommand]:
        """
        Control phase - sustain improvements and institutionalize changes.
        
        Integrates with governance for permanent process changes.
        """
        project_id = span.attributes.get("project_id")
        control_plan = span.attributes.get("control_plan", {})
        process_changes = span.attributes.get("process_changes", [])
        
        self._transition(f"Establishing controls for {project_id}", 
                        LeanState.DEFINE)  # Ready for next project
        
        # Flag governance layer to ratify permanent change
        if process_changes:
            return NextCommand(
                fq_name="swarmsh.roberts.voting",
                args=[
                    "--motion-id", f"process_change_{project_id}",
                    "--voting-method", "voice_vote",
                    "--description", f"Ratify process improvements from {project_id}"
                ],
                description="Request governance approval for process changes"
            )
        
        return None


if __name__ == "__main__":
    LeanAgent().run()