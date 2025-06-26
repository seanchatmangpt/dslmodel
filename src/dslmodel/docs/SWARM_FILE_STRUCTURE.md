# SwarmAgent File Structure

## Overview

All SwarmAgent files have been moved to the proper location within `/Users/sac/dev/dslmodel/src/dslmodel/`.

## Directory Structure

```
/Users/sac/dev/dslmodel/src/dslmodel/
├── agents/                          # SwarmAgent implementations
│   ├── swarm/                       # Core SwarmAgent framework
│   │   ├── __init__.py              # Package exports
│   │   ├── swarm_agent.py           # Base SwarmAgent class
│   │   ├── swarm_models.py          # Pydantic models
│   │   └── README.md                # Framework documentation
│   ├── examples/                    # Agent implementations
│   │   ├── ping_agent.py            # Simple ping-pong agent
│   │   ├── roberts_agent.py         # Roberts Rules governance
│   │   ├── scrum_agent.py           # Scrum delivery framework
│   │   ├── lean_agent.py            # Lean Six Sigma optimization
│   │   ├── demo_minimal.py          # Pattern demonstration
│   │   └── weaver_demo.py           # Weaver integration demo
│   ├── run_swarm_demo.py           # Interactive demo script
│   ├── test_swarm_agents.py        # Test harness
│   ├── validate_weaver.py          # Weaver validation
│   ├── README.md                   # SwarmAgent overview
│   └── WEAVER_INTEGRATION.md       # Weaver integration docs
├── commands/                        # CLI commands
│   ├── swarm.py                    # Full-featured CLI
│   └── swarm_standalone.py         # Dependency-free CLI
├── otel/                           # OpenTelemetry integration
│   └── models/
│       └── swarm_attributes.py     # Generated Weaver models
├── weaver/                         # Weaver integration
│   ├── __init__.py                 # Package exports and paths
│   ├── weaver.yaml                 # Main Weaver config
│   ├── registry/                   # Semantic conventions
│   │   ├── swarm_agents.yaml       # SwarmAgent conventions
│   │   ├── dslmodel.yaml           # DSLModel conventions
│   │   └── registry_manifest.yaml  # Registry metadata
│   └── templates/                  # Code generation templates
│       └── registry/
│           ├── python/             # Python templates
│           │   ├── swarm_attributes.j2
│           │   ├── pydantic_model.j2
│           │   └── metric_dataclass.j2
│           └── docs/               # Documentation templates
│               └── attributes.md.j2
└── docs/                           # Documentation
    ├── SWARM_IMPLEMENTATION.md     # Implementation overview
    ├── WEAVER_INTEGRATION.md       # Weaver integration guide
    ├── WEAVER_FSM_INTEGRATION.md   # FSM integration
    ├── CLI_INTEGRATION_SUMMARY.md  # CLI integration
    └── SWARM_FILE_STRUCTURE.md     # This file
```

## Key Integration Points

### 1. CLI Integration
- **Main CLI**: `dsl swarm` via `commands/swarm.py`
- **Standalone**: `python commands/swarm_standalone.py`
- **Package export**: Registered in `cli.py`

### 2. OpenTelemetry/Weaver
- **Semantic conventions**: `weaver/registry/swarm_agents.yaml`
- **Generated models**: `otel/models/swarm_attributes.py`
- **Templates**: `weaver/templates/`
- **Validation**: `agents/validate_weaver.py`

### 3. Agent Framework
- **Base class**: `agents/swarm/swarm_agent.py`
- **Models**: `agents/swarm/swarm_models.py`
- **Examples**: `agents/examples/`
- **Tests**: `agents/test_swarm_agents.py`

## File Movements Completed

### Moved to `src/dslmodel/docs/`:
- `SWARM_IMPLEMENTATION.md` → `docs/SWARM_IMPLEMENTATION.md`
- `WEAVER_INTEGRATION.md` → `docs/WEAVER_INTEGRATION.md`
- `WEAVER_FSM_INTEGRATION.md` → `docs/WEAVER_FSM_INTEGRATION.md`
- `CLI_INTEGRATION_SUMMARY.md` → `docs/CLI_INTEGRATION_SUMMARY.md`

### Moved to `src/dslmodel/weaver/`:
- `weaver.yaml` → `weaver/weaver.yaml`
- `weaver_templates/` → `weaver/templates/`
- `semconv_registry/` → `weaver/registry/`

### Already in correct locations:
- All agent implementations in `agents/`
- CLI commands in `commands/`
- Generated models in `otel/models/`

## Package Access

### Import Paths
```python
# SwarmAgent framework
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData

# Agent examples
from dslmodel.agents.examples.roberts_agent import RobertsAgent

# Generated Weaver models
from dslmodel.otel.models.swarm_attributes import SwarmSpanAttributes

# Weaver paths
from dslmodel.weaver import REGISTRY_PATH, TEMPLATES_PATH
```

### CLI Access
```bash
# Main CLI
dsl swarm status
dsl swarm start roberts
dsl swarm emit 'swarmsh.roberts.vote'

# Standalone
python -m dslmodel.commands.swarm_standalone status

# Poetry tasks
poe swarm-status
poe swarm-demo
```

## Benefits of Proper Structure

1. **Package coherence**: All files in proper Python package structure
2. **Import consistency**: Standard dslmodel.* import paths
3. **CLI integration**: Seamless integration with main dsl command
4. **Documentation centralization**: All docs in one location
5. **Weaver organization**: Semantic conventions and templates together
6. **Development workflow**: Clear separation of concerns

All SwarmAgent functionality is now properly integrated within the dslmodel package structure and ready for production use.