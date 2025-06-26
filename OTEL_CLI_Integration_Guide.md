# OpenTelemetry CLI Integration with DSLModel

## Overview

This guide demonstrates the successful integration of OpenTelemetry observability features with the existing DSLModel pyproject.toml CLI structure. The integration provides full OTEL capabilities while maintaining backward compatibility with the existing coordination system.

## 🎯 Integration Architecture

```
DSLModel CLI Structure
├── dsl (main CLI entry)
│   ├── coord (existing coordination)
│   ├── otel (OTEL-enhanced coordination) ✨ NEW
│   ├── swarm (swarm agents)
│   ├── forge (weaver forge)
│   └── auto (autonomous engine)
└── Poetry Tasks (poe)
    ├── existing tasks
    └── otel-* tasks ✨ NEW
```

## 📁 Files Created/Modified

### New Files
1. **`src/dslmodel/commands/otel_coordination.py`** - OTEL-enhanced coordination CLI
2. **`test_cli_integration.py`** - Integration test suite
3. **`OTEL_CLI_Integration_Guide.md`** - This documentation

### Modified Files
1. **`src/dslmodel/cli.py`** - Added OTEL coordination to main CLI
2. **`src/dslmodel/commands/__init__.py`** - Added OTEL module imports
3. **`pyproject.toml`** - Added OTEL dependencies and Poetry tasks

## 🚀 Usage Examples

### Using the dsl CLI

```bash
# Check OTEL status
dsl otel otel status

# Create work with full OTEL tracing
dsl otel work claim bug "Memory leak" --priority critical --story-points 5

# List work with trace information
dsl otel work list --show-traces

# Generate test traces
dsl otel otel test-trace

# Complete work with telemetry
dsl otel work complete WORK-123 --score 8
```

### Using Poetry Tasks

```bash
# Install OTEL dependencies
poe otel-install

# Check OTEL status
poe otel-status

# Run demo workflow
poe otel-demo

# Create work with tracing
poe otel-work

# List work with traces
poe otel-list
```

## 🔧 Key Features

### 1. **Graceful Fallback**
- Works without OTEL dependencies installed
- Uses mock objects when OpenTelemetry is unavailable
- Maintains full CLI functionality

### 2. **Semantic Conventions**
```python
class CoordinationAttributes:
    WORK_ID = "coordination.work.id"
    WORK_TYPE = "coordination.work.type"
    WORK_PRIORITY = "coordination.work.priority"
    WORK_TEAM = "coordination.work.team"
    # ... more conventions
```

### 3. **Context Propagation**
```python
@contextmanager
def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Enhanced tracing with metrics and context propagation"""
    with tracer.start_as_current_span(f"dslmodel.coordination.{name}") as span:
        # Automatic attribute setting
        # Baggage propagation
        # Metrics recording
        yield span
```

### 4. **Comprehensive Metrics**
- `dslmodel.coordination.work_items.created` - Counter
- `dslmodel.coordination.work_items.completed` - Counter  
- `dslmodel.coordination.work_item.duration` - Histogram
- `dslmodel.coordination.api.latency` - Histogram

## 📦 pyproject.toml Configuration

### Dependencies
```toml
# OpenTelemetry dependencies (optional)
opentelemetry-api = { version = "^1.20.0", optional = true }
opentelemetry-sdk = { version = "^1.20.0", optional = true }
opentelemetry-exporter-otlp = { version = "^1.20.0", optional = true }
opentelemetry-instrumentation = { version = "^0.41b0", optional = true }
opentelemetry-semantic-conventions = { version = "^0.41b0", optional = true }

[tool.poetry.extras]
otel = [
    "opentelemetry-api",
    "opentelemetry-sdk", 
    "opentelemetry-exporter-otlp",
    "opentelemetry-instrumentation",
    "opentelemetry-semantic-conventions"
]
```

### Poetry Tasks
```toml
[tool.poe.tasks.otel-status]
help = "Show OpenTelemetry status"
cmd = "dsl otel otel status"

[tool.poe.tasks.otel-demo]
help = "Run OTEL coordination demo"
sequence = [
    { cmd = "dsl otel init" },
    { cmd = "dsl otel work claim bug 'Memory leak' --priority critical --team backend" },
    { cmd = "dsl otel work list --show-traces" }
]
```

## 🔍 CLI Command Structure

### Main CLI (`dsl`)
```
dsl --help
├── gen                    # Generate DSLModel classes
├── openapi               # Generate from OpenAPI
├── asyncapi              # AsyncAPI commands
├── slidev                # Slidev presentations
├── coord                 # Basic coordination
├── otel                  # OTEL-enhanced coordination ✨
├── forge                 # Weaver forge
├── auto                  # Autonomous engine
└── swarm                 # Swarm agents
```

### OTEL Sub-commands (`dsl otel`)
```
dsl otel --help
├── work                  # Work management with OTEL
│   ├── claim            # Claim work with tracing
│   ├── list             # List with trace info
│   ├── complete         # Complete with metrics
│   ├── stats            # Statistics
│   └── progress         # Update progress
├── otel                  # OTEL operations
│   ├── status           # Show OTEL status
│   ├── test-trace       # Generate test trace
│   └── export-spans     # Export spans
├── agent                 # Agent management
│   ├── list             # List agents
│   └── run              # Run agent
├── init                  # Initialize
└── reset                 # Reset environment
```

## 🎯 Integration Benefits

### 1. **Unified CLI Experience**
- Single `dsl` entry point for all functionality
- Consistent command structure across modules
- Backward compatibility with existing commands

### 2. **Optional OTEL Features**
- Core functionality works without OTEL dependencies
- Enhanced features available with `pip install dslmodel[otel]`
- Graceful degradation when OTEL not available

### 3. **Production Ready**
- Proper semantic conventions
- Context propagation for distributed tracing
- Comprehensive metrics collection
- Poetry task automation

### 4. **Developer Experience**
- Rich CLI help and documentation
- Type-safe configuration
- Easy testing and validation

## 🚀 Getting Started

### 1. Basic Usage (no OTEL dependencies)
```bash
# Works immediately
dsl otel work claim bug "Simple bug"
dsl otel work list
```

### 2. Full OTEL Features
```bash
# Install OTEL dependencies
pip install dslmodel[otel]
# or
poe otel-install

# Set OTEL endpoint (optional)
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Use enhanced features
dsl otel work claim bug "Traced bug" --priority high
dsl otel otel test-trace
```

### 3. Development Workflow
```bash
# Quick demo
poe otel-demo

# Check status
poe otel-status

# Create and track work
poe otel-work
poe otel-list
```

## 🧪 Testing

### Integration Tests
```bash
python test_cli_integration.py
```

Tests verify:
- Module imports work correctly
- CLI command structure is proper
- OTEL integration functions
- pyproject.toml configuration
- Fallback behavior when OTEL unavailable

### Expected Results
- ✅ pyproject.toml configuration correct
- ✅ CLI structure properly integrated
- ✅ Graceful fallback working
- ⚠️ Full features require OTEL dependencies

## 📊 Observability Features

### Traces
- **Span Names**: `dslmodel.coordination.*`
- **Attributes**: Work type, priority, team, business context
- **Context Propagation**: Via W3C headers and baggage
- **Trace Links**: Connect work creation to completion

### Metrics
- **Counters**: Work items created/completed by team/priority
- **Histograms**: Work duration, API latency
- **Gauges**: Active work items, capacity utilization

### Logs
- **Structured Logging**: JSON format with trace correlation
- **Business Context**: Work IDs, teams, priorities embedded
- **Error Tracking**: Exceptions automatically captured

## 🔄 Future Enhancements

### Planned Features
1. **Dashboard Integration**: Grafana dashboards from Poetry tasks
2. **Alert Configuration**: Automated SLO monitoring setup
3. **Workflow Automation**: OTEL-driven optimization loops
4. **Service Mesh**: Istio/Envoy integration examples

### Extension Points
1. **Custom Exporters**: For proprietary monitoring systems
2. **Additional Metrics**: Business-specific KPIs
3. **Trace Sampling**: Intelligent sampling strategies
4. **Resource Detection**: Auto-detect cloud environments

## ✨ Conclusion

The OTEL CLI integration successfully enhances the DSLModel coordination system with world-class observability features while maintaining the existing developer experience. The integration demonstrates:

- **Seamless Integration** with existing CLI structure
- **Progressive Enhancement** through optional dependencies
- **Production Readiness** with proper conventions and practices
- **Developer Productivity** through Poetry task automation

This approach provides a foundation for advanced observability practices while ensuring backward compatibility and ease of adoption.