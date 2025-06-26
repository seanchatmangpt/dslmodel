---
to: src/dslmodel/agents/examples/<%= fileName %>.py
---
"""
<%= name %> Agent - <%= purpose %>

This agent demonstrates <%= name.toLowerCase() %> coordination patterns
using the SwarmAgent framework with OpenTelemetry integration.
"""

from typing import Optional, Dict, Any, List
from pydantic import Field
from transitions import Machine

from dslmodel.agents.swarm.swarm_agent import SwarmAgent
from dslmodel.agents.swarm.swarm_models import SpanData, NextCommand
from dslmodel.mixins.fsm_mixin import trigger


class <%= className %>(SwarmAgent):
    """<%= purpose %>"""
    
    # Agent configuration
    AGENT_TYPE = "<%= name.toLowerCase() %>"
    LISTEN_FILTER = "<%= listen_filter %>"
    
    # State machine configuration
    name: str = Field(default="<%= className %>")
    states: List[str] = Field(default=<%= JSON.stringify(states) %>)
    initial_state: str = Field(default="<%= initialState %>")
    
    # Agent-specific fields
    processed_count: int = Field(default=0)
    last_span_id: Optional[str] = Field(default=None)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Define state transitions
        transitions = [
<% transitions.forEach(function(t) { %>            {
                "trigger": "<%= t.trigger %>",
                "source": "<%= t.source %>",
                "dest": "<%= t.dest %>",
                "before": "log_transition",
                "after": "update_metrics"
            },
<% }); %>        ]
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=self.initial_state,
            auto_transitions=False
        )
        
        # Map triggers to handler methods
        self.TRIGGER_MAPPING = {
<% triggers.forEach(function(trigger) { %>            "<%= trigger %>": self.handle_<%= trigger %>,
<% }); %>        }
    
    def log_transition(self):
        """Log state transition."""
        print(f"🔄 {self.name}: Transitioning from {self.state}")
    
    def update_metrics(self):
        """Update agent metrics after transition."""
        self.processed_count += 1
        self.metrics["transitions"] = self.processed_count
<% triggers.forEach(function(trigger) { %>
    @trigger("<%= trigger %>")
    def handle_<%= trigger %>(self, span: SpanData) -> Optional[NextCommand]:
        """Handle <%= trigger %> trigger.
        
        Args:
            span: The telemetry span that triggered this handler
            
        Returns:
            NextCommand if this agent needs to trigger another agent
        """
        span_id = span.span_id
        self.last_span_id = span_id
        
        # Extract relevant attributes
        attributes = span.attributes or {}
        
        print(f"📊 {self.name}: Processing <%= trigger %> span {span_id[:8]}...")
        
        # TODO: Add <%= trigger %> logic here
        # Example: Analyze span data, update internal state, decide on next action
        
        # Transition to next state
        if hasattr(self, "<%= trigger %>"):
            getattr(self, "<%= trigger %>")()
<% if (has_next_command) { %>        
        # Example: Trigger next agent in workflow
        # return NextCommand(
        #     name="swarmsh.next.action",
        #     attributes={
        #         "previous_agent": self.AGENT_TYPE,
        #         "trigger": "<%= trigger %>",
        #         "data": {}
        #     }
        # )
<% } %>        
        return None
<% }); %>
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "agent": self.name,
            "type": self.AGENT_TYPE,
            "state": self.state,
            "processed_count": self.processed_count,
            "last_span": self.last_span_id,
            "metrics": self.metrics
        }


# Example usage
if __name__ == "__main__":
    # Create agent instance
    agent = <%= className %>()
    
    # Example span data
    test_span = SpanData(
        name="<%= listen_filter %>.<%= triggers[0] %>",
        trace_id="test_trace_123",
        span_id="test_span_456",
        timestamp=1234567890.123,
        attributes={
            "test": True,
            "source": "example"
        }
    )
    
    # Process span
    print(f"🚀 Testing {agent.name}...")
    print(f"📍 Initial state: {agent.state}")
    
    result = agent.forward(test_span)
    
    print(f"📍 Final state: {agent.state}")
    print(f"📊 Status: {agent.get_status()}")
    
    if result:
        print(f"➡️  Next command: {result.name}")