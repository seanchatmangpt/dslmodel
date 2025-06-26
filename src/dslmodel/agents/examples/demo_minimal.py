#!/usr/bin/env python3
"""
Minimal demo showing the SwarmAgent pattern without external dependencies.
This demonstrates the 80/20 implementation of the swarm agent system.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional

# Mock the base classes to show the pattern
class MockSpanData:
    def __init__(self, name: str, attributes: Dict):
        self.name = name
        self.attributes = attributes
        self.trace_id = f"trace_{int(time.time() * 1000)}"
        self.span_id = f"span_{int(time.time() * 1000000)}"
        self.timestamp = time.time()


class MockNextCommand:
    def __init__(self, fq_name: str, args: list, description: str = ""):
        self.fq_name = fq_name
        self.args = args
        self.description = description
    
    def __repr__(self):
        return f"NextCommand({self.fq_name} {' '.join(self.args)})"


def demo_agent_pattern():
    """Demonstrate the core SwarmAgent pattern."""
    print("🚀 SwarmAgent Pattern Demo (80/20 Implementation)")
    print("=" * 60)
    
    # 1. Example: Roberts Rules Agent
    print("\n1️⃣ Roberts Rules Agent Pattern:")
    print("-" * 40)
    
    # Simulated span for opening a motion
    open_span = MockSpanData(
        name="swarmsh.roberts.open",
        attributes={"meeting_id": "board_q1", "motion_id": "approve_sprint_42"}
    )
    
    # Roberts agent would process this span
    print(f"📥 Received span: {open_span.name}")
    print(f"   Attributes: {open_span.attributes}")
    
    # Agent logic: check trigger map
    if "open" in open_span.name:
        print("✅ Matched trigger: 'open' → open_motion()")
        print("🔄 State transition: IDLE → MOTION_OPEN")
        
        # Generate command
        cmd = MockNextCommand(
            fq_name="swarmsh.roberts.call-to-order",
            args=["--meeting-id", "board_q1"],
            description="Call meeting to order"
        )
        print(f"📤 Emitting command: {cmd}")
    
    # 2. Example: Scrum Agent
    print("\n\n2️⃣ Scrum Agent Pattern:")
    print("-" * 40)
    
    # Simulated span for sprint review with quality issue
    review_span = MockSpanData(
        name="swarmsh.scrum.review",
        attributes={
            "sprint_number": "42",
            "defect_rate": 4.5,  # Above 3% threshold
            "velocity": 38
        }
    )
    
    print(f"📥 Received span: {review_span.name}")
    print(f"   Defect rate: {review_span.attributes['defect_rate']}%")
    
    if "review" in review_span.name:
        print("✅ Matched trigger: 'review' → review()")
        print("🔄 State transition: EXECUTING → REVIEW")
        
        # Check KPIs
        if review_span.attributes["defect_rate"] > 3.0:
            print("⚠️ Defect rate exceeds threshold!")
            
            # Trigger Lean project
            cmd = MockNextCommand(
                fq_name="swarmsh.lean.define",
                args=[
                    "--project-id", f"defect-sprint{review_span.attributes['sprint_number']}",
                    "--problem-statement", f"Defect>{review_span.attributes['defect_rate']}%"
                ],
                description="Initiate Lean project for quality improvement"
            )
            print(f"📤 Triggering Lean optimization: {cmd}")
    
    # 3. Example: Agent Coordination
    print("\n\n3️⃣ Agent Coordination Pattern:")
    print("-" * 40)
    
    print("📊 Simulating full governance → delivery → optimization cycle:")
    
    steps = [
        ("Roberts", "Motion approved → triggering sprint planning"),
        ("Scrum", "Sprint review → quality issue detected"),
        ("Lean", "DMAIC project → process improvement validated"),
        ("Lean→Roberts", "Requesting governance approval for process change"),
        ("Roberts", "Process change approved → cycle complete")
    ]
    
    for i, (agent, action) in enumerate(steps, 1):
        print(f"\n  Step {i}: [{agent}] {action}")
        time.sleep(0.5)  # Simulate processing
    
    print("\n✅ Full cycle demonstrated!")
    
    # 4. Key Implementation Details
    print("\n\n4️⃣ Key Implementation Details:")
    print("-" * 40)
    
    print("""
    Each SwarmAgent subclass provides:
    
    1. StateEnum - Defines agent lifecycle states
       Example: IDLE → MOTION_OPEN → VOTING → CLOSED
    
    2. TRIGGER_MAP - Maps span keywords to handler methods
       Example: {"open": "open_motion", "vote": "call_vote"}
    
    3. @trigger decorated methods - Handle state transitions
       Example: @trigger(source=IDLE, dest=MOTION_OPEN)
    
    4. LISTEN_FILTER (optional) - Filters spans by prefix
       Example: "swarmsh.roberts." (ignores other spans)
    
    The base SwarmAgent class handles:
    - Watching span stream (JSONL file)
    - Routing spans to handlers
    - Executing CLI commands
    - Managing state transitions
    """)
    
    # 5. Running the Swarm
    print("\n5️⃣ Running the Swarm:")
    print("-" * 40)
    
    print("""
    To run the full swarm:
    
    # Terminal 1: Start Roberts agent
    python agents/roberts_agent.py
    
    # Terminal 2: Start Scrum agent
    python agents/scrum_agent.py
    
    # Terminal 3: Start Lean agent
    python agents/lean_agent.py
    
    # Terminal 4: Emit initial span
    echo '{"name": "swarmsh.roberts.vote", "trace_id": "t1", "span_id": "s1", 
           "timestamp": 1234567890, "attributes": {"motion_id": "sprint42"}}' >> telemetry_spans.jsonl
    
    The agents will autonomously coordinate based on span attributes!
    """)


if __name__ == "__main__":
    demo_agent_pattern()