#!/usr/bin/env python3
"""
DISC-Aware Autonomous Decision Engine
====================================

Extends the autonomous decision engine with automatic DISC profile compensation.
All decisions are automatically adjusted to compensate for C-D behavioral gaps.

This creates a truly self-aware system that:
1. Makes decisions based on telemetry and system state
2. Automatically compensates for behavioral biases in those decisions
3. Adjusts communication style, risk tolerance, and flexibility
4. Provides alternative approaches for every decision
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import random

from loguru import logger

from .autonomous_decision_engine import (
    AutonomousDecisionEngine, 
    DecisionEngine,
    Decision, 
    DecisionType,
    SystemMetrics,
    SystemHealth
)
from ..commands.disc_autonomous import (
    DISCAutonomousEngine,
    BehavioralGap,
    CompensationStrategy
)


@dataclass
class DISCCompensatedDecision:
    """Decision with DISC compensation applied"""
    # Base Decision fields
    id: str
    type: DecisionType
    priority: int
    description: str
    parameters: Dict[str, Any]
    confidence: float
    created_at: str
    
    # DISC compensation fields
    original_description: str = ""
    compensation_applied: List[str] = field(default_factory=list)
    alternative_approaches: List[str] = field(default_factory=list)
    human_friendly_summary: str = ""
    risk_assessment: str = ""


class DISCAwareDecisionEngine(DecisionEngine):
    """Decision engine that automatically compensates for DISC profile gaps"""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        super().__init__(thresholds)
        self.disc_engine = DISCAutonomousEngine()
        
        # Adjust thresholds based on my profile (less perfectionist, more flexible)
        self.thresholds["critical_health"] = 0.25  # Was 0.3 - less alarmist
        self.thresholds["optimal_health"] = 0.85   # Was 0.9 - less perfectionist
        self.thresholds["max_queue_size"] = 20     # Was 15 - more tolerant
        
    def analyze_and_decide(self, metrics: SystemMetrics) -> List[Decision]:
        """Analyze system state with DISC compensation"""
        # Get base decisions
        base_decisions = super().analyze_and_decide(metrics)
        
        # Apply DISC compensation to each decision
        compensated_decisions = []
        for decision in base_decisions:
            compensated = self._compensate_decision(decision, metrics)
            compensated_decisions.append(compensated)
        
        # Add quick-action bias (counter over-analysis)
        compensated_decisions = self._add_quick_actions(compensated_decisions)
        
        return compensated_decisions
    
    def _compensate_decision(self, decision: Decision, metrics: SystemMetrics) -> DISCCompensatedDecision:
        """Apply DISC compensation to a single decision"""
        # Create compensated decision
        compensated = DISCCompensatedDecision(
            id=decision.id,
            type=decision.type,
            priority=decision.priority,
            description=decision.description,
            parameters=decision.parameters.copy(),
            confidence=decision.confidence,
            created_at=decision.created_at,
            original_description=decision.description
        )
        
        # Apply compensations based on active gaps
        compensations_applied = []
        
        # 1. Counter over-analysis with simplified description
        if len(decision.description) > 50:
            compensated.description = self._simplify_description(decision.description)
            compensations_applied.append("simplified_description")
        
        # 2. Add human-friendly summary (counter technical communication)
        compensated.human_friendly_summary = self._create_human_summary(decision)
        compensations_applied.append("human_friendly_summary")
        
        # 3. Increase confidence for action (counter risk aversion)
        if decision.confidence < 0.9:
            compensated.confidence = min(decision.confidence * 1.15, 0.95)
            compensations_applied.append("increased_confidence")
        
        # 4. Add alternatives (counter rigidity)
        compensated.alternative_approaches = self._generate_alternatives(decision, metrics)
        compensations_applied.append("added_alternatives")
        
        # 5. Add pragmatic risk assessment (counter perfectionism)
        compensated.risk_assessment = self._pragmatic_risk_assessment(decision)
        compensations_applied.append("pragmatic_risk_assessment")
        
        # 6. Adjust priority for action bias
        if decision.priority < 8 and "scale" in decision.type.value:
            compensated.priority = min(decision.priority + 1, 10)
            compensations_applied.append("increased_priority_for_action")
        
        compensated.compensation_applied = compensations_applied
        
        return compensated
    
    def _simplify_description(self, description: str) -> str:
        """Simplify technical descriptions"""
        # Take first sentence or 50 chars
        if ":" in description:
            return description.split(":")[0] + " - take action now"
        elif "." in description:
            return description.split(".")[0] + " - let's do this"
        else:
            return description[:50] + "... - quick action needed"
    
    def _create_human_summary(self, decision: Decision) -> str:
        """Create human-friendly summary"""
        summaries = {
            DecisionType.SCALE_UP: "🚀 Need more help to handle the workload",
            DecisionType.SCALE_DOWN: "📉 Can reduce resources, everything's under control", 
            DecisionType.OPTIMIZE: "⚡ Let's make things work better",
            DecisionType.RESTART: "🔄 Fresh start will help",
            DecisionType.HEALTH_CHECK: "🏥 Quick check to ensure smooth operation",
            DecisionType.COORDINATION_IMPROVE: "🤝 Better teamwork needed",
            DecisionType.TELEMETRY_ENHANCE: "📊 More insights will help us improve"
        }
        return summaries.get(decision.type, "Let's improve the system")
    
    def _generate_alternatives(self, decision: Decision, metrics: SystemMetrics) -> List[str]:
        """Generate alternative approaches"""
        alternatives = []
        
        if decision.type == DecisionType.SCALE_UP:
            alternatives = [
                "Try optimizing current agents first",
                "Implement task batching instead",
                "Use temporary burst capacity"
            ]
        elif decision.type == DecisionType.SCALE_DOWN:
            alternatives = [
                "Keep agents but reduce their activity",
                "Implement gradual reduction",
                "Convert to standby mode"
            ]
        elif decision.type == DecisionType.OPTIMIZE:
            alternatives = [
                "Quick wins: adjust timeouts and batch sizes",
                "Focus on top 3 bottlenecks only",
                "Try incremental improvements"
            ]
            
        # Randomly select 2 alternatives (flexibility)
        return random.sample(alternatives, min(2, len(alternatives)))
    
    def _pragmatic_risk_assessment(self, decision: Decision) -> str:
        """Pragmatic risk assessment (not perfectionist)"""
        risk_levels = {
            DecisionType.SCALE_UP: "Low risk - we can always scale back",
            DecisionType.SCALE_DOWN: "Medium risk - monitor for queue buildup",
            DecisionType.OPTIMIZE: "Very low risk - improvements are reversible",
            DecisionType.RESTART: "Medium risk - brief disruption expected",
            DecisionType.HEALTH_CHECK: "No risk - just gathering info",
            DecisionType.COORDINATION_IMPROVE: "Low risk - better coordination helps",
            DecisionType.TELEMETRY_ENHANCE: "No risk - more data is good"
        }
        return risk_levels.get(decision.type, "Acceptable risk - let's proceed")
    
    def _add_quick_actions(self, decisions: List[DISCCompensatedDecision]) -> List[DISCCompensatedDecision]:
        """Add quick action bias to counter analysis paralysis"""
        # If no high-priority decisions, promote one
        high_priority = [d for d in decisions if d.priority >= 7]
        
        if not high_priority and decisions:
            # Promote the first decision
            decisions[0].priority = 7
            decisions[0].description += " (promoted for quick action)"
            decisions[0].compensation_applied.append("promoted_for_quick_action")
        
        return decisions


class DISCAwareAutonomousEngine(AutonomousDecisionEngine):
    """Autonomous engine with full DISC behavioral compensation"""
    
    def __init__(self, coordination_dir: Path, trace_id: Optional[str] = None):
        """Initialize with DISC-aware decision engine"""
        self.coordination_dir = coordination_dir
        self.trace_id = trace_id or str(uuid.uuid4())
        self.decision_engine = DISCAwareDecisionEngine()  # Use DISC-aware version
        self.disc_engine = DISCAutonomousEngine()
        
        logger.info(f"DISC-Aware Autonomous Engine initialized (trace: {self.trace_id})")
        logger.info(f"Profile: {self.disc_engine.my_profile.profile_type} - compensations active")
    
    def make_autonomous_decisions(self, metrics: SystemMetrics) -> List[DISCCompensatedDecision]:
        """Generate DISC-compensated autonomous decisions"""
        logger.info("Making DISC-compensated autonomous decisions...")
        
        # Get compensated decisions
        decisions = self.decision_engine.analyze_and_decide(metrics)
        
        # Log with compensation details
        logger.info(f"Generated {len(decisions)} compensated decisions")
        for decision in decisions:
            logger.info(f"  [{decision.priority}] {decision.type.value}: {decision.human_friendly_summary}")
            if hasattr(decision, 'alternative_approaches') and decision.alternative_approaches:
                logger.info(f"    Alternatives: {', '.join(decision.alternative_approaches)}")
        
        return decisions
    
    def execute_decisions(self, decisions: List[Decision], max_per_cycle: int = 4) -> Dict[str, Any]:
        """Execute with adjusted limits (less perfectionist)"""
        # Increase max per cycle (action bias)
        return super().execute_decisions(decisions, max_per_cycle)
    
    def _execute_decision(self, decision: Decision) -> Dict[str, Any]:
        """Execute with DISC awareness"""
        result = super()._execute_decision(decision)
        
        # Add compensation metadata
        if isinstance(decision, DISCCompensatedDecision):
            result["compensations_applied"] = decision.compensation_applied
            result["had_alternatives"] = len(decision.alternative_approaches) > 0
        
        return result
    
    def run_cycle(self) -> Dict[str, Any]:
        """Run cycle with DISC compensation tracking"""
        logger.info(f"Starting DISC-aware autonomous cycle (trace: {self.trace_id})")
        
        try:
            # 1. Analyze system state
            metrics = self.analyze_system_state()
            
            # 2. Make DISC-compensated decisions
            decisions = self.make_autonomous_decisions(metrics)
            
            # 3. Execute with compensation
            execution_results = self.execute_decisions(decisions)
            
            # 4. Track compensation effectiveness
            compensation_stats = self._calculate_compensation_stats(decisions)
            
            # 5. Return enhanced cycle summary
            cycle_result = {
                "trace_id": self.trace_id,
                "timestamp": datetime.now().isoformat(),
                "disc_profile": self.disc_engine.my_profile.profile_type,
                "metrics": asdict(metrics),
                "decisions_generated": len(decisions),
                "execution_results": execution_results,
                "compensation_stats": compensation_stats
            }
            
            # Quick summary (counter over-communication)
            logger.success(f"✅ Cycle done: {len(decisions)} decisions, "
                         f"{compensation_stats['total_compensations']} compensations applied")
            
            return cycle_result
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            # Pragmatic error handling (not perfectionist)
            return {
                "trace_id": self.trace_id,
                "error": str(e),
                "suggestion": "No worries, we'll try again next cycle",
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_compensation_stats(self, decisions: List[DISCCompensatedDecision]) -> Dict[str, Any]:
        """Calculate compensation effectiveness stats"""
        total_compensations = sum(len(d.compensation_applied) for d in decisions if hasattr(d, 'compensation_applied'))
        
        compensation_types = {}
        for decision in decisions:
            if hasattr(decision, 'compensation_applied'):
                for comp in decision.compensation_applied:
                    compensation_types[comp] = compensation_types.get(comp, 0) + 1
        
        return {
            "total_compensations": total_compensations,
            "compensation_types": compensation_types,
            "avg_alternatives": sum(len(d.alternative_approaches) for d in decisions if hasattr(d, 'alternative_approaches')) / max(len(decisions), 1)
        }
    
    def explain_decision(self, decision: DISCCompensatedDecision) -> str:
        """Explain decision in human-friendly terms"""
        explanation = f"""
🎯 Decision: {decision.human_friendly_summary}

📊 Why: {decision.original_description}

⚡ Action: {decision.type.value} with confidence {decision.confidence:.0%}

🔄 Alternatives considered:
{chr(10).join(f'  • {alt}' for alt in decision.alternative_approaches)}

⚠️ Risk: {decision.risk_assessment}

🧠 DISC compensations applied: {', '.join(decision.compensation_applied)}
"""
        return explanation