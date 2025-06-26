# DSLModel Subsystem Diagrams

## 1. Consolidated CLI Migration Path

```mermaid
graph TD
    subgraph "Legacy Commands (Deprecated)"
        L1[dsl gen]
        L2[dsl evolve]
        L3[dsl agents]
        L4[dsl validate]
        L5[dsl forge]
        L6[dsl worktree]
        L7[dsl demo]
        L8[dsl 8020]
        L9[dsl swarm]
        L10[dsl telemetry]
    end
    
    subgraph "Consolidated Commands"
        subgraph "Core (80%)"
            C1[dsl dsl core gen]
            C2[dsl dsl core evolve]
            C3[dsl dsl core agent]
            C4[dsl dsl core validate]
            C5[dsl dsl core dev]
            C6[dsl dsl core demo]
        end
        
        subgraph "Advanced (20%)"
            A1[dsl dsl advanced security]
            A2[dsl dsl advanced telemetry]
            A3[dsl dsl advanced research]
        end
    end
    
    L1 -.->|migrate| C1
    L2 -.->|migrate| C2
    L3 -.->|migrate| C3
    L4 -.->|migrate| C4
    L5 -.->|migrate| C5
    L6 -.->|migrate| C5
    L7 -.->|migrate| C6
    L8 -.->|migrate| C4
    L9 -.->|migrate| C3
    L10 -.->|migrate| A2
```

## 2. Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Agent Created
    
    Idle --> Claiming: Feature Assigned
    Claiming --> Working: Worktree Claimed
    Claiming --> Error: Claim Failed
    
    Working --> Validating: Work Complete
    Working --> Error: Work Failed
    
    Validating --> Submitting: Tests Pass
    Validating --> Working: Tests Fail
    
    Submitting --> Finished: PR Created
    Submitting --> Error: Submit Failed
    
    Finished --> Idle: Ready for Next
    Error --> Idle: Reset
    
    note right of Working
        Isolated in worktree
        Emitting progress spans
    end note
    
    note right of Validating
        Running test suite
        OTEL validation
    end note
```

## 3. Telemetry Flow Detail

```mermaid
flowchart LR
    subgraph "Span Generation"
        A[Agent Activity]
        E[Evolution Events]
        V[Validation Results]
        S[System Metrics]
    end
    
    subgraph "Span Processing"
        ENRICH[Enrich<br/>Context]
        FILTER[Filter<br/>Noise]
        BATCH[Batch<br/>Optimize]
        COMPRESS[Compress<br/>Storage]
    end
    
    subgraph "Real-time Analysis"
        PATTERN[Pattern<br/>Detection]
        ANOMALY[Anomaly<br/>Detection]
        PREDICT[Predictive<br/>Analysis]
    end
    
    subgraph "Actions"
        ALERT[Alerts]
        REMEDIATE[Auto-fix]
        EVOLVE[Evolution]
        REPORT[Reports]
    end
    
    A --> ENRICH
    E --> ENRICH
    V --> ENRICH
    S --> ENRICH
    
    ENRICH --> FILTER
    FILTER --> BATCH
    BATCH --> COMPRESS
    
    COMPRESS --> PATTERN
    COMPRESS --> ANOMALY
    COMPRESS --> PREDICT
    
    PATTERN --> ALERT
    PATTERN --> EVOLVE
    ANOMALY --> REMEDIATE
    PREDICT --> REPORT
```

## 4. Weaver Integration Architecture

```mermaid
graph TB
    subgraph "Semantic Conventions"
        YAML[YAML Definitions]
        PYTHON[Python Classes]
        SCHEMA[JSON Schema]
    end
    
    subgraph "Weaver Engine"
        PARSER[Convention Parser]
        VALIDATOR[Schema Validator]
        GENERATOR[Code Generator]
        REGISTRY[Convention Registry]
    end
    
    subgraph "Generated Artifacts"
        MODELS[Pydantic Models]
        VALIDATORS[Validation Rules]
        TELEMETRY[Telemetry Classes]
        DOCS[Documentation]
    end
    
    subgraph "Runtime Integration"
        SPAN_VAL[Span Validation]
        TYPE_SAFE[Type Safety]
        AUTO_COMPLETE[Autocomplete]
    end
    
    YAML --> PARSER
    PYTHON --> PARSER
    SCHEMA --> VALIDATOR
    
    PARSER --> REGISTRY
    VALIDATOR --> REGISTRY
    REGISTRY --> GENERATOR
    
    GENERATOR --> MODELS
    GENERATOR --> VALIDATORS
    GENERATOR --> TELEMETRY
    GENERATOR --> DOCS
    
    MODELS --> SPAN_VAL
    VALIDATORS --> SPAN_VAL
    TELEMETRY --> TYPE_SAFE
    TYPE_SAFE --> AUTO_COMPLETE
```

## 5. Evolution Learning Cycle

```mermaid
graph LR
    subgraph "Data Collection"
        SUCCESS[Success Patterns]
        FAILURE[Failure Patterns]
        PERF[Performance Data]
        USER[User Feedback]
    end
    
    subgraph "Pattern Analysis"
        ML[Machine Learning]
        STATS[Statistical Analysis]
        TREND[Trend Detection]
    end
    
    subgraph "Knowledge Base"
        PATTERNS[Pattern DB]
        RULES[Evolution Rules]
        WEIGHTS[Confidence Weights]
    end
    
    subgraph "Application"
        PRIORITIZE[Priority Scoring]
        PREDICT[Success Prediction]
        OPTIMIZE[Parameter Tuning]
    end
    
    SUCCESS --> ML
    FAILURE --> ML
    PERF --> STATS
    USER --> TREND
    
    ML --> PATTERNS
    STATS --> RULES
    TREND --> WEIGHTS
    
    PATTERNS --> PRIORITIZE
    RULES --> PREDICT
    WEIGHTS --> OPTIMIZE
    
    PRIORITIZE --> Next[Next Evolution]
    PREDICT --> Next
    OPTIMIZE --> Next
```

## 6. Worktree Isolation Model

```mermaid
graph TD
    subgraph "Main Repository"
        MAIN[main branch]
        DEV[dev branch]
    end
    
    subgraph "Worktree Pool"
        subgraph "Agent 1 Worktree"
            W1[worktree-agent1]
            B1[feature/auth]
            F1[Files Modified]
        end
        
        subgraph "Agent 2 Worktree"
            W2[worktree-agent2]
            B2[feature/api]
            F2[Files Modified]
        end
        
        subgraph "Evolution Worktree"
            W3[worktree-evolution]
            B3[evolution/perf]
            F3[Experiments]
        end
    end
    
    subgraph "Integration"
        PR1[Pull Request 1]
        PR2[Pull Request 2]
        PR3[Evolution PR]
    end
    
    MAIN --> W1
    MAIN --> W2
    MAIN --> W3
    
    W1 --> B1
    W2 --> B2
    W3 --> B3
    
    B1 --> F1
    B2 --> F2
    B3 --> F3
    
    F1 --> PR1
    F2 --> PR2
    F3 --> PR3
    
    PR1 --> MAIN
    PR2 --> MAIN
    PR3 --> DEV
```

## 7. Validation Hierarchy

```mermaid
graph TB
    subgraph "Validation Levels"
        L1[Level 1: Syntax<br/>Basic Correctness]
        L2[Level 2: Semantic<br/>Business Logic]
        L3[Level 3: Integration<br/>System Compatibility]
        L4[Level 4: Performance<br/>Efficiency Metrics]
        L5[Level 5: Security<br/>Vulnerability Scan]
        L6[Level 6: OTEL<br/>Telemetry Compliance]
        L7[Level 7: Weaver<br/>Convention Adherence]
        L8[Level 8: Evolution<br/>Improvement Verified]
        L9[Level 9: 8020<br/>Value Delivery]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
    L6 --> L7
    L7 --> L8
    L8 --> L9
    
    L9 --> PASS[Validation Complete]
    
    L1 -.->|Fail| FIX[Fix & Retry]
    L2 -.->|Fail| FIX
    L3 -.->|Fail| FIX
    L4 -.->|Fail| FIX
    L5 -.->|Fail| FIX
    L6 -.->|Fail| FIX
    L7 -.->|Fail| FIX
    L8 -.->|Fail| FIX
    L9 -.->|Fail| FIX
    
    FIX -.-> L1
```

## 8. Autonomous Decision Flow

```mermaid
flowchart TD
    subgraph "Input Analysis"
        TELEMETRY[Telemetry Stream]
        ALERTS[System Alerts]
        PATTERNS[Pattern DB]
    end
    
    subgraph "Decision Engine"
        ANALYZE[Situation Analysis]
        SCORE[Risk Scoring]
        OPTIONS[Generate Options]
        SELECT[Select Action]
    end
    
    subgraph "Confidence Evaluation"
        HISTORICAL[Historical Success]
        IMPACT[Impact Assessment]
        SAFETY[Safety Check]
        CONFIDENCE[Confidence Score]
    end
    
    subgraph "Execution"
        TEST[Test in Worktree]
        VALIDATE[Validate Results]
        APPLY[Apply to Production]
        ROLLBACK[Rollback if Needed]
    end
    
    TELEMETRY --> ANALYZE
    ALERTS --> ANALYZE
    PATTERNS --> ANALYZE
    
    ANALYZE --> SCORE
    SCORE --> OPTIONS
    OPTIONS --> SELECT
    
    SELECT --> HISTORICAL
    HISTORICAL --> IMPACT
    IMPACT --> SAFETY
    SAFETY --> CONFIDENCE
    
    CONFIDENCE -->|High| TEST
    CONFIDENCE -->|Low| MANUAL[Manual Review]
    
    TEST --> VALIDATE
    VALIDATE -->|Pass| APPLY
    VALIDATE -->|Fail| ROLLBACK
```

## 9. Security Architecture

```mermaid
graph TB
    subgraph "Attack Surface"
        API[API Endpoints]
        CLI[CLI Commands]
        DEPS[Dependencies]
        CONFIG[Configuration]
    end
    
    subgraph "Security Layers"
        AUTH[Authentication]
        AUTHZ[Authorization]
        VALID[Input Validation]
        ENCRYPT[Encryption]
    end
    
    subgraph "Monitoring"
        IDS[Intrusion Detection]
        AUDIT[Audit Logging]
        THREAT[Threat Intel]
        COMPLIANCE[Compliance Check]
    end
    
    subgraph "Response"
        BLOCK[Block Attack]
        ALERT_SEC[Security Alert]
        PATCH[Auto Patch]
        ISOLATE[Isolate System]
    end
    
    API --> AUTH
    CLI --> AUTH
    DEPS --> VALID
    CONFIG --> ENCRYPT
    
    AUTH --> AUTHZ
    AUTHZ --> IDS
    VALID --> IDS
    ENCRYPT --> AUDIT
    
    IDS --> THREAT
    AUDIT --> COMPLIANCE
    
    THREAT --> BLOCK
    THREAT --> ALERT_SEC
    COMPLIANCE --> PATCH
    ALERT_SEC --> ISOLATE
```

## 10. Performance Optimization Pipeline

```mermaid
graph LR
    subgraph "Measurement"
        BASELINE[Baseline Metrics]
        CURRENT[Current Metrics]
        COMPARE[Delta Analysis]
    end
    
    subgraph "Identification"
        BOTTLENECK[Bottlenecks]
        INEFFICIENT[Inefficiencies]
        REDUNDANT[Redundancies]
    end
    
    subgraph "Optimization"
        CACHE[Add Caching]
        PARALLEL[Parallelize]
        ALGORITHM[Better Algorithms]
        REDUCE[Reduce Overhead]
    end
    
    subgraph "Validation"
        BENCHMARK[Benchmark]
        PROFILE[Profile]
        LOAD_TEST[Load Test]
    end
    
    BASELINE --> COMPARE
    CURRENT --> COMPARE
    
    COMPARE --> BOTTLENECK
    COMPARE --> INEFFICIENT
    COMPARE --> REDUNDANT
    
    BOTTLENECK --> CACHE
    BOTTLENECK --> PARALLEL
    INEFFICIENT --> ALGORITHM
    REDUNDANT --> REDUCE
    
    CACHE --> BENCHMARK
    PARALLEL --> BENCHMARK
    ALGORITHM --> PROFILE
    REDUCE --> LOAD_TEST
    
    BENCHMARK --> DEPLOY[Deploy if Better]
    PROFILE --> DEPLOY
    LOAD_TEST --> DEPLOY
```