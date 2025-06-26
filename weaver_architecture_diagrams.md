# Weaver Architecture Diagrams for Claude Code (DSLModel)

## 1. Weaver Architecture Overview

```mermaid
graph TB
    subgraph "Weaver Core Engine"
        WE[Weaver Engine<br/>weaver_engine.py]
        WE --> |Uses| J2[Jinja2 Templates]
        WE --> |Generates| AG[Artifacts Generator]
        AG --> PM[Pydantic Models]
        AG --> CLI[CLI Commands]
        AG --> TS[Test Suites]
        AG --> DOC[Documentation]
    end
    
    subgraph "Semantic Conventions"
        SCR[Semantic Convention Registry<br/>semconv_registry/]
        YAML[YAML Conventions]
        PY[Python Conventions]
        YAML --> SCR
        PY --> |Converts to| YAML
    end
    
    subgraph "Weaver CLI"
        WCLI[dsl weaver]
        WCLI --> |generate| WE
        WCLI --> |list| SCR
        WCLI --> |validate| VAL[Convention Validator]
        WCLI --> |init| INIT[Registry Initializer]
    end
    
    subgraph "Integration Points"
        OTEL[OTEL Integration]
        FSM[FSM Integration]
        DSL[DSLModel Integration]
        WE --> OTEL
        WE --> FSM
        WE --> DSL
    end
    
    style WE fill:#f9f,stroke:#333,stroke-width:4px
    style SCR fill:#9ff,stroke:#333,stroke-width:2px
```

## 2. Weaver Forge Workflow

```mermaid
graph LR
    subgraph "Input Sources"
        PM[Python Module<br/>my_spec.py]
        YF[YAML File<br/>my_convention.yaml]
        TS[Telemetry Spec<br/>telemetry_spec.py]
    end
    
    subgraph "Forge Process"
        FC[dsl forge]
        BUILD[forge build]
        VAL[forge validate]
        E2E[forge e2e]
        
        FC --> BUILD
        FC --> VAL
        FC --> E2E
    end
    
    subgraph "Convention Processing"
        PL[Python Loader<br/>loader.py]
        CV[Convention Validator]
        YC[YAML Converter]
        
        PM --> PL
        PL --> CV
        CV --> YC
        YF --> CV
    end
    
    subgraph "Generation Pipeline"
        WF[Weaver Forge<br/>Integration]
        WE[Weaver Engine]
        TG[Template Generator]
        
        YC --> WF
        WF --> WE
        WE --> TG
    end
    
    subgraph "Output Artifacts"
        GEN[Generated Code]
        MOD[Pydantic Models]
        CMD[CLI Commands]
        TEST[Test Files]
        DOCS[Documentation]
        
        TG --> GEN
        GEN --> MOD
        GEN --> CMD
        GEN --> TEST
        GEN --> DOCS
    end
    
    BUILD --> PL
    VAL --> CV
    E2E --> TS
    TS --> PL
    
    style FC fill:#f9f,stroke:#333,stroke-width:4px
    style WE fill:#9ff,stroke:#333,stroke-width:2px
```

## 3. Semantic Convention Flow

```mermaid
flowchart TD
    subgraph "Convention Definition"
        PD[Python Definition<br/>@convention decorator]
        YD[YAML Definition<br/>semantic_conventions.yaml]
    end
    
    subgraph "Convention Models"
        ATT[Attribute Model]
        SPAN[Span Model]
        CS[ConventionSet Model]
        
        PD --> ATT
        PD --> SPAN
        ATT --> CS
        SPAN --> CS
        YD --> CS
    end
    
    subgraph "Registry Management"
        REG[Convention Registry]
        VER[Version Control]
        META[Metadata Storage]
        
        CS --> REG
        REG --> VER
        REG --> META
    end
    
    subgraph "Code Generation"
        TPL[Template Selection]
        CTX[Context Building]
        GEN[Code Generation]
        
        REG --> TPL
        META --> CTX
        TPL --> GEN
        CTX --> GEN
    end
    
    subgraph "Output Validation"
        SV[Schema Validation]
        TV[Type Validation]
        OV[OTEL Validation]
        
        GEN --> SV
        GEN --> TV
        GEN --> OV
    end
    
    style REG fill:#f9f,stroke:#333,stroke-width:4px
    style GEN fill:#9ff,stroke:#333,stroke-width:2px
```

## 4. Weaver-OTEL Integration

```mermaid
graph TB
    subgraph "Weaver Layer"
        WC[Weaver Conventions]
        WG[Weaver Generator]
        WT[Weaver Templates]
    end
    
    subgraph "Integration Layer"
        WOI[Weaver-OTEL Integration<br/>weaver_integration.py]
        EWI[Extended Integration<br/>extended_weaver_integration.py]
        FWI[FSM Integration<br/>fsm_weaver_integration.py]
    end
    
    subgraph "OTEL Components"
        TRACE[Tracer]
        SPAN[Span Processor]
        EXP[Exporters]
        ATTR[Attributes]
    end
    
    subgraph "Generated Components"
        OBS[Observable Models]
        INST[Instrumented Code]
        TEL[Telemetry Emitters]
        VAL[Validators]
    end
    
    WC --> WOI
    WG --> WOI
    WT --> WOI
    
    WOI --> OBS
    EWI --> INST
    FWI --> TEL
    
    OBS --> TRACE
    INST --> SPAN
    TEL --> ATTR
    VAL --> ATTR
    
    TRACE --> EXP
    SPAN --> EXP
    
    style WOI fill:#f9f,stroke:#333,stroke-width:4px
    style TRACE fill:#9ff,stroke:#333,stroke-width:2px
```

## 5. Weaver Validation Pipeline

```mermaid
flowchart LR
    subgraph "Input Data"
        SPANS[Telemetry Spans]
        CONV[Conventions]
        SCHEMA[Weaver Schema]
    end
    
    subgraph "Validation Engine"
        WV[Weaver Validator<br/>weaver_otel_validator.py]
        NRM[Normalizer]
        CV[Concurrent Validator]
        
        SPANS --> NRM
        NRM --> WV
        CONV --> WV
        SCHEMA --> WV
        WV --> CV
    end
    
    subgraph "Validation Types"
        SV[Schema Validation]
        AV[Attribute Validation]
        RV[Relationship Validation]
        PV[Performance Validation]
        
        CV --> SV
        CV --> AV
        CV --> RV
        CV --> PV
    end
    
    subgraph "Results Processing"
        RES[Validation Results]
        REP[Report Generator]
        META[Metadata Enrichment]
        
        SV --> RES
        AV --> RES
        RV --> RES
        PV --> RES
        
        RES --> META
        META --> REP
    end
    
    subgraph "Output"
        PASS[✅ Passed]
        FAIL[❌ Failed]
        WARN[⚠️ Warnings]
        PERF[📊 Performance]
        
        REP --> PASS
        REP --> FAIL
        REP --> WARN
        REP --> PERF
    end
    
    style WV fill:#f9f,stroke:#333,stroke-width:4px
    style RES fill:#9ff,stroke:#333,stroke-width:2px
```

## 6. Weaver Health Check System

```mermaid
graph TD
    subgraph "Health Check Components"
        HC[dsl weaver-health]
        OC[Ollama Check]
        WC[Weaver Check]
        RC[Registry Check]
        IC[Integration Check]
    end
    
    subgraph "Ollama Integration"
        OS[Ollama Server]
        OM[Ollama Models]
        OV[Model Validation]
        
        OC --> OS
        OC --> OM
        OM --> OV
    end
    
    subgraph "Weaver Status"
        WI[Weaver Installation]
        WA[Weaver Accessibility]
        WV[Version Check]
        
        WC --> WI
        WC --> WA
        WC --> WV
    end
    
    subgraph "Registry Analysis"
        RS[Registry Status]
        CF[Convention Files]
        CV[Convention Validity]
        
        RC --> RS
        RC --> CF
        CF --> CV
    end
    
    subgraph "System Integration"
        OTEL[OTEL Compatibility]
        DSL[DSLModel Integration]
        LLM[LLM Analysis]
        
        IC --> OTEL
        IC --> DSL
        IC --> LLM
    end
    
    subgraph "Health Report"
        STATUS[Overall Status]
        ISSUES[Issues Found]
        REC[Recommendations]
        MON[Monitoring Mode]
        
        OV --> STATUS
        WV --> STATUS
        CV --> STATUS
        OTEL --> STATUS
        
        STATUS --> ISSUES
        ISSUES --> REC
        STATUS --> MON
    end
    
    HC --> OC
    HC --> WC
    HC --> RC
    HC --> IC
    
    style HC fill:#f9f,stroke:#333,stroke-width:4px
    style STATUS fill:#9ff,stroke:#333,stroke-width:2px
```

## 7. Weaver Template System

```mermaid
graph LR
    subgraph "Template Sources"
        BT[Base Templates<br/>weaver_templates/]
        PT[Python Templates<br/>pydantic_model.j2]
        CT[CLI Templates<br/>cli_command.j2]
        DT[Doc Templates<br/>documentation.j2]
        MT[Metric Templates<br/>metric_dataclass.j2]
    end
    
    subgraph "Template Engine"
        J2[Jinja2 Engine]
        CTX[Context Builder]
        VAR[Variable Resolver]
        FIL[Filter Functions]
        
        BT --> J2
        PT --> J2
        CT --> J2
        DT --> J2
        MT --> J2
        
        CTX --> J2
        VAR --> CTX
        FIL --> J2
    end
    
    subgraph "Context Data"
        CONV[Convention Data]
        META[Metadata]
        CFG[Config Values]
        PROJ[Project Settings]
        
        CONV --> VAR
        META --> VAR
        CFG --> VAR
        PROJ --> VAR
    end
    
    subgraph "Generated Output"
        CODE[Generated Code]
        FMT[Formatting]
        VAL[Validation]
        SAVE[File Writing]
        
        J2 --> CODE
        CODE --> FMT
        FMT --> VAL
        VAL --> SAVE
    end
    
    style J2 fill:#f9f,stroke:#333,stroke-width:4px
    style CODE fill:#9ff,stroke:#333,stroke-width:2px
```

## 8. Weaver E2E Feature Generation

```mermaid
flowchart TD
    subgraph "Feature Specification"
        SPEC[Telemetry Spec<br/>feature_spec.py]
        REQ[Requirements]
        TEL[Telemetry Definition]
        
        REQ --> SPEC
        TEL --> SPEC
    end
    
    subgraph "E2E Pipeline"
        E2E[dsl forge e2e]
        PARSE[Spec Parser]
        PLAN[Generation Plan]
        
        SPEC --> E2E
        E2E --> PARSE
        PARSE --> PLAN
    end
    
    subgraph "Artifact Generation"
        MOD[Model Generation]
        CLI[CLI Generation]
        TEST[Test Generation]
        DOC[Doc Generation]
        OTEL[OTEL Integration]
        
        PLAN --> MOD
        PLAN --> CLI
        PLAN --> TEST
        PLAN --> DOC
        PLAN --> OTEL
    end
    
    subgraph "Feature Components"
        PM[Pydantic Models]
        CC[CLI Commands]
        TS[Test Suite]
        DD[Documentation]
        TI[Telemetry Implementation]
        
        MOD --> PM
        CLI --> CC
        TEST --> TS
        DOC --> DD
        OTEL --> TI
    end
    
    subgraph "Integration & Validation"
        INT[System Integration]
        VAL[E2E Validation]
        DEMO[Demo Generation]
        
        PM --> INT
        CC --> INT
        TI --> INT
        
        INT --> VAL
        VAL --> DEMO
    end
    
    style E2E fill:#f9f,stroke:#333,stroke-width:4px
    style INT fill:#9ff,stroke:#333,stroke-width:2px
```

## 9. Weaver-FSM Integration

```mermaid
stateDiagram-v2
    [*] --> Init: Initialize FSM
    
    state "FSM Definition" as FSM {
        Init --> States: Define States
        States --> Transitions: Define Transitions
        Transitions --> Guards: Add Guards
    }
    
    state "Weaver Integration" as WI {
        Guards --> Observable: Add ObservableFSMMixin
        Observable --> Telemetry: Generate Telemetry
        Telemetry --> Conventions: Create Conventions
    }
    
    state "Code Generation" as CG {
        Conventions --> Models: Generate FSM Models
        Models --> Instrumentation: Add OTEL
        Instrumentation --> Validation: Validate Spans
    }
    
    state "Runtime" as RT {
        Validation --> Execute: Run FSM
        Execute --> Emit: Emit Telemetry
        Emit --> Monitor: Monitor States
        Monitor --> Execute: Feedback Loop
    }
    
    Monitor --> [*]: Complete
```

## 10. Weaver Development Workflow

```mermaid
graph TD
    subgraph "Development Start"
        REQ[Requirements]
        TEL[Telemetry Design]
        
        REQ --> TEL
    end
    
    subgraph "Convention Authoring"
        PYDEF[Python Definition]
        YDEF[YAML Definition]
        
        TEL --> PYDEF
        TEL --> YDEF
    end
    
    subgraph "Weaver Processing"
        BUILD[dsl forge build]
        VAL[dsl weaver validate]
        GEN[dsl weaver generate]
        
        PYDEF --> BUILD
        YDEF --> VAL
        BUILD --> GEN
        VAL --> GEN
    end
    
    subgraph "Development Artifacts"
        MOD[Models]
        CLI[Commands]
        TEST[Tests]
        
        GEN --> MOD
        GEN --> CLI
        GEN --> TEST
    end
    
    subgraph "Integration Testing"
        UNIT[Unit Tests]
        INT[Integration Tests]
        E2E[E2E Tests]
        
        TEST --> UNIT
        TEST --> INT
        TEST --> E2E
    end
    
    subgraph "Deployment"
        PKG[Package]
        DOC[Documentation]
        REL[Release]
        
        MOD --> PKG
        CLI --> PKG
        GEN --> DOC
        PKG --> REL
        DOC --> REL
    end
    
    style TEL fill:#f9f,stroke:#333,stroke-width:4px
    style GEN fill:#9ff,stroke:#333,stroke-width:2px
    style REL fill:#9f9,stroke:#333,stroke-width:2px
```

## Summary

These diagrams visualize the comprehensive Weaver integration in Claude Code (DSLModel):

1. **Architecture Overview**: Shows how Weaver Engine is the core that generates all artifacts
2. **Forge Workflow**: Illustrates the complete pipeline from specs to generated code
3. **Semantic Convention Flow**: Details how conventions are defined, processed, and used
4. **OTEL Integration**: Shows the deep integration between Weaver and OpenTelemetry
5. **Validation Pipeline**: Demonstrates the comprehensive validation system
6. **Health Check System**: Visualizes the monitoring and health verification flow
7. **Template System**: Shows how Jinja2 templates are used for code generation
8. **E2E Feature Generation**: Illustrates end-to-end feature creation from telemetry specs
9. **FSM Integration**: Shows state machine integration with observability
10. **Development Workflow**: Complete developer journey using Weaver

The Weaver system implements a "Define Once, Generate Everything" philosophy where OpenTelemetry semantic conventions drive the entire development process, ensuring consistency, type safety, and built-in observability across the Claude Code system.