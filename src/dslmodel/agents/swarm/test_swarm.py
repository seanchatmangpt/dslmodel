#!/usr/bin/env python3
"""Test script for SwarmAgent framework."""

import json
import time
import pathlib
import tempfile
from typing import Dict, Any

from dslmodel.agents.swarm import SpanData
from dslmodel.agents.examples.ping_agent import PingAgent
from dslmodel.agents.examples.roberts_agent import RobertsAgent
from dslmodel.agents.examples.scrum_agent import ScrumAgent
from dslmodel.agents.examples.lean_agent import LeanAgent


def create_test_span(name: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Create a test span dictionary."""
    return {
        "name": name,
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": attributes
    }


def test_ping_agent():
    """Test the minimal PingAgent."""
    print("\n=== Testing PingAgent ===")
    
    agent = PingAgent()
    
    # Create test span
    span_dict = create_test_span("swarmsh.ping.request", {"source": "test"})
    span = SpanData(**span_dict)
    
    # Initial state should be IDLE
    assert agent.current_state.name == "IDLE"
    print(f"✓ Initial state: {agent.current_state.name}")
    
    # Process span
    cmd = agent.forward(span)
    
    # Should transition to PINGED and return pong command
    assert agent.current_state.name == "PINGED"
    assert cmd is not None
    assert cmd.fq_name == "swarmsh.ping.pong"
    assert "--ping-id" in cmd.args
    
    print(f"✓ State after ping: {agent.current_state.name}")
    print(f"✓ Command generated: {cmd.fq_name} {cmd.args}")


def test_roberts_agent():
    """Test Roberts Rules agent."""
    print("\n=== Testing RobertsAgent ===")
    
    agent = RobertsAgent()
    
    # Test motion opening
    span = SpanData(**create_test_span(
        "swarmsh.roberts.open_motion",
        {"motion_id": "test_motion", "meeting_id": "test_meeting"}
    ))
    
    assert agent.current_state.name == "IDLE"
    cmd = agent.forward(span)
    
    assert agent.current_state.name == "MOTION_OPEN"
    assert cmd.fq_name == "swarmsh.roberts.call-to-order"
    print(f"✓ Opened motion, state: {agent.current_state.name}")
    
    # Test voting
    span = SpanData(**create_test_span(
        "swarmsh.roberts.call_vote",
        {"motion_id": "test_motion", "voting_method": "ballot"}
    ))
    
    cmd = agent.forward(span)
    assert agent.current_state.name == "VOTING"
    assert cmd.fq_name == "swarmsh.roberts.voting"
    print(f"✓ Called vote, state: {agent.current_state.name}")
    
    # Test adjournment with sprint trigger
    span = SpanData(**create_test_span(
        "swarmsh.roberts.close_meeting",
        {
            "motion_id": "sprint_planning",
            "result": "passed",
            "votes_yes": 5,
            "votes_no": 1,
            "sprint_number": "42",
            "team_id": "alpha"
        }
    ))
    
    cmd = agent.forward(span)
    assert agent.current_state.name == "CLOSED"
    assert cmd.fq_name == "swarmsh.scrum.sprint-planning"
    print(f"✓ Adjourned and triggered sprint, state: {agent.current_state.name}")


def test_scrum_agent():
    """Test Scrum agent."""
    print("\n=== Testing ScrumAgent ===")
    
    agent = ScrumAgent()
    
    # Test sprint planning
    span = SpanData(**create_test_span(
        "swarmsh.scrum.plan_sprint",
        {"sprint_number": "42", "team_id": "alpha", "capacity": 50}
    ))
    
    assert agent.current_state.name == "PLANNING"
    cmd = agent.forward(span)
    
    assert agent.current_state.name == "EXECUTING"
    assert cmd.fq_name == "swarmsh.scrum.backlog-populate"
    print(f"✓ Sprint planned, state: {agent.current_state.name}")
    
    # Test daily standup (no state change)
    span = SpanData(**create_test_span(
        "swarmsh.scrum.daily",
        {"blockers": ["backend API unavailable"]}
    ))
    
    cmd = agent.forward(span)
    assert agent.current_state.name == "EXECUTING"  # No state change
    assert cmd.fq_name == "swarmsh.scrum.escalate-blockers"
    print(f"✓ Daily with blockers handled, state unchanged: {agent.current_state.name}")
    
    # Test review with quality issue
    span = SpanData(**create_test_span(
        "swarmsh.scrum.review",
        {
            "sprint_number": "42",
            "velocity": 45,
            "defect_rate": 5.2,  # Above 3% threshold
            "customer_satisfaction": 8.5
        }
    ))
    
    cmd = agent.forward(span)
    assert agent.current_state.name == "REVIEW"
    assert cmd.fq_name == "swarmsh.lean.define"  # Triggers Lean project
    print(f"✓ Review triggered Lean project due to high defects, state: {agent.current_state.name}")


def test_lean_agent():
    """Test Lean Six Sigma agent."""
    print("\n=== Testing LeanAgent ===")
    
    agent = LeanAgent()
    
    # Test DMAIC workflow
    states = ["DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "CONTROL"]
    triggers = ["define", "measure", "analyze", "improve", "control"]
    
    for i, (state, trigger) in enumerate(zip(states[:-1], triggers[:-1])):
        span = SpanData(**create_test_span(
            f"swarmsh.lean.{trigger}",
            {"project_id": "test_lean_001"}
        ))
        
        assert agent.current_state.name == state
        cmd = agent.forward(span)
        assert agent.current_state.name == states[i + 1]
        print(f"✓ {state} → {states[i + 1]}, command: {cmd.path[-1] if cmd else 'None'}")
    
    # Test control with governance trigger
    span = SpanData(**create_test_span(
        "swarmsh.lean.control",
        {"project_id": "test_lean_001", "validated": True}
    ))
    
    cmd = agent.forward(span)
    assert cmd.path == ["swarmsh", "roberts", "voting"]
    print(f"✓ Control phase triggered governance vote")


def test_inter_agent_workflow():
    """Test a complete inter-agent workflow."""
    print("\n=== Testing Inter-Agent Workflow ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = pathlib.Path(tmpdir)
        span_file = test_dir / "test_spans.jsonl"
        
        # Create agents with test directory
        roberts = RobertsAgent(root_dir=test_dir, span_file="test_spans.jsonl")
        scrum = ScrumAgent(root_dir=test_dir, span_file="test_spans.jsonl")
        lean = LeanAgent(root_dir=test_dir, span_file="test_spans.jsonl")
        
        print("\n1. Roberts approves sprint motion")
        # Roberts: IDLE → MOTION_OPEN → VOTING → CLOSED
        spans = [
            create_test_span("swarmsh.roberts.open", {"motion_id": "sprint42"}),
            create_test_span("swarmsh.roberts.vote", {"motion_id": "sprint42"}),
            create_test_span("swarmsh.roberts.close", {
                "motion_id": "sprint42",
                "result": "passed",
                "sprint_number": "42"
            })
        ]
        
        for span_dict in spans:
            span = SpanData(**span_dict)
            cmd = roberts.forward(span)
            if cmd:
                print(f"  Roberts: {roberts.current_state.name} → {cmd.fq_name}")
        
        print("\n2. Scrum executes sprint and finds quality issue")
        # Scrum: PLANNING → EXECUTING → REVIEW
        spans = [
            create_test_span("swarmsh.scrum.plan", {"sprint_number": "42"}),
            create_test_span("swarmsh.scrum.review", {
                "sprint_number": "42",
                "defect_rate": 5.0  # Triggers Lean
            })
        ]
        
        for span_dict in spans:
            span = SpanData(**span_dict)
            cmd = scrum.forward(span)
            if cmd:
                print(f"  Scrum: {scrum.current_state.name} → {cmd.fq_name}")
        
        print("\n3. Lean improves process and requests approval")
        # Lean: DEFINE → ... → CONTROL
        spans = [
            create_test_span("swarmsh.lean.define", {"project_id": "defect-sprint42"}),
            create_test_span("swarmsh.lean.measure", {"project_id": "defect-sprint42"}),
            create_test_span("swarmsh.lean.analyze", {"project_id": "defect-sprint42"}),
            create_test_span("swarmsh.lean.improve", {"project_id": "defect-sprint42"}),
            create_test_span("swarmsh.lean.control", {
                "project_id": "defect-sprint42",
                "validated": True
            })
        ]
        
        for span_dict in spans:
            span = SpanData(**span_dict)
            cmd = lean.forward(span)
            if cmd:
                print(f"  Lean: {lean.current_state.name} → {cmd.fq_name}")
        
        print("\n✓ Complete workflow executed successfully!")


def main():
    """Run all tests."""
    print("🧪 Testing SwarmAgent Framework")
    print("=" * 50)
    
    try:
        test_ping_agent()
        test_roberts_agent()
        test_scrum_agent()
        test_lean_agent()
        test_inter_agent_workflow()
        
        print("\n✅ All tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()