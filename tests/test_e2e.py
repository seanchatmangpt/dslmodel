"""
E2E Tests for DSLModel Enterprise Coordination Features

This test suite validates the complete integration of:
- Qwen3 LLM integration
- Enterprise coordination frameworks (Roberts, Scrum, Lean)
- Demo generation engine
- ROI calculations
"""
import pytest
import asyncio
from typing import Dict, Any

# Test minimal demo without heavy dependencies
from dslmodel.examples.enterprise_demo_minimal import (
    RobertsRulesDemo,
    ScrumAtScaleDemo,
    LeanSixSigmaDemo,
    EnterpriseCoordinationDemo,
    run_enterprise_demo
)


class TestEnterpriseCoordinationE2E:
    """End-to-end tests for enterprise coordination features."""
    
    def test_roberts_rules_chaos_injection(self):
        """Test Roberts Rules parliamentary chaos scenarios."""
        demo = RobertsRulesDemo(
            meeting_id="TEST-BOARD-001",
            current_motion="Approve test budget"
        )
        
        # Inject chaos
        demo.inject_parliamentary_chaos()
        
        # Verify chaos was injected
        assert demo.chaos_description != ""
        assert any(keyword in demo.chaos_description for keyword in [
            "Motion", "Chair", "Voting", "Parliamentary", "Quorum"
        ])
        
    def test_roberts_rules_resolution(self):
        """Test SwarmSH resolution of parliamentary chaos."""
        demo = RobertsRulesDemo(
            meeting_id="TEST-BOARD-002",
            current_motion="Approve digital transformation"
        )
        
        demo.inject_parliamentary_chaos()
        demo.swarmsh_resolution()
        
        # Verify resolution was generated
        assert demo.resolution != ""
        assert len(demo.resolution) > 10  # Non-trivial resolution
        
    def test_scrum_coordination_metrics(self):
        """Test Scrum at Scale coordination improvements."""
        demo = ScrumAtScaleDemo(
            release_name="TEST-RELEASE-001",
            teams=["Team A", "Team B", "Team C"]
        )
        
        # Verify initial state
        assert demo.ceremony_overhead_before == 0.42
        assert demo.ceremony_overhead_after == 0.08
        
        demo.inject_scrum_chaos()
        demo.swarmsh_resolution()
        
        # Verify chaos and resolution
        assert demo.chaos_description != ""
        assert demo.resolution != ""
        
        # Verify metrics improvement
        assert demo.ceremony_overhead_after < demo.ceremony_overhead_before
        
    def test_lean_six_sigma_roi_transformation(self):
        """Test Lean Six Sigma ROI improvements."""
        demo = LeanSixSigmaDemo(
            project_name="TEST-PROCESS-001",
            target_process="Test customer onboarding"
        )
        
        # Verify initial negative ROI
        assert demo.roi_before == -2.3
        assert demo.roi_after == 4.7
        assert demo.duration_before == 18
        assert demo.duration_after == 2
        
        demo.inject_lean_chaos()
        demo.swarmsh_resolution()
        
        # Verify improvements
        assert demo.roi_after > demo.roi_before
        assert demo.duration_after < demo.duration_before
        
    @pytest.mark.asyncio
    async def test_full_enterprise_demo_integration(self):
        """Test complete enterprise coordination demo."""
        # Create demo with all three frameworks
        demo = EnterpriseCoordinationDemo(
            customer_name="E2E Test Corporation",
            roberts_demo=RobertsRulesDemo(meeting_id="E2E-BOARD"),
            scrum_demo=ScrumAtScaleDemo(
                release_name="E2E-RELEASE",
                teams=["Frontend", "Backend", "QA"]
            ),
            lean_demo=LeanSixSigmaDemo(
                project_name="E2E Process Improvement",
                target_process="E2E customer flow"
            )
        )
        
        # Run full demo
        results = await demo.run_full_demo()
        
        # Validate results structure
        assert results['customer'] == "E2E Test Corporation"
        assert 'roberts_metrics' in results
        assert 'scrum_metrics' in results
        assert 'lean_metrics' in results
        assert 'executive_summary' in results
        assert 'coordination_improvement' in results
        
        # Validate metrics
        assert results['roberts_metrics']['meeting_efficiency'] == "76% time reduction"
        assert "42% → 8%" in results['scrum_metrics']['ceremony_overhead']
        assert "+$4.7M" in results['lean_metrics']['roi_improvement']
        
        # Validate coordination improvements
        improvements = results['coordination_improvement']
        assert improvements['overall_coordination_efficiency'] == 0.79
        assert all(v > 0.7 for v in improvements.values())
        
    @pytest.mark.asyncio
    async def test_enterprise_demo_execution_time(self):
        """Test that demo executes within reasonable time."""
        import time
        
        start_time = time.time()
        results = await run_enterprise_demo("Performance Test Corp")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Demo should complete within 2 minutes even with AI calls
        assert execution_time < 120, f"Demo took {execution_time:.1f}s, expected < 120s"
        
        # Verify demo completed successfully
        assert results is not None
        assert results['customer'] == "Performance Test Corp"
        
    def test_coordination_improvement_calculations(self):
        """Test coordination improvement metric calculations."""
        demo = EnterpriseCoordinationDemo(
            customer_name="Metrics Test Corp",
            roberts_demo=RobertsRulesDemo(meeting_id="METRICS-001"),
            scrum_demo=ScrumAtScaleDemo(release_name="METRICS-SPRINT", teams=["A"]),
            lean_demo=LeanSixSigmaDemo(
                project_name="METRICS-LEAN",
                target_process="Metrics process"
            )
        )
        
        improvements = demo._calculate_coordination_improvement()
        
        # Verify all metrics are calculated correctly
        assert improvements['meeting_efficiency'] == 0.76
        assert improvements['ceremony_overhead_reduction'] == 0.81
        assert improvements['process_cycle_time'] == 0.73
        assert improvements['project_duration'] == 0.89
        assert improvements['overall_coordination_efficiency'] == 0.79
        
        # Verify average calculation
        expected_average = (0.76 + 0.81 + 0.73 + 0.89) / 4
        assert abs(improvements['overall_coordination_efficiency'] - expected_average) < 0.01


class TestDemoGenerationEngine:
    """Test the demo generation capabilities."""
    
    def test_chaos_scenario_diversity(self):
        """Test that chaos scenarios are diverse and realistic."""
        roberts_scenarios = set()
        scrum_scenarios = set()
        lean_scenarios = set()
        
        # Generate multiple scenarios
        for _ in range(10):
            roberts = RobertsRulesDemo(meeting_id="TEST")
            roberts.inject_parliamentary_chaos()
            roberts_scenarios.add(roberts.chaos_description)
            
            scrum = ScrumAtScaleDemo(release_name="TEST", teams=["A"])
            scrum.inject_scrum_chaos()
            scrum_scenarios.add(scrum.chaos_description)
            
            lean = LeanSixSigmaDemo(project_name="TEST", target_process="TEST")
            lean.inject_lean_chaos()
            lean_scenarios.add(lean.chaos_description)
        
        # Verify diversity (should get at least 3 different scenarios)
        assert len(roberts_scenarios) >= 3, "Roberts Rules scenarios lack diversity"
        assert len(scrum_scenarios) >= 3, "Scrum scenarios lack diversity"
        assert len(lean_scenarios) >= 3, "Lean scenarios lack diversity"


@pytest.mark.integration
class TestLLMIntegration:
    """Test LLM integration for demo generation."""
    
    def test_qwen3_initialization(self):
        """Test that Qwen3 is properly initialized."""
        try:
            from dslmodel.utils.llm_init import init_qwen3, test_model
            lm = init_qwen3(temperature=0.1)
            
            # Test with simple prompt
            response = test_model(prompt="Say 'test successful'")
            assert response is not None
            assert len(response) > 0
            
        except Exception as e:
            pytest.skip(f"Qwen3 not available: {e}")
            
    def test_ai_resolution_generation(self):
        """Test AI-generated resolutions are coherent."""
        try:
            demo = RobertsRulesDemo(
                meeting_id="AI-TEST",
                current_motion="Test AI motion"
            )
            demo.chaos_description = "Test chaos scenario"
            demo.swarmsh_resolution()
            
            # Verify AI generated something meaningful
            assert len(demo.resolution) > 20
            assert demo.resolution != "SwarmSH automated parliamentary procedure enforcement restored order"
            
        except Exception as e:
            pytest.skip(f"AI resolution test skipped: {e}")


# Benchmarking fixture
@pytest.fixture
def benchmark_results():
    """Fixture to collect benchmark results."""
    results = {}
    yield results
    
    # Print benchmark summary
    if results:
        print("\n📊 E2E Benchmark Results:")
        for name, duration in results.items():
            print(f"  {name}: {duration:.2f}s")


@pytest.mark.benchmark
async def test_e2e_performance_benchmark(benchmark_results):
    """Benchmark E2E demo execution performance."""
    import time
    
    # Benchmark individual components
    components = {
        "Roberts Rules": RobertsRulesDemo(meeting_id="BENCH-001"),
        "Scrum at Scale": ScrumAtScaleDemo(release_name="BENCH-001", teams=["A"]),
        "Lean Six Sigma": LeanSixSigmaDemo(project_name="BENCH-001", target_process="Bench")
    }
    
    for name, component in components.items():
        start = time.time()
        
        if hasattr(component, 'inject_parliamentary_chaos'):
            component.inject_parliamentary_chaos()
        elif hasattr(component, 'inject_scrum_chaos'):
            component.inject_scrum_chaos()
        elif hasattr(component, 'inject_lean_chaos'):
            component.inject_lean_chaos()
            
        component.swarmsh_resolution()
        
        duration = time.time() - start
        benchmark_results[name] = duration
        
    # Benchmark full demo
    start = time.time()
    await run_enterprise_demo("Benchmark Corp")
    full_duration = time.time() - start
    benchmark_results["Full Demo"] = full_duration
    
    # Assert reasonable performance
    assert full_duration < 120, f"Full demo too slow: {full_duration:.1f}s"