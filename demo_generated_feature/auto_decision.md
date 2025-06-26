# Autonomous Decision Engine

**Version:** 0.1.0

This feature was auto-generated from telemetry specifications.

## Overview

Autonomous Decision Engine provides comprehensive telemetry instrumentation with 6 defined spans.

## Installation

```bash
pip install dslmodel
```

## Usage

### CLI Commands

```bash
# Show status
dsl auto_decision status

# Run operations
dsl auto_decision run --config config.yaml
```

### Python API

```python
from dslmodel.auto_decision import AutoDecision

# Initialize
feature = AutoDecision()

# Get status
status = feature.get_status()

# Run operations
result = feature.run()
```

## Telemetry Spans

The following spans are emitted:


### swarmsh.autonomous.system_analysis

System state analysis and metric calculation

**Attributes:**
  - `completion_rate` (double): Work completion rate (0.0-1.0)
  - `active_agents` (int): Number of active agents
  - `work_queue_size` (int): Size of work queue
  - `health_score` (double): Overall system health score (0.0-1.0)
  - `health_state` (string): System health state (critical, degraded, healthy, optimal)

### swarmsh.autonomous.decision_generation

Autonomous decision generation based on system state

**Attributes:**
  - `decision_count` (int): Number of decisions generated
  - `highest_priority` (int): Priority of highest priority decision
  - `decision_types` (string[]): Types of decisions generated

### swarmsh.autonomous.decision_execution

Execution of autonomous decisions

**Attributes:**
  - `decision_id` (string): Unique decision identifier
  - `decision_type` (string): Type of decision being executed
  - `execution_result` (string): Result of decision execution
  - `confidence` (double): Decision confidence score

### swarmsh.autonomous.cycle_complete

Complete autonomous decision cycle

**Attributes:**
  - `cycle_duration_ms` (int): Duration of complete cycle in milliseconds
  - `decisions_executed` (int): Number of decisions executed
  - `decisions_failed` (int): Number of decisions that failed
  - `system_improvement` (boolean): Whether system improvement was achieved

### swarmsh.autonomous.scaling_decision

Agent scaling decision (up or down)

**Attributes:**
  - `scaling_direction` (string): Scaling direction (up, down)
  - `current_agents` (int): Current number of agents
  - `target_agents` (int): Target number of agents
  - `trigger_reason` (string): Reason for scaling decision

### swarmsh.autonomous.coordination_improvement

Coordination system improvement action

**Attributes:**
  - `improvement_type` (string): Type of coordination improvement
  - `queue_size_before` (int): Work queue size before improvement
  - `queue_size_after` (int): Work queue size after improvement


## Configuration

Configuration can be provided via YAML file:

```yaml
# config.yaml
auto_decision:
  enabled: true
  options:
    verbose: true
```
