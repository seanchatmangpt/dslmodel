# Claude Code - Complete Mermaid Diagram Documentation

## 1. Tool Hierarchy and Categories

```mermaid
graph TD
    CC[Claude Code Tools] --> F[File Operations]
    CC --> B[Bash Operations]
    CC --> S[Search Operations]
    CC --> W[Web Operations]
    CC --> A[Agent Operations]
    CC --> T[Todo Operations]
    CC --> N[Notebook Operations]
    CC --> P[Special Operations]
    
    F --> F1[Read]
    F --> F2[Write]
    F --> F3[Edit]
    F --> F4[MultiEdit]
    
    B --> B1[Bash]
    
    S --> S1[Grep]
    S --> S2[Glob]
    S --> S3[LS]
    
    W --> W1[WebFetch]
    W --> W2[WebSearch]
    
    A --> A1[Task]
    
    T --> T1[TodoRead]
    T --> T2[TodoWrite]
    
    N --> N1[NotebookRead]
    N --> N2[NotebookEdit]
    
    P --> P1[exit_plan_mode]
    P --> P2[Unknown Tools]
    
    style CC fill:#f9f,stroke:#333,stroke-width:4px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style B fill:#fbf,stroke:#333,stroke-width:2px
    style S fill:#bfb,stroke:#333,stroke-width:2px
    style W fill:#ffb,stroke:#333,stroke-width:2px
    style A fill:#fbb,stroke:#333,stroke-width:2px
```

## 2. OpenTelemetry Span Structure

```mermaid
graph TB
    subgraph "Span Hierarchy"
        Root[claude_code.operation.*]
        Root --> File1[claude_code.file]
        Root --> Bash1[claude_code.bash]
        Root --> Agent1[claude_code.agent]
        
        Agent1 --> Event1[Progress 25%]
        Agent1 --> Event2[Progress 50%]
        Agent1 --> Event3[Progress 75%]
        Agent1 --> Event4[Progress 100%]
    end
    
    subgraph "Span Attributes"
        Base[Base Attributes]
        Base --> BA1[tool.name]
        Base --> BA2[tool.category]
        Base --> BA3[session.id]
        Base --> BA4[user.request]
        Base --> BA5[duration_ms]
        
        Specific[Tool-Specific]
        Specific --> SA1[file.path]
        Specific --> SA2[bash.command]
        Specific --> SA3[agent.progress]
        Specific --> SA4[web.url]
    end
    
    Root -.->|inherits| Base
    File1 -.->|adds| Specific
```

## 3. Telemetry Flow Architecture

```mermaid
flowchart LR
    subgraph "User Layer"
        U[User Request]
    end
    
    subgraph "Claude Code Core"
        TC[Tool Call]
        TI[Tool Interceptor]
    end
    
    subgraph "Weaver Layer"
        WW[Weaver Wrapper]
        WM[Weaver Models]
        WT[Weaver Telemetry]
    end
    
    subgraph "OpenTelemetry"
        TP[Tracer Provider]
        SP[Span Processor]
        EX[Exporters]
    end
    
    subgraph "Backends"
        CE[Console Exporter]
        JE[Jaeger Exporter]
        ME[Memory Exporter]
        PE[Prometheus]
    end
    
    U --> TC
    TC --> TI
    TI --> WW
    WW --> WM
    WM --> WT
    WT --> TP
    TP --> SP
    SP --> EX
    EX --> CE
    EX --> JE
    EX --> ME
    EX --> PE
    
    style U fill:#f9f,stroke:#333,stroke-width:2px
    style WT fill:#bbf,stroke:#333,stroke-width:2px
    style EX fill:#bfb,stroke:#333,stroke-width:2px
```

## 4. Tool Execution Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initialized: Tool Request
    Initialized --> Validating: Validate Args
    Validating --> SpanCreated: Create OTEL Span
    SpanCreated --> Executing: Execute Tool
    
    Executing --> Success: No Errors
    Executing --> Failed: Exception
    
    Success --> Recording: Record Metrics
    Failed --> Recording: Record Error
    
    Recording --> SpanClosed: Close Span
    SpanClosed --> [*]: Return Result
    
    note right of SpanCreated
        Set base attributes:
        - tool.name
        - tool.category
        - session.id
        - start_time
    end note
    
    note right of Recording
        Update span:
        - duration_ms
        - status (OK/ERROR)
        - result attributes
    end note
```

## 5. Integration Patterns

```mermaid
graph TD
    subgraph "Integration Approaches"
        D[Decorator Pattern]
        M[Middleware Pattern]
        W[Direct Wrapper]
        C[Context Manager]
    end
    
    subgraph "Decorator"
        D1["@weaver_telemetry"]
        D2[Function]
        D1 -->|wraps| D2
    end
    
    subgraph "Middleware"
        M1[Tool Request]
        M2[Middleware Layer]
        M3[Tool Execution]
        M1 --> M2
        M2 --> M3
    end
    
    subgraph "Wrapper"
        W1[ClaudeCodeWrapper]
        W2[Tool Methods]
        W1 -->|contains| W2
    end
    
    subgraph "Context"
        C1[WeaverContext]
        C2[Multiple Tools]
        C1 -->|groups| C2
    end
    
    D --> D1
    M --> M1
    W --> W1
    C --> C1
```

## 6. Data Flow Through System

```mermaid
flowchart TB
    subgraph "Input"
        UR[User Request]
        TA[Tool Arguments]
    end
    
    subgraph "Processing"
        TM[Tool Mapping]
        AV[Argument Validation]
        SC[Span Creation]
        TE[Tool Execution]
        RM[Result Mapping]
    end
    
    subgraph "Telemetry"
        AT[Attributes]
        EV[Events]
        ST[Status]
        DU[Duration]
    end
    
    subgraph "Output"
        RES[Result]
        TEL[Telemetry Data]
        MET[Metrics]
    end
    
    UR --> TM
    TA --> AV
    TM --> SC
    AV --> SC
    SC --> TE
    
    TE --> AT
    TE --> EV
    TE --> ST
    TE --> DU
    
    TE --> RM
    AT --> TEL
    EV --> TEL
    ST --> TEL
    DU --> TEL
    
    RM --> RES
    TEL --> MET
```

## 7. Error Handling Flow

```mermaid
flowchart LR
    subgraph "Error Sources"
        TE[Tool Error]
        VE[Validation Error]
        TE2[Timeout Error]
        PE[Permission Error]
    end
    
    subgraph "Error Handling"
        EC[Error Capture]
        ER[Error Recording]
        ES[Status Setting]
        EE[Exception Event]
    end
    
    subgraph "Propagation"
        SP[Span Status ERROR]
        EX[Exception Raised]
        ME[Metrics Updated]
    end
    
    TE --> EC
    VE --> EC
    TE2 --> EC
    PE --> EC
    
    EC --> ER
    ER --> ES
    ER --> EE
    
    ES --> SP
    EE --> EX
    ES --> ME
    
    style TE fill:#f99,stroke:#333,stroke-width:2px
    style SP fill:#f99,stroke:#333,stroke-width:2px
```

## 8. Attribute Inheritance Model

```mermaid
classDiagram
    class BaseAttributes {
        +tool.name: string
        +tool.category: string
        +session.id: string
        +user.request: string
        +duration_ms: double
    }
    
    class FileAttributes {
        +file.path: string
        +file.operation: string
        +file.size_bytes: int
        +file.lines_affected: int
    }
    
    class BashAttributes {
        +bash.command: string
        +bash.exit_code: int
        +bash.timeout_ms: double
    }
    
    class SearchAttributes {
        +search.pattern: string
        +search.path: string
        +search.results_count: int
    }
    
    class WebAttributes {
        +web.url: string
        +web.operation: string
        +web.response_size_bytes: int
        +web.cache_hit: boolean
    }
    
    class AgentAttributes {
        +agent.id: string
        +agent.task: string
        +agent.status: string
        +agent.progress_percent: double
    }
    
    BaseAttributes <|-- FileAttributes
    BaseAttributes <|-- BashAttributes
    BaseAttributes <|-- SearchAttributes
    BaseAttributes <|-- WebAttributes
    BaseAttributes <|-- AgentAttributes
```

## 9. Session and Metrics Aggregation

```mermaid
graph TB
    subgraph "Session Management"
        SI[Session Init]
        ST[Session Tracking]
        SM[Session Metrics]
    end
    
    subgraph "Tool Metrics"
        TC[Total Calls]
        SC[Success Count]
        FC[Failure Count]
        AD[Avg Duration]
        SR[Success Rate]
    end
    
    subgraph "Aggregation"
        TA[Tool Aggregates]
        SA[Session Aggregates]
        GA[Global Aggregates]
    end
    
    SI --> ST
    ST --> TC
    ST --> SC
    ST --> FC
    TC --> AD
    SC --> SR
    FC --> SR
    
    TC --> TA
    SC --> TA
    FC --> TA
    AD --> TA
    SR --> TA
    
    TA --> SA
    SA --> GA
    
    style SM fill:#bfb,stroke:#333,stroke-width:2px
    style GA fill:#fbf,stroke:#333,stroke-width:2px
```

## 10. Complete System Architecture

```mermaid
graph TB
    subgraph "Claude Code Core"
        CLI[CLI Interface]
        TOOLS[Tool Registry]
        EXEC[Tool Executor]
    end
    
    subgraph "Weaver Integration"
        YAML[Semantic Conventions YAML]
        GEN[Weaver Generator]
        MOD[Generated Models]
        WRAP[Weaver Wrapper]
    end
    
    subgraph "Telemetry Pipeline"
        TRACE[Tracer]
        SPAN[Span Creation]
        ATTR[Attribute Setting]
        EVENT[Event Recording]
        EXPORT[Export Pipeline]
    end
    
    subgraph "Storage & Analysis"
        CONSOLE[Console Output]
        JAEGER[Jaeger UI]
        PROM[Prometheus]
        CUSTOM[Custom Backend]
    end
    
    CLI --> TOOLS
    TOOLS --> EXEC
    EXEC --> WRAP
    
    YAML --> GEN
    GEN --> MOD
    MOD --> WRAP
    
    WRAP --> TRACE
    TRACE --> SPAN
    SPAN --> ATTR
    SPAN --> EVENT
    ATTR --> EXPORT
    EVENT --> EXPORT
    
    EXPORT --> CONSOLE
    EXPORT --> JAEGER
    EXPORT --> PROM
    EXPORT --> CUSTOM
    
    style CLI fill:#f9f,stroke:#333,stroke-width:3px
    style WRAP fill:#bbf,stroke:#333,stroke-width:3px
    style EXPORT fill:#bfb,stroke:#333,stroke-width:3px
```

## 11. Tool Category Decision Tree

```mermaid
graph TD
    START[Tool Request] --> Q1{File System?}
    Q1 -->|Yes| FILE[claude_code.file]
    Q1 -->|No| Q2{Command Execution?}
    
    Q2 -->|Yes| BASH[claude_code.bash]
    Q2 -->|No| Q3{Search Operation?}
    
    Q3 -->|Yes| SEARCH[claude_code.search]
    Q3 -->|No| Q4{Web Access?}
    
    Q4 -->|Yes| WEB[claude_code.web]
    Q4 -->|No| Q5{Agent Task?}
    
    Q5 -->|Yes| AGENT[claude_code.agent]
    Q5 -->|No| Q6{Todo Management?}
    
    Q6 -->|Yes| TODO[claude_code.todo]
    Q6 -->|No| Q7{Notebook?}
    
    Q7 -->|Yes| NOTEBOOK[claude_code.notebook]
    Q7 -->|No| UNKNOWN[claude_code.unknown]
    
    style START fill:#ffd,stroke:#333,stroke-width:2px
    style UNKNOWN fill:#fdd,stroke:#333,stroke-width:2px
```

## 12. Progress Tracking for Long Operations

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode
    participant WeaverWrapper
    participant OTEL
    participant Backend
    
    User->>ClaudeCode: Start Task
    ClaudeCode->>WeaverWrapper: Execute Agent Task
    WeaverWrapper->>OTEL: Create Span
    
    loop Progress Updates
        WeaverWrapper->>OTEL: Add Event (25%)
        OTEL->>Backend: Export Event
        WeaverWrapper->>OTEL: Add Event (50%)
        OTEL->>Backend: Export Event
        WeaverWrapper->>OTEL: Add Event (75%)
        OTEL->>Backend: Export Event
        WeaverWrapper->>OTEL: Add Event (100%)
        OTEL->>Backend: Export Event
    end
    
    WeaverWrapper->>OTEL: Set Status OK
    WeaverWrapper->>OTEL: Close Span
    OTEL->>Backend: Export Final Span
    WeaverWrapper->>ClaudeCode: Return Result
    ClaudeCode->>User: Task Complete
```

These diagrams provide a comprehensive visual overview of:
- Tool organization and hierarchy
- Telemetry architecture and flow
- Integration patterns and approaches
- Data flow through the system
- Error handling mechanisms
- Attribute inheritance model
- Session and metrics aggregation
- Complete system architecture
- Decision trees for tool categorization
- Progress tracking for long-running operations

Each diagram focuses on a specific aspect of Claude Code's architecture, making it easy to understand how all the pieces fit together.