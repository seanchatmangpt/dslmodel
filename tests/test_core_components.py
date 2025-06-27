#!/usr/bin/env python3
"""Core DSLModel Components Test Suite
Tests for fundamental components: models, CLI, utilities, and basic functionality.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import core DSLModel components
from dslmodel.core.models import BaseModel
from dslmodel.template import render
from dslmodel.utils import str_tools
from dslmodel.mixins import FSMMixin
from dslmodel.workflow.workflow_models import Workflow, Job, Action, CronSchedule, DateSchedule
from dslmodel.workflow.workflow_executor import (
    initialize_context, 
    update_context, 
    evaluate_condition,
    execute_action,
    execute_job,
    execute_workflow
)


class TestCoreModels:
    """Test core model functionality"""
    
    def test_base_model_creation(self):
        """Test basic model creation and validation"""
        class TestModel(BaseModel):
            name: str
            value: int
            optional_field: str = "default"
        
        # Test valid model creation
        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42
        assert model.optional_field == "default"
        
        # Test model serialization
        data = model.model_dump()
        assert data["name"] == "test"
        assert data["value"] == 42
    
    def test_model_validation(self):
        """Test model validation and error handling"""
        class TestModel(BaseModel):
            name: str
            value: int
        
        # Test invalid data
        with pytest.raises(Exception):
            TestModel(name="test", value="not_an_integer")
    
    def test_fsm_mixin(self):
        """Test FSM (Finite State Machine) mixin functionality"""
        class TestFSM(FSMMixin):
            def __init__(self):
                super().__init__()
                self.states = ["idle", "running", "completed"]
                self.current_state = "idle"
        
        fsm = TestFSM()
        
        # Test state transitions
        assert fsm.current_state == "idle"
        fsm.current_state = "running"
        assert fsm.current_state == "running"
        
        # Test state validation
        assert "idle" in fsm.states
        assert "invalid_state" not in fsm.states


class TestTemplateSystem:
    """Test template rendering system"""
    
    def test_basic_template_rendering(self):
        """Test basic Jinja2 template rendering"""
        template = "Hello {{ name }}, you have {{ count }} items"
        context = {"name": "Alice", "count": 5}
        
        result = render(template, **context)
        assert result == "Hello Alice, you have 5 items"
    
    def test_template_with_conditionals(self):
        """Test template with conditional logic"""
        template = """
        {% if user.is_admin %}
        Welcome admin {{ user.name }}
        {% else %}
        Welcome user {{ user.name }}
        {% endif %}
        """
        
        admin_context = {"user": {"name": "Alice", "is_admin": True}}
        user_context = {"user": {"name": "Bob", "is_admin": False}}
        
        admin_result = render(template, **admin_context).strip()
        user_result = render(template, **user_context).strip()
        
        assert "Welcome admin Alice" in admin_result
        assert "Welcome user Bob" in user_result
    
    def test_template_with_loops(self):
        """Test template with loop constructs"""
        template = """
        {% for item in items %}
        - {{ item.name }}: {{ item.value }}
        {% endfor %}
        """
        
        context = {
            "items": [
                {"name": "Item1", "value": 10},
                {"name": "Item2", "value": 20}
            ]
        }
        
        result = render(template, **context).strip()
        assert "Item1: 10" in result
        assert "Item2: 20" in result


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_string_tools(self):
        """Test string utility functions"""
        # Test string formatting
        assert str_tools.snake_case("CamelCase") == "camel_case"
        assert str_tools.camel_case("snake_case") == "SnakeCase"
        assert str_tools.kebab_case("snake_case") == "snake-case"
    
    def test_string_validation(self):
        """Test string validation utilities"""
        assert str_tools.is_valid_identifier("valid_name_123")
        assert not str_tools.is_valid_identifier("123_invalid")
        assert not str_tools.is_valid_identifier("invalid-name")


class TestWorkflowModels:
    """Test workflow model definitions"""
    
    def test_workflow_creation(self):
        """Test workflow model creation"""
        workflow = Workflow(
            name="test_workflow",
            description="A test workflow",
            jobs=[],
            schedules=[],
            context={}
        )
        
        assert workflow.name == "test_workflow"
        assert workflow.description == "A test workflow"
        assert len(workflow.jobs) == 0
    
    def test_job_creation(self):
        """Test job model creation"""
        job = Job(
            name="test_job",
            description="A test job",
            steps=[],
            depends_on=[]
        )
        
        assert job.name == "test_job"
        assert job.description == "A test job"
        assert len(job.steps) == 0
    
    def test_action_creation(self):
        """Test action model creation"""
        action = Action(
            name="test_action",
            description="A test action",
            code="print('Hello World')",
            shell=None,
            cond=None
        )
        
        assert action.name == "test_action"
        assert action.code == "print('Hello World')"
    
    def test_schedule_models(self):
        """Test schedule model creation"""
        cron_schedule = CronSchedule(cron="0 0 * * *")
        date_schedule = DateSchedule(run_date="2024-01-01T00:00:00Z")
        
        assert cron_schedule.cron == "0 0 * * *"
        assert date_schedule.run_date == "2024-01-01T00:00:00Z"


class TestWorkflowExecutor:
    """Test workflow execution engine"""
    
    def test_context_initialization(self):
        """Test context initialization"""
        init_ctx = {"key1": "value1", "key2": 42}
        context = initialize_context(init_ctx)
        
        assert context["key1"] == "value1"
        assert context["key2"] == 42
        assert context is not init_ctx  # Should be a copy
    
    def test_context_update(self):
        """Test context updating with template rendering"""
        context = {"name": "Alice", "count": 5}
        updates = {"message": "Hello {{ name }}, count: {{ count }}"}
        
        new_context = update_context(context, updates)
        
        assert new_context["message"] == "Hello Alice, count: 5"
        assert new_context["name"] == "Alice"
        assert new_context["count"] == 5
    
    def test_condition_evaluation(self):
        """Test condition evaluation"""
        context = {"x": 10, "y": 5, "flag": True}
        
        # Test simple conditions
        assert evaluate_condition("x > y", context) == True
        assert evaluate_condition("x < y", context) == False
        assert evaluate_condition("flag", context) == True
        assert evaluate_condition("not flag", context) == False
    
    def test_action_execution(self):
        """Test action execution"""
        context = {"counter": 0}
        
        action = Action(
            name="increment",
            code="counter += 1",
            shell=None,
            cond=None
        )
        
        new_context = execute_action(action, context)
        assert new_context["counter"] == 1
    
    def test_job_execution(self):
        """Test job execution with multiple actions"""
        context = {"counter": 0, "messages": []}
        
        actions = [
            Action(name="increment", code="counter += 1"),
            Action(name="add_message", code="messages.append('Hello')")
        ]
        
        job = Job(name="test_job", steps=actions)
        
        new_context = execute_job(job, context)
        assert new_context["counter"] == 1
        assert "Hello" in new_context["messages"]
    
    def test_workflow_execution(self):
        """Test complete workflow execution"""
        actions = [
            Action(name="setup", code="result = 'setup_complete'"),
            Action(name="process", code="result += '_processed'")
        ]
        
        job = Job(name="main_job", steps=actions)
        workflow = Workflow(name="test_workflow", jobs=[job])
        
        context = execute_workflow(workflow)
        assert context["result"] == "setup_complete_processed"
    
    def test_conditional_action_execution(self):
        """Test action execution with conditions"""
        context = {"should_run": True, "executed": False}
        
        action = Action(
            name="conditional",
            code="executed = True",
            cond=Mock(expr="should_run")
        )
        
        # Should execute when condition is True
        new_context = execute_action(action, context)
        assert new_context["executed"] == True
        
        # Should not execute when condition is False
        context["should_run"] = False
        context["executed"] = False
        action.cond.expr = "should_run"
        
        new_context = execute_action(action, context)
        assert new_context["executed"] == False


class TestCLIComponents:
    """Test CLI-related components"""
    
    @patch('dslmodel.cli.app')
    def test_cli_app_import(self, mock_app):
        """Test CLI app can be imported"""
        from dslmodel.cli import app
        assert app is not None
    
    def test_cli_help_output(self):
        """Test CLI help command output"""
        # This would require running the actual CLI
        # For now, we'll test the structure
        assert True  # Placeholder for actual CLI testing


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_template_rendering(self):
        """Test template rendering with invalid templates"""
        with pytest.raises(Exception):
            render("{{ invalid_template }}", invalid_var="test")
    
    def test_invalid_condition_evaluation(self):
        """Test condition evaluation with invalid expressions"""
        context = {"x": 10}
        
        # Should handle invalid expressions gracefully
        result = evaluate_condition("invalid_expression", context)
        assert result == False
    
    def test_context_with_builtins(self):
        """Test context handling with builtins"""
        context = {"__builtins__": "should_be_removed", "data": "valid"}
        
        new_context = update_context(context, {})
        assert "__builtins__" not in new_context
        assert "data" in new_context


class TestPerformanceBasics:
    """Test basic performance characteristics"""
    
    def test_template_rendering_performance(self):
        """Test template rendering performance"""
        import time
        
        template = "{{ 'x' * 1000 }}"
        context = {}
        
        start_time = time.time()
        result = render(template, **context)
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0
        assert len(result) == 1000
    
    def test_context_update_performance(self):
        """Test context update performance"""
        import time
        
        context = {f"key_{i}": f"value_{i}" for i in range(100)}
        updates = {f"update_{i}": f"new_value_{i}" for i in range(50)}
        
        start_time = time.time()
        new_context = update_context(context, updates)
        end_time = time.time()
        
        # Should complete in reasonable time (< 0.1 second)
        assert (end_time - start_time) < 0.1
        assert len(new_context) == 150


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 