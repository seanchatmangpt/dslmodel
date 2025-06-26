# Weaver + FSM + DSLModel Integration

This document describes the integration between OpenTelemetry Weaver Forge, FSMMixin state machines, and DSLModel for building observable, type-safe workflows.

## Overview

The integration combines four key components:

1. **Weaver Forge**: Generates type-safe Pydantic models from OpenTelemetry semantic conventions
2. **FSMMixin**: Provides state machine capabilities with `@trigger` decorators
3. **DSLModel**: Base model with Jinja2, DSPy, file handling, and workflow capabilities
4. **OpenTelemetry**: Automatic instrumentation of state transitions and business logic

## Key Benefits

- **Type Safety**: OTEL semantic conventions enforce valid telemetry data
- **Observability**: Automatic span/metric generation for state transitions
- **Declarative**: Define workflows using semantic conventions + state machines
- **AI-Powered**: Integrate DSPy for intelligent state transitions
- **Scalable**: Built on proven DSLModel patterns

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Semantic        │    │ Weaver Forge    │    │ Generated       │
│ Conventions     │───►│ Code Generator  │───►│ FSM Models      │
│ (YAML)          │    │                 │    │ (Python)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ OpenTelemetry   │◄───│ Observable      │◄───│ WeaverFSMModel  │
│ Spans/Metrics   │    │ State Machine   │    │ (Base Class)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Classes

### `ObservableFSMMixin`

Extends `FSMMixin` with automatic OpenTelemetry instrumentation:

```python
class ObservableFSMMixin(FSMMixin):
    def setup_observability(self, service_name: str):
        """Initialize OTEL instrumentation."""
        
    def add_transition(self, *args, **kwargs):
        """Override to wrap transitions with spans."""
```

### `WeaverFSMModel`

Base class combining DSLModel with observable FSM:

```python
class WeaverFSMModel(DSLModel, ObservableFSMMixin):
    """
    Combines:
    - DSLModel features (Jinja2, DSPy, workflows)
    - FSM state machine capabilities
    - Automatic OTEL instrumentation
    """
```

### `WorkflowStateGenerator`

Generates semantic conventions and FSM models:

```python
generator = WorkflowStateGenerator()

# Create semantic conventions
semconv_path = generator.create_workflow_semconv(
    workflow_name="order_processing",
    states=["pending", "validated", "shipped", "delivered"],
    attributes={
        "customer_id": {"type": "string", "requirement_level": "required"}
    }
)

# Generate complete FSM model
generator.generate_fsm_model(
    workflow_name="order_processing",
    states=["pending", "validated", "shipped", "delivered"],
    transitions=[
        {"trigger": "validate", "source": "pending", "dest": "validated"},
        {"trigger": "ship", "source": "validated", "dest": "shipped"}
    ]
)
```

## Usage Patterns

### 1. Basic Observable FSM

```python
from enum import Enum
from dslmodel.otel.fsm_weaver_integration import WeaverFSMModel, observable_trigger

class OrderState(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class Order(WeaverFSMModel):
    order_id: str
    customer_id: str
    state: OrderState = OrderState.PENDING
    
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.setup_fsm(OrderState, initial=OrderState.PENDING)
        self.setup_observability("order-service")
    
    @observable_trigger(source=OrderState.PENDING, dest=OrderState.SHIPPED)
    def ship_order(self):
        # Business logic with automatic span creation
        logger.info(f"Shipping order {self.order_id}")
        return True
        
    @observable_trigger(source=OrderState.SHIPPED, dest=OrderState.DELIVERED)
    def deliver_order(self):
        logger.info(f"Order {self.order_id} delivered")
        return True
```

### 2. Generated Models from Semantic Conventions

Create `semconv/order.yaml`:

```yaml
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
            - id: shipped
              value: 'shipped'
            - id: delivered
              value: 'delivered'
        requirement_level: required
        brief: 'Current order state'
      - id: customer_id
        type: string
        requirement_level: required
        brief: 'Customer identifier'
```

Generate model:

```python
from dslmodel.otel.weaver_integration import WeaverForgeIntegration

weaver = WeaverForgeIntegration()
weaver.generate_models("semconv", target="python")

# Generates src/dslmodel/otel/models/order_workflow_model.py
```

### 3. Workflow Integration

```python
from dslmodel.workflow import Workflow, Job, Action

class DataPipeline(WeaverFSMModel):
    # ... FSM implementation
    
    def to_workflow_action(self) -> Action:
        """Convert to workflow action."""
        return Action(
            name=f"pipeline_{self.name}",
            module="data_pipeline", 
            method="execute",
            parameters=self.model_dump()
        )

# Create workflow
pipeline1 = DataPipeline(name="sales-data")
pipeline2 = DataPipeline(name="customer-data")

workflow = Workflow(
    name="daily-analytics",
    jobs=[
        Job(name="sales-job", actions=[pipeline1.to_workflow_action()]),
        Job(name="customer-job", actions=[pipeline2.to_workflow_action()])
    ]
)
```

### 4. AI-Enhanced State Transitions

```python
class SmartWorkflow(WeaverFSMModel):
    prompt_history: List[str] = Field(default_factory=list)
    
    @observable_trigger(source="analyzing", dest="*")  # AI determines destination
    def smart_transition(self, context: str):
        """Use DSPy to determine next state."""
        # Use FSMMixin's forward() method for AI-powered transitions
        result = self.forward(
            f"Given context: {context}, what should be the next state?",
            possible_states=self.possible_transitions()
        )
        return result
```

## Observability Features

### Automatic Span Creation

Every state transition creates an OpenTelemetry span with:

```python
{
    "span_name": "fsm.transition.ship_order",
    "attributes": {
        "fsm.transition.trigger": "ship_order",
        "fsm.transition.source": "pending",
        "fsm.transition.dest": "shipped",
        "fsm.model.type": "OrderWorkflow"
    }
}
```

### Metrics Collection

Automatic metrics for:
- `fsm.transitions.total`: Counter of state transitions
- `fsm.state.duration`: Histogram of time spent in each state
- `pipeline.records.stored`: Custom business metrics

### Error Handling

Failed transitions automatically:
- Set span status to ERROR
- Record exception details
- Emit error metrics
- Support retry logic

## Template System

### FSM-Aware Templates

Templates generate models with FSM capabilities:

```jinja2
class {{ group.id | pascal_case }}Model(WeaverFSMModel):
    """{{ group.brief }}"""
    
    {% for attr in group.attributes %}
    {{ attr.id }}: {{ attr.type | python_type }} = Field(
        description="{{ attr.brief }}"
    )
    {% endfor %}
    
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.setup_fsm({{ group.id | pascal_case }}State)
        self.setup_observability("{{ group.id }}")
```

### Custom Templates

Create domain-specific templates:

```bash
mkdir -p weaver_templates/registry/python
# Add custom templates for your domain
```

## Best Practices

### 1. State Design

- Keep states focused and meaningful
- Use clear, business-oriented state names
- Design for observability (each state should be measurable)

### 2. Transition Logic

- Keep transition methods focused on single responsibility
- Use conditions and guards for complex business rules
- Always return boolean from transition methods

### 3. Error Handling

```python
@observable_trigger(source="processing", dest="failed")
def handle_error(self, error: Exception):
    """Centralized error handling."""
    self.error_message = str(error)
    self.error_count += 1
    
    # Emit custom metrics
    if self._meter:
        error_counter = self._meter.create_counter("workflow.errors.total")
        error_counter.add(1, attributes={
            "error_type": error.__class__.__name__,
            "workflow": self.__class__.__name__
        })
    
    return True
```

### 4. Testing

```python
def test_workflow_transitions():
    """Test state transitions with mocked observability."""
    with patch('opentelemetry.trace.get_tracer'):
        workflow = MyWorkflow(name="test")
        
        # Test state transitions
        assert workflow.state == WorkflowState.INITIAL
        workflow.start_processing()
        assert workflow.state == WorkflowState.PROCESSING
        
        # Test metrics collection
        workflow.complete_processing()
        assert workflow.transition_count == 2
```

## Performance Considerations

### Span Management

- Spans are created/ended automatically
- Minimal overhead (~1-2ms per transition)
- Uses async batch span processor

### Memory Usage

- State history not stored by default
- Use `prompts` list selectively for AI features
- Clean up completed workflows

### Scaling

- Stateless model design enables horizontal scaling
- OTEL data exported to external systems
- Workflow orchestration supports parallel execution

## Troubleshooting

### Common Issues

1. **FSM Not Initialized**
   ```python
   # Ensure model_post_init is called
   def model_post_init(self, __context):
       super().model_post_init(__context)
       self.setup_fsm(MyState)
   ```

2. **Missing OTEL Data**
   ```python
   # Check tracer provider setup
   from opentelemetry import trace
   assert trace.get_tracer_provider() is not None
   ```

3. **Template Generation Fails**
   ```bash
   # Verify weaver installation
   weaver --version
   
   # Check template directory
   ls weaver_templates/registry/python/
   ```

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("dslmodel.otel").setLevel(logging.DEBUG)
logging.getLogger("transitions").setLevel(logging.DEBUG)
```

## Examples

See complete examples in:
- `src/dslmodel/examples/weaver_fsm_example.py` - Basic integration
- `src/dslmodel/examples/dslmodel_weaver_fsm_workflow.py` - Advanced features
- `tests/test_weaver_fsm_integration.py` - Test patterns

## Future Enhancements

- **Distributed State Machines**: Cross-service state coordination
- **Visual Workflow Designer**: Generate semantic conventions from UI
- **ML-Powered Transitions**: Predict optimal transition paths
- **Real-time Dashboards**: Live workflow monitoring
- **Workflow Optimization**: Automatic performance tuning