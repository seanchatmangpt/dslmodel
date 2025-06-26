# DSLModel + OpenTelemetry + FSMMixin Integration

## File Organization

### Core Integration (`/src/dslmodel/integrations/otel/`)
- **`weaver_integration.py`** - Core Weaver Forge integration
- **`extended_weaver_integration.py`** - Extended Weaver features
- **`fsm_weaver_integration.py`** - FSM + Weaver integration
- **`models/dslmodel_attributes.py`** - Generated Pydantic models from semantic conventions
- **`metrics/dslmodel_metrics.py`** - Generated metric dataclasses

### Workflows (`/src/dslmodel/workflows/`)
- **`workflow_orchestrator.py`** - DSLModel + OTEL + FSMMixin orchestrator
- **`advanced_workflow_fsm.py`** - Complex FSM with conditional transitions

### Examples (`/src/dslmodel/examples/otel/`)
- **`working_fsm_demo.py`** - Practical working example (✅ **TESTED**)
- **`simple_fsm_demo.py`** - Minimal FSM demonstration

### Tests (`/src/dslmodel/integrations/otel/tests/`)
- **`test_integration.py`** - Basic integration validation tests
- **`full_loop_test.py`** - Complete end-to-end integration test

## Summary

Successfully integrated three powerful components:

1. **DSLModel** - Pydantic-based models with rich mixins
2. **OpenTelemetry Models** - Generated from semantic conventions via Weaver  
3. **FSMMixin** - State machine capabilities with AI-powered transitions

## Verified Integration (from `full_loop_test.py`)

### ✅ **Test Results**:
- **LM Model**: ollama/qwen3 initialized successfully
- **Workflows Created**: 4 (data-pipeline, ml-training, api-validation, report-generation)
- **Workflows Successful**: 3 completed
- **Workflows Failed**: 1 (simulated failure for testing)
- **OTEL Validations Passed**: 4/4 (100% validation success)
- **Telemetry Spans Generated**: 4 complete span records
- **Export Success**: ✅ JSONL format compatible with OTEL collectors

### **Integration Components Verified**:
- ✅ DSLModel (Pydantic base)
- ✅ OpenTelemetry Weaver models
- ✅ FSM state management
- ✅ LM integration (ollama/qwen3)
- ✅ Type-safe telemetry validation
- ✅ JSONL telemetry export

### **Generated Telemetry Sample**:
```json
{
  "traceID": "trace_1750925711022382",
  "spanID": "span_9666739", 
  "operationName": "dslmodel.workflow.data-pipeline",
  "startTime": 1750925711022382,
  "duration": 50000,
  "tags": {
    "workflow_name": "data-pipeline",
    "workflow_status": "completed",
    "workflow_duration_ms": 50,
    "model_type": "dsl_workflow",
    "metric.name": "dslmodel.workflow.duration",
    "metric.instrument": "histogram"
  }
}
```

## Usage Patterns

### **Import Structure**:
```python
# Core integration
from dslmodel.integrations.otel import WeaverForgeIntegration, DslmodelAttributes

# Workflows  
from dslmodel.workflows import WorkflowOrchestrator, AdvancedWorkflowFSM

# Examples
from dslmodel.examples.otel.working_fsm_demo import DSLWorkflow
```

### **Simple Workflow**:
```python
workflow = DSLWorkflow(workflow_name="my-pipeline")
workflow.start_processing()
workflow.complete_successfully(duration_ms=150)
telemetry = workflow.get_telemetry_data()  # Ready for OTEL spans
```

## Integration Value

### **Before Integration**:
- Manual telemetry attribute management
- No type safety for OTEL data
- Basic state tracking
- Separate concerns

### **After Integration**:
- **Type-safe OTEL attributes** generated from semantic conventions
- **Automatic validation** prevents invalid telemetry data  
- **Rich state machine behavior** with AI-powered transitions
- **Unified model** combining DSL capabilities, telemetry, and state management
- **Production-ready** patterns for workflow orchestration

The integration demonstrates how DSLModel, OpenTelemetry semantic conventions, and state machines can work together to create robust, observable, and intelligent workflow systems with proper file organization following Python package best practices.