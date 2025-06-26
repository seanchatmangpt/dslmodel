# Agent Coordination CLI - Project Context for Claude

## Overview

This project implements an 80/20 Agent Coordination CLI in Python using Typer, focusing on the core 20% of features that provide 80% of the value. It's designed for managing work in AI agent swarms with nanosecond-precision IDs and atomic operations.

## Key Files

- `coordination_cli_v2.py` - Main Typer CLI implementation
- `test_coordination_cli_v2.py` - Comprehensive test suite  
- `coordination_cli_simple.py` - Simplified version without dependencies
- `.claude/commands/*.md` - Claude command definitions

## Architecture Principles

1. **80/20 Focus**: Only essential features included
2. **Fast-path Optimization**: JSONL append for 14x faster claims
3. **Atomic Operations**: File locking prevents race conditions
4. **Nanosecond IDs**: Guaranteed unique identifiers
5. **JSON Persistence**: Simple, portable data storage

## Core Commands

### Work Management
- `claim` - Claim work with atomic locking
- `progress` - Update work progress percentage
- `complete` - Mark work complete with velocity
- `list-work` - List and filter work items

### System Management  
- `dashboard` - View coordination overview
- `optimize` - Archive completed work for performance

## Custom Claude Commands

The `.claude/commands/` directory contains specialized commands:

- `/claim-work` - Intelligent work claiming with parsing
- `/complete-work` - Complete with testing and validation
- `/update-progress` - Progress updates with milestone guidance
- `/coordination-dashboard` - Comprehensive system view
- `/sprint-planning` - Sprint initialization and planning
- `/team-analysis` - Team performance metrics
- `/work-health-check` - System health diagnostics
- `/generate-report` - Formatted reports for stakeholders
- `/optimize-coordination` - Performance optimization
- `/infinite-coordination` - Autonomous coordination loop

## Performance Characteristics

- **Fast-path claims**: ~1ms (JSONL append)
- **Regular claims**: ~15ms (JSON parse/write)
- **Dashboard render**: ~5-10ms
- **Optimization**: Scales with completed items

## Data Files

Located in `$COORDINATION_DIR` (default: `/tmp/coordination`):
- `work_claims.json` - Active work items
- `work_claims_fast.jsonl` - Fast-path append-only log
- `coordination_log.json` - Completed work history
- `archived_claims/` - Archived completed work

## Development Workflow

1. Use `/claim-work` to claim new tasks
2. Update progress with `/update-progress`
3. Run tests before completing work
4. Use `/complete-work` when done
5. Check `/coordination-dashboard` for overview
6. Run `/optimize-coordination` periodically

## Testing

```bash
# Run all tests
pytest test_coordination_cli_v2.py -v

# Run specific test class
pytest test_coordination_cli_v2.py::TestClaimCommand -v

# Run with coverage
pytest --cov=coordination_cli_v2 test_coordination_cli_v2.py
```

## Code Style

- Follow PEP 8 Python style guide
- Use type hints for all functions
- Keep functions focused (single responsibility)
- Document with clear docstrings
- Test all new functionality

## Common Patterns

### Claiming Work
```python
# Fast-path (default)
./coordination_cli_v2.py claim feature "Description" --priority high

# Regular JSON
./coordination_cli_v2.py claim bug "Description" --fast=false
```

### Progress Updates
```python
# With work ID
./coordination_cli_v2.py progress work_123 75

# Using environment variable
export CURRENT_WORK_ITEM=work_123
./coordination_cli_v2.py progress 75
```

## Environment Variables

- `COORDINATION_DIR` - Base directory for data files
- `CURRENT_WORK_ITEM` - Active work item ID
- `AGENT_ID` - Current agent identifier

## Future Enhancements (Remaining 80%)

- OpenTelemetry distributed tracing
- Claude AI work prioritization  
- Scrum ceremony automation
- Real-time WebSocket updates
- Distributed coordination protocol

## Troubleshooting

### File Lock Conflicts
- Another process is updating
- Wait and retry or use fast-path

### JSON Parse Errors  
- Check file integrity
- Run `/work-health-check`
- Use `/optimize-coordination` to clean

### Performance Issues
- Archive old work regularly
- Use fast-path for new claims
- Monitor file sizes

## Integration Points

This CLI can integrate with:
- CI/CD pipelines for automated work tracking
- Monitoring systems via JSON logs
- Agent frameworks for autonomous operation
- Project management tools via export

## Architecture Diagrams

### 1. Overall Claude Code Architecture

```mermaid
graph TB
    subgraph "Claude Code Core"
        CC[Claude Code Instance]
        CM[Conversation Manager]
        TM[Tool Manager]
        MM[Memory Manager]
    end
    
    subgraph "DSLModel Integration"
        CLI[DSL CLI Interface]
        SA[SwarmAgent System]
        OTEL[OpenTelemetry]
        WE[Weaver Engine]
    end
    
    subgraph "Cognitive Enhancement Layer"
        CE[Cognitive Engine]
        PL[Pattern Learning]
        WO[Workflow Optimizer]
        CT[Context Tracker]
    end
    
    subgraph "Storage & Persistence"
        FS[File System]
        GIT[Git Repositories]
        JSONL[JSONL Telemetry]
        CLAUDE_MD[CLAUDE.md]
    end
    
    CC --> CM --> TM
    CC --> MM
    TM --> CLI
    CLI --> SA
    SA --> OTEL
    CLI --> WE
    
    CC --> CE
    CE --> PL
    CE --> WO
    CE --> CT
    
    MM --> FS
    CM --> CLAUDE_MD
    OTEL --> JSONL
    CLI --> GIT
    
    style CC fill:#f9f,stroke:#333,stroke-width:4px
    style CE fill:#bbf,stroke:#333,stroke-width:2px
    style SA fill:#bfb,stroke:#333,stroke-width:2px
```

### 2. CLI Command Structure & Consolidation

```mermaid
graph LR
    subgraph "Legacy Structure (25+ commands)"
        L1[dsl gen]
        L2[dsl evolve]
        L3[dsl evolve-unified]
        L4[dsl evolve-legacy]
        L5[dsl auto-evolve]
        L6[dsl evolve-worktree]
        L7[dsl 8020]
        L8[dsl validate]
        L9[dsl validate-weaver]
        L10[dsl forge]
        L11[dsl weaver]
        L12[dsl worktree]
        L13[dsl swarm]
        L14[dsl agents]
        L15[dsl redteam]
        L16[dsl telemetry]
    end
    
    subgraph "Consolidated 80/20 Structure"
        subgraph "Core Commands (80% usage)"
            C1[dsl gen<br/>Model Generation]
            C2[dsl evolve<br/>Unified Evolution]
            C3[dsl agent<br/>Agent Coordination]
            C4[dsl validate<br/>All Validation]
            C5[dsl dev<br/>Dev Tools]
            C6[dsl demo<br/>Demonstrations]
        end
        
        subgraph "Advanced (20% usage)"
            A1[dsl security<br/>Security Tools]
            A2[dsl telemetry<br/>Monitoring]
            A3[dsl research<br/>Research Tools]
        end
    end
    
    L1 --> C1
    L2 --> C2
    L3 --> C2
    L4 --> C2
    L5 --> C2
    L6 --> C2
    L7 --> C4
    L8 --> C4
    L9 --> C4
    L10 --> C5
    L11 --> C5
    L12 --> C5
    L13 --> C3
    L14 --> C3
    L15 --> A1
    L16 --> A2
    
    style C1 fill:#f96,stroke:#333,stroke-width:2px
    style C2 fill:#f96,stroke:#333,stroke-width:2px
    style C3 fill:#f96,stroke:#333,stroke-width:2px
    style C4 fill:#f96,stroke:#333,stroke-width:2px
```

### 3. SwarmAgent Communication Flow

```mermaid
sequenceDiagram
    participant RobertsAgent
    participant ScrumAgent
    participant LeanAgent
    participant OTEL
    participant JSONL
    
    Note over RobertsAgent: Motion Proposed
    RobertsAgent->>OTEL: emit_span("swarmsh.roberts.open")
    OTEL->>JSONL: Write span to file
    
    RobertsAgent->>RobertsAgent: State: IDLE → MOTION_OPEN
    
    Note over RobertsAgent: Voting
    RobertsAgent->>OTEL: emit_span("swarmsh.roberts.vote")
    OTEL->>JSONL: Write span
    RobertsAgent->>RobertsAgent: State: MOTION_OPEN → VOTING
    
    Note over RobertsAgent: Motion Passes
    RobertsAgent->>OTEL: emit_span("swarmsh.roberts.close")
    OTEL->>ScrumAgent: Trigger: "swarmsh.scrum.plan"
    
    Note over ScrumAgent: Sprint Planning
    ScrumAgent->>ScrumAgent: State: IDLE → PLANNING
    ScrumAgent->>OTEL: emit_span("swarmsh.scrum.plan")
    
    Note over ScrumAgent: Defect Found
    ScrumAgent->>OTEL: emit_span("swarmsh.scrum.review")
    OTEL->>LeanAgent: Trigger: "swarmsh.lean.define"
    
    Note over LeanAgent: DMAIC Cycle
    LeanAgent->>LeanAgent: State: IDLE → DEFINE
    LeanAgent->>OTEL: emit_span("swarmsh.lean.define")
    
    Note over LeanAgent: Process Change
    LeanAgent->>OTEL: emit_span("swarmsh.lean.improve")
    OTEL->>RobertsAgent: Trigger: "swarmsh.roberts.open"
    
    Note over JSONL: Continuous span streaming
```

### 4. OTEL Telemetry Integration

```mermaid
graph TB
    subgraph "Telemetry Sources"
        S1[SwarmAgent Spans]
        S2[Evolution Metrics]
        S3[Validation Results]
        S4[Cognitive Events]
        S5[Worktree Operations]
    end
    
    subgraph "OTEL Core"
        TP[TracerProvider]
        SP[SpanProcessor]
        SE[SpanExporter]
        SC[SpanContext]
    end
    
    subgraph "Exporters"
        JE[JSONL Exporter]
        CE[Console Exporter]
        ME[Memory Exporter]
    end
    
    subgraph "Storage"
        SPANS[spans.jsonl]
        AGENT[agent_coordination/]
        METRICS[metrics.json]
    end
    
    subgraph "Consumers"
        VAL[Validators]
        MON[Monitors]
        LEARN[Learning Systems]
    end
    
    S1 --> TP
    S2 --> TP
    S3 --> TP
    S4 --> TP
    S5 --> TP
    
    TP --> SP
    SP --> SE
    SE --> JE
    SE --> CE
    SE --> ME
    
    JE --> SPANS
    JE --> AGENT
    ME --> METRICS
    
    SPANS --> VAL
    AGENT --> MON
    METRICS --> LEARN
    
    style TP fill:#f9f,stroke:#333,stroke-width:2px
    style JE fill:#9f9,stroke:#333,stroke-width:2px
```

### 5. Evolution System Workflow

```mermaid
stateDiagram-v2
    [*] --> Analysis: Start Evolution
    
    Analysis --> Detection: Analyze Gaps
    Detection --> Prioritization: Detect Issues
    Prioritization --> Implementation: 80/20 Prioritize
    
    state Implementation {
        [*] --> Worktree: Create Worktree
        Worktree --> Mutation: Apply Changes
        Mutation --> Testing: Run Tests
        Testing --> Validation: Validate
        Validation --> [*]: Success
        Validation --> Worktree: Failure
    }
    
    Implementation --> Merge: All Tests Pass
    Merge --> Monitoring: Deploy
    Monitoring --> Learning: Collect Metrics
    Learning --> [*]: Complete
    
    Learning --> Analysis: Continuous Loop
    
    note right of Prioritization
        80/20 Rule:
        Focus on 20% changes
        that deliver 80% value
    end note
    
    note right of Monitoring
        OTEL telemetry tracks:
        - Performance impact
        - Error rates
        - User satisfaction
    end note
```

### 6. Validation Pipeline

```mermaid
graph LR
    subgraph "Input Sources"
        IS1[JSONL Spans]
        IS2[Agent Telemetry]
        IS3[Evolution Metrics]
    end
    
    subgraph "Validation Types"
        subgraph "OTEL Validation"
            OV1[Span Schema]
            OV2[Trace Integrity]
            OV3[Attribute Compliance]
        end
        
        subgraph "Weaver Validation"
            WV1[Semantic Conventions]
            WV2[Attribute Rules]
            WV3[Span Relationships]
        end
        
        subgraph "8020 Validation"
            EV1[Efficiency Metrics]
            EV2[Value Delivery]
            EV3[Effort Analysis]
        end
    end
    
    subgraph "Results"
        R1[Validation Report]
        R2[Success Metrics]
        R3[Failure Analysis]
        R4[Remediation Actions]
    end
    
    IS1 --> OV1
    IS2 --> WV1
    IS3 --> EV1
    
    OV1 --> R1
    OV2 --> R1
    OV3 --> R1
    
    WV1 --> R2
    WV2 --> R2
    WV3 --> R2
    
    EV1 --> R3
    EV2 --> R3
    EV3 --> R4
    
    style EV1 fill:#f96,stroke:#333,stroke-width:2px
    style EV2 fill:#f96,stroke:#333,stroke-width:2px
```

### 7. Worktree Management System

```mermaid
graph TB
    subgraph "Worktree Lifecycle"
        CREATE[Create Worktree]
        CHECKOUT[Checkout Branch]
        DEVELOP[Development]
        TEST[Testing]
        VALIDATE[Validation]
        MERGE[Merge]
        CLEANUP[Cleanup]
    end
    
    subgraph "Isolation Benefits"
        ISO1[Safe Experimentation]
        ISO2[Parallel Development]
        ISO3[Easy Rollback]
        ISO4[Clean Testing]
    end
    
    subgraph "Integration Points"
        GIT[Git Commands]
        SWARM[SwarmAgent Coordination]
        OTEL[OTEL Telemetry]
        EVOLVE[Evolution System]
    end
    
    CREATE --> CHECKOUT
    CHECKOUT --> DEVELOP
    DEVELOP --> TEST
    TEST --> VALIDATE
    VALIDATE --> MERGE
    VALIDATE --> CLEANUP
    MERGE --> CLEANUP
    
    CREATE --> ISO1
    DEVELOP --> ISO2
    TEST --> ISO3
    VALIDATE --> ISO4
    
    CREATE --> GIT
    DEVELOP --> SWARM
    TEST --> OTEL
    MERGE --> EVOLVE
    
    style CREATE fill:#9f9,stroke:#333,stroke-width:2px
    style MERGE fill:#f99,stroke:#333,stroke-width:2px
```

### 8. Cognitive Enhancement Architecture

```mermaid
graph TB
    subgraph "Claude Code Core"
        CC[Claude Code Instance]
        CONTEXT[Context Manager]
        TOOLS[Tool Executor]
    end
    
    subgraph "Cognitive Enhancements"
        subgraph "Memory System"
            SM[Session Memory]
            PM[Pattern Memory]
            CM[Context Memory]
        end
        
        subgraph "Learning System"
            PL[Pattern Learner]
            SL[Success Learner]
            FL[Failure Learner]
        end
        
        subgraph "Optimization System"
            WO[Workflow Optimizer]
            CO[Context Optimizer]
            TO[Task Optimizer]
        end
    end
    
    subgraph "Auto-Deployment"
        AD[Auto-Deployer]
        CV[Capability Validator]
        CI[Continuous Improvement]
    end
    
    subgraph "Integration"
        DSL[DSLModel Integration]
        SWARM[SwarmAgent Network]
        TELEM[Telemetry System]
    end
    
    CC --> CONTEXT
    CC --> TOOLS
    
    CONTEXT --> SM
    CONTEXT --> PM
    CONTEXT --> CM
    
    TOOLS --> PL
    TOOLS --> SL
    TOOLS --> FL
    
    PL --> WO
    SL --> CO
    FL --> TO
    
    AD --> CV
    CV --> CI
    CI --> CC
    
    WO --> DSL
    CO --> SWARM
    TO --> TELEM
    
    style CC fill:#f9f,stroke:#333,stroke-width:4px
    style AD fill:#9ff,stroke:#333,stroke-width:2px
    style PL fill:#ff9,stroke:#333,stroke-width:2px
```

### 9. 80/20 System Integration

```mermaid
pie title "80/20 Command Usage Distribution"
    "Core Commands (80%)" : 80
    "Advanced Commands (20%)" : 20
```

```mermaid
graph LR
    subgraph "80% Value Delivery"
        V1[Model Generation]
        V2[Evolution System]
        V3[Agent Coordination]
        V4[Validation]
        V5[Development Tools]
    end
    
    subgraph "20% Effort Focus"
        E1[Consolidated CLI]
        E2[Unified Commands]
        E3[Auto-Optimization]
        E4[Smart Defaults]
    end
    
    E1 --> V1
    E1 --> V2
    E2 --> V3
    E2 --> V4
    E3 --> V5
    E4 --> V1
    E4 --> V2
    
    style E1 fill:#9f9,stroke:#333,stroke-width:2px
    style E2 fill:#9f9,stroke:#333,stroke-width:2px
```

### 10. Complete System Flow

```mermaid
flowchart TB
    subgraph "User Interaction"
        USER[User] --> CMD[CLI Command]
    end
    
    subgraph "Claude Code Processing"
        CMD --> CC[Claude Code]
        CC --> PARSE[Parse Intent]
        PARSE --> ENHANCE[Cognitive Enhancement]
        ENHANCE --> EXEC[Execute]
    end
    
    subgraph "DSLModel Ecosystem"
        EXEC --> DSL{DSL Router}
        DSL --> GEN[Generation]
        DSL --> EVOLVE[Evolution]
        DSL --> AGENT[Agents]
        DSL --> VALIDATE[Validation]
    end
    
    subgraph "Telemetry & Learning"
        GEN --> OTEL[OTEL Spans]
        EVOLVE --> OTEL
        AGENT --> OTEL
        VALIDATE --> OTEL
        
        OTEL --> LEARN[Learning System]
        LEARN --> PATTERN[Pattern Recognition]
        PATTERN --> ENHANCE
    end
    
    subgraph "Results"
        GEN --> RESULT[Output]
        EVOLVE --> RESULT
        AGENT --> RESULT
        VALIDATE --> RESULT
        RESULT --> USER
    end
    
    style USER fill:#f9f,stroke:#333,stroke-width:4px
    style CC fill:#9ff,stroke:#333,stroke-width:2px
    style OTEL fill:#ff9,stroke:#333,stroke-width:2px
    style LEARN fill:#9f9,stroke:#333,stroke-width:2px
```