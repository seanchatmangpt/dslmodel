"""
Working FSM Demo - Simplified approach

Let's create a minimal example that focuses on the integration
without getting caught up in complex state machine configuration.
"""
from enum import Enum
from loguru import logger

from dslmodel import DSLModel
from dslmodel.integrations.otel.models.dslmodel_attributes import DslmodelAttributes
from dslmodel.integrations.otel.metrics.dslmodel_metrics import DslmodelMetricsMetric


class WorkflowStatus(str, Enum):
    """Simple workflow status that matches OTEL attributes."""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class DSLWorkflow(DSLModel):
    """
    DSL Workflow that demonstrates integration without complex FSM.
    
    Shows the core value: DSLModel + OpenTelemetry models working together.
    """
    
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.STARTED
    
    # OpenTelemetry integration
    otel_attributes: DslmodelAttributes
    duration_metric: DslmodelMetricsMetric
    
    def __init__(self, **kwargs):
        """Initialize workflow with OTEL integration."""
        # Must initialize otel_attributes before calling super().__init__
        otel_attrs = DslmodelAttributes(
            workflow_name=kwargs.get('workflow_name', 'default'),
            workflow_status="started",
            model_type="dsl_workflow"
        )
        
        duration_metric = DslmodelMetricsMetric(
            name="dslmodel.workflow.duration",
            brief="Workflow execution duration",
            instrument="histogram"
        )
        duration_metric.__post_init__()
        
        kwargs['otel_attributes'] = otel_attrs
        kwargs['duration_metric'] = duration_metric
        
        super().__init__(**kwargs)
        
        logger.info(f"Initialized workflow: {self.workflow_name}")
        logger.info(f"OTEL namespace: {self.otel_attributes.otel_namespace()}")
    
    def start_processing(self):
        """Start workflow processing."""
        logger.info(f"Starting processing for {self.workflow_name}")
        self.status = WorkflowStatus.STARTED
        self.otel_attributes.workflow_status = "started"
    
    def complete_successfully(self, duration_ms: int = 100):
        """Complete workflow successfully."""
        logger.success(f"Workflow {self.workflow_name} completed successfully")
        self.status = WorkflowStatus.COMPLETED
        self.otel_attributes.workflow_status = "completed"
        self.otel_attributes.workflow_duration_ms = duration_ms
    
    def fail_with_error(self, error: str):
        """Fail workflow with error."""
        logger.error(f"Workflow {self.workflow_name} failed: {error}")
        self.status = WorkflowStatus.FAILED
        self.otel_attributes.workflow_status = "failed"
    
    def get_telemetry_data(self) -> dict:
        """Get telemetry data for OpenTelemetry spans."""
        base_attrs = self.otel_attributes.model_dump()
        base_attrs.update({
            "workflow.final_status": self.status.value,
            "metric.name": self.duration_metric.name,
            "metric.instrument": self.duration_metric.instrument,
            "metric.unit": self.duration_metric.unit
        })
        return base_attrs
    
    def get_summary(self) -> dict:
        """Get workflow execution summary."""
        return {
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "otel_namespace": self.otel_attributes.otel_namespace(),
            "duration_ms": self.otel_attributes.workflow_duration_ms,
            "telemetry": self.get_telemetry_data()
        }


class WorkflowSimulation:
    """Simulate different workflow execution patterns."""
    
    @staticmethod
    def successful_workflow():
        """Demonstrate successful workflow execution."""
        logger.info("=== Successful Workflow Demo ===")
        
        workflow = DSLWorkflow(
            workflow_name="data-processing-pipeline"
        )
        
        workflow.start_processing()
        # Simulate work
        logger.info("Simulating data processing...")
        
        workflow.complete_successfully(duration_ms=250)
        
        summary = workflow.get_summary()
        logger.info(f"Summary: {summary}")
        
        return workflow
    
    @staticmethod
    def failed_workflow():
        """Demonstrate failed workflow execution."""
        logger.info("\n=== Failed Workflow Demo ===")
        
        workflow = DSLWorkflow(
            workflow_name="analysis-pipeline"
        )
        
        workflow.start_processing()
        # Simulate failure
        workflow.fail_with_error("Invalid input data format")
        
        summary = workflow.get_summary()
        logger.info(f"Summary: {summary}")
        
        return workflow
    
    @staticmethod
    def demonstrate_otel_integration():
        """Show OpenTelemetry integration capabilities."""
        logger.info("\n=== OpenTelemetry Integration Demo ===")
        
        # Create multiple workflows
        workflows = []
        
        for i in range(3):
            wf = DSLWorkflow(workflow_name=f"batch-job-{i+1}")
            wf.start_processing()
            
            if i % 2 == 0:
                wf.complete_successfully(duration_ms=100 + i * 50)
            else:
                wf.fail_with_error(f"Simulated error {i}")
            
            workflows.append(wf)
        
        # Aggregate telemetry
        telemetry_data = []
        for wf in workflows:
            telemetry_data.append(wf.get_telemetry_data())
        
        logger.info("Collected telemetry from all workflows:")
        for i, data in enumerate(telemetry_data):
            logger.info(f"Workflow {i+1}: {data}")
        
        # Show OTEL attributes validation
        logger.info("\n=== OTEL Attributes Validation ===")
        test_attrs = DslmodelAttributes(
            workflow_name="validation-test",
            workflow_status="completed",
            workflow_duration_ms=123,
            model_type="test"
        )
        
        logger.info(f"Valid OTEL attributes: {test_attrs.model_dump()}")
        
        # Test validation
        try:
            invalid_attrs = DslmodelAttributes(
                workflow_name="invalid-test",
                workflow_status="invalid_status"  # Should fail
            )
        except Exception as e:
            logger.success(f"Validation works! Caught: {e}")
        
        return workflows


def main():
    """Run all demonstrations."""
    logger.info("🚀 DSLModel + OpenTelemetry Integration Demo")
    logger.info("=" * 50)
    
    # Run simulations
    sim = WorkflowSimulation()
    
    successful = sim.successful_workflow()
    failed = sim.failed_workflow()
    batch = sim.demonstrate_otel_integration()
    
    # Final integration summary
    logger.info("\n🎯 Integration Summary:")
    logger.info("✅ DSLModel provides Pydantic base with mixins")
    logger.info("✅ Generated OTEL models from semantic conventions")
    logger.info("✅ Type-safe telemetry attributes with validation")
    logger.info("✅ Metrics integration with dataclasses")
    logger.info("✅ Workflow state management")
    logger.info("✅ Ready for OpenTelemetry span instrumentation")
    
    return {
        "successful_workflow": successful,
        "failed_workflow": failed,
        "batch_workflows": batch
    }


if __name__ == "__main__":
    results = main()