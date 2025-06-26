#!/usr/bin/env python3
"""
Simple LLM Test with qwen3
Test basic LLM functionality without complex coordination
"""

import dspy
import time
from pathlib import Path

def test_qwen3_basic():
    """Test basic qwen3 functionality"""
    print("🧠 Testing ollama/qwen3 basic functionality")
    print("=" * 50)
    
    try:
        # Initialize LM
        lm = dspy.LM(model="ollama/qwen3", max_tokens=200, temperature=0.1)
        dspy.settings.configure(lm=lm)
        
        print("✅ LLM initialized successfully")
        print(f"   Model: ollama/qwen3")
        print(f"   Max tokens: 200")
        
        # Test simple signature
        class SimpleAnalysis(dspy.Signature):
            """Analyze system state and provide recommendations"""
            system_info = dspy.InputField(desc="Current system information")
            analysis = dspy.OutputField(desc="Brief analysis and recommendation")
        
        analyzer = dspy.ChainOfThought(SimpleAnalysis)
        
        # Test with coordination-like input
        system_info = """
        System State:
        - Active work items: 15
        - Teams: backend, frontend, qa
        - Average progress: 45%
        - System health: good
        """
        
        print("\n🔍 Testing analysis...")
        result = analyzer(system_info=system_info)
        
        print("✅ LLM analysis completed")
        print(f"   Input: System state with 15 active items")
        print(f"   Output: {result.analysis[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_coordination_decision():
    """Test coordination-style decision making"""
    print("\n🎯 Testing coordination decision making")
    print("=" * 50)
    
    try:
        lm = dspy.LM(model="ollama/qwen3", max_tokens=150, temperature=0.2)
        dspy.settings.configure(lm=lm)
        
        class WorkDecision(dspy.Signature):
            """Decide what work action to take"""
            current_state = dspy.InputField(desc="Current work state")
            action = dspy.OutputField(desc="Recommended action")
            reasoning = dspy.OutputField(desc="Brief reasoning")
        
        decider = dspy.ChainOfThought(WorkDecision)
        
        # Test decision scenario
        state = "5 active work items, team capacity available, no critical issues"
        
        result = decider(current_state=state)
        
        print("✅ Decision making test completed")
        print(f"   State: {state}")
        print(f"   Action: {result.action}")
        print(f"   Reasoning: {result.reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Decision test failed: {e}")
        return False

def test_multiple_decisions():
    """Test multiple decision cycles"""
    print("\n🔄 Testing multiple decision cycles")
    print("=" * 50)
    
    try:
        lm = dspy.LM(model="ollama/qwen3", max_tokens=100, temperature=0.3)
        dspy.settings.configure(lm=lm)
        
        class QuickDecision(dspy.Signature):
            """Make quick coordination decision"""
            scenario = dspy.InputField(desc="Current scenario")
            decision = dspy.OutputField(desc="Quick decision")
        
        quick_decider = dspy.ChainOfThought(QuickDecision)
        
        scenarios = [
            "Low work capacity - need to claim more work",
            "High work load - focus on completion", 
            "Balanced state - maintain current pace"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            result = quick_decider(scenario=scenario)
            print(f"   Cycle {i}: {scenario}")
            print(f"           → {result.decision[:80]}...")
        
        print("✅ Multiple cycles completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Multiple cycles failed: {e}")
        return False

def benchmark_llm_speed():
    """Benchmark LLM response speed"""
    print("\n⚡ Benchmarking LLM speed")
    print("=" * 50)
    
    try:
        lm = dspy.LM(model="ollama/qwen3", max_tokens=50, temperature=0.0)
        dspy.settings.configure(lm=lm)
        
        class FastDecision(dspy.Signature):
            """Fast decision making"""
            input = dspy.InputField(desc="Input")
            output = dspy.OutputField(desc="Output")
        
        fast_decider = dspy.ChainOfThought(FastDecision)
        
        # Run multiple fast decisions
        times = []
        for i in range(3):
            start_time = time.time()
            result = fast_decider(input=f"Quick decision {i+1}")
            duration = time.time() - start_time
            times.append(duration)
            print(f"   Decision {i+1}: {duration:.2f}s")
        
        avg_time = sum(times) / len(times)
        print(f"\n📊 Performance:")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   Min time: {min(times):.2f}s")
        print(f"   Max time: {max(times):.2f}s")
        
        return avg_time < 10.0  # Should be reasonable for local LLM
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False

def main():
    """Run all LLM tests"""
    print("🧠 Simple LLM Test Suite with ollama/qwen3")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_qwen3_basic),
        ("Coordination Decision", test_coordination_decision),
        ("Multiple Cycles", test_multiple_decisions),
        ("Speed Benchmark", benchmark_llm_speed),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n⚡ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! qwen3 is working for coordination!")
        print("\n💡 Ready for full LLM coordination loop:")
        print("   python llm_coordination_agent.py 3")
    else:
        print("⚠️ Some tests failed. Check ollama setup.")

if __name__ == "__main__":
    main()