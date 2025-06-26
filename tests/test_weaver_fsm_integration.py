"""
Tests for Weaver + FSM + DSLModel Integration

Validates that all components work together correctly.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from dslmodel.otel.fsm_weaver_integration import (
    ObservableFSMMixin,
    WeaverFSMModel,
    WorkflowStateGenerator,
    observable_trigger
)
from dslmodel.dsl_models import DSLModel
from dslmodel.mixins.fsm_mixin import FSMMixin

from enum import Enum
from pydantic import Field


class TestState(str, Enum):
    """Test states for FSM."""
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"


class TestObservableFSM(WeaverFSMModel):
    """Test model with observable FSM."""
    
    name: str = Field(description="Test name")
    counter: int = Field(default=0)
    state: TestState = Field(default=TestState.IDLE)
    
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.setup_fsm(TestState, initial=TestState.IDLE)
        
    @observable_trigger(source=TestState.IDLE, dest=TestState.RUNNING)
    def start(self):
        self.counter += 1
        return True
        
    @observable_trigger(source=TestState.RUNNING, dest=TestState.DONE)  
    def finish(self):
        self.counter += 10
        return True


class TestWeaverFSMIntegration:
    """Test the Weaver FSM integration."""
    
    def test_observable_fsm_mixin_inheritance(self):
        """Test that ObservableFSMMixin properly extends FSMMixin."""
        assert issubclass(ObservableFSMMixin, FSMMixin)
        
    def test_weaver_fsm_model_inheritance(self):
        """Test that WeaverFSMModel combines DSLModel and ObservableFSMMixin."""
        assert issubclass(WeaverFSMModel, DSLModel)
        assert issubclass(WeaverFSMModel, ObservableFSMMixin)
        
    def test_fsm_state_transitions(self):
        """Test basic FSM state transitions work."""
        model = TestObservableFSM(name="test")
        
        # Initial state
        assert model.state == TestState.IDLE
        assert model.counter == 0
        
        # Transition to running
        model.start()
        assert model.state == TestState.RUNNING
        assert model.counter == 1
        
        # Transition to done
        model.finish()
        assert model.state == TestState.DONE
        assert model.counter == 11
        
    def test_model_serialization(self):
        """Test model can be serialized/deserialized."""
        model = TestObservableFSM(name="serialize-test")
        model.start()
        
        # Serialize
        data = model.model_dump()
        assert data["name"] == "serialize-test"
        assert data["state"] == TestState.RUNNING
        assert data["counter"] == 1
        
        # Deserialize
        model2 = TestObservableFSM(**data)
        assert model2.name == model.name
        assert model2.state == model.state
        assert model2.counter == model.counter
        
    @patch('dslmodel.otel.fsm_weaver_integration.trace.get_tracer')
    def test_observability_setup(self, mock_get_tracer):
        """Test observability is properly initialized."""
        mock_tracer = Mock()
        mock_get_tracer.return_value = mock_tracer
        
        model = TestObservableFSM(name="obs-test")
        model.setup_observability("test-service")
        
        assert model._tracer == mock_tracer
        mock_get_tracer.assert_called_with("test-service")
        
    def test_workflow_state_generator_init(self):
        """Test WorkflowStateGenerator initialization."""
        generator = WorkflowStateGenerator()
        
        assert generator.weaver is not None
        assert generator.weaver.project_root == Path.cwd()
        
    def test_create_workflow_semconv(self, tmp_path):
        """Test semantic convention generation for workflows."""
        # Mock weaver with tmp path
        from dslmodel.otel.weaver_integration import WeaverForgeIntegration
        weaver = WeaverForgeIntegration(project_root=tmp_path)
        generator = WorkflowStateGenerator(weaver)
        
        # Create semconv
        semconv_path = generator.create_workflow_semconv(
            workflow_name="test_workflow",
            states=["start", "process", "end"],
            attributes={
                "user_id": {
                    "type": "string",
                    "requirement_level": "required",
                    "brief": "User identifier"
                }
            }
        )
        
        # Verify file created
        assert semconv_path.exists()
        assert semconv_path.name == "test_workflow.yaml"
        
        # Verify content
        import yaml
        content = yaml.safe_load(semconv_path.read_text())
        
        assert "groups" in content
        assert content["groups"][0]["id"] == "test_workflow_workflow"
        assert len(content["groups"][0]["attributes"]) == 4  # state + 2 defaults + user_id
        
    def test_dslmodel_features_preserved(self):
        """Test that DSLModel features work with FSM integration."""
        model = TestObservableFSM(name="feature-test")
        
        # Field names
        assert "name" in model.field_names()
        assert "counter" in model.field_names()
        
        # JSON export
        json_str = model.model_dump_json()
        assert "feature-test" in json_str
        
        # Model config
        assert model.model_config["arbitrary_types_allowed"] == True
        
    def test_observable_trigger_decorator(self):
        """Test the observable_trigger decorator."""
        
        class TestModel(WeaverFSMModel):
            count: int = Field(default=0)
            
            @observable_trigger(source="a", dest="b")
            def transition(self):
                self.count += 1
                return True
                
        # Verify decorator preserves function
        assert hasattr(TestModel.transition, "__name__")
        assert TestModel.transition.__name__ == "transition"
        
    def test_multiple_inheritance_mro(self):
        """Test method resolution order is correct."""
        mro = WeaverFSMModel.__mro__
        
        # DSLModel should come before ObservableFSMMixin
        dsl_index = mro.index(DSLModel)
        fsm_index = mro.index(ObservableFSMMixin)
        
        assert dsl_index < fsm_index
        
    def test_fsm_template_generation(self, tmp_path):
        """Test FSM template creation."""
        weaver = WeaverForgeIntegration(project_root=tmp_path) 
        generator = WorkflowStateGenerator(weaver)
        
        # Ensure templates
        generator._ensure_fsm_templates()
        
        # Check template exists
        template_path = (
            tmp_path / "weaver_templates" / "registry" / 
            "python" / "fsm_pydantic_model.j2"
        )
        assert template_path.exists()
        
        # Verify template content
        content = template_path.read_text()
        assert "WeaverFSMModel" in content
        assert "setup_fsm" in content
        assert "@trigger" in content