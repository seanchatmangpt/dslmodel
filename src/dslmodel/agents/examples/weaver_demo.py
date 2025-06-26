#!/usr/bin/env python3
"""
Demo showing SwarmAgent integration with OpenTelemetry Weaver.
This demonstrates semantic convention validation and code generation.
"""

import json
import time
import sys
from pathlib import Path

# Add path for direct model import (bypassing package dependencies)
models_path = Path(__file__).parent.parent.parent / "otel" / "models"
sys.path.insert(0, str(models_path))
print(f"Looking for models in: {models_path}")

try:
    from swarm_attributes import (
        SwarmAgentName, SwarmAgentState, VotingMethod, VoteResult, DMAICPhase,
        RobertsSpanAttributes, ScrumSpanAttributes, LeanSpanAttributes,
        PingSpanAttributes, TransitionSpanAttributes
    )
    WEAVER_AVAILABLE = True
except ImportError as e:
    WEAVER_AVAILABLE = False


def demonstrate_weaver_integration():
    """Demonstrate SwarmAgent integration with Weaver semantic conventions."""
    print("🔗 SwarmAgent + OpenTelemetry Weaver Integration Demo")
    print("=" * 60)
    
    if not WEAVER_AVAILABLE:
        print("❌ Weaver models not available")
        return
    
    print("✅ Weaver semantic convention models loaded")
    
    # 1. Demonstrate type-safe span creation
    print("\n1️⃣ Type-safe span creation with Weaver models:")
    print("-" * 50)
    
    # Roberts Rules span
    roberts_attrs = {
        "agent_name": SwarmAgentName.ROBERTS_AGENT,
        "agent_state": SwarmAgentState.VOTING,
        "meeting_id": "board_q1_2024",
        "motion_id": "approve_sprint_42",
        "voting_method": VotingMethod.BALLOT,
        "vote_result": VoteResult.PASSED,
        "votes_yes": 8,
        "votes_no": 1
    }
    
    try:
        roberts_span = RobertsSpanAttributes(**roberts_attrs)
        print(f"✅ Roberts span validated: {roberts_span.motion_id}")
        print(f"   Vote result: {roberts_span.vote_result} ({roberts_span.votes_yes}-{roberts_span.votes_no})")
    except Exception as e:
        print(f"❌ Roberts span validation failed: {e}")
    
    # Scrum span with quality trigger
    scrum_attrs = {
        "agent_name": SwarmAgentName.SCRUM_AGENT,
        "agent_state": SwarmAgentState.REVIEW,
        "sprint_number": "42",
        "team_id": "alpha",
        "velocity": 38,
        "defect_rate": 4.5,  # Above threshold
        "customer_satisfaction": 92
    }
    
    try:
        scrum_span = ScrumSpanAttributes(**scrum_attrs)
        print(f"✅ Scrum span validated: Sprint {scrum_span.sprint_number}")
        print(f"   Defect rate: {scrum_span.defect_rate}% (triggers Lean project)")
    except Exception as e:
        print(f"❌ Scrum span validation failed: {e}")
    
    # Lean project spawn
    lean_attrs = {
        "agent_name": SwarmAgentName.LEAN_AGENT,
        "agent_state": SwarmAgentState.DEFINE,
        "project_id": "defect_reduction_q4",
        "problem_statement": "Defect rate 4.5% exceeds 3% target",
        "phase": DMAICPhase.DEFINE,
        "sponsor": "scrum-agent"
    }
    
    try:
        lean_span = LeanSpanAttributes(**lean_attrs)
        print(f"✅ Lean span validated: {lean_span.project_id}")
        print(f"   Phase: {lean_span.phase} - {lean_span.problem_statement}")
    except Exception as e:
        print(f"❌ Lean span validation failed: {e}")
    
    # 2. Demonstrate semantic convention compliance
    print("\n2️⃣ Semantic convention compliance:")
    print("-" * 50)
    
    # Show enum constraints
    print(f"📋 Valid agent names: {[e.value for e in SwarmAgentName]}")
    print(f"📋 Valid voting methods: {[e.value for e in VotingMethod]}")
    print(f"📋 Valid DMAIC phases: {[e.value for e in DMAICPhase]}")
    
    # Demonstrate validation failure
    print("\n🧪 Testing validation failure:")
    try:
        # Invalid agent name should fail
        invalid_attrs = roberts_attrs.copy()
        invalid_attrs["agent_name"] = "InvalidAgent"
        RobertsSpanAttributes(**invalid_attrs)
        print("❌ Validation should have failed!")
    except Exception as e:
        print(f"✅ Validation correctly rejected invalid agent name: {type(e).__name__}")
    
    # 3. Generate compliant JSONL spans
    print("\n3️⃣ Generating Weaver-compliant JSONL spans:")
    print("-" * 50)
    
    spans = []
    
    # Roberts span
    roberts_span_data = {
        "name": "swarmsh.roberts.vote",
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": roberts_span.model_dump(exclude_none=True)
    }
    spans.append(roberts_span_data)
    
    # Scrum span
    scrum_span_data = {
        "name": "swarmsh.scrum.review",
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": scrum_span.model_dump(exclude_none=True)
    }
    spans.append(scrum_span_data)
    
    # Lean span
    lean_span_data = {
        "name": "swarmsh.lean.define",
        "trace_id": f"trace_{int(time.time() * 1000)}",
        "span_id": f"span_{int(time.time() * 1000000)}",
        "timestamp": time.time(),
        "attributes": lean_span.model_dump(exclude_none=True)
    }
    spans.append(lean_span_data)
    
    # Write to JSONL
    output_dir = Path("/tmp/swarm_weaver_demo")
    output_dir.mkdir(exist_ok=True)
    
    span_file = output_dir / "weaver_compliant_spans.jsonl"
    with span_file.open("w") as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")
    
    print(f"📄 Generated {len(spans)} compliant spans: {span_file}")
    
    # Show sample span
    print("\n📄 Sample compliant span:")
    print(json.dumps(roberts_span_data, indent=2))
    
    # 4. Demonstrate agent coordination validation
    print("\n4️⃣ Agent coordination validation:")
    print("-" * 50)
    
    # Transition span
    transition_attrs = {
        "agent_name": SwarmAgentName.ROBERTS_AGENT,
        "transition_from": SwarmAgentState.VOTING,
        "transition_to": SwarmAgentState.CLOSED,
        "prompt": "Motion passed - triggering sprint planning"
    }
    
    try:
        transition_span = TransitionSpanAttributes(**transition_attrs)
        print(f"✅ Transition validated: {transition_span.transition_from} → {transition_span.transition_to}")
        print(f"   Prompt: {transition_span.prompt}")
    except Exception as e:
        print(f"❌ Transition validation failed: {e}")
    
    # 5. Benefits summary
    print("\n5️⃣ Weaver Integration Benefits:")
    print("-" * 50)
    print("✅ Type safety - Enums prevent invalid values")
    print("✅ Schema validation - Pydantic models validate structure")
    print("✅ Code generation - Models auto-generated from YAML")
    print("✅ Consistency - All agents use same attribute conventions")
    print("✅ Documentation - Self-documenting with field descriptions")
    print("✅ Evolution - Schema versioning and backward compatibility")
    
    print("\n🎉 SwarmAgent Weaver integration demonstration complete!")


if __name__ == "__main__":
    demonstrate_weaver_integration()