# SwarmAgent Framework

A lightweight, span-driven multi-agent system for orchestrating governance, delivery, and optimization workflows.

## Overview

The SwarmAgent framework enables creation of autonomous agents that:
- React to OpenTelemetry spans in real-time
- Maintain state via finite state machines
- Coordinate through CLI command execution
- Implement specialized methodologies (Roberts Rules, Scrum, Lean/DMAIC)

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Roberts    │     │   Scrum     │     │    Lean     │
│   Agent     │     │   Agent     │     │   Agent     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │ SwarmAgent  │
                    │ Base Class  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ JSONL Span  │
                    │   Stream    │
                    └─────────────┘
```

## Quick Start

### 1. Create Your Agent

```python
from enum import Enum, auto
from dslmodel.agents.swarm import SwarmAgent, NextCommand, trigger

class MyState(Enum):
    IDLE = auto()
    ACTIVE = auto()
    DONE = auto()

class MyAgent(SwarmAgent):
    StateEnum = MyState
    TRIGGER_MAP = {"start": "on_start", "finish": "on_finish"}
    LISTEN_FILTER = "swarmsh.myagent."  # Optional

    @trigger(source=MyState.IDLE, dest=MyState.ACTIVE)
    def on_start(self, span):
        self._transition("Starting work", MyState.ACTIVE)
        return NextCommand(
            fq_name="swarmsh.myagent.process",
            args=["--task-id", span.attributes.get("task_id", "default")]
        )

    @trigger(source=MyState.ACTIVE, dest=MyState.DONE)
    def on_finish(self, span):
        self._transition("Work complete", MyState.DONE)
```

### 2. Run Your Agent

```bash
python my_agent.py
```

### 3. Trigger Events

```bash
# Via coordination CLI
python coordination_cli.py myagent start --task-id task123

# Or emit spans directly
echo '{"name":"swarmsh.myagent.start","trace_id":"t1","span_id":"s1","timestamp":1234567890,"attributes":{"task_id":"task123"}}' >> ~/s2s/agent_coordination/telemetry_spans.jsonl
```

## Creating Swarm-Aware Agents

### Requirements Checklist

| Component | Description | Example |
|-----------|-------------|---------|
| **StateEnum** | Enum defining agent lifecycle states | `class State(Enum): IDLE = auto()` |
| **TRIGGER_MAP** | Maps event keywords to handler methods | `{"ping": "on_ping"}` |
| **@trigger methods** | State transition handlers | `@trigger(source=IDLE, dest=ACTIVE)` |
| **LISTEN_FILTER** | (Optional) Span name prefix filter | `"swarmsh.myagent."` |

### Agent Recipe

```python
# agents/[domain]_agent.py
from enum import Enum, auto
from dslmodel.agents.swarm import SwarmAgent, NextCommand, trigger

class [Domain]State(Enum):
    # Define your states
    IDLE = auto()
    # ... more states

class [Domain]Agent(SwarmAgent):
    StateEnum = [Domain]State
    LISTEN_FILTER = "swarmsh.[domain]."
    TRIGGER_MAP = {
        "keyword1": "handler_method1",
        "keyword2": "handler_method2",
    }

    @trigger(source=[Domain]State.IDLE, dest=[Domain]State.NEXT)
    def handler_method1(self, span):
        # 1. Extract data from span
        param = span.attributes.get("param", "default")
        
        # 2. Record transition
        self._transition(f"Handling {param}", [Domain]State.NEXT)
        
        # 3. Return next command (optional)
        return NextCommand(
            fq_name="swarmsh.[domain].action",
            args=["--param", param]
        )

if __name__ == "__main__":
    [Domain]Agent().run()
```

## Built-in Agent Examples

### Roberts Agent (Governance)
- **Purpose**: Formal meeting procedures and voting
- **States**: IDLE → MOTION_OPEN → VOTING → CLOSED
- **Triggers**: open, vote, close
- **Integration**: Can spawn Scrum sprints after approval

### Scrum Agent (Delivery)
- **Purpose**: Sprint management and team coordination
- **States**: PLANNING → EXECUTING → REVIEW → RETRO
- **Triggers**: plan, daily, review, retro
- **Integration**: Can spawn Lean projects for quality issues

### Lean Agent (Optimization)
- **Purpose**: DMAIC continuous improvement
- **States**: DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL
- **Triggers**: define, measure, analyze, improve, control
- **Integration**: Can request Roberts votes for process changes

## Running the Full Swarm

```bash
# Terminal 1: Roberts Agent
python agents/roberts_agent.py

# Terminal 2: Scrum Agent
python agents/scrum_agent.py

# Terminal 3: Lean Agent
python agents/lean_agent.py

# Terminal 4: Monitor spans
tail -f ~/s2s/agent_coordination/telemetry_spans.jsonl | jq .

# Terminal 5: Trigger initial event
python coordination_cli.py roberts open --motion-id sprint42 --meeting-id board
```

## Inter-Agent Communication Flow

```
Roberts.vote_passed → Scrum.sprint_planning
                ↓
         Scrum.review_failed → Lean.define_project
                                    ↓
                            Lean.control → Roberts.vote_process_change
```

## Advanced Features

### Async Support

```python
import asyncio

async def main():
    agent = MyAgent()
    await agent.arun()  # Async version of run()

asyncio.run(main())
```

### Custom Span Filtering

```python
class MyAgent(SwarmAgent):
    LISTEN_FILTER = "swarmsh.myapp."  # Only process myapp spans
    
    def forward(self, span):
        # Additional custom filtering
        if span.attributes.get("environment") != "production":
            return None
        return super().forward(span)
```

### Span Emission

Agents automatically emit transition spans:

```json
{
  "name": "myagent.transition",
  "trace_id": "trace_1234567890",
  "span_id": "span_1234567890000",
  "timestamp": 1234567890.123,
  "attributes": {
    "agent": "MyAgent",
    "from_state": "IDLE",
    "to_state": "ACTIVE",
    "prompt": "Starting work"
  }
}
```

## Configuration

### Environment Variables

```bash
# Agent coordination root directory
export S2S_AGENT_ROOT=~/s2s/agent_coordination

# Span file name
export S2S_SPAN_FILE=telemetry_spans.jsonl

# CLI command
export S2S_CLI_CMD="python coordination_cli.py"
```

### Programmatic Configuration

```python
agent = MyAgent(
    root_dir=Path("/custom/path"),
    span_file="custom_spans.jsonl",
    cli_command=["node", "cli.js"]
)
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import patch, MagicMock

def test_agent_transition():
    agent = MyAgent()
    span = SpanData(
        name="swarmsh.myagent.start",
        trace_id="t1",
        span_id="s1",
        timestamp=1234567890,
        attributes={"task_id": "test123"}
    )
    
    with patch.object(agent, 'run_cli') as mock_cli:
        cmd = agent.forward(span)
        assert cmd.fq_name == "swarmsh.myagent.process"
        assert agent.current_state == MyState.ACTIVE
```

### Integration Testing

```python
# Create test span file
test_spans = Path("test_spans.jsonl")
test_spans.write_text('{"name":"swarmsh.ping.request","trace_id":"t1","span_id":"s1","timestamp":1234567890,"attributes":{}}\n')

# Run agent with test file
agent = PingAgent(span_file="test_spans.jsonl")
# ... assertions
```

## Best Practices

1. **State Design**: Keep states focused on major lifecycle phases
2. **Trigger Names**: Use clear, action-oriented keywords
3. **Span Attributes**: Document expected attributes in docstrings
4. **Error Handling**: Agents should gracefully handle missing attributes
5. **Command Design**: Return meaningful commands that advance workflows

## FAQ

**Q: Do agents clash on the span socket?**  
A: No, each agent creates its own listener. The CLI broadcasts to all.

**Q: How do I debug agent behavior?**  
A: Enable debug logging and monitor the span stream with `tail -f | jq`

**Q: Can agents run in containers?**  
A: Yes, mount the span file as a volume and ensure CLI access

**Q: What if an agent crashes?**  
A: Agents maintain state via FSM and can resume from current state

## Next Steps

- Explore the [example agents](../examples/) for patterns
- Read about [OpenTelemetry integration](../../otel/)
- Check out the [coordination CLI](../../commands/coordination_cli.py)
- Build your own domain-specific agents!