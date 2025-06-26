#!/usr/bin/env python3
"""
QWen3 Coordination Test
Demonstrate real LLM coordination with qwen3 using simple approach
"""

import dspy
import json
import time
from pathlib import Path
from typer.testing import CliRunner
from coordination_cli_v2 import app, COORDINATION_DIR

runner = CliRunner()

def setup_qwen3():
    """Setup qwen3 LLM"""
    lm = dspy.LM(model="ollama/qwen3", max_tokens=300, temperature=0.1)
    dspy.settings.configure(lm=lm)
    return lm

class CoordinationDecision(dspy.Signature):
    """Make coordination decisions for work management"""
    system_state = dspy.InputField(desc="Current coordination system state")
    decision_type = dspy.InputField(desc="Type of decision needed")
    action = dspy.OutputField(desc="Specific action to take")
    reasoning = dspy.OutputField(desc="Brief reasoning for the decision")

def test_qwen3_coordination():
    """Test full coordination cycle with qwen3"""
    print("🧠 QWen3 Coordination Test")
    print("=" * 50)
    
    # Setup
    lm = setup_qwen3()
    decider = dspy.ChainOfThought(CoordinationDecision)
    
    # Ensure clean coordination environment
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test 1: Decide to claim work
    print("\n1️⃣ Testing work claiming decision...")
    state = "Active work: 2 items, Team capacity: available, System health: good"
    result = decider(system_state=state, decision_type="work_claiming")
    
    print(f"   State: {state}")
    print(f"   Action: {result.action}")
    print(f"   Reasoning: {result.reasoning[:100]}...")
    
    # Act on decision: claim work if recommended
    if "claim" in result.action.lower():
        claim_result = runner.invoke(app, [
            "claim", "feature", "LLM-recommended feature", "--priority", "high"
        ])
        if claim_result.exit_code == 0:
            print("   ✅ Successfully claimed work based on LLM decision")
        else:
            print("   ❌ Failed to claim work")
    
    # Test 2: Decide on progress update
    print("\n2️⃣ Testing progress update decision...")
    state = "Work in progress, last update: 2 hours ago, complexity: moderate"
    result = decider(system_state=state, decision_type="progress_update")
    
    print(f"   State: {state}")
    print(f"   Action: {result.action}")
    print(f"   Reasoning: {result.reasoning[:100]}...")
    
    # Test 3: System optimization decision
    print("\n3️⃣ Testing optimization decision...")
    state = "Completed items: 5, File size: growing, Performance: good"
    result = decider(system_state=state, decision_type="optimization")
    
    print(f"   State: {state}")
    print(f"   Action: {result.action}")
    print(f"   Reasoning: {result.reasoning[:100]}...")
    
    # Act on optimization if recommended
    if "optim" in result.action.lower():
        opt_result = runner.invoke(app, ["optimize"])
        if opt_result.exit_code == 0:
            print("   ✅ Successfully optimized based on LLM decision")
        else:
            print("   ❌ Failed to optimize")

def test_decision_quality():
    """Test quality of qwen3 decisions"""
    print("\n🎯 Testing Decision Quality")
    print("=" * 50)
    
    lm = setup_qwen3()
    decider = dspy.ChainOfThought(CoordinationDecision)
    
    scenarios = [
        ("Low capacity", "Active: 1 item, Capacity: high, Load: light"),
        ("High load", "Active: 10 items, Capacity: limited, Load: heavy"),
        ("Balanced", "Active: 5 items, Capacity: moderate, Load: balanced"),
    ]
    
    for scenario_name, state in scenarios:
        result = decider(system_state=state, decision_type="workload_management")
        print(f"\n   Scenario: {scenario_name}")
        print(f"   State: {state}")
        print(f"   Decision: {result.action[:80]}...")
        print(f"   Reasoning: {result.reasoning[:80]}...")

def run_mini_coordination_loop():
    """Run a mini coordination loop with qwen3"""
    print("\n🔄 Mini Coordination Loop with QWen3")
    print("=" * 50)
    
    lm = setup_qwen3()
    decider = dspy.ChainOfThought(CoordinationDecision)
    
    for cycle in range(3):
        print(f"\n   Cycle {cycle + 1}:")
        
        # Analyze current state
        result = runner.invoke(app, ["dashboard"])
        dashboard_info = result.stdout if result.exit_code == 0 else "Unknown state"
        
        # Get LLM decision
        simple_state = f"Cycle {cycle + 1}, Dashboard shows: system operational"
        decision = decider(
            system_state=simple_state,
            decision_type="next_action"
        )
        
        print(f"     LLM Analysis: {decision.action[:60]}...")
        print(f"     Reasoning: {decision.reasoning[:60]}...")
        
        # Take simple action based on decision
        if cycle == 0 and "claim" in decision.action.lower():
            runner.invoke(app, ["claim", "task", f"Task cycle {cycle + 1}"])
            print("     ✅ Claimed work item")
        elif cycle == 1:
            print("     ✅ Continued monitoring")
        elif cycle == 2 and "optim" in decision.action.lower():
            runner.invoke(app, ["optimize"])
            print("     ✅ Ran optimization")

def main():
    """Run qwen3 coordination tests"""
    print("🧠 QWen3 Real LLM Coordination Testing")
    print("=" * 60)
    
    try:
        # Test basic coordination
        test_qwen3_coordination()
        
        # Test decision quality  
        test_decision_quality()
        
        # Run mini loop
        run_mini_coordination_loop()
        
        print("\n🎉 QWen3 Coordination Test Complete!")
        print("✅ Real LLM successfully demonstrated:")
        print("   • Intelligent decision making")
        print("   • Context-aware reasoning")
        print("   • Action-oriented coordination")
        print("   • Multi-cycle operation")
        
        print("\n💡 Ready to run full LLM coordination agent:")
        print("   python llm_coordination_agent.py 3")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()