"""
OTEL Feedback Loop Integration
==============================

Connects OTEL monitoring with task coordination, git operations,
validation systems, and DSPy analysis to create closed feedback loops
for autonomous system improvement.
"""

import json
import datetime
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from .span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from .task_utils import create_task, get_coordinator
except ImportError:
    def create_task(agent: str, args: List[Any], priority: int = 50) -> str:
        print(f"[FEEDBACK] Would create task: {agent} with args {args}")
        return f"mock_task_{datetime.datetime.now().timestamp()}"
    
    def get_coordinator():
        return None

try:
    from .log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

@dataclass
class FeedbackEvent:
    """Represents a feedback event in the system."""
    timestamp: str
    source: str  # otel_monitor, validation, git_operation, dspy_analysis
    event_type: str  # gap_detected, validation_failed, git_error, analysis_complete
    data: Dict[str, Any]
    severity: str = "info"  # info, warning, error, critical
    action_taken: Optional[str] = None
    task_created: Optional[str] = None

class FeedbackProcessor:
    """Processes feedback events and takes corrective actions."""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_history: List[FeedbackEvent] = []
        self.auto_remediation = True
        self._lock = threading.Lock()
    
    def register_handler(self, event_type: str, handler: Callable[[FeedbackEvent], None]):
        """Register a handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    @span("feedback_process_event")
    def process_event(self, event: FeedbackEvent) -> Optional[str]:
        """Process a feedback event and potentially take action."""
        with self._lock:
            self.event_history.append(event)
            
            # Call registered handlers
            handlers = self.event_handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Feedback handler failed: {e}")
            
            # Auto-remediation logic
            if self.auto_remediation:
                action = self._auto_remediate(event)
                if action:
                    event.action_taken = action
                    return action
        
        return None
    
    def _auto_remediate(self, event: FeedbackEvent) -> Optional[str]:
        """Attempt automatic remediation based on event type."""
        if event.event_type == "otel_gap_detected":
            return self._remediate_otel_gap(event)
        elif event.event_type == "validation_failed":
            return self._remediate_validation_failure(event)
        elif event.event_type == "git_operation_failed":
            return self._remediate_git_failure(event)
        elif event.event_type == "dspy_analysis_incomplete":
            return self._remediate_dspy_issue(event)
        elif event.event_type == "performance_degradation":
            return self._remediate_performance(event)
        
        return None
    
    def _remediate_otel_gap(self, event: FeedbackEvent) -> Optional[str]:
        """Remediate OTEL monitoring gaps."""
        gap_type = event.data.get("gap_type")
        
        if gap_type == "missing_spans":
            # Create task to add missing spans
            task_id = create_task(
                agent="otel_enhancer",
                args=["add_spans", event.data.get("missing_operations", [])],
                priority=70
            )
            logger.info(f"Created OTEL span enhancement task: {task_id}")
            return f"otel_enhancement:{task_id}"
        
        elif gap_type == "incomplete_telemetry":
            # Create task to enhance telemetry coverage
            task_id = create_task(
                agent="telemetry_enhancer", 
                args=["enhance_coverage", event.data.get("component")],
                priority=60
            )
            logger.info(f"Created telemetry enhancement task: {task_id}")
            return f"telemetry_enhancement:{task_id}"
        
        return None
    
    def _remediate_validation_failure(self, event: FeedbackEvent) -> Optional[str]:
        """Remediate validation system failures."""
        failure_type = event.data.get("failure_type")
        
        if failure_type == "schema_mismatch":
            # Create task to regenerate schemas
            task_id = create_task(
                agent="schema_regenerator",
                args=["regenerate", event.data.get("schema_name")],
                priority=80
            )
            logger.info(f"Created schema regeneration task: {task_id}")
            return f"schema_regen:{task_id}"
        
        elif failure_type == "semantic_validation_failed":
            # Create task to update semantic rules
            task_id = create_task(
                agent="semantic_updater",
                args=["update_rules", event.data.get("validation_errors", [])],
                priority=70
            )
            logger.info(f"Created semantic update task: {task_id}")
            return f"semantic_update:{task_id}"
        
        return None
    
    def _remediate_git_failure(self, event: FeedbackEvent) -> Optional[str]:
        """Remediate git operation failures."""
        error_type = event.data.get("error_type")
        
        if error_type == "merge_conflict":
            # Create task for intelligent conflict resolution
            task_id = create_task(
                agent="conflict_resolver",
                args=["resolve", event.data.get("conflicted_files", [])],
                priority=90
            )
            logger.info(f"Created conflict resolution task: {task_id}")
            return f"conflict_resolution:{task_id}"
        
        elif error_type == "permission_denied":
            # Create task to fix repository permissions
            task_id = create_task(
                agent="permission_fixer",
                args=["fix_perms", event.data.get("repo_path")],
                priority=85
            )
            logger.info(f"Created permission fix task: {task_id}")
            return f"permission_fix:{task_id}"
        
        return None
    
    def _remediate_dspy_issue(self, event: FeedbackEvent) -> Optional[str]:
        """Remediate DSPy analysis issues."""
        issue_type = event.data.get("issue_type")
        
        if issue_type == "runtime_missing":
            # Create task to initialize DSPy runtime
            task_id = create_task(
                agent="dspy_initializer",
                args=["init_runtime", event.data.get("missing_components", [])],
                priority=75
            )
            logger.info(f"Created DSPy runtime init task: {task_id}")
            return f"dspy_init:{task_id}"
        
        elif issue_type == "analysis_timeout":
            # Create task to optimize DSPy programs
            task_id = create_task(
                agent="dspy_optimizer",
                args=["optimize", event.data.get("slow_programs", [])],
                priority=60
            )
            logger.info(f"Created DSPy optimization task: {task_id}")
            return f"dspy_optimization:{task_id}"
        
        return None
    
    def _remediate_performance(self, event: FeedbackEvent) -> Optional[str]:
        """Remediate performance issues."""
        perf_type = event.data.get("performance_type")
        
        if perf_type == "slow_validation":
            # Create task to optimize validation pipeline
            task_id = create_task(
                agent="validation_optimizer",
                args=["optimize_pipeline", event.data.get("slow_layers", [])],
                priority=65
            )
            logger.info(f"Created validation optimization task: {task_id}")
            return f"validation_optimization:{task_id}"
        
        elif perf_type == "memory_leak":
            # Create task for memory optimization
            task_id = create_task(
                agent="memory_optimizer",
                args=["fix_leaks", event.data.get("leaky_components", [])],
                priority=85
            )
            logger.info(f"Created memory optimization task: {task_id}")
            return f"memory_optimization:{task_id}"
        
        return None
    
    @span("feedback_get_insights")
    def get_system_insights(self) -> Dict[str, Any]:
        """Analyze feedback history to provide system insights."""
        with self._lock:
            recent_events = [e for e in self.event_history 
                           if (datetime.datetime.now() - 
                               datetime.datetime.fromisoformat(e.timestamp)).days < 7]
            
            insights = {
                "total_events": len(self.event_history),
                "recent_events": len(recent_events),
                "event_types": {},
                "severity_distribution": {},
                "remediation_success_rate": 0,
                "top_issues": [],
                "system_health_score": 0.0
            }
            
            # Event type analysis
            for event in recent_events:
                insights["event_types"][event.event_type] = (
                    insights["event_types"].get(event.event_type, 0) + 1
                )
                insights["severity_distribution"][event.severity] = (
                    insights["severity_distribution"].get(event.severity, 0) + 1
                )
            
            # Remediation success rate
            remediated_events = [e for e in recent_events if e.action_taken]
            if recent_events:
                insights["remediation_success_rate"] = len(remediated_events) / len(recent_events)
            
            # Top issues
            event_counts = list(insights["event_types"].items())
            event_counts.sort(key=lambda x: x[1], reverse=True)
            insights["top_issues"] = event_counts[:5]
            
            # System health score (higher is better)
            critical_events = len([e for e in recent_events if e.severity == "critical"])
            error_events = len([e for e in recent_events if e.severity == "error"])
            
            if recent_events:
                health_penalty = (critical_events * 3 + error_events * 2) / len(recent_events)
                remediation_bonus = insights["remediation_success_rate"] * 0.3
                insights["system_health_score"] = max(0, min(1, 1 - health_penalty + remediation_bonus))
            else:
                insights["system_health_score"] = 1.0
            
            return insights

# Global feedback processor
_processor = None

def get_feedback_processor() -> FeedbackProcessor:
    """Get or create the global feedback processor."""
    global _processor
    if _processor is None:
        _processor = FeedbackProcessor()
        _setup_default_handlers()
    return _processor

def _setup_default_handlers():
    """Setup default feedback event handlers."""
    processor = _processor
    
    # Log all events
    def log_event(event: FeedbackEvent):
        logger.info(f"Feedback event: {event.event_type} from {event.source} (severity: {event.severity})")
    
    # Register for all event types
    for event_type in [
        "otel_gap_detected", "validation_failed", "git_operation_failed",
        "dspy_analysis_incomplete", "performance_degradation"
    ]:
        processor.register_handler(event_type, log_event)

# Convenience functions for sending feedback events

@span("feedback_send_event")
def send_feedback_event(
    source: str,
    event_type: str,
    data: Dict[str, Any],
    severity: str = "info"
) -> Optional[str]:
    """Send a feedback event to the processor."""
    event = FeedbackEvent(
        timestamp=datetime.datetime.now().isoformat(),
        source=source,
        event_type=event_type,
        data=data,
        severity=severity
    )
    
    processor = get_feedback_processor()
    return processor.process_event(event)

@span("feedback_otel_gap")
def report_otel_gap(gap_type: str, details: Dict[str, Any]) -> Optional[str]:
    """Report an OTEL monitoring gap."""
    return send_feedback_event(
        source="otel_monitor",
        event_type="otel_gap_detected",
        data={"gap_type": gap_type, **details},
        severity="warning"
    )

@span("feedback_validation_failure")
def report_validation_failure(failure_type: str, details: Dict[str, Any]) -> Optional[str]:
    """Report a validation system failure."""
    return send_feedback_event(
        source="validation_system",
        event_type="validation_failed", 
        data={"failure_type": failure_type, **details},
        severity="error"
    )

@span("feedback_git_failure")
def report_git_failure(error_type: str, details: Dict[str, Any]) -> Optional[str]:
    """Report a git operation failure."""
    return send_feedback_event(
        source="git_operations",
        event_type="git_operation_failed",
        data={"error_type": error_type, **details},
        severity="error"
    )

@span("feedback_dspy_issue")
def report_dspy_issue(issue_type: str, details: Dict[str, Any]) -> Optional[str]:
    """Report a DSPy analysis issue."""
    return send_feedback_event(
        source="dspy_analysis",
        event_type="dspy_analysis_incomplete",
        data={"issue_type": issue_type, **details},
        severity="warning"
    )

@span("feedback_performance_issue")
def report_performance_issue(perf_type: str, details: Dict[str, Any]) -> Optional[str]:
    """Report a performance degradation."""
    return send_feedback_event(
        source="performance_monitor",
        event_type="performance_degradation",
        data={"performance_type": perf_type, **details},
        severity="warning"
    )

# Integration with existing systems

def integrate_with_otel_monitor():
    """Integrate feedback loop with OTEL monitoring system."""
    try:
        from ..commands.claude_code_otel_monitoring import ClaudeCodeOTELMonitor
        
        # Monkey patch to add feedback integration
        original_identify_gap = ClaudeCodeOTELMonitor.identify_gap
        
        def patched_identify_gap(self, gap_type: str, details: Dict[str, Any]):
            result = original_identify_gap(self, gap_type, details)
            
            # Send feedback event
            report_otel_gap(gap_type, details)
            
            return result
        
        ClaudeCodeOTELMonitor.identify_gap = patched_identify_gap
        logger.info("Integrated feedback loop with OTEL monitor")
        
    except ImportError:
        logger.warning("Could not integrate with OTEL monitor - module not found")

def integrate_with_validation_system():
    """Integrate feedback loop with validation system."""
    try:
        from ..commands.multilayer_weaver_feedback import MultilayerWeaverFeedback
        
        # Add feedback reporting to validation failures
        # This would require modifying the validation system to call feedback functions
        logger.info("Validation system integration placeholder - requires validation system modifications")
        
    except ImportError:
        logger.warning("Could not integrate with validation system - module not found")

# Auto-initialize integrations when module is imported
try:
    integrate_with_otel_monitor()
    integrate_with_validation_system()
except Exception as e:
    logger.warning(f"Could not auto-initialize feedback integrations: {e}")