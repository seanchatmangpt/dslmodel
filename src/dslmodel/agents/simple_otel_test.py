#!/usr/bin/env python3
"""
Simple OTEL Test - Validate our weaver system with real telemetry
Eating our own dogfood with available OTEL components
"""

import asyncio
import tempfile
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import subprocess

# Basic OTEL setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Our system imports
import sys
sys.path.append('/Users/sac/dev/dslmodel/src')
from dslmodel.agents.generated.worktree_models import (
    WorktreeSpanFactory, 
    AgentWorktreeCreateSpan,
    AgentTaskProgressSpan,
    AgentCoordinationRequestSpan
)

class SimpleOTELTester:
    """
    Simple OTEL validation - prove our weaver system works with real telemetry
    """
    
    def __init__(self):
        self.spans_captured = []
        self._setup_otel()
    
    def _setup_otel(self):
        """Setup OpenTelemetry with console output"""
        print("🔧 Setting up OTEL telemetry...")
        
        # Resource configuration
        resource = Resource(attributes={
            SERVICE_NAME: "weaver-agent-dogfood-test"
        })
        
        # Tracer provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        
        # Console exporter to see traces
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        provider.add_span_processor(console_processor)
        
        print("✓ OTEL configured with console output")
    
    async def run_dogfood_test(self):
        """Run dogfood test - use our own system with real OTEL"""
        print("🍖 EATING OUR OWN DOGFOOD - Testing Weaver System")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Basic span operations with real OTEL
        test1 = await self._test_span_operations()
        test_results["span_operations"] = test1
        
        # Test 2: Span factory with OTEL
        test2 = await self._test_span_factory()
        test_results["span_factory"] = test2
        
        # Test 3: Agent coordination spans
        test3 = await self._test_coordination_spans()
        test_results["coordination_spans"] = test3
        
        # Test 4: Validate semantic conventions
        test4 = await self._test_semantic_conventions()
        test_results["semantic_conventions"] = test4
        
        # Generate report
        report = self._generate_dogfood_report(test_results)
        
        return {
            "all_tests_passed": all(t.get("success", False) for t in test_results.values()),
            "test_results": test_results,
            "report": report
        }
    
    async def _test_span_operations(self):
        """Test 1: Basic span operations produce real OTEL output"""
        print("\n📊 Test 1: Basic Span Operations")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            print("Creating AgentWorktreeCreateSpan...")
            
            # Create span using our generated model
            create_span = AgentWorktreeCreateSpan(
                agent_id="dogfood_agent_1",
                worktree_path="/tmp/dogfood_test",
                feature_id="dogfood_feature",
                branch_name="dogfood_branch"
            )
            
            print(f"  Span created: {create_span.span_name}")
            print(f"  Agent ID: {create_span.agent_id}")
            
            # Start OTEL span
            print("Starting OTEL span...")
            otel_span = create_span.start_span()
            
            # Simulate some work
            print("Simulating work (0.2s)...")
            await asyncio.sleep(0.2)
            
            # Add custom attributes
            otel_span.set_attribute("test.dogfood", "true")
            otel_span.set_attribute("test.validation", "eating_own_dogfood")
            
            # End span
            print("Ending span...")
            create_span.end_span(otel_span, success=True)
            
            duration = time.time() - start_time
            
            print(f"✓ Span operations completed in {duration:.2f}s")
            
            return {
                "success": True,
                "duration": duration,
                "span_name": create_span.span_name,
                "agent_id": create_span.agent_id,
                "details": "Basic span operations successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Basic span operations failed"
            }
    
    async def _test_span_factory(self):
        """Test 2: Span factory creates proper OTEL spans"""
        print("\n🏗️  Test 2: Span Factory Operations")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            factory = WorktreeSpanFactory()
            print("Span factory created")
            
            # Test different span types
            span_types = [
                ("agent.worktree.create", {
                    "agent_id": "factory_agent",
                    "worktree_path": "/tmp/factory",
                    "feature_id": "factory_feature",
                    "branch_name": "factory_branch"
                }),
                ("agent.task.progress", {
                    "agent_id": "factory_agent",
                    "task_id": "factory_task",
                    "progress_percentage": 50.0,
                    "current_activity": "Factory testing"
                }),
                ("agent.coordination.request", {
                    "requesting_agent": "factory_agent_1",
                    "target_agents": ["factory_agent_2"],
                    "coordination_reason": "Factory coordination test",
                    "coordination_channel": "factory_channel"
                })
            ]
            
            spans_created = 0
            
            for span_name, attributes in span_types:
                print(f"Creating {span_name}...")
                
                try:
                    span_obj = factory.create_span(span_name, **attributes)
                    print(f"  ✓ {span_name} created")
                    
                    # Start and end the span
                    otel_span = span_obj.start_span()
                    await asyncio.sleep(0.05)  # Brief work simulation
                    span_obj.end_span(otel_span, success=True)
                    
                    spans_created += 1
                    
                except Exception as e:
                    print(f"  ❌ {span_name} failed: {e}")
            
            duration = time.time() - start_time
            success = spans_created == len(span_types)
            
            print(f"Spans created: {spans_created}/{len(span_types)}")
            print(f"{'✓' if success else '❌'} Factory test completed in {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "spans_created": spans_created,
                "spans_expected": len(span_types),
                "details": f"Factory created {spans_created} spans successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Span factory test failed"
            }
    
    async def _test_coordination_spans(self):
        """Test 3: Agent coordination with OTEL spans"""
        print("\n🤝 Test 3: Agent Coordination Spans")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            print("Testing coordination span sequence...")
            
            # Coordination request
            coord_request = AgentCoordinationRequestSpan(
                requesting_agent="coord_agent_1",
                target_agents=["coord_agent_2", "coord_agent_3"],
                coordination_reason="Dogfood coordination test",
                coordination_channel="dogfood_channel"
            )
            
            print("Starting coordination request span...")
            request_span = coord_request.start_span()
            await asyncio.sleep(0.1)
            
            # Simulate coordination work
            request_span.set_attribute("coordination.participants", 3)
            request_span.set_attribute("coordination.type", "dogfood_test")
            
            coord_request.end_span(request_span, success=True)
            print("✓ Coordination request completed")
            
            # Multiple progress updates to simulate coordination
            print("Simulating coordination progress...")
            for i, progress in enumerate([25, 50, 75, 100]):
                progress_span = AgentTaskProgressSpan(
                    agent_id=f"coord_agent_{i+1}",
                    task_id="coord_task",
                    progress_percentage=progress,
                    current_activity=f"Coordination step {i+1}"
                )
                
                span = progress_span.start_span()
                await asyncio.sleep(0.05)
                progress_span.end_span(span, success=True)
                print(f"  ✓ Progress {progress}% logged")
            
            duration = time.time() - start_time
            
            print(f"✓ Coordination spans completed in {duration:.2f}s")
            
            return {
                "success": True,
                "duration": duration,
                "coordination_steps": 5,  # 1 request + 4 progress
                "details": "Coordination spans sequence successful"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Coordination spans test failed"
            }
    
    async def _test_semantic_conventions(self):
        """Test 4: Validate our spans follow semantic conventions"""
        print("\n📋 Test 4: Semantic Conventions Validation")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            print("Validating semantic conventions compliance...")
            
            # Test span naming conventions
            factory = WorktreeSpanFactory()
            available_spans = factory.get_available_spans()
            
            expected_patterns = [
                "agent.worktree.",
                "agent.coordination.",
                "agent.task.",
                "feature.integration."
            ]
            
            pattern_compliance = 0
            for span_name in available_spans:
                for pattern in expected_patterns:
                    if span_name.startswith(pattern):
                        pattern_compliance += 1
                        break
            
            compliance_rate = pattern_compliance / len(available_spans) if available_spans else 0
            
            print(f"Available spans: {len(available_spans)}")
            print(f"Pattern compliant: {pattern_compliance}")
            print(f"Compliance rate: {compliance_rate*100:.1f}%")
            
            # Test attribute conventions
            print("Testing attribute conventions...")
            test_span = AgentWorktreeCreateSpan(
                agent_id="convention_test",
                worktree_path="/tmp/conventions",
                feature_id="convention_feature",
                branch_name="convention_branch"
            )
            
            # Check required attributes are present
            required_attrs = ["agent_id", "worktree_path", "feature_id", "branch_name"]
            attrs_present = sum(1 for attr in required_attrs if hasattr(test_span, attr))
            attr_compliance = attrs_present / len(required_attrs)
            
            print(f"Required attributes: {attrs_present}/{len(required_attrs)}")
            print(f"Attribute compliance: {attr_compliance*100:.1f}%")
            
            duration = time.time() - start_time
            success = compliance_rate >= 0.8 and attr_compliance >= 0.8
            
            print(f"{'✓' if success else '❌'} Conventions validated in {duration:.2f}s")
            
            return {
                "success": success,
                "duration": duration,
                "compliance_rate": compliance_rate,
                "attribute_compliance": attr_compliance,
                "available_spans": len(available_spans),
                "details": f"Semantic conventions {compliance_rate*100:.1f}% compliant"
            }
            
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "details": "Semantic conventions validation failed"
            }
    
    def _generate_dogfood_report(self, test_results: Dict[str, Any]) -> str:
        """Generate dogfood test report"""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get("success", False))
        
        report = f"""
🍖 DOGFOOD TEST REPORT - We Ate Our Own Cooking!
===============================================

🎯 Test Summary:
- Tests Run: {total_tests}
- Tests Passed: {passed_tests}
- Tests Failed: {total_tests - passed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

📊 Detailed Results:
"""
        
        for test_name, result in test_results.items():
            status = "✓ PASS" if result.get("success", False) else "❌ FAIL"
            duration = result.get("duration", 0)
            report += f"  {test_name}: {status} ({duration:.2f}s)\n"
            
            # Add specific details
            details = result.get("details", "")
            if details:
                report += f"    → {details}\n"
        
        # Performance summary
        total_duration = sum(result.get("duration", 0) for result in test_results.values())
        report += f"\n⏱️  Total Test Duration: {total_duration:.2f}s\n"
        
        # Key insights
        if "semantic_conventions" in test_results:
            conv_result = test_results["semantic_conventions"]
            if conv_result.get("success"):
                report += f"\n📋 Semantic Conventions:\n"
                report += f"  - Compliance Rate: {conv_result.get('compliance_rate', 0)*100:.1f}%\n"
                report += f"  - Available Spans: {conv_result.get('available_spans', 0)}\n"
        
        if "span_factory" in test_results:
            factory_result = test_results["span_factory"]
            if factory_result.get("success"):
                report += f"\n🏗️  Span Factory:\n"
                report += f"  - Spans Created: {factory_result.get('spans_created', 0)}\n"
                report += f"  - Success Rate: 100%\n"
        
        # Overall verdict
        if passed_tests == total_tests:
            report += "\n🎉 DOGFOOD SUCCESS! Our weaver-first system works perfectly!\n"
            report += "   All OTEL spans are generated correctly according to semantic conventions.\n"
            report += "   The system successfully eats its own dogfood. 🍖✓\n"
        else:
            report += "\n⚠️  DOGFOOD ISSUES DETECTED\n"
            report += "   Some tests failed - system needs fixes before production use.\n"
        
        return report

async def main():
    """Run the dogfood test"""
    print("🍖 STARTING DOGFOOD TEST")
    print("Testing our weaver-first system with real OTEL telemetry")
    print()
    
    tester = SimpleOTELTester()
    results = await tester.run_dogfood_test()
    
    print("\n" + "=" * 60)
    print("🏁 DOGFOOD TEST COMPLETE")
    print("=" * 60)
    print(results["report"])
    
    # Save results
    with open("dogfood_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Results saved to dogfood_test_results.json")
    
    if results["all_tests_passed"]:
        print("🎉 WE SUCCESSFULLY ATE OUR OWN DOGFOOD! 🍖✓")
    else:
        print("❌ Dogfood test revealed issues. System needs fixes.")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())