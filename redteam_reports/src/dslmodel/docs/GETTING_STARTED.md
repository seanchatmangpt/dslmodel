# Getting Started with SwarmAgent

## Prerequisites

- Python 3.12+
- Basic understanding of OpenTelemetry concepts
- Familiarity with command-line interfaces

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install dslmodel[otel]
```

### Option 2: Development Installation
```bash
git clone https://github.com/seanchatmangpt/dslmodel.git
cd dslmodel
poetry install --extras otel
```

## Verification

Verify installation:
```bash
dsl swarm --help
```

Expected output:
```
Usage: dsl swarm [OPTIONS] COMMAND [ARGS]...

  SwarmAgent coordination and management

Commands:
  demo     Run demonstration workflows
  emit     Emit coordination spans
  monitor  Monitor agent coordination
  start    Start specific agents
  status   Show system status
  validate Validate span schemas
```

## Quick Start Tutorial

### Step 1: Check System Status
```bash
dsl swarm status
```

This shows:
- Coordination directory location
- Available agents
- Recent span activity

### Step 2: Run Your First Demo
```bash
dsl swarm demo ping
```

This demonstrates basic agent coordination with a simple ping workflow.

### Step 3: Start Agent Services
```bash
# Start governance agent
dsl swarm start roberts --background

# Start delivery agent  
dsl swarm start scrum --background

# Start optimization agent
dsl swarm start lean --background
```

### Step 4: Trigger a Governance Workflow
```bash
# Open a motion for sprint planning
dsl swarm emit 'swarmsh.roberts.open' --attrs '{"motion_id": "sprint_42", "meeting_id": "board_q1"}'

# Vote on the motion
dsl swarm emit 'swarmsh.roberts.vote' --attrs '{"motion_id": "sprint_42", "voting_method": "ballot"}'

# Close motion with result
dsl swarm emit 'swarmsh.roberts.close' --attrs '{"motion_id": "sprint_42", "vote_result": "passed"}'
```

### Step 5: Monitor the Coordination
```bash
dsl swarm monitor --follow
```

You'll see:
- Roberts agent processing governance events
- Scrum agent automatically triggered for sprint planning
- Lean agent monitoring for optimization opportunities

## Understanding the Output

### Span Format
Each coordination event is an OpenTelemetry span:
```json
{
  "name": "swarmsh.roberts.vote",
  "trace_id": "trace_1234567890",
  "span_id": "span_9876543210", 
  "timestamp": 1750925395.778377,
  "attributes": {
    "motion_id": "sprint_42",
    "voting_method": "ballot"
  }
}
```

### Agent States
Agents follow finite state machines:

**Roberts Agent (Governance)**:
- IDLE → MOTION_OPEN → VOTING → CLOSED

**Scrum Agent (Delivery)**:
- IDLE → PLANNING → SPRINT_ACTIVE → REVIEW

**Lean Agent (Optimization)**:
- IDLE → DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL

## Common Workflows

### Governance → Delivery
1. Motion proposed → Roberts IDLE → MOTION_OPEN
2. Vote called → Roberts MOTION_OPEN → VOTING  
3. Motion passes → Roberts VOTING → CLOSED
4. Sprint triggered → Scrum IDLE → PLANNING

### Quality Issues → Optimization
1. Sprint review detects defects → Scrum REVIEW
2. Defect rate > threshold → Lean IDLE → DEFINE
3. Lean Six Sigma project initiated

### Manual Coordination
```bash
# Direct scrum planning
dsl swarm emit 'swarmsh.scrum.plan' --attrs '{"sprint_number": "43", "team_id": "alpha"}'

# Direct lean project
dsl swarm emit 'swarmsh.lean.define' --attrs '{"project_id": "efficiency", "problem_statement": "Response time > 500ms"}'
```

## Validation

### Verify Spans Are Valid
```bash
dsl swarm validate
```

### Check Weaver Compliance
```bash
weaver registry check -r src/dslmodel/weaver/registry/
```

### Run Full Demo
```bash
dsl swarm demo full
```

## Troubleshooting

### Common Issues

**"No coordination directory found"**
```bash
# Initialize coordination
mkdir -p ~/.swarm_coordination
export SWARM_ROOT_DIR=~/.swarm_coordination
```

**"Faker module not found"** 
```bash
# Install missing dependency
pip install faker
```

**"Agents not responding"**
```bash
# Check agent status
dsl swarm status

# Restart agents
dsl swarm start roberts --background
```

### Debug Mode
```bash
# Enable verbose logging
export SWARM_DEBUG=1
dsl swarm monitor --follow
```

## Next Steps

1. **[Architecture Overview](ARCHITECTURE.md)** - Understand the system design
2. **[Custom Agents](CUSTOM_AGENTS.md)** - Build your own agents
3. **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Deploy in production
4. **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Validate system performance

## Examples

See working examples in:
- `src/dslmodel/agents/examples/` - Agent implementations
- `dsl swarm demo --help` - Built-in demonstrations
- [GitHub Examples](https://github.com/seanchatmangpt/dslmodel/tree/main/examples)

## Support

- **Documentation**: This docs directory
- **CLI Help**: `dsl swarm --help`  
- **Issues**: [GitHub Issues](https://github.com/seanchatmangpt/dslmodel/issues)