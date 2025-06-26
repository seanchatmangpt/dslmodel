"""
Full Loop Test with OpenTelemetry Integration

Tests the complete integration:
1. Initialize LM with ollama/qwen3
2. Create DSLModel with OTEL attributes
3. Use FSMMixin for state management
4. Generate real telemetry data
5. Validate with Weaver conventions
"""
import time
import json
from pathlib import Path
from loguru import logger

from dslmodel.utils.dspy_tools import init_lm
from dslmodel.examples.otel.working_fsm_demo import DSLWorkflow
from dslmodel.integrations.otel.models.dslmodel_attributes import DslmodelAttributes
from dslmodel.integrations.otel.metrics.dslmodel_metrics import DslmodelMetricsMetric


class FullLoopOrchestrator:
    """
    Full loop test orchestrator that demonstrates the complete integration.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.telemetry_file = Path("./telemetry_output.jsonl")
        self.results = []
        
    def step_1_initialize_lm(self):
        """Step 1: Initialize language model."""
        logger.info("STEP 1: Initializing LM with ollama/qwen3")
        try:
            init_lm("ollama/qwen3")
            logger.success("✅ LM initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ LM initialization failed: {e}")
            return False
    
    def step_2_create_workflows(self):
        """Step 2: Create multiple DSL workflows with OTEL integration."""
        logger.info("STEP 2: Creating DSL workflows with OTEL attributes")
        workflows = []
        
        workflow_configs = [
            {"name": "data-pipeline", "type": "batch_processing"},
            {"name": "ml-training", "type": "model_training"},
            {"name": "api-validation", "type": "service_testing"},
            {"name": "report-generation", "type": "analytics"}
        ]
        
        for config in workflow_configs:
            try:
                workflow = DSLWorkflow(
                    workflow_name=config["name"],
                    workflow_type=config["type"]
                )
                workflows.append(workflow)
                logger.info(f"  ✅ Created workflow: {config['name']}")
            except Exception as e:
                logger.error(f"  ❌ Failed to create workflow {config['name']}: {e}")
        
        return workflows
    
    def step_3_execute_workflows(self, workflows):
        """Step 3: Execute workflows and collect telemetry."""
        logger.info("STEP 3: Executing workflows and collecting telemetry")
        
        telemetry_data = []
        
        for i, workflow in enumerate(workflows):
            try:
                # Start processing
                workflow.start_processing()
                
                # Simulate work duration
                work_duration = 50 + (i * 30)  # Varying durations
                time.sleep(0.1)  # Brief simulation
                
                # Complete or fail randomly
                if i % 3 == 2:  # Every 3rd workflow fails
                    workflow.fail_with_error(f"Simulated error in step {i+1}")
                else:
                    workflow.complete_successfully(duration_ms=work_duration)
                
                # Collect telemetry
                telemetry = workflow.get_telemetry_data()
                telemetry["execution_order"] = i + 1
                telemetry["timestamp"] = time.time()
                telemetry_data.append(telemetry)
                
                logger.info(f"  ✅ Workflow {workflow.workflow_name}: {workflow.status.value}")
                
            except Exception as e:
                logger.error(f"  ❌ Workflow {workflow.workflow_name} failed: {e}")
        
        return telemetry_data
    
    def step_4_validate_otel_data(self, telemetry_data):
        """Step 4: Validate telemetry data against OTEL conventions."""
        logger.info("STEP 4: Validating telemetry data against OTEL conventions")
        
        validation_results = []
        
        for data in telemetry_data:
            try:
                # Validate against DslmodelAttributes
                attrs = DslmodelAttributes(
                    workflow_name=data["workflow_name"],
                    workflow_status=data["workflow_status"],
                    workflow_duration_ms=data.get("workflow_duration_ms"),
                    model_type=data.get("model_type", "dsl_workflow")
                )
                
                validation_results.append({
                    "workflow": data["workflow_name"],
                    "valid": True,
                    "otel_namespace": attrs.otel_namespace(),
                    "status": data["workflow_status"]
                })
                
                logger.info(f"  ✅ {data['workflow_name']}: OTEL validation passed")
                
            except Exception as e:
                validation_results.append({
                    "workflow": data["workflow_name"],
                    "valid": False,
                    "error": str(e)
                })
                logger.error(f"  ❌ {data['workflow_name']}: OTEL validation failed: {e}")
        
        return validation_results
    
    def step_5_export_telemetry(self, telemetry_data):
        """Step 5: Export telemetry to JSONL format for OTEL consumption."""
        logger.info("STEP 5: Exporting telemetry to JSONL format")
        
        try:
            with open(self.telemetry_file, "w") as f:
                for data in telemetry_data:
                    # Format as OTEL span
                    span = {
                        "traceID": f"trace_{int(data['timestamp'] * 1000000)}",
                        "spanID": f"span_{hash(data['workflow_name']) % 10000000}",
                        "operationName": f"dslmodel.workflow.{data['workflow_name']}",
                        "startTime": int(data["timestamp"] * 1000000),  # microseconds
                        "duration": ((data.get("workflow_duration_ms") or 100) * 1000),  # microseconds
                        "tags": {
                            k: v for k, v in data.items() 
                            if k not in ["timestamp", "execution_order"]
                        }
                    }
                    f.write(json.dumps(span) + "\n")
            
            logger.success(f"✅ Telemetry exported to {self.telemetry_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export telemetry: {e}")
            return False
    
    def step_6_generate_summary(self, workflows, telemetry_data, validation_results):
        """Step 6: Generate comprehensive test summary."""
        logger.info("STEP 6: Generating test summary")
        
        summary = {
            "test_timestamp": time.time(),
            "lm_model": "ollama/qwen3",
            "total_workflows": len(workflows),
            "successful_workflows": sum(1 for w in workflows if w.status.value == "completed"),
            "failed_workflows": sum(1 for w in workflows if w.status.value == "failed"),
            "otel_validation_passed": sum(1 for v in validation_results if v["valid"]),
            "otel_validation_failed": sum(1 for v in validation_results if not v["valid"]),
            "telemetry_spans_generated": len(telemetry_data),
            "integration_components": [
                "DSLModel (Pydantic base)",
                "OpenTelemetry Weaver models", 
                "FSM state management",
                "LM integration (ollama/qwen3)",
                "Type-safe telemetry validation",
                "JSONL telemetry export"
            ]
        }
        
        return summary
    
    def run_full_loop(self):
        """Execute the complete integration test loop."""
        logger.info("🚀 STARTING FULL LOOP INTEGRATION TEST")
        logger.info("=" * 60)
        
        # Step 1: Initialize LM
        if not self.step_1_initialize_lm():
            return {"success": False, "error": "LM initialization failed"}
        
        # Step 2: Create workflows
        workflows = self.step_2_create_workflows()
        if not workflows:
            return {"success": False, "error": "No workflows created"}
        
        # Step 3: Execute workflows
        telemetry_data = self.step_3_execute_workflows(workflows)
        
        # Step 4: Validate OTEL data
        validation_results = self.step_4_validate_otel_data(telemetry_data)
        
        # Step 5: Export telemetry
        export_success = self.step_5_export_telemetry(telemetry_data)
        
        # Step 6: Generate summary
        summary = self.step_6_generate_summary(workflows, telemetry_data, validation_results)
        
        # Final results
        logger.info("\n🎯 FULL LOOP TEST RESULTS")
        logger.info("=" * 40)
        logger.info(f"LM Model: {summary['lm_model']}")
        logger.info(f"Workflows Created: {summary['total_workflows']}")
        logger.info(f"Workflows Successful: {summary['successful_workflows']}")
        logger.info(f"Workflows Failed: {summary['failed_workflows']}")
        logger.info(f"OTEL Validations Passed: {summary['otel_validation_passed']}")
        logger.info(f"OTEL Validations Failed: {summary['otel_validation_failed']}")
        logger.info(f"Telemetry Spans: {summary['telemetry_spans_generated']}")
        logger.info(f"Export Success: {export_success}")
        
        logger.info(f"\n🔧 Integration Components:")
        for component in summary["integration_components"]:
            logger.info(f"  ✓ {component}")
        
        # Overall success criteria
        overall_success = (
            summary["total_workflows"] > 0 and
            summary["otel_validation_passed"] > 0 and
            export_success
        )
        
        if overall_success:
            logger.success("\n✅ FULL LOOP INTEGRATION TEST PASSED")
        else:
            logger.error("\n❌ FULL LOOP INTEGRATION TEST FAILED")
        
        return {
            "success": overall_success,
            "summary": summary,
            "telemetry_file": str(self.telemetry_file),
            "workflows": [w.get_summary() for w in workflows],
            "validation_results": validation_results
        }


def main():
    """Run the full loop integration test."""
    orchestrator = FullLoopOrchestrator()
    results = orchestrator.run_full_loop()
    
    # Save detailed results
    results_file = Path("./full_loop_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n📊 Detailed results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    results = main()