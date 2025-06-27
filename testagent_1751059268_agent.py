"""Generated TestAgent_1751059268 SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class TestAgent_1751059268State(Enum):
    IDLE = auto()
    ACTIVE = auto()
    COMPLETE = auto()

class TestAgent_1751059268Agent(SwarmAgent):
    """
    TestAgent_1751059268 agent for handling start, work, finish workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = TestAgent_1751059268State
    LISTEN_FILTER = "swarmsh.testagent_1751059268."
    TRIGGER_MAP = {
        "start": "on_start",
        "work": "on_work",
        "finish": "on_finish",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass

    @trigger(source=TestAgent_1751059268State.IDLE, dest=TestAgent_1751059268State.ACTIVE)
    def on_start(self, span: SpanData) -> Optional[NextCommand]:
        """Handle start trigger."""
        self._transition(f"Processing start from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1751059268State.ACTIVE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1751059268.start",
            args=["--span-id", span.span_id],
            description=f"Execute start action"
        )

    @trigger(source=TestAgent_1751059268State.ACTIVE, dest=TestAgent_1751059268State.COMPLETE)
    def on_work(self, span: SpanData) -> Optional[NextCommand]:
        """Handle work trigger."""
        self._transition(f"Processing work from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1751059268State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1751059268.work",
            args=["--span-id", span.span_id],
            description=f"Execute work action"
        )

    @trigger(source=TestAgent_1751059268State.COMPLETE, dest=TestAgent_1751059268State.COMPLETE)
    def on_finish(self, span: SpanData) -> Optional[NextCommand]:
        """Handle finish trigger."""
        self._transition(f"Processing finish from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1751059268State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1751059268.finish",
            args=["--span-id", span.span_id],
            description=f"Execute finish action"
        )


if __name__ == "__main__":
    TestAgent_1751059268Agent().run()
