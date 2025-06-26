---
module-name: "DSLModel Framework v2"
description: "Enhanced AI-powered domain-specific language framework with verified OpenTelemetry integration, type-safe workflows, and intelligent state machine orchestration"
related-modules:
  - name: "Agent Coordination System"
    path: ./src/dslmodel/agents
  - name: "OpenTelemetry Integration v2"
    path: ./src/dslmodel/integrations/otel
  - name: "OTEL Ecosystem Documentation"
    path: ./context/otel.md
  - name: "CLI Tools"
    path: ./src/dslmodel/cli.py
  - name: "Template System"
    path: ./src/dslmodel/template
  - name: "Example Implementations"
    path: ./src/dslmodel/examples
  - name: "MQ7 Messaging System"
    path: ./src/dslmodel/mq7
  - name: "Swarm Agent Framework v2"
    path: ./src/dslmodel/agents/swarm
  - name: "Weaver Integration"
    path: ./src/dslmodel/weaver
  - name: "Workflow Orchestration"
    path: ./src/dslmodel/workflows
architecture:
  style: "Type-Safe Event-Driven Microservices with Verified AI Agent Coordination"
  components:
    - name: "DSL Generator Core"
      description: "Pydantic model generation from natural language prompts using DSPy and LLMs"
    - name: "Agent Swarm System"
      description: "Distributed agent coordination with OpenTelemetry span-driven communication"
    - name: "OpenTelemetry Ecosystem v2"
      description: "Type-safe observability with generated Pydantic models from Weaver Forge semantic conventions"
    - name: "Template Engine"
      description: "Jinja2-based code generation with custom extensions"
    - name: "CLI Framework"
      description: "Typer-based command-line interface with multiple sub-applications"
    - name: "MQ7 Event System"
      description: "Asynchronous message passing for agent coordination"
    - name: "FSM + OTEL Orchestration"
      description: "Verified finite state machine workflows with integrated telemetry and AI-powered transitions"
  patterns:
    - name: "Mixin Architecture"
      usage: "Compositional design through FSMMixin, JinjaMixin, ToolMixin, etc."
    - name: "Type-Safe OTEL Coordination"
      usage: "Agents react to validated OpenTelemetry spans with generated Pydantic models"
    - name: "Verified Workflow Patterns"
      usage: "Tested workflow orchestration with DSLModel + OTEL + FSM integration"
    - name: "Template-Driven Generation"
      usage: "Code and model generation through Jinja2 templates with AI assistance"
    - name: "Event-Sourced Workflows"
      usage: "MQ7 event registration and handling for distributed coordination"
---

# DSLModel Framework Architecture v2

## Overview

DSLModel v2 is an enhanced AI-powered framework with verified OpenTelemetry integration that bridges natural language and code generation through domain-specific languages. The system implements a proven architecture where **type-safe telemetry drives intelligent workflows** - OpenTelemetry traces coordinate agent behavior through generated Pydantic models with 100% validation success.

## Core Philosophy

**"Type-Safe Traces Drive Intelligence"** - The system demonstrates verified computational patterns where:
- Type-safe telemetry spans trigger validated agent behaviors
- Weaver Forge generates Pydantic models from semantic conventions
- FSM + OTEL + DSLModel orchestration enables intelligent workflows
- AI-powered state transitions with prompt-driven logic
- 100% telemetry validation through generated models

## System Architecture

### 1. **AI-Powered DSL Generation**
```
Natural Language Prompt → DSPy Modules → Pydantic Models → Generated Code
```

The core engine uses:
- **DSPy Integration**: Structured prompting for reliable model generation
- **Pydantic v2**: Type-safe model definitions with validation
- **Template System**: Jinja2-based code generation with custom extensions
- **Multiple Output Formats**: Python classes, JSON schemas, API endpoints

### 2. **Enhanced Agent Swarm Coordination v2**
```
Type-Safe OTEL Spans → Validated Triggers → AI State Transitions → Telemetry Export → Verified Loop
```

**SwarmAgent Architecture v2:**
- Agents process validated telemetry through generated Pydantic models
- Type-safe span validation prevents invalid coordination data
- FSM integration with @trigger decorators and AI-powered transitions
- JSONL telemetry export compatible with OTEL collectors
- Verified workflow patterns from full_loop_test.py integration

**Agent Types:**
- **Roberts Rules Agent**: Governance and motion processing
- **Scrum Agent**: Agile workflow management
- **Lean Agent**: Process optimization and defect tracking
- **Research Agent**: Information gathering and analysis

### 3. **Verified OpenTelemetry Ecosystem v2**

The system implements a complete type-safe observability pipeline with automated feedback loops:

```
WEAVER GENERATION → PYDANTIC VALIDATION → FSM ORCHESTRATION → TELEMETRY EXPORT → FEEDBACK LOOP → OPTIMIZATION
```

**Verified Components:**
- **Complete OTEL Ecosystem**: Full observability stack in `src/dslmodel/otel/` (see [OTEL Documentation](./otel.md))
- **Telemetry Feedback Loop**: Automated optimization from telemetry analysis 
- **Weaver Forge Integration**: Generates type-safe Pydantic models from semantic conventions
- **JSONL Telemetry Export**: OTEL-compatible span data with validation
- **FSM + OTEL Orchestration**: State machines with integrated telemetry
- **Workflow Orchestrator**: DSLModel + OTEL + FSM unified patterns
- **Production Testing**: Verified through full_loop_test.py (100% validation success)

### 4. **Template-Driven Architecture**

**Jinja2 Extensions:**
- `FakerExtension`: Realistic test data generation
- `InflectionExtension`: String transformations
- `PydanticExtension`: Model-aware template processing

**Template Patterns:**
- Model generation templates
- CLI command scaffolding
- API endpoint creation
- Documentation generation

## Key Innovations

### 1. **Type-Safe Telemetry as Workflow Engine**
Unlike traditional observability, verified telemetry actively drives intelligent workflows:
- Type-safe spans trigger validated agent state transitions
- Generated Pydantic models ensure data integrity
- AI-powered FSM transitions with prompt-driven logic
- Workflow orchestration through DSLModel + OTEL + FSM patterns
- Verified integration patterns with 100% telemetry validation

### 2. **Verified Workflow Patterns**
The system operates through tested integration patterns:
- **Model Generation**: Weaver Forge creates type-safe OTEL models
- **Validation**: 100% telemetry data validation through Pydantic
- **Orchestration**: Verified FSM + OTEL + DSLModel workflows
- **Testing**: Production-ready patterns with comprehensive validation

### 3. **Type-Safe Multi-Agent Coordination**
Agents coordinate through validated telemetry patterns:
- Type-safe span data prevents coordination errors
- Generated models ensure consistent agent communication
- FSM state transitions with AI-powered decision logic
- Verified coordination patterns through integration testing

## CLI Architecture

### Main Command: `dsl`
```bash
dsl gen "Create a user model with email validation"
dsl swarm demo                    # Verified agent coordination
dsl forge build --target python  # Generate OTEL models
dsl forge validate               # Validate semantic conventions
dsl demo run --cycles 3          # Full cycle demonstrations
```

### Sub-Applications:
- **AsyncAPI**: Handler and Vue page generation
- **Slidev**: Presentation creation and export
- **OTEL**: Type-safe telemetry coordination (if available)
- **Forge**: Weaver Forge semantic convention building
- **Autonomous**: AI decision engine
- **Swarm**: Verified agent orchestration
- **Demo**: Automated full cycle demonstrations

## Development Workflow

### 1. **Verified Testing Strategy v2**
```bash
python src/dslmodel/integrations/otel/tests/full_loop_test.py  # Complete integration
dsl forge validate                                            # Validate OTEL models
poetry run poe otel-test                                     # CLI validation
poetry run poe demo-full-fast                                # Quick full cycle
```

### 2. **Poetry Integration**
- Dependency management through `pyproject.toml`
- CLI scripts: `dsl = "dslmodel.cli:app"`
- Optional OTEL dependencies with `[otel]` extra
- Poethepoet tasks for complex workflows

### 3. **Enhanced Documentation v2**
- Auto-generated API docs with pdoc
- Verified integration examples with working code
- Updated Mermaid diagrams for v2 architecture
- Context-driven documentation through CCS v2.0

## Integration Points

### External Systems
- **OpenAI**: LLM integration for model generation
- **Groq**: Alternative LLM provider
- **Ollama**: Local LLM support (verified with qwen3)
- **GitHub**: Repository integration and Actions
- **Docker**: Containerized OTEL collectors
- **Prometheus**: Metrics collection and alerting

### AI Frameworks
- **DSPy**: Structured prompting and LLM integration
- **Pydantic AI**: Type-safe AI interactions
- **OpenTelemetry**: Comprehensive observability
- **Weaver Forge**: Type-safe model generation from semantic conventions

## Future Evolution

The system is designed for verified production workflows:
- **Type-Safe OTEL Integration**: Validated telemetry with generated models
- **Workflow Orchestration**: FSM + OTEL + DSLModel patterns
- **AI-Powered State Machines**: Intelligent transitions with prompt logic
- **Production Testing**: Comprehensive validation and verification patterns

## Getting Started

1. **Installation**: `poetry install -E otel` (with OTEL support)
2. **Basic Generation**: `dsl gen "Create a product catalog model"`
3. **OTEL Integration**: `dsl forge build --target python`
4. **Workflow Demo**: `python src/dslmodel/integrations/otel/tests/full_loop_test.py`
5. **Agent Demo**: `dsl swarm demo`
6. **Full Cycle**: `dsl demo run --cycles 1`

The framework v2 represents a paradigm shift where type-safe observability drives intelligent workflows, creating verified and production-ready adaptive software systems with comprehensive validation and testing.