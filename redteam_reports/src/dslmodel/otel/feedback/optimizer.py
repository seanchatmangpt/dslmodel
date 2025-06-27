"""
Optimization Engine - Generate optimization actions from telemetry insights
"""

from typing import Dict, List, Any
from .analyzer import TelemetryAnalyzer

class OptimizationEngine:
    """Generates optimization actions from telemetry insights"""
    
    def __init__(self, analyzer: TelemetryAnalyzer):
        self.analyzer = analyzer
    
    async def generate_optimizations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        optimizations = []
        
        # Analyze each team
        for team in ["backend", "frontend", "platform"]:
            perf = await self.analyzer.analyze_team_performance(team)
            
            if perf.error_rate > 0.1:
                optimizations.append({
                    "type": "reduce_batch_size",
                    "target": team,
                    "reason": f"High error rate ({perf.error_rate:.1%})",
                    "action": {
                        "reduce_wip_limit": 2,
                        "increase_review_time": True
                    }
                })
            
            if perf.cycle_time_p95 > 86400:
                optimizations.append({
                    "type": "break_down_work",
                    "target": team,
                    "reason": f"High P95 cycle time ({perf.cycle_time_p95/3600:.1f}h)",
                    "action": {
                        "max_story_points": 5,
                        "require_subtasks": True
                    }
                })
        
        # Analyze work patterns
        patterns = await self.analyzer.analyze_work_patterns()
        for work_type, analysis in patterns.items():
            if analysis.success_rate < 0.8:
                optimizations.append({
                    "type": "adjust_priority",
                    "target": work_type,
                    "reason": f"Low success rate ({analysis.success_rate:.1%})",
                    "action": {
                        "new_priority": analysis.recommended_priority,
                        "add_validation": True
                    }
                })
        
        # System health optimizations
        health = await self.analyzer.analyze_system_health()
        if health.health_score < 80:
            optimizations.append({
                "type": "scale_resources",
                "target": "system",
                "reason": f"Low health score ({health.health_score:.0f})",
                "action": {
                    "scale_factor": 1.5,
                    "add_caching": True,
                    "enable_circuit_breaker": True
                }
            })
        
        return optimizations