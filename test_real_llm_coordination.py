#!/usr/bin/env python3
"""
Test Real LLM Coordination with ollama/qwen3
Demonstrates full LLM integration with a real language model
"""

import os
import sys
import time
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from llm_coordination_agent import LLMCoordinationAgent
from coordination_cli_v2 import COORDINATION_DIR

def test_llm_availability():
    """Test if LLM is available"""
    print("🔍 Testing LLM availability...")
    
    try:
        # Simple init function for testing
        lm = dspy.LM(model="ollama/qwen3")
        
        # Test simple completion
        import dspy
        dspy.settings.configure(lm=lm)
        
        class SimpleTest(dspy.Signature):
            """Test LLM connection"""
            input = dspy.InputField(desc="Test input")
            output = dspy.OutputField(desc="Test output")
        
        test_module = dspy.ChainOfThought(SimpleTest)
        result = test_module(input="Hello, can you respond?")
        
        print(f"✅ LLM connection successful!")
        print(f"   Model: ollama/qwen3")
        print(f"   Response: {result.output[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        print("   Make sure Ollama is running and qwen3 model is available")
        print("   Run: ollama pull qwen2.5:7b")
        return False

def run_real_llm_test():
    """Run coordination test with real LLM"""
    print("\n🧠 Running Real LLM Coordination Test")
    print("=" * 50)
    
    # Ensure clean coordination directory
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize agent with real LLM
    agent = LLMCoordinationAgent(
        model="ollama/qwen3",
        max_iterations=3,
        sleep_interval=5,
        claim_threshold=3
    )
    
    print(f"🚀 Starting LLM Agent")
    print(f"   Model: {agent.lm}")
    print(f"   Max iterations: {agent.max_iterations}")
    print(f"   Claim threshold: {agent.claim_threshold}")
    
    try:
        # Run the intelligent loop
        agent.run_intelligent_loop()
        
        print("\n📊 Final Results:")
        print(f"   Decisions made: {agent.performance_metrics['decisions_made']}")
        print(f"   Work claimed: {agent.performance_metrics['work_claimed']}")
        print(f"   Work completed: {agent.performance_metrics['work_completed']}")
        print(f"   Avg confidence: {agent.performance_metrics['avg_confidence']:.2f}")
        
        # Show sample decisions with reasoning
        print("\n🧠 Sample LLM Decisions:")
        for i, decision in enumerate(agent.decision_history[-3:], 1):
            print(f"   {i}. {decision['action']} (confidence: {decision['confidence']:.2f})")
            print(f"      Reasoning: {decision['reasoning'][:120]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_llm_vs_mock():
    """Compare LLM decisions with mock decisions"""
    print("\n🔬 Comparing LLM vs Mock Decisions")
    print("=" * 50)
    
    try:
        # Test LLM agent
        print("Testing Real LLM Agent...")
        llm_agent = LLMCoordinationAgent(
            model="ollama/qwen3",
            max_iterations=2,
            sleep_interval=1
        )
        
        # Get current state
        state = llm_agent.analyze_system_state()
        decisions = llm_agent.get_llm_recommendations(state)
        
        print(f"LLM Decisions: {len(decisions)}")
        for d in decisions[:2]:
            print(f"  • {d.action}: {d.reasoning[:80]}... (conf: {d.confidence:.2f})")
        
        # Reset for mock comparison
        from mock_llm_coordination_agent import MockLLMCoordinationAgent
        print("\nTesting Mock LLM Agent...")
        mock_agent = MockLLMCoordinationAgent(max_iterations=1)
        mock_state = mock_agent.analyze_system_state()
        mock_decisions = mock_agent.get_intelligent_decisions(mock_state)
        
        print(f"Mock Decisions: {len(mock_decisions)}")
        for d in mock_decisions[:2]:
            print(f"  • {d.action}: {d.reasoning[:80]}... (conf: {d.confidence:.2f})")
        
        print("\n💡 Comparison:")
        print(f"   LLM avg confidence: {sum(d.confidence for d in decisions) / max(1, len(decisions)):.2f}")
        print(f"   Mock avg confidence: {sum(d.confidence for d in mock_decisions) / max(1, len(mock_decisions)):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return False

def run_stress_test():
    """Run stress test with real LLM"""
    print("\n🔥 Running LLM Stress Test")
    print("=" * 50)
    
    try:
        agent = LLMCoordinationAgent(
            model="ollama/qwen3",
            max_iterations=10,
            sleep_interval=2,
            claim_threshold=5
        )
        
        start_time = time.time()
        agent.run_intelligent_loop()
        duration = time.time() - start_time
        
        print(f"\n⚡ Stress Test Results:")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Avg cycle time: {duration / agent.iteration:.1f}s")
        print(f"   Decisions/minute: {agent.performance_metrics['decisions_made'] * 60 / duration:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stress test failed: {e}")
        return False

def analyze_decision_quality():
    """Analyze quality of LLM decisions"""
    print("\n📊 Analyzing LLM Decision Quality")
    print("=" * 50)
    
    try:
        agent = LLMCoordinationAgent(
            model="ollama/qwen3",
            max_iterations=5,
            sleep_interval=1
        )
        
        # Run and collect decisions
        agent.run_intelligent_loop()
        decisions = agent.decision_history
        
        print(f"📈 Quality Metrics:")
        print(f"   Total decisions: {len(decisions)}")
        
        if decisions:
            confidences = [d['confidence'] for d in decisions]
            print(f"   Avg confidence: {sum(confidences) / len(confidences):.2f}")
            print(f"   Min confidence: {min(confidences):.2f}")
            print(f"   Max confidence: {max(confidences):.2f}")
            
            # Analyze by action type
            by_action = {}
            for d in decisions:
                action = d['action']
                if action not in by_action:
                    by_action[action] = []
                by_action[action].append(d['confidence'])
            
            print(f"\n📋 By Action Type:")
            for action, confs in by_action.items():
                avg_conf = sum(confs) / len(confs)
                print(f"   {action}: {len(confs)} decisions, avg confidence {avg_conf:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quality analysis failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🧠 Real LLM Coordination Testing Suite")
    print("Testing with ollama/qwen3")
    print("=" * 60)
    
    tests = [
        ("LLM Availability", test_llm_availability),
        ("Real LLM Test", run_real_llm_test),
        ("LLM vs Mock Comparison", compare_llm_vs_mock),
        ("Decision Quality Analysis", analyze_decision_quality),
    ]
    
    # Add stress test if requested
    if len(sys.argv) > 1 and sys.argv[1] == "stress":
        tests.append(("Stress Test", run_stress_test))
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"   {'✅ PASS' if success else '❌ FAIL'}")
        except KeyboardInterrupt:
            print(f"\n⚡ Test interrupted by user")
            break
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LLM coordination is working perfectly.")
    else:
        print("⚠️ Some tests failed. Check LLM setup and dependencies.")

if __name__ == "__main__":
    main()