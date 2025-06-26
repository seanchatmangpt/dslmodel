#!/usr/bin/env python3
"""
Autonomous Evolution Health Tests - 8020 Critical Path Validation
Focus on highest impact validation that covers 80% of system reliability
"""

import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test imports with proper path handling
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dslmodel.commands.autonomous_evolution_daemon import AutonomousEvolutionDaemon
from src.dslmodel.generated.models.autonomous_evolution_loop import (
    Autonomous_evolution_scheduler,
    Autonomous_evolution_cycle,
    Autonomous_evolution_meaningful_work
)


class TestAutonomousEvolutionHealth:
    """Critical health tests for autonomous evolution system"""
    
    @pytest.fixture
    def daemon(self):
        """Create daemon instance for testing"""
        return AutonomousEvolutionDaemon(base_path=Path.cwd())
    
    def test_weaver_models_importable(self):
        """CRITICAL: Test that Weaver-generated models can be imported and instantiated"""
        # Test scheduler model
        scheduler = Autonomous_evolution_scheduler(
            scheduler_id="test-scheduler",
            schedule_interval_minutes=10,
            scheduler_state="testing"
        )
        assert scheduler.scheduler_id == "test-scheduler"
        assert scheduler.schedule_interval_minutes == 10
        
        # Test cycle model
        cycle = Autonomous_evolution_cycle(
            cycle_id="test-cycle",
            scheduler_id="test-scheduler", 
            cycle_number=1,
            selected_strategy="performance",
            meaningful_work_achieved=True
        )
        assert cycle.cycle_id == "test-cycle"
        assert cycle.meaningful_work_achieved is True
        
        # Test meaningful work model
        work = Autonomous_evolution_meaningful_work(
            cycle_id="test-cycle",
            assessment_type="fitness_threshold",
            baseline_fitness=0.75,
            achieved_fitness=0.85,
            improvement_percentage=13.3,
            meaningful_threshold=5.0,
            work_classification="meaningful",
            deployment_recommended=True
        )
        assert work.deployment_recommended is True
        assert work.improvement_percentage == 13.3
    
    def test_telemetry_emission_works(self):
        """CRITICAL: Test that OTEL telemetry emission doesn't crash"""
        scheduler = Autonomous_evolution_scheduler(
            scheduler_id="telemetry-test",
            schedule_interval_minutes=10,
            scheduler_state="testing"
        )
        
        # Should not raise exception
        trace_id = scheduler.emit_telemetry()
        assert isinstance(trace_id, str)
        assert len(trace_id) > 0
    
    def test_daemon_initialization(self, daemon):
        """CRITICAL: Test daemon can be created and initialized"""
        assert daemon.scheduler_id.startswith("autonomous-")
        assert daemon.schedule_interval == 10 * 60  # 10 minutes
        assert daemon.meaningful_work_threshold == 0.05  # 5%
        assert len(daemon.strategies) == 5  # 5 evolution strategies
        assert "performance" in daemon.strategies
        assert "quality" in daemon.strategies
    
    @pytest.mark.asyncio
    async def test_strategy_selection_logic(self, daemon):
        """HIGH: Test strategy selection produces valid results"""
        cycle_id = "test-cycle-001"
        
        # Mock system metrics to avoid dependency on actual system
        with patch.object(daemon, '_get_system_metrics') as mock_metrics:
            mock_metrics.return_value = MagicMock(
                cpu_usage=50.0,
                memory_usage=60.0,
                error_rate=0.0
            )
            
            strategy = await daemon._select_strategy(cycle_id)
            
            # Should return a valid strategy
            assert strategy in daemon.strategies.keys()
            assert isinstance(strategy, str)
            assert len(strategy) > 0
    
    @pytest.mark.asyncio 
    async def test_meaningful_work_assessment(self, daemon):
        """HIGH: Test meaningful work assessment logic"""
        cycle_id = "test-cycle-002"
        
        # Test case 1: High improvement (should be meaningful)
        high_improvement_result = {
            'strategy': 'performance',
            'fitness_improvement': 0.15,  # 15% improvement
            'experiments': 3
        }
        
        assessment = await daemon._assess_meaningful_work(cycle_id, high_improvement_result)
        
        assert assessment['deployment_recommended'] is True
        assert assessment['classification'] in ['meaningful', 'highly_meaningful']
        assert assessment['improvement_percentage'] == 15.0
        
        # Test case 2: Low improvement (should not be meaningful)
        low_improvement_result = {
            'strategy': 'performance', 
            'fitness_improvement': 0.01,  # 1% improvement
            'experiments': 3
        }
        
        assessment = await daemon._assess_meaningful_work(cycle_id, low_improvement_result)
        
        assert assessment['deployment_recommended'] is False
        assert assessment['classification'] in ['marginal', 'insignificant']
    
    @pytest.mark.asyncio
    async def test_resource_management_check(self, daemon):
        """HIGH: Test resource limits are enforced"""
        
        # Mock system metrics with high resource usage
        with patch.object(daemon, '_get_system_metrics') as mock_metrics:
            mock_metrics.return_value = MagicMock(
                cpu_usage=90.0,  # Above limit (80%)
                memory_usage=90.0,  # Above limit (85%)
                active_worktrees=10
            )
            
            resource_ok = await daemon._check_resources()
            assert resource_ok is False  # Should reject due to high usage
            
            # Test with normal resource usage
            mock_metrics.return_value = MagicMock(
                cpu_usage=50.0,  # Below limit
                memory_usage=70.0,  # Below limit  
                active_worktrees=2
            )
            
            resource_ok = await daemon._check_resources()
            assert resource_ok is True  # Should accept
    
    def test_evolution_strategies_configured(self, daemon):
        """MEDIUM: Test evolution strategies are properly configured"""
        strategies = daemon.strategies
        
        # Check all expected strategies exist
        expected_strategies = ['performance', 'quality', 'security', 'features', 'architecture']
        for strategy_name in expected_strategies:
            assert strategy_name in strategies
            strategy = strategies[strategy_name]
            
            # Check strategy has required attributes
            assert hasattr(strategy, 'name')
            assert hasattr(strategy, 'description')
            assert hasattr(strategy, 'fitness_weight')
            assert hasattr(strategy, 'resource_intensity')
            
            # Check values are reasonable
            assert 0 <= strategy.fitness_weight <= 1.0
            assert 0 <= strategy.resource_intensity <= 1.0
            assert len(strategy.description) > 10  # Non-trivial description
    
    def test_cron_scripts_exist(self):
        """MEDIUM: Test cron automation scripts exist and are executable"""
        base_path = Path.cwd()
        
        # Check evolution cron script exists
        cron_script = base_path / "evolution_cron.sh"
        assert cron_script.exists(), "evolution_cron.sh missing"
        
        # Check setup script exists
        setup_script = base_path / "setup_evolution_cron.py"
        assert setup_script.exists(), "setup_evolution_cron.py missing"
        
        # Check daemon module exists
        daemon_module = base_path / "src/dslmodel/commands/autonomous_evolution_daemon.py" 
        assert daemon_module.exists(), "autonomous_evolution_daemon.py missing"


class TestRealSystemIntegration:
    """Real system integration tests - verify actual functionality"""
    
    @pytest.mark.asyncio
    async def test_single_evolution_cycle_completes(self):
        """CRITICAL: Test that a real evolution cycle can complete without crashing"""
        daemon = AutonomousEvolutionDaemon()
        daemon.schedule_interval = 5  # Short interval for test
        
        start_time = time.time()
        
        try:
            # Run one real evolution cycle
            await daemon._run_evolution_cycle()
            
            # Verify cycle completed
            assert daemon.cycle_number == 1
            assert len(daemon.evolution_history) == 1
            
            # Verify cycle produced results
            history_entry = daemon.evolution_history[0]
            assert 'cycle_id' in history_entry
            assert 'strategy' in history_entry
            assert 'meaningful_work' in history_entry
            assert isinstance(history_entry['meaningful_work'], bool)
            
            # Verify reasonable completion time (< 30 seconds)
            completion_time = time.time() - start_time
            assert completion_time < 30, f"Cycle took too long: {completion_time:.1f}s"
            
        except Exception as e:
            pytest.fail(f"Evolution cycle crashed: {e}")
    
    def test_setup_evolution_cron_imports(self):
        """HIGH: Test that cron setup script imports work"""
        try:
            # This import should work if the system is healthy
            from setup_evolution_cron import install_cron_job, check_cron_service
            
            # Basic smoke test - these functions should be callable
            assert callable(install_cron_job)
            assert callable(check_cron_service)
            
        except ImportError as e:
            pytest.fail(f"Cron setup imports failed: {e}")


if __name__ == "__main__":
    # Quick smoke test when run directly
    print("🧪 Running autonomous evolution health checks...")
    
    # Test 1: Can we import the models?
    try:
        from src.dslmodel.generated.models.autonomous_evolution_loop import Autonomous_evolution_scheduler
        print("✅ Weaver models importable")
    except ImportError as e:
        print(f"❌ Weaver models failed: {e}")
    
    # Test 2: Can we create daemon?
    try:
        daemon = AutonomousEvolutionDaemon()
        print(f"✅ Daemon created: {daemon.scheduler_id}")
    except Exception as e:
        print(f"❌ Daemon creation failed: {e}")
    
    # Test 3: Do cron scripts exist?
    try:
        base = Path.cwd()
        assert (base / "evolution_cron.sh").exists()
        assert (base / "setup_evolution_cron.py").exists() 
        print("✅ Cron scripts present")
    except AssertionError:
        print("❌ Cron scripts missing")
    
    print("\n🎯 Run full tests with: python -m pytest tests/test_autonomous_evolution_health.py -v")