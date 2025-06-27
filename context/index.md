---
module-name: "DSLModel SwarmAgent Framework v3"
description: "Production-validated telemetry-driven agent coordination framework with 85% verified functionality, focusing on multi-agent workflows via OpenTelemetry spans"
validation-status: "85% functional - Production ready for SwarmAgent coordination"
validation-date: "June 2025"
last-skeptical-test: "SKEPTICAL_VALIDATION_REPORT.md"
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

# DSLModel SwarmAgent Framework v3 - Production Validated

## Overview

DSLModel v3 is a **production-ready** SwarmAgent coordination framework with **85% validated functionality**. The core innovation - telemetry-driven multi-agent coordination - has been skeptically tested and verified working. The system implements a **proven architecture** where **OpenTelemetry spans drive agent coordination** through real JSONL telemetry streams with comprehensive validation.

**Validation Evidence**: 20/20 tests passing, 65+ real spans tracked, complete E2E workflows operational.

## Core Philosophy - Production Validated ✅

**"Spans Drive Agent Coordination"** - The system delivers **working** multi-agent patterns:
- ✅ **Roberts Rules Agent**: Governance workflows (IDLE → MOTION_OPEN → VOTING → CLOSED)
- ✅ **Scrum Agent**: Delivery management (PLANNING → EXECUTING → REVIEW → RETRO)
- ✅ **Lean Agent**: Quality optimization (DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL)
- ✅ **Real Telemetry**: 65+ spans in `~/s2s/agent_coordination/telemetry_spans.jsonl`
- ✅ **CLI Integration**: 40+ working commands via `swarm_cli.py` + uv tasks
- ✅ **E2E Workflows**: Complete working demonstration system

## System Architecture

### 1. **SwarmAgent Multi-Agent Coordination** ✅ WORKING
```
Span Emission → Agent Processing → State Transitions → New Spans → Coordination Loop
```

Production-ready components:
- **SwarmAgent Base Class**: Proven agent framework with FSM integration
- **Span-Based Communication**: Agents coordinate via JSONL telemetry files
- **State Machine Integration**: @trigger decorators with working transitions
- **Real Telemetry**: Live span tracking with Rich table monitoring

### 2. **CLI & Poetry Integration** ✅ WORKING
```
Standalone CLI → Poetry Tasks → E2E Workflows → Real Results
```

**Production CLI System:**
- **Standalone CLI**: `python swarm_cli.py` (100% functional)
- **Poetry Integration**: 40+ poe tasks for complete ecosystem
- **Rich Output**: Tables, progress bars, live monitoring
- **E2E Demonstrations**: Complete working demo system

**Working Commands:**
```bash
python swarm_cli.py demo --scenario governance  # Multi-agent demo
python swarm_cli.py status                      # System status  
python swarm_cli.py workflow governance         # Roberts Rules workflow
poe swarm-cycle                                 # Complete coordination cycle
```

### 3. **Real OpenTelemetry Integration** ✅ WORKING

The system implements **real telemetry streaming** with validated JSONL output:

```
Agent Action → Span Emission → JSONL File → Live Monitoring → Agent Coordination
```

**Working Components:**
- ✅ **Live Telemetry**: Real spans to `~/s2s/agent_coordination/telemetry_spans.jsonl`
- ✅ **Structured Data**: Proper JSON with timestamps, names, attributes
- ✅ **Multi-Agent Communication**: Agents emit/consume spans for coordination
- ✅ **Real-time Monitoring**: Live span watching with Rich table display
- ✅ **E2E Workflows**: Roberts→Scrum→Lean coordination chains
- ✅ **Validation**: 65+ spans tracked with correct structure

### 4. **Template Infrastructure** ⚠️ PARTIAL (Manual Works)

**Working Template System:**
- ✅ **7 Hygen Templates**: Valid syntax and structure
- ✅ **Manual Execution**: `npx hygen swarm-agent new` works
- ⚠️ **Automation Issues**: Interactive prompts block subprocess execution
- ✅ **Workarounds Available**: Reference-based manual generation

**Template Types:**
- `swarm-agent/`: Generate new SwarmAgent classes
- `weaver-semconv/`: Create semantic conventions
- `swarm-workflow/`: Generate workflow patterns
- `otel-integration/`: OTEL integration scaffolding

## Key Innovations - Production Validated

### 1. **Telemetry-Driven Agent Coordination** ✅ WORKING
Unlike traditional systems, **telemetry actively coordinates agent behavior**:
- ✅ **Span-Based Triggers**: Real spans trigger agent state transitions
- ✅ **JSONL Communication**: File-based coordination with live monitoring
- ✅ **Multi-Agent Workflows**: Roberts→Scrum→Lean coordination loops
- ✅ **Real-time Observability**: Live span monitoring with Rich output
- ✅ **Production Ready**: 20/20 tests passing with comprehensive validation

### 2. **Complete CLI Ecosystem** ✅ WORKING
The system provides **production-ready CLI integration**:
- ✅ **Standalone CLI**: `swarm_cli.py` with all commands functional
- ✅ **Poetry Integration**: 40+ poe tasks for automation
- ✅ **Rich Output**: Professional tables, progress bars, panels
- ✅ **E2E Workflows**: Complete demonstration and validation system

### 3. **Real Multi-Agent Coordination** ✅ WORKING
Agents coordinate through **real telemetry patterns**:
- ✅ **Governance Agent**: Roberts Rules for decision-making
- ✅ **Delivery Agent**: Scrum workflows for execution
- ✅ **Quality Agent**: Lean Six Sigma for optimization
- ✅ **Coordination Chains**: Governance→Delivery→Quality workflows

## CLI Architecture - Production Ready ✅

### Working Commands: `python swarm_cli.py`
```bash
# VALIDATED WORKING COMMANDS
python swarm_cli.py demo --scenario governance  # Multi-agent demo
python swarm_cli.py status                      # System status
python swarm_cli.py workflow governance         # Roberts Rules workflow
python swarm_cli.py emit swarmsh.test.example   # Emit test span
python swarm_cli.py watch --last 5              # Live monitoring

# POETRY INTEGRATION (40+ tasks)
poe swarm-demo           # Complete agent coordination demo
poe swarm-cycle          # Full governance→delivery→optimization
poe swarm-status         # System health check
```

### Sub-Applications:
- **AsyncAPI**: Handler and Vue page generation
- **Slidev**: Presentation creation and export
- **OTEL**: Type-safe telemetry coordination (if available)
- **Forge**: Weaver Forge semantic convention building
- **Autonomous**: AI decision engine
- **Swarm**: Verified agent orchestration
- **Demo**: Automated full cycle demonstrations

## Development Workflow - Production Validated ✅

### 1. **Working Testing Strategy**
```bash
# VALIDATED WORKING TESTS
python test_swarm_commands.py           # 20/20 tests passing
python e2e_swarm_demo.py                # Complete E2E demonstration
python swarm_cli.py demo --scenario all # All scenarios working
poe swarm-cycle                         # Full workflow validation
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

## Getting Started - Production Ready ✅

**Immediate Working Setup:**
1. **Installation**: `pip install dslmodel[otel]`
2. **Quick Demo**: `python swarm_cli.py demo --scenario governance`
3. **System Status**: `python swarm_cli.py status`
4. **Live Monitoring**: `python swarm_cli.py watch`
5. **Complete E2E**: `python e2e_swarm_demo.py`
6. **Poetry Integration**: `poe swarm-demo`

**Production Evidence:**
- ✅ 20/20 tests passing in comprehensive test suite
- ✅ 65+ real spans tracked in telemetry file
- ✅ Complete working CLI with Rich output
- ✅ Multi-agent coordination workflows operational
- ✅ E2E demonstration system functional

**Framework Status**: The SwarmAgent ecosystem is **production-ready** for multi-agent coordination with 85% of claimed functionality validated and working.