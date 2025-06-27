# DSL Test Command

## Overview
The `test` command provides comprehensive testing capabilities for DSLModel components, including unit tests, integration tests, and performance tests.

## Usage
```bash
# Run all tests
dsl test all

# Run unit tests
dsl test unit

# Run integration tests
dsl test integration

# Run performance tests
dsl test performance

# Run security tests
dsl test security

# Run telemetry tests
dsl test telemetry

# Run agent tests
dsl test agent

# Generate test report
dsl test report

# Run test demo
dsl test demo

# Show test coverage
dsl test coverage
```

## Subcommands

### all
Run all tests:
```bash
dsl test all
```

### unit
Run unit tests:
```bash
dsl test unit --module "dslmodel.core"
```

### integration
Run integration tests:
```bash
dsl test integration --test-suite "agent-coordination"
```

### performance
Run performance tests:
```bash
dsl test performance --duration 300 --concurrent-users 100
```

### security
Run security tests:
```bash
dsl test security --scan-type "vulnerability"
```

### telemetry
Run telemetry tests:
```bash
dsl test telemetry --endpoint "otel-collector"
```

### agent
Run agent tests:
```bash
dsl test agent --agent-type "development"
```

### report
Generate test report:
```bash
dsl test report --output "test_report.html"
```

### demo
Run test demonstration:
```bash
dsl test demo
```

### coverage
Show test coverage:
```bash
dsl test coverage --module "dslmodel.core"
```

## Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: System performance validation
- **Security Tests**: Security vulnerability testing
- **Telemetry Tests**: OpenTelemetry integration testing

## Context
The testing system provides comprehensive validation of DSLModel components, ensuring reliability, performance, and security across all system components. 