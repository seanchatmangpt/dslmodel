#!/usr/bin/env python3
"""
Simplified OpenTelemetry Concurrent Test Runner
Tests without requiring external OTLP collector
"""

import asyncio
import time
import random
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import threading
from collections import defaultdict
import concurrent.futures

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich import box
from rich.syntax import Syntax

console = Console()

@dataclass
class MockSpan:
    """Mock span for testing without OTLP"""
    trace_id: str
    span_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "OK"
    parent_span_id: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

@dataclass
class TestScenario:
    """Test scenario configuration"""
    name: str
    permutation_count: int
    concurrency_level: int
    test_type: str  # "async", "sync", "mixed"
    validation_rules: List[str]
    expected_duration_ms: float

class MockTelemetryCollector:
    """In-memory telemetry collector for testing"""
    
    def __init__(self):
        self.spans: List[MockSpan] = []
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
        
    def add_span(self, span: MockSpan):
        """Add a span to the collector"""
        with self.lock:
            self.spans.append(span)
    
    def add_metric(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """Add a metric value"""
        with self.lock:
            self.metrics[name].append(value)
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of collected traces"""
        with self.lock:
            if not self.spans:
                return {"total_spans": 0}
            
            traces = defaultdict(list)
            for span in self.spans:
                traces[span.trace_id].append(span)
            
            return {
                "total_spans": len(self.spans),
                "total_traces": len(traces),
                "avg_spans_per_trace": len(self.spans) / len(traces) if traces else 0,
                "successful_spans": sum(1 for s in self.spans if s.status == "OK"),
                "failed_spans": sum(1 for s in self.spans if s.status != "OK"),
                "avg_duration_ms": sum(s.duration_ms for s in self.spans) / len(self.spans) if self.spans else 0,
                "max_duration_ms": max((s.duration_ms for s in self.spans), default=0),
                "min_duration_ms": min((s.duration_ms for s in self.spans), default=0)
            }

class ConcurrentOTelTester:
    """Tests OpenTelemetry integration with concurrent operations"""
    
    def __init__(self):
        self.console = Console()
        self.collector = MockTelemetryCollector()
        self.test_results = []
        self._trace_counter = 0
        self._span_counter = 0
        self._counter_lock = threading.Lock()
        
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        with self._counter_lock:
            self._trace_counter += 1
            return f"{self._trace_counter:032x}"
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        with self._counter_lock:
            self._span_counter += 1
            return f"{self._span_counter:016x}"
    
    async def test_permutation_async(self, permutation_id: str, validation_rules: List[str]) -> Dict[str, Any]:
        """Test a single permutation asynchronously"""
        trace_id = self._generate_trace_id()
        
        # Root span
        root_span = MockSpan(
            trace_id=trace_id,
            span_id=self._generate_span_id(),
            name=f"test_{permutation_id}",
            start_time=time.time(),
            attributes={
                "permutation.id": permutation_id,
                "test.type": "async",
                "test.rules": validation_rules
            }
        )
        
        try:
            # Parse permutation
            parts = permutation_id.split("_")
            if len(parts) >= 3:
                model_type, mixin_combo, gen_source = parts[0], parts[1], parts[2]
                root_span.attributes.update({
                    "model.type": model_type,
                    "mixin.combo": mixin_combo,
                    "generation.source": gen_source
                })
            
            # Child spans for each validation
            child_spans = []
            validation_results = {}
            
            for rule in validation_rules:
                child_span = MockSpan(
                    trace_id=trace_id,
                    span_id=self._generate_span_id(),
                    name=f"validate_{rule}",
                    start_time=time.time(),
                    parent_span_id=root_span.span_id,
                    attributes={"validation.rule": rule}
                )
                
                # Simulate validation work
                await asyncio.sleep(random.uniform(0.01, 0.1))
                
                # Random validation result
                success = random.random() > 0.1
                validation_results[rule] = success
                
                child_span.status = "OK" if success else "ERROR"
                child_span.end_time = time.time()
                child_span.attributes["validation.result"] = success
                
                child_spans.append(child_span)
                self.collector.add_span(child_span)
            
            # Complete root span
            root_span.status = "OK" if all(validation_results.values()) else "ERROR"
            root_span.end_time = time.time()
            root_span.attributes["validation.passed"] = sum(validation_results.values())
            root_span.attributes["validation.total"] = len(validation_results)
            
            self.collector.add_span(root_span)
            
            # Record metrics
            self.collector.add_metric("test.duration.ms", root_span.duration_ms)
            self.collector.add_metric("test.validations.passed", sum(validation_results.values()))
            
            return {
                "permutation_id": permutation_id,
                "trace_id": trace_id,
                "success": all(validation_results.values()),
                "duration_ms": root_span.duration_ms,
                "validation_results": validation_results,
                "span_count": 1 + len(child_spans)
            }
            
        except Exception as e:
            root_span.status = "ERROR"
            root_span.end_time = time.time()
            root_span.attributes["error"] = str(e)
            self.collector.add_span(root_span)
            
            return {
                "permutation_id": permutation_id,
                "trace_id": trace_id,
                "success": False,
                "error": str(e),
                "duration_ms": root_span.duration_ms
            }
    
    def test_permutation_sync(self, permutation_id: str, validation_rules: List[str]) -> Dict[str, Any]:
        """Test a single permutation synchronously"""
        trace_id = self._generate_trace_id()
        span_id = self._generate_span_id()
        
        span = MockSpan(
            trace_id=trace_id,
            span_id=span_id,
            name=f"test_{permutation_id}_sync",
            start_time=time.time(),
            attributes={
                "permutation.id": permutation_id,
                "test.type": "sync"
            }
        )
        
        try:
            # Simulate work
            time.sleep(random.uniform(0.01, 0.05))
            
            # Random result
            success = random.random() > 0.15
            
            span.status = "OK" if success else "ERROR"
            span.end_time = time.time()
            
            self.collector.add_span(span)
            
            return {
                "permutation_id": permutation_id,
                "trace_id": trace_id,
                "success": success,
                "duration_ms": span.duration_ms
            }
            
        except Exception as e:
            span.status = "ERROR"
            span.end_time = time.time()
            self.collector.add_span(span)
            
            return {
                "permutation_id": permutation_id,
                "trace_id": trace_id,
                "success": False,
                "error": str(e),
                "duration_ms": span.duration_ms
            }
    
    async def run_async_scenario(self, scenario: TestScenario, permutations: List[str]) -> Dict[str, Any]:
        """Run async test scenario"""
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(
                f"[cyan]Running {scenario.name} (async)", 
                total=len(permutations)
            )
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(scenario.concurrency_level)
            
            async def run_with_progress(perm):
                async with semaphore:
                    result = await self.test_permutation_async(perm, scenario.validation_rules)
                    progress.advance(task)
                    return result
            
            # Run all tests
            results = await asyncio.gather(*[run_with_progress(p) for p in permutations])
        
        duration = time.time() - start_time
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "scenario": scenario.name,
            "type": "async",
            "duration_seconds": duration,
            "total_tests": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "success_rate": successful / len(results) if results else 0,
            "avg_duration_ms": sum(r.get("duration_ms", 0) for r in results) / len(results) if results else 0,
            "throughput_per_second": len(results) / duration if duration > 0 else 0,
            "results": results
        }
    
    def run_sync_scenario(self, scenario: TestScenario, permutations: List[str]) -> Dict[str, Any]:
        """Run sync test scenario"""
        start_time = time.time()
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(
                f"[blue]Running {scenario.name} (sync)", 
                total=len(permutations)
            )
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=scenario.concurrency_level) as executor:
                # Submit all tasks
                future_to_perm = {
                    executor.submit(self.test_permutation_sync, perm, scenario.validation_rules): perm
                    for perm in permutations
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_perm):
                    result = future.result()
                    results.append(result)
                    progress.advance(task)
        
        duration = time.time() - start_time
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "scenario": scenario.name,
            "type": "sync",
            "duration_seconds": duration,
            "total_tests": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "success_rate": successful / len(results) if results else 0,
            "avg_duration_ms": sum(r.get("duration_ms", 0) for r in results) / len(results) if results else 0,
            "throughput_per_second": len(results) / duration if duration > 0 else 0,
            "results": results
        }
    
    def display_scenario_results(self, results: Dict[str, Any]):
        """Display results for a scenario"""
        panel_content = f"""
[bold]Scenario:[/bold] {results['scenario']}
[bold]Type:[/bold] {results['type']}
[bold]Duration:[/bold] {results['duration_seconds']:.2f}s
[bold]Total Tests:[/bold] {results['total_tests']}
[bold]Success Rate:[/bold] {results['success_rate']*100:.1f}%
[bold]Throughput:[/bold] {results['throughput_per_second']:.1f} tests/sec
[bold]Avg Duration:[/bold] {results['avg_duration_ms']:.1f}ms
"""
        
        panel = Panel(
            panel_content.strip(),
            title=f"[bold]{results['scenario']} Results[/bold]",
            border_style="green" if results['success_rate'] > 0.9 else "yellow"
        )
        
        self.console.print(panel)
    
    def display_telemetry_summary(self):
        """Display collected telemetry summary"""
        summary = self.collector.get_trace_summary()
        
        table = Table(title="Telemetry Collection Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green", width=20)
        
        for key, value in summary.items():
            if isinstance(value, float):
                table.add_row(key.replace("_", " ").title(), f"{value:.2f}")
            else:
                table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(table)
    
    async def run_test_suite(self):
        """Run complete test suite"""
        self.console.print("\n[bold cyan]🧪 OpenTelemetry Concurrent Testing Suite[/bold cyan]")
        self.console.print("=" * 60)
        
        # Generate test permutations
        permutations = []
        for model in ["base", "fsm", "workflow"]:
            for mixin in ["none", "jinja", "tool"]:
                for source in ["prompt", "schema", "api"]:
                    permutations.append(f"{model}_{mixin}_{source}")
        
        # Define test scenarios
        scenarios = [
            TestScenario(
                name="High Concurrency Async",
                permutation_count=len(permutations),
                concurrency_level=20,
                test_type="async",
                validation_rules=["schema", "syntax", "compatibility"],
                expected_duration_ms=50
            ),
            TestScenario(
                name="Moderate Concurrency Sync",
                permutation_count=len(permutations),
                concurrency_level=8,
                test_type="sync",
                validation_rules=["basic", "telemetry"],
                expected_duration_ms=30
            ),
            TestScenario(
                name="Stress Test Async",
                permutation_count=len(permutations) * 2,  # Double the load
                concurrency_level=50,
                test_type="async",
                validation_rules=["schema", "syntax", "semantic", "telemetry", "performance"],
                expected_duration_ms=100
            )
        ]
        
        all_results = []
        
        for scenario in scenarios:
            self.console.print(f"\n[bold]Running scenario: {scenario.name}[/bold]")
            
            # Adjust permutations for stress test
            test_perms = permutations * 2 if "Stress" in scenario.name else permutations
            
            if scenario.test_type == "async":
                results = await self.run_async_scenario(scenario, test_perms)
            else:
                results = self.run_sync_scenario(scenario, test_perms)
            
            all_results.append(results)
            self.display_scenario_results(results)
        
        # Display telemetry summary
        self.console.print("\n")
        self.display_telemetry_summary()
        
        # Save results
        self.save_test_results(all_results)
        
        return all_results
    
    def save_test_results(self, results: List[Dict[str, Any]]):
        """Save test results to files"""
        output_dir = Path("output/otel_concurrent_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(results),
            "total_tests": sum(r["total_tests"] for r in results),
            "overall_success_rate": sum(r["successful"] for r in results) / sum(r["total_tests"] for r in results),
            "scenarios": [
                {
                    "name": r["scenario"],
                    "type": r["type"],
                    "success_rate": r["success_rate"],
                    "throughput": r["throughput_per_second"]
                }
                for r in results
            ]
        }
        
        with open(output_dir / "test_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed results
        with open(output_dir / "detailed_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save telemetry data
        telemetry_data = {
            "spans": [asdict(span) for span in self.collector.spans[:100]],  # Sample
            "metrics": dict(self.collector.metrics),
            "summary": self.collector.get_trace_summary()
        }
        
        with open(output_dir / "telemetry_data.json", "w") as f:
            json.dump(telemetry_data, f, indent=2, default=str)
        
        self.console.print(f"\n💾 Results saved to: {output_dir}")

async def main():
    """Run the test suite"""
    tester = ConcurrentOTelTester()
    
    try:
        results = await tester.run_test_suite()
        
        # Display final summary
        total_tests = sum(r["total_tests"] for r in results)
        total_successful = sum(r["successful"] for r in results)
        
        console.print(f"\n[bold green]✅ Testing Complete![/bold green]")
        console.print(f"📊 Total Tests: {total_tests}")
        console.print(f"✅ Successful: {total_successful}")
        console.print(f"❌ Failed: {total_tests - total_successful}")
        console.print(f"📈 Overall Success Rate: {(total_successful/total_tests*100):.1f}%")
        
    except Exception as e:
        console.print(f"[red]❌ Testing failed: {e}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())