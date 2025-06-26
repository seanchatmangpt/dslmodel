"""
Advanced Example: DSLModel + Weaver + FSM + Workflow Integration

This example shows the full power of combining:
- DSLModel's declarative model capabilities (Jinja2, DSPy, etc.)
- Weaver Forge for type-safe OTEL semantic conventions
- FSMMixin for state machine workflows
- DSLModel's Workflow system for orchestration
- OpenTelemetry for complete observability
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

from loguru import logger
from pydantic import Field, computed_field

# DSLModel imports
from dslmodel.workflow import Workflow, Job, Action
from dslmodel.dsl_models import DSLModel

# Integration imports
from dslmodel.otel.fsm_weaver_integration import (
    WeaverFSMModel,
    observable_trigger,
    ObservableFSMMixin
)

# OpenTelemetry setup (reuse from previous example)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


class DataPipelineState(str, Enum):
    """States for data processing pipeline."""
    INITIALIZED = "initialized"
    INGESTING = "ingesting"
    VALIDATING = "validating"
    TRANSFORMING = "transforming"
    ENRICHING = "enriching"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class DataQualityMetrics(DSLModel):
    """Nested model for data quality metrics."""
    total_records: int = Field(default=0, description="Total records processed")
    valid_records: int = Field(default=0, description="Records passing validation")
    error_records: int = Field(default=0, description="Records with errors")
    duplicate_records: int = Field(default=0, description="Duplicate records found")
    
    @computed_field
    @property
    def validity_rate(self) -> float:
        """Calculate data validity rate."""
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100
        
    @computed_field
    @property 
    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_records == 0:
            return 0.0
        return (self.error_records / self.total_records) * 100


class DataPipelineModel(WeaverFSMModel):
    """
    Advanced data pipeline model combining all DSLModel features.
    
    Features:
    - State machine for pipeline stages
    - Jinja2 templates for dynamic configuration
    - DSPy integration for AI-powered transformations
    - Full OpenTelemetry instrumentation
    - Workflow orchestration support
    """
    
    # Pipeline identification
    pipeline_id: str = Field(
        default="{{ 'PIPE-' + fake_lexify('????-????') }}",
        description="Unique pipeline identifier"
    )
    pipeline_name: str = Field(description="Human-readable pipeline name")
    
    # State machine
    state: DataPipelineState = Field(
        default=DataPipelineState.INITIALIZED,
        description="Current pipeline state"
    )
    
    # Configuration
    source_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data source configuration"
    )
    transform_rules: List[str] = Field(
        default_factory=list,
        description="Transformation rules to apply"
    )
    
    # Metrics and monitoring
    quality_metrics: DataQualityMetrics = Field(
        default_factory=DataQualityMetrics,
        description="Data quality metrics"
    )
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    # AI enhancement flag
    use_ai_enrichment: bool = Field(
        default=False,
        description="Whether to use AI for data enrichment"
    )
    
    def model_post_init(self, __context) -> None:
        """Initialize FSM and observability."""
        super().model_post_init(__context)
        
        # Setup FSM
        self.setup_fsm(DataPipelineState, initial=DataPipelineState.INITIALIZED)
        
        # Enhanced observability with pipeline context
        self.setup_observability(
            service_name=f"data-pipeline.{self.pipeline_name.lower().replace(' ', '-')}"
        )
        
    # State transitions with business logic
    
    @observable_trigger(source=DataPipelineState.INITIALIZED, dest=DataPipelineState.INGESTING)
    def start_ingestion(self, source_path: str) -> bool:
        """Start data ingestion from source."""
        logger.info(f"Starting ingestion for pipeline {self.pipeline_id}")
        
        self.start_time = datetime.now()
        self.source_config["path"] = source_path
        
        # Simulate reading data
        self.quality_metrics.total_records = 1000  # Mock data
        
        return True
        
    @observable_trigger(source=DataPipelineState.INGESTING, dest=DataPipelineState.VALIDATING)
    def validate_data(self) -> bool:
        """Validate ingested data."""
        logger.info(f"Validating {self.quality_metrics.total_records} records")
        
        # Simulate validation
        self.quality_metrics.valid_records = 950
        self.quality_metrics.error_records = 30
        self.quality_metrics.duplicate_records = 20
        
        if self.quality_metrics.validity_rate < 90:
            logger.warning(f"Low validity rate: {self.quality_metrics.validity_rate}%")
            
        return True
        
    @observable_trigger(source=DataPipelineState.VALIDATING, dest=DataPipelineState.TRANSFORMING)
    def transform_data(self) -> bool:
        """Apply transformation rules."""
        logger.info(f"Applying {len(self.transform_rules)} transformation rules")
        
        # Add OTEL span attributes for transform details
        if hasattr(self, '_tracer') and self._tracer:
            span = trace.get_current_span()
            span.set_attributes({
                "pipeline.transform.rules_count": len(self.transform_rules),
                "pipeline.transform.valid_records": self.quality_metrics.valid_records
            })
        
        return True
        
    @observable_trigger(
        source=DataPipelineState.TRANSFORMING,
        dest=DataPipelineState.ENRICHING,
        conditions=["should_enrich"]
    )
    def enrich_data(self) -> bool:
        """Enrich data using AI if enabled."""
        logger.info("Enriching data with AI")
        
        # Here we could use DSPy to enrich data
        if self.use_ai_enrichment:
            # Mock AI enrichment
            enriched_prompt = f"Enrich dataset {self.pipeline_name} with additional insights"
            logger.info(f"AI Prompt: {enriched_prompt}")
            
        return True
        
    @observable_trigger(
        source=[DataPipelineState.TRANSFORMING, DataPipelineState.ENRICHING],
        dest=DataPipelineState.STORING
    )
    def store_results(self, output_path: str) -> bool:
        """Store processed data."""
        logger.info(f"Storing results to {output_path}")
        
        # Record storage metrics
        if hasattr(self, '_meter') and self._meter:
            storage_counter = self._meter.create_counter(
                "pipeline.records.stored",
                description="Records successfully stored"
            )
            storage_counter.add(
                self.quality_metrics.valid_records,
                attributes={"pipeline": self.pipeline_name}
            )
            
        return True
        
    @observable_trigger(source=DataPipelineState.STORING, dest=DataPipelineState.COMPLETED)
    def complete_pipeline(self) -> bool:
        """Mark pipeline as completed."""
        self.end_time = datetime.now()
        
        duration = (self.end_time - self.start_time).total_seconds()
        logger.success(
            f"Pipeline {self.pipeline_id} completed in {duration:.2f}s. "
            f"Processed {self.quality_metrics.valid_records} valid records."
        )
        
        return True
        
    @observable_trigger(
        source=[
            DataPipelineState.INGESTING,
            DataPipelineState.VALIDATING, 
            DataPipelineState.TRANSFORMING,
            DataPipelineState.ENRICHING,
            DataPipelineState.STORING
        ],
        dest=DataPipelineState.RETRYING
    )
    def retry_stage(self, error: str) -> bool:
        """Retry current stage on error."""
        self.retry_count += 1
        logger.warning(f"Retrying pipeline stage (attempt {self.retry_count}): {error}")
        
        if self.retry_count > 3:
            return self.fail_pipeline("Max retries exceeded")
            
        return True
        
    @observable_trigger(source="*", dest=DataPipelineState.FAILED)
    def fail_pipeline(self, error: str) -> bool:
        """Mark pipeline as failed."""
        logger.error(f"Pipeline {self.pipeline_id} failed: {error}")
        
        if hasattr(self, '_tracer') and self._tracer:
            span = trace.get_current_span()
            span.set_status(Status(StatusCode.ERROR, error))
            
        return True
        
    # Condition methods
    def should_enrich(self) -> bool:
        """Check if enrichment should be performed."""
        return self.use_ai_enrichment
        
    # Workflow integration methods
    def to_workflow_action(self) -> Action:
        """Convert pipeline to workflow action."""
        return Action(
            name=f"pipeline_{self.pipeline_name.lower().replace(' ', '_')}",
            module="data_pipeline",
            method="execute",
            parameters={
                "pipeline_id": self.pipeline_id,
                "source_config": self.source_config,
                "transform_rules": self.transform_rules,
                "use_ai_enrichment": self.use_ai_enrichment
            }
        )


class DataPipelineOrchestrator(DSLModel):
    """
    Orchestrates multiple data pipelines using DSLModel's Workflow system.
    """
    
    workflow_name: str = Field(description="Orchestration workflow name")
    pipelines: List[DataPipelineModel] = Field(
        default_factory=list,
        description="Pipelines to orchestrate"
    )
    parallel_execution: bool = Field(
        default=True,
        description="Execute pipelines in parallel"
    )
    
    def create_workflow(self) -> Workflow:
        """Create a workflow from configured pipelines."""
        jobs = []
        
        for i, pipeline in enumerate(self.pipelines):
            # Create job for each pipeline
            job = Job(
                name=f"job_{pipeline.pipeline_name.lower().replace(' ', '_')}",
                actions=[pipeline.to_workflow_action()],
                depends_on=[] if self.parallel_execution else [f"job_{i-1}"] if i > 0 else []
            )
            jobs.append(job)
            
        workflow = Workflow(
            name=self.workflow_name,
            jobs=jobs,
            on_failure="continue"  # Continue other pipelines even if one fails
        )
        
        return workflow
        
    @classmethod
    def from_config(cls, config_path: Path) -> "DataPipelineOrchestrator":
        """Create orchestrator from YAML configuration."""
        return cls.from_yaml(str(config_path))


async def run_pipeline_example():
    """Example: Run a single observable data pipeline."""
    
    # Create pipeline
    pipeline = DataPipelineModel(
        pipeline_name="Customer Analytics Pipeline",
        transform_rules=[
            "normalize_dates",
            "clean_phone_numbers", 
            "standardize_addresses"
        ],
        use_ai_enrichment=True
    )
    
    logger.info(f"Created pipeline: {pipeline.pipeline_id}")
    
    # Execute pipeline stages
    try:
        pipeline.start_ingestion("/data/customers.csv")
        await asyncio.sleep(0.1)
        
        pipeline.validate_data()
        logger.info(f"Data quality: {pipeline.quality_metrics.validity_rate:.1f}% valid")
        
        pipeline.transform_data()
        await asyncio.sleep(0.1)
        
        if pipeline.should_enrich():
            pipeline.enrich_data()
            
        pipeline.store_results("/data/processed/customers_clean.parquet")
        pipeline.complete_pipeline()
        
    except Exception as e:
        pipeline.fail_pipeline(str(e))
        
    # Export pipeline state
    logger.info("\nFinal pipeline state:")
    print(pipeline.model_dump_json(indent=2))
    
    return pipeline


async def run_orchestration_example():
    """Example: Orchestrate multiple pipelines with workflow."""
    
    # Create multiple pipelines
    pipelines = [
        DataPipelineModel(
            pipeline_name="Sales Data Pipeline",
            transform_rules=["aggregate_daily", "calculate_metrics"],
            use_ai_enrichment=False
        ),
        DataPipelineModel(
            pipeline_name="Customer Feedback Pipeline",
            transform_rules=["sentiment_analysis", "categorize_issues"],
            use_ai_enrichment=True
        ),
        DataPipelineModel(
            pipeline_name="Product Inventory Pipeline",
            transform_rules=["update_stock_levels", "predict_demand"],
            use_ai_enrichment=True
        )
    ]
    
    # Create orchestrator
    orchestrator = DataPipelineOrchestrator(
        workflow_name="Daily Analytics Workflow",
        pipelines=pipelines,
        parallel_execution=True
    )
    
    # Generate workflow
    workflow = orchestrator.create_workflow()
    
    # Save workflow configuration
    workflow_path = Path("/tmp/analytics_workflow.yaml")
    workflow.to_yaml(str(workflow_path))
    logger.info(f"Saved workflow to {workflow_path}")
    
    # Show workflow structure
    logger.info("\nGenerated Workflow Structure:")
    print(workflow.model_dump_json(indent=2))
    
    return orchestrator


async def main():
    """Run all examples."""
    logger.info("=== DSLModel + Weaver + FSM Integration Demo ===\n")
    
    # Single pipeline example
    logger.info("1. Running single pipeline example...")
    await run_pipeline_example()
    
    # Orchestration example  
    logger.info("\n2. Running orchestration example...")
    await run_orchestration_example()
    
    logger.info("\nIntegration demo complete!")


if __name__ == "__main__":
    asyncio.run(main())