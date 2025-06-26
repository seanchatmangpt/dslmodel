"""Generated TestAgent_1750926106 SwarmAgent."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class TestAgent_1750926106State(Enum):
    IDLE = auto()
    ACTIVE = auto()
    COMPLETE = auto()

class TestAgent_1750926106Agent(SwarmAgent):
    """
    TestAgent_1750926106 agent for handling start, work, finish workflows.
    
    Generated automatically - customize as needed.
    """
    
    StateEnum = TestAgent_1750926106State
    LISTEN_FILTER = "swarmsh.testagent_1750926106."
    TRIGGER_MAP = {
        "start": "on_start",
        "work": "on_work",
        "finish": "on_finish",
    }
    
    def setup_triggers(self):
        """No additional setup needed."""
        pass

    @trigger(source=TestAgent_1750926106State.IDLE, dest=TestAgent_1750926106State.ACTIVE)
    def on_start(self, span: SpanData) -> Optional[NextCommand]:
        """Handle start trigger."""
        self._transition(f"Processing start from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1750926106State.ACTIVE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1750926106.start",
            args=["--span-id", span.span_id],
            description=f"Execute start action"
        )

    @trigger(source=TestAgent_1750926106State.ACTIVE, dest=TestAgent_1750926106State.COMPLETE)
    def on_work(self, span: SpanData) -> Optional[NextCommand]:
        """Handle work trigger."""
        self._transition(f"Processing work from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1750926106State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1750926106.work",
            args=["--span-id", span.span_id],
            description=f"Execute work action"
        )

    @trigger(source=TestAgent_1750926106State.COMPLETE, dest=TestAgent_1750926106State.COMPLETE)
    def on_finish(self, span: SpanData) -> Optional[NextCommand]:
        """Handle finish trigger."""
        self._transition(f"Processing finish from {span.attributes.get('source', 'unknown')}", 
                        TestAgent_1750926106State.COMPLETE)
        
        # TODO: Add your business logic here
        return NextCommand(
            fq_name="swarmsh.testagent_1750926106.finish",
            args=["--span-id", span.span_id],
            description=f"Execute finish action"
        )


if __name__ == "__main__":
    TestAgent_1750926106Agent().run()
