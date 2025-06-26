# Evolution System Telemetry

**Version:** 0.1.0

This feature was auto-generated from telemetry specifications.

## Overview

Evolution System Telemetry provides comprehensive telemetry instrumentation with 6 defined spans.

## Installation

```bash
pip install dslmodel
```

## Usage

### CLI Commands

```bash
# Show status
dsl evolution_system status

# Run operations
dsl evolution_system run --config config.yaml
```

### Python API

```python
from dslmodel.evolution_system import EvolutionSystem

# Initialize
feature = EvolutionSystem()

# Get status
status = feature.get_status()

# Run operations
result = feature.run()
```

## Telemetry Spans

The following spans are emitted:


### dslmodel.evolution.analyze

Evolution system analysis phase - detecting improvement opportunities

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.analysis_type` (string): Type of analysis being performed (test_failures, performance_metrics, code_quality, full_analysis)
  - `evolution.issues_found` (int): Number of issues discovered during analysis
  - `evolution.analysis_duration_ms` (int): Duration of analysis phase in milliseconds
  - `evolution.repository_path` (string): Path to the repository being analyzed

### dslmodel.evolution.generate

Evolution improvement generation - creating improvement recommendations

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.improvement_id` (string): Unique identifier for the generated improvement
  - `evolution.improvement_type` (string): Type of improvement (performance_optimization, code_fix, refactoring, security_fix, dependency_update)
  - `evolution.confidence_score` (double): Confidence score for the improvement (0.0 to 1.0)
  - `evolution.estimated_effort_hours` (int): Estimated effort to implement the improvement in hours
  - `evolution.priority` (string): Priority level (critical, high, medium, low)
  - `evolution.target_files` (string[]): Files that would be affected by this improvement

### dslmodel.evolution.apply

Evolution improvement application - implementing improvements

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.improvement_id` (string): Unique identifier for the applied improvement
  - `evolution.application_mode` (string): Mode of improvement application (automatic, manual, dry_run, assisted)
  - `evolution.application_result` (string): Result of the improvement application (success, failed, partial, skipped)
  - `evolution.files_modified` (string[]): List of files modified during improvement application
  - `evolution.application_duration_ms` (int): Duration of improvement application in milliseconds
  - `evolution.worktree_path` (string): Path to worktree used for isolated testing

### dslmodel.evolution.learn

Evolution system learning phase - updating patterns from historical data

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.patterns_analyzed` (int): Number of historical patterns analyzed
  - `evolution.success_rate` (double): Overall success rate from historical data (0.0 to 1.0)
  - `evolution.patterns_updated` (int): Number of improvement patterns updated based on learning
  - `evolution.confidence_adjustments` (int): Number of confidence score adjustments made
  - `evolution.learning_model_version` (string): Version of the learning model used

### dslmodel.evolution.validate

Evolution improvement validation - verifying improvement effectiveness

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.improvement_id` (string): Unique identifier for the validated improvement
  - `evolution.validation_type` (string): Type of validation (test_execution, performance_benchmark, security_scan, integration_test, user_acceptance)
  - `evolution.validation_result` (string): Result of the validation (passed, failed, warning, inconclusive)
  - `evolution.metrics_before` (string): JSON string of metrics before improvement
  - `evolution.metrics_after` (string): JSON string of metrics after improvement
  - `evolution.performance_improvement` (double): Percentage improvement in performance (e.g., 0.25 for 25% improvement)

### dslmodel.evolution.worktree

Evolution worktree coordination - managing isolated testing environments

**Attributes:**
  - `evolution.session_id` (string): Unique identifier for the evolution session
  - `evolution.worktree_id` (string): Unique identifier for the worktree
  - `evolution.worktree_action` (string): Worktree action (create, test, validate, cleanup, merge)
  - `evolution.branch_name` (string): Git branch name for the worktree
  - `evolution.test_results` (string): JSON string of test execution results
  - `evolution.isolation_level` (string): Level of isolation (full, partial, none)


## Configuration

Configuration can be provided via YAML file:

```yaml
# config.yaml
evolution_system:
  enabled: true
  options:
    verbose: true
```
