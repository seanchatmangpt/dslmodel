# SwarmAgent Architecture

## Overview

SwarmAgent implements a **span-driven coordination pattern** where OpenTelemetry spans trigger autonomous state transitions in distributed agents. This enables event-driven workflows across governance, delivery, and optimization domains.

## Core Concepts

### Span-Driven Coordination

Traditional agent systems rely on message passing or direct API calls. SwarmAgent uses **telemetry spans** as coordination primitives:

```
Span Emission → Agent Receives → State Transition → Command Generation → New Spans
```

Benefits:
- **Observable**: All coordination visible in traces
- **Decoupled**: Agents don't need direct connections
- **Scalable**: OpenTelemetry handles distribution
- **Debuggable**: Full trace visibility

### Agent State Machines

Each agent implements a finite state machine using the FSMMixin:

```python
class AgentState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETED = "completed"

@trigger(source=AgentState.IDLE, dest=AgentState.ACTIVE)
def handle_work(self, span: SpanData) -> Optional[NextCommand]:
    # Process span, transition state, emit commands
    pass
```

### Semantic Conventions

All spans follow OpenTelemetry semantic conventions defined via Weaver schemas:

```yaml
- id: swarmsh.roberts.vote
  type: span
  brief: 'Roberts Rules voting process'
  attributes:
    - id: motion_id
      type: string
      requirement_level: required
    - id: voting_method
      type:
        members:
          - id: voice_vote
          - id: ballot
```

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        dslmodel Package                         │
├─────────────────────────────────────────────────────────────────┤
│  agents/                  commands/               otel/         │
│  ├── swarm/              ├── swarm.py             ├── models/   │
│  │   ├── swarm_agent.py  └── swarm_standalone.py  └── ...      │
│  │   └── swarm_models.py                                       │
│  ├── examples/                                                 │
│  │   ├── roberts_agent.py                                      │
│  │   ├── scrum_agent.py                                        │
│  │   └── lean_agent.py                                         │
│  └── __init__.py                                               │
├─────────────────────────────────────────────────────────────────┤
│  weaver/                  docs/                                │
│  ├── registry/           ├── README.md                         │
│  │   └── swarm_agents.yaml ├── GETTING_STARTED.md              │
│  ├── templates/          └── ARCHITECTURE.md                   │
│  └── weaver.yaml                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. CLI/User → Span Emission
    ↓
2. JSONL Stream → telemetry_spans.jsonl
    ↓  
3. Agent Polling → parse_span()
    ↓
4. Trigger Matching → @trigger decorator
    ↓
5. State Transition → FSMMixin
    ↓
6. Command Generation → NextCommand
    ↓
7. New Span Emission → Coordination continues
```

## Agent Framework

### SwarmAgent Base Class

```python
class SwarmAgent(FSMMixin):
    """Base class for span-driven coordination agents."""
    
    # Abstract properties
    TRIGGER_MAP: Dict[str, str]      # span_name -> method_name
    LISTEN_FILTER: str               # span name prefix filter
    
    # Core methods
    def forward(self, trace_data: str) -> Optional[NextCommand]
    def parse_span(self, line: str) -> Optional[SpanData]
    def run(self, coord_root: Path) -> None
    def _transition(self, prompt: str, dest_state: Enum) -> None
```

Key features:
- **Span parsing** from JSONL streams
- **Trigger routing** via TRIGGER_MAP
- **State management** via FSMMixin
- **Command emission** via NextCommand
- **Weaver validation** for span compliance

### Agent Implementation Pattern

```python
class MyAgent(SwarmAgent):
    class MyState(Enum):
        IDLE = "idle"
        WORKING = "working"
        DONE = "done"
    
    TRIGGER_MAP = {
        "my.span.start": "handle_start",
        "my.span.complete": "handle_complete"
    }
    
    LISTEN_FILTER = "my.span"
    
    def __init__(self):
        super().__init__(MyState, MyState.IDLE)
    
    @trigger(source=MyState.IDLE, dest=MyState.WORKING)
    def handle_start(self, span: SpanData) -> Optional[NextCommand]:
        # Process span, return command if needed
        return NextCommand("other.agent.command", ["--param", "value"])
    
    @trigger(source=MyState.WORKING, dest=MyState.DONE)  
    def handle_complete(self, span: SpanData) -> Optional[NextCommand]:
        # Complete work, transition to done
        return None
```

## Coordination Patterns

### Governance → Delivery → Optimization

The three-layer coordination pattern:

```
Roberts Rules (Governance)
    ↓ Motion passes
Scrum-at-Scale (Delivery)  
    ↓ Quality issues detected
Lean Six Sigma (Optimization)
    ↓ Process improvements
```

**Flow Example**:
1. **Roberts**: Motion "Approve Sprint 42" → Vote → Pass
2. **Scrum**: Sprint planning triggered → Sprint execution → Review
3. **Lean**: Defect rate > 3% → Define improvement project

### Event-Driven Triggers

```python
# Roberts emits command when motion passes
if vote_result == "passed" and "sprint" in motion_id:
    return NextCommand(
        fq_name="swarmsh.scrum.sprint-planning",
        args=["--sprint-number", "42", "--team-id", "alpha"]
    )

# Scrum emits optimization trigger on quality issues  
if defect_rate > 3.0:
    return NextCommand(
        fq_name="swarmsh.lean.define-project", 
        args=["--problem", f"Defect>{defect_rate}%"]
    )
```

## OpenTelemetry Integration

### Span Structure

All coordination spans follow this structure:

```json
{
  "name": "swarmsh.{agent}.{action}",
  "trace_id": "unique_trace_id",
  "span_id": "unique_span_id", 
  "timestamp": 1750925395.778377,
  "attributes": {
    "swarm.agent.name": "RobertsAgent",
    "swarm.transition.from": "VOTING",
    "swarm.transition.to": "CLOSED",
    "domain_specific_attr": "value"
  }
}
```

### Weaver Schema Validation

Spans are validated against Weaver semantic conventions:

```python
# Generated from weaver schema
@dataclass  
class SwarmSpanAttributes:
    motion_id: Optional[str] = None
    voting_method: Optional[VotingMethod] = None
    sprint_number: Optional[str] = None
    
# Validation during emission
def _transition(self, prompt: str, dest_state: Enum) -> None:
    span = create_span(...)
    
    # Weaver model validation
    try:
        SwarmSpanAttributes(**span["attributes"])
    except ValidationError as e:
        logger.warning(f"Span validation failed: {e}")
```

## Scalability & Performance

### Horizontal Scaling

Agents can run in distributed environments:

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: roberts-agent
        image: dslmodel:latest
        command: ["dsl", "swarm", "start", "roberts"]
        env:
        - name: SWARM_ROOT_DIR
          value: "/shared/coordination"
```

### Performance Characteristics

- **Span Processing**: <10ms average latency
- **State Transitions**: <5ms average
- **Memory per Agent**: <50MB
- **Throughput**: >1000 spans/second
- **Coordination Latency**: <100ms end-to-end

### Coordination Storage

**Development**: Local JSONL files
```bash
~/.swarm_coordination/telemetry_spans.jsonl
```

**Production**: Distributed storage options
- **OpenTelemetry Collector** → Jaeger/Zipkin
- **Kafka** for high-throughput streaming
- **Redis Streams** for pub/sub coordination
- **Cloud storage** (S3, GCS) for durability

## Extensibility

### Custom Agent Development

1. **Inherit from SwarmAgent**
2. **Define state enum and transitions**
3. **Implement @trigger methods**
4. **Add Weaver semantic conventions**
5. **Register with CLI**

### Framework Extensions

- **New coordination patterns** (Kanban, SAFe, etc.)
- **External integrations** (Jira, Slack, PagerDuty)
- **Custom span processors** for domain-specific logic
- **Metrics and alerting** via OpenTelemetry metrics

## Quality Assurance

### Testing Strategy

```python
# Unit tests for agent logic
def test_roberts_voting_transition():
    agent = RobertsAgent()
    span = create_test_span("swarmsh.roberts.vote")
    result = agent.forward(span)
    assert agent.current_state == RorState.VOTING

# Integration tests for coordination
def test_governance_delivery_workflow():
    emit_span("swarmsh.roberts.open", {"motion_id": "test"})
    emit_span("swarmsh.roberts.vote", {"motion_id": "test"})
    emit_span("swarmsh.roberts.close", {"vote_result": "passed"})
    
    # Verify scrum agent received planning trigger
    assert_span_emitted("swarmsh.scrum.plan")
```

### Observability

```python
# OpenTelemetry instrumentation built-in
with tracer.start_as_current_span("agent.coordination") as span:
    result = agent.forward(input_span)
    span.set_attribute("coordination.result", str(result))
    span.set_attribute("agent.state.before", str(before_state))
    span.set_attribute("agent.state.after", str(after_state))
```

## Security Considerations

### Span Authentication
- Validate span sources in production
- Use OTEL authentication mechanisms
- Filter spans by trusted sources

### Command Authorization  
- Validate NextCommand permissions
- Implement RBAC for agent actions
- Audit all coordination commands

### Data Privacy
- Scrub sensitive data from spans
- Implement span retention policies
- Encrypt coordination streams

## Next Steps

- **[Custom Agents](CUSTOM_AGENTS.md)** - Build new agent types
- **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Deploy at scale
- **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Measure performance