"""
Workflow Orchestrator with OpenTelemetry Integration

This module demonstrates the integration of:
1. DSLModel - Base model with all mixins
2. Generated OpenTelemetry models from Weaver
3. FSMMixin - State machine capabilities
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
import time
from loguru import logger

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger
from dslmodel.integrations.otel.models.dslmodel_attributes import DslmodelAttributes
from dslmodel.integrations.otel.metrics.dslmodel_metrics import DslmodelMetricsMetric


class WorkflowState(str, Enum):
    """Workflow execution states aligned with OTEL attributes."""
    INITIALIZED = "initialized"
    STARTED = "started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowOrchestrator(DSLModel, FSMMixin):
    """
    Orchestrates DSL workflow execution with OpenTelemetry instrumentation.
    
    Combines:
    - DSLModel capabilities (file handling, templates, DSPy)
    - OpenTelemetry semantic conventions
    - State machine behavior via FSMMixin
    """
    
    # Workflow metadata
    workflow_name: str
    workflow_type: str = "dsl_orchestration"
    
    # State machine
    state: WorkflowState = WorkflowState.INITIALIZED
    
    # OpenTelemetry attributes (composition)
    otel_attributes: Optional[DslmodelAttributes] = None
    
    # Workflow context
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    steps_completed: List[str] = []
    
    # Metrics
    duration_metric: Optional[DslmodelMetricsMetric] = None
    
    def __init__(self, **kwargs):
        """Initialize workflow with OTEL attributes."""
        super().__init__(**kwargs)
        
        # Set up state machine
        self.setup_fsm(
            state_enum=WorkflowState,
            initial=WorkflowState.INITIALIZED.value
        )
        
        # Initialize OTEL attributes
        self.otel_attributes = DslmodelAttributes(
            workflow_name=self.workflow_name,
            workflow_status="started",
            model_type="workflow_orchestrator"
        )
        
        # Initialize metrics
        self.duration_metric = DslmodelMetricsMetric(
            name="dslmodel.workflow.duration",
            brief="Workflow execution duration",
            instrument="histogram"
        )
        self.duration_metric.__post_init__()
        
        logger.info(f"Initialized workflow: {self.workflow_name}")
    
    # State transitions with @trigger decorator
    
    @trigger(
        source=WorkflowState.INITIALIZED.value,
        dest=WorkflowState.STARTED.value,
        after="record_start"
    )
    def start_workflow(self):
        """Start the workflow execution."""
        logger.info(f"Starting workflow: {self.workflow_name}")
        self.otel_attributes.workflow_status = "started"
    
    def record_start(self):
        """Record workflow start time."""
        self.start_time = time.time()
        logger.debug(f"Workflow started at: {self.start_time}")
    
    @trigger(
        source=WorkflowState.STARTED.value,
        dest=WorkflowState.PROCESSING.value,
        after="execute_steps"
    )
    def begin_processing(self):
        """Transition to processing state."""
        logger.info("Beginning workflow processing")
    
    def execute_steps(self):
        """Execute workflow steps (simplified for demo)."""
        steps = ["validate_input", "transform_data", "generate_output"]
        
        for step in steps:
            logger.info(f"Executing step: {step}")
            time.sleep(0.1)  # Simulate work
            self.steps_completed.append(step)
            
            # Update OTEL attributes with progress
            if self.otel_attributes.workflow_duration_ms is None:
                elapsed = (time.time() - self.start_time) * 1000
                self.otel_attributes.workflow_duration_ms = int(elapsed)
    
    @trigger(
        source=WorkflowState.PROCESSING.value,
        dest=WorkflowState.COMPLETED.value,
        after="record_completion"
    )
    def complete_workflow(self):
        """Complete the workflow successfully."""
        logger.success(f"Workflow completed: {self.workflow_name}")
        self.otel_attributes.workflow_status = "completed"
    
    def record_completion(self):
        """Record workflow completion and metrics."""
        self.end_time = time.time()
        duration_ms = int((self.end_time - self.start_time) * 1000)
        
        # Update OTEL attributes
        self.otel_attributes.workflow_duration_ms = duration_ms
        
        logger.info(f"Workflow duration: {duration_ms}ms")
        logger.info(f"Steps completed: {len(self.steps_completed)}")
    
    @trigger(
        source=[WorkflowState.STARTED.value, WorkflowState.PROCESSING.value],
        dest=WorkflowState.FAILED.value,
        after="record_failure"
    )
    def fail_workflow(self, error: str):
        """Fail the workflow with error."""
        logger.error(f"Workflow failed: {error}")
        self.error_message = error
        self.otel_attributes.workflow_status = "failed"
    
    def record_failure(self):
        """Record failure metrics."""
        if self.start_time:
            self.end_time = time.time()
            duration_ms = int((self.end_time - self.start_time) * 1000)
            self.otel_attributes.workflow_duration_ms = duration_ms
    
    @trigger(
        source=[WorkflowState.STARTED.value, WorkflowState.PROCESSING.value],
        dest=WorkflowState.CANCELLED.value,
        after="cleanup_resources"
    )
    def cancel_workflow(self):
        """Cancel the workflow execution."""
        logger.warning(f"Workflow cancelled: {self.workflow_name}")
    
    def cleanup_resources(self):
        """Clean up any resources on cancellation."""
        logger.info("Cleaning up workflow resources")
    
    # Utility methods
    
    def get_telemetry_attributes(self) -> Dict[str, Any]:
        """Get OpenTelemetry attributes for spans."""
        if not self.otel_attributes:
            return {}
        
        attrs = self.otel_attributes.model_dump()
        attrs["workflow.state"] = self.state.value
        attrs["workflow.steps_completed"] = len(self.steps_completed)
        
        return attrs
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary."""
        return {
            "workflow_name": self.workflow_name,
            "state": self.state.value,
            "duration_ms": self.otel_attributes.workflow_duration_ms if self.otel_attributes else None,
            "steps_completed": self.steps_completed,
            "error": self.error_message,
            "possible_transitions": self.possible_transitions(),
            "telemetry": self.get_telemetry_attributes()
        }
    
    # FSMMixin AI-powered transition
    
    def decide_next_action(self) -> str:
        """Use AI to decide next workflow action."""
        context = {
            "current_state": self.state.value,
            "steps_completed": self.steps_completed,
            "has_error": bool(self.error_message),
            "duration_so_far": (time.time() - self.start_time) * 1000 if self.start_time else 0
        }
        
        # Use FSMMixin's forward() method for AI decision
        return self.forward(
            prompt=f"Decide next action for workflow in state {self.state.value}",
            context=context
        )


# Example usage function
def demonstrate_workflow():
    """Demonstrate the WorkflowOrchestrator with state transitions."""
    
    # Create workflow
    workflow = WorkflowOrchestrator(
        workflow_name="example-dsl-pipeline"
    )
    
    logger.info("=== Workflow Orchestration Demo ===")
    logger.info(f"Initial state: {workflow.state}")
    logger.info(f"Possible transitions: {workflow.possible_transitions()}")
    
    # Execute workflow
    try:
        # Start
        workflow.start_workflow()
        logger.info(f"After start - State: {workflow.state}")
        
        # Process
        workflow.begin_processing()
        logger.info(f"After processing - State: {workflow.state}")
        
        # Complete
        workflow.complete_workflow()
        logger.info(f"Final state: {workflow.state}")
        
        # Show summary
        summary = workflow.get_workflow_summary()
        logger.info(f"Workflow summary: {summary}")
        
        # Show OTEL integration
        logger.info(f"OTEL namespace: {workflow.otel_attributes.otel_namespace()}")
        logger.info(f"Telemetry attributes: {workflow.get_telemetry_attributes()}")
        
    except Exception as e:
        workflow.fail_workflow(str(e))
        logger.error(f"Workflow failed: {e}")
    
    return workflow


if __name__ == "__main__":
    workflow = demonstrate_workflow()