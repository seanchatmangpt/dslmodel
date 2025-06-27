#!/usr/bin/env python3
"""
OTEL Validation - Actually test our weaver system with real telemetry
Eat our own dogfood - validate the OTEL traces work as designed
"""

import asyncio
import tempfile
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import subprocess

# OTEL Setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Our system imports
import sys
sys.path.append('/Users/sac/dev/dslmodel/src')
from dslmodel.agents.generated.worktree_models import (
    WorktreeSpanFactory, 
    create_worktree_span,
    create_coordination_request,
    create_task_progress
)
from dslmodel.agents.worktree_pipeline import AgentWorktreePipeline

class OTELValidator:
    """
    Validates our weaver-first system with real OTEL telemetry
    """
    
    def __init__(self):
        self.traces_collected = []
        self.test_repo_path = None
        self.pipeline = None
        
        # Setup real OTEL
        self._setup_otel()
    
    def _setup_otel(self):
        """Setup real OpenTelemetry instrumentation"""
        print("🔧 Setting up real OTEL instrumentation...")
        
        # Create resource
        resource = Resource(attributes={
            SERVICE_NAME: "weaver-agent-system"
        })
        
        # Setup tracer provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        
        # Add console exporter to see traces
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        provider.add_span_processor(console_processor)
        
        # Add custom span collector
        collector = SpanCollector(self.traces_collected)
        collector_processor = BatchSpanProcessor(collector)
        provider.add_span_processor(collector_processor)
        
        print("✓ OTEL instrumentation configured")
        
        # Auto-instrument common libraries
        RequestsInstrumentor().instrument()
        
        return trace.get_tracer(__name__)
    
    async def run_otel_validation(self) -> Dict[str, Any]:
        """Run complete OTEL validation with real traces"""
        print("🧪 Starting OTEL Validation - Eating Our Own Dogfood")
        print("=" * 60)
        
        validation_results = {}
        
        try:
            # Setup test environment
            await self._setup_test_environment()
            
            # Test 1: Basic span generation
            basic_spans = await self._test_basic_span_generation()
            validation_results["basic_spans"] = basic_spans
            
            # Test 2: Worktree pipeline with OTEL
            pipeline_test = await self._test_pipeline_with_otel()
            validation_results["pipeline_otel"] = pipeline_test
            
            # Test 3: Multi-agent coordination with traces
            coordination_test = await self._test_coordination_traces()
            validation_results["coordination_traces"] = coordination_test
            
            # Test 4: Validate semantic conventions compliance
            conventions_test = await self._test_semantic_conventions_compliance()
            validation_results["conventions_compliance"] = conventions_test
            
            # Test 5: Trace analysis and metrics
            trace_analysis = await self._analyze_collected_traces()
            validation_results["trace_analysis"] = trace_analysis
            
            # Generate OTEL validation report
            report = self._generate_otel_report(validation_results)
            
            return {
                "validation_successful": all(r.get("success", False) for r in validation_results.values()),
                "traces_collected": len(self.traces_collected),
                "validation_results": validation_results,
                "report": report
            }
            
        finally:
            await self._cleanup_test_environment()
    
    async def _setup_test_environment(self):
        """Setup test environment for OTEL validation"""
        print("🔧 Setting up OTEL test environment...")
        
        # Create temporary git repository
        self.test_repo_path = Path(tempfile.mkdtemp(prefix="otel_validation_"))
        os.chdir(self.test_repo_path)
        
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "otel@test.weaver"], check=True)
        subprocess.run(["git", "config", "user.name", "OTEL Validator"], check=True)
        
        # Create initial commit
        (self.test_repo_path / "README.md").write_text("# OTEL Validation Repository")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit for OTEL validation"], check=True)
        
        # Initialize pipeline
        self.pipeline = AgentWorktreePipeline(str(self.test_repo_path))
        
        print(f"✓ OTEL test environment ready at {self.test_repo_path}")
    
    async def _test_basic_span_generation(self) -> Dict[str, Any]:
        """Test 1: Validate basic span generation produces real OTEL traces"""
        print("\n📊 Test 1: Basic Span Generation with OTEL")
        print("-" * 40)
        
        start_time = time.time()
        spans_before = len(self.traces_collected)
        
        try:
            # Test each span type from our generated models
            factory = WorktreeSpanFactory()
            
            # Test worktree creation span
            create_span_data = factory.create_span(
                "agent.worktree.create",
                agent_id="otel_test_agent",
                worktree_path="/tmp/otel_test",
                feature_id="otel_validation_feature",
                branch_name="otel_test_branch"
            )
            
            otel_span = create_span_data.start_span()
            await asyncio.sleep(0.1)  # Simulate work
            create_span_data.end_span(otel_span, success=True)
            
            # Test coordination request span
            coord_span = create_coordination_request(
                "otel_agent_1", 
                ["otel_agent_2", "otel_agent_3"],
                "OTEL validation coordination",
                "otel_channel"
            )
            await asyncio.sleep(0.05)
            coord_span.end()
            
            # Test progress span
            progress_span = create_task_progress(
                "otel_agent_1",
                "otel_task_123", 
                75.0,
                "OTEL validation in progress",
                ["otel_test.py"]
            )
            await asyncio.sleep(0.05)
            progress_span.end()
            
            # Wait for span processing
            await asyncio.sleep(0.5)
            
            spans_after = len(self.traces_collected)
            spans_generated = spans_after - spans_before
            
            duration = time.time() - start_time
            success = spans_generated >= 3
            
            print(f"  Spans generated: {spans_generated}")
            print(f"  OTEL integration: {'✓' if success else '✗'}")
            print(f"  Duration: {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "spans_generated": spans_generated,
                "spans_expected": 3,
                "details": f"Generated {spans_generated} OTEL spans"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Basic span generation failed"
            }
    
    async def _test_pipeline_with_otel(self) -> Dict[str, Any]:
        """Test 2: Run actual pipeline operations and validate OTEL traces"""
        print("\n🔄 Test 2: Pipeline Operations with OTEL Tracing")
        print("-" * 40)
        
        start_time = time.time()
        spans_before = len(self.traces_collected)
        
        try:
            # Run actual pipeline operations
            agent_id = "otel_pipeline_agent"
            feature_id = "otel_pipeline_feature"
            branch_name = "otel_pipeline_branch"
            
            # Create worktree with OTEL tracing
            worktree_path = await self.pipeline.create_agent_worktree(
                agent_id, feature_id, branch_name
            )
            
            # Activate agent with OTEL tracing
            await self.pipeline.activate_agent(agent_id, ["otel", "validation", "testing"])
            
            # Assign and progress task with OTEL tracing
            task_id = "otel_validation_task"
            await self.pipeline.assign_task(
                agent_id, task_id, "OTEL validation task", 2000.0
            )
            
            # Multiple progress updates
            for progress in [25, 50, 75, 100]:
                await self.pipeline.report_progress(
                    agent_id, task_id, progress, f"OTEL validation at {progress}%"
                )
                await asyncio.sleep(0.1)
            
            # Complete task
            await self.pipeline.complete_task(
                agent_id, task_id, "success", ["otel_validation.py"]
            )
            
            # Wait for span processing
            await asyncio.sleep(1.0)
            
            spans_after = len(self.traces_collected)
            pipeline_spans = spans_after - spans_before
            
            # Cleanup
            await self.pipeline.cleanup_worktree(agent_id)
            
            duration = time.time() - start_time
            success = pipeline_spans >= 6  # Expected spans from pipeline operations
            
            print(f"  Pipeline spans: {pipeline_spans}")
            print(f"  Worktree created: {'✓' if Path(worktree_path).parent.exists() else '✗'}")
            print(f"  OTEL traces: {'✓' if success else '✗'}")
            print(f"  Duration: {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "pipeline_spans": pipeline_spans,
                "expected_spans": 6,
                "worktree_path": worktree_path,
                "details": f"Pipeline generated {pipeline_spans} OTEL spans"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Pipeline OTEL test failed"
            }
    
    async def _test_coordination_traces(self) -> Dict[str, Any]:
        """Test 3: Multi-agent coordination with distributed tracing"""
        print("\n🤝 Test 3: Multi-Agent Coordination Tracing")
        print("-" * 40)
        
        start_time = time.time()
        spans_before = len(self.traces_collected)
        
        try:
            # Setup multiple agents
            agents = ["otel_coord_1", "otel_coord_2", "otel_coord_3"]
            feature_id = "otel_coordination_feature"
            
            # Create worktrees for all agents with tracing
            for i, agent_id in enumerate(agents):
                branch_name = f"otel_coord_branch_{i+1}"
                await self.pipeline.create_agent_worktree(agent_id, feature_id, branch_name)
                await self.pipeline.activate_agent(agent_id, ["coordination", "otel"])
            
            # Test coordination with distributed tracing
            coord_id = await self.pipeline.request_coordination(
                agents[0], agents[1:], "OTEL distributed coordination test"
            )
            
            # Agents respond with tracing
            for agent_id in agents[1:]:
                await self.pipeline.respond_to_coordination(agent_id, coord_id, "accept")
                await asyncio.sleep(0.1)
            
            # Feature integration with tracing
            await self.pipeline.integrate_feature(feature_id, agents, "parallel")
            
            # Cleanup with tracing
            for agent_id in agents:
                await self.pipeline.cleanup_worktree(agent_id)
            
            # Wait for span processing
            await asyncio.sleep(1.0)
            
            spans_after = len(self.traces_collected)
            coordination_spans = spans_after - spans_before
            
            duration = time.time() - start_time
            success = coordination_spans >= 10  # Expected spans from coordination
            
            print(f"  Coordination spans: {coordination_spans}")
            print(f"  Agents coordinated: {len(agents)}")
            print(f"  Distributed traces: {'✓' if success else '✗'}")
            print(f"  Duration: {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "coordination_spans": coordination_spans,
                "agents_count": len(agents),
                "expected_spans": 10,
                "details": f"Coordination generated {coordination_spans} distributed traces"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Coordination tracing test failed"
            }
    
    async def _test_semantic_conventions_compliance(self) -> Dict[str, Any]:
        """Test 4: Validate traces comply with our semantic conventions"""
        print("\n📋 Test 4: Semantic Conventions Compliance")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Analyze collected traces for compliance
            compliant_spans = 0
            total_spans = len(self.traces_collected)
            
            expected_span_names = {
                "agent.worktree.create",
                "agent.worktree.activate",
                "agent.coordination.request", 
                "agent.coordination.response",
                "agent.task.start",
                "agent.task.progress",
                "agent.task.complete",
                "feature.integration.start",
                "feature.integration.merge",
                "feature.integration.complete"
            }
            
            span_names_found = set()
            required_attributes_found = 0
            
            for span_data in self.traces_collected:
                span_name = span_data.get("name", "")
                attributes = span_data.get("attributes", {})
                
                # Check if span name matches conventions
                if span_name in expected_span_names:
                    compliant_spans += 1
                    span_names_found.add(span_name)
                
                # Check for required attributes
                if "agent.id" in attributes:
                    required_attributes_found += 1
            
            compliance_rate = compliant_spans / max(total_spans, 1)
            conventions_coverage = len(span_names_found) / len(expected_span_names)
            
            duration = time.time() - start_time
            success = compliance_rate >= 0.8 and conventions_coverage >= 0.5
            
            print(f"  Compliant spans: {compliant_spans}/{total_spans} ({compliance_rate*100:.1f}%)")
            print(f"  Convention coverage: {len(span_names_found)}/{len(expected_span_names)} ({conventions_coverage*100:.1f}%)")
            print(f"  Required attributes: {required_attributes_found}")
            print(f"  Compliance: {'✓' if success else '✗'}")
            print(f"  Duration: {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "compliance_rate": compliance_rate,
                "conventions_coverage": conventions_coverage,
                "compliant_spans": compliant_spans,
                "total_spans": total_spans,
                "span_names_found": list(span_names_found),
                "details": f"Compliance rate: {compliance_rate*100:.1f}%"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Semantic conventions compliance test failed"
            }
    
    async def _analyze_collected_traces(self) -> Dict[str, Any]:
        """Test 5: Analyze collected traces for insights"""
        print("\n📈 Test 5: Trace Analysis and Metrics")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            total_traces = len(self.traces_collected)
            
            if total_traces == 0:
                return {
                    "success": False,
                    "duration": time.time() - start_time,
                    "details": "No traces collected for analysis"
                }
            
            # Analyze trace patterns
            span_durations = []
            span_counts_by_name = {}
            error_spans = 0
            
            for span_data in self.traces_collected:
                span_name = span_data.get("name", "unknown")
                duration = span_data.get("duration_ms", 0)
                status = span_data.get("status", {})
                
                span_durations.append(duration)
                span_counts_by_name[span_name] = span_counts_by_name.get(span_name, 0) + 1
                
                if status.get("status_code") == "ERROR":
                    error_spans += 1
            
            # Calculate metrics
            avg_duration = sum(span_durations) / len(span_durations) if span_durations else 0
            max_duration = max(span_durations) if span_durations else 0
            min_duration = min(span_durations) if span_durations else 0
            error_rate = error_spans / total_traces if total_traces > 0 else 0
            
            # Identify most frequent spans
            most_frequent_span = max(span_counts_by_name.items(), key=lambda x: x[1]) if span_counts_by_name else ("none", 0)
            
            duration = time.time() - start_time
            success = total_traces > 0 and error_rate < 0.1
            
            print(f"  Total traces: {total_traces}")
            print(f"  Avg duration: {avg_duration:.2f}ms")
            print(f"  Duration range: {min_duration:.2f}ms - {max_duration:.2f}ms")
            print(f"  Error rate: {error_rate*100:.1f}%")
            print(f"  Most frequent: {most_frequent_span[0]} ({most_frequent_span[1]} times)")
            print(f"  Analysis: {'✓' if success else '✗'}")
            print(f"  Duration: {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "total_traces": total_traces,
                "avg_duration_ms": avg_duration,
                "max_duration_ms": max_duration,
                "min_duration_ms": min_duration,
                "error_rate": error_rate,
                "span_counts": span_counts_by_name,
                "most_frequent_span": most_frequent_span,
                "details": f"Analyzed {total_traces} traces with {error_rate*100:.1f}% error rate"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Trace analysis failed"
            }
    
    def _generate_otel_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate comprehensive OTEL validation report"""
        total_tests = len(validation_results)
        passed_tests = sum(1 for result in validation_results.values() if result.get("success", False))
        
        report = f"""
OTEL Validation Report - Eating Our Own Dogfood
===============================================

🔍 Validation Summary:
- Tests Run: {total_tests}
- Tests Passed: {passed_tests}
- Tests Failed: {total_tests - passed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%
- Total Traces: {len(self.traces_collected)}

📊 Test Results:
"""
        
        for test_name, result in validation_results.items():
            status = "✓ PASS" if result.get("success", False) else "✗ FAIL"
            duration = result.get("duration", 0)
            report += f"  {test_name}: {status} ({duration:.2f}s)\n"
            
            # Add specific metrics
            if test_name == "basic_spans" and "spans_generated" in result:
                report += f"    → Generated {result['spans_generated']} spans\n"
            elif test_name == "pipeline_otel" and "pipeline_spans" in result:
                report += f"    → Pipeline created {result['pipeline_spans']} spans\n"
            elif test_name == "coordination_traces" and "coordination_spans" in result:
                report += f"    → Coordination created {result['coordination_spans']} spans\n"
            elif test_name == "conventions_compliance" and "compliance_rate" in result:
                report += f"    → Compliance: {result['compliance_rate']*100:.1f}%\n"
            elif test_name == "trace_analysis" and "total_traces" in result:
                report += f"    → Analyzed {result['total_traces']} traces\n"
        
        # Performance summary
        total_duration = sum(result.get("duration", 0) for result in validation_results.values())
        report += f"\n⏱️  Total Validation Time: {total_duration:.2f}s\n"
        
        # Trace analysis summary
        if "trace_analysis" in validation_results:
            analysis = validation_results["trace_analysis"]
            if analysis.get("success"):
                report += f"\n📈 Trace Performance:\n"
                report += f"  - Average span duration: {analysis.get('avg_duration_ms', 0):.2f}ms\n"
                report += f"  - Error rate: {analysis.get('error_rate', 0)*100:.1f}%\n"
                
                most_frequent = analysis.get("most_frequent_span", ("none", 0))
                report += f"  - Most frequent span: {most_frequent[0]} ({most_frequent[1]} times)\n"
        
        # Recommendations
        if passed_tests < total_tests:
            report += "\n🔧 Recommendations:\n"
            for test_name, result in validation_results.items():
                if not result.get("success", False):
                    if "error" in result:
                        report += f"  - Fix {test_name}: {result['error']}\n"
                    else:
                        report += f"  - Review {test_name}: {result.get('details', 'No details')}\n"
        else:
            report += "\n🎉 All OTEL validations passed! System is working correctly.\n"
        
        return report
    
    async def _cleanup_test_environment(self):
        """Cleanup OTEL test environment"""
        if self.test_repo_path and self.test_repo_path.exists():
            os.chdir("/")
            import shutil
            shutil.rmtree(self.test_repo_path)
            print(f"✓ OTEL test environment cleaned up")

class SpanCollector:
    """Custom span collector to capture traces for validation"""
    
    def __init__(self, traces_list: List[Dict[str, Any]]):
        self.traces_list = traces_list
    
    def export(self, spans):
        """Export spans to our collection"""
        for span in spans:
            span_data = {
                "name": span.name,
                "trace_id": f"{span.context.trace_id:032x}",
                "span_id": f"{span.context.span_id:016x}",
                "parent_id": f"{span.parent.span_id:016x}" if span.parent else None,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ms": (span.end_time - span.start_time) / 1_000_000 if span.end_time else 0,
                "status": {
                    "status_code": span.status.status_code.name,
                    "description": span.status.description
                },
                "attributes": dict(span.attributes) if span.attributes else {},
                "events": [{"name": event.name, "timestamp": event.timestamp, "attributes": dict(event.attributes)} for event in span.events] if span.events else []
            }
            self.traces_list.append(span_data)
        
        return None  # Success
    
    def shutdown(self):
        """Shutdown collector"""
        pass

async def main():
    """Run OTEL validation - eat our own dogfood"""
    validator = OTELValidator()
    results = await validator.run_otel_validation()
    
    print("\n" + "=" * 60)
    print("🏁 OTEL Validation Complete")
    print("=" * 60)
    print(results["report"])
    
    # Save detailed results
    with open("otel_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to otel_validation_results.json")
    
    if results["validation_successful"]:
        print("🎉 OTEL validation passed! We successfully ate our own dogfood.")
    else:
        print("❌ OTEL validation failed. System needs fixes.")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())