# Swarm Coordination CLI

80/20 implementation of SwarmSH-inspired agent coordination system for DSLModel.

## Overview

This implementation focuses on the core 20% of features that provide 80% of the value:
- Agent management
- Work queue coordination
- JSON-based persistence
- Basic telemetry tracking
- Simple state management

## Quick Start

### Using Poetry Tasks (poe)

```bash
# Run demo
poe swarm-demo

# Initialize swarm with agents and work
poe swarm-init

# Run a complete work cycle
poe swarm-cycle

# Show status
poe swarm-status

# Clean up data
poe swarm-clean
```

### Direct CLI Usage

```bash
# Create agents
python -m dslmodel.cli.swarm create-agent "Agent_Alpha" --team alpha
python -m dslmodel.cli.swarm create-agent "Agent_Beta" --team beta

# Assign work
python -m dslmodel.cli.swarm assign "Analyze system logs" --priority high
python -m dslmodel.cli.swarm assign "Generate report" --priority medium

# Process work queue
python -m dslmodel.cli.swarm process

# Check status
python -m dslmodel.cli.swarm status

# View telemetry
python -m dslmodel.cli.swarm telemetry --last 10

# Complete work
python -m dslmodel.cli.swarm complete work_12345

# Run dashboard
python -m dslmodel.cli.swarm dashboard
```

## Core Features

### 1. Agent Management
- Create agents with nanosecond-precision IDs
- Assign agents to teams
- Track agent status (idle/working)
- Monitor work completion metrics

### 2. Work Queue
- Priority-based work assignment
- Atomic file operations for consistency
- Work states: pending → in_progress → completed
- Team-based work routing

### 3. JSON Coordination
- Atomic reads/writes with backup
- File-based persistence in `./swarm_data/`
- No external database required

### 4. Telemetry
- Event logging for all operations
- Rolling window of 1000 events
- Performance tracking built-in

## Integration with FSM

The swarm system integrates with DSLModel's FSMMixin for advanced state management:

```python
from dslmodel.examples.swarm_fsm_integration import SwarmCoordinator

# Create coordinator
coordinator = SwarmCoordinator()

# Add FSM-managed agents
coordinator.add_agent("Agent_Alpha", team="alpha")

# Add FSM-managed work
coordinator.add_work("Implement feature X", priority="high")

# Process with state transitions
coordinator.process_cycle()
```

## Architecture

```
swarm_data/
├── agents.json       # Agent registry
├── work_queue.json   # Work items
├── teams.json        # Team definitions
└── telemetry.json    # Event log
```

## Poe Tasks Reference

| Task | Description | Example |
|------|-------------|---------|
| `swarm` | Run CLI | `poe swarm` |
| `swarm-demo` | Full demo | `poe swarm-demo` |
| `swarm-status` | Show status | `poe swarm-status` |
| `swarm-agent` | Create agent | `poe swarm-agent "Bob" --team alpha` |
| `swarm-work` | Assign work | `poe swarm-work "Fix bug" -p high` |
| `swarm-process` | Process queue | `poe swarm-process` |
| `swarm-dashboard` | Live view | `poe swarm-dashboard` |
| `swarm-telemetry` | Show events | `poe swarm-telemetry -n 20` |
| `swarm-complete` | Complete work | `poe swarm-complete work_123` |
| `swarm-init` | Initialize | `poe swarm-init` |
| `swarm-cycle` | Run cycle | `poe swarm-cycle` |
| `swarm-clean` | Clean data | `poe swarm-clean` |

## Key Differences from SwarmSH

This 80/20 implementation simplifies:
- No bash scripts (pure Python)
- No distributed locking (file-based coordination)
- Simplified telemetry (JSON vs OpenTelemetry)
- Basic work assignment (no complex algorithms)
- Focused feature set (core functionality only)

## Extension Points

The system is designed for easy extension:
- Custom work assignment algorithms
- Advanced telemetry integration
- Multi-node coordination
- Real-time monitoring
- AI-driven work routing

## Performance

- Sub-second agent creation
- Instant work assignment
- Minimal memory footprint
- No external dependencies for core features