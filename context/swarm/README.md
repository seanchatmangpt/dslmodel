# DSL Swarm Command

## Overview
The `swarm` command manages SwarmAgent coordination and provides comprehensive swarm management capabilities for distributed development.

## Usage
```bash
# Create a new agent
dsl swarm create-agent

# Assign new work to the swarm
dsl swarm assign

# Process work queue
dsl swarm process

# Mark work as completed
dsl swarm complete

# Show swarm status
dsl swarm status

# Show live dashboard
dsl swarm dashboard

# Show telemetry events
dsl swarm telemetry

# Run swarm coordination demo
dsl swarm demo

# Clean swarm data directory
dsl swarm clean

# Initialize swarm with sample data
dsl swarm init

# Run complete full cycle demo
dsl swarm full-cycle

# Show full cycle demo status
dsl swarm full-cycle-status

# Clean all full cycle demo data
dsl swarm full-cycle-clean
```

## Subcommands

### create-agent
Create a new agent with specified capabilities:
```bash
dsl swarm create-agent --name "backend-agent" --capabilities "api,testing"
```

### assign
Assign new work to the swarm:
```bash
dsl swarm assign --work "Implement user authentication" --priority high
```

### process
Process work queue and assign work to agents:
```bash
dsl swarm process
```

### complete
Mark work as completed:
```bash
dsl swarm complete --work-id "work_123"
```

### status
Show current swarm status:
```bash
dsl swarm status
```

### dashboard
Show live dashboard (simplified):
```bash
dsl swarm dashboard
```

### telemetry
Show telemetry events:
```bash
dsl swarm telemetry
```

### demo
Run a demo showing swarm coordination:
```bash
dsl swarm demo
```

### clean
Clean swarm data directory:
```bash
dsl swarm clean
```

### init
Initialize swarm with sample agents and work:
```bash
dsl swarm init
```

## Swarm Architecture
- **Agent Pool**: Collection of available agents
- **Work Queue**: Pending work items
- **Coordination Engine**: Work distribution and monitoring
- **Telemetry Integration**: Real-time monitoring and feedback

## Context
The swarm system provides distributed, autonomous development capabilities with intelligent work distribution and real-time coordination. 