#!/usr/bin/env python3
"""Demo script for running the SwarmAgent ecosystem."""

import sys
import time
import json
import subprocess
import multiprocessing
from pathlib import Path
from typing import List, Dict

# Agent classes
from dslmodel.agents.examples.ping_agent import PingAgent
from dslmodel.agents.examples.roberts_agent import RobertsAgent
from dslmodel.agents.examples.scrum_agent import ScrumAgent
from dslmodel.agents.examples.lean_agent import LeanAgent


class SwarmDemo:
    """Demo orchestrator for the swarm agent system."""
    
    def __init__(self, root_dir: Path = None):
        self.root_dir = root_dir or Path("~/s2s/agent_coordination").expanduser()
        self.span_file = self.root_dir / "telemetry_spans.jsonl"
        self.processes: List[multiprocessing.Process] = []
        
    def setup(self):
        """Initialize demo environment."""
        print("🚀 Setting up swarm demo environment...")
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.span_file.touch()
        print(f"📁 Demo directory: {self.root_dir}")
        print(f"📄 Span stream: {self.span_file}")
        
    def start_agent(self, agent_class):
        """Start an agent in a separate process."""
        def run_agent():
            agent = agent_class(root_dir=self.root_dir)
            agent.run()
        
        p = multiprocessing.Process(target=run_agent)
        p.daemon = True
        p.start()
        self.processes.append(p)
        print(f"✅ Started {agent_class.__name__}")
        
    def emit_span(self, name: str, attributes: Dict = None):
        """Emit a demo span."""
        span = {
            "name": name,
            "trace_id": f"demo_{int(time.time() * 1000)}",
            "span_id": f"span_{int(time.time() * 1000000)}",
            "timestamp": time.time(),
            "attributes": attributes or {}
        }
        
        with self.span_file.open("a") as f:
            json.dump(span, f)
            f.write("\n")
        
        print(f"📤 Emitted: {name}")
        if attributes:
            for k, v in attributes.items():
                print(f"   {k}: {v}")
    
    def monitor_spans(self, duration: int = 30):
        """Monitor span stream for activity."""
        print(f"\n📊 Monitoring spans for {duration} seconds...")
        print("=" * 60)
        
        start_time = time.time()
        last_pos = 0
        
        while time.time() - start_time < duration:
            if self.span_file.exists():
                with self.span_file.open() as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    last_pos = f.tell()
                    
                    for line in new_lines:
                        if line.strip():
                            try:
                                span = json.loads(line)
                                ts = time.strftime('%H:%M:%S', time.localtime(span['timestamp']))
                                attrs = span.get('attributes', {})
                                print(f"[{ts}] {span['name']}")
                                if attrs:
                                    for k, v in attrs.items():
                                        print(f"        {k}: {v}")
                            except json.JSONDecodeError:
                                pass
            
            time.sleep(0.5)
    
    def cleanup(self):
        """Stop all agents."""
        print("\n🛑 Stopping agents...")
        for p in self.processes:
            p.terminate()
            p.join(timeout=2)
        print("✅ All agents stopped")
    
    def run_ping_demo(self):
        """Simple ping-pong demo."""
        print("\n🏓 PING-PONG DEMO")
        print("=" * 40)
        
        # Start ping agent
        self.start_agent(PingAgent)
        time.sleep(1)
        
        # Send pings
        for i in range(3):
            self.emit_span("swarmsh.ping.request", {"source": f"demo_{i}", "count": i})
            time.sleep(2)
        
        # Monitor results
        self.monitor_spans(5)
    
    def run_governance_demo(self):
        """Governance workflow demo."""
        print("\n⚖️ GOVERNANCE WORKFLOW DEMO")
        print("=" * 40)
        
        # Start Roberts agent
        self.start_agent(RobertsAgent)
        time.sleep(1)
        
        # Open motion
        self.emit_span("swarmsh.roberts.open", {
            "meeting_id": "board_2024_q1",
            "motion_id": "approve_sprint_42"
        })
        time.sleep(2)
        
        # Call vote
        self.emit_span("swarmsh.roberts.vote", {
            "motion_id": "approve_sprint_42",
            "voting_method": "voice_vote"
        })
        time.sleep(2)
        
        # Close with passing vote
        self.emit_span("swarmsh.roberts.close", {
            "motion_id": "approve_sprint_42",
            "result": "passed",
            "votes_yes": 7,
            "votes_no": 2,
            "sprint_number": "42"
        })
        
        # Monitor results
        self.monitor_spans(5)
    
    def run_full_cycle_demo(self):
        """Full governance → delivery → optimization cycle."""
        print("\n🔄 FULL CYCLE DEMO (Governance → Delivery → Optimization)")
        print("=" * 60)
        
        # Start all agents
        print("Starting all framework agents...")
        self.start_agent(RobertsAgent)
        self.start_agent(ScrumAgent)
        self.start_agent(LeanAgent)
        time.sleep(2)
        
        # Phase 1: Governance approval
        print("\n📋 Phase 1: Governance Approval")
        self.emit_span("swarmsh.roberts.open", {"meeting_id": "quarterly", "motion_id": "sprint_q4_2024"})
        time.sleep(1)
        
        self.emit_span("swarmsh.roberts.vote", {
            "motion_id": "sprint_q4_2024",
            "voting_method": "ballot"
        })
        time.sleep(1)
        
        self.emit_span("swarmsh.roberts.close", {
            "motion_id": "sprint_q4_2024",
            "result": "passed",
            "votes_yes": 8,
            "votes_no": 1,
            "sprint_number": "q4_2024"
        })
        time.sleep(2)
        
        # Phase 2: Sprint execution
        print("\n🏃 Phase 2: Sprint Execution")
        self.emit_span("swarmsh.scrum.plan", {
            "sprint_number": "q4_2024",
            "team_id": "alpha",
            "story_points": 42
        })
        time.sleep(2)
        
        # Daily standups
        for day in range(1, 4):
            self.emit_span("swarmsh.scrum.daily", {
                "team_id": "alpha",
                "day": day,
                "blockers": 1 if day == 2 else 0
            })
            time.sleep(1)
        
        # Sprint review with quality issue
        print("\n📊 Phase 3: Sprint Review (Quality Issue Detected)")
        self.emit_span("swarmsh.scrum.review", {
            "sprint_number": "q4_2024",
            "velocity": 38,
            "defect_rate": 4.7,  # Above 3% threshold
            "customer_satisfaction": 92
        })
        time.sleep(2)
        
        # Phase 4: Lean optimization
        print("\n🔧 Phase 4: Lean Six Sigma Optimization")
        self.emit_span("swarmsh.lean.define", {
            "project_id": "defect_reduction_q4",
            "problem_statement": "Defect rate 4.7% exceeds 3% target"
        })
        time.sleep(1)
        
        # DMAIC cycle
        for phase in ["measure", "analyze", "improve"]:
            self.emit_span(f"swarmsh.lean.{phase}", {
                "project_id": "defect_reduction_q4",
                "phase": phase.upper()
            })
            time.sleep(1)
        
        # Control with governance approval request
        self.emit_span("swarmsh.lean.control", {
            "project_id": "defect_reduction_q4",
            "validated": True,
            "new_defect_rate": 2.1
        })
        
        # Monitor the full cycle
        self.monitor_spans(10)


def main():
    """Run swarm demos."""
    demo = SwarmDemo()
    
    try:
        demo.setup()
        
        if len(sys.argv) > 1:
            demo_type = sys.argv[1].lower()
            
            if demo_type == "ping":
                demo.run_ping_demo()
            elif demo_type == "governance":
                demo.run_governance_demo()
            elif demo_type == "full":
                demo.run_full_cycle_demo()
            else:
                print(f"Unknown demo type: {demo_type}")
                print("Available demos: ping, governance, full")
        else:
            # Run all demos
            demo.run_ping_demo()
            demo.cleanup()
            time.sleep(2)
            
            demo.run_governance_demo()
            demo.cleanup()
            time.sleep(2)
            
            demo.run_full_cycle_demo()
            
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted")
    finally:
        demo.cleanup()
        print("\n✨ Demo complete!")


if __name__ == "__main__":
    main()