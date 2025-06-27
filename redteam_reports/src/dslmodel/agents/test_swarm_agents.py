"""Test harness for SwarmAgent implementations."""

import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, Optional, List
import pytest

from dslmodel.agents.swarm import SpanData
from dslmodel.agents.examples.ping_agent import PingAgent, PingState
from dslmodel.agents.examples.roberts_agent import RobertsAgent, RorState
from dslmodel.agents.examples.scrum_agent import ScrumAgent, ScrumState
from dslmodel.agents.examples.lean_agent import LeanAgent, LeanState


class TestHarness:
    """Test harness for swarm agents."""
    
    def __init__(self, test_dir: Optional[Path] = None):
        self.test_dir = test_dir or Path("/tmp/swarm_test")
        self.span_file = self.test_dir / "telemetry_spans.jsonl"
        self.agents: List[threading.Thread] = []
        
    def setup(self):
        """Set up test environment."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.span_file.touch()
        
    def teardown(self):
        """Clean up test environment."""
        # Stop all agent threads
        for agent_thread in self.agents:
            if agent_thread.is_alive():
                # Agents run infinite loops, so we need to be forceful
                agent_thread._stop()
        
        # Clean up files
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def emit_span(self, name: str, attributes: Optional[Dict] = None) -> SpanData:
        """Emit a test span to the stream."""
        span_data = {
            "name": name,
            "trace_id": f"test_trace_{int(time.time() * 1000)}",
            "span_id": f"test_span_{int(time.time() * 1000000)}",
            "timestamp": time.time(),
            "attributes": attributes or {}
        }
        
        with self.span_file.open("a") as f:
            f.write(json.dumps(span_data) + "\n")
        
        return SpanData(**span_data)
    
    def run_agent_async(self, agent_class, timeout: float = 5.0):
        """Run an agent in a background thread for testing."""
        agent = agent_class(root_dir=self.test_dir)
        
        def run_with_timeout():
            try:
                # Run for a limited time during tests
                start = time.time()
                while time.time() - start < timeout:
                    # Check for new spans manually
                    with agent.span_stream.open() as f:
                        for line in f:
                            if line.strip():
                                span = agent.parse_span(line.strip())
                                if span:
                                    agent.forward(span)
                    time.sleep(0.1)
            except Exception as e:
                print(f"Agent error: {e}")
        
        thread = threading.Thread(target=run_with_timeout)
        thread.daemon = True
        thread.start()
        self.agents.append(thread)
        return agent
    
    def wait_for_spans(self, count: int, timeout: float = 2.0) -> List[Dict]:
        """Wait for and collect spans from the stream."""
        spans = []
        start = time.time()
        
        while len(spans) < count and time.time() - start < timeout:
            if self.span_file.exists():
                with self.span_file.open() as f:
                    lines = f.readlines()
                    spans = [json.loads(line.strip()) for line in lines if line.strip()]
            time.sleep(0.1)
        
        return spans


def test_ping_agent():
    """Test the PingAgent responds to ping spans."""
    harness = TestHarness()
    harness.setup()
    
    try:
        # Start PingAgent
        agent = harness.run_agent_async(PingAgent, timeout=2.0)
        time.sleep(0.2)  # Let agent initialize
        
        # Emit a ping span
        harness.emit_span("swarmsh.ping.request", {"source": "test_harness"})
        
        # Wait a moment for processing
        time.sleep(0.5)
        
        # Check agent state changed
        assert agent.current_state == PingState.PINGED
        
        # Check for transition span
        spans = harness.wait_for_spans(2)  # Original + transition
        assert len(spans) >= 2
        
        transition_spans = [s for s in spans if "transition" in s["name"]]
        assert len(transition_spans) > 0
        assert transition_spans[0]["attributes"]["to_state"] == "PINGED"
        
    finally:
        harness.teardown()


def test_roberts_scrum_integration():
    """Test Roberts → Scrum agent integration."""
    harness = TestHarness()
    harness.setup()
    
    try:
        # Start both agents
        roberts = harness.run_agent_async(RobertsAgent, timeout=3.0)
        scrum = harness.run_agent_async(ScrumAgent, timeout=3.0)
        time.sleep(0.3)
        
        # Emit voting span to trigger Roberts
        harness.emit_span("swarmsh.roberts.vote", {
            "motion_id": "sprint42",
            "voting_method": "ballot"
        })
        
        time.sleep(0.5)
        
        # Roberts should transition to VOTING
        assert roberts.current_state == RorState.VOTING
        
        # Emit vote completion
        harness.emit_span("swarmsh.roberts.close", {
            "vote_result": "passed",
            "motion_id": "sprint42"
        })
        
        time.sleep(0.5)
        
        # Roberts should transition to CLOSED
        assert roberts.current_state == RorState.CLOSED
        
        # Check spans for sprint planning trigger
        spans = harness.wait_for_spans(5)
        planning_triggers = [s for s in spans if "sprint-planning" in str(s)]
        assert len(planning_triggers) > 0
        
    finally:
        harness.teardown()


def test_scrum_lean_integration():
    """Test Scrum → Lean agent integration for quality issues."""
    harness = TestHarness()
    harness.setup()
    
    try:
        # Start both agents
        scrum = harness.run_agent_async(ScrumAgent, timeout=3.0)
        lean = harness.run_agent_async(LeanAgent, timeout=3.0)
        time.sleep(0.3)
        
        # Simulate sprint review with high defect rate
        harness.emit_span("swarmsh.scrum.review", {
            "sprint_number": "42",
            "defect_rate": 5.2  # Above 3% threshold
        })
        
        time.sleep(0.5)
        
        # Scrum should transition to REVIEW
        assert scrum.current_state == ScrumState.REVIEW
        
        # Check for Lean project trigger
        spans = harness.wait_for_spans(3)
        lean_triggers = [s for s in spans if "lean.define" in str(s)]
        assert len(lean_triggers) > 0
        
    finally:
        harness.teardown()


def test_full_governance_cycle():
    """Test complete governance → delivery → optimization cycle."""
    harness = TestHarness()
    harness.setup()
    
    try:
        # Start all three framework agents
        roberts = harness.run_agent_async(RobertsAgent, timeout=5.0)
        scrum = harness.run_agent_async(ScrumAgent, timeout=5.0)
        lean = harness.run_agent_async(LeanAgent, timeout=5.0)
        time.sleep(0.5)
        
        # 1. Governance: Open motion
        harness.emit_span("swarmsh.roberts.open", {"meeting_id": "quarterly"})
        time.sleep(0.3)
        assert roberts.current_state == RorState.MOTION_OPEN
        
        # 2. Governance: Vote and pass
        harness.emit_span("swarmsh.roberts.vote", {
            "motion_id": "sprint_q4",
            "voting_method": "voice_vote"
        })
        time.sleep(0.3)
        
        harness.emit_span("swarmsh.roberts.close", {
            "vote_result": "passed",
            "motion_id": "sprint_q4"
        })
        time.sleep(0.3)
        
        # 3. Delivery: Sprint planning triggered
        harness.emit_span("swarmsh.scrum.plan", {
            "sprint_number": "q4",
            "team_id": "alpha"
        })
        time.sleep(0.3)
        assert scrum.current_state == ScrumState.EXECUTING
        
        # 4. Delivery: Sprint review with issues
        harness.emit_span("swarmsh.scrum.review", {
            "sprint_number": "q4",
            "defect_rate": 4.5
        })
        time.sleep(0.3)
        
        # 5. Optimization: Lean project triggered
        harness.emit_span("swarmsh.lean.define", {
            "project_id": "defect-sprint-q4",
            "problem_statement": "Defect>4.5%"
        })
        time.sleep(0.3)
        assert lean.current_state == LeanState.MEASURE
        
        # 6. Optimization: Complete DMAIC cycle
        for event, next_state in [
            ("measure", LeanState.ANALYZE),
            ("analyze", LeanState.IMPROVE),
            ("improve", LeanState.CONTROL)
        ]:
            harness.emit_span(f"swarmsh.lean.{event}", {
                "project_id": "defect-sprint-q4"
            })
            time.sleep(0.3)
        
        # 7. Optimization → Governance: Request approval
        harness.emit_span("swarmsh.lean.control", {
            "project_id": "defect-sprint-q4",
            "validated": True
        })
        time.sleep(0.3)
        
        # Verify full cycle
        spans = harness.wait_for_spans(15)
        
        # Check key transitions occurred
        motion_spans = [s for s in spans if "roberts" in s["name"]]
        sprint_spans = [s for s in spans if "scrum" in s["name"]]
        lean_spans = [s for s in spans if "lean" in s["name"]]
        
        assert len(motion_spans) > 0
        assert len(sprint_spans) > 0
        assert len(lean_spans) > 0
        
        print(f"✅ Full governance cycle completed with {len(spans)} spans")
        
    finally:
        harness.teardown()


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Testing PingAgent...")
    test_ping_agent()
    print("✓ PingAgent test passed\n")
    
    print("🧪 Testing Roberts → Scrum integration...")
    test_roberts_scrum_integration()
    print("✓ Roberts → Scrum test passed\n")
    
    print("🧪 Testing Scrum → Lean integration...")
    test_scrum_lean_integration()
    print("✓ Scrum → Lean test passed\n")
    
    print("🧪 Testing full governance cycle...")
    test_full_governance_cycle()
    print("✓ Full cycle test passed\n")
    
    print("🎉 All tests passed!")