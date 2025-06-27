"""
Autonomous Decision Engine - Python Implementation
Telemetry-driven autonomous system improvement based on SwarmSH pattern.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger


class DecisionType(str, Enum):
    """Types of autonomous decisions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    OPTIMIZE = "optimize"
    RESTART = "restart"
    HEALTH_CHECK = "health_check"
    COORDINATION_IMPROVE = "coordination_improve"
    TELEMETRY_ENHANCE = "telemetry_enhance"


class SystemHealth(str, Enum):
    """System health states."""
    CRITICAL = "critical"
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    OPTIMAL = "optimal"


@dataclass
class SystemMetrics:
    """System state metrics for decision making."""
    completion_rate: float
    active_agents: int
    work_queue_size: int
    telemetry_volume: int
    health_score: float
    error_rate: float
    response_time_ms: float
    timestamp: str
    
    @classmethod
    def from_coordination_data(cls, coordination_dir: Path) -> "SystemMetrics":
        """Extract metrics from coordination files."""
        metrics = {
            "completion_rate": 0.0,
            "active_agents": 0,
            "work_queue_size": 0,
            "telemetry_volume": 0,
            "health_score": 0.0,
            "error_rate": 0.0,
            "response_time_ms": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Read coordination files if they exist
            if coordination_dir.exists():
                # Count agent files
                agent_files = list(coordination_dir.glob("agent_*.json"))
                metrics["active_agents"] = len(agent_files)
                
                # Analyze work files
                work_files = list(coordination_dir.glob("work_*.json"))
                metrics["work_queue_size"] = len(work_files)
                
                # Calculate completion rate
                completed_files = list(coordination_dir.glob("completed_*.json"))
                total_work = len(work_files) + len(completed_files)
                if total_work > 0:
                    metrics["completion_rate"] = len(completed_files) / total_work
                
                # Count telemetry files
                telemetry_files = list(coordination_dir.glob("telemetry_*.json"))
                metrics["telemetry_volume"] = len(telemetry_files)
            
            # Calculate health score
            metrics["health_score"] = cls._calculate_health_score(metrics)
            
        except Exception as e:
            logger.warning(f"Error reading coordination data: {e}")
            
        return cls(**metrics)
    
    @staticmethod
    def _calculate_health_score(metrics: Dict[str, Any]) -> float:
        """Calculate overall system health score (0.0-1.0)."""
        # Simple health calculation based on key metrics
        health = 0.0
        
        # Completion rate contributes 40%
        health += metrics["completion_rate"] * 0.4
        
        # Agent count contributes 30% (optimal around 3-5 agents)
        agent_score = min(metrics["active_agents"] / 5.0, 1.0)
        health += agent_score * 0.3
        
        # Work queue size contributes 20% (lower is better)
        queue_score = max(0.0, 1.0 - (metrics["work_queue_size"] / 10.0))
        health += queue_score * 0.2
        
        # Telemetry volume contributes 10% (some telemetry is good)
        telemetry_score = min(metrics["telemetry_volume"] / 20.0, 1.0)
        health += telemetry_score * 0.1
        
        return min(health, 1.0)


@dataclass
class Decision:
    """Represents an autonomous decision."""
    id: str
    type: DecisionType
    priority: int
    description: str
    parameters: Dict[str, Any]
    confidence: float
    created_at: str
    
    @classmethod
    def create(cls, decision_type: DecisionType, description: str, 
               priority: int = 5, parameters: Optional[Dict] = None,
               confidence: float = 0.8) -> "Decision":
        """Create a new decision with unique ID."""
        return cls(
            id=str(uuid.uuid4()),
            type=decision_type,
            priority=priority,
            description=description,
            parameters=parameters or {},
            confidence=confidence,
            created_at=datetime.now().isoformat()
        )


class DecisionEngine:
    """Rule-based autonomous decision engine."""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """Initialize with configurable thresholds."""
        self.thresholds = thresholds or {
            "critical_health": 0.3,
            "degraded_health": 0.6,
            "optimal_health": 0.9,
            "max_queue_size": 15,
            "min_agents": 2,
            "max_agents": 8,
            "high_completion_rate": 0.8,
            "low_completion_rate": 0.4
        }
    
    def analyze_and_decide(self, metrics: SystemMetrics) -> List[Decision]:
        """Analyze system state and generate autonomous decisions."""
        decisions = []
        
        # Determine system health state
        health_state = self._get_health_state(metrics.health_score)
        
        logger.info(f"System health: {health_state.value} (score: {metrics.health_score:.2f})")
        
        # Apply decision rules based on health state
        if health_state == SystemHealth.CRITICAL:
            decisions.extend(self._critical_decisions(metrics))
        elif health_state == SystemHealth.DEGRADED:
            decisions.extend(self._degraded_decisions(metrics))
        elif health_state == SystemHealth.HEALTHY:
            decisions.extend(self._healthy_decisions(metrics))
        elif health_state == SystemHealth.OPTIMAL:
            decisions.extend(self._optimal_decisions(metrics))
        
        # Sort decisions by priority (higher first)
        decisions.sort(key=lambda d: d.priority, reverse=True)
        
        return decisions
    
    def _get_health_state(self, health_score: float) -> SystemHealth:
        """Determine health state from score."""
        if health_score < self.thresholds["critical_health"]:
            return SystemHealth.CRITICAL
        elif health_score < self.thresholds["degraded_health"]:
            return SystemHealth.DEGRADED
        elif health_score < self.thresholds["optimal_health"]:
            return SystemHealth.HEALTHY
        else:
            return SystemHealth.OPTIMAL
    
    def _critical_decisions(self, metrics: SystemMetrics) -> List[Decision]:
        """Decisions for critical system state."""
        decisions = []
        
        # Emergency agent scaling
        if metrics.active_agents < self.thresholds["min_agents"]:
            decisions.append(Decision.create(
                DecisionType.SCALE_UP,
                f"Emergency scale up: only {metrics.active_agents} agents active",
                priority=10,
                parameters={"target_agents": self.thresholds["min_agents"]},
                confidence=0.95
            ))
        
        # Clear work queue
        if metrics.work_queue_size > self.thresholds["max_queue_size"]:
            decisions.append(Decision.create(
                DecisionType.COORDINATION_IMPROVE,
                f"Critical queue size: {metrics.work_queue_size} items",
                priority=9,
                parameters={"action": "clear_old_work", "max_age_hours": 2}
            ))
        
        return decisions
    
    def _degraded_decisions(self, metrics: SystemMetrics) -> List[Decision]:
        """Decisions for degraded system state."""
        decisions = []
        
        # Scale up if completion rate is low
        if metrics.completion_rate < self.thresholds["low_completion_rate"]:
            decisions.append(Decision.create(
                DecisionType.SCALE_UP,
                f"Low completion rate: {metrics.completion_rate:.2f}",
                priority=7,
                parameters={"target_agents": metrics.active_agents + 1}
            ))
        
        # Optimize coordination
        if metrics.work_queue_size > 5:
            decisions.append(Decision.create(
                DecisionType.COORDINATION_IMPROVE,
                f"Queue building up: {metrics.work_queue_size} items",
                priority=6,
                parameters={"action": "optimize_distribution"}
            ))
        
        return decisions
    
    def _healthy_decisions(self, metrics: SystemMetrics) -> List[Decision]:
        """Decisions for healthy system state."""
        decisions = []
        
        # Optimize if completion rate could be better
        if metrics.completion_rate < self.thresholds["high_completion_rate"]:
            decisions.append(Decision.create(
                DecisionType.OPTIMIZE,
                f"Room for improvement: {metrics.completion_rate:.2f} completion rate",
                priority=4,
                parameters={"focus": "completion_rate"}
            ))
        
        return decisions
    
    def _optimal_decisions(self, metrics: SystemMetrics) -> List[Decision]:
        """Decisions for optimal system state."""
        decisions = []
        
        # Scale down if over-provisioned
        if (metrics.active_agents > self.thresholds["max_agents"] or 
            (metrics.active_agents > 3 and metrics.work_queue_size == 0)):
            decisions.append(Decision.create(
                DecisionType.SCALE_DOWN,
                f"System over-provisioned: {metrics.active_agents} agents, {metrics.work_queue_size} queue",
                priority=2,
                parameters={"target_agents": max(2, metrics.active_agents - 1)}
            ))
        
        # Enhance telemetry
        if metrics.telemetry_volume < 10:
            decisions.append(Decision.create(
                DecisionType.TELEMETRY_ENHANCE,
                "Opportunity to enhance telemetry collection",
                priority=1,
                parameters={"action": "increase_sampling"}
            ))
        
        return decisions


class AutonomousDecisionEngine:
    """Main autonomous decision engine coordinator."""
    
    def __init__(self, coordination_dir: Path, trace_id: Optional[str] = None):
        """Initialize the autonomous decision engine."""
        self.coordination_dir = coordination_dir
        self.trace_id = trace_id or str(uuid.uuid4())
        self.decision_engine = DecisionEngine()
        
        logger.info(f"Autonomous Decision Engine initialized (trace: {self.trace_id})")
    
    def analyze_system_state(self) -> SystemMetrics:
        """Analyze current system state and return metrics."""
        logger.info("Analyzing system state...")
        
        metrics = SystemMetrics.from_coordination_data(self.coordination_dir)
        
        # Log key metrics
        logger.info(f"System metrics: "
                   f"health={metrics.health_score:.2f}, "
                   f"agents={metrics.active_agents}, "
                   f"queue={metrics.work_queue_size}, "
                   f"completion={metrics.completion_rate:.2f}")
        
        return metrics
    
    def make_autonomous_decisions(self, metrics: SystemMetrics) -> List[Decision]:
        """Generate autonomous decisions based on system metrics."""
        logger.info("Making autonomous decisions...")
        
        decisions = self.decision_engine.analyze_and_decide(metrics)
        
        logger.info(f"Generated {len(decisions)} decisions")
        for decision in decisions:
            logger.info(f"  [{decision.priority}] {decision.type.value}: {decision.description}")
        
        return decisions
    
    def execute_decisions(self, decisions: List[Decision], max_per_cycle: int = 3) -> Dict[str, Any]:
        """Execute autonomous decisions with limits."""
        logger.info(f"Executing up to {max_per_cycle} decisions...")
        
        executed = []
        failed = []
        
        # Execute highest priority decisions first
        for decision in decisions[:max_per_cycle]:
            try:
                result = self._execute_decision(decision)
                executed.append({
                    "decision_id": decision.id,
                    "type": decision.type.value,
                    "result": result
                })
                logger.success(f"Executed: {decision.description}")
            except Exception as e:
                failed.append({
                    "decision_id": decision.id,
                    "error": str(e)
                })
                logger.error(f"Failed to execute {decision.description}: {e}")
        
        return {
            "executed": executed,
            "failed": failed,
            "skipped": len(decisions) - len(executed) - len(failed)
        }
    
    def _execute_decision(self, decision: Decision) -> Dict[str, Any]:
        """Execute a single decision."""
        # This is where actual execution logic would go
        # For now, simulate execution
        
        if decision.type == DecisionType.SCALE_UP:
            return {"action": "scaled_up", "agents": decision.parameters.get("target_agents")}
        elif decision.type == DecisionType.COORDINATION_IMPROVE:
            return {"action": "coordination_improved", "method": decision.parameters.get("action")}
        elif decision.type == DecisionType.OPTIMIZE:
            return {"action": "optimization_applied", "focus": decision.parameters.get("focus")}
        else:
            return {"action": "simulated", "type": decision.type.value}
    
    def run_cycle(self) -> Dict[str, Any]:
        """Run a complete autonomous decision cycle."""
        logger.info(f"Starting autonomous decision cycle (trace: {self.trace_id})")
        
        try:
            # 1. Analyze system state
            metrics = self.analyze_system_state()
            
            # 2. Make decisions
            decisions = self.make_autonomous_decisions(metrics)
            
            # 3. Execute decisions
            execution_results = self.execute_decisions(decisions)
            
            # 4. Return cycle summary
            cycle_result = {
                "trace_id": self.trace_id,
                "timestamp": datetime.now().isoformat(),
                "metrics": asdict(metrics),
                "decisions_generated": len(decisions),
                "execution_results": execution_results
            }
            
            logger.success(f"Autonomous cycle completed (trace: {self.trace_id})")
            return cycle_result
            
        except Exception as e:
            logger.error(f"Autonomous cycle failed: {e}")
            return {
                "trace_id": self.trace_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def status(self) -> Dict[str, Any]:
        """Get current system status without making changes."""
        metrics = self.analyze_system_state()
        health_state = self.decision_engine._get_health_state(metrics.health_score)
        
        return {
            "health_state": health_state.value,
            "metrics": asdict(metrics),
            "trace_id": self.trace_id
        }