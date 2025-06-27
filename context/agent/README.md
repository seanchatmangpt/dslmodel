# DSL Agent Command

## Overview
The `agent` command manages agent coordination with exclusive worktrees and OpenTelemetry communication for distributed development workflows.

## Usage
```bash
# Initialize agent coordination system
dsl agent init

# Register new agent with capabilities
dsl agent register-agent

# Add feature request to development queue
dsl agent add-feature

# Assign best matching feature to agent
dsl agent assign-work

# Show agent status
dsl agent agent-status

# Run coordination cycles
dsl agent coordination-cycle

# Run complete demonstration
dsl agent demo

# Show worktree status
dsl agent worktree-status
```

## Subcommands

### init
Initialize the agent coordination system:
```bash
dsl agent init
```

### register-agent
Register a new agent with specific capabilities:
```bash
dsl agent register-agent --name "backend-agent" --capabilities "api-development,testing"
```

### add-feature
Add a feature request to the development queue:
```bash
dsl agent add-feature --description "Implement user authentication" --priority high
```

### assign-work
Assign best matching feature to an available agent:
```bash
dsl agent assign-work
```

### agent-status
Show status of all agents in the coordination system:
```bash
dsl agent agent-status
```

### coordination-cycle
Run coordination cycle(s) to assign work and monitor progress:
```bash
dsl agent coordination-cycle --cycles 5
```

### demo
Run complete agent coordination demonstration:
```bash
dsl agent demo
```

### worktree-status
Show status of all managed worktrees:
```bash
dsl agent worktree-status
```

## Agent Types
- **Development Agents**: Code generation and implementation
- **Testing Agents**: Automated testing and validation
- **Deployment Agents**: CI/CD and deployment automation
- **Security Agents**: Security scanning and compliance

## Context
The agent system provides distributed, autonomous development capabilities with telemetry-driven coordination and exclusive worktree management. 