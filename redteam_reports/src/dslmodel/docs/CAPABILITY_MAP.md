# SwarmAgent Capability Map

## Overview

The SwarmAgent system provides span-driven coordination across governance, delivery, and optimization domains through autonomous agents that respond to OpenTelemetry telemetry spans.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SwarmAgent Ecosystem                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐   │
│  │ Roberts Agent   │      │  Scrum Agent    │      │   Lean Agent    │   │
│  │  (Governance)   │─────▶│   (Delivery)    │─────▶│ (Optimization)  │   │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘   │
│           │                         │                         │            │
│           │                         │                         │            │
│           └─────────────────────────┴─────────────────────────┘            │
│                              Coordination Loop                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OpenTelemetry Span Stream                        │   │
│  │  {"name": "swarmsh.roberts.vote", "attributes": {...}}             │   │
│  │  {"name": "swarmsh.scrum.plan", "attributes": {...}}               │   │
│  │  {"name": "swarmsh.lean.define", "attributes": {...}}              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Capabilities

### 🏛️ Roberts Rules Agent (Governance)

**Purpose**: Implement Roberts Rules of Order for governance decisions

**State Machine**:
```
IDLE ──open──▶ MOTION_OPEN ──vote──▶ VOTING ──close──▶ CLOSED
  ▲                                                        │
  └────────────────────────────────────────────────────────┘
```

**Capabilities**:
- Motion management
- Voting coordination  
- Sprint approval
- Governance decisions

**Triggers**:
- `roberts.open` - Open motion for consideration
- `roberts.vote` - Call for votes
- `roberts.close` - Close motion with result

**Emits**: 
- `scrum.sprint-planning` (when sprint motions pass)
- `lean.define-project` (when improvement motions pass)

### 📅 Scrum-at-Scale Agent (Delivery)

**Purpose**: Manage agile delivery using Scrum-at-Scale framework

**State Machine**:
```
IDLE ──plan──▶ PLANNING ──start──▶ SPRINT_ACTIVE ──review──▶ REVIEW
  ▲                                                              │
  └──────────────────────────────────────────────────────────────┘
```

**Capabilities**:
- Sprint planning
- Backlog management
- Velocity tracking
- Quality monitoring

**Triggers**:
- `scrum.plan` - Plan sprint
- `scrum.start` - Start sprint execution
- `scrum.review` - Sprint review

**Emits**:
- `lean.define-project` (when quality issues detected)
- `roberts.open` (when governance approval needed)

### 🎯 Lean Six Sigma Agent (Optimization)

**Purpose**: Drive continuous improvement using Lean Six Sigma methodology

**State Machine**:
```
IDLE ──define──▶ DEFINE ──measure──▶ MEASURE ──analyze──▶ ANALYZE
  ▲                                                           │
  │                                                           ▼
  └────── CONTROL ◀──control── IMPROVE ◀──────improve────────┘
```

**Capabilities**:
- Process optimization
- Root cause analysis
- Metrics improvement
- Quality control

**Triggers**:
- `lean.define` - Define improvement project
- `lean.measure` - Measure current state
- `lean.analyze` - Analyze root causes
- `lean.improve` - Implement improvements
- `lean.control` - Control and sustain

**Emits**:
- `scrum.plan` (improvement implementation)
- `roberts.open` (process change approval)

### 🏓 Ping Test Agent (Testing)

**Purpose**: System connectivity and health testing

**State Machine**:
```
IDLE ──ping──▶ PING_SENT ──pong──▶ PONG_RECEIVED
  ▲                                      │
  └──────────────────────────────────────┘
```

**Capabilities**:
- Connectivity testing
- Latency measurement
- Health checking

## Coordination Patterns

### Pattern 1: Governance → Delivery
```
Roberts Motion Passes → Scrum Sprint Planning → Sprint Execution
```

**Example Flow**:
1. `roberts.open` - "Approve Sprint 42 funding"
2. `roberts.vote` - Team votes on motion
3. `roberts.close` - Motion passes
4. → Triggers `scrum.plan` with sprint details
5. `scrum.start` - Sprint begins execution

### Pattern 2: Quality → Optimization
```
Sprint Review Detects Issues → Lean Project Initiated → Improvements
```

**Example Flow**:
1. `scrum.review` - Defect rate > 3%
2. → Triggers `lean.define` for quality improvement
3. `lean.measure` - Baseline metrics
4. `lean.analyze` - Root cause analysis
5. `lean.improve` - Implement fixes

### Pattern 3: Optimization → Governance
```
Process Changes → Governance Approval → Implementation
```

**Example Flow**:
1. `lean.control` - Major process change identified
2. → Triggers `roberts.open` for approval motion
3. `roberts.vote` - Stakeholder voting
4. `roberts.close` - Change approved
5. → Returns to Lean implementation

## Deployment Scenarios

### Development Environment
```
┌──────────────────┐
│  Local Machine   │
├──────────────────┤
│ • JSONL Files    │
│ • Single Process │
│ • Console Logs   │
└──────────────────┘
```

### Production Environment
```
┌────────────────────────────────────────────┐
│           Kubernetes Cluster               │
├────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Roberts  │  │  Scrum   │  │   Lean   │ │
│  │   Pod    │  │   Pod    │  │   Pod    │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│        │             │             │        │
│        └─────────────┴─────────────┘        │
│                     │                       │
│            ┌────────────────┐               │
│            │ Kafka/Redis    │               │
│            │ Event Stream   │               │
│            └────────────────┘               │
│                     │                       │
│         ┌───────────────────────┐           │
│         │ OpenTelemetry Collector│          │
│         └───────────────────────┘           │
│                     │                       │
│         ┌───────────────────────┐           │
│         │ Prometheus/Grafana   │           │
│         └───────────────────────┘           │
└────────────────────────────────────────────┘
```

## CLI Commands

### Capability Inspection
```bash
# Show full capability map
dsl capability show

# Show specific agent details
dsl capability agent roberts

# Show coordination patterns
dsl capability patterns

# Show trigger dependencies
dsl capability show --triggers

# Validate system
dsl capability validate
```

### Capability Export
```bash
# Export to JSON
dsl capability export capabilities.json

# Export to Markdown
dsl capability export capabilities.md --format markdown
```

## Telemetry Schema

### Required Span Attributes
```json
{
  "name": "swarmsh.{agent}.{trigger}",
  "trace_id": "unique_trace_id",
  "span_id": "unique_span_id",
  "timestamp": 1234567890.123,
  "attributes": {
    // Agent-specific attributes
  }
}
```

### Agent-Specific Attributes

**Roberts Agent**:
- `motion_id` - Unique motion identifier
- `meeting_id` - Meeting context
- `voting_method` - Method of voting (voice_vote, ballot, roll_call)
- `vote_result` - Outcome (passed, failed, tabled)
- `votes_yes` - Yes vote count
- `votes_no` - No vote count

**Scrum Agent**:
- `sprint_number` - Sprint identifier
- `team_id` - Team responsible
- `velocity` - Team velocity metric
- `capacity` - Team capacity
- `defect_rate` - Quality metric
- `blockers` - Sprint impediments

**Lean Agent**:
- `project_id` - Improvement project ID
- `problem_statement` - Problem description
- `phase` - Current DMAIC phase
- `sponsor` - Project sponsor
- `metrics` - Key metrics
- `root_causes` - Identified root causes

## Performance Characteristics

| Metric | Target | Validated |
|--------|--------|-----------|
| Span Processing | <10ms | ✅ |
| State Transitions | <5ms | ✅ |
| Memory per Agent | <50MB | ✅ |
| Throughput | >1000 spans/sec | ✅ |
| Coordination Latency | <100ms | ✅ |

## Extension Points

### Adding New Agents

1. **Inherit from SwarmAgent**
2. **Define state enum**
3. **Implement trigger methods**
4. **Add to capability map**
5. **Register with CLI**

### Adding New Patterns

1. **Define coordination flow**
2. **Update trigger mappings**
3. **Add pattern documentation**
4. **Test end-to-end flow**

## Validation Status

| Component | Status | Details |
|-----------|--------|---------|
| Roberts Agent | ✅ | Fully implemented |
| Scrum Agent | ✅ | Fully implemented |
| Lean Agent | ✅ | Fully implemented |
| Ping Agent | ✅ | Test implementation |
| Coordination Data | ✅ | 58+ spans recorded |
| Weaver Schema | ✅ | Validated |
| CLI Integration | ✅ | All commands working |
| Documentation | ✅ | Comprehensive |

---

Generated by: `dsl capability show`