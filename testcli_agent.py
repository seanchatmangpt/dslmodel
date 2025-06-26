"""Generated TestCLI SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class TestCLIState(Enum):
    INIT = auto()
    WORK = auto()
    DONE = auto()

class TestCLIAgent(SwarmAgent):
    """
    TestCLI agent for handling start, process, finish workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = TestCLIState
    LISTEN_FILTER = "swarmsh.testcli."
    TRIGGER_MAP = {
        "start": "on_start",
        "process": "on_process",
        "finish": "on_finish",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass

    @trigger(source=TestCLIState.INIT, dest=TestCLIState.WORK)
    def on_start(self, span: SpanData) -> Optional[NextCommand]:
        """Handle start trigger."""
        self._transition(f"Processing start from {span.attributes.get('source', 'unknown')}", 
                        TestCLIState.WORK)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testcli.start",
            args=["--span-id", span.span_id],
            description=f"Execute start action"
        )

    @trigger(source=TestCLIState.WORK, dest=TestCLIState.DONE)
    def on_process(self, span: SpanData) -> Optional[NextCommand]:
        """Handle process trigger."""
        self._transition(f"Processing process from {span.attributes.get('source', 'unknown')}", 
                        TestCLIState.DONE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testcli.process",
            args=["--span-id", span.span_id],
            description=f"Execute process action"
        )

    @trigger(source=TestCLIState.DONE, dest=TestCLIState.DONE)
    def on_finish(self, span: SpanData) -> Optional[NextCommand]:
        """Handle finish trigger."""
        self._transition(f"Processing finish from {span.attributes.get('source', 'unknown')}", 
                        TestCLIState.DONE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testcli.finish",
            args=["--span-id", span.span_id],
            description=f"Execute finish action"
        )


if __name__ == "__main__":
    TestCLIAgent().run()
