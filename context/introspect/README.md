# DSL Introspect Command

## Overview
The `introspect` command provides comprehensive system introspection capabilities for debugging, monitoring, and analysis.

## Usage
```bash
# Show system introspection
dsl introspect system

# Show agent introspection
dsl introspect agent

# Show telemetry introspection
dsl introspect telemetry

# Show worktree introspection
dsl introspect worktree

# Show capability introspection
dsl introspect capabilities

# Show security introspection
dsl introspect security

# Show performance introspection
dsl introspect performance

# Generate introspection report
dsl introspect report

# Run introspection demo
dsl introspect demo
```

## Subcommands

### system
Show system introspection:
```bash
dsl introspect system
```

### agent
Show agent introspection:
```bash
dsl introspect agent --agent-id "agent-123"
```

### telemetry
Show telemetry introspection:
```bash
dsl introspect telemetry --duration 300
```

### worktree
Show worktree introspection:
```bash
dsl introspect worktree --worktree-name "feature-auth"
```

### capabilities
Show capability introspection:
```bash
dsl introspect capabilities --capability "telemetry-processing"
```

### security
Show security introspection:
```bash
dsl introspect security --scan-type "vulnerability"
```

### performance
Show performance introspection:
```bash
dsl introspect performance --metrics "response-time,throughput"
```

### report
Generate comprehensive introspection report:
```bash
dsl introspect report --output "introspection_report.json"
```

### demo
Run introspection demonstration:
```bash
dsl introspect demo
```

## Introspection Features
- **System Analysis**: Comprehensive system state analysis
- **Performance Monitoring**: Real-time performance metrics
- **Security Assessment**: Security posture evaluation
- **Debugging Support**: Detailed debugging information

## Context
The introspection system provides deep visibility into system internals, enabling effective debugging, monitoring, and optimization of DSLModel components. 