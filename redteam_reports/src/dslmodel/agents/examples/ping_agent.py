"""Minimal 'Hello World' agent example."""

from enum import Enum, auto
from typing import Optional

from dslmodel.mixins import trigger
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class PingState(Enum):
    """Simple ping/pong states."""
    IDLE = auto()
    PINGED = auto()


class PingAgent(SwarmAgent):
    """
    Minimal example agent that responds to ping spans with pong commands.
    
    This demonstrates the basic pattern for creating swarm agents.
    """
    
    StateEnum = PingState
    TRIGGER_MAP = {"ping": "on_ping"}  # map keyword → method
    LISTEN_FILTER = "swarmsh.ping."    # optional optimization
    
    def setup_triggers(self):
        """No additional setup needed for this simple agent."""
        pass
    
    @trigger(source=PingState.IDLE, dest=PingState.PINGED)
    def on_ping(self, span: SpanData) -> Optional[NextCommand]:
        """
        Handle ping spans by transitioning state and returning pong command.
        """
        # Record span + change state
        self._transition(f"Received ping from {span.attributes.get('source', 'unknown')}", 
                        PingState.PINGED)
        
        # Reply with a CLI command that emits a pong
        return NextCommand(
            fq_name="swarmsh.ping.pong",
            args=["--detail", "auto-reply", "--ping-id", span.span_id],
            description="Automated pong response"
        )


if __name__ == "__main__":
    # Run standalone
    PingAgent().run()