"""
DSLModel Generated Tests - From Semantic Conventions
Auto-generated test suite - covers 80% of test scenarios
"""

import pytest
from unittest.mock import Mock, patch
from .generated_models import *
from .generated_cli import app
from typer.testing import CliRunner

runner = CliRunner()

class TestGeneratedModels:
    """Test generated Pydantic models"""
    

    def test_create_model(self):
        """Test Create a new DSLModel instance"""
        # Test model creation
        model = CreateModel(
            model_type="test",
            name="test_create"
        )
        
        assert model.model_type == "test"
        assert model.operation_type == "create"
        
        # Test telemetry span creation
        with model.start_span() as span:
            assert span is not None
            # Span context should be active

    def test_validate_model(self):
        """Test Validate a DSLModel instance"""
        # Test model creation
        model = ValidateModel(
            model_type="test",
            name="test_validate"
        )
        
        assert model.model_type == "test"
        assert model.operation_type == "validate"
        
        # Test telemetry span creation
        with model.start_span() as span:
            assert span is not None
            # Span context should be active

    def test_execute_model(self):
        """Test Execute an agent operation"""
        # Test model creation
        model = ExecuteModel(
            model_type="test",
            name="test_execute"
        )
        
        assert model.model_type == "test"
        assert model.operation_type == "execute"
        
        # Test telemetry span creation
        with model.start_span() as span:
            assert span is not None
            # Span context should be active

    def test_run_model(self):
        """Test Run a workflow"""
        # Test model creation
        model = RunModel(
            model_type="test",
            name="test_run"
        )
        
        assert model.model_type == "test"
        assert model.operation_type == "run"
        
        # Test telemetry span creation
        with model.start_span() as span:
            assert span is not None
            # Span context should be active

    def test_health_model(self):
        """Test System health check"""
        # Test model creation
        model = HealthModel(
            model_type="test",
            name="test_health"
        )
        
        assert model.model_type == "test"
        assert model.operation_type == "health"
        
        # Test telemetry span creation
        with model.start_span() as span:
            assert span is not None
            # Span context should be active


class TestGeneratedCLI:
    """Test generated CLI commands"""
    
    def test_weave_generate(self):
        """Test weave generate command"""
        result = runner.invoke(app, ["weave", "generate"])
        assert result.exit_code == 0
        assert "Generation complete" in result.stdout
    
    def test_status_command(self):
        """Test status command"""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "System Status" in result.stdout

class TestTelemetryIntegration:
    """Test OpenTelemetry integration"""
    
    @patch('opentelemetry.trace.get_tracer')
    def test_span_creation(self, mock_tracer):
        """Test that spans are created correctly"""
        mock_span = Mock()
        mock_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = mock_span
        
        model = CreateModel(model_type="test", name="test_create")
        with model.start_span():
            pass
        
        mock_tracer.return_value.start_as_current_span.assert_called_once()

# Performance Tests - Focus on the 20% that matters
class TestPerformance:
    """Test performance of generated code"""
    
    def test_model_creation_speed(self):
        """Test that model creation is fast"""
        import time
        start = time.time()
        
        for i in range(100):
            model = create_model("create", name=f"test_{i}")
        
        duration = time.time() - start
        assert duration < 1.0  # Should create 100 models in under 1 second
