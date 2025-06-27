"""SwarmAgent Validation Loop - Continuous telemetry monitoring and auto-remediation.

Real-time validation loop that:
1. Monitors telemetry spans continuously
2. Validates using Weaver semantic conventions  
3. Auto-remediates validation failures
4. Provides real-time metrics and alerts
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Callable
import traceback
from enum import Enum

from loguru import logger
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.layout import Layout

# Import Weaver validation components
try:
    from .weaver_otel_validator import WeaverOTELValidator, ValidationStatus, WeaverValidationResult
    from ..core.weaver_engine import WeaverEngine
    WEAVER_AVAILABLE = True
except ImportError:
    WEAVER_AVAILABLE = False
    logger.warning("Weaver validation not available")

# Import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry not available")


class LoopStatus(Enum):
    """Validation loop status."""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class RemediationAction(Enum):
    """Auto-remediation actions."""
    NORMALIZE_FORMAT = "normalize_format"
    ADD_MISSING_ATTRIBUTES = "add_missing_attributes"
    FIX_TIMESTAMP = "fix_timestamp"
    RETRY_VALIDATION = "retry_validation"
    ALERT_ADMIN = "alert_admin"
    QUARANTINE_SPAN = "quarantine_span"


@dataclass
class ValidationMetrics:
    """Real-time validation metrics."""
    total_spans_processed: int = 0
    total_validations: int = 0
    passed_validations: int = 0
    failed_validations: int = 0
    error_validations: int = 0
    auto_remediations: int = 0
    successful_remediations: int = 0
    
    # Performance metrics
    avg_validation_time_ms: float = 0.0
    current_throughput: float = 0.0
    peak_throughput: float = 0.0
    
    # Time tracking
    loop_start_time: float = field(default_factory=time.time)
    last_span_time: Optional[float] = None
    uptime_seconds: float = 0.0
    
    def update_performance(self, validation_time_ms: float):
        """Update performance metrics."""
        self.avg_validation_time_ms = (
            (self.avg_validation_time_ms * self.total_validations + validation_time_ms) 
            / (self.total_validations + 1)
        )
        
        # Calculate current throughput (validations per second)
        current_time = time.time()
        if self.last_span_time:
            time_diff = current_time - self.last_span_time
            if time_diff > 0:
                self.current_throughput = 1.0 / time_diff
                if self.current_throughput > self.peak_throughput:
                    self.peak_throughput = self.current_throughput
        
        self.last_span_time = current_time
        self.uptime_seconds = current_time - self.loop_start_time


@dataclass 
class RemediationResult:
    """Result of auto-remediation attempt."""
    action: RemediationAction
    success: bool
    original_span: Dict[str, Any]
    remediated_span: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0


class SwarmValidationLoop:
    """Continuous SwarmAgent validation loop with auto-remediation."""
    
    def __init__(self,
                 coordination_dir: Path = Path("/Users/sac/s2s/agent_coordination"),
                 convention_name: str = "swarm_agent",
                 validation_interval: float = 1.0,
                 max_remediation_attempts: int = 3,
                 enable_auto_remediation: bool = True):
        self.coordination_dir = coordination_dir
        self.convention_name = convention_name
        self.validation_interval = validation_interval
        self.max_remediation_attempts = max_remediation_attempts
        self.enable_auto_remediation = enable_auto_remediation
        
        # Components
        self.console = Console()
        self.validator = WeaverOTELValidator(
            coordination_dir=coordination_dir,
            convention_name=convention_name,
            max_workers=20
        ) if WEAVER_AVAILABLE else None
        
        # State management
        self.status = LoopStatus.STOPPED
        self.metrics = ValidationMetrics()
        self.processed_spans: Set[str] = set()  # Track span IDs to avoid duplicates
        self.remediation_cache: Dict[str, List[RemediationResult]] = {}
        self.alert_handlers: List[Callable] = []
        
        # OpenTelemetry setup
        self.tracer = self._setup_tracer() if OTEL_AVAILABLE else None
        
        # Live display components
        self.layout = self._create_layout()
        self.live_display = None
        
    def _setup_tracer(self):
        """Setup OpenTelemetry tracer for loop telemetry."""
        if not OTEL_AVAILABLE:
            return None
            
        resource = Resource.create({
            "service.name": "swarm-validation-loop",
            "service.version": "1.0.0",
            "loop.convention": self.convention_name
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        return trace.get_tracer(__name__)
    
    def _create_layout(self) -> Layout:
        """Create rich layout for live display."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=5)
        )
        
        layout["main"].split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="activity", ratio=2)
        )
        
        return layout
    
    def add_alert_handler(self, handler: Callable[[str, Dict[str, Any]], None]):
        """Add custom alert handler for validation failures."""
        self.alert_handlers.append(handler)
    
    def _trigger_alerts(self, message: str, context: Dict[str, Any]):
        """Trigger all configured alert handlers."""
        for handler in self.alert_handlers:
            try:
                handler(message, context)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    async def _load_new_spans(self) -> List[Dict[str, Any]]:
        """Load new spans since last check."""
        spans_file = self.coordination_dir / "telemetry_spans.jsonl"
        new_spans = []
        
        if not spans_file.exists():
            return new_spans
        
        try:
            with open(spans_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        span = json.loads(line)
                        
                        # Create unique span identifier
                        span_id = f"{span.get('trace_id', f'line_{line_num}')}_{span.get('span_id', line_num)}"
                        
                        # Skip if already processed
                        if span_id in self.processed_spans:
                            continue
                        
                        # Normalize legacy format
                        if "ts" in span and "attrs" in span:
                            normalized_span = {
                                "name": span["name"],
                                "trace_id": f"legacy_{line_num}",
                                "span_id": f"legacy_span_{line_num}",
                                "timestamp": time.time(),
                                "attributes": span["attrs"]
                            }
                            new_spans.append(normalized_span)
                        else:
                            new_spans.append(span)
                        
                        self.processed_spans.add(span_id)
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error loading spans: {e}")
        
        return new_spans
    
    async def _validate_span(self, span: Dict[str, Any]) -> WeaverValidationResult:
        """Validate a single span using Weaver validator."""
        if not self.validator:
            return WeaverValidationResult(
                check_name="no_validator",
                status=ValidationStatus.ERROR,
                duration_ms=0,
                message="Weaver validator not available"
            )
        
        with self.tracer.start_as_current_span("validate_loop_span") if self.tracer else nullcontext():
            return await self.validator.validate_span_weaver(span)
    
    async def _auto_remediate(self, span: Dict[str, Any], validation_result: WeaverValidationResult) -> Optional[RemediationResult]:
        """Attempt to auto-remediate validation failure."""
        if not self.enable_auto_remediation:
            return None
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span("auto_remediate") if self.tracer else nullcontext():
            # Determine remediation action based on validation failure
            action = self._determine_remediation_action(validation_result)
            
            try:
                remediated_span = await self._apply_remediation(span, action)
                
                if remediated_span:
                    # Re-validate remediated span
                    re_validation = await self._validate_span(remediated_span)
                    success = re_validation.status == ValidationStatus.PASSED
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    return RemediationResult(
                        action=action,
                        success=success,
                        original_span=span,
                        remediated_span=remediated_span,
                        duration_ms=duration_ms
                    )
                else:
                    return RemediationResult(
                        action=action,
                        success=False,
                        original_span=span,
                        error_message="Failed to apply remediation",
                        duration_ms=(time.time() - start_time) * 1000
                    )
                    
            except Exception as e:
                return RemediationResult(
                    action=action,
                    success=False,
                    original_span=span,
                    error_message=str(e),
                    duration_ms=(time.time() - start_time) * 1000
                )
    
    def _determine_remediation_action(self, validation_result: WeaverValidationResult) -> RemediationAction:
        """Determine appropriate remediation action based on validation failure."""
        message = validation_result.message.lower()
        
        if "missing required fields" in message and "timestamp" in message:
            return RemediationAction.FIX_TIMESTAMP
        elif "missing required attributes" in message:
            return RemediationAction.ADD_MISSING_ATTRIBUTES
        elif "invalid timestamp" in message:
            return RemediationAction.FIX_TIMESTAMP
        elif "invalid span name format" in message:
            return RemediationAction.NORMALIZE_FORMAT
        else:
            return RemediationAction.RETRY_VALIDATION
    
    async def _apply_remediation(self, span: Dict[str, Any], action: RemediationAction) -> Optional[Dict[str, Any]]:
        """Apply specific remediation action to span."""
        remediated_span = span.copy()
        
        if action == RemediationAction.FIX_TIMESTAMP:
            if "timestamp" not in remediated_span or not isinstance(remediated_span["timestamp"], (int, float)):
                remediated_span["timestamp"] = time.time()
            
        elif action == RemediationAction.ADD_MISSING_ATTRIBUTES:
            # Extract agent and trigger from span name
            name_parts = remediated_span.get("name", "").split(".")
            if len(name_parts) >= 3:
                agent_type = name_parts[1]
                trigger = name_parts[2]
                
                if "attributes" not in remediated_span:
                    remediated_span["attributes"] = {}
                
                attrs = remediated_span["attributes"]
                if "swarm.agent" not in attrs:
                    attrs["swarm.agent"] = agent_type
                if "swarm.trigger" not in attrs:
                    attrs["swarm.trigger"] = trigger
        
        elif action == RemediationAction.NORMALIZE_FORMAT:
            # Already handled during span loading
            pass
        
        elif action == RemediationAction.RETRY_VALIDATION:
            # No changes needed, just retry
            pass
        
        return remediated_span
    
    def _generate_metrics_panel(self) -> Panel:
        """Generate real-time metrics panel."""
        self.metrics.uptime_seconds = time.time() - self.metrics.loop_start_time
        
        success_rate = (
            (self.metrics.passed_validations / self.metrics.total_validations * 100) 
            if self.metrics.total_validations > 0 else 0
        )
        
        remediation_rate = (
            (self.metrics.successful_remediations / self.metrics.auto_remediations * 100)
            if self.metrics.auto_remediations > 0 else 0
        )
        
        metrics_text = f"""📊 Validation Metrics
        
Total Spans: {self.metrics.total_spans_processed}
Validations: {self.metrics.total_validations}
✅ Passed: {self.metrics.passed_validations}
❌ Failed: {self.metrics.failed_validations}
⚠️  Errors: {self.metrics.error_validations}

🔧 Auto-Remediation:
Total Attempts: {self.metrics.auto_remediations}
Successful: {self.metrics.successful_remediations}
Success Rate: {remediation_rate:.1f}%

⚡ Performance:
Success Rate: {success_rate:.1f}%
Avg Validation: {self.metrics.avg_validation_time_ms:.1f}ms
Current Throughput: {self.metrics.current_throughput:.1f}/s
Peak Throughput: {self.metrics.peak_throughput:.1f}/s
Uptime: {self.metrics.uptime_seconds:.0f}s"""
        
        return Panel(
            metrics_text,
            title=f"🔄 SwarmAgent Validation Loop [{self.status.value.upper()}]",
            border_style="green" if self.status == LoopStatus.RUNNING else "yellow"
        )
    
    def _generate_activity_panel(self) -> Panel:
        """Generate recent activity panel."""
        activity_text = f"""🔍 Recent Activity

Convention: {self.convention_name}
Monitoring: {self.coordination_dir}
Interval: {self.validation_interval}s
Auto-Remediation: {'✅ Enabled' if self.enable_auto_remediation else '❌ Disabled'}

📂 Processed Spans: {len(self.processed_spans)}
🏥 Remediation Cache: {len(self.remediation_cache)} entries

⏰ Last Check: {datetime.now().strftime('%H:%M:%S')}
🎯 Next Check: {(datetime.now() + timedelta(seconds=self.validation_interval)).strftime('%H:%M:%S')}"""
        
        return Panel(
            activity_text,
            title="📈 Loop Activity",
            border_style="blue"
        )
    
    def _update_display(self):
        """Update live display with current metrics."""
        if not self.live_display:
            return
        
        self.layout["header"].update(Panel(
            f"🔄 SwarmAgent Validation Loop - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            style="bold blue"
        ))
        
        self.layout["metrics"].update(self._generate_metrics_panel())
        self.layout["activity"].update(self._generate_activity_panel())
        
        # Footer with controls
        footer_text = "Press Ctrl+C to stop | 'p' to pause/resume | 'r' to reset metrics"
        self.layout["footer"].update(Panel(footer_text, style="dim"))
    
    async def _validation_cycle(self):
        """Single validation cycle."""
        with self.tracer.start_as_current_span("validation_cycle") if self.tracer else nullcontext():
            # Load new spans
            new_spans = await self._load_new_spans()
            
            if not new_spans:
                return
            
            logger.info(f"🔍 Processing {len(new_spans)} new spans")
            
            for span in new_spans:
                self.metrics.total_spans_processed += 1
                
                # Validate span
                start_time = time.time()
                validation_result = await self._validate_span(span)
                validation_time_ms = (time.time() - start_time) * 1000
                
                # Update metrics
                self.metrics.total_validations += 1
                self.metrics.update_performance(validation_time_ms)
                
                if validation_result.status == ValidationStatus.PASSED:
                    self.metrics.passed_validations += 1
                elif validation_result.status == ValidationStatus.FAILED:
                    self.metrics.failed_validations += 1
                    
                    # Attempt auto-remediation for failed validations
                    if self.enable_auto_remediation:
                        remediation_result = await self._auto_remediate(span, validation_result)
                        
                        if remediation_result:
                            self.metrics.auto_remediations += 1
                            
                            if remediation_result.success:
                                self.metrics.successful_remediations += 1
                                logger.info(f"✅ Auto-remediated span with {remediation_result.action.value}")
                            else:
                                logger.warning(f"❌ Remediation failed: {remediation_result.error_message}")
                                
                                # Trigger alerts for failed remediation
                                self._trigger_alerts(
                                    f"Auto-remediation failed for span: {span.get('name', 'unknown')}",
                                    {
                                        "span": span,
                                        "validation_result": validation_result.__dict__,
                                        "remediation_result": remediation_result.__dict__
                                    }
                                )
                else:
                    self.metrics.error_validations += 1
                    
                    # Trigger alerts for validation errors
                    self._trigger_alerts(
                        f"Validation error for span: {span.get('name', 'unknown')}",
                        {
                            "span": span,
                            "validation_result": validation_result.__dict__
                        }
                    )
    
    async def start_loop(self, display_live: bool = True):
        """Start the validation loop."""
        if self.status == LoopStatus.RUNNING:
            logger.warning("Validation loop is already running")
            return
        
        logger.info(f"🚀 Starting SwarmAgent validation loop")
        logger.info(f"   Convention: {self.convention_name}")
        logger.info(f"   Monitoring: {self.coordination_dir}")
        logger.info(f"   Interval: {self.validation_interval}s")
        logger.info(f"   Auto-remediation: {self.enable_auto_remediation}")
        
        self.status = LoopStatus.STARTING
        
        # Setup live display
        if display_live:
            self.live_display = Live(
                self.layout, 
                console=self.console, 
                refresh_per_second=2,
                screen=True
            )
            self.live_display.start()
        
        try:
            self.status = LoopStatus.RUNNING
            
            while self.status == LoopStatus.RUNNING:
                try:
                    # Run validation cycle
                    await self._validation_cycle()
                    
                    # Update display
                    if display_live:
                        self._update_display()
                    
                    # Wait for next cycle
                    await asyncio.sleep(self.validation_interval)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Stopping validation loop (Ctrl+C)")
                    break
                except Exception as e:
                    logger.error(f"❌ Validation cycle error: {e}")
                    logger.error(traceback.format_exc())
                    self.status = LoopStatus.ERROR
                    break
        
        finally:
            self.status = LoopStatus.STOPPED
            if display_live and self.live_display:
                self.live_display.stop()
            
            logger.info(f"🏁 Validation loop stopped")
            logger.info(f"   Total spans processed: {self.metrics.total_spans_processed}")
            logger.info(f"   Total validations: {self.metrics.total_validations}")
            logger.info(f"   Success rate: {(self.metrics.passed_validations / self.metrics.total_validations * 100) if self.metrics.total_validations > 0 else 0:.1f}%")
            logger.info(f"   Auto-remediations: {self.metrics.auto_remediations}")
    
    def stop_loop(self):
        """Stop the validation loop."""
        if self.status == LoopStatus.RUNNING:
            self.status = LoopStatus.STOPPING
            logger.info("🛑 Stopping validation loop...")
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return {
            "status": self.status.value,
            "metrics": {
                "total_spans_processed": self.metrics.total_spans_processed,
                "total_validations": self.metrics.total_validations,
                "passed_validations": self.metrics.passed_validations,
                "failed_validations": self.metrics.failed_validations,
                "error_validations": self.metrics.error_validations,
                "auto_remediations": self.metrics.auto_remediations,
                "successful_remediations": self.metrics.successful_remediations,
                "success_rate_percent": (
                    (self.metrics.passed_validations / self.metrics.total_validations * 100) 
                    if self.metrics.total_validations > 0 else 0
                ),
                "remediation_rate_percent": (
                    (self.metrics.successful_remediations / self.metrics.auto_remediations * 100)
                    if self.metrics.auto_remediations > 0 else 0
                ),
                "avg_validation_time_ms": self.metrics.avg_validation_time_ms,
                "current_throughput": self.metrics.current_throughput,
                "peak_throughput": self.metrics.peak_throughput,
                "uptime_seconds": time.time() - self.metrics.loop_start_time
            },
            "configuration": {
                "convention_name": self.convention_name,
                "coordination_dir": str(self.coordination_dir),
                "validation_interval": self.validation_interval,
                "enable_auto_remediation": self.enable_auto_remediation,
                "max_remediation_attempts": self.max_remediation_attempts
            }
        }


# Null context manager for when tracer is None
class nullcontext:
    def __enter__(self):
        return self
    def __exit__(self, *excinfo):
        pass


# Example alert handlers
def slack_alert_handler(message: str, context: Dict[str, Any]):
    """Example Slack alert handler."""
    logger.info(f"📢 SLACK ALERT: {message}")
    # In real implementation, send to Slack webhook

def email_alert_handler(message: str, context: Dict[str, Any]):
    """Example email alert handler.""" 
    logger.info(f"📧 EMAIL ALERT: {message}")
    # In real implementation, send email

def pagerduty_alert_handler(message: str, context: Dict[str, Any]):
    """Example PagerDuty alert handler."""
    logger.info(f"🚨 PAGERDUTY ALERT: {message}")
    # In real implementation, trigger PagerDuty incident