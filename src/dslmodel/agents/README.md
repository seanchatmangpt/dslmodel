# SwarmAgent Implementation (80/20 Solution)

## Overview

This is an 80/20 implementation of the SwarmAgent pattern - autonomous agents that react to OpenTelemetry spans and coordinate through a shared event stream.

## What Was Implemented

### 1. Core Infrastructure
- **Base Class**: `SwarmAgent` in `swarm/swarm_agent.py` - provides span watching, state management, and CLI execution
- **Data Models**: `swarm/swarm_models.py` - Pydantic models for spans, commands, and agent state
- **Integration**: Uses existing `FSMMixin` for state machine functionality

### 2. Example Agents

#### PingAgent (`examples/ping_agent.py`)
- Minimal "Hello World" example
- Responds to ping spans with pong commands
- States: IDLE → PINGED

#### RobertsAgent (`examples/roberts_agent.py`)
- Governance framework (Roberts Rules of Order)
- Manages meetings, motions, and voting
- States: IDLE → MOTION_OPEN → VOTING → CLOSED
- Triggers sprint planning when motions pass

#### ScrumAgent (`examples/scrum_agent.py`)
- Delivery framework (Scrum-at-Scale)
- Manages sprints: planning, execution, review, retrospectives
- States: PLANNING → EXECUTING → REVIEW → RETRO
- Triggers Lean projects when quality issues detected (>3% defect rate)

#### LeanAgent (`examples/lean_agent.py`)
- Optimization framework (DFLSS/DMAIC)
- Manages continuous improvement projects
- States: DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL
- Requests governance approval for process changes

### 3. Testing & Demo
- **Test Harness**: `test_swarm_agents.py` - unit tests for agent functionality
- **Demo Script**: `run_swarm_demo.py` - interactive demos of agent coordination
- **Minimal Demo**: `examples/demo_minimal.py` - shows the pattern without dependencies

## Key Design Decisions

### What Each Agent Provides:
1. **StateEnum** - Enum defining the agent's lifecycle states
2. **TRIGGER_MAP** - Dict mapping span keywords to handler methods
3. **@trigger methods** - State transition handlers that process spans
4. **LISTEN_FILTER** (optional) - Span name prefix for filtering

### What the Base Class Handles:
- Watching span stream (JSONL file)
- Parsing spans and routing to handlers
- State transitions with span emission
- CLI command execution
- Async/sync operation modes

## Running the Swarm

### Quick Start
```bash
# Terminal 1: Start governance agent
python src/dslmodel/agents/examples/roberts_agent.py

# Terminal 2: Start delivery agent  
python src/dslmodel/agents/examples/scrum_agent.py

# Terminal 3: Start optimization agent
python src/dslmodel/agents/examples/lean_agent.py

# Terminal 4: Trigger initial event
echo '{"name": "swarmsh.roberts.vote", "trace_id": "t1", "span_id": "s1", "timestamp": 1234567890, "attributes": {"motion_id": "sprint42"}}' >> ~/s2s/agent_coordination/telemetry_spans.jsonl
```

### Demo Script
```bash
# Run interactive demos
python src/dslmodel/agents/run_swarm_demo.py ping      # Simple ping-pong
python src/dslmodel/agents/run_swarm_demo.py governance # Roberts Rules workflow
python src/dslmodel/agents/run_swarm_demo.py full      # Full cycle demo
```

## Architecture Benefits

1. **Decoupled** - Agents communicate only through spans, no direct dependencies
2. **Extensible** - New agents just need StateEnum + TRIGGER_MAP + handlers
3. **Observable** - All coordination visible in span stream
4. **Testable** - Each agent can be tested in isolation
5. **Scalable** - Agents can run on different machines watching same stream

## Next Steps

To extend this system:
1. Add more agents (Sales, Marketing, HR, etc.)
2. Implement span persistence/querying
3. Add agent health monitoring
4. Create visual span flow diagrams
5. Integrate with real OpenTelemetry collectors

The 80/20 implementation provides a solid foundation for span-driven agent coordination with minimal complexity.