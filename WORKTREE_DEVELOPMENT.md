# DSLModel E2E Worktree Development Guide

## Overview

This guide describes the worktree-based development workflow for DSLModel E2E features. Using Git worktrees allows us to develop multiple features in parallel while maintaining clean separation and easy E2E validation.

## Worktree Structure

```
~/dev/
├── dslmodel/                       # Main repository
└── dslmodel-worktrees/            # Worktree directory
    ├── swarmsh-core/              # Core SwarmSH coordination engine
    ├── enterprise-coordination/    # Roberts/Scrum/Lean implementations
    ├── weaver-fsm-integration/    # Weaver + FSM integration
    ├── otel-telemetry/           # OpenTelemetry instrumentation
    ├── demo-engine/              # Demo generation system
    ├── productization/           # Sales & packaging features
    └── scripts/                  # Cross-worktree utilities
```

## Feature Branches

### 1. `feature/swarmsh-core`
**Purpose**: Core coordination engine implementation
- Coordination CLI
- Conflict-free data structures
- Shell export functionality
- Work item management

### 2. `feature/enterprise-coordination`
**Purpose**: Enterprise framework implementations
- Roberts Rules of Order engine
- Scrum at Scale coordination
- Lean Six Sigma process automation
- Unified coordination metrics

### 3. `feature/weaver-fsm-integration`
**Purpose**: Type-safe state machines with observability
- FSMMixin enhancements
- Weaver Forge integration
- Observable state transitions
- Semantic convention generation

### 4. `feature/otel-telemetry`
**Purpose**: Full observability stack
- OpenTelemetry integration
- Span/metric generation
- Distributed tracing
- Compliance audit trails

### 5. `feature/demo-engine`
**Purpose**: Automated demo generation
- Customer context analysis
- Chaos scenario generation
- Resolution demonstrations
- ROI calculation

### 6. `feature/productization`
**Purpose**: Sales and packaging features
- Pricing tiers
- License management
- Customer onboarding
- Documentation generation

## Development Workflow

### Initial Setup

```bash
# Run the setup script to create all worktrees
./scripts/setup_worktree_e2e.sh

# Open VS Code with multi-root workspace
code ~/dev/dslmodel-worktrees/dslmodel-e2e.code-workspace
```

### Daily Development

1. **Choose your worktree** based on the feature you're developing:
   ```bash
   cd ~/dev/dslmodel-worktrees/swarmsh-core
   ```

2. **Sync with main** before starting work:
   ```bash
   ~/dev/dslmodel-worktrees/scripts/sync_worktrees.sh
   ```

3. **Develop your feature** with E2E validation in mind:
   ```bash
   # Make changes
   vim src/dslmodel/...
   
   # Run E2E demo to validate
   poetry run python src/dslmodel/examples/enterprise_demo_minimal.py
   ```

4. **Test across worktrees** to ensure integration:
   ```bash
   ~/dev/dslmodel-worktrees/scripts/run_e2e_tests.sh
   ```

5. **Check worktree status** before committing:
   ```bash
   ~/dev/dslmodel-worktrees/scripts/worktree_status.sh
   ```

### E2E Validation Pattern

Each feature should include:

1. **Unit tests** in `tests/test_<feature>.py`
2. **Integration tests** that validate cross-feature functionality
3. **E2E demo** that shows real-world usage
4. **Performance benchmarks** with measurable metrics

Example E2E test structure:
```python
# tests/test_e2e_coordination.py
import pytest
from dslmodel.examples.enterprise_demo_minimal import run_enterprise_demo

@pytest.mark.asyncio
async def test_enterprise_coordination_e2e():
    """Full E2E test of enterprise coordination features."""
    results = await run_enterprise_demo("Test Corp")
    
    # Validate Roberts Rules improvements
    assert results['roberts_metrics']['meeting_efficiency'] == "76% time reduction"
    
    # Validate Scrum metrics
    assert "42% → 8%" in results['scrum_metrics']['ceremony_overhead']
    
    # Validate Lean Six Sigma ROI
    assert "+$4.7M" in results['lean_metrics']['roi_improvement']
    
    # Validate overall coordination
    assert results['coordination_improvement']['overall_coordination_efficiency'] > 0.75
```

## Best Practices

### 1. **Feature Isolation**
- Keep features focused and independent
- Use worktrees to avoid branch pollution
- Merge to main only after E2E validation

### 2. **Cross-Feature Testing**
- Always run E2E tests before pushing
- Test integration points between features
- Validate performance impact

### 3. **Documentation**
- Update feature docs in each worktree
- Include E2E examples for new features
- Document integration points

### 4. **Performance Tracking**
- Benchmark critical paths
- Use OTEL spans for performance analysis
- Document performance characteristics

## Merging Strategy

1. **Feature Complete**: Ensure all E2E tests pass
2. **Sync with Main**: Resolve any conflicts
3. **Create PR**: With E2E validation results
4. **Peer Review**: Focus on integration impacts
5. **Merge**: After approval and CI passes

## Troubleshooting

### Worktree Issues
```bash
# List all worktrees
git worktree list

# Remove broken worktree
git worktree remove <path> --force

# Prune stale worktree info
git worktree prune
```

### Poetry Environment Issues
```bash
# Recreate virtual environment in worktree
cd ~/dev/dslmodel-worktrees/<feature>
poetry env remove python
poetry install
```

### E2E Test Failures
1. Check Ollama is running: `ollama list`
2. Verify environment variables are set
3. Run individual demos to isolate issues
4. Check logs in `.pytest_cache/`

## CI/CD Integration

Each push to a feature branch triggers:
1. Unit tests for that feature
2. Integration tests with main
3. E2E demo execution
4. Performance benchmarks
5. Documentation build

## Release Process

1. **Feature Freeze**: Lock worktree branches
2. **Integration Testing**: Full E2E suite
3. **Performance Validation**: Benchmark suite
4. **Documentation Update**: Generate from demos
5. **Release Tag**: After all validations pass

---

## Quick Commands

```bash
# Setup all worktrees
./scripts/setup_worktree_e2e.sh

# Check status across all worktrees
~/dev/dslmodel-worktrees/scripts/worktree_status.sh

# Run E2E tests everywhere
~/dev/dslmodel-worktrees/scripts/run_e2e_tests.sh

# Sync all worktrees with main
~/dev/dslmodel-worktrees/scripts/sync_worktrees.sh

# Open multi-root workspace
code ~/dev/dslmodel-worktrees/dslmodel-e2e.code-workspace
```

Ready for parallel E2E feature development! 🚀