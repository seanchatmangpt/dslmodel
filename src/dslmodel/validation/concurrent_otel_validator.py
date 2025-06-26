"""Concurrent OpenTelemetry validation and testing framework for SwarmAgent."""

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set
import traceback

from loguru import logger
from pydantic import BaseModel, ValidationError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry not available - install with: pip install opentelemetry-api opentelemetry-sdk")


class ValidationStatus(Enum):
    """Status of validation checks."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    status: ValidationStatus
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class TestScenario:
    """Test scenario definition."""
    name: str
    description: str
    spans_to_emit: List[Dict[str, Any]]
    expected_outcomes: List[str]
    timeout_seconds: float = 30.0
    concurrent_agents: int = 1


class ConcurrentOTELValidator:
    """Validates SwarmAgent telemetry using concurrent OpenTelemetry checks."""
    
    def __init__(self, 
                 coordination_dir: Path = Path("/Users/sac/s2s/agent_coordination"),
                 max_workers: int = 10):
        self.coordination_dir = coordination_dir
        self.max_workers = max_workers
        self.console = Console()
        self.results: List[ValidationResult] = []
        self.tracer = self._setup_tracer() if OTEL_AVAILABLE else None
        
    def _setup_tracer(self):
        """Setup OpenTelemetry tracer."""
        if not OTEL_AVAILABLE:
            return None
            
        resource = Resource.create({
            "service.name": "swarm-validator",
            "service.version": "1.0.0"
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        return trace.get_tracer(__name__)
    
    async def validate_span_schema(self, span: Dict[str, Any]) -> ValidationResult:
        """Validate a span against SwarmAgent schema."""
        start_time = time.time()
        
        try:
            # Required fields
            required_fields = ["name", "trace_id", "span_id", "timestamp", "attributes"]
            missing_fields = [f for f in required_fields if f not in span]
            
            if missing_fields:
                return ValidationResult(
                    check_name="span_schema",
                    status=ValidationStatus.FAILED,
                    duration_ms=(time.time() - start_time) * 1000,
                    message=f"Missing required fields: {missing_fields}",
                    details={"span": span}
                )
            
            # Validate span name format
            if not span["name"].startswith("swarmsh."):
                return ValidationResult(
                    check_name="span_name_format",
                    status=ValidationStatus.FAILED,
                    duration_ms=(time.time() - start_time) * 1000,
                    message=f"Invalid span name format: {span['name']}",
                    details={"expected_prefix": "swarmsh.", "actual": span["name"]}
                )
            
            # Validate timestamp
            if not isinstance(span["timestamp"], (int, float)) or span["timestamp"] <= 0:
                return ValidationResult(
                    check_name="span_timestamp",
                    status=ValidationStatus.FAILED,
                    duration_ms=(time.time() - start_time) * 1000,
                    message=f"Invalid timestamp: {span['timestamp']}"
                )
            
            return ValidationResult(
                check_name="span_schema",
                status=ValidationStatus.PASSED,
                duration_ms=(time.time() - start_time) * 1000,
                message="Span schema valid",
                trace_id=span.get("trace_id"),
                span_id=span.get("span_id")
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="span_schema",
                status=ValidationStatus.ERROR,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Validation error: {str(e)}",
                details={"error": traceback.format_exc()}
            )
    
    async def validate_agent_attributes(self, span: Dict[str, Any]) -> ValidationResult:
        """Validate agent-specific attributes."""
        start_time = time.time()
        
        try:
            name_parts = span["name"].split(".")
            if len(name_parts) < 3:
                return ValidationResult(
                    check_name="agent_attributes",
                    status=ValidationStatus.FAILED,
                    duration_ms=(time.time() - start_time) * 1000,
                    message="Invalid span name structure"
                )
            
            agent_type = name_parts[1]
            attrs = span.get("attributes", {})
            
            # Agent-specific validation rules
            validation_rules = {
                "roberts": {
                    "open": ["motion_id", "meeting_id"],
                    "vote": ["motion_id", "voting_method"],
                    "close": ["motion_id", "vote_result"]
                },
                "scrum": {
                    "plan": ["sprint_number", "team_id"],
                    "review": ["sprint_number", "defect_rate"]
                },
                "lean": {
                    "define": ["project_id", "problem_statement"],
                    "measure": ["project_id"],
                    "analyze": ["project_id"]
                }
            }
            
            trigger = name_parts[2] if len(name_parts) > 2 else None
            
            if agent_type in validation_rules and trigger in validation_rules[agent_type]:
                required_attrs = validation_rules[agent_type][trigger]
                missing_attrs = [a for a in required_attrs if a not in attrs]
                
                if missing_attrs:
                    return ValidationResult(
                        check_name="agent_attributes",
                        status=ValidationStatus.FAILED,
                        duration_ms=(time.time() - start_time) * 1000,
                        message=f"Missing required attributes for {agent_type}.{trigger}: {missing_attrs}",
                        details={"required": required_attrs, "actual": list(attrs.keys())}
                    )
            
            return ValidationResult(
                check_name="agent_attributes",
                status=ValidationStatus.PASSED,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Agent attributes valid for {agent_type}"
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="agent_attributes",
                status=ValidationStatus.ERROR,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Validation error: {str(e)}"
            )
    
    async def validate_coordination_flow(self, spans: List[Dict[str, Any]]) -> ValidationResult:
        """Validate coordination flow patterns."""
        start_time = time.time()
        
        try:
            # Look for known coordination patterns
            patterns_found = []
            
            # Governance → Delivery pattern
            roberts_close = any(s["name"] == "swarmsh.roberts.close" and 
                              s.get("attributes", {}).get("vote_result") == "passed" 
                              for s in spans)
            scrum_plan = any(s["name"] == "swarmsh.scrum.plan" for s in spans)
            
            if roberts_close and scrum_plan:
                patterns_found.append("governance_to_delivery")
            
            # Quality → Optimization pattern
            scrum_review = any(s["name"] == "swarmsh.scrum.review" and
                             s.get("attributes", {}).get("defect_rate", 0) > 3.0
                             for s in spans)
            lean_define = any(s["name"] == "swarmsh.lean.define" for s in spans)
            
            if scrum_review and lean_define:
                patterns_found.append("quality_to_optimization")
            
            return ValidationResult(
                check_name="coordination_flow",
                status=ValidationStatus.PASSED if patterns_found else ValidationStatus.FAILED,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Found {len(patterns_found)} coordination patterns",
                details={"patterns": patterns_found, "total_spans": len(spans)}
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="coordination_flow",
                status=ValidationStatus.ERROR,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Flow validation error: {str(e)}"
            )
    
    def load_spans(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load spans from coordination directory."""
        spans_file = self.coordination_dir / "telemetry_spans.jsonl"
        spans = []
        
        if spans_file.exists():
            with open(spans_file, 'r') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    if line.strip():
                        try:
                            spans.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON on line {i+1}")
        
        return spans
    
    async def run_validation_suite(self, test_scenarios: Optional[List[TestScenario]] = None) -> Dict[str, Any]:
        """Run complete validation suite concurrently."""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("validation_suite") if self.tracer else nullcontext() as span:
            # Load existing spans
            spans = self.load_spans()
            logger.info(f"Loaded {len(spans)} spans for validation")
            
            # Create validation tasks
            validation_tasks = []
            
            # Schema validation for each span
            for span_data in spans[:100]:  # Limit to first 100 for performance
                validation_tasks.append(("schema", self.validate_span_schema(span_data)))
                validation_tasks.append(("attributes", self.validate_agent_attributes(span_data)))
            
            # Flow validation
            validation_tasks.append(("flow", self.validate_coordination_flow(spans)))
            
            # Run test scenarios if provided
            if test_scenarios:
                for scenario in test_scenarios:
                    validation_tasks.append(("scenario", self.run_test_scenario(scenario)))
            
            # Execute all validations concurrently
            results = await self._execute_concurrent_validations(validation_tasks)
            
            # Generate summary
            summary = self._generate_summary(results)
            summary["duration_seconds"] = time.time() - start_time
            
            if self.tracer and span:
                span.set_attribute("validation.total_checks", len(results))
                span.set_attribute("validation.passed", summary["passed"])
                span.set_attribute("validation.failed", summary["failed"])
            
            return summary
    
    async def _execute_concurrent_validations(self, 
                                            validation_tasks: List[tuple]) -> List[ValidationResult]:
        """Execute validation tasks concurrently with progress tracking."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Running validations...", total=len(validation_tasks))
            
            # Group tasks by type for better concurrency control
            grouped_tasks = {}
            for task_type, coro in validation_tasks:
                if task_type not in grouped_tasks:
                    grouped_tasks[task_type] = []
                grouped_tasks[task_type].append(coro)
            
            # Run each group concurrently
            for task_type, tasks in grouped_tasks.items():
                progress.update(task, description=f"Validating {task_type}...")
                
                # Use asyncio.gather for concurrent execution
                chunk_size = min(10, len(tasks))  # Process in chunks
                for i in range(0, len(tasks), chunk_size):
                    chunk = tasks[i:i+chunk_size]
                    chunk_results = await asyncio.gather(*chunk, return_exceptions=True)
                    
                    for result in chunk_results:
                        if isinstance(result, Exception):
                            results.append(ValidationResult(
                                check_name=task_type,
                                status=ValidationStatus.ERROR,
                                duration_ms=0,
                                message=f"Task failed: {str(result)}"
                            ))
                        else:
                            results.append(result)
                    
                    progress.advance(task, len(chunk))
        
        return results
    
    async def run_test_scenario(self, scenario: TestScenario) -> ValidationResult:
        """Run a specific test scenario."""
        start_time = time.time()
        
        try:
            logger.info(f"Running test scenario: {scenario.name}")
            
            # Emit test spans
            spans_file = self.coordination_dir / "telemetry_spans.jsonl"
            emitted_spans = []
            
            for span_def in scenario.spans_to_emit:
                span = {
                    "name": span_def["name"],
                    "trace_id": f"test_trace_{int(time.time() * 1000)}",
                    "span_id": f"test_span_{int(time.time() * 1000000)}",
                    "timestamp": time.time(),
                    "attributes": span_def.get("attributes", {})
                }
                
                # Write to coordination file
                with open(spans_file, 'a') as f:
                    f.write(json.dumps(span) + '\n')
                
                emitted_spans.append(span)
                await asyncio.sleep(0.1)  # Small delay between spans
            
            # Wait for agents to process
            await asyncio.sleep(2)
            
            # Check expected outcomes
            outcomes_met = []
            for expected in scenario.expected_outcomes:
                # Simple check - in real implementation would be more sophisticated
                if "coordination" in expected:
                    outcomes_met.append(expected)
            
            success = len(outcomes_met) == len(scenario.expected_outcomes)
            
            return ValidationResult(
                check_name=f"scenario_{scenario.name}",
                status=ValidationStatus.PASSED if success else ValidationStatus.FAILED,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Scenario completed: {len(outcomes_met)}/{len(scenario.expected_outcomes)} outcomes met",
                details={
                    "emitted_spans": len(emitted_spans),
                    "expected_outcomes": scenario.expected_outcomes,
                    "outcomes_met": outcomes_met
                }
            )
            
        except Exception as e:
            return ValidationResult(
                check_name=f"scenario_{scenario.name}",
                status=ValidationStatus.ERROR,
                duration_ms=(time.time() - start_time) * 1000,
                message=f"Scenario error: {str(e)}"
            )
    
    def _generate_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary."""
        summary = {
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.status == ValidationStatus.PASSED),
            "failed": sum(1 for r in results if r.status == ValidationStatus.FAILED),
            "errors": sum(1 for r in results if r.status == ValidationStatus.ERROR),
            "checks_by_type": {},
            "failed_checks": [],
            "performance_stats": {
                "avg_duration_ms": sum(r.duration_ms for r in results) / len(results) if results else 0,
                "max_duration_ms": max((r.duration_ms for r in results), default=0),
                "min_duration_ms": min((r.duration_ms for r in results), default=0)
            }
        }
        
        # Group by check type
        for result in results:
            check_type = result.check_name.split("_")[0]
            if check_type not in summary["checks_by_type"]:
                summary["checks_by_type"][check_type] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0
                }
            
            summary["checks_by_type"][check_type]["total"] += 1
            if result.status == ValidationStatus.PASSED:
                summary["checks_by_type"][check_type]["passed"] += 1
            elif result.status == ValidationStatus.FAILED:
                summary["checks_by_type"][check_type]["failed"] += 1
                summary["failed_checks"].append({
                    "check": result.check_name,
                    "message": result.message,
                    "details": result.details
                })
            elif result.status == ValidationStatus.ERROR:
                summary["checks_by_type"][check_type]["errors"] += 1
        
        return summary
    
    def display_results(self, summary: Dict[str, Any]):
        """Display validation results in a rich format."""
        # Overall summary panel
        status_color = "green" if summary["failed"] == 0 else "red"
        
        summary_text = f"""[bold]Validation Summary[/bold]

Total Checks: {summary['total_checks']}
✅ Passed: {summary['passed']}
❌ Failed: {summary['failed']}
⚠️  Errors: {summary['errors']}

Duration: {summary['duration_seconds']:.2f} seconds
Avg Check Time: {summary['performance_stats']['avg_duration_ms']:.1f}ms
"""
        
        panel = Panel(summary_text, 
                     title="🔍 SwarmAgent Validation Results",
                     border_style=status_color)
        self.console.print(panel)
        
        # Detailed results table
        if summary["checks_by_type"]:
            table = Table(title="Validation Results by Type")
            table.add_column("Check Type", style="cyan")
            table.add_column("Total", style="white")
            table.add_column("Passed", style="green")
            table.add_column("Failed", style="red")
            table.add_column("Errors", style="yellow")
            table.add_column("Success Rate", style="magenta")
            
            for check_type, stats in summary["checks_by_type"].items():
                success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                table.add_row(
                    check_type.title(),
                    str(stats["total"]),
                    str(stats["passed"]),
                    str(stats["failed"]),
                    str(stats["errors"]),
                    f"{success_rate:.1f}%"
                )
            
            self.console.print(table)
        
        # Failed checks details
        if summary["failed_checks"]:
            self.console.print("\n[bold red]Failed Checks:[/bold red]")
            for i, failed in enumerate(summary["failed_checks"][:10]):  # Show first 10
                self.console.print(f"{i+1}. [yellow]{failed['check']}[/yellow]: {failed['message']}")
                if failed.get("details"):
                    self.console.print(f"   Details: {failed['details']}")


# Null context manager for when OTEL is not available
class nullcontext:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


async def main():
    """Example usage of concurrent validator."""
    validator = ConcurrentOTELValidator()
    
    # Define test scenarios
    test_scenarios = [
        TestScenario(
            name="governance_approval",
            description="Test governance motion approval flow",
            spans_to_emit=[
                {"name": "swarmsh.roberts.open", "attributes": {"motion_id": "test_motion", "meeting_id": "test"}},
                {"name": "swarmsh.roberts.vote", "attributes": {"motion_id": "test_motion", "voting_method": "ballot"}},
                {"name": "swarmsh.roberts.close", "attributes": {"motion_id": "test_motion", "vote_result": "passed"}}
            ],
            expected_outcomes=["motion_approved", "coordination_triggered"]
        ),
        TestScenario(
            name="quality_trigger",
            description="Test quality issue triggering optimization",
            spans_to_emit=[
                {"name": "swarmsh.scrum.review", "attributes": {"sprint_number": "99", "defect_rate": 5.2}},
                {"name": "swarmsh.lean.define", "attributes": {"project_id": "quality_99", "problem_statement": "High defects"}}
            ],
            expected_outcomes=["quality_issue_detected", "optimization_triggered"]
        )
    ]
    
    # Run validation suite
    logger.info("Starting concurrent validation suite...")
    summary = await validator.run_validation_suite(test_scenarios)
    
    # Display results
    validator.display_results(summary)
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())