"""
DSLModel Generated Models - Weaver First Approach
Auto-generated from semantic conventions - DO NOT EDIT MANUALLY
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class DSLModelBase(BaseModel):
    """Base class for all DSLModel generated models"""
    model_type: str = Field(..., description="Type of DSLModel")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        extra = "allow"
        validate_assignment = True


class CreateModel(DSLModelBase):
    """Create a new DSLModel instance
    
    Covers 40% of all DSLModel operations
    Generated from span: dslmodel.model.create
    """
    operation_type: str = Field(default="create", description="Operation type")
    name: Optional[str] = Field(..., description="Name of the model being created")
    validation_success: Optional[bool] = Field(None, description="Whether model validation passed")
    generation_duration_ms: Optional[int] = Field(None, description="Time taken to generate model in milliseconds")

    def start_span(self):
        """Start OpenTelemetry span for this operation"""
        return tracer.start_as_current_span(
            "dslmodel.model.create",
            attributes={
                "dslmodel.operation.type": self.operation_type,
                "dslmodel.model.type": self.model_type,
            }
        )
    
    def execute_with_telemetry(self, operation_func):
        """Execute operation with automatic telemetry"""
        with self.start_span() as span:
            try:
                result = operation_func(self)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

class ValidateModel(DSLModelBase):
    """Validate a DSLModel instance
    
    Covers 25% of all DSLModel operations
    Generated from span: dslmodel.model.validate
    """
    operation_type: str = Field(default="validate", description="Operation type")
    validation_rules_checked: Optional[int] = Field(None, description="Number of validation rules checked")
    validation_errors: Optional[int] = Field(None, description="Number of validation errors found")
    validation_success: Optional[bool] = Field(..., description="Overall validation result")

    def start_span(self):
        """Start OpenTelemetry span for this operation"""
        return tracer.start_as_current_span(
            "dslmodel.model.validate",
            attributes={
                "dslmodel.operation.type": self.operation_type,
                "dslmodel.model.type": self.model_type,
            }
        )
    
    def execute_with_telemetry(self, operation_func):
        """Execute operation with automatic telemetry"""
        with self.start_span() as span:
            try:
                result = operation_func(self)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

class ExecuteModel(DSLModelBase):
    """Execute an agent operation
    
    Covers 20% of all DSLModel operations - agent-specific
    Generated from span: dslmodel.agent.execute
    """
    operation_type: str = Field(default="execute", description="Operation type")
    agent_name: Optional[str] = Field(..., description="Name of the agent")
    agent_state: Optional[str] = Field(None, description="Current agent state")
    execution_success: Optional[bool] = Field(..., description="Whether agent execution succeeded")
    execution_duration_ms: Optional[int] = Field(None, description="Agent execution duration in milliseconds")

    def start_span(self):
        """Start OpenTelemetry span for this operation"""
        return tracer.start_as_current_span(
            "dslmodel.agent.execute",
            attributes={
                "dslmodel.operation.type": self.operation_type,
                "dslmodel.model.type": self.model_type,
            }
        )
    
    def execute_with_telemetry(self, operation_func):
        """Execute operation with automatic telemetry"""
        with self.start_span() as span:
            try:
                result = operation_func(self)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

class RunModel(DSLModelBase):
    """Run a workflow
    
    Covers 10% of all DSLModel operations - workflow-specific
    Generated from span: dslmodel.workflow.run
    """
    operation_type: str = Field(default="run", description="Operation type")
    workflow_name: Optional[str] = Field(..., description="Name of the workflow")
    workflow_steps_total: Optional[int] = Field(None, description="Total number of workflow steps")
    workflow_steps_completed: Optional[int] = Field(None, description="Number of completed steps")
    workflow_success: Optional[bool] = Field(..., description="Whether workflow completed successfully")

    def start_span(self):
        """Start OpenTelemetry span for this operation"""
        return tracer.start_as_current_span(
            "dslmodel.workflow.run",
            attributes={
                "dslmodel.operation.type": self.operation_type,
                "dslmodel.model.type": self.model_type,
            }
        )
    
    def execute_with_telemetry(self, operation_func):
        """Execute operation with automatic telemetry"""
        with self.start_span() as span:
            try:
                result = operation_func(self)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

class HealthModel(DSLModelBase):
    """System health check
    
    Covers 5% of operations but critical for monitoring
    Generated from span: dslmodel.system.health
    """
    operation_type: str = Field(default="health", description="Operation type")
    health_status: str = Field(..., description="Overall system health status")
    health_score: Optional[float] = Field(None, description="Health score from 0.0 to 1.0")
    active_models: Optional[int] = Field(None, description="Number of active models in the system")

    def start_span(self):
        """Start OpenTelemetry span for this operation"""
        return tracer.start_as_current_span(
            "dslmodel.system.health",
            attributes={
                "dslmodel.operation.type": self.operation_type,
                "dslmodel.model.type": self.model_type,
            }
        )
    
    def execute_with_telemetry(self, operation_func):
        """Execute operation with automatic telemetry"""
        with self.start_span() as span:
            try:
                result = operation_func(self)
                span.set_status(trace.Status(trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise


# Factory Functions - The 80% use cases made simple
def create_model(model_type: str, **kwargs) -> DSLModelBase:
    """Factory function to create models - covers 80% of use cases"""
    model_classes = {
        "create": CreateModel,
        "validate": ValidateModel, 
        "execute": ExecuteModel,
        "run": RunModel,
        "health": HealthModel
    }
    
    model_class = model_classes.get(model_type)
    if not model_class:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return model_class(model_type=model_type, **kwargs)

def create_agent(name: str, **kwargs) -> ExecuteModel:
    """Create agent model - most common use case"""
    return ExecuteModel(
        model_type="agent",
        agent_name=name,
        **kwargs
    )

def create_workflow(name: str, **kwargs) -> RunModel:
    """Create workflow model - second most common use case"""
    return RunModel(
        model_type="workflow", 
        workflow_name=name,
        **kwargs
    )
