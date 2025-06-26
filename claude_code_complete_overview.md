# Claude Code Complete Overview

## Master Architecture Diagram

```mermaid
graph TB
    subgraph "Claude Code Ecosystem"
        subgraph "Tools Layer"
            TOOLS[18+ Tool Types]
            FILE[File Ops<br/>Read/Write/Edit]
            BASH[Bash Ops<br/>Commands]
            SEARCH[Search Ops<br/>Grep/Glob/LS]
            WEB[Web Ops<br/>Fetch/Search]
            AGENT[Agent Ops<br/>Tasks]
            OTHER[Todo/Notebook/Special]
        end
        
        subgraph "Telemetry Layer"
            WEAVER[Weaver Models]
            SEMCONV[Semantic Conventions]
            WRAPPER[Tool Wrappers]
            SPANS[OTEL Spans]
        end
        
        subgraph "Integration Layer"
            DEC[Decorators]
            MID[Middleware]
            CTX[Context Managers]
            DIRECT[Direct Wrappers]
        end
        
        subgraph "Data Flow"
            INPUT[User Requests]
            EXEC[Tool Execution]
            TELEM[Telemetry Generation]
            OUTPUT[Results + Metrics]
        end
        
        subgraph "Backends"
            CONSOLE[Console Export]
            JAEGER[Jaeger Traces]
            PROM[Prometheus Metrics]
            CUSTOM[Custom Backends]
        end
    end
    
    %% Tool connections
    TOOLS --> FILE
    TOOLS --> BASH
    TOOLS --> SEARCH
    TOOLS --> WEB
    TOOLS --> AGENT
    TOOLS --> OTHER
    
    %% Telemetry flow
    SEMCONV --> WEAVER
    WEAVER --> WRAPPER
    WRAPPER --> SPANS
    
    %% Integration flow
    FILE --> DEC
    BASH --> MID
    SEARCH --> CTX
    WEB --> DIRECT
    AGENT --> MID
    OTHER --> MID
    
    %% Data flow
    INPUT --> EXEC
    EXEC --> WRAPPER
    WRAPPER --> TELEM
    TELEM --> OUTPUT
    
    %% Backend connections
    SPANS --> CONSOLE
    SPANS --> JAEGER
    SPANS --> PROM
    SPANS --> CUSTOM
    
    %% Styling
    style TOOLS fill:#f9f,stroke:#333,stroke-width:4px
    style WEAVER fill:#bbf,stroke:#333,stroke-width:3px
    style SPANS fill:#bfb,stroke:#333,stroke-width:3px
    style OUTPUT fill:#ffd,stroke:#333,stroke-width:3px
```

## Key Metrics and Capabilities

```mermaid
mindmap
  root((Claude Code))
    Tools
      18+ Tool Types
      File Operations
        Read
        Write
        Edit
        MultiEdit
      Command Execution
        Bash
      Search Operations
        Grep
        Glob
        LS
      Web Operations
        WebFetch
        WebSearch
      Agent Operations
        Task with Progress
      Management
        TodoRead/Write
        NotebookRead/Edit
    Telemetry
      OpenTelemetry Spans
      Weaver Models
      Semantic Conventions
      Real-time Metrics
      Error Tracking
      Progress Events
    Integration
      4 Pattern Types
        Decorators
        Middleware
        Context Managers
        Direct Wrappers
      Session Management
      Metrics Aggregation
    Observability
      Span Attributes
        Base Attributes
        Tool-Specific
        Performance Metrics
      Span Relationships
        Parent-Child
        Events
        Status Tracking
      Export Options
        Console
        Jaeger
        Prometheus
        Custom Backends
```

## Complete Feature Matrix

| Category | Tools | Telemetry Features | Integration Options |
|----------|-------|--------------------|---------------------|
| **File Operations** | Read, Write, Edit, MultiEdit | Path, operation, size, lines affected | All patterns supported |
| **Bash Operations** | Command execution | Command, exit code, duration, timeout | Middleware preferred |
| **Search Operations** | Grep, Glob, LS | Pattern, path, results count | Context managers useful |
| **Web Operations** | WebFetch, WebSearch | URL, operation type, response size, cache | Direct wrapper common |
| **Agent Operations** | Task execution | ID, task, status, progress events | Middleware with events |
| **Todo Operations** | Read, Write | Todo count, status breakdown | Simple wrapper |
| **Notebook Operations** | Read, Edit cells | Path, cell ID, cell type | Specialized wrapper |
| **Special Operations** | Plan exit, Unknown | Custom attributes | Flexible handling |

## Benefits Summary

1. **Complete Observability** - Every tool action is tracked with detailed telemetry
2. **Type-Safe Models** - Weaver-generated Pydantic models ensure data consistency  
3. **Flexible Integration** - Multiple patterns for different use cases
4. **Performance Tracking** - Duration, success rates, and detailed metrics
5. **Error Visibility** - Automatic exception capture and status tracking
6. **Progress Monitoring** - Real-time progress events for long operations
7. **Standards Compliance** - Full OpenTelemetry compliance
8. **Easy Debugging** - Detailed spans with all context needed
9. **Metrics Aggregation** - Session and global metrics automatically collected
10. **Extensible Design** - Easy to add new tools and attributes

## Quick Start Integration

```python
# 1. Import the wrapper
from dslmodel.claude_code_weaver_wrapper import wrapped_tools

# 2. Use wrapped tools - telemetry is automatic!
result = wrapped_tools.read("/path/to/file.py")
result = wrapped_tools.bash("python test.py")
result = wrapped_tools.task("Analyze codebase", "Find security issues")

# 3. Get metrics summary
metrics = wrapped_tools.get_metrics_summary()
print(metrics)
```

That's it! Complete telemetry for all Claude Code operations with minimal code changes.