#!/usr/bin/env python3
"""
Simplified demo of the OpenTelemetry ecosystem loop.

This script demonstrates the core concepts without requiring
full OpenTelemetry SDK installation.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field
from queue import Queue


@dataclass
class MockSpan:
    """Simplified span representation."""
    name: str
    trace_id: str
    span_id: str
    timestamp: float
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "OK"
    
    def to_jsonl(self) -> str:
        """Convert to JSONL format for SwarmAgent."""
        return json.dumps({
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "timestamp": self.timestamp,
            "attributes": self.attributes,
            "events": self.events,
            "status": self.status
        })


class SimpleTelemetry:
    """Simplified telemetry system."""
    
    def __init__(self, span_file: Path):
        self.span_file = span_file
        self.span_file.parent.mkdir(parents=True, exist_ok=True)
        self.span_file.touch()
        self.trace_counter = 0
        self.span_counter = 0
    
    def create_span(self, name: str, attributes: Dict[str, Any] = None) -> MockSpan:
        """Create a new span."""
        self.trace_counter += 1
        self.span_counter += 1
        
        span = MockSpan(
            name=name,
            trace_id=f"trace_{self.trace_counter:08d}",
            span_id=f"span_{self.span_counter:016d}",
            timestamp=time.time(),
            attributes=attributes or {}
        )
        
        # Write to JSONL file
        with self.span_file.open("a") as f:
            f.write(span.to_jsonl() + "\n")
        
        return span


class AgentSimulator:
    """Simulates SwarmAgent behavior."""
    
    def __init__(self, name: str, telemetry: SimpleTelemetry):
        self.name = name
        self.telemetry = telemetry
        self.state = "IDLE"
        self.command_queue = Queue()
    
    def process_span(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a span and potentially generate a command."""
        span_name = span_data.get("name", "")
        attributes = span_data.get("attributes", {})
        
        # Roberts Agent Logic
        if self.name == "roberts" and "roberts" in span_name:
            if "open" in span_name and self.state == "IDLE":
                self.state = "MOTION_OPEN"
                print(f"  🏛️  Roberts: IDLE → MOTION_OPEN")
                return None  # No command for this transition
                
            elif "vote" in span_name and self.state == "MOTION_OPEN":
                self.state = "VOTING"
                print(f"  🏛️  Roberts: MOTION_OPEN → VOTING")
                return None
                
            elif "close" in span_name and self.state == "VOTING":
                self.state = "CLOSED"
                print(f"  🏛️  Roberts: VOTING → CLOSED")
                
                # If motion passed and it's a sprint motion, trigger Scrum
                if attributes.get("result") == "passed" and "sprint" in attributes.get("motion_id", ""):
                    return {
                        "command": "swarmsh.scrum.plan",
                        "args": {
                            "sprint_number": attributes.get("sprint_number", "42"),
                            "team_id": attributes.get("team_id", "alpha"),
                            "capacity": 50
                        }
                    }
        
        # Scrum Agent Logic
        elif self.name == "scrum" and "scrum" in span_name:
            if "plan" in span_name and self.state == "IDLE":
                self.state = "PLANNING"
                print(f"  📅 Scrum: IDLE → PLANNING → EXECUTING")
                self.state = "EXECUTING"  # Quick transition for demo
                return None
                
            elif "review" in span_name and self.state == "EXECUTING":
                self.state = "REVIEW"
                print(f"  📅 Scrum: EXECUTING → REVIEW")
                
                # Check for quality issues
                defect_rate = attributes.get("defect_rate", 0)
                if defect_rate > 3.0:
                    print(f"  ⚠️  Scrum: Defect rate {defect_rate}% > 3% threshold!")
                    return {
                        "command": "swarmsh.lean.define",
                        "args": {
                            "project_id": f"defect-sprint{attributes.get('sprint_number', '42')}",
                            "problem_statement": f"Defect rate {defect_rate}% exceeds threshold",
                            "sponsor": "scrum-agent"
                        }
                    }
        
        # Lean Agent Logic
        elif self.name == "lean" and "lean" in span_name:
            if "define" in span_name and self.state == "IDLE":
                self.state = "DEFINE"
                print(f"  🎯 Lean: IDLE → DEFINE")
                
                # For demo, quickly progress through DMAIC
                print(f"  🎯 Lean: Starting DMAIC process for {attributes.get('project_id')}")
                return {
                    "command": "swarmsh.lean.measure",
                    "args": {"project_id": attributes.get("project_id")}
                }
        
        return None


def run_demo():
    """Run the OpenTelemetry ecosystem loop demo."""
    print("🌟 OpenTelemetry Ecosystem Loop Demo (Simplified)")
    print("=" * 60)
    
    # Setup
    span_file = Path("/tmp/swarm_demo_spans.jsonl")
    telemetry = SimpleTelemetry(span_file)
    
    print(f"\n📁 Span file: {span_file}")
    
    # Create agents
    agents = {
        "roberts": AgentSimulator("roberts", telemetry),
        "scrum": AgentSimulator("scrum", telemetry),
        "lean": AgentSimulator("lean", telemetry)
    }
    
    print(f"🤖 Agents created: {list(agents.keys())}")
    
    # Agent monitoring thread
    processed_spans = set()
    commands_to_execute = Queue()
    
    def monitor_spans():
        """Monitor spans and trigger agents."""
        while True:
            try:
                with span_file.open() as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        try:
                            span_data = json.loads(line)
                            span_id = span_data.get("span_id")
                            
                            if span_id in processed_spans:
                                continue
                            
                            processed_spans.add(span_id)
                            
                            # Process with each agent
                            for agent_name, agent in agents.items():
                                command = agent.process_span(span_data)
                                if command:
                                    commands_to_execute.put((agent_name, command))
                        
                        except json.JSONDecodeError:
                            continue
            
            except Exception as e:
                pass
            
            time.sleep(0.1)
    
    # Start monitor in background
    monitor_thread = threading.Thread(target=monitor_spans, daemon=True)
    monitor_thread.start()
    
    # Demo scenario
    print("\n🎬 Starting Demo Scenario")
    print("\n1️⃣  Roberts Rules: Opening motion for Sprint 42")
    
    # Step 1: Open motion
    telemetry.create_span("swarmsh.roberts.open", {
        "motion_id": "sprint42",
        "meeting_id": "board",
        "swarm.agent": "roberts",
        "swarm.trigger": "open"
    })
    time.sleep(0.5)
    
    # Step 2: Call vote
    print("\n2️⃣  Roberts Rules: Calling for a vote")
    telemetry.create_span("swarmsh.roberts.vote", {
        "motion_id": "sprint42",
        "voting_method": "voice_vote",
        "swarm.agent": "roberts",
        "swarm.trigger": "vote"
    })
    time.sleep(0.5)
    
    # Step 3: Close with approval
    print("\n3️⃣  Roberts Rules: Motion passes!")
    telemetry.create_span("swarmsh.roberts.close", {
        "motion_id": "sprint42",
        "result": "passed",
        "votes_yes": 7,
        "votes_no": 2,
        "sprint_number": "42",
        "team_id": "alpha",
        "swarm.agent": "roberts",
        "swarm.trigger": "close"
    })
    time.sleep(0.5)
    
    # Process commands from agents
    while not commands_to_execute.empty():
        agent_name, command = commands_to_execute.get()
        print(f"\n  → {agent_name} agent generated command: {command['command']}")
        
        # Execute the command (create span)
        if command["command"] == "swarmsh.scrum.plan":
            telemetry.create_span(command["command"], {
                **command["args"],
                "swarm.agent": "scrum",
                "swarm.trigger": "plan"
            })
    
    time.sleep(0.5)
    
    # Step 4: Scrum review with issues
    print("\n4️⃣  Scrum: Sprint review detects quality issues")
    telemetry.create_span("swarmsh.scrum.review", {
        "sprint_number": "42",
        "velocity": 45,
        "defect_rate": 5.2,  # Above threshold!
        "customer_satisfaction": 7.8,
        "swarm.agent": "scrum",
        "swarm.trigger": "review"
    })
    time.sleep(0.5)
    
    # Process remaining commands
    while not commands_to_execute.empty():
        agent_name, command = commands_to_execute.get()
        print(f"\n  → {agent_name} agent generated command: {command['command']}")
        
        if command["command"] == "swarmsh.lean.define":
            telemetry.create_span(command["command"], {
                **command["args"],
                "swarm.agent": "lean",
                "swarm.trigger": "define"
            })
    
    time.sleep(0.5)
    
    # Summary
    print("\n\n📊 Loop Summary:")
    print(f"  • Total spans created: {telemetry.span_counter}")
    print(f"  • Agent states:")
    for name, agent in agents.items():
        print(f"    - {name}: {agent.state}")
    
    print("\n🔄 The Ecosystem Loop:")
    print("  1. CLI command → OpenTelemetry span")
    print("  2. Span → JSONL file")
    print("  3. SwarmAgent reads span → state transition")
    print("  4. Agent generates command → new span")
    print("  5. Loop continues autonomously!")
    
    print("\n✅ Demo complete! The loop would continue as new spans arrive...")
    
    # Show span file contents
    print(f"\n📜 Generated spans in {span_file}:")
    with span_file.open() as f:
        for i, line in enumerate(f, 1):
            span = json.loads(line)
            print(f"  {i}. {span['name']} (agent: {span['attributes'].get('swarm.agent', 'none')})")


if __name__ == "__main__":
    run_demo()