"""Weaver-first concurrent OpenTelemetry validation for SwarmAgent.

80/20 refactor: Use Weaver-generated schemas instead of hardcoded validation rules.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import traceback

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry not available")

# Import Weaver core for semantic conventions
try:
    from ..core.weaver_engine import WeaverEngine
    WEAVER_AVAILABLE = True
except ImportError:
    WEAVER_AVAILABLE = False
    logger.warning("WeaverEngine not available")


class ValidationStatus(Enum):
    """Status of validation checks."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class WeaverValidationResult:
    """Result of a Weaver-based validation check."""
    check_name: str
    status: ValidationStatus
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    weaver_convention: Optional[str] = None
    span_type: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class WeaverOTELValidator:
    """Weaver-first validator using generated semantic conventions."""
    
    def __init__(self, 
                 coordination_dir: Path = Path("/Users/sac/s2s/agent_coordination"),
                 convention_name: str = "swarm_agent",
                 max_workers: int = 20):
        self.coordination_dir = coordination_dir
        self.convention_name = convention_name
        self.max_workers = max_workers
        self.console = Console()
        self.results: List[WeaverValidationResult] = []
        
        # Initialize Weaver engine for semantic conventions
        self.weaver_engine = WeaverEngine() if WEAVER_AVAILABLE else None
        self.semantic_convention = self._load_semantic_convention()
        self.tracer = self._setup_tracer() if OTEL_AVAILABLE else None
        
        # Cache validation rules from Weaver
        self.validation_cache = self._build_validation_cache()
        
    def _setup_tracer(self):
        """Setup OpenTelemetry tracer for validation telemetry."""
        if not OTEL_AVAILABLE:
            return None
            
        resource = Resource.create({
            "service.name": "weaver-swarm-validator",
            "service.version": "2.0.0",
            "weaver.convention": self.convention_name
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        return trace.get_tracer(__name__)
    
    def _load_semantic_convention(self) -> Optional[Dict[str, Any]]:
        """Load semantic convention from Weaver engine."""
        if not self.weaver_engine:
            logger.warning("WeaverEngine not available - falling back to basic validation")
            return None
            
        try:
            convention = self.weaver_engine.load_semantic_convention(self.convention_name)
            logger.info(f"🔧 Loaded Weaver convention: {self.convention_name}")
            return convention
        except Exception as e:
            logger.error(f"Failed to load convention {self.convention_name}: {e}")
            return None
    
    def _build_validation_cache(self) -> Dict[str, Dict[str, Any]]:
        """Build validation rules cache from Weaver semantic conventions."""
        cache = {}
        
        if not self.semantic_convention:
            # Fallback to basic rules
            logger.warning("Using fallback validation rules - Weaver convention not loaded")
            return self._get_fallback_rules()
        
        # Parse semantic convention spans and attributes
        spans = self.semantic_convention.get("spans", [])
        groups = self.semantic_convention.get("groups", [])
        
        # Build attribute group lookup
        attribute_groups = {}
        for group in groups:
            group_id = group.get("id", "")
            attributes = group.get("attributes", [])
            attribute_groups[group_id] = {
                attr.get("id"): {
                    "type": attr.get("type", "string"),
                    "requirement_level": attr.get("requirement_level", "optional"),
                    "brief": attr.get("brief", "")
                }
                for attr in attributes
            }
        
        # Build span validation rules
        for span in spans:
            span_name = span.get("span_name", "")
            attributes = span.get("attributes", [])
            
            # Collect required attributes from referenced groups
            required_attrs = []
            optional_attrs = []
            
            for attr_ref in attributes:
                if "ref" in attr_ref:
                    group_id = attr_ref["ref"]
                    if group_id in attribute_groups:
                        for attr_id, attr_info in attribute_groups[group_id].items():
                            if attr_info["requirement_level"] == "required":
                                required_attrs.append(attr_id)
                            else:
                                optional_attrs.append(attr_id)
            
            cache[span_name] = {
                "required_attributes": required_attrs,
                "optional_attributes": optional_attrs,
                "events": span.get("events", []),
                "brief": span.get("brief", "")
            }
        
        logger.info(f"🏗️  Built validation cache for {len(cache)} span types")
        return cache
    
    def _get_fallback_rules(self) -> Dict[str, Dict[str, Any]]:
        """Fallback validation rules when Weaver is not available."""
        return {
            "swarmsh.roberts.open": {
                "required_attributes": ["motion_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["meeting_id"],
                "events": ["motion_opened"]
            },
            "swarmsh.roberts.vote": {
                "required_attributes": ["motion_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["voting_method"],
                "events": ["voting_started"]
            },
            "swarmsh.roberts.close": {
                "required_attributes": ["motion_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["vote_result", "votes_yes", "votes_no"],
                "events": ["motion_resolved"]
            },
            "swarmsh.scrum.plan": {
                "required_attributes": ["sprint_number", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["team_id", "capacity"],
                "events": ["sprint_planned"]
            },
            "swarmsh.scrum.review": {
                "required_attributes": ["sprint_number", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["velocity", "defect_rate"],
                "events": ["metrics_collected"]
            },
            "swarmsh.lean.define": {
                "required_attributes": ["project_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": ["problem_statement"],
                "events": ["problem_identified"]
            },
            "swarmsh.lean.measure": {
                "required_attributes": ["project_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": [],
                "events": ["baseline_established"]
            },
            "swarmsh.lean.analyze": {
                "required_attributes": ["project_id", "swarm.agent", "swarm.trigger"],
                "optional_attributes": [],
                "events": ["root_cause_identified"]
            }
        }
    
    async def validate_span_weaver(self, span: Dict[str, Any]) -> WeaverValidationResult:
        """Validate span using Weaver-generated semantic conventions."""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("validate_span") if self.tracer else nullcontext():
            try:
                # Basic schema validation
                required_fields = ["name", "trace_id", "span_id", "timestamp", "attributes"]
                missing_fields = [f for f in required_fields if f not in span]
                
                if missing_fields:
                    return WeaverValidationResult(
                        check_name="weaver_span_schema",
                        status=ValidationStatus.FAILED,
                        duration_ms=(time.time() - start_time) * 1000,
                        message=f"Missing required fields: {missing_fields}",
                        details={"span": span, "missing_fields": missing_fields},
                        weaver_convention=self.convention_name,
                        span_type=span.get("name")
                    )
                
                span_name = span["name"]
                
                # Check if span type is in our Weaver-generated rules
                if span_name not in self.validation_cache:
                    # Allow unknown spans with warning
                    return WeaverValidationResult(
                        check_name="weaver_span_type",
                        status=ValidationStatus.PASSED,
                        duration_ms=(time.time() - start_time) * 1000,
                        message=f"Unknown span type (allowed): {span_name}",
                        details={"known_types": list(self.validation_cache.keys())},
                        weaver_convention=self.convention_name,
                        span_type=span_name
                    )
                
                # Validate using Weaver rules
                rules = self.validation_cache[span_name]
                attrs = span.get("attributes", {})
                
                # Check required attributes
                required_attrs = rules.get("required_attributes", [])
                missing_required = [attr for attr in required_attrs if attr not in attrs]
                
                if missing_required:
                    return WeaverValidationResult(
                        check_name="weaver_required_attributes",
                        status=ValidationStatus.FAILED,
                        duration_ms=(time.time() - start_time) * 1000,
                        message=f"Missing required attributes: {missing_required}",
                        details={
                            "span_name": span_name,
                            "missing_attributes": missing_required,
                            "required_attributes": required_attrs,
                            "present_attributes": list(attrs.keys())
                        },
                        weaver_convention=self.convention_name,
                        span_type=span_name
                    )
                
                # Validate timestamp
                if not isinstance(span["timestamp"], (int, float)) or span["timestamp"] <= 0:
                    return WeaverValidationResult(
                        check_name="weaver_timestamp",
                        status=ValidationStatus.FAILED,
                        duration_ms=(time.time() - start_time) * 1000,
                        message=f"Invalid timestamp: {span['timestamp']}",
                        weaver_convention=self.convention_name,
                        span_type=span_name
                    )
                
                return WeaverValidationResult(
                    check_name="weaver_span_validation",
                    status=ValidationStatus.PASSED,
                    duration_ms=(time.time() - start_time) * 1000,
                    message=f"Span valid per Weaver convention",
                    details={
                        "span_name": span_name,
                        "validated_attributes": len(attrs),
                        "convention_rules": rules
                    },
                    weaver_convention=self.convention_name,
                    span_type=span_name,
                    trace_id=span.get("trace_id"),
                    span_id=span.get("span_id")
                )
                
            except Exception as e:
                return WeaverValidationResult(
                    check_name="weaver_validation_error",
                    status=ValidationStatus.ERROR,
                    duration_ms=(time.time() - start_time) * 1000,
                    message=f"Validation error: {str(e)}",
                    details={"error": traceback.format_exc()},
                    weaver_convention=self.convention_name
                )
    
    def load_spans(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load telemetry spans from coordination directory."""
        spans_file = self.coordination_dir / "telemetry_spans.jsonl"
        spans = []
        
        if not spans_file.exists():
            logger.warning(f"Spans file not found: {spans_file}")
            return spans
        
        try:
            with open(spans_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if limit and len(spans) >= limit:
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        span = json.loads(line)
                        
                        # Normalize legacy format to new format
                        if "ts" in span and "attrs" in span:
                            # Convert old format: ts,attrs -> timestamp,attributes
                            normalized_span = {
                                "name": span["name"],
                                "trace_id": f"legacy_{line_num}",
                                "span_id": f"legacy_span_{line_num}",
                                "timestamp": time.time(),  # Use current time for legacy
                                "attributes": span["attrs"]
                            }
                            spans.append(normalized_span)
                        else:
                            spans.append(span)
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error loading spans: {e}")
            
        logger.info(f"📊 Loaded {len(spans)} spans for Weaver validation")
        return spans
    
    async def run_concurrent_validation(self, spans: List[Dict[str, Any]]) -> List[WeaverValidationResult]:
        """Run Weaver validation concurrently on all spans."""
        if not spans:
            return []
        
        with self.tracer.start_as_current_span("concurrent_validation_suite") if self.tracer else nullcontext():
            start_time = time.time()
            
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def validate_with_semaphore(span):
                async with semaphore:
                    return await self.validate_span_weaver(span)
            
            # Run all validations concurrently
            tasks = [validate_with_semaphore(span) for span in spans]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Validation exception for span {i}: {result}")
                    valid_results.append(WeaverValidationResult(
                        check_name="weaver_exception",
                        status=ValidationStatus.ERROR,
                        duration_ms=0,
                        message=str(result),
                        weaver_convention=self.convention_name
                    ))
                else:
                    valid_results.append(result)
            
            total_time = time.time() - start_time
            logger.info(f"🚀 Weaver validation completed: {len(valid_results)} spans in {total_time:.2f}s")
            
            return valid_results
    
    def display_weaver_results(self, results: List[WeaverValidationResult]):
        """Display Weaver validation results with rich formatting."""
        if not results:
            self.console.print("[yellow]No validation results to display[/yellow]")
            return
        
        # Calculate summary statistics
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        errors = sum(1 for r in results if r.status == ValidationStatus.ERROR)
        total = len(results)
        
        # Performance stats
        durations = [r.duration_ms for r in results if r.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Summary panel
        summary = f"""Total Validations: {total}
✅ Passed: {passed}
❌ Failed: {failed}
⚠️  Errors: {errors}

Performance (Weaver-powered):
Avg Duration: {avg_duration:.1f}ms
Max Duration: {max_duration:.1f}ms
Min Duration: {min_duration:.1f}ms

Convention: {self.convention_name}
Validation Rules: {len(self.validation_cache)} span types"""
        
        panel = Panel(
            summary,
            title=f"🔧 Weaver Validation Results",
            border_style="green" if failed == 0 else "red"
        )
        self.console.print(panel)
        
        # Detailed results by span type
        span_type_stats = {}
        for result in results:
            span_type = result.span_type or "unknown"
            if span_type not in span_type_stats:
                span_type_stats[span_type] = {"passed": 0, "failed": 0, "errors": 0}
            
            if result.status == ValidationStatus.PASSED:
                span_type_stats[span_type]["passed"] += 1
            elif result.status == ValidationStatus.FAILED:
                span_type_stats[span_type]["failed"] += 1
            else:
                span_type_stats[span_type]["errors"] += 1
        
        # Results table
        table = Table(title="Validation Results by Span Type")
        table.add_column("Span Type", style="cyan")
        table.add_column("Passed", style="green")
        table.add_column("Failed", style="red")
        table.add_column("Errors", style="yellow")
        table.add_column("Success Rate", style="blue")
        
        for span_type, stats in span_type_stats.items():
            total_type = stats["passed"] + stats["failed"] + stats["errors"]
            success_rate = (stats["passed"] / total_type * 100) if total_type > 0 else 0
            
            table.add_row(
                span_type,
                str(stats["passed"]),
                str(stats["failed"]),
                str(stats["errors"]),
                f"{success_rate:.1f}%"
            )
        
        self.console.print(table)
        
        # Show failed validations
        failed_results = [r for r in results if r.status == ValidationStatus.FAILED]
        if failed_results:
            self.console.print(f"\n[red]Failed Validations ({len(failed_results)}):[/red]")
            for result in failed_results[:10]:  # Show first 10
                self.console.print(f"  • {result.check_name}: {result.message}")
    
    async def run_weaver_validation_suite(self) -> Dict[str, Any]:
        """Run complete Weaver-based validation suite."""
        with self.tracer.start_as_current_span("weaver_validation_suite") if self.tracer else nullcontext():
            logger.info(f"🔧 Starting Weaver validation suite with convention: {self.convention_name}")
            
            # Load spans
            spans = self.load_spans()
            if not spans:
                return {
                    "total_validations": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "weaver_convention": self.convention_name,
                    "message": "No spans found"
                }
            
            # Run concurrent validation
            start_time = time.time()
            results = await self.run_concurrent_validation(spans)
            total_time = time.time() - start_time
            
            # Calculate summary
            passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
            failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
            errors = sum(1 for r in results if r.status == ValidationStatus.ERROR)
            
            # Performance metrics
            durations = [r.duration_ms for r in results if r.duration_ms > 0]
            throughput = len(results) / total_time if total_time > 0 else 0
            
            summary = {
                "total_validations": len(results),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration_seconds": total_time,
                "throughput_per_second": throughput,
                "weaver_convention": self.convention_name,
                "validation_rules": len(self.validation_cache),
                "performance_stats": {
                    "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                    "max_duration_ms": max(durations) if durations else 0,
                    "min_duration_ms": min(durations) if durations else 0
                },
                "failed_validations": [
                    {
                        "check": r.check_name,
                        "message": r.message,
                        "span_type": r.span_type
                    }
                    for r in results if r.status == ValidationStatus.FAILED
                ]
            }
            
            # Display results
            self.display_weaver_results(results)
            
            return summary


# Null context manager for when tracer is None
class nullcontext:
    def __enter__(self):
        return self
    def __exit__(self, *excinfo):
        pass