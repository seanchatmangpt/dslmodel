# DSL Capabilities Command

## Overview
The `capabilities` command manages system capabilities, providing comprehensive capability discovery, registration, and management.

## Usage
```bash
# List all capabilities
dsl capabilities list

# Show capability details
dsl capabilities show

# Register new capability
dsl capabilities register

# Update capability
dsl capabilities update

# Remove capability
dsl capabilities remove

# Test capability
dsl capabilities test

# Validate capability
dsl capabilities validate

# Export capabilities
dsl capabilities export

# Import capabilities
dsl capabilities import

# Show capability status
dsl capabilities status
```

## Subcommands

### list
List all available capabilities:
```bash
dsl capabilities list
```

### show
Show detailed information about a capability:
```bash
dsl capabilities show --name "telemetry-processing"
```

### register
Register a new capability:
```bash
dsl capabilities register --name "new-capability" --description "Description" --version "1.0.0"
```

### update
Update an existing capability:
```bash
dsl capabilities update --name "existing-capability" --version "2.0.0"
```

### remove
Remove a capability:
```bash
dsl capabilities remove --name "obsolete-capability"
```

### test
Test a capability:
```bash
dsl capabilities test --name "telemetry-processing"
```

### validate
Validate capability configuration:
```bash
dsl capabilities validate --name "autonomous-system"
```

### export
Export capabilities to file:
```bash
dsl capabilities export --output "capabilities.json"
```

### import
Import capabilities from file:
```bash
dsl capabilities import --file "capabilities.json"
```

### status
Show capability status:
```bash
dsl capabilities status
```

## Capability Types
- **Core Capabilities**: Essential system functions
- **Extension Capabilities**: Optional system extensions
- **Integration Capabilities**: External system integrations
- **Security Capabilities**: Security and compliance features

## Context
The capabilities system provides comprehensive management of system capabilities, enabling dynamic capability discovery, registration, and lifecycle management. 