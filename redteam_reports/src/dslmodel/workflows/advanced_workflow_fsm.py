"""
Advanced Workflow with FSMMixin Features

Demonstrates:
- Conditional transitions
- Loops and retries
- AI-powered decision making via forward()
- Complex state machine patterns
"""
from enum import Enum
from typing import Optional, Dict, Any, List
import random
from loguru import logger

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger
from dslmodel.integrations.otel.models.dslmodel_attributes import DslmodelAttributes


class AdvancedWorkflowState(str, Enum):
    """Advanced workflow states with retry and validation loops."""
    IDLE = "idle"
    VALIDATING = "validating"
    PROCESSING = "processing"
    REVIEWING = "reviewing"
    RETRYING = "retrying"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"


class AdvancedWorkflowFSM(DSLModel, FSMMixin):
    """
    Advanced workflow demonstrating full FSMMixin capabilities.
    
    Features:
    - Conditional transitions based on validation results
    - Retry loops with backoff
    - AI-powered optimization decisions
    - Complex state patterns
    """
    
    # Workflow config
    workflow_name: str
    max_retries: int = 3
    enable_optimization: bool = True
    
    # State
    state: AdvancedWorkflowState = AdvancedWorkflowState.IDLE
    
    # Runtime data
    validation_score: float = 0.0
    retry_count: int = 0
    processing_results: Dict[str, Any] = {}
    optimization_applied: bool = False
    
    # OTEL integration
    otel_attributes: Optional[DslmodelAttributes] = None
    
    def __init__(self, **kwargs):
        """Initialize advanced workflow FSM."""
        super().__init__(**kwargs)
        
        # Setup complex state machine
        self.setup_fsm(
            state_enum=AdvancedWorkflowState,
            initial=AdvancedWorkflowState.IDLE.value
        )
        
        # Add conditional transitions
        self._setup_conditional_transitions()
        
        self.otel_attributes = DslmodelAttributes(
            workflow_name=self.workflow_name,
            workflow_status="started",
            model_type="advanced_fsm"
        )
    
    def _setup_conditional_transitions(self):
        """Set up transitions with conditions programmatically."""
        # Add validation loop
        self.add_transition(
            trigger="retry_validation",
            source=AdvancedWorkflowState.VALIDATING,
            dest=AdvancedWorkflowState.VALIDATING,
            conditions=["can_retry"],
            after="increment_retry"
        )
        
        # Add optimization bypass
        self.add_transition(
            trigger="skip_optimization",
            source=AdvancedWorkflowState.REVIEWING,
            dest=AdvancedWorkflowState.COMPLETED,
            unless=["should_optimize"]
        )
    
    # Condition methods
    
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.validation_score >= 0.8
    
    def can_retry(self) -> bool:
        """Check if retries are available."""
        return self.retry_count < self.max_retries
    
    def should_optimize(self) -> bool:
        """Determine if optimization is needed."""
        if not self.enable_optimization:
            return False
        
        # Use AI to decide
        decision = self.forward(
            prompt="Should we optimize this workflow?",
            context={
                "validation_score": self.validation_score,
                "processing_results": self.processing_results,
                "retry_count": self.retry_count
            }
        )
        
        return "yes" in decision.lower() or "optimize" in decision.lower()
    
    # State transitions
    
    @trigger(
        source=AdvancedWorkflowState.IDLE,
        dest=AdvancedWorkflowState.VALIDATING
    )
    def start_validation(self):
        """Begin workflow validation."""
        logger.info(f"Starting validation for {self.workflow_name}")
        self.retry_count = 0
    
    @trigger(
        source=AdvancedWorkflowState.VALIDATING,
        dest=AdvancedWorkflowState.PROCESSING,
        conditions=["is_valid"]
    )
    def proceed_to_processing(self):
        """Move to processing after successful validation."""
        logger.success(f"Validation passed with score: {self.validation_score}")
        self.otel_attributes.workflow_status = "started"
    
    @trigger(
        source=AdvancedWorkflowState.VALIDATING,
        dest=AdvancedWorkflowState.RETRYING,
        unless=["is_valid"],
        conditions=["can_retry"]
    )
    def retry_after_validation_failure(self):
        """Retry validation after failure."""
        logger.warning(f"Validation failed, retry {self.retry_count + 1}/{self.max_retries}")
    
    @trigger(
        source=AdvancedWorkflowState.RETRYING,
        dest=AdvancedWorkflowState.VALIDATING,
        after="increment_retry"
    )
    def retry_validation_attempt(self):
        """Return to validation for retry."""
        logger.info("Retrying validation...")
    
    def increment_retry(self):
        """Increment retry counter."""
        self.retry_count += 1
    
    @trigger(
        source=AdvancedWorkflowState.VALIDATING,
        dest=AdvancedWorkflowState.FAILED,
        unless=["is_valid", "can_retry"]
    )
    def fail_after_max_retries(self):
        """Fail workflow after exhausting retries."""
        logger.error(f"Validation failed after {self.retry_count} retries")
        self.otel_attributes.workflow_status = "failed"
    
    @trigger(
        source=AdvancedWorkflowState.PROCESSING,
        dest=AdvancedWorkflowState.REVIEWING,
        after="analyze_results"
    )
    def complete_processing(self):
        """Complete processing phase."""
        logger.info("Processing completed, moving to review")
    
    def analyze_results(self):
        """Analyze processing results."""
        self.processing_results = {
            "items_processed": random.randint(50, 200),
            "success_rate": random.uniform(0.7, 0.99),
            "performance_score": random.uniform(0.6, 0.95)
        }
        logger.info(f"Processing results: {self.processing_results}")
    
    @trigger(
        source=AdvancedWorkflowState.REVIEWING,
        dest=AdvancedWorkflowState.OPTIMIZING,
        conditions=["should_optimize"]
    )
    def proceed_to_optimization(self):
        """Move to optimization phase if needed."""
        logger.info("Optimization required, proceeding...")
    
    @trigger(
        source=AdvancedWorkflowState.OPTIMIZING,
        dest=AdvancedWorkflowState.COMPLETED,
        after="apply_optimizations"
    )
    def complete_with_optimization(self):
        """Complete workflow after optimization."""
        logger.success("Workflow completed with optimizations")
        self.otel_attributes.workflow_status = "completed"
    
    def apply_optimizations(self):
        """Apply AI-driven optimizations."""
        optimization_plan = self.forward(
            prompt="Generate optimization plan",
            context=self.processing_results
        )
        
        logger.info(f"Applied optimizations: {optimization_plan}")
        self.optimization_applied = True
    
    @trigger(
        source=AdvancedWorkflowState.REVIEWING,
        dest=AdvancedWorkflowState.COMPLETED,
        unless=["should_optimize"]
    )
    def complete_without_optimization(self):
        """Complete workflow without optimization."""
        logger.success("Workflow completed (optimization skipped)")
        self.otel_attributes.workflow_status = "completed"
    
    # Workflow execution methods
    
    def execute(self) -> Dict[str, Any]:
        """Execute the full workflow with automatic transitions."""
        logger.info(f"=== Executing Advanced Workflow: {self.workflow_name} ===")
        
        # Start validation
        self.start_validation()
        
        # Simulate validation attempts
        while self.state == AdvancedWorkflowState.VALIDATING:
            self.validation_score = random.uniform(0.5, 1.0)
            logger.info(f"Validation score: {self.validation_score}")
            
            if self.is_valid():
                self.proceed_to_processing()
            elif self.can_retry():
                self.retry_after_validation_failure()
                self.retry_validation_attempt()
            else:
                self.fail_after_max_retries()
                break
        
        # Continue if not failed
        if self.state == AdvancedWorkflowState.PROCESSING:
            self.complete_processing()
            
            # Review phase with AI decision
            if self.should_optimize():
                self.proceed_to_optimization()
                self.complete_with_optimization()
            else:
                self.complete_without_optimization()
        
        # Return final state
        return {
            "final_state": self.state.value,
            "validation_score": self.validation_score,
            "retry_count": self.retry_count,
            "processing_results": self.processing_results,
            "optimization_applied": self.optimization_applied,
            "otel_status": self.otel_attributes.workflow_status if self.otel_attributes else None
        }
    
    def visualize_state_machine(self) -> str:
        """Generate a text representation of possible transitions."""
        transitions = []
        
        for state in AdvancedWorkflowState:
            possible = self.possible_triggers(state.value)
            if possible:
                transitions.append(f"{state.value}: {', '.join(possible)}")
        
        return "\n".join(transitions)


def demonstrate_advanced_fsm():
    """Demonstrate advanced FSM features."""
    
    # Create workflow with optimization enabled
    workflow = AdvancedWorkflowFSM(
        workflow_name="advanced-fsm-demo",
        max_retries=3,
        enable_optimization=True
    )
    
    logger.info("State machine transitions:")
    logger.info(workflow.visualize_state_machine())
    
    # Execute workflow
    result = workflow.execute()
    
    logger.info(f"\nFinal result: {result}")
    
    # Show FSM introspection
    logger.info(f"\nFinal state: {workflow.state}")
    logger.info(f"State machine states: {[s.value for s in AdvancedWorkflowState]}")
    logger.info(f"Possible triggers from final state: {workflow.possible_triggers()}")
    
    return workflow


if __name__ == "__main__":
    demonstrate_advanced_fsm()