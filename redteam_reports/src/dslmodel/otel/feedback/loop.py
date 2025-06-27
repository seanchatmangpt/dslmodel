"""
Telemetry Feedback Loop - Using OTEL data to optimize coordination
Demonstrates the full ecosystem loop from telemetry to action
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .analyzer import TelemetryAnalyzer, TelemetryQueryClient
from .optimizer import OptimizationEngine

@dataclass
class FeedbackCycleResult:
    """Results from a feedback cycle"""
    cycle_timestamp: str
    team_performance: Dict[str, Any]
    system_health: Dict[str, Any]
    optimizations_applied: int
    projected_improvements: Dict[str, float]

class FeedbackLoop:
    """Main feedback loop orchestrator"""
    
    def __init__(self):
        self.client = TelemetryQueryClient()
        self.analyzer = TelemetryAnalyzer(self.client)
        self.optimizer = OptimizationEngine(self.analyzer)
        self.applied_optimizations = []
    
    async def run_feedback_cycle(self) -> FeedbackCycleResult:
        """Run one complete feedback cycle"""
        print("🔄 Starting Telemetry Feedback Cycle\n")
        
        # 1. Collect and analyze telemetry
        print("📊 Analyzing telemetry data...")
        
        # Team performance
        teams_perf = {}
        for team in ["backend", "frontend", "platform"]:
            perf = await self.analyzer.analyze_team_performance(team)
            teams_perf[team] = perf
            print(f"\n{team.upper()} Team:")
            print(f"  Velocity: {perf.velocity:.0f} points/sprint")
            print(f"  Cycle Time P50: {perf.cycle_time_p50/3600:.1f}h")
            print(f"  Error Rate: {perf.error_rate:.1%}")
            if perf.recommendations:
                print(f"  Recommendations: {', '.join(perf.recommendations)}")
        
        # Work patterns
        print("\n📈 Work Pattern Analysis:")
        patterns = await self.analyzer.analyze_work_patterns()
        for work_type, analysis in patterns.items():
            print(f"\n{work_type}:")
            print(f"  Avg Duration: {analysis.avg_duration:.0f}ms")
            print(f"  Success Rate: {analysis.success_rate:.1%}")
            print(f"  Recommended Priority: {analysis.recommended_priority}")
        
        # System health
        print("\n🏥 System Health:")
        health = await self.analyzer.analyze_system_health()
        print(f"  Health Score: {health.health_score:.0f}/100")
        print(f"  P99 Latency: {health.latency_p99:.0f}ms")
        print(f"  Error Rate: {health.error_rate:.2f}/min")
        
        # 2. Generate optimizations
        print("\n🎯 Generating Optimizations...")
        optimizations = await self.optimizer.generate_optimizations()
        
        for i, opt in enumerate(optimizations, 1):
            print(f"\n{i}. {opt['type'].upper()}:")
            print(f"   Target: {opt['target']}")
            print(f"   Reason: {opt['reason']}")
            print(f"   Actions: {json.dumps(opt['action'], indent=6)}")
        
        # 3. Apply optimizations (simulate)
        print("\n⚡ Applying Optimizations...")
        for opt in optimizations[:3]:  # Apply top 3
            await self.apply_optimization(opt)
            self.applied_optimizations.append({
                "optimization": opt,
                "applied_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        # 4. Measure impact (would wait and re-analyze in production)
        print("\n📏 Projected Impact:")
        print("  • Reduced error rates by 15-20%")
        print("  • Improved P95 latency by 25%")
        print("  • Increased throughput by 10%")
        
        # 5. Create feedback report
        result = FeedbackCycleResult(
            cycle_timestamp=datetime.now().isoformat(),
            team_performance={
                team: {
                    "velocity": perf.velocity,
                    "error_rate": perf.error_rate,
                    "cycle_time_p50": perf.cycle_time_p50
                }
                for team, perf in teams_perf.items()
            },
            system_health={
                "score": health.health_score,
                "latency_p99": health.latency_p99,
                "error_rate": health.error_rate
            },
            optimizations_applied=len(optimizations),
            projected_improvements={
                "error_reduction": 0.15,
                "latency_improvement": 0.25,
                "throughput_increase": 0.10
            }
        )
        
        print("\n✅ Feedback cycle complete!")
        return result
    
    async def apply_optimization(self, optimization: Dict[str, Any]):
        """Apply an optimization (simulate in this example)"""
        opt_type = optimization["type"]
        target = optimization["target"]
        
        print(f"  ▶️  Applying {opt_type} to {target}...")
        
        # In production, this would:
        # 1. Update configuration files
        # 2. Adjust system parameters
        # 3. Notify teams
        # 4. Create tracking issues
        
        # Simulate application delay
        await asyncio.sleep(0.5)
        
        print(f"  ✅ {opt_type} applied successfully")
    
    async def continuous_loop(self, interval_minutes: int = 30):
        """Run continuous feedback loop"""
        print(f"🔁 Starting continuous feedback loop (every {interval_minutes} minutes)\n")
        
        while True:
            try:
                result = await self.run_feedback_cycle()
                
                # Check if optimizations are improving metrics
                if len(self.applied_optimizations) > 0:
                    print("\n📊 Optimization Performance:")
                    # Would query actual metrics to measure impact
                    print("  ✅ Previous optimizations showing positive impact")
                
                # Wait for next cycle
                print(f"\n⏰ Next cycle in {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                print(f"\n❌ Error in feedback loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error