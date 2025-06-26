#!/usr/bin/env python3
"""
OpenTelemetry Concurrent Validation and Testing Framework
Tests DSLModel OpenTelemetry integration with concurrent operations
"""

import asyncio
import concurrent.futures
import time
import random
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
from collections import defaultdict

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich import box

console = Console()

@dataclass
class ValidationResult:
    """Result of a single validation test"""
    test_name: str
    permutation_id: str
    success: bool
    duration_ms: float
    trace_id: str
    span_id: str
    error: Optional[str] = None
    attributes: Dict[str, Any] = None

@dataclass
class ConcurrentTestMetrics:
    """Metrics for concurrent test execution"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float
    total_duration_ms: float
    concurrency_level: int
    spans_per_second: float
    traces_created: int

class OTelConcurrentValidator:
    """Validates OpenTelemetry integration with concurrent operations"""
    
    def __init__(self, service_name: str = "dslmodel_otel_validator"):
        self.service_name = service_name
        self.console = Console()
        self.results: List[ValidationResult] = []
        self.metrics_lock = threading.Lock()
        self.metrics_data = defaultdict(int)
        
        # Initialize OpenTelemetry
        self._init_telemetry()
        
    def _init_telemetry(self):
        """Initialize OpenTelemetry providers"""
        # Resource with service info
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": "testing"
        })
        
        # Trace provider
        trace_provider = TracerProvider(resource=resource)
        
        # OTLP exporter (configure endpoint as needed)
        otlp_exporter = OTLPSpanExporter(
            endpoint="localhost:4317",
            insecure=True
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__)
        
        # Metrics provider
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint="localhost:4317", insecure=True),
            export_interval_millis=1000
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        set_meter_provider(meter_provider)
        
        self.meter = metrics.get_meter(__name__)
        
        # Create metrics instruments
        self.test_counter = self.meter.create_counter(
            "dslmodel.validation.tests",
            unit="1",
            description="Number of validation tests executed"
        )
        
        self.test_duration = self.meter.create_histogram(
            "dslmodel.validation.duration",
            unit="ms",
            description="Duration of validation tests"
        )
        
        self.concurrent_gauge = self.meter.create_observable_gauge(
            "dslmodel.validation.concurrent",
            callbacks=[lambda _: [self.metrics_data.get("concurrent_tests", 0)]],
            description="Number of concurrent tests running"
        )
        
    async def validate_permutation_async(self, permutation_id: str, test_scenario: str) -> ValidationResult:
        """Validate a single permutation asynchronously"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span(
            f"validate_{permutation_id}",
            attributes={
                "dslmodel.permutation.id": permutation_id,
                "dslmodel.test.scenario": test_scenario,
                "dslmodel.test.async": True
            }
        ) as span:
            try:
                # Increment concurrent counter
                with self.metrics_lock:
                    self.metrics_data["concurrent_tests"] += 1
                
                # Simulate validation work
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                # Parse permutation ID
                parts = permutation_id.split("_")
                if len(parts) >= 3:
                    model_type, mixin_combo, gen_source = parts[0], parts[1], parts[2]
                    
                    span.set_attributes({
                        "dslmodel.model_type": model_type,
                        "dslmodel.mixin.combination": mixin_combo,
                        "dslmodel.generation.source": gen_source
                    })
                
                # Simulate random validation checks
                validations = {
                    "schema_valid": random.random() > 0.1,
                    "mixins_compatible": random.random() > 0.05,
                    "generation_successful": random.random() > 0.08,
                    "telemetry_configured": random.random() > 0.02
                }
                
                span.set_attributes({
                    f"validation.{k}": v for k, v in validations.items()
                })
                
                success = all(validations.values())
                
                if not success:
                    failed_checks = [k for k, v in validations.items() if not v]
                    error_msg = f"Failed checks: {', '.join(failed_checks)}"
                    span.set_status(Status(StatusCode.ERROR, error_msg))
                    raise ValueError(error_msg)
                
                span.set_status(Status(StatusCode.OK))
                
                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                self.test_counter.add(1, {"result": "success", "test_scenario": test_scenario})
                self.test_duration.record(duration_ms, {"permutation": permutation_id})
                
                return ValidationResult(
                    test_name=test_scenario,
                    permutation_id=permutation_id,
                    success=True,
                    duration_ms=duration_ms,
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    span_id=format(span.get_span_context().span_id, '016x'),
                    attributes=validations
                )
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_counter.add(1, {"result": "failure", "test_scenario": test_scenario})
                self.test_duration.record(duration_ms, {"permutation": permutation_id})
                
                return ValidationResult(
                    test_name=test_scenario,
                    permutation_id=permutation_id,
                    success=False,
                    duration_ms=duration_ms,
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    span_id=format(span.get_span_context().span_id, '016x'),
                    error=str(e)
                )
            finally:
                # Decrement concurrent counter
                with self.metrics_lock:
                    self.metrics_data["concurrent_tests"] -= 1
    
    def validate_permutation_sync(self, permutation_id: str, test_scenario: str) -> ValidationResult:
        """Validate a single permutation synchronously"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span(
            f"validate_{permutation_id}_sync",
            attributes={
                "dslmodel.permutation.id": permutation_id,
                "dslmodel.test.scenario": test_scenario,
                "dslmodel.test.async": False
            }
        ) as span:
            try:
                # Simulate validation work
                time.sleep(random.uniform(0.1, 0.3))
                
                # Simulate validation
                success = random.random() > 0.15
                
                if not success:
                    error_msg = "Simulated sync validation failure"
                    span.set_status(Status(StatusCode.ERROR, error_msg))
                    raise ValueError(error_msg)
                
                span.set_status(Status(StatusCode.OK))
                duration_ms = (time.time() - start_time) * 1000
                
                return ValidationResult(
                    test_name=test_scenario,
                    permutation_id=permutation_id,
                    success=True,
                    duration_ms=duration_ms,
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    span_id=format(span.get_span_context().span_id, '016x')
                )
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return ValidationResult(
                    test_name=test_scenario,
                    permutation_id=permutation_id,
                    success=False,
                    duration_ms=duration_ms,
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    span_id=format(span.get_span_context().span_id, '016x'),
                    error=str(e)
                )
    
    async def run_concurrent_async_tests(self, permutations: List[str], concurrency: int = 10) -> List[ValidationResult]:
        """Run async concurrent validation tests"""
        self.console.print(f"\n🚀 Running async concurrent tests (concurrency={concurrency})")
        
        with self.tracer.start_as_current_span("concurrent_async_validation") as span:
            span.set_attributes({
                "test.concurrency": concurrency,
                "test.total_permutations": len(permutations),
                "test.type": "async"
            })
            
            # Create test scenarios
            test_scenarios = ["schema_validation", "mixin_compatibility", "generation_test", "telemetry_check"]
            
            # Create all test tasks
            tasks = []
            for permutation in permutations:
                scenario = random.choice(test_scenarios)
                task = self.validate_permutation_async(permutation, scenario)
                tasks.append(task)
            
            # Run with limited concurrency
            semaphore = asyncio.Semaphore(concurrency)
            
            async def run_with_semaphore(task):
                async with semaphore:
                    return await task
            
            # Execute all tasks
            results = await asyncio.gather(*[run_with_semaphore(task) for task in tasks])
            
            # Update span with results
            successful = sum(1 for r in results if r.success)
            span.set_attributes({
                "test.successful": successful,
                "test.failed": len(results) - successful,
                "test.success_rate": successful / len(results) if results else 0
            })
            
            return results
    
    def run_concurrent_sync_tests(self, permutations: List[str], max_workers: int = 5) -> List[ValidationResult]:
        """Run sync concurrent validation tests using ThreadPoolExecutor"""
        self.console.print(f"\n🔄 Running sync concurrent tests (workers={max_workers})")
        
        with self.tracer.start_as_current_span("concurrent_sync_validation") as span:
            span.set_attributes({
                "test.max_workers": max_workers,
                "test.total_permutations": len(permutations),
                "test.type": "sync"
            })
            
            results = []
            test_scenarios = ["schema_validation", "mixin_compatibility", "generation_test", "telemetry_check"]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_permutation = {
                    executor.submit(
                        self.validate_permutation_sync, 
                        perm, 
                        random.choice(test_scenarios)
                    ): perm 
                    for perm in permutations
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_permutation):
                    result = future.result()
                    results.append(result)
            
            # Update span
            successful = sum(1 for r in results if r.success)
            span.set_attributes({
                "test.successful": successful,
                "test.failed": len(results) - successful,
                "test.success_rate": successful / len(results) if results else 0
            })
            
            return results
    
    def generate_test_report(self, results: List[ValidationResult]) -> ConcurrentTestMetrics:
        """Generate metrics report from test results"""
        if not results:
            return ConcurrentTestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        durations = [r.duration_ms for r in results]
        
        return ConcurrentTestMetrics(
            total_tests=len(results),
            successful_tests=successful,
            failed_tests=failed,
            avg_duration_ms=sum(durations) / len(durations),
            max_duration_ms=max(durations),
            min_duration_ms=min(durations),
            total_duration_ms=sum(durations),
            concurrency_level=self.metrics_data.get("max_concurrent", 0),
            spans_per_second=len(results) / (sum(durations) / 1000) if durations else 0,
            traces_created=len(set(r.trace_id for r in results))
        )
    
    def display_results(self, results: List[ValidationResult], title: str):
        """Display test results in a table"""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Permutation", style="cyan", width=30)
        table.add_column("Test", style="yellow", width=20)
        table.add_column("Status", style="green", width=10)
        table.add_column("Duration", style="blue", width=10)
        table.add_column("Trace ID", style="magenta", width=20)
        
        # Show sample of results
        for result in results[:10]:
            status = "✅ PASS" if result.success else "❌ FAIL"
            table.add_row(
                result.permutation_id,
                result.test_name,
                status,
                f"{result.duration_ms:.1f}ms",
                result.trace_id[:16] + "..."
            )
        
        if len(results) > 10:
            table.add_row("...", "...", "...", "...", "...")
        
        self.console.print(table)
    
    async def run_full_validation_suite(self):
        """Run complete concurrent validation suite"""
        self.console.print("🧪 [bold cyan]OpenTelemetry Concurrent Validation Suite[/bold cyan]")
        self.console.print("=" * 60)
        
        # Generate test permutations
        model_types = ["base", "fsm", "workflow", "agent", "event", "template"]
        mixin_combos = ["none", "jinja", "tool", "file", "all"]
        gen_sources = ["prompt", "schema", "api", "template", "weaver"]
        
        # Create subset of permutations for testing
        test_permutations = []
        for model in model_types[:3]:  # Test subset
            for mixin in mixin_combos[:3]:
                for source in gen_sources[:3]:
                    test_permutations.append(f"{model}_{mixin}_{source}")
        
        self.console.print(f"📊 Testing {len(test_permutations)} permutations")
        
        # Run async tests
        async_results = await self.run_concurrent_async_tests(test_permutations, concurrency=15)
        self.display_results(async_results, "Async Concurrent Test Results")
        async_metrics = self.generate_test_report(async_results)
        
        # Run sync tests
        sync_results = self.run_concurrent_sync_tests(test_permutations, max_workers=8)
        self.display_results(sync_results, "Sync Concurrent Test Results")
        sync_metrics = self.generate_test_report(sync_results)
        
        # Display metrics comparison
        self.display_metrics_comparison(async_metrics, sync_metrics)
        
        # Save results
        self.save_validation_results(async_results + sync_results)
        
        return async_results + sync_results
    
    def display_metrics_comparison(self, async_metrics: ConcurrentTestMetrics, sync_metrics: ConcurrentTestMetrics):
        """Display comparison of async vs sync metrics"""
        table = Table(title="Concurrent Test Metrics Comparison", box=box.DOUBLE_EDGE)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Async Tests", style="green", width=20)
        table.add_column("Sync Tests", style="blue", width=20)
        table.add_column("Difference", style="yellow", width=15)
        
        metrics = [
            ("Total Tests", async_metrics.total_tests, sync_metrics.total_tests),
            ("Successful", async_metrics.successful_tests, sync_metrics.successful_tests),
            ("Failed", async_metrics.failed_tests, sync_metrics.failed_tests),
            ("Avg Duration (ms)", f"{async_metrics.avg_duration_ms:.1f}", f"{sync_metrics.avg_duration_ms:.1f}"),
            ("Max Duration (ms)", f"{async_metrics.max_duration_ms:.1f}", f"{sync_metrics.max_duration_ms:.1f}"),
            ("Min Duration (ms)", f"{async_metrics.min_duration_ms:.1f}", f"{sync_metrics.min_duration_ms:.1f}"),
            ("Spans/Second", f"{async_metrics.spans_per_second:.1f}", f"{sync_metrics.spans_per_second:.1f}"),
            ("Traces Created", async_metrics.traces_created, sync_metrics.traces_created)
        ]
        
        for metric_name, async_val, sync_val in metrics:
            if isinstance(async_val, (int, float)) and isinstance(sync_val, (int, float)):
                diff = async_val - sync_val
                diff_str = f"+{diff}" if diff > 0 else str(diff)
            else:
                diff_str = "-"
            
            table.add_row(
                metric_name,
                str(async_val),
                str(sync_val),
                diff_str
            )
        
        self.console.print(table)
    
    def save_validation_results(self, results: List[ValidationResult]):
        """Save validation results to file"""
        output_dir = Path("output/otel_validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "service_name": self.service_name,
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [asdict(r) for r in results]
        }
        
        with open(output_dir / "validation_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        # Save trace mappings
        trace_map = defaultdict(list)
        for result in results:
            trace_map[result.trace_id].append({
                "span_id": result.span_id,
                "permutation": result.permutation_id,
                "test": result.test_name,
                "success": result.success
            })
        
        with open(output_dir / "trace_mappings.json", "w") as f:
            json.dump(dict(trace_map), f, indent=2)
        
        self.console.print(f"\n💾 Results saved to: {output_dir}")

async def main():
    """Run the concurrent validation suite"""
    validator = OTelConcurrentValidator()
    
    try:
        results = await validator.run_full_validation_suite()
        
        # Final summary
        successful = sum(1 for r in results if r.success)
        console.print(f"\n✅ Validation Complete!")
        console.print(f"📊 Total: {len(results)} | Success: {successful} | Failed: {len(results) - successful}")
        console.print(f"📈 Success Rate: {(successful/len(results)*100):.1f}%")
        
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())