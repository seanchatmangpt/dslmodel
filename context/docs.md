# DSLModel Technical Documentation v2

## Development Guidelines

### Code Organization Principles v2

1. **Enhanced Mixin-Based Architecture**: Core functionality organized through verified mixins:
   - `FSMMixin`: State machine integration with OTEL telemetry and AI transitions
   - `JinjaMixin`: Template rendering capabilities
   - `ToolMixin`: AI tool integration
   - `FileHandlerMixin`: File system operations
   - `DSLModel`: Base class with rich validation and export capabilities

2. **Dependency Injection**: Use the `inject` library for clean dependency management:
   ```python
   import inject
   
   @inject.autoparams()
   def process_model(generator: DSLClassGenerator):
       return generator.generate_from_prompt(prompt)
   ```

3. **Enhanced Type Safety**: Leverage Pydantic v2 with generated OTEL models:
   ```python
   from dslmodel import DSLModel
   from dslmodel.integrations.otel import DslmodelAttributes
   from pydantic import Field
   
   class WorkflowModel(DSLModel):
       name: str = Field(..., description="Workflow identifier")
       status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)
       otel_attributes: DslmodelAttributes = Field(..., description="Type-safe telemetry")
   ```

### Testing Strategy (80/20 Implementation)

**High ROI Tests:**
- **Smoke Tests**: Framework availability and import validation
- **Essential Workflows**: Core user journeys (generate → validate → output)
- **Error Handling**: Graceful failure modes
- **Performance Baselines**: Simple timeout assertions

**Test Commands v2:**
```bash
# Verified integration testing
python src/dslmodel/integrations/otel/tests/full_loop_test.py  # Complete integration (~30s)
dsl forge validate                                            # OTEL model validation
poetry run poe otel-test                                     # CLI OTEL validation
poetry run poe demo-full-fast                                # Quick full cycle demo
poetry run pytest src/dslmodel/integrations/otel/tests/      # Integration test suite
```

**Test Structure:**
```python
def test_essential_workflow():
    """Test core functionality - high ROI, low complexity"""
    # Focus on what matters most
    # Avoid complex mocking
    # Use real CLI execution
    assert system_works()
```

### OpenTelemetry Integration Patterns v2

**1. Type-Safe Model Generation:**
```python
from dslmodel.integrations.otel import WeaverForgeIntegration
from dslmodel.integrations.otel import DslmodelAttributes

# Generate type-safe OTEL models
integration = WeaverForgeIntegration()
success = integration.generate_models("semconv_registry", target="python")
```

**2. Validated Telemetry Creation:**
```python
from dslmodel.integrations.otel import DslmodelAttributes
from dslmodel.workflows import WorkflowOrchestrator

# Create workflow with validated telemetry
workflow = WorkflowOrchestrator(
    workflow_name="data-pipeline",
    workflow_status="started"
)

# Get validated telemetry data
telemetry = workflow.get_telemetry_data()
print(telemetry.to_json())  # OTEL-compatible span
```

**3. FSM + OTEL Coordination:**
```python
from dslmodel.examples.otel import DSLWorkflow

# Create workflow with FSM + OTEL integration
workflow = DSLWorkflow(workflow_name="governance-pipeline")

# Execute with automatic state transitions and telemetry
workflow.start_processing()  # FSM transition + OTEL span
workflow.complete_successfully(duration_ms=150)

# Export telemetry
span_data = workflow.export_telemetry()  # JSONL format
```

### Weaver Forge Integration v2

**Type-Safe Model Generation:**
```bash
# Generate OTEL models from semantic conventions
dsl forge build --target python --output output/

# Validate Python-based conventions
dsl forge validate --module dslmodel.weaver.telemetry_spec

# Build from Python modules
dsl forge build --module dslmodel.weaver.autonomous_decision_spec
```

**Convention Structure:**
```yaml
groups:
  - id: swarm.agent
    prefix: swarm.agent
    attributes:
      - id: name
        type: string
        requirement_level: required
        brief: "Agent identifier"
```

## Business Domain Information

### Agent Coordination Domain

The system models real-world coordination patterns through AI agents:

**Roberts Rules Agent:**
- Manages governance and formal processes
- Handles motions, voting, and parliamentary procedure
- Triggers: `motion.open`, `motion.second`, `motion.vote`

**Scrum Agent:**
- Agile project management workflows
- Sprint planning, retrospectives, daily standups
- Triggers: `sprint.start`, `story.estimate`, `retrospective.conduct`

**Lean Agent:**
- Process optimization and continuous improvement
- Defect tracking, waste elimination
- Triggers: `defect.detected`, `process.optimize`, `waste.eliminate`

### Enhanced Workflow State Management v2

**FSM + OTEL Integration:**
```python
from dslmodel.mixins import FSMMixin, trigger
from dslmodel.workflows import WorkflowOrchestrator
from enum import Enum

class WorkflowState(Enum):
    INITIALIZED = "initialized"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowAgent(WorkflowOrchestrator):
    def __init__(self):
        super().__init__()
        self.setup_fsm(state_enum=WorkflowState, initial=WorkflowState.INITIALIZED)
    
    @trigger(source=WorkflowState.INITIALIZED, dest=WorkflowState.STARTED)
    def start_workflow(self):
        self.record_start()  # Automatic OTEL telemetry
```

**State Transitions:**
- Always emit telemetry spans for state changes
- Include context data in span attributes
- Use Weaver conventions for attribute naming

### Template System Domain

**Jinja2 Extensions:**
```python
# Faker integration for realistic test data
{{ fake.name() }}
{{ fake.email() }}
{{ fake.company() }}

# Inflection for string transformations
{{ "user_model" | camelize }}  # UserModel
{{ "UserModel" | underscore }} # user_model

# Pydantic model awareness
{% for field in model.fields %}
{{ field.name }}: {{ field.type }}
{% endfor %}
```

## Technical Implementation Details

### MQ7 Event System

**Event Registration:**
```python
from dslmodel.mq7.event_registry import EventRegistry

# Register event handler
@EventRegistry.register("user.signup")
def handle_user_signup(event_data):
    # Process signup
    # Emit telemetry
    return {"status": "processed"}
```

**Async Event Processing:**
```python
import asyncio
from dslmodel.mq7 import HappyClient

async def process_events():
    client = HappyClient()
    await client.start()
    # Events are processed automatically
```

### DSPy Integration Patterns

**Structured Generation:**
```python
from dslmodel.dspy_modules.gen_pydantic_instance import gen_instance

# Generate Pydantic model from prompt
model_instance = gen_instance(
    prompt="Create a user model with email validation",
    model_class=UserModel
)
```

**Chain of Thought:**
```python
import dspy

class ModelGenerator(dspy.Module):
    def __init__(self):
        self.generate = dspy.ChainOfThought(
            "prompt -> reasoning, model_code"
        )
    
    def forward(self, prompt):
        return self.generate(prompt=prompt)
```

### CLI Architecture Details

**Typer Integration:**
```python
import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def generate(
    prompt: Annotated[str, typer.Argument(help="Generation prompt")],
    output_dir: Annotated[str, typer.Option("--output", "-o")] = "."
):
    """Generate DSL models from natural language."""
    # Implementation
```

**Sub-Application Pattern:**
```python
# Main CLI
main_app = typer.Typer()

# Sub-applications
swarm_app = typer.Typer()
coord_app = typer.Typer()

# Mount sub-apps
main_app.add_typer(swarm_app, name="swarm")
main_app.add_typer(coord_app, name="coord")
```

## Integration Patterns

### External LLM Integration

**OpenAI Configuration:**
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)

# Use with proper error handling
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
except OpenAIError as e:
    # Handle gracefully
    logger.error(f"OpenAI API error: {e}")
```

**Groq Alternative:**
```python
# Configure for Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
```

### Poetry Workflow Integration

**Task Definitions:**
```toml
[tool.poe.tasks.custom-workflow]
help = "Custom workflow description"
sequence = [
    { cmd = "dsl gen 'model prompt'" },
    { cmd = "dsl swarm emit span.trigger" },
    { cmd = "dsl coord work list" }
]
```

**Development Tasks v2:**
```bash
poe api --dev                    # Development API server
poe docs --docformat numpy      # Generate documentation
poe test-watch                   # Continuous testing
poe swarm-integrated             # Integrated swarm demo via dsl CLI
poe demo-full-fast              # Quick full cycle demonstration
poe otel-test                   # OTEL integration testing
```

## Troubleshooting Guides

### Common Issues

**1. OpenAI API Key Issues:**
```bash
# Check environment
echo $OPENAI_API_KEY

# Test with dummy key (for import testing)
OPENAI_API_KEY=test_key dsl --help
```

**2. Poetry Environment Problems:**
```bash
# Reset environment
poetry env remove python
poetry install

# Check environment
poetry env info
poetry run python -c "import dslmodel; print('OK')"
```

**3. OTEL Integration Issues:**
```bash
# Check OTEL model generation
dsl forge build --target python
dsl forge validate

# Test type-safe telemetry
python src/dslmodel/integrations/otel/tests/test_integration.py

# Validate full integration
python src/dslmodel/integrations/otel/tests/full_loop_test.py
```

**4. Agent Coordination Problems:**
```bash
# Test integrated swarm coordination
dsl swarm demo
dsl swarm status
dsl swarm telemetry

# Test FSM + OTEL integration
python src/dslmodel/examples/otel/working_fsm_demo.py

# Validate workflow orchestration
python src/dslmodel/workflows/workflow_orchestrator.py
```

### Debug Patterns

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# OTEL debug
os.environ['OTEL_LOG_LEVEL'] = 'DEBUG'
```

**Validate Generated Models:**
```python
from pydantic import ValidationError

try:
    model = GeneratedModel(**data)
except ValidationError as e:
    print(f"Validation errors: {e.errors()}")
```

### Performance Optimization

**Template Caching:**
```python
from jinja2 import Environment, FileSystemLoader

# Use cached loader
env = Environment(
    loader=FileSystemLoader('templates'),
    cache_size=100,
    auto_reload=False  # In production
)
```

**OTEL Sampling:**
```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBasedSampler

# Sample 10% of traces in production
sampler = TraceIdRatioBasedSampler(rate=0.1)
```

## Security Considerations

### Credential Management

**Never in Code:**
```python
# ❌ Never do this
api_key = "sk-..."

# ✅ Use environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")
```

**Template Security:**
```python
# Sanitize user input in templates
from markupsafe import escape

safe_prompt = escape(user_prompt)
```

### OTEL Security

**Sanitize Span Attributes:**
```python
def safe_span_attributes(data):
    """Remove sensitive data from span attributes."""
    safe_data = data.copy()
    safe_data.pop('api_key', None)
    safe_data.pop('password', None)
    return safe_data
```

## Version Control Best Practices

### Context Maintenance

1. **Update context with code changes**
2. **Review context in pull requests**
3. **Keep diagrams synchronized with architecture**
4. **Version control all context files**

### Git Hooks

```bash
# Pre-commit hook to validate context
#!/bin/bash
if [ -f context/index.md ]; then
    # Validate YAML front matter
    python -c "import yaml; yaml.safe_load(open('context/index.md').read().split('---')[1])"
fi
```

This documentation provides comprehensive guidance for developing, integrating, and maintaining the DSLModel framework. Regular updates ensure it remains accurate and useful for both human developers and AI systems.