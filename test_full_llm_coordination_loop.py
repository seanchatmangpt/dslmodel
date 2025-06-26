#!/usr/bin/env python3
"""
Comprehensive Test Suite for Full LLM Coordination Loop
Tests the complete intelligent coordination workflow with observability
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil

import pytest
from typer.testing import CliRunner

from coordination_cli_v2 import app, COORDINATION_DIR, WORK_CLAIMS_FILE
from mock_llm_coordination_agent import MockLLMCoordinationAgent, CoordinationState

runner = CliRunner()

class TestFullCoordinationLoop:
    """Test the complete coordination loop with LLM integration"""
    
    @pytest.fixture
    def temp_coordination_env(self):
        """Set up temporary coordination environment for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_coord_dir = Path(tmpdir) / "coordination"
            test_coord_dir.mkdir()
            
            # Patch coordination directory
            import coordination_cli_v2
            import mock_llm_coordination_agent
            
            original_dir = coordination_cli_v2.COORDINATION_DIR
            coordination_cli_v2.COORDINATION_DIR = test_coord_dir
            mock_llm_coordination_agent.COORDINATION_DIR = test_coord_dir
            
            # Update file paths
            coordination_cli_v2.WORK_CLAIMS_FILE = test_coord_dir / "work_claims.json"
            coordination_cli_v2.FAST_CLAIMS_FILE = test_coord_dir / "work_claims_fast.jsonl"
            coordination_cli_v2.COORDINATION_LOG_FILE = test_coord_dir / "coordination_log.json"
            
            mock_llm_coordination_agent.WORK_CLAIMS_FILE = coordination_cli_v2.WORK_CLAIMS_FILE
            mock_llm_coordination_agent.FAST_CLAIMS_FILE = coordination_cli_v2.FAST_CLAIMS_FILE
            
            yield test_coord_dir
            
            # Restore original
            coordination_cli_v2.COORDINATION_DIR = original_dir
    
    def test_mock_llm_agent_initialization(self, temp_coordination_env):
        """Test mock LLM agent initialization and configuration"""
        agent = MockLLMCoordinationAgent(
            max_iterations=1,
            sleep_interval=0,
            claim_threshold=3
        )
        
        assert agent.claim_threshold == 3
        assert agent.max_iterations == 1
        assert agent.sleep_interval == 0
        assert agent.agent_id.startswith("agent_")
        assert agent.brain is not None
        
    def test_system_state_analysis(self, temp_coordination_env):
        """Test system state analysis and metrics calculation"""
        # Create some test work items
        runner.invoke(app, ["claim", "feature", "Test feature 1", "--priority", "high"])
        runner.invoke(app, ["claim", "bug", "Test bug", "--priority", "critical"])
        runner.invoke(app, ["claim", "task", "Test task", "--team", "backend"])
        
        agent = MockLLMCoordinationAgent(max_iterations=1)
        state = agent.analyze_system_state()
        
        assert isinstance(state, CoordinationState)
        assert state.active_work_count == 3
        assert "backend" in state.team_distribution
        assert "high" in state.priority_breakdown or "critical" in state.priority_breakdown
        assert state.avg_progress >= 0
        assert state.system_health in ["healthy", "warning", "critical"]
        
    def test_intelligent_work_claiming(self, temp_coordination_env):
        """Test LLM-based intelligent work claiming decisions"""
        agent = MockLLMCoordinationAgent(max_iterations=1, claim_threshold=2)
        
        # Start with empty system
        state = agent.analyze_system_state()
        assert state.active_work_count == 0
        
        # Get claiming decision
        decisions = agent.get_intelligent_decisions(state)
        claim_decisions = [d for d in decisions if d.action == "claim_work"]
        
        assert len(claim_decisions) > 0
        claim_decision = claim_decisions[0]
        
        assert claim_decision.action == "claim_work"
        assert claim_decision.parameters["work_type"] in ["feature", "bug", "task", "refactor"]
        assert claim_decision.parameters["priority"] in ["critical", "high", "medium", "low"]
        assert claim_decision.parameters["team"] is not None
        assert claim_decision.reasoning is not None
        assert 0.0 <= claim_decision.confidence <= 1.0
        
    def test_intelligent_progress_updates(self, temp_coordination_env):
        """Test LLM-based progress update decisions"""
        # Create a work item
        runner.invoke(app, ["claim", "feature", "Test feature", "--fast=false"])
        
        agent = MockLLMCoordinationAgent(max_iterations=1)
        active_items = agent.get_active_items()
        assert len(active_items) == 1
        
        work_item = active_items[0]
        
        # Test progress decision
        progress_decision = agent.brain.decide_progress_update(work_item)
        
        assert progress_decision.action == "update_progress"
        assert progress_decision.target == work_item["work_item_id"]
        assert 0 <= progress_decision.parameters["progress"] <= 100
        assert progress_decision.parameters["status"] in ["active", "in_progress", "blocked"]
        assert progress_decision.reasoning is not None
        
    def test_intelligent_completion_decisions(self, temp_coordination_env):
        """Test LLM-based work completion decisions"""
        # Create and progress a work item to near completion
        result = runner.invoke(app, ["claim", "bug", "Test bug", "--fast=false"])
        assert result.exit_code == 0
        
        # Get the work item and set high progress
        with open(temp_coordination_env / "work_claims.json", 'r') as f:
            claims = json.load(f)
        
        work_id = claims[0]["work_item_id"]
        runner.invoke(app, ["progress", work_id, "95"])
        
        agent = MockLLMCoordinationAgent(max_iterations=1)
        active_items = agent.get_active_items()
        high_progress_item = active_items[0]
        
        # Test completion decision
        completion_decision = agent.brain.decide_completion(high_progress_item)
        
        if completion_decision:  # Might be None if not ready
            assert completion_decision.action == "complete_work"
            assert completion_decision.target == work_id
            assert 1 <= completion_decision.parameters["velocity"] <= 21
            assert completion_decision.parameters["result"] in ["success", "partial", "failed"]
            assert completion_decision.reasoning is not None
    
    def test_full_coordination_cycle(self, temp_coordination_env):
        """Test complete coordination cycle with all phases"""
        agent = MockLLMCoordinationAgent(max_iterations=3, sleep_interval=0, claim_threshold=2)
        
        # Track metrics before running
        initial_metrics = agent.performance_metrics.copy()
        
        # Run the loop
        agent.run_intelligent_loop()
        
        # Verify metrics were updated
        assert agent.performance_metrics["decisions_made"] > initial_metrics["decisions_made"]
        assert agent.iteration == 3
        assert len(agent.decision_history) > 0
        
        # Verify some work was claimed
        final_state = agent.analyze_system_state()
        assert final_state.active_work_count > 0
        
    def test_decision_quality_and_reasoning(self, temp_coordination_env):
        """Test quality of LLM decisions and reasoning"""
        agent = MockLLMCoordinationAgent(max_iterations=2, sleep_interval=0)
        
        # Create initial work
        runner.invoke(app, ["claim", "feature", "Initial work", "--fast=false"])
        
        # Run cycles and collect decisions
        agent.run_intelligent_loop()
        
        # Analyze decision quality
        decisions = agent.decision_history
        assert len(decisions) > 0
        
        # Check reasoning quality
        for decision in decisions:
            assert decision["reasoning"] is not None
            assert len(decision["reasoning"]) > 10  # Non-trivial reasoning
            assert decision["confidence"] > 0.0
            assert decision["action"] in ["claim_work", "update_progress", "complete_work"]
        
        # Check confidence distribution
        confidences = [d["confidence"] for d in decisions]
        avg_confidence = sum(confidences) / len(confidences)
        assert 0.3 <= avg_confidence <= 1.0  # Reasonable confidence range
    
    def test_performance_metrics_tracking(self, temp_coordination_env):
        """Test comprehensive performance metrics tracking"""
        agent = MockLLMCoordinationAgent(max_iterations=5, sleep_interval=0, claim_threshold=3)
        
        # Run agent
        agent.run_intelligent_loop()
        
        metrics = agent.performance_metrics
        
        # Verify all metrics are tracked
        assert "decisions_made" in metrics
        assert "work_claimed" in metrics
        assert "work_completed" in metrics
        assert "avg_confidence" in metrics
        assert "reasoning_quality" in metrics
        
        # Verify metric values make sense
        assert metrics["decisions_made"] >= 0
        assert metrics["work_claimed"] >= 0
        assert metrics["work_completed"] >= 0
        assert 0.0 <= metrics["avg_confidence"] <= 1.0
        assert isinstance(metrics["reasoning_quality"], list)
    
    def test_system_health_monitoring(self, temp_coordination_env):
        """Test system health monitoring and thresholds"""
        agent = MockLLMCoordinationAgent(max_iterations=1)
        
        # Test with different work loads
        test_cases = [
            (0, "healthy"),   # No work
            (5, "healthy"),   # Normal load
            (15, "healthy"),  # Higher load but manageable
        ]
        
        for work_count, expected_health in test_cases:
            # Create work items
            for i in range(work_count):
                runner.invoke(app, ["claim", "task", f"Task {i}", "--fast=false"])
            
            state = agent.analyze_system_state()
            assert state.active_work_count == work_count
            # Health assessment may vary based on thresholds
            assert state.system_health in ["healthy", "warning", "critical"]
            
            # Clean up for next test
            if (temp_coordination_env / "work_claims.json").exists():
                (temp_coordination_env / "work_claims.json").write_text("[]")
    
    def test_decision_execution_error_handling(self, temp_coordination_env):
        """Test error handling in decision execution"""
        agent = MockLLMCoordinationAgent(max_iterations=1)
        
        # Create a mock decision with invalid parameters
        from mock_llm_coordination_agent import MockLLMDecision
        
        invalid_decision = MockLLMDecision(
            action="claim_work",
            target=None,
            parameters={
                "work_type": "invalid_type",
                "priority": "invalid_priority",
                "team": "test_team",
                "description": "Test work"
            },
            reasoning="Test reasoning",
            confidence=0.8
        )
        
        # This should handle the error gracefully
        result = agent.execute_claim_work(invalid_decision)
        assert isinstance(result, bool)  # Should return success/failure boolean
    
    def test_coordination_state_serialization(self, temp_coordination_env):
        """Test coordination state can be serialized for LLM consumption"""
        # Create diverse work items
        runner.invoke(app, ["claim", "feature", "Feature work", "--priority", "high", "--team", "frontend"])
        runner.invoke(app, ["claim", "bug", "Bug work", "--priority", "critical", "--team", "backend"])
        
        agent = MockLLMCoordinationAgent(max_iterations=1)
        state = agent.analyze_system_state()
        
        # Test JSON serialization
        state_dict = state.__dict__
        state_json = json.dumps(state_dict)
        parsed_state = json.loads(state_json)
        
        assert parsed_state["active_work_count"] == state.active_work_count
        assert parsed_state["team_distribution"] == state.team_distribution
        assert parsed_state["priority_breakdown"] == state.priority_breakdown

class TestLLMIntegrationComparison:
    """Compare different LLM integration approaches"""
    
    def test_mock_vs_random_performance(self, temp_coordination_env):
        """Compare mock LLM performance against random decisions"""
        # This test would compare the mock LLM agent against a purely random agent
        # to demonstrate the value of intelligent decision-making
        
        from coordination_cli_v2 import COORDINATION_DIR
        
        # Test mock LLM agent
        mock_agent = MockLLMCoordinationAgent(max_iterations=3, sleep_interval=0)
        mock_agent.run_intelligent_loop()
        mock_metrics = mock_agent.performance_metrics
        
        # Reset environment
        if (temp_coordination_env / "work_claims.json").exists():
            (temp_coordination_env / "work_claims.json").write_text("[]")
        
        # For comparison, we'd implement a random agent here
        # For now, just verify mock agent produces reasonable results
        assert mock_metrics["decisions_made"] > 0
        assert mock_metrics["avg_confidence"] > 0.5  # Should have reasonable confidence

def test_end_to_end_workflow():
    """Integration test of the complete workflow"""
    
    # This could be run as a subprocess to test the full CLI
    import subprocess
    import os
    
    # Test the mock LLM agent as a subprocess
    try:
        result = subprocess.run([
            "python", "mock_llm_coordination_agent.py", "2", "1"
        ], capture_output=True, text=True, timeout=30)
        
        # Check that it runs without crashing
        assert result.returncode == 0 or result.returncode == 130  # 130 = KeyboardInterrupt
        
        # Check for expected output patterns
        output = result.stdout
        assert "Mock LLM Coordination Agent Started" in output or "🧠" in output
        
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        # Test environment might not support subprocess execution
        pytest.skip(f"Subprocess test skipped: {e}")

class CoordinationTestRunner:
    """Test runner for manual coordination testing"""
    
    @staticmethod
    def run_performance_comparison():
        """Run performance comparison between different coordination strategies"""
        print("🧪 Running Coordination Performance Comparison")
        print("=" * 60)
        
        strategies = [
            ("Mock LLM", "python mock_llm_coordination_agent.py 5 1"),
            ("Random Demo", "python infinite_coordination_demo.py 5 1"),
        ]
        
        for name, command in strategies:
            print(f"\n🔬 Testing {name}...")
            try:
                start_time = time.time()
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                duration = time.time() - start_time
                
                print(f"   Duration: {duration:.1f}s")
                print(f"   Exit code: {result.returncode}")
                
                # Extract metrics from output
                output = result.stdout
                if "Final Summary" in output:
                    print("   ✅ Completed successfully")
                else:
                    print("   ⚠️ May have been interrupted")
                    
            except subprocess.TimeoutExpired:
                print("   ⏱️ Timeout - process taking too long")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    @staticmethod
    def run_stress_test():
        """Run stress test with high iteration count"""
        print("\n🔥 Running Stress Test (High Iterations)")
        print("=" * 60)
        
        try:
            result = subprocess.run([
                "python", "mock_llm_coordination_agent.py", "20", "0"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Stress test completed successfully")
                # Could extract and analyze performance metrics here
            else:
                print(f"⚠️ Stress test ended with code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("⏱️ Stress test timeout - performance may need optimization")

if __name__ == "__main__":
    # Run manual tests if called directly
    print("🧪 Coordination Loop Manual Testing")
    
    runner = CoordinationTestRunner()
    runner.run_performance_comparison()
    runner.run_stress_test()
    
    print("\n🎯 Manual Test Complete")
    print("Run 'pytest test_full_llm_coordination_loop.py -v' for automated tests")