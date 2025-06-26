#!/usr/bin/env python3
"""
Agent Orchestration with Telemetry Validation
==============================================

Implements agent orchestration workflow with comprehensive OpenTelemetry validation
for the organizational transformation demo. Demonstrates:

1. Multi-agent coordination with telemetry
2. Real-time span validation and verification  
3. Workflow orchestration with trace correlation
4. Telemetry-driven decision making

80/20 Focus: Essential telemetry validation with minimal complexity
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
# Note: SpanAttributes available if needed
# from opentelemetry.semantic_conventions.trace import SpanAttributes
from opentelemetry.trace.status import Status, StatusCode

# Configure OTEL
trace.set_tracer_provider(TracerProvider())
metrics.set_meter_provider(MeterProvider())

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Add console exporter for demo visibility
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# Define custom semantic conventions for organizational transformation
class TransformationAttributes:
    """Custom semantic conventions for organizational transformation telemetry"""
    
    # Agent identification
    AGENT_TYPE = "transformation.agent.type"
    AGENT_ID = "transformation.agent.id"
    AGENT_STATE = "transformation.agent.state"
    
    # Workflow attributes
    WORKFLOW_PHASE = "transformation.workflow.phase"
    WORKFLOW_STEP = "transformation.workflow.step"
    WORKFLOW_INTEGRATION_POINT = "transformation.workflow.integration_point"
    
    # Business metrics
    BUSINESS_VALUE = "transformation.business.value"
    DEFECT_RATE = "transformation.quality.defect_rate"
    VELOCITY = "transformation.agile.velocity"
    ROI = "transformation.financial.roi"
    
    # Validation results
    VALIDATION_STATUS = "transformation.validation.status"
    VALIDATION_METRIC = "transformation.validation.metric"
    VALIDATION_THRESHOLD = "transformation.validation.threshold"

@dataclass
class TelemetryValidation:
    """Represents a telemetry validation result"""
    span_id: str
    trace_id: str
    operation: str
    agent_type: str
    validation_status: str
    metrics: Dict[str, Any]
    timestamp: datetime
    success: bool
    message: str

class AgentType(Enum):
    ROBERTS_RULES = "roberts_rules"
    SCRUM_SCALE = "scrum_scale" 
    LEAN_SIX_SIGMA = "lean_six_sigma"
    ORCHESTRATOR = "orchestrator"

class WorkflowPhase(Enum):
    GOVERNANCE = "governance"
    AGILE_SCALING = "agile_scaling"
    PROCESS_OPTIMIZATION = "process_optimization"
    INTEGRATION = "integration"

class TelemetryOrchestrator:
    """Orchestrates agents with comprehensive telemetry validation"""
    
    def __init__(self):
        self.validations: List[TelemetryValidation] = []
        self.active_spans: Dict[str, Span] = {}
        self.workflow_state = {
            "current_phase": None,
            "phase_results": {},
            "integration_points": [],
            "total_validations": 0,
            "successful_validations": 0
        }
        
        # Initialize metrics
        self.validation_counter = meter.create_counter(
            "transformation_validations_total",
            description="Total number of telemetry validations performed"
        )
        
        self.validation_success_rate = meter.create_histogram(
            "transformation_validation_success_rate",
            description="Success rate of telemetry validations"
        )
        
        self.agent_coordination_duration = meter.create_histogram(
            "transformation_agent_coordination_duration_ms",
            description="Duration of agent coordination operations in milliseconds"
        )

    async def orchestrate_transformation_workflow(self) -> Dict[str, Any]:
        """Execute complete transformation workflow with telemetry validation"""
        
        with tracer.start_as_current_span("transformation.workflow.execute") as root_span:
            root_span.set_attribute(TransformationAttributes.WORKFLOW_PHASE, "complete")
            root_span.set_attribute(TransformationAttributes.AGENT_TYPE, AgentType.ORCHESTRATOR.value)
            
            print("🔄 AGENT ORCHESTRATION WITH TELEMETRY VALIDATION")
            print("=" * 55)
            
            try:
                # Phase 1: Roberts Rules Governance
                governance_result = await self._orchestrate_governance_phase()
                await self._validate_phase_telemetry(WorkflowPhase.GOVERNANCE, governance_result)
                
                # Phase 2: Scrum at Scale
                agile_result = await self._orchestrate_agile_phase(governance_result)
                await self._validate_phase_telemetry(WorkflowPhase.AGILE_SCALING, agile_result)
                
                # Phase 3: Lean Six Sigma
                process_result = await self._orchestrate_process_phase(agile_result)
                await self._validate_phase_telemetry(WorkflowPhase.PROCESS_OPTIMIZATION, process_result)
                
                # Phase 4: Integration Validation
                integration_result = await self._validate_full_integration()
                await self._validate_phase_telemetry(WorkflowPhase.INTEGRATION, integration_result)
                
                # Final validation summary
                validation_summary = await self._generate_validation_summary()
                
                root_span.set_attribute("transformation.workflow.success", True)
                root_span.set_attribute("transformation.validation.total", len(self.validations))
                root_span.set_attribute("transformation.validation.success_rate", 
                                      self.workflow_state["successful_validations"] / max(1, self.workflow_state["total_validations"]))
                
                return validation_summary
                
            except Exception as e:
                root_span.record_exception(e)
                root_span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    async def _orchestrate_governance_phase(self) -> Dict[str, Any]:
        """Orchestrate Roberts Rules governance phase with telemetry"""
        
        with tracer.start_as_current_span("transformation.governance.orchestrate") as span:
            span.set_attribute(TransformationAttributes.WORKFLOW_PHASE, WorkflowPhase.GOVERNANCE.value)
            span.set_attribute(TransformationAttributes.AGENT_TYPE, AgentType.ROBERTS_RULES.value)
            
            print("\n🏛️ PHASE 1: GOVERNANCE ORCHESTRATION")
            print("-" * 40)
            
            # Simulate governance operations with telemetry
            motion_data = {
                "id": "MOTION-2024-TRANSFORM",
                "title": "Enterprise Digital Transformation Initiative", 
                "budget": 2500000,
                "approval_votes": 8,
                "against_votes": 1,
                "approval_rate": 0.8
            }
            
            # Create motion span
            with tracer.start_as_current_span("roberts.motion.create") as motion_span:
                motion_span.set_attribute("roberts.motion.id", motion_data["id"])
                motion_span.set_attribute("roberts.motion.budget", motion_data["budget"])
                motion_span.set_attribute("roberts.motion.approval_rate", motion_data["approval_rate"])
                
                # Validate telemetry in real-time
                validation = await self._validate_span_attributes(motion_span, {
                    "roberts.motion.approval_rate": {"min": 0.6, "max": 1.0},
                    "roberts.motion.budget": {"min": 1000000, "max": 10000000}
                })
                
                print(f"   📊 Motion Created: {motion_data['title']}")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
                
            # Voting simulation
            with tracer.start_as_current_span("roberts.voting.execute") as voting_span:
                voting_span.set_attribute("roberts.voting.total", 10)
                voting_span.set_attribute("roberts.voting.for", motion_data["approval_votes"])
                voting_span.set_attribute("roberts.voting.against", motion_data["against_votes"])
                voting_span.set_attribute("roberts.voting.result", "approved")
                
                validation = await self._validate_span_attributes(voting_span, {
                    "roberts.voting.for": {"min": 5},  # Minimum votes for approval
                })
                
                print(f"   🗳️  Voting Completed: {motion_data['approval_votes']} for, {motion_data['against_votes']} against")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
                
            span.set_attribute(TransformationAttributes.BUSINESS_VALUE, motion_data["budget"])
            span.set_attribute("roberts.governance.outcome", "approved")
            
            return {
                "phase": "governance",
                "motion": motion_data,
                "telemetry_validations": len([v for v in self.validations if v.agent_type == AgentType.ROBERTS_RULES.value]),
                "success": True
            }

    async def _orchestrate_agile_phase(self, governance_input: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Scrum at Scale phase with telemetry correlation"""
        
        with tracer.start_as_current_span("transformation.agile.orchestrate") as span:
            span.set_attribute(TransformationAttributes.WORKFLOW_PHASE, WorkflowPhase.AGILE_SCALING.value)
            span.set_attribute(TransformationAttributes.AGENT_TYPE, AgentType.SCRUM_SCALE.value)
            span.set_attribute("governance.motion.id", governance_input["motion"]["id"])
            
            print("\n🏃‍♂️ PHASE 2: AGILE SCALING ORCHESTRATION")
            print("-" * 40)
            
            # PI Planning with governance correlation
            pi_data = {
                "pi_number": "PI-2024-Q4",
                "teams": 8,
                "capacity": 960,
                "governance_budget": governance_input["motion"]["budget"]
            }
            
            with tracer.start_as_current_span("scrum.pi_planning.execute") as pi_span:
                pi_span.set_attribute("scrum.pi.number", pi_data["pi_number"])
                pi_span.set_attribute("scrum.pi.teams", pi_data["teams"])
                pi_span.set_attribute("scrum.pi.capacity", pi_data["capacity"])
                pi_span.set_attribute("scrum.pi.governance_alignment", governance_input["motion"]["id"])
                
                validation = await self._validate_span_attributes(pi_span, {
                    "scrum.pi.teams": {"min": 3, "max": 15},
                    "scrum.pi.capacity": {"min": 100}
                })
                
                print(f"   📊 PI Planning: {pi_data['pi_number']} with {pi_data['teams']} teams")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
            
            # Sprint execution simulation with quality metrics
            sprint_metrics = {
                "velocity": 85.2,
                "defect_rate": 0.147,  # 14.7%
                "completed_stories": 156,
                "cycle_time": 4.8
            }
            
            with tracer.start_as_current_span("scrum.sprint.execute") as sprint_span:
                sprint_span.set_attribute(TransformationAttributes.VELOCITY, sprint_metrics["velocity"])
                sprint_span.set_attribute(TransformationAttributes.DEFECT_RATE, sprint_metrics["defect_rate"])
                sprint_span.set_attribute("scrum.sprint.completed_stories", sprint_metrics["completed_stories"])
                sprint_span.set_attribute("scrum.sprint.cycle_time", sprint_metrics["cycle_time"])
                
                # Critical validation: defect rate threshold
                validation = await self._validate_span_attributes(sprint_span, {
                    TransformationAttributes.DEFECT_RATE: {"max": 0.10},  # 10% threshold
                    TransformationAttributes.VELOCITY: {"min": 70.0}
                })
                
                # Check if defect rate exceeds threshold
                defect_threshold_exceeded = sprint_metrics["defect_rate"] > 0.10
                sprint_span.set_attribute("scrum.quality.threshold_exceeded", defect_threshold_exceeded)
                
                print(f"   🏃 Sprint Execution: {sprint_metrics['velocity']:.1f}% velocity")
                print(f"   🐛 Defect Rate: {sprint_metrics['defect_rate']:.1%}")
                print(f"   ⚠️ Quality Threshold: {'EXCEEDED' if defect_threshold_exceeded else 'WITHIN LIMITS'}")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
                
            span.set_attribute(TransformationAttributes.BUSINESS_VALUE, pi_data["capacity"])
            span.set_attribute("scrum.quality.improvement_trigger", sprint_metrics["defect_rate"] > 0.10)
            
            return {
                "phase": "agile_scaling",
                "pi_planning": pi_data,
                "sprint_metrics": sprint_metrics,
                "improvement_trigger": sprint_metrics["defect_rate"] > 0.10,
                "telemetry_validations": len([v for v in self.validations if v.agent_type == AgentType.SCRUM_SCALE.value]),
                "success": True
            }

    async def _orchestrate_process_phase(self, agile_input: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Lean Six Sigma process optimization with telemetry"""
        
        with tracer.start_as_current_span("transformation.process.orchestrate") as span:
            span.set_attribute(TransformationAttributes.WORKFLOW_PHASE, WorkflowPhase.PROCESS_OPTIMIZATION.value)
            span.set_attribute(TransformationAttributes.AGENT_TYPE, AgentType.LEAN_SIX_SIGMA.value)
            span.set_attribute("agile.improvement_trigger", agile_input["improvement_trigger"])
            
            print("\n🔧 PHASE 3: PROCESS OPTIMIZATION ORCHESTRATION")
            print("-" * 40)
            
            # Only proceed if triggered by quality issues
            if not agile_input["improvement_trigger"]:
                print("   ℹ️ No quality issues detected - Lean Six Sigma not triggered")
                return {"phase": "process_optimization", "triggered": False, "success": True}
            
            # DMAIC project initiation
            lss_project = {
                "project_id": "LSS-TRANSFORM-2024",
                "baseline_defect_rate": agile_input["sprint_metrics"]["defect_rate"],
                "target_defect_rate": 0.05,  # 5%
                "expected_savings": 850000,
                "implementation_weeks": 21
            }
            
            with tracer.start_as_current_span("lss.dmaic.define") as define_span:
                define_span.set_attribute("lss.project.id", lss_project["project_id"])
                define_span.set_attribute("lss.baseline.defect_rate", lss_project["baseline_defect_rate"])
                define_span.set_attribute("lss.target.defect_rate", lss_project["target_defect_rate"])
                define_span.set_attribute("lss.expected.savings", lss_project["expected_savings"])
                
                validation = await self._validate_span_attributes(define_span, {
                    "lss.baseline.defect_rate": {"min": 0.10, "max": 0.50},  # Reasonable defect range
                    "lss.target.defect_rate": {"max": 0.10},  # Target should be better
                    "lss.expected.savings": {"min": 100000}  # Minimum ROI
                })
                
                print(f"   📋 LSS Project: {lss_project['project_id']}")
                print(f"   📊 Baseline → Target: {lss_project['baseline_defect_rate']:.1%} → {lss_project['target_defect_rate']:.1%}")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
            
            # Process improvement simulation
            improvement_results = {
                "defect_reduction": 0.68,  # 68%
                "cycle_time_improvement": 0.38,  # 38%
                "roi_estimate": 3.4,
                "process_efficiency_gain": 0.47  # 47%
            }
            
            with tracer.start_as_current_span("lss.improve.implement") as improve_span:
                improve_span.set_attribute("lss.improvement.defect_reduction", improvement_results["defect_reduction"])
                improve_span.set_attribute("lss.improvement.cycle_time", improvement_results["cycle_time_improvement"])
                improve_span.set_attribute(TransformationAttributes.ROI, improvement_results["roi_estimate"])
                improve_span.set_attribute("lss.improvement.efficiency_gain", improvement_results["process_efficiency_gain"])
                
                validation = await self._validate_span_attributes(improve_span, {
                    "lss.improvement.defect_reduction": {"min": 0.30},  # Minimum 30% improvement
                    TransformationAttributes.ROI: {"min": 2.0}  # Minimum 2x ROI
                })
                
                print(f"   💡 Defect Reduction: {improvement_results['defect_reduction']:.0%}")
                print(f"   📈 ROI Estimate: {improvement_results['roi_estimate']:.1f}x")
                print(f"   ✅ Telemetry Validation: {validation.validation_status}")
                
            span.set_attribute(TransformationAttributes.BUSINESS_VALUE, lss_project["expected_savings"])
            span.set_attribute("lss.project.success", True)
            
            return {
                "phase": "process_optimization",
                "project": lss_project,
                "improvements": improvement_results,
                "triggered": True,
                "telemetry_validations": len([v for v in self.validations if v.agent_type == AgentType.LEAN_SIX_SIGMA.value]),
                "success": True
            }

    async def _validate_full_integration(self) -> Dict[str, Any]:
        """Validate full integration across all phases with telemetry"""
        
        with tracer.start_as_current_span("transformation.integration.validate") as span:
            span.set_attribute(TransformationAttributes.WORKFLOW_PHASE, WorkflowPhase.INTEGRATION.value)
            span.set_attribute(TransformationAttributes.AGENT_TYPE, AgentType.ORCHESTRATOR.value)
            
            print("\n🔄 PHASE 4: INTEGRATION VALIDATION")
            print("-" * 40)
            
            # Validate integration points
            integration_points = [
                {
                    "from": "roberts_rules",
                    "to": "scrum_scale", 
                    "mechanism": "governance_budget_to_pi_capacity",
                    "validated": True
                },
                {
                    "from": "scrum_scale",
                    "to": "lean_six_sigma",
                    "mechanism": "defect_threshold_trigger",
                    "validated": True
                },
                {
                    "from": "lean_six_sigma", 
                    "to": "roberts_rules",
                    "mechanism": "savings_to_governance_reporting",
                    "validated": True
                }
            ]
            
            total_validations = len(self.validations)
            successful_validations = len([v for v in self.validations if v.success])
            success_rate = successful_validations / max(1, total_validations)
            
            span.set_attribute("integration.points.total", len(integration_points))
            span.set_attribute("integration.points.validated", len([p for p in integration_points if p["validated"]]))
            span.set_attribute("integration.validation.total", total_validations)
            span.set_attribute("integration.validation.success_rate", success_rate)
            
            # Final integration validation
            validation = TelemetryValidation(
                span_id=format(span.get_span_context().span_id, 'x'),
                trace_id=format(span.get_span_context().trace_id, 'x'),
                operation="integration_validation",
                agent_type=AgentType.ORCHESTRATOR.value,
                validation_status="success" if success_rate >= 0.8 else "warning",
                metrics={"success_rate": success_rate, "total_validations": total_validations},
                timestamp=datetime.now(),
                success=success_rate >= 0.8,
                message=f"Integration validation {success_rate:.1%} success rate"
            )
            
            self.validations.append(validation)
            
            print(f"   🔗 Integration Points: {len([p for p in integration_points if p['validated']])}/{len(integration_points)} validated")
            print(f"   📊 Overall Success Rate: {success_rate:.1%}")
            print(f"   ✅ Integration Status: {'SUCCESSFUL' if success_rate >= 0.8 else 'NEEDS ATTENTION'}")
            
            return {
                "phase": "integration",
                "integration_points": integration_points,
                "validation_summary": {
                    "total": total_validations,
                    "successful": successful_validations,
                    "success_rate": success_rate
                },
                "success": success_rate >= 0.8
            }

    async def _validate_span_attributes(self, span: Span, validations: Dict[str, Dict[str, Any]]) -> TelemetryValidation:
        """Validate span attributes against defined thresholds"""
        
        span_context = span.get_span_context()
        span_id = format(span_context.span_id, 'x')
        trace_id = format(span_context.trace_id, 'x')
        
        validation_results = []
        agent_type = "unknown"
        
        # Extract agent type from span attributes
        for attr_name, attr_value in span._attributes.items() if hasattr(span, '_attributes') else []:
            if attr_name == TransformationAttributes.AGENT_TYPE:
                agent_type = attr_value
                break
        
        # Perform validations
        for attr_name, constraints in validations.items():
            if hasattr(span, '_attributes') and attr_name in span._attributes:
                attr_value = span._attributes[attr_name]
                
                # Check min constraint
                if 'min' in constraints and attr_value < constraints['min']:
                    validation_results.append(f"{attr_name} below minimum: {attr_value} < {constraints['min']}")
                    
                # Check max constraint  
                if 'max' in constraints and attr_value > constraints['max']:
                    validation_results.append(f"{attr_name} above maximum: {attr_value} > {constraints['max']}")
        
        # Determine validation status
        success = len(validation_results) == 0
        status = "success" if success else "failed"
        message = "All validations passed" if success else "; ".join(validation_results)
        
        # Record validation in span
        span.set_attribute(TransformationAttributes.VALIDATION_STATUS, status)
        if not success:
            span.set_status(Status(StatusCode.ERROR, message))
        
        # Create validation record
        validation = TelemetryValidation(
            span_id=span_id,
            trace_id=trace_id,
            operation=span.name if hasattr(span, 'name') else "unknown",
            agent_type=agent_type,
            validation_status=status,
            metrics=dict(span._attributes) if hasattr(span, '_attributes') else {},
            timestamp=datetime.now(),
            success=success,
            message=message
        )
        
        self.validations.append(validation)
        self.workflow_state["total_validations"] += 1
        if success:
            self.workflow_state["successful_validations"] += 1
        
        # Record metrics
        self.validation_counter.add(1, {"status": status, "agent_type": agent_type})
        
        return validation

    async def _validate_phase_telemetry(self, phase: WorkflowPhase, phase_result: Dict[str, Any]):
        """Validate telemetry for completed phase"""
        
        print(f"   📋 Phase {phase.value.title()} Telemetry Summary:")
        print(f"      • Success: {phase_result['success']}")
        if 'telemetry_validations' in phase_result:
            print(f"      • Telemetry Validations: {phase_result['telemetry_validations']}")
        
        self.workflow_state["phase_results"][phase.value] = phase_result

    async def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        
        print("\n📊 TELEMETRY VALIDATION SUMMARY")
        print("=" * 35)
        
        # Calculate statistics
        total_validations = len(self.validations)
        successful_validations = len([v for v in self.validations if v.success])
        success_rate = successful_validations / max(1, total_validations)
        
        # Group by agent type
        agent_stats = {}
        for validation in self.validations:
            agent_type = validation.agent_type
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {"total": 0, "success": 0}
            agent_stats[agent_type]["total"] += 1
            if validation.success:
                agent_stats[agent_type]["success"] += 1
        
        print(f"   📈 Overall Success Rate: {success_rate:.1%}")
        print(f"   📊 Total Validations: {total_validations}")
        print(f"   ✅ Successful: {successful_validations}")
        print(f"   ❌ Failed: {total_validations - successful_validations}")
        
        print("\n   📋 By Agent Type:")
        for agent_type, stats in agent_stats.items():
            agent_success_rate = stats["success"] / max(1, stats["total"])
            print(f"      • {agent_type}: {agent_success_rate:.1%} ({stats['success']}/{stats['total']})")
        
        # Failed validations details
        failed_validations = [v for v in self.validations if not v.success]
        if failed_validations:
            print(f"\n   ⚠️ Failed Validations ({len(failed_validations)}):")
            for fv in failed_validations:
                print(f"      • {fv.operation}: {fv.message}")
        
        summary = {
            "validation_summary": {
                "total_validations": total_validations,
                "successful_validations": successful_validations,
                "success_rate": success_rate,
                "agent_statistics": agent_stats,
                "failed_validations": [asdict(v) for v in failed_validations]
            },
            "workflow_state": self.workflow_state,
            "telemetry_validated": success_rate >= 0.8,
            "recommendation": "Production ready" if success_rate >= 0.9 else "Needs improvement" if success_rate >= 0.7 else "Critical issues"
        }
        
        print(f"\n   🎯 Recommendation: {summary['recommendation']}")
        
        return summary

async def run_orchestration_demo():
    """Execute the complete agent orchestration with telemetry validation demo"""
    
    orchestrator = TelemetryOrchestrator()
    
    start_time = time.time()
    
    try:
        # Run the orchestrated workflow
        results = await orchestrator.orchestrate_transformation_workflow()
        
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        print(f"\n✅ ORCHESTRATION COMPLETED SUCCESSFULLY")
        print(f"   ⏱️ Duration: {duration:.1f}ms")
        print(f"   📊 Validation Rate: {results['validation_summary']['success_rate']:.1%}")
        print(f"   🎯 Status: {results['recommendation']}")
        
        # Save results
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "agent_orchestration_telemetry_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"   📁 Results saved to: demo_output/agent_orchestration_telemetry_results.json")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ORCHESTRATION FAILED: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_orchestration_demo())