---
to: src/dslmodel/agents/tests/test_<%= fileName %>.py
---
"""
Tests for <%= className %>.
"""

import pytest
from unittest.mock import Mock, patch
from dslmodel.agents.examples.<%= fileName %> import <%= className %>
from dslmodel.agents.swarm.swarm_models import SpanData, NextCommand


class Test<%= className %>:
    """Test suite for <%= className %>."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return <%= className %>()
    
    @pytest.fixture  
    def sample_span(self):
        """Create a sample span for testing."""
        return SpanData(
            name="<%= listen_filter %>.<%= triggers[0] %>",
            trace_id="test_trace_001",
            span_id="test_span_001",
            timestamp=1234567890.0,
            attributes={
                "test": True,
                "action": "<%= triggers[0] %>"
            }
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct configuration."""
        assert agent.AGENT_TYPE == "<%= name.toLowerCase() %>"
        assert agent.LISTEN_FILTER == "<%= listen_filter %>"
        assert agent.state == "<%= initialState %>"
        assert agent.processed_count == 0
    
    def test_state_transitions(self, agent):
        """Test state machine transitions."""
        # Test available states
        assert set(agent.states) == set(<%= JSON.stringify(states) %>)
        
        # Test transitions exist
<% triggers.forEach(function(trigger, index) { %>        assert hasattr(agent, "<%= trigger %>")
<% }); %>    
<% triggers.forEach(function(trigger, index) { %>
    def test_handle_<%= trigger %>(self, agent, sample_span):
        """Test <%= trigger %> handler."""
        # Modify span for this trigger
        sample_span.name = "<%= listen_filter %>.<%= trigger %>"
        
        # Process span
        result = agent.handle_<%= trigger %>(sample_span)
        
        # Verify processing
        assert agent.last_span_id == sample_span.span_id
        assert agent.processed_count == 1
<% if (has_next_command) { %>        
        # Verify next command if expected
        # assert isinstance(result, NextCommand) or result is None
<% } else { %>        
        # This agent doesn't trigger others
        assert result is None
<% } %>
<% }); %>
    def test_span_filtering(self, agent, sample_span):
        """Test agent only processes relevant spans."""
        # Test with non-matching span
        sample_span.name = "other.service.action"
        result = agent.forward(sample_span)
        
        assert result is None
        assert agent.processed_count == 0
        
        # Test with matching span
        sample_span.name = "<%= listen_filter %>.<%= triggers[0] %>"
        result = agent.forward(sample_span)
        
        assert agent.processed_count == 1
    
    def test_get_status(self, agent, sample_span):
        """Test status reporting."""
        # Process a span
        agent.forward(sample_span)
        
        status = agent.get_status()
        
        assert status["agent"] == agent.name
        assert status["type"] == agent.AGENT_TYPE
        assert status["processed_count"] == 1
        assert status["last_span"] == sample_span.span_id
    
    def test_metrics_tracking(self, agent, sample_span):
        """Test metrics are tracked correctly."""
        # Process multiple spans
        for i in range(3):
            sample_span.span_id = f"test_span_{i:03d}"
            agent.forward(sample_span)
        
        assert agent.processed_count == 3
        assert agent.metrics["transitions"] == 3
<% if (has_next_command) { %>
    def test_next_command_generation(self, agent):
        """Test agent can generate next commands."""
        # Create a span that should trigger next command
        span = SpanData(
            name="<%= listen_filter %>.<%= triggers[0] %>",
            trace_id="test_trace",
            span_id="test_span",
            timestamp=1234567890.0,
            attributes={
                "trigger_next": True
            }
        )
        
        # Mock the handler to return a NextCommand
        with patch.object(agent, 'handle_<%= triggers[0] %>', return_value=NextCommand(
            name="swarmsh.next.action",
            attributes={"triggered_by": "<%= name.toLowerCase() %>"}
        )):
            result = agent.forward(span)
            
            assert isinstance(result, NextCommand)
            assert result.name == "swarmsh.next.action"
            assert result.attributes["triggered_by"] == "<%= name.toLowerCase() %>"
<% } %>