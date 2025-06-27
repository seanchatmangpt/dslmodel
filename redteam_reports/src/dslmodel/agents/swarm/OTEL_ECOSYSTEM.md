# OpenTelemetry Ecosystem Loop for SwarmAgent

## Overview

The SwarmAgent framework integrates with OpenTelemetry to create a complete observability loop where:

1. **CLI Commands** generate OpenTelemetry spans
2. **Spans** are exported to multiple destinations (Console, JSONL, OTLP)
3. **SwarmAgents** listen to the span stream and react based on patterns
4. **Agent Reactions** generate new CLI commands
5. **New Commands** create new spans, continuing the autonomous loop

```
┌─────────────┐
│ CLI Command │
└──────┬──────┘
       │ Creates
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ OTEL Spans  │────▶│   Console   │     │    OTLP     │
└──────┬──────┘     └─────────────┘     └─────────────┘
       │ Exported to
       ▼
┌─────────────┐
│ JSONL File  │
└──────┬──────┘
       │ Consumed by
       ▼
┌─────────────┐
│SwarmAgents  │
└──────┬──────┘
       │ Generate
       ▼
┌─────────────┐
│NextCommands │
└──────┬──────┘
       │ Execute as
       └─────────────┐
                     │
                     ▼
              [Loop Continues]
```

## Architecture Components

### 1. OpenTelemetry SDK Integration

The `SwarmTelemetry` class provides full OTEL SDK integration:

```python
telemetry = SwarmTelemetry(
    service_name="swarm-ecosystem",
    span_file=Path("~/s2s/agent_coordination/telemetry_spans.jsonl"),
    enable_console=True,    # Debug output
    enable_otlp=True       # Send to collector
)
```

Features:
- Multiple span exporters (Console, JSONL, OTLP)
- Resource attributes for service identification
- Metrics collection (counters, histograms)
- Proper span context propagation

### 2. Custom JSONL Span Exporter

The `JSONLSpanExporter` bridges OpenTelemetry spans to SwarmAgent format:

```python
class JSONLSpanExporter(SpanExporter):
    """Exports OTEL spans to JSONL for SwarmAgent consumption."""
    
    def export(self, spans):
        # Convert OTEL span format to SwarmAgent SpanData format
        # Preserves trace context, attributes, and events
```

This ensures SwarmAgents can consume real OpenTelemetry spans while maintaining compatibility with the existing JSONL-based architecture.

### 3. Instrumented CLI

The `SwarmCLI` class provides OpenTelemetry-instrumented commands:

```python
cli = SwarmCLI(telemetry)

# Every command creates proper OTEL spans
cli.roberts_open_motion("sprint42", "board")
cli.scrum_review("42", velocity=45, defect_rate=5.2)
cli.lean_define("improvement-001", "High defect rate")
```

Each command:
- Creates spans with semantic attributes
- Records events for important state changes
- Sets proper span status (OK/ERROR)
- Increments metrics counters

### 4. Semantic Conventions

Defined in `semconv_registry/swarm.yaml`:

```yaml
# SwarmAgent framework attributes
swarm.agent: "roberts"           # Which agent
swarm.trigger: "vote"           # What triggered it
swarm.state.from: "IDLE"        # State transition
swarm.state.to: "VOTING"
swarm.command: "swarmsh.scrum.plan"  # Generated command

# Domain-specific attributes
roberts.motion_id: "sprint42"
roberts.voting_method: "ballot"
scrum.defect_rate: 5.2
lean.project_id: "improvement-001"
```

## Complete Loop Example

### Step 1: CLI Command Creates Span

```python
# User or system initiates action
cli.roberts_open_motion("sprint42", "board")
```

This creates an OTEL span:
```json
{
  "name": "swarmsh.roberts.open",
  "trace_id": "7d3f4e8a9b2c1d5e6f7a8b9c0d1e2f3a",
  "attributes": {
    "motion_id": "sprint42",
    "meeting_id": "board",
    "swarm.agent": "roberts",
    "swarm.trigger": "open"
  }
}
```

### Step 2: Span Exported to JSONL

The `JSONLSpanExporter` writes to the configured file:
```bash
~/s2s/agent_coordination/telemetry_spans.jsonl
```

### Step 3: SwarmAgent Reacts

```python
# RobertsAgent listening to span stream
span = parse_span(line)
if "open" in span.name.lower():
    cmd = self.open_motion(span)
    # Returns: NextCommand("swarmsh.roberts.call-to-order", ...)
```

### Step 4: Agent Command Execution

```python
# Monitor executes the command
cli.execute_command(cmd)
```

This creates a new span, continuing the loop!

### Step 5: Cross-Agent Communication

When Roberts approves a sprint motion:
```
Roberts.close (vote passed) 
    → generates command: "swarmsh.scrum.sprint-planning"
    → Scrum.plan span created
    → ScrumAgent reacts and transitions state
```

## Running the Full Loop

### Basic Setup

```python
import asyncio
from dslmodel.agents.swarm.otel_loop import run_ecosystem_loop

# Run the demo
asyncio.run(run_ecosystem_loop())
```

### Production Setup

```python
# 1. Initialize telemetry
telemetry = SwarmTelemetry(
    service_name="production-swarm",
    enable_otlp=True  # Send to collector
)

# 2. Start agents in separate processes
python -m dslmodel.agents.examples.roberts_agent &
python -m dslmodel.agents.examples.scrum_agent &
python -m dslmodel.agents.examples.lean_agent &

# 3. Use instrumented CLI
cli = SwarmCLI(telemetry)
cli.roberts_open_motion("real-motion", "production")
```

## Observability Benefits

### 1. Full Trace Visibility

Every action in the swarm creates connected traces:
```
├─ swarmsh.roberts.open
├─ swarmsh.roberts.vote
├─ swarmsh.roberts.close
│  └─ swarm.loop.iteration
│     └─ swarmsh.command.execute
│        └─ swarmsh.scrum.plan
└─ swarmsh.scrum.review
   └─ swarm.loop.iteration
      └─ swarmsh.lean.define
```

### 2. Metrics Collection

Track system health with built-in metrics:
- `swarm.spans.total` - Total spans by type
- `swarm.commands.total` - Commands executed
- `swarm.loop.duration` - Loop iteration time
- `swarm.agent.transitions` - State changes

### 3. Distributed Tracing

With OTLP export enabled, view traces in:
- Jaeger
- Zipkin
- Datadog
- New Relic
- Any OTLP-compatible backend

### 4. Real-time Monitoring

```bash
# Watch spans in real-time
tail -f ~/s2s/agent_coordination/telemetry_spans.jsonl | jq '
  select(.name | startswith("swarmsh")) | 
  {time: .timestamp, name: .name, agent: .attributes."swarm.agent"}
'
```

## Advanced Patterns

### Context Propagation

```python
# Parent span context flows through the system
with telemetry.tracer.start_as_current_span("workflow") as parent:
    cli.roberts_open_motion("motion1")  # Child of workflow
    cli.roberts_vote("motion1")         # Sibling span
```

### Error Handling

```python
try:
    with self._span("risky.operation") as span:
        result = risky_operation()
        span.set_status(Status(StatusCode.OK))
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.record_exception(e)
```

### Custom Attributes

```python
# Add domain-specific attributes
span.set_attributes({
    "business.value": 1000000,
    "risk.level": "high",
    "approval.required": True
})
```

## Integration with Existing Tools

### 1. Weaver Code Generation

Generate typed models from semantic conventions:

```bash
# Generate Python models
cd /Users/sac/dev/dslmodel
python -m dslmodel.otel.weaver_integration generate \
    --registry semconv_registry \
    --templates weaver_templates/registry/python \
    --output src/dslmodel/otel/models
```

### 2. DSLModel Integration

Generated models extend DSLModel base:

```python
class SwarmAttributes(DSLModel):
    """Auto-generated from swarm.yaml."""
    swarm_agent: str = Field(..., description="SwarmAgent name")
    swarm_trigger: str = Field(..., description="Trigger keyword")
```

### 3. Coordination CLI Enhancement

Enhance existing CLI with OTEL:

```python
# In coordination_cli.py
from dslmodel.agents.swarm.otel_loop import SwarmTelemetry

telemetry = SwarmTelemetry()

@traced  # Auto-instrument commands
def work_claim(assignee: str):
    # Existing logic
    pass
```

## Best Practices

1. **Semantic Naming**: Use dot-notation for span names (`swarmsh.agent.action`)
2. **Rich Attributes**: Include business context in span attributes
3. **Error Handling**: Always set span status and record exceptions
4. **Batch Processing**: Use BatchSpanProcessor for production
5. **Sampling**: Configure trace sampling for high-volume systems
6. **Metrics**: Track key business metrics, not just technical ones

## Troubleshooting

### Spans Not Appearing

```bash
# Check span file is being written
ls -la ~/s2s/agent_coordination/telemetry_spans.jsonl

# Verify agents are running
ps aux | grep agent.py

# Check for errors in agent output
tail -f agent.log
```

### Performance Issues

```python
# Use sampling for high volume
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

sampler = TraceIdRatioBased(0.1)  # Sample 10%
tracer_provider = TracerProvider(sampler=sampler)
```

### OTLP Connection Failed

```bash
# Verify collector is running
docker ps | grep otel-collector

# Check endpoint configuration
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

## Summary

The OpenTelemetry ecosystem loop provides:

1. **Complete Observability**: Every action is traced
2. **Autonomous Operation**: Agents react to real telemetry
3. **Standards Compliance**: Uses OpenTelemetry conventions
4. **Extensibility**: Easy to add new agents and patterns
5. **Production Ready**: Scales with sampling and batching

This creates a self-documenting, self-monitoring system where the telemetry IS the event bus, and observability IS the architecture.