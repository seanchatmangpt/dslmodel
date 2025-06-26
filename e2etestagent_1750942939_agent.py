"""Generated E2ETestAgent_1750942939 SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class E2ETestAgent_1750942939State(Enum):
    INIT = auto()
    PROCESSING = auto()
    COMPLETE = auto()

class E2ETestAgent_1750942939Agent(SwarmAgent):
    """
    E2ETestAgent_1750942939 agent for handling start, process, finish workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = E2ETestAgent_1750942939State
    LISTEN_FILTER = "swarmsh.e2etestagent_1750942939."
    TRIGGER_MAP = {
        "start": "on_start",
        "process": "on_process",
        "finish": "on_finish",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass

    @trigger(source=E2ETestAgent_1750942939State.INIT, dest=E2ETestAgent_1750942939State.PROCESSING)
    def on_start(self, span: SpanData) -> Optional[NextCommand]:
        """Handle start trigger."""
        self._transition(f"Processing start from {span.attributes.get('source', 'unknown')}", 
                        E2ETestAgent_1750942939State.PROCESSING)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.e2etestagent_1750942939.start",
            args=["--span-id", span.span_id],
            description=f"Execute start action"
        )

    @trigger(source=E2ETestAgent_1750942939State.PROCESSING, dest=E2ETestAgent_1750942939State.COMPLETE)
    def on_process(self, span: SpanData) -> Optional[NextCommand]:
        """Handle process trigger."""
        self._transition(f"Processing process from {span.attributes.get('source', 'unknown')}", 
                        E2ETestAgent_1750942939State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.e2etestagent_1750942939.process",
            args=["--span-id", span.span_id],
            description=f"Execute process action"
        )

    @trigger(source=E2ETestAgent_1750942939State.COMPLETE, dest=E2ETestAgent_1750942939State.COMPLETE)
    def on_finish(self, span: SpanData) -> Optional[NextCommand]:
        """Handle finish trigger."""
        self._transition(f"Processing finish from {span.attributes.get('source', 'unknown')}", 
                        E2ETestAgent_1750942939State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.e2etestagent_1750942939.finish",
            args=["--span-id", span.span_id],
            description=f"Execute finish action"
        )


if __name__ == "__main__":
    E2ETestAgent_1750942939Agent().run()
