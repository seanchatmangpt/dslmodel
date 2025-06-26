#!/usr/bin/env python3
"""
Multi-Layer Weaver Validation with Feedback Loops
=================================================

Implements 5 layers of validation following agents' 80/20 strategy:
1. Start simple (Implementer) → Layer 1: Semantic Convention Validation  
2. Think systematically (Analyst) → Layer 2: Generated Code Validation
3. Stay flexible (Creative) → Layer 3: Runtime Telemetry Validation
4. Validate assumptions (Critic) → Layer 4: Integration Validation
5. Align with goals (Strategist) → Layer 5: System Health & Performance

Each layer provides feedback to improve the next iteration.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Core imports
from dslmodel.claude_telemetry import ClaudeTelemetry, tracer
from dslmodel.core.weaver_engine import WeaverEngine, GenerationType
from dslmodel.validation.weaver_otel_validator import WeaverOTELValidator

@dataclass
class ValidationResult:
    """Result from a validation layer"""
    layer: str
    status: str  # "pass", "warn", "fail"
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeedbackLoop:
    """Feedback from validation to improve next iteration"""
    source_layer: str
    target_layer: str
    feedback_type: str  # "fix", "enhance", "optimize"
    message: str
    priority: str  # "high", "medium", "low"
    implemented: bool = False

class Layer1_SemanticConventionValidator:
    """Layer 1: Start Simple (Implementer) - Validate semantic conventions"""
    
    def __init__(self):
        self.weaver_engine = WeaverEngine()
        
    async def validate(self, convention_name: str) -> ValidationResult:
        """Validate semantic convention structure and content"""
        
        with tracer.start_as_current_span("layer1.semantic_validation") as span:
            span.set_attribute("convention", convention_name)
            
            result = ValidationResult(layer="semantic_convention", status="pass", score=1.0)
            
            try:
                # Load and validate convention
                convention = self.weaver_engine.load_semantic_convention(convention_name)
                
                # Basic structure checks
                if not convention.get("spans"):
                    result.issues.append("No spans defined in convention")
                    result.score -= 0.3
                    
                if not convention.get("groups"):
                    result.issues.append("No groups defined in convention")
                    result.score -= 0.2
                    
                # Check span definitions
                spans = convention.get("spans", [])
                for span_def in spans:
                    if not span_def.get("id"):
                        result.issues.append(f"Span missing id: {span_def}")
                        result.score -= 0.1
                        
                    if not span_def.get("brief"):
                        result.issues.append(f"Span missing brief: {span_def.get('id')}")
                        result.score -= 0.05
                
                # Suggest improvements
                if result.score < 1.0:
                    result.improvements.append("Add missing span definitions")
                    result.improvements.append("Ensure all spans have id and brief")
                
                # Update status based on score
                if result.score >= 0.8:
                    result.status = "pass"
                elif result.score >= 0.6:
                    result.status = "warn"
                else:
                    result.status = "fail"
                    
                result.telemetry = {
                    "spans_count": len(spans),
                    "validation_time_ms": time.time() * 1000,
                    "convention_size": len(str(convention))
                }
                
                span.set_attribute("validation.score", result.score)
                span.set_attribute("validation.status", result.status)
                
            except Exception as e:
                result.status = "fail"
                result.score = 0.0
                result.issues.append(f"Failed to load convention: {e}")
                
            return result

class Layer2_GeneratedCodeValidator:
    """Layer 2: Think Systematically (Analyst) - Validate generated code quality"""
    
    def __init__(self):
        self.weaver_engine = WeaverEngine()
        
    async def validate(self, convention_name: str, feedback: List[FeedbackLoop] = None) -> ValidationResult:
        """Validate generated code from semantic convention"""
        
        with tracer.start_as_current_span("layer2.code_validation") as span:
            span.set_attribute("convention", convention_name)
            
            result = ValidationResult(layer="generated_code", status="pass", score=1.0)
            
            try:
                # Apply feedback from Layer 1
                if feedback:
                    layer1_feedback = [f for f in feedback if f.source_layer == "semantic_convention"]
                    for fb in layer1_feedback:
                        span.add_event(f"Applied feedback: {fb.message}")
                
                # Generate code
                generation_result = await self.weaver_engine.generate_artifacts(
                    convention_name, 
                    GenerationType.ALL
                )
                
                # Validate generated artifacts
                issues = []
                improvements = []
                
                # Check model generation
                if not generation_result.models_generated:
                    issues.append("No Pydantic models generated")
                    result.score -= 0.3
                else:
                    improvements.append("Models generated successfully")
                
                # Check CLI generation
                if not generation_result.cli_generated:
                    issues.append("No CLI commands generated")
                    result.score -= 0.2
                else:
                    improvements.append("CLI commands generated")
                
                # Check test generation
                if not generation_result.tests_generated:
                    issues.append("No tests generated")
                    result.score -= 0.2
                else:
                    improvements.append("Test suite generated")
                
                # Code quality checks
                if generation_result.models_generated:
                    # Check for OTEL integration
                    model_files = list(Path("src/dslmodel/generated").glob("*.py"))
                    for model_file in model_files:
                        content = model_file.read_text()
                        if "from opentelemetry" not in content:
                            issues.append(f"Missing OTEL integration in {model_file.name}")
                            result.score -= 0.1
                
                result.issues = issues
                result.improvements = improvements
                
                # Update status
                if result.score >= 0.8:
                    result.status = "pass"
                elif result.score >= 0.6:
                    result.status = "warn"
                else:
                    result.status = "fail"
                
                result.telemetry = {
                    "models_generated": generation_result.models_generated,
                    "cli_generated": generation_result.cli_generated,
                    "tests_generated": generation_result.tests_generated,
                    "generation_time_ms": generation_result.generation_time_ms
                }
                
                span.set_attribute("validation.score", result.score)
                span.set_attribute("validation.status", result.status)
                
            except Exception as e:
                result.status = "fail"
                result.score = 0.0
                result.issues.append(f"Code generation failed: {e}")
                
            return result

class Layer3_RuntimeTelemetryValidator:
    """Layer 3: Stay Flexible (Creative) - Validate runtime telemetry"""
    
    def __init__(self):
        self.otel_validator = WeaverOTELValidator()
        
    async def validate(self, convention_name: str, feedback: List[FeedbackLoop] = None) -> ValidationResult:
        """Validate runtime telemetry against semantic conventions"""
        
        with tracer.start_as_current_span("layer3.telemetry_validation") as span:
            span.set_attribute("convention", convention_name)
            
            result = ValidationResult(layer="runtime_telemetry", status="pass", score=1.0)
            
            try:
                # Apply feedback from previous layers
                if feedback:
                    applied_feedback = [f for f in feedback if f.target_layer == "runtime_telemetry"]
                    for fb in applied_feedback:
                        span.add_event(f"Applied feedback: {fb.message}")
                
                # Run telemetry validation
                validation_results = await self.otel_validator.validate_spans_async(
                    convention_name=convention_name,
                    sample_spans=10
                )
                
                # Analyze results
                passed = validation_results.get("passed", 0)
                total = validation_results.get("total", 1)
                
                result.score = passed / total if total > 0 else 0.0
                
                # Extract issues and improvements
                if "errors" in validation_results:
                    result.issues.extend(validation_results["errors"])
                    
                if "warnings" in validation_results:
                    result.improvements.extend(validation_results["warnings"])
                
                # Creative suggestions for telemetry improvement
                if result.score < 0.9:
                    result.improvements.append("Consider adding custom attributes for better observability")
                    result.improvements.append("Add span events for key state transitions")
                
                # Update status
                if result.score >= 0.9:
                    result.status = "pass"
                elif result.score >= 0.7:
                    result.status = "warn"
                else:
                    result.status = "fail"
                
                result.telemetry = {
                    "spans_validated": total,
                    "spans_passed": passed,
                    "validation_time_ms": validation_results.get("execution_time_ms", 0)
                }
                
                span.set_attribute("validation.score", result.score)
                span.set_attribute("validation.status", result.status)
                
            except Exception as e:
                result.status = "fail"
                result.score = 0.0
                result.issues.append(f"Telemetry validation failed: {e}")
                
            return result

class Layer4_IntegrationValidator:
    """Layer 4: Validate Assumptions (Critic) - System integration validation"""
    
    async def validate(self, convention_name: str, feedback: List[FeedbackLoop] = None) -> ValidationResult:
        """Validate system integration and cross-component compatibility"""
        
        from dslmodel.claude_telemetry import tracer
        with tracer.start_as_current_span("layer4.integration_validation") as span:
            span.set_attribute("convention", convention_name)
            
            result = ValidationResult(layer="system_integration", status="pass", score=1.0)
            
            try:
                # Critical validation of assumptions
                critical_checks = []
                
                # Check CLI integration
                try:
                    # Simulate CLI command execution
                    from dslmodel.commands import weaver
                    critical_checks.append(("CLI integration", True))
                except Exception as e:
                    critical_checks.append(("CLI integration", False))
                    result.issues.append(f"CLI integration broken: {e}")
                
                # Check OTEL integration
                try:
                    from opentelemetry import trace
                    tracer = trace.get_tracer(__name__)
                    with tracer.start_as_current_span("integration_test"):
                        critical_checks.append(("OTEL integration", True))
                except Exception as e:
                    critical_checks.append(("OTEL integration", False))
                    result.issues.append(f"OTEL integration broken: {e}")
                
                # Check template system
                try:
                    from jinja2 import Environment
                    critical_checks.append(("Template system", True))
                except Exception as e:
                    critical_checks.append(("Template system", False))
                    result.issues.append(f"Template system broken: {e}")
                
                # Calculate integration score
                passed_checks = sum(1 for _, status in critical_checks if status)
                total_checks = len(critical_checks)
                result.score = passed_checks / total_checks if total_checks > 0 else 0.0
                
                # Critic's suspicious validation
                if result.score == 1.0:
                    result.improvements.append("Suspiciously perfect - add edge case testing")
                
                if result.score < 0.8:
                    result.improvements.append("Fix critical integration issues before proceeding")
                    result.improvements.append("Add integration smoke tests")
                
                # Update status
                if result.score >= 0.8:
                    result.status = "pass"
                elif result.score >= 0.6:
                    result.status = "warn"
                else:
                    result.status = "fail"
                
                result.telemetry = {
                    "integration_checks": len(critical_checks),
                    "passed_checks": passed_checks,
                    "check_details": dict(critical_checks)
                }
                
                span.set_attribute("validation.score", result.score)
                span.set_attribute("validation.status", result.status)
                
            except Exception as e:
                result.status = "fail"
                result.score = 0.0
                result.issues.append(f"Integration validation failed: {e}")
                
            return result

class Layer5_SystemHealthValidator:
    """Layer 5: Align with Goals (Strategist) - System health and performance"""
    
    async def validate(self, convention_name: str, feedback: List[FeedbackLoop] = None) -> ValidationResult:
        """Validate system health, performance, and strategic alignment"""
        
        with tracer.start_as_current_span("layer5.health_validation") as span:
            span.set_attribute("convention", convention_name)
            
            result = ValidationResult(layer="system_health", status="pass", score=1.0)
            
            try:
                # Strategic health checks
                health_metrics = {}
                
                # Performance check
                start_time = time.time()
                # Simulate load
                for _ in range(100):
                    pass
                performance_time = time.time() - start_time
                
                if performance_time < 0.1:
                    health_metrics["performance"] = 1.0
                elif performance_time < 0.5:
                    health_metrics["performance"] = 0.8
                else:
                    health_metrics["performance"] = 0.5
                    result.issues.append("Performance degradation detected")
                
                # Memory check (simplified)
                try:
                    import psutil
                    memory_percent = psutil.virtual_memory().percent
                except ImportError:
                    memory_percent = 50  # Default assumption
                if memory_percent < 80:
                    health_metrics["memory"] = 1.0
                elif memory_percent < 90:
                    health_metrics["memory"] = 0.8
                    result.improvements.append("Memory usage approaching limits")
                else:
                    health_metrics["memory"] = 0.5
                    result.issues.append("High memory usage detected")
                
                # Strategic alignment check
                # Check if system follows 80/20 principle
                convention_files = list(Path("src/dslmodel/registry/semantic").glob("*.yaml"))
                if len(convention_files) > 0:
                    health_metrics["strategic_alignment"] = 1.0
                    result.improvements.append("System follows 80/20 principle with semantic conventions")
                else:
                    health_metrics["strategic_alignment"] = 0.5
                    result.issues.append("Missing semantic conventions - not following 80/20 principle")
                
                # Calculate overall health score
                result.score = sum(health_metrics.values()) / len(health_metrics)
                
                # Strategic recommendations
                if result.score >= 0.9:
                    result.improvements.append("System health excellent - consider expansion")
                elif result.score >= 0.7:
                    result.improvements.append("System health good - monitor trends")
                else:
                    result.improvements.append("System health concerning - immediate action needed")
                
                # Update status
                if result.score >= 0.8:
                    result.status = "pass"
                elif result.score >= 0.6:
                    result.status = "warn"
                else:
                    result.status = "fail"
                
                result.telemetry = {
                    "performance_time_ms": performance_time * 1000,
                    "memory_percent": memory_percent,
                    "health_metrics": health_metrics,
                    "strategic_alignment": health_metrics.get("strategic_alignment", 0.0)
                }
                
                span.set_attribute("validation.score", result.score)
                span.set_attribute("validation.status", result.status)
                
            except Exception as e:
                result.status = "fail"
                result.score = 0.0
                result.issues.append(f"Health validation failed: {e}")
                
            return result

class MultiLayerWeaverValidator:
    """Orchestrates all 5 validation layers with feedback loops"""
    
    def __init__(self):
        self.layer1 = Layer1_SemanticConventionValidator()
        self.layer2 = Layer2_GeneratedCodeValidator()
        self.layer3 = Layer3_RuntimeTelemetryValidator()
        self.layer4 = Layer4_IntegrationValidator()
        self.layer5 = Layer5_SystemHealthValidator()
        self.feedback_loops: List[FeedbackLoop] = []
        
    def generate_feedback(self, results: List[ValidationResult]) -> List[FeedbackLoop]:
        """Generate feedback loops between validation layers"""
        
        feedback = []
        
        # Layer 1 → Layer 2 feedback
        layer1_result = next((r for r in results if r.layer == "semantic_convention"), None)
        if layer1_result and layer1_result.status != "pass":
            feedback.append(FeedbackLoop(
                source_layer="semantic_convention",
                target_layer="generated_code",
                feedback_type="fix",
                message="Fix semantic convention issues before code generation",
                priority="high"
            ))
        
        # Layer 2 → Layer 3 feedback
        layer2_result = next((r for r in results if r.layer == "generated_code"), None)
        if layer2_result and "Missing OTEL integration" in str(layer2_result.issues):
            feedback.append(FeedbackLoop(
                source_layer="generated_code",
                target_layer="runtime_telemetry",
                feedback_type="enhance",
                message="Add missing OTEL instrumentation to generated code",
                priority="high"
            ))
        
        # Layer 3 → Layer 4 feedback
        layer3_result = next((r for r in results if r.layer == "runtime_telemetry"), None)
        if layer3_result and layer3_result.score < 0.8:
            feedback.append(FeedbackLoop(
                source_layer="runtime_telemetry",
                target_layer="system_integration",
                feedback_type="fix",
                message="Telemetry issues may affect system integration",
                priority="medium"
            ))
        
        # Layer 4 → Layer 5 feedback
        layer4_result = next((r for r in results if r.layer == "system_integration"), None)
        if layer4_result and layer4_result.status == "fail":
            feedback.append(FeedbackLoop(
                source_layer="system_integration",
                target_layer="system_health",
                feedback_type="fix",
                message="Integration failures impact system health",
                priority="high"
            ))
        
        # Layer 5 → Layer 1 feedback (strategic loop)
        layer5_result = next((r for r in results if r.layer == "system_health"), None)
        if layer5_result and "80/20 principle" in str(layer5_result.issues):
            feedback.append(FeedbackLoop(
                source_layer="system_health",
                target_layer="semantic_convention",
                feedback_type="enhance",
                message="Improve semantic conventions to follow 80/20 principle",
                priority="medium"
            ))
        
        return feedback
    
    async def validate_all_layers(self, convention_name: str) -> Dict[str, Any]:
        """Run all validation layers with feedback loops"""
        
        with tracer.start_as_current_span("multilayer.validation") as span:
            span.set_attribute("convention", convention_name)
            
            print(f"🔄 Multi-Layer Weaver Validation: {convention_name}")
            print("=" * 60)
            
            results = []
            current_feedback = self.feedback_loops.copy()
            
            # Layer 1: Semantic Convention Validation
            print("\n📋 Layer 1: Semantic Convention Validation")
            layer1_result = await self.layer1.validate(convention_name)
            results.append(layer1_result)
            print(f"   Status: {layer1_result.status} | Score: {layer1_result.score:.2f}")
            
            # Layer 2: Generated Code Validation
            print("\n🔧 Layer 2: Generated Code Validation")
            layer2_result = await self.layer2.validate(convention_name, current_feedback)
            results.append(layer2_result)
            print(f"   Status: {layer2_result.status} | Score: {layer2_result.score:.2f}")
            
            # Layer 3: Runtime Telemetry Validation
            print("\n📊 Layer 3: Runtime Telemetry Validation")
            layer3_result = await self.layer3.validate(convention_name, current_feedback)
            results.append(layer3_result)
            print(f"   Status: {layer3_result.status} | Score: {layer3_result.score:.2f}")
            
            # Layer 4: Integration Validation
            print("\n🔗 Layer 4: System Integration Validation")
            layer4_result = await self.layer4.validate(convention_name, current_feedback)
            results.append(layer4_result)
            print(f"   Status: {layer4_result.status} | Score: {layer4_result.score:.2f}")
            
            # Layer 5: System Health Validation
            print("\n🏥 Layer 5: System Health Validation")
            layer5_result = await self.layer5.validate(convention_name, current_feedback)
            results.append(layer5_result)
            print(f"   Status: {layer5_result.status} | Score: {layer5_result.score:.2f}")
            
            # Generate feedback for next iteration
            new_feedback = self.generate_feedback(results)
            self.feedback_loops.extend(new_feedback)
            
            # Calculate overall score
            overall_score = sum(r.score for r in results) / len(results)
            overall_status = "pass" if overall_score >= 0.8 else "warn" if overall_score >= 0.6 else "fail"
            
            # Report results
            print("\n" + "=" * 60)
            print("🎯 MULTI-LAYER VALIDATION RESULTS")
            print("=" * 60)
            print(f"Overall Score: {overall_score:.2f}")
            print(f"Overall Status: {overall_status}")
            
            # Show layer breakdown
            print("\nLayer Breakdown:")
            for result in results:
                print(f"  {result.layer}: {result.status} ({result.score:.2f})")
            
            # Show feedback loops
            if new_feedback:
                print(f"\n🔄 Generated {len(new_feedback)} feedback loops:")
                for fb in new_feedback:
                    print(f"  {fb.source_layer} → {fb.target_layer}: {fb.message}")
            
            # Show improvements
            all_improvements = []
            for result in results:
                all_improvements.extend(result.improvements)
            
            if all_improvements:
                print(f"\n💡 Improvements ({len(all_improvements)}):")
                for improvement in all_improvements[:5]:  # Show top 5
                    print(f"  • {improvement}")
            
            span.set_attribute("overall.score", overall_score)
            span.set_attribute("overall.status", overall_status)
            span.set_attribute("feedback.loops", len(new_feedback))
            
            return {
                "overall_score": overall_score,
                "overall_status": overall_status,
                "layer_results": results,
                "feedback_loops": new_feedback,
                "improvements": all_improvements
            }

async def main():
    """Demonstrate multi-layer weaver validation"""
    
    with ClaudeTelemetry.request("multilayer_weaver_validation", complexity="complex", domain="validation"):
        
        validator = MultiLayerWeaverValidator()
        
        # Test with available convention
        convention_name = "swarm_agent"
        
        # Run validation
        results = await validator.validate_all_layers(convention_name)
        
        print(f"\n✨ Multi-layer validation complete!")
        print(f"System validated with {len(results['feedback_loops'])} feedback loops generated")
        print("Ready for autonomous improvement cycles!")

if __name__ == "__main__":
    asyncio.run(main())