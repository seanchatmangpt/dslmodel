# Hygen Templates for SwarmAgent Ecosystem

This directory contains Hygen templates for rapidly scaffolding new components in the SwarmAgent ecosystem. Each template is designed to generate production-ready code with full integration into the existing architecture.

## 📁 Available Templates

### 1. `swarm-agent` - SwarmAgent Components
Generate new SwarmAgent implementations with FSM integration and OpenTelemetry support.

```bash
# Generate a new monitoring agent
hygen swarm-agent new

# Example prompts:
# Name: Monitoring
# States: IDLE,WATCHING,ALERTING,REPORTING
# Triggers: start,detect,alert,report
```

**Generated files:**
- `src/dslmodel/agents/examples/monitoring_agent.py` - Agent implementation
- `src/dslmodel/agents/tests/test_monitoring_agent.py` - Test suite

### 2. `swarm-workflow` - Multi-Agent Workflows
Create complete workflow orchestrations with multiple agents.

```bash
# Generate a deployment workflow
hygen swarm-workflow new

# Example prompts:
# Name: deployment
# Agents: validator,deployer,monitor
# Steps: 5
# Include rollback: yes
```

**Generated files:**
- `src/dslmodel/workflows/deployment_workflow.py` - Workflow implementation

### 3. `otel-integration` - OpenTelemetry Integration
Add custom telemetry with exporters and processors.

```bash
# Generate metrics telemetry
hygen otel-integration new

# Example prompts:
# Name: Metrics
# Signal type: metrics
# Custom exporter: yes
```

**Generated files:**
- `src/dslmodel/otel/metrics_telemetry.py` - OTEL integration

### 4. `cli-command` - CLI Commands
Create new CLI commands with Rich formatting.

```bash
# Generate analyze command
hygen cli-command new

# Example prompts:
# Name: analyze
# Parent command: swarm
# Has subcommands: no
```

**Generated files:**
- `src/dslmodel/commands/swarm_analyze_command.py` - Command implementation

### 5. `fsm-mixin` - State Machine Mixins
Build reusable FSM mixins with advanced features.

```bash
# Generate approval workflow mixin
hygen fsm-mixin new

# Example prompts:
# Name: Approval
# States: PENDING,REVIEWING,APPROVED,REJECTED
# Include timeout: yes
# Include retry: yes
```

**Generated files:**
- `src/dslmodel/mixins/approval_fsm_mixin.py` - FSM mixin

## 🚀 Quick Start

### Installation
```bash
# Install hygen globally
npm install -g hygen

# Or use npx (no installation needed)
npx hygen <template> <action>
```

### Basic Usage
```bash
# Interactive mode - prompts for all options
hygen swarm-agent new

# With predefined values
hygen swarm-agent new --name Analytics --states IDLE,PROCESSING,REPORTING
```

### Batch Generation
```bash
# Generate multiple components for a feature
hygen swarm-agent new --name Auth
hygen swarm-workflow new --name authentication --agents auth,validator,logger
hygen cli-command new --name auth --parent-command swarm
```

## 📋 Template Features

### Common Features Across All Templates
- ✅ **Type hints** and Pydantic models
- ✅ **Comprehensive docstrings**
- ✅ **Error handling** patterns
- ✅ **Logging** integration
- ✅ **Example usage** in `__main__`
- ✅ **Test scaffolding** (where applicable)

### SwarmAgent Features
- State machine with transitions
- OpenTelemetry span processing
- Trigger mapping and decorators
- NextCommand generation
- Status reporting

### Workflow Features
- Multi-step orchestration
- Span emission for coordination
- Progress tracking with Rich
- Dry-run support
- Optional rollback capability

### OTEL Features
- Custom exporters and processors
- Semantic conventions
- Context managers for spans
- Metrics and event tracking
- JSONL export format

### CLI Features
- Typer command structure
- Rich formatted output
- Multiple output formats (table, json, yaml)
- Async command support
- Subcommand groups

### FSM Mixin Features
- State transition callbacks
- Timeout handling
- Retry logic with backoff
- State persistence
- History tracking

## 🔧 Customization

### Modifying Templates
Templates are EJS files located in `_templates/<template-name>/new/`:

1. **index.js** - Defines prompts and data processing
2. **\*.ejs.t** - Template files with EJS syntax

### Adding New Templates
```bash
# Create new template structure
hygen generator new --name my-feature

# Edit the generated files in _templates/my-feature/new/
```

### Template Variables
All templates have access to:
- User inputs from prompts
- Derived values (className, fileName, etc.)
- Helper functions (JSON.stringify, etc.)

## 📚 Examples

### Complete Feature Implementation
```bash
# 1. Create the agent
hygen swarm-agent new \
  --name Scheduler \
  --states IDLE,SCHEDULING,EXECUTING,COMPLETE \
  --triggers schedule,execute,complete

# 2. Create the workflow
hygen swarm-workflow new \
  --name scheduling \
  --agents scheduler,executor,monitor \
  --steps 4

# 3. Add CLI command
hygen cli-command new \
  --name schedule \
  --parent-command swarm \
  --arguments task-name,cron-expression

# 4. Add telemetry
hygen otel-integration new \
  --name Scheduling \
  --signal-type traces \
  --has-exporter yes
```

### Testing Generated Code
```bash
# Run the generated agent
python src/dslmodel/agents/examples/scheduler_agent.py

# Run tests
pytest src/dslmodel/agents/tests/test_scheduler_agent.py

# Test the workflow
python src/dslmodel/workflows/scheduling_workflow.py --dry-run

# Test CLI command
python -m dslmodel.cli swarm schedule "backup" "0 2 * * *"
```

## 🎯 Best Practices

1. **Naming Conventions**
   - Use PascalCase for agent/mixin names
   - Use lowercase for command names
   - Use descriptive state names (ACTIVE not A)

2. **State Design**
   - Always include ERROR state
   - Keep states focused and minimal
   - Use clear transition triggers

3. **Integration**
   - Test generated code immediately
   - Update imports in `__init__.py` files
   - Add to CLI command registry if needed

4. **Documentation**
   - Update component lists after generation
   - Add usage examples to generated code
   - Document any custom modifications

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure generated files are in correct directories
   - Update `__init__.py` files to export new components
   - Check for circular imports

2. **Template Errors**
   - Validate EJS syntax in template files
   - Check for undefined variables in templates
   - Review index.js for data processing issues

3. **Integration Issues**
   - Verify parent commands exist for CLI
   - Ensure state names are valid Python identifiers
   - Check file permissions for generated files

### Getting Help
- Review generated code for TODO comments
- Check template source files for examples
- Run generated example code in `__main__`

## 🔄 Continuous Improvement

These templates are designed to evolve with the project:
- Add new prompts as patterns emerge
- Extract common code into shared templates
- Update templates when base classes change
- Add validation for common mistakes

Remember: Templates are starting points. Always review and customize generated code for your specific needs!