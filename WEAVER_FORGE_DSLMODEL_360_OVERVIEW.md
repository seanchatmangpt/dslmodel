# Weaver Forge and DSLModel Integration: 360-Degree Overview

## Executive Summary

The integration of OpenTelemetry Weaver Forge with DSLModel creates a powerful framework for building observable, type-safe, AI-enhanced workflows. This integration combines:

- **Weaver Forge**: Generates strongly-typed Pydantic models from OpenTelemetry semantic conventions
- **DSLModel**: Provides declarative model capabilities with Jinja2 templates, DSPy AI integration, and file handling
- **FSMMixin**: Enables finite state machine workflows with automatic state transitions
- **OpenTelemetry**: Delivers comprehensive observability with spans, metrics, and traces

The result is a production-ready system that enforces type safety while providing complete visibility into workflow execution.

## 1. Architecture Overview

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Semantic Conventions Layer                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ OTEL Semantic   │    │ Custom Domain   │    │ Workflow State  │ │
│  │ Conventions     │    │ Conventions     │    │ Definitions     │ │
│  │ (YAML)          │    │ (YAML)          │    │ (YAML)          │ │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘ │
└───────────┼──────────────────────┼──────────────────────┼──────────┘
            │                      │                      │
            ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Weaver Forge Engine                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Template Engine │    │ Code Generator  │    │ Type System     │ │
│  │ (Jinja2)       │    │                 │    │ Validator       │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Generated Model Layer                            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ Type-Safe       │    │ Observable FSM  │    │ Workflow        │ │
│  │ Pydantic Models │    │ Models          │    │ Models          │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DSLModel Integration                           │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ DSLModel Base   │    │ FSMMixin State  │    │ AI/DSPy         │ │
│  │ (Templates,     │ +  │ Machine         │ +  │ Integration     │ │
│  │ I/O, Utils)     │    │                 │    │                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Observability Layer                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │ OTEL Traces     │    │ OTEL Metrics    │    │ Health/Status   │ │
│  │ (Spans)         │    │ (Counters,      │    │ Monitoring      │ │
│  │                 │    │ Histograms)     │    │                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Integration Points

1. **Semantic Convention → Model Generation**
   - YAML semantic conventions define attributes, metrics, and constraints
   - Weaver Forge processes these through Jinja2 templates
   - Generated models inherit from `WeaverFSMModel` base class

2. **FSM Integration**
   - `ObservableFSMMixin` wraps state transitions with OTEL spans
   - `@observable_trigger` decorator provides automatic instrumentation
   - State machines become fully observable workflows

3. **DSLModel Features**
   - Jinja2 templating for dynamic field generation
   - DSPy integration for AI-powered decisions
   - Built-in serialization, validation, and file I/O

4. **Workflow Orchestration**
   - FSM models can be composed into complex workflows
   - Parallel and sequential execution patterns
   - Full observability across workflow stages

## 2. Complete Workflow: From Conventions to Code

### Step 1: Define Semantic Conventions

```yaml
# semconv_registry/workflows/order_processing.yaml
groups:
  - id: order_workflow
    prefix: order
    type: attribute_group
    brief: 'Order processing workflow attributes'
    attributes:
      - id: state
        type:
          allow_custom_values: false
          members:
            - id: pending
              value: 'pending'
            - id: validated
              value: 'validated'
            - id: payment_processing
              value: 'payment_processing'
            - id: shipped
              value: 'shipped'
            - id: delivered
              value: 'delivered'
        requirement_level: required
        brief: 'Current order state'
      
      - id: order_id
        type: string
        requirement_level: required
        brief: 'Unique order identifier'
        
      - id: total_amount
        type: double
        requirement_level: required
        brief: 'Total order amount in USD'
        
      - id: customer_id
        type: string
        requirement_level: required
        brief: 'Customer identifier'

  - id: order.metrics
    type: metric
    metric_name: order.processing.duration
    brief: 'Measures order processing duration'
    instrument: histogram
    unit: 'ms'
    attributes:
      - ref: order.state
      - ref: order.customer_id
```

### Step 2: Configure Weaver Templates

```jinja2
{# weaver_templates/registry/python/fsm_pydantic_model.j2 #}
"""
Generated {{ group.id }} FSM Model
{{ group.brief }}
"""
from typing import Optional
from enum import Enum
from pydantic import Field

from dslmodel.integrations.otel.fsm_weaver_integration import WeaverFSMModel, observable_trigger


class {{ group.id | pascal_case }}State(str, Enum):
    """States for {{ group.id }} workflow."""
    {%- for member in group.attributes[0].type.members %}
    {{ member.id | upper }} = "{{ member.value }}"
    {%- endfor %}


class {{ group.id | pascal_case }}Model(WeaverFSMModel):
    """
    {{ group.brief }}
    
    Features:
    - Type-safe fields with validation
    - FSM state machine capabilities
    - Automatic OTEL instrumentation
    - AI-powered decision making
    """
    
    {%- for attr in group.attributes %}
    {{ attr.id }}: {{ attr.type | python_type }} = Field(
        {%- if attr.default %}default={{ attr.default }},{% endif %}
        description="{{ attr.brief }}"
    )
    {%- endfor %}
    
    def model_post_init(self, __context) -> None:
        """Initialize FSM and observability."""
        super().model_post_init(__context)
        
        # Setup FSM with workflow states
        self.setup_fsm(
            {{ group.id | pascal_case }}State, 
            initial={{ group.id | pascal_case }}State.{{ group.attributes[0].type.members[0].id | upper }}
        )
        
        # Setup observability
        self.setup_observability(service_name="{{ group.id }}")
```

### Step 3: Generate Models

```python
# src/dslmodel/integrations/otel/weaver_integration.py
from dslmodel.integrations.otel.weaver_integration import WeaverForgeIntegration

# Initialize integration
weaver = WeaverForgeIntegration()

# Generate models from semantic conventions
success = weaver.generate_models(
    semconv_path="semconv_registry/workflows",
    target="python",
    output_dir="src/dslmodel/generated"
)
```

### Step 4: Implement Business Logic

```python
# src/dslmodel/workflows/order_processor.py
from dslmodel.generated.order_workflow_model import (
    OrderWorkflowModel, 
    OrderWorkflowState
)

class OrderProcessor(OrderWorkflowModel):
    """Enhanced order processor with business logic."""
    
    # Additional fields
    payment_verified: bool = Field(default=False)
    inventory_reserved: bool = Field(default=False)
    
    @observable_trigger(
        source=OrderWorkflowState.PENDING, 
        dest=OrderWorkflowState.VALIDATED
    )
    def validate_order(self) -> bool:
        """Validate order with automatic span creation."""
        if self.total_amount <= 0:
            raise ValueError("Invalid order amount")
            
        # AI-powered fraud detection
        risk_assessment = self.forward(
            f"Assess fraud risk for order {self.order_id} "
            f"from customer {self.customer_id} "
            f"with amount ${self.total_amount}"
        )
        
        if "high risk" in str(risk_assessment).lower():
            return self.flag_for_review("AI detected high fraud risk")
            
        return True
    
    @observable_trigger(
        source=OrderWorkflowState.VALIDATED,
        dest=OrderWorkflowState.PAYMENT_PROCESSING  
    )
    def process_payment(self) -> bool:
        """Process payment with metrics."""
        # Record custom metric
        if self._meter:
            payment_counter = self._meter.create_counter(
                "order.payments.initiated",
                description="Number of payment attempts"
            )
            payment_counter.add(1, attributes={
                "customer_id": self.customer_id,
                "amount_range": self._get_amount_range()
            })
        
        return True
    
    def _get_amount_range(self) -> str:
        """Categorize order amount."""
        if self.total_amount < 100:
            return "small"
        elif self.total_amount < 1000:
            return "medium"
        else:
            return "large"
```

## 3. Integration Capabilities

### 3.1 Type Safety & Validation

```python
# Automatic validation from semantic conventions
order = OrderProcessor(
    order_id="ORD-123",
    customer_id="CUST-456",
    total_amount=99.99,
    state="invalid"  # ❌ ValidationError: not in allowed values
)

# Type-safe state transitions
order.state = OrderWorkflowState.SHIPPED  # ✅ IDE autocomplete
order.ship_order()  # ✅ Only available in correct state
```

### 3.2 Observable State Machines

```python
# Every transition creates detailed spans
{
    "span_name": "fsm.transition.validate_order",
    "trace_id": "7d3a4f9d2c1b5e8a",
    "attributes": {
        "fsm.transition.trigger": "validate_order",
        "fsm.transition.source": "pending", 
        "fsm.transition.dest": "validated",
        "fsm.model.type": "OrderProcessor",
        "order.order_id": "ORD-123",
        "order.customer_id": "CUST-456",
        "order.total_amount": 99.99
    },
    "duration_ms": 125
}
```

### 3.3 AI-Enhanced Workflows

```python
class IntelligentWorkflow(WeaverFSMModel):
    """Workflow with AI decision making."""
    
    @observable_trigger(source="analyzing", dest="*")
    def ai_transition(self, context: str):
        """AI determines next state."""
        # Get possible transitions
        possible_states = self.get_triggers(self.state)
        
        # Use DSPy for intelligent routing
        prompt = f"""
        Current state: {self.state}
        Context: {context}
        Possible next states: {possible_states}
        
        What should be the next state and why?
        """
        
        decision = self.forward(prompt)
        next_state = self._parse_ai_decision(decision)
        
        # Transition to AI-selected state
        getattr(self, f"to_{next_state}")()
        return True
```

### 3.4 Workflow Composition

```python
# Compose multiple FSM models into workflows
from dslmodel.workflow import Workflow, Job, Action

# Create pipeline models
data_pipeline = DataPipelineModel(
    pipeline_name="Customer Analytics",
    transform_rules=["normalize", "enrich", "aggregate"]
)

ml_pipeline = MLPipelineModel(
    model_name="Churn Predictor",
    features=["usage_stats", "payment_history"]
)

# Orchestrate as workflow
workflow = Workflow(
    name="daily-analytics",
    jobs=[
        Job(
            name="data-prep",
            actions=[data_pipeline.to_workflow_action()]
        ),
        Job(
            name="ml-training",
            actions=[ml_pipeline.to_workflow_action()],
            depends_on=["data-prep"]
        )
    ]
)

# Execute with full observability
workflow.run()
```

## 4. Real Implementation Examples

### 4.1 Order Processing System

From `src/dslmodel/examples/weaver_fsm_example.py`:

```python
class OrderWorkflow(WeaverFSMModel):
    """Production-ready order processing workflow."""
    
    # Type-safe fields from semantic conventions
    order_id: str = Field(description="Unique order identifier")
    customer_id: str = Field(description="Customer placing the order")
    total_amount: float = Field(description="Total order amount in USD")
    state: OrderState = Field(default=OrderState.PENDING)
    
    @observable_trigger(source=OrderState.PENDING, dest=OrderState.VALIDATED)
    def validate_order(self) -> bool:
        """Validate with automatic observability."""
        logger.info(f"Validating order {self.order_id}")
        
        if self.total_amount <= 0:
            raise ValueError("Invalid order amount")
            
        # Business logic with span attributes
        self.is_validated = True
        return True
```

### 4.2 Data Pipeline with Metrics

From `src/dslmodel/examples/dslmodel_weaver_fsm_workflow.py`:

```python
class DataPipelineModel(WeaverFSMModel):
    """Observable data pipeline with quality metrics."""
    
    pipeline_id: str = Field(
        default="{{ 'PIPE-' + fake_lexify('????-????') }}",
        description="Auto-generated pipeline ID"
    )
    
    quality_metrics: DataQualityMetrics = Field(
        default_factory=DataQualityMetrics
    )
    
    @observable_trigger(
        source=DataPipelineState.VALIDATING,
        dest=DataPipelineState.TRANSFORMING
    )
    def transform_data(self) -> bool:
        """Transform with detailed metrics."""
        # Add span attributes
        span = trace.get_current_span()
        span.set_attributes({
            "pipeline.transform.rules_count": len(self.transform_rules),
            "pipeline.transform.valid_records": self.quality_metrics.valid_records
        })
        
        # Record custom metrics
        if self._meter:
            self._meter.create_histogram(
                "pipeline.transform.duration"
            ).record(
                self._get_transform_duration(),
                attributes={"pipeline": self.pipeline_name}
            )
        
        return True
```

### 4.3 Workflow State Generator

```python
# Generate complete FSM workflow from configuration
generator = WorkflowStateGenerator()

success = generator.generate_fsm_model(
    workflow_name="approval",
    states=["draft", "submitted", "reviewing", "approved", "rejected"],
    transitions=[
        {"trigger": "submit", "source": "draft", "dest": "submitted"},
        {"trigger": "approve", "source": "reviewing", "dest": "approved"},
        {"trigger": "reject", "source": "reviewing", "dest": "rejected"}
    ],
    attributes={
        "approver_id": {
            "type": "string",
            "requirement_level": "required",
            "brief": "ID of the approver"
        }
    }
)
```

## 5. Testing and Validation Patterns

### 5.1 Unit Testing FSM Models

```python
def test_fsm_state_transitions():
    """Test state machine transitions."""
    model = TestObservableFSM(name="test")
    
    # Initial state
    assert model.state == TestState.IDLE
    
    # Valid transition
    model.start()
    assert model.state == TestState.RUNNING
    
    # Invalid transition should fail
    with pytest.raises(MachineError):
        model.start()  # Can't start when already running
```

### 5.2 Integration Testing with Mocked OTEL

```python
@patch('opentelemetry.trace.get_tracer')
def test_observability_integration(mock_tracer):
    """Test OTEL integration."""
    model = OrderWorkflow(order_id="TEST-123")
    model.setup_observability("test-service")
    
    # Verify tracer setup
    assert model._tracer is not None
    mock_tracer.assert_called_with("test-service")
    
    # Test span creation
    with patch.object(model._tracer, 'start_span') as mock_span:
        model.validate_order()
        mock_span.assert_called_with(
            "fsm.transition.validate_order",
            attributes={
                "fsm.transition.trigger": "validate_order",
                "fsm.transition.source": "pending",
                "fsm.transition.dest": "validated"
            }
        )
```

### 5.3 Semantic Convention Validation

```python
def test_generated_model_validation():
    """Test generated models enforce conventions."""
    # Valid model
    order = OrderWorkflowModel(
        order_id="ORD-123",
        customer_id="CUST-456",
        total_amount=99.99,
        state=OrderWorkflowState.PENDING
    )
    assert order.model_validate(order.model_dump())
    
    # Invalid state value
    with pytest.raises(ValidationError) as exc:
        OrderWorkflowModel(
            order_id="ORD-123",
            customer_id="CUST-456", 
            total_amount=99.99,
            state="invalid_state"
        )
    assert "state" in str(exc.value)
```

## 6. Production Deployment Considerations

### 6.1 Performance Optimization

```python
# Batch span processor for production
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://otel-collector:4317"),
        max_queue_size=2048,
        max_export_batch_size=512,
        schedule_delay_millis=5000
    )
)
```

### 6.2 Error Handling & Recovery

```python
class ResilientWorkflow(WeaverFSMModel):
    """Workflow with built-in error handling."""
    
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    
    @observable_trigger(source="processing", dest="failed")
    def handle_error(self, error: Exception) -> bool:
        """Centralized error handling."""
        # Record error metrics
        if self._meter:
            error_counter = self._meter.create_counter(
                "workflow.errors.total"
            )
            error_counter.add(1, attributes={
                "error_type": error.__class__.__name__,
                "workflow": self.__class__.__name__,
                "retry_count": self.retry_count
            })
        
        # Implement retry logic
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            return self.retry_processing()
        
        return True
```

### 6.3 Monitoring & Alerting

```yaml
# prometheus-rules.yaml
groups:
  - name: workflow_alerts
    rules:
      - alert: HighWorkflowErrorRate
        expr: |
          rate(workflow_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High workflow error rate"
          description: "Workflow {{ $labels.workflow }} has error rate > 10%"
      
      - alert: SlowStateTransitions  
        expr: |
          histogram_quantile(0.95, fsm_transition_duration_seconds) > 1
        for: 10m
        annotations:
          summary: "Slow FSM transitions detected"
```

### 6.4 Scalability Patterns

```python
# Distributed workflow execution
class DistributedOrchestrator(DSLModel):
    """Orchestrate workflows across multiple workers."""
    
    def distribute_workflow(self, workflow: Workflow):
        """Distribute jobs across workers."""
        for job in workflow.jobs:
            # Send to task queue (Celery, RQ, etc.)
            task_queue.send_task(
                "execute_job",
                args=[job.model_dump()],
                headers={
                    "traceparent": self._get_trace_context()
                }
            )
```

## 7. Future Roadmap

### 7.1 Enhanced Code Generation

- **Multi-language Support**: Generate models for Go, Java, JavaScript
- **GraphQL Schema Generation**: Auto-generate GraphQL types from conventions
- **API Client Generation**: Generate type-safe API clients
- **Database Schema Generation**: Generate SQL/NoSQL schemas

### 7.2 Advanced Observability

- **Distributed Tracing**: Cross-service workflow correlation
- **Custom Dashboards**: Auto-generated Grafana dashboards
- **Anomaly Detection**: ML-based workflow anomaly detection
- **Cost Attribution**: Track workflow execution costs

### 7.3 AI/ML Integration

- **Predictive Transitions**: ML models predict optimal state paths
- **Automated Optimization**: AI suggests workflow improvements
- **Natural Language Workflows**: Define workflows in plain English
- **Self-Healing Workflows**: Automatic error recovery strategies

### 7.4 Developer Experience

- **Visual Workflow Designer**: Drag-and-drop workflow creation
- **IDE Plugins**: IntelliSense for semantic conventions
- **Testing Framework**: Specialized workflow testing tools
- **Documentation Generation**: Auto-generate workflow docs

### 7.5 Enterprise Features

- **Workflow Versioning**: Manage workflow schema evolution
- **A/B Testing**: Compare workflow variations
- **Compliance Tools**: Audit trail and compliance reporting
- **Multi-tenancy**: Isolated workflow execution environments

## Conclusion

The Weaver Forge and DSLModel integration represents a significant advancement in building observable, type-safe workflows. By combining OpenTelemetry's semantic conventions with DSLModel's powerful features, developers can create production-ready systems that are:

- **Type-Safe**: Compile-time validation prevents runtime errors
- **Observable**: Every state transition is automatically instrumented
- **Intelligent**: AI-powered decision making built-in
- **Composable**: Build complex workflows from simple components
- **Testable**: Comprehensive testing patterns included
- **Scalable**: Production-ready performance optimizations

The integration is already being used in production systems and continues to evolve with new capabilities being added regularly. The combination of semantic conventions, code generation, state machines, and observability creates a powerful foundation for modern workflow development.