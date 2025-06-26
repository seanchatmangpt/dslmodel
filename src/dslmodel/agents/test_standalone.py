#!/usr/bin/env python3
"""Standalone test for SwarmAgent implementations without full package dependencies."""

import sys
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import base components
from swarm.swarm_agent import SwarmAgent
from swarm.swarm_models import SpanData, NextCommand

# Import example agents
from examples.ping_agent import PingAgent, PingState
from examples.roberts_agent import RobertsAgent, RorState
from examples.scrum_agent import ScrumAgent, ScrumState
from examples.lean_agent import LeanAgent, LeanState


def test_base_functionality():
    """Test basic agent setup and span parsing."""
    print("🧪 Testing base functionality...")
    
    # Create test directory
    test_dir = Path("/tmp/swarm_test_standalone")
    test_dir.mkdir(exist_ok=True)
    span_file = test_dir / "telemetry_spans.jsonl"
    
    # Initialize agent
    agent = PingAgent(root_dir=test_dir)
    
    # Test span parsing
    test_span = {
        "name": "swarmsh.ping.test",
        "trace_id": "trace_123",
        "span_id": "span_456",
        "timestamp": time.time(),
        "attributes": {"source": "test"}
    }
    
    with span_file.open("w") as f:
        json.dump(test_span, f)
        f.write("\n")
    
    # Parse span
    with span_file.open() as f:
        line = f.readline()
        parsed = agent.parse_span(line)
    
    assert parsed is not None
    assert parsed.name == "swarmsh.ping.test"
    assert parsed.trace_id == "trace_123"
    print("✅ Base functionality test passed")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


def test_state_transitions():
    """Test agent state transitions."""
    print("\n🧪 Testing state transitions...")
    
    test_dir = Path("/tmp/swarm_test_transitions")
    test_dir.mkdir(exist_ok=True)
    
    # Test PingAgent transitions
    ping = PingAgent(root_dir=test_dir)
    assert ping.current_state == PingState.IDLE
    
    # Create ping span
    span = SpanData(
        name="swarmsh.ping.request",
        trace_id="test_trace",
        span_id="test_span",
        timestamp=time.time(),
        attributes={"source": "test"}
    )
    
    # Process span
    cmd = ping.forward(span)
    assert cmd is not None
    assert "pong" in cmd.fq_name
    
    print("✅ State transition test passed")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


def test_trigger_mapping():
    """Test trigger keyword mapping."""
    print("\n🧪 Testing trigger mapping...")
    
    test_dir = Path("/tmp/swarm_test_triggers")
    test_dir.mkdir(exist_ok=True)
    
    # Test each agent's trigger map
    agents = [
        (PingAgent, "ping", "on_ping"),
        (RobertsAgent, "vote", "call_vote"),
        (ScrumAgent, "review", "review"),
        (LeanAgent, "analyze", "analyze")
    ]
    
    for agent_class, keyword, expected_method in agents:
        agent = agent_class(root_dir=test_dir)
        assert keyword in agent.TRIGGER_MAP
        assert agent.TRIGGER_MAP[keyword] == expected_method
        assert hasattr(agent, expected_method)
        print(f"  ✓ {agent_class.__name__} trigger mapping verified")
    
    print("✅ Trigger mapping test passed")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


def test_agent_interactions():
    """Test simple agent interaction scenario."""
    print("\n🧪 Testing agent interactions...")
    
    test_dir = Path("/tmp/swarm_test_interactions")
    test_dir.mkdir(exist_ok=True)
    span_file = test_dir / "telemetry_spans.jsonl"
    
    # Initialize agents
    roberts = RobertsAgent(root_dir=test_dir)
    scrum = ScrumAgent(root_dir=test_dir)
    
    # Simulate Roberts vote passing
    vote_span = {
        "name": "swarmsh.roberts.close",
        "trace_id": "trace_vote",
        "span_id": "span_vote",
        "timestamp": time.time(),
        "attributes": {
            "motion_id": "sprint_42",
            "result": "passed",
            "votes_yes": 7,
            "votes_no": 1,
            "sprint_number": "42"
        }
    }
    
    # Process vote span with Roberts agent
    vote_data = SpanData(**vote_span)
    cmd = roberts.adjourn(vote_data)
    
    assert cmd is not None
    assert "scrum.sprint-planning" in cmd.fq_name
    assert "--sprint-number" in cmd.args
    assert "42" in cmd.args
    
    print("✅ Agent interaction test passed")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


def test_listen_filter():
    """Test LISTEN_FILTER functionality."""
    print("\n🧪 Testing LISTEN_FILTER...")
    
    test_dir = Path("/tmp/swarm_test_filter")
    test_dir.mkdir(exist_ok=True)
    
    # Test agent with filter
    roberts = RobertsAgent(root_dir=test_dir)
    assert roberts.LISTEN_FILTER == "swarmsh.roberts."
    
    # Test filtered span (should process)
    roberts_span = SpanData(
        name="swarmsh.roberts.vote",
        trace_id="test",
        span_id="test",
        timestamp=time.time(),
        attributes={}
    )
    
    # Test non-matching span (should ignore)
    other_span = SpanData(
        name="swarmsh.scrum.daily",
        trace_id="test",
        span_id="test",
        timestamp=time.time(),
        attributes={}
    )
    
    # Roberts should process its own spans
    cmd1 = roberts.forward(roberts_span)
    assert cmd1 is not None  # Should process
    
    # Roberts should ignore other spans
    cmd2 = roberts.forward(other_span)
    assert cmd2 is None  # Should ignore
    
    print("✅ LISTEN_FILTER test passed")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


def main():
    """Run all standalone tests."""
    print("🚀 Running SwarmAgent Standalone Tests")
    print("=" * 50)
    
    try:
        test_base_functionality()
        test_state_transitions()
        test_trigger_mapping()
        test_agent_interactions()
        test_listen_filter()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📝 Summary:")
        print("- Base SwarmAgent functionality ✅")
        print("- State transitions ✅")
        print("- Trigger mappings ✅")
        print("- Agent interactions ✅")
        print("- Listen filters ✅")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()