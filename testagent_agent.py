"""Generated TestAgent SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class TestAgentState(Enum):
    INIT = auto()
    PROCESS = auto()
    DONE = auto()

class TestAgentAgent(SwarmAgent):
    """
    TestAgent agent for handling start, work, complete workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = TestAgentState
    LISTEN_FILTER = "swarmsh.testagent."
    TRIGGER_MAP = {
        "start": "on_start",
        "work": "on_work",
        "complete": "on_complete",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass

    @trigger(source=TestAgentState.INIT, dest=TestAgentState.PROCESS)
    def on_start(self, span: SpanData) -> Optional[NextCommand]:
        """Handle start trigger."""
        self._transition(f"Processing start from {span.attributes.get('source', 'unknown')}", 
                        TestAgentState.PROCESS)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent.start",
            args=["--span-id", span.span_id],
            description=f"Execute start action"
        )

    @trigger(source=TestAgentState.PROCESS, dest=TestAgentState.DONE)
    def on_work(self, span: SpanData) -> Optional[NextCommand]:
        """Handle work trigger."""
        self._transition(f"Processing work from {span.attributes.get('source', 'unknown')}", 
                        TestAgentState.DONE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent.work",
            args=["--span-id", span.span_id],
            description=f"Execute work action"
        )

    @trigger(source=TestAgentState.DONE, dest=TestAgentState.DONE)
    def on_complete(self, span: SpanData) -> Optional[NextCommand]:
        """Handle complete trigger."""
        self._transition(f"Processing complete from {span.attributes.get('source', 'unknown')}", 
                        TestAgentState.DONE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent.complete",
            args=["--span-id", span.span_id],
            description=f"Execute complete action"
        )


if __name__ == "__main__":
    TestAgentAgent().run()
