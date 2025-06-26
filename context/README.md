# DSLModel Context Documentation v2

This directory contains comprehensive context documentation following the **Codebase Context Specification (CCS) v2.0** with enhanced OpenTelemetry integration and advanced agent coordination capabilities.

## 📁 Directory Structure

```
context/
├── index.md              # Primary context with YAML metadata and overview
├── docs.md               # Detailed technical documentation
├── otel.md               # Complete OpenTelemetry ecosystem documentation
├── diagrams/             # Mermaid diagrams for visual understanding
│   ├── architecture.mmd  # System architecture overview
│   ├── data-flow.mmd     # Data flow and sequence diagrams
│   └── evolution-loop.mmd # Evolution cycle visualization
└── README.md             # This file
```

## 🚀 Quick Start for AI Tools

### Simple Integration
Add this instruction to your AI tool prompt:

```
"Before starting a task, if a context directory exists, read it for architectural overview and project context starting at context/index.md"
```

### Advanced Integration
For sophisticated tools:
1. Parse YAML front matter in `index.md` for structured metadata
2. Process Mermaid diagrams for visual architecture understanding  
3. Index documentation content for contextual awareness
4. Track context hierarchy through project structure

## 📖 Documentation Overview

### [index.md](./index.md)
**Primary entry point** with:
- YAML metadata describing the project
- Architectural overview and philosophy
- Key innovations ("Traces Generate Code")
- Component relationships
- Integration points

### [docs.md](./docs.md)
**Detailed technical documentation** covering:
- Development guidelines and patterns
- Business domain information
- Technical implementation details
- Integration patterns and troubleshooting
- Security considerations

### [otel.md](./otel.md)
**Complete OpenTelemetry ecosystem documentation** including:
- Full observability pipeline architecture
- Telemetry feedback loop implementation
- OTEL-enhanced CLI integration
- Semantic conventions and instrumentation
- Production deployment and configuration

### [diagrams/](./diagrams/)
**Visual architecture documentation**:
- `architecture.mmd`: Complete system architecture
- `data-flow.mmd`: Request flow and agent coordination
- `evolution-loop.mmd`: Auto-evolution cycle

## 🎯 Key Insights for AI Development

### Core Innovation v2
This framework demonstrates **telemetry-driven evolution with verified integration** where:
- **Type-safe OTEL models** generated from semantic conventions via Weaver Forge
- **FSM + OTEL + DSLModel** orchestration enables intelligent state transitions
- **Verified workflow patterns** with 100% telemetry validation (from full_loop_test.py)
- **AI-powered state machines** with automatic prompt-driven transitions
- **Production-ready patterns** with proper file organization and testing

### Architecture Patterns v2
1. **Enhanced Mixin Composition**: `FSMMixin`, `JinjaMixin`, `ToolMixin`, `DSLModel` base
2. **Type-Safe OTEL Integration**: Generated models from semantic conventions
3. **Verified State Machines**: @trigger decorators with AI-powered transitions  
4. **Workflow Orchestration**: DSLModel + OTEL + FSM unified patterns
5. **Template-Driven Generation**: Jinja2 with verified AI-assisted prompting
6. **Production Testing**: 80/20 patterns with verified integration tests

### Integration Points v2
- **LLM Integration**: OpenAI/Groq/Ollama via DSPy with verified ollama/qwen3 support
- **Type-Safe Observability**: OTEL ecosystem with generated Pydantic models
- **Verified Agent Coordination**: Tested multi-agent workflows via telemetry spans
- **Weaver Forge Integration**: Automated model generation from semantic conventions
- **FSM Orchestration**: State machines with OTEL instrumentation
- **Sustainable Code Generation**: Template + AI with validated patterns

## 🛠️ Development Workflow

### Essential Commands v2
```bash
# Quick validation & testing
python src/dslmodel/integrations/otel/tests/full_loop_test.py  # Complete integration test
dsl forge validate                                            # Validate OTEL models
poetry run poe otel-test                                     # CLI OTEL validation

# Development
poetry install -E otel     # Install with OTEL dependencies
dsl gen "create model"     # Generate from prompt
dsl forge build            # Generate OTEL models from conventions
dsl swarm demo            # Agent coordination demo

# OTEL Integration
dsl forge build --target python --output output/            # Generate models
dsl forge validate --module dslmodel.weaver.telemetry_spec  # Validate conventions
dsl otel status           # Telemetry validation (if available)

# Verified Coordination
poe swarm-demo            # Complete agent workflow
poe swarm-status          # System health check  
poe otel-demo             # OTEL ecosystem demo
```

### Agent Coordination v2
Agents communicate through verified telemetry patterns:
```bash
# Verified coordination commands (from updated CLI)
dsl swarm init            # Initialize agents and work items
dsl swarm process         # Process work queue
dsl swarm status          # View system status
dsl swarm telemetry       # Show telemetry events
dsl swarm dashboard       # Show coordination dashboard
dsl swarm clean           # Clean coordination data

# OTEL workflow testing
python src/dslmodel/integrations/otel/tests/full_loop_test.py

# FSM + OTEL integration demo
python src/dslmodel/examples/otel/working_fsm_demo.py
```

## 🔧 Context Maintenance

### Keeping Documentation Current
1. **Update with code changes**: Context should evolve with the codebase
2. **Review in pull requests**: Include context updates in code reviews
3. **Validate diagrams**: Ensure Mermaid diagrams reflect current architecture
4. **Test instructions**: Verify that documented commands still work

### Contributing to Context
When making significant changes:
1. Update relevant sections in `index.md` and `docs.md`
2. Refresh diagrams if architecture changes
3. Test documented workflows
4. Update metadata in YAML front matter

## 🎨 Mermaid Diagram Usage

### Viewing Diagrams
Use any Mermaid-compatible viewer:
- GitHub (renders automatically)
- Mermaid Live Editor
- VS Code Mermaid extensions
- Documentation generators that support Mermaid

### Updating Diagrams
When system architecture changes:
1. Update relevant `.mmd` files
2. Validate syntax with Mermaid tools
3. Ensure diagrams stay synchronized with code
4. Consider adding new diagrams for complex features

## 📚 Additional Resources

### Project Links v2
- **Main Repository**: Current directory
- **CLI Documentation**: See `src/dslmodel/cli.py` (enhanced with OTEL)
- **OTEL Integration**: `src/dslmodel/integrations/otel/` (new organization)
- **Workflow Orchestration**: `src/dslmodel/workflows/`
- **Agent Framework**: `src/dslmodel/agents/` and `src/dslmodel/agents/swarm/`
- **Verified Examples**: `src/dslmodel/examples/otel/` (working demos)
- **Integration Tests**: `src/dslmodel/integrations/otel/tests/`
- **Weaver Integration**: `src/dslmodel/weaver/` (semantic conventions)

### External Documentation v2
- [DSPy Framework](https://dspy-docs.vercel.app/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Weaver](https://github.com/open-telemetry/weaver) (model generation)
- [Pydantic v2](https://docs.pydantic.dev/latest/) (type safety)
- [Transitions FSM](https://github.com/pytransitions/transitions) (state machines)
- [Poetry Dependency Management](https://python-poetry.org/docs/)
- [Typer CLI Framework](https://typer.tiangolo.com/)

---

**This context documentation v2 enables both human developers and AI systems to quickly understand and effectively work with the enhanced DSLModel framework featuring verified OpenTelemetry integration, type-safe workflows, and intelligent state machines. The documentation follows CCS v2.0 standards with enhanced OTEL patterns and verified testing approaches.**