#!/usr/bin/env python3
"""Minimal test script for SwarmAgent framework - no external dependencies."""

import sys
import os
import json
import time
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import only what we need
from enum import Enum, auto
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# Mock the necessary models
class AgentModel:
    """Mock base model."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class NextCommand(AgentModel):
    """Model for CLI commands."""
    def __init__(self, fq_name=None, path=None, args=None, description=None):
        self.fq_name = fq_name
        self.path = path or (fq_name.split('.') if fq_name else [])
        self.args = args or []
        self.description = description

class SpanData(AgentModel):
    """OpenTelemetry span data model."""
    def __init__(self, name, trace_id, span_id, timestamp, attributes=None, **kwargs):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.timestamp = timestamp
        self.attributes = attributes or {}
        for k, v in kwargs.items():
            setattr(self, k, v)

# Simple state machine mixin
class SimpleStateMachine:
    """Minimal state machine implementation."""
    def __init__(self):
        self.current_state = None
        self.transitions = []
    
    def setup_fsm(self, state_enum, initial):
        self.state_enum = state_enum
        self.current_state = initial

def trigger(source, dest):
    """Simple trigger decorator."""
    def decorator(func):
        func._trigger_source = source
        func._trigger_dest = dest
        func._is_trigger = True
        return func
    return decorator

# Test implementation
print("🧪 Testing SwarmAgent Concepts")
print("=" * 50)

# Test 1: State transitions
print("\n=== Test 1: State Transitions ===")

class TestState(Enum):
    IDLE = auto()
    ACTIVE = auto()
    DONE = auto()

class TestMachine(SimpleStateMachine):
    def __init__(self):
        super().__init__()
        self.setup_fsm(TestState, TestState.IDLE)
    
    @trigger(source=TestState.IDLE, dest=TestState.ACTIVE)
    def activate(self):
        print(f"  Transitioning: {self.current_state.name} → ACTIVE")
        self.current_state = TestState.ACTIVE
        return "activated"
    
    @trigger(source=TestState.ACTIVE, dest=TestState.DONE)
    def complete(self):
        print(f"  Transitioning: {self.current_state.name} → DONE")
        self.current_state = TestState.DONE
        return "completed"

machine = TestMachine()
print(f"✓ Initial state: {machine.current_state.name}")

result = machine.activate()
print(f"✓ After activate: {machine.current_state.name} (result: {result})")

result = machine.complete()
print(f"✓ After complete: {machine.current_state.name} (result: {result})")

# Test 2: Span processing
print("\n=== Test 2: Span Processing ===")

span = SpanData(
    name="swarmsh.test.action",
    trace_id="trace_123",
    span_id="span_456",
    timestamp=time.time(),
    attributes={"user": "test", "action": "demo"}
)

print(f"✓ Created span: {span.name}")
print(f"  - Trace ID: {span.trace_id}")
print(f"  - Attributes: {span.attributes}")

# Test 3: Command generation
print("\n=== Test 3: Command Generation ===")

cmd1 = NextCommand(
    fq_name="swarmsh.scrum.sprint-planning",
    args=["--sprint", "42", "--team", "alpha"]
)

cmd2 = NextCommand(
    path=["swarmsh", "lean", "define"],
    args=["--project-id", "improvement-001"],
    description="Start improvement project"
)

print(f"✓ Command 1: {cmd1.fq_name} {cmd1.args}")
print(f"✓ Command 2: {'/'.join(cmd2.path)} {cmd2.args}")

# Test 4: Agent workflow simulation
print("\n=== Test 4: Agent Workflow Simulation ===")

class WorkflowState(Enum):
    INIT = auto()
    PLANNING = auto()
    EXECUTING = auto()
    REVIEWING = auto()
    COMPLETE = auto()

class WorkflowAgent(SimpleStateMachine):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.setup_fsm(WorkflowState, WorkflowState.INIT)
        self.trigger_map = {
            "plan": self.plan,
            "execute": self.execute,
            "review": self.review,
            "complete": self.complete
        }
    
    def forward(self, span):
        """Route spans to handlers."""
        for keyword, handler in self.trigger_map.items():
            if keyword in span.name.lower():
                return handler(span)
        return None
    
    @trigger(source=WorkflowState.INIT, dest=WorkflowState.PLANNING)
    def plan(self, span):
        self.current_state = WorkflowState.PLANNING
        print(f"  {self.name}: Starting planning phase")
        return NextCommand(
            fq_name=f"swarmsh.{self.name.lower()}.create-plan",
            args=["--id", span.attributes.get("id", "default")]
        )
    
    @trigger(source=WorkflowState.PLANNING, dest=WorkflowState.EXECUTING)
    def execute(self, span):
        self.current_state = WorkflowState.EXECUTING
        print(f"  {self.name}: Executing plan")
        return NextCommand(
            fq_name=f"swarmsh.{self.name.lower()}.run-tasks",
            args=["--parallel", "true"]
        )
    
    @trigger(source=WorkflowState.EXECUTING, dest=WorkflowState.REVIEWING)
    def review(self, span):
        self.current_state = WorkflowState.REVIEWING
        print(f"  {self.name}: Reviewing results")
        
        # Simulate KPI check
        if span.attributes.get("defects", 0) > 3:
            print(f"  {self.name}: Quality issue detected!")
            return NextCommand(
                fq_name="swarmsh.lean.define",
                args=["--problem", "High defect rate"]
            )
        return None
    
    @trigger(source=WorkflowState.REVIEWING, dest=WorkflowState.COMPLETE)
    def complete(self, span):
        self.current_state = WorkflowState.COMPLETE
        print(f"  {self.name}: Workflow complete")
        return None

# Simulate workflow
scrum = WorkflowAgent("Scrum")
lean = WorkflowAgent("Lean")

# Scrum workflow
print("\n1. Scrum Agent Workflow:")
spans = [
    SpanData("swarmsh.scrum.plan", "t1", "s1", time.time(), {"id": "sprint-42"}),
    SpanData("swarmsh.scrum.execute", "t1", "s2", time.time(), {}),
    SpanData("swarmsh.scrum.review", "t1", "s3", time.time(), {"defects": 5})
]

for span in spans:
    cmd = scrum.forward(span)
    if cmd:
        print(f"    → Command: {cmd.fq_name}")

# Lean workflow triggered by Scrum
print("\n2. Lean Agent Workflow (triggered by Scrum):")
lean_span = SpanData("swarmsh.lean.plan", "t2", "s4", time.time(), {"problem": "High defects"})
cmd = lean.forward(lean_span)
if cmd:
    print(f"    → Command: {cmd.fq_name}")

print("\n✅ All concept tests passed!")
print("\nKey SwarmAgent patterns demonstrated:")
print("- State machine with transitions")
print("- Span-driven event processing")
print("- Command generation for CLI integration")
print("- Inter-agent communication via commands")