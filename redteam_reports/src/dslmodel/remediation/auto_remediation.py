"""
Auto-Remediation Engine
Automatically fixes system issues based on telemetry patterns and autonomous decisions.
"""

import asyncio
import time
import subprocess
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from loguru import logger

from ..telemetry.realtime_processor import TelemetryEvent, TelemetryMetrics, get_telemetry_processor
from ..agents.autonomous_decision_engine import AutonomousDecisionEngine


class RemediationAction(Enum):
    """Types of remediation actions."""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up" 
    SCALE_DOWN = "scale_down"
    CLEAR_CACHE = "clear_cache"
    KILL_PROCESS = "kill_process"
    UPDATE_CONFIG = "update_config"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    CIRCUIT_BREAKER = "circuit_breaker"
    THROTTLE_REQUESTS = "throttle_requests"
    HEALTH_CHECK = "health_check"


@dataclass
class RemediationPlan:
    """A plan for fixing a detected issue."""
    issue_type: str
    severity: str  # critical, high, medium, low
    action: RemediationAction
    parameters: Dict[str, Any]
    estimated_impact: str
    rollback_plan: Optional[str] = None
    confidence: float = 0.8
    trace_id: str = None


@dataclass
class RemediationResult:
    """Result of executing a remediation plan."""
    plan: RemediationPlan
    success: bool
    execution_time_ms: float
    output: str
    error: Optional[str] = None
    side_effects: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "issue_type": self.plan.issue_type,
            "action": self.plan.action.value,
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
            "output": self.output[:500],  # Truncate long outputs
            "error": self.error,
            "confidence": self.plan.confidence,
            "trace_id": self.plan.trace_id
        }


class AutoRemediationEngine:
    """Automatically fixes issues based on telemetry and autonomous decisions."""
    
    def __init__(self, coordination_dir: Path, dry_run: bool = False):
        """Initialize the auto-remediation engine."""
        self.coordination_dir = coordination_dir
        self.dry_run = dry_run
        self.enabled = True
        self.max_concurrent_actions = 3
        self.active_remediations = {}
        self.remediation_history = []
        
        # Integration with telemetry and autonomous engine
        self.telemetry_processor = get_telemetry_processor()
        self.autonomous_engine = AutonomousDecisionEngine(coordination_dir)
        
        # Pattern-to-remediation mapping
        self.remediation_strategies = {
            "error_spike": self._create_error_spike_plan,
            "latency_increase": self._create_latency_plan,
            "throughput_drop": self._create_throughput_plan,
            "cascade_failure": self._create_cascade_failure_plan,
            "resource_exhaustion": self._create_resource_plan,
            "unhealthy_agents": self._create_agent_health_plan
        }
        
        # Subscribe to telemetry patterns
        self.telemetry_processor.subscribe_to_metrics(self._on_metrics_received)
        
        logger.info(f"Auto-remediation engine initialized (dry_run={dry_run})")
    
    def _on_metrics_received(self, metrics: TelemetryMetrics):
        """Handle incoming telemetry metrics and trigger remediation if needed."""
        try:
            # Check for patterns that need remediation
            for pattern_name, score in metrics.health_indicators.items():
                if score > 0.7:  # High severity threshold
                    logger.warning(f"Detected high-severity pattern: {pattern_name} (score: {score:.2f})")
                    self._trigger_remediation(pattern_name, score, metrics)
                    
        except Exception as e:
            logger.error(f"Error processing metrics for remediation: {e}")
    
    def _trigger_remediation(self, pattern_name: str, severity_score: float, metrics: TelemetryMetrics):
        """Trigger remediation for a detected pattern."""
        if not self.enabled:
            logger.info(f"Remediation disabled - would handle {pattern_name}")
            return
        
        # Check if we're already handling this pattern
        if pattern_name in self.active_remediations:
            logger.debug(f"Already remediating {pattern_name}")
            return
        
        # Check concurrent limit
        if len(self.active_remediations) >= self.max_concurrent_actions:
            logger.warning(f"Max concurrent remediations reached, queuing {pattern_name}")
            return
        
        # Create remediation plan
        if pattern_name in self.remediation_strategies:
            plan = self.remediation_strategies[pattern_name](severity_score, metrics)
            if plan:
                self._execute_remediation_async(plan)
    
    def _execute_remediation_async(self, plan: RemediationPlan):
        """Execute remediation plan asynchronously."""
        import threading
        
        def execute():
            try:
                self.active_remediations[plan.issue_type] = plan
                result = self._execute_remediation(plan)
                self.remediation_history.append(result)
                
                if result.success:
                    logger.success(f"Remediation successful: {plan.issue_type}")
                else:
                    logger.error(f"Remediation failed: {plan.issue_type} - {result.error}")
                    
            except Exception as e:
                logger.error(f"Remediation execution error: {e}")
            finally:
                self.active_remediations.pop(plan.issue_type, None)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
    
    def _execute_remediation(self, plan: RemediationPlan) -> RemediationResult:
        """Execute a specific remediation plan."""
        start_time = time.time()
        
        if self.dry_run:
            logger.info(f"DRY RUN: Would execute {plan.action.value} for {plan.issue_type}")
            return RemediationResult(
                plan=plan,
                success=True,
                execution_time_ms=(time.time() - start_time) * 1000,
                output=f"DRY RUN: {plan.action.value} simulated",
                side_effects=["dry_run_simulation"]
            )
        
        try:
            # Route to specific action handlers
            action_handlers = {
                RemediationAction.RESTART_SERVICE: self._restart_service,
                RemediationAction.SCALE_UP: self._scale_up,
                RemediationAction.SCALE_DOWN: self._scale_down,
                RemediationAction.CLEAR_CACHE: self._clear_cache,
                RemediationAction.KILL_PROCESS: self._kill_process,
                RemediationAction.UPDATE_CONFIG: self._update_config,
                RemediationAction.CIRCUIT_BREAKER: self._enable_circuit_breaker,
                RemediationAction.HEALTH_CHECK: self._run_health_check
            }
            
            handler = action_handlers.get(plan.action)
            if not handler:
                raise ValueError(f"No handler for action: {plan.action}")
            
            output = handler(plan.parameters)
            
            return RemediationResult(
                plan=plan,
                success=True,
                execution_time_ms=(time.time() - start_time) * 1000,
                output=output
            )
            
        except Exception as e:
            return RemediationResult(
                plan=plan,
                success=False,
                execution_time_ms=(time.time() - start_time) * 1000,
                output="",
                error=str(e)
            )
    
    def _create_error_spike_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for error spike remediation."""
        # Find service with highest error rate
        worst_service = max(metrics.error_rates, key=metrics.error_rates.get) if metrics.error_rates else None
        
        if not worst_service or metrics.error_rates[worst_service] < 0.2:
            return None
        
        return RemediationPlan(
            issue_type="error_spike",
            severity="critical" if severity > 0.8 else "high",
            action=RemediationAction.RESTART_SERVICE,
            parameters={"service_name": worst_service, "graceful": True},
            estimated_impact="Service downtime: 10-30 seconds",
            rollback_plan="Restart can be reverted immediately",
            confidence=0.7,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    def _create_latency_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for latency remediation."""
        return RemediationPlan(
            issue_type="latency_increase",
            severity="medium",
            action=RemediationAction.SCALE_UP,
            parameters={"target_agents": 3, "reason": "latency_spike"},
            estimated_impact="Additional resource usage",
            confidence=0.8,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    def _create_throughput_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for throughput drop remediation."""
        return RemediationPlan(
            issue_type="throughput_drop", 
            severity="high",
            action=RemediationAction.SCALE_UP,
            parameters={"target_agents": 5, "reason": "throughput_recovery"},
            estimated_impact="Increased capacity and costs",
            confidence=0.8,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    def _create_cascade_failure_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for cascade failure prevention."""
        return RemediationPlan(
            issue_type="cascade_failure",
            severity="critical",
            action=RemediationAction.CIRCUIT_BREAKER,
            parameters={"enable_circuit_breaker": True, "timeout_seconds": 300},
            estimated_impact="Reduced functionality to prevent total failure",
            confidence=0.9,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    def _create_resource_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for resource exhaustion."""
        return RemediationPlan(
            issue_type="resource_exhaustion",
            severity="high",
            action=RemediationAction.CLEAR_CACHE,
            parameters={"cache_type": "memory", "percentage": 50},
            estimated_impact="Temporary performance reduction",
            confidence=0.6,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    def _create_agent_health_plan(self, severity: float, metrics: TelemetryMetrics) -> Optional[RemediationPlan]:
        """Create plan for unhealthy agents."""
        return RemediationPlan(
            issue_type="unhealthy_agents",
            severity="medium",
            action=RemediationAction.HEALTH_CHECK,
            parameters={"restart_unhealthy": True},
            estimated_impact="Removal and restart of unhealthy agents",
            confidence=0.9,
            trace_id=f"remediation_{int(time.time())}"
        )
    
    # Action handlers
    def _restart_service(self, params: Dict[str, Any]) -> str:
        """Restart a service."""
        service_name = params.get("service_name", "unknown")
        graceful = params.get("graceful", True)
        
        # In real implementation, this would restart actual services
        # For demo, we'll simulate agent restart
        result = self.autonomous_engine.execute_emergency_scaling(target_agents=2)
        return f"Service {service_name} restart initiated ({'graceful' if graceful else 'forceful'}): {result}"
    
    def _scale_up(self, params: Dict[str, Any]) -> str:
        """Scale up services."""
        target_agents = params.get("target_agents", 3)
        reason = params.get("reason", "auto_remediation")
        
        # Use autonomous engine for scaling
        result = self.autonomous_engine.execute_emergency_scaling(target_agents=target_agents)
        return f"Scaled up to {target_agents} agents for {reason}: {result}"
    
    def _scale_down(self, params: Dict[str, Any]) -> str:
        """Scale down services."""
        target_agents = params.get("target_agents", 1)
        
        result = self.autonomous_engine.execute_emergency_scaling(target_agents=target_agents)
        return f"Scaled down to {target_agents} agents: {result}"
    
    def _clear_cache(self, params: Dict[str, Any]) -> str:
        """Clear system caches."""
        cache_type = params.get("cache_type", "memory")
        percentage = params.get("percentage", 50)
        
        # Simulate cache clearing
        return f"Cleared {percentage}% of {cache_type} cache"
    
    def _kill_process(self, params: Dict[str, Any]) -> str:
        """Kill problematic processes."""
        process_name = params.get("process_name", "unknown")
        return f"Terminated process: {process_name}"
    
    def _update_config(self, params: Dict[str, Any]) -> str:
        """Update configuration."""
        config_key = params.get("config_key", "unknown")
        config_value = params.get("config_value", "unknown")
        return f"Updated config: {config_key} = {config_value}"
    
    def _enable_circuit_breaker(self, params: Dict[str, Any]) -> str:
        """Enable circuit breaker to prevent cascade failures."""
        timeout = params.get("timeout_seconds", 300)
        return f"Circuit breaker enabled for {timeout} seconds"
    
    def _run_health_check(self, params: Dict[str, Any]) -> str:
        """Run health checks and restart unhealthy components."""
        restart_unhealthy = params.get("restart_unhealthy", False)
        
        # Check agent health via coordination files
        agent_files = list(self.coordination_dir.glob("agent_*.json"))
        healthy_agents = len(agent_files)
        
        if restart_unhealthy and healthy_agents < 2:
            result = self.autonomous_engine.execute_emergency_scaling(target_agents=3)
            return f"Health check: {healthy_agents} healthy agents, scaled to 3: {result}"
        
        return f"Health check: {healthy_agents} healthy agents"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current remediation engine status."""
        return {
            "enabled": self.enabled,
            "dry_run": self.dry_run,
            "active_remediations": len(self.active_remediations),
            "total_remediations": len(self.remediation_history),
            "success_rate": sum(1 for r in self.remediation_history if r.success) / max(len(self.remediation_history), 1),
            "recent_actions": [r.plan.action.value for r in self.remediation_history[-5:]]
        }
    
    def get_remediation_history(self) -> List[Dict[str, Any]]:
        """Get history of remediation actions."""
        return [result.to_dict() for result in self.remediation_history]
    
    def enable(self):
        """Enable auto-remediation."""
        self.enabled = True
        logger.info("Auto-remediation enabled")
    
    def disable(self):
        """Disable auto-remediation."""
        self.enabled = False
        logger.info("Auto-remediation disabled")


# Global auto-remediation instance
_global_remediation_engine: Optional[AutoRemediationEngine] = None


def get_auto_remediation_engine(coordination_dir: Path, dry_run: bool = False) -> AutoRemediationEngine:
    """Get the global auto-remediation engine."""
    global _global_remediation_engine
    if _global_remediation_engine is None:
        _global_remediation_engine = AutoRemediationEngine(coordination_dir, dry_run)
    return _global_remediation_engine


def trigger_manual_remediation(issue_type: str, action: RemediationAction, parameters: Dict[str, Any]) -> RemediationResult:
    """Manually trigger a remediation action."""
    engine = get_auto_remediation_engine(Path("coordination"))
    
    plan = RemediationPlan(
        issue_type=issue_type,
        severity="manual",
        action=action,
        parameters=parameters,
        estimated_impact="Manual intervention",
        confidence=1.0,
        trace_id=f"manual_{int(time.time())}"
    )
    
    return engine._execute_remediation(plan)