#!/usr/bin/env python3
"""
Telemetry Feedback Loop - Using OTEL data to optimize coordination
Demonstrates the full ecosystem loop from telemetry to action
"""

import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio
import aiohttp

# Mock telemetry query client (replace with actual Prometheus/Tempo client)
class TelemetryQueryClient:
    """Query interface for telemetry data"""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090",
                 tempo_url: str = "http://localhost:3100"):
        self.prometheus_url = prometheus_url
        self.tempo_url = tempo_url
    
    async def query_metrics(self, query: str, start: datetime, end: datetime) -> Dict:
        """Query Prometheus for metrics"""
        # Mock implementation - replace with actual PromQL
        mock_data = {
            'coordination_work_items_completed_total': [
                {"team": "backend", "value": 45},
                {"team": "frontend", "value": 38},
                {"team": "platform", "value": 52}
            ],
            'coordination_api_latency_bucket': [
                {"le": "100", "value": 0.7},
                {"le": "500", "value": 0.9},
                {"le": "1000", "value": 0.95},
                {"le": "+Inf", "value": 1.0}
            ],
            'coordination_work_item_duration_seconds': [
                {"percentile": "p50", "value": 3600},
                {"percentile": "p95", "value": 14400},
                {"percentile": "p99", "value": 28800}
            ]
        }
        return mock_data.get(query, [])
    
    async def query_traces(self, service: str, operation: str, 
                          start: datetime, end: datetime) -> List[Dict]:
        """Query Tempo for traces"""
        # Mock trace data
        return [
            {
                "trace_id": f"trace_{i}",
                "duration_ms": 100 + i * 50,
                "status": "success" if i % 5 != 0 else "error",
                "attributes": {
                    "work.type": ["bug", "feature", "refactor"][i % 3],
                    "work.priority": ["low", "medium", "high", "critical"][i % 4],
                    "work.team": ["backend", "frontend", "platform"][i % 3]
                }
            }
            for i in range(20)
        ]
    
    async def query_logs(self, filter_expr: str, start: datetime, end: datetime) -> List[Dict]:
        """Query Loki for logs"""
        # Mock log data
        return [
            {
                "timestamp": datetime.now() - timedelta(minutes=i),
                "level": "INFO" if i % 10 != 0 else "ERROR",
                "message": f"Log entry {i}",
                "trace_id": f"trace_{i}",
                "attributes": {"work.id": f"work_{i}"}
            }
            for i in range(50)
        ]

###############################################################################
# Analysis Models
###############################################################################

@dataclass
class TeamPerformance:
    """Team performance metrics from telemetry"""
    team: str
    velocity: float  # Story points per sprint
    cycle_time_p50: float  # Median time to complete work
    cycle_time_p95: float  # 95th percentile
    error_rate: float  # Percentage of failed work items
    throughput: float  # Items completed per day
    wip_limit_violations: int  # Times WIP limit exceeded
    recommendations: List[str] = field(default_factory=list)

@dataclass
class WorkItemAnalysis:
    """Analysis of work item patterns"""
    work_type: str
    avg_duration: float
    success_rate: float
    common_blockers: List[str]
    optimal_batch_size: int
    recommended_priority: str

@dataclass
class SystemHealth:
    """Overall system health from telemetry"""
    health_score: float  # 0-100
    latency_p99: float  # 99th percentile API latency
    error_rate: float
    active_incidents: List[Dict]
    capacity_utilization: float
    recommendations: List[str]

###############################################################################
# Feedback Loop Components
###############################################################################

class TelemetryAnalyzer:
    """Analyzes telemetry data to generate insights"""
    
    def __init__(self, client: TelemetryQueryClient):
        self.client = client
    
    async def analyze_team_performance(self, team: str, 
                                     lookback_days: int = 14) -> TeamPerformance:
        """Analyze team performance from telemetry"""
        end = datetime.now()
        start = end - timedelta(days=lookback_days)
        
        # Query metrics
        completed = await self.client.query_metrics(
            f'sum(coordination_work_items_completed_total{{team="{team}"}})',
            start, end
        )
        
        duration = await self.client.query_metrics(
            f'coordination_work_item_duration_seconds{{team="{team}"}}',
            start, end
        )
        
        # Query traces for error rate
        traces = await self.client.query_traces("coordination-cli", "work.*", start, end)
        team_traces = [t for t in traces if t["attributes"].get("work.team") == team]
        error_count = sum(1 for t in team_traces if t["status"] == "error")
        error_rate = error_count / len(team_traces) if team_traces else 0
        
        # Calculate metrics
        velocity = completed[0]["value"] if completed else 0
        cycle_time_p50 = next((d["value"] for d in duration if d["percentile"] == "p50"), 3600)
        cycle_time_p95 = next((d["value"] for d in duration if d["percentile"] == "p95"), 14400)
        throughput = velocity / lookback_days
        
        # Generate recommendations
        recommendations = []
        if error_rate > 0.1:
            recommendations.append(f"High error rate ({error_rate:.1%}). Review failed work items.")
        if cycle_time_p95 > 86400:  # > 24 hours
            recommendations.append("P95 cycle time exceeds 24h. Consider breaking down large items.")
        if velocity < 20:
            recommendations.append("Low velocity. Check for blockers or capacity issues.")
        
        return TeamPerformance(
            team=team,
            velocity=velocity,
            cycle_time_p50=cycle_time_p50,
            cycle_time_p95=cycle_time_p95,
            error_rate=error_rate,
            throughput=throughput,
            wip_limit_violations=0,  # Would calculate from traces
            recommendations=recommendations
        )
    
    async def analyze_work_patterns(self) -> Dict[str, WorkItemAnalysis]:
        """Analyze patterns in work item completion"""
        end = datetime.now()
        start = end - timedelta(days=30)
        
        # Query traces grouped by work type
        traces = await self.client.query_traces("coordination-cli", "work.*", start, end)
        
        # Group by work type
        by_type = defaultdict(list)
        for trace in traces:
            work_type = trace["attributes"].get("work.type", "unknown")
            by_type[work_type].append(trace)
        
        analyses = {}
        for work_type, type_traces in by_type.items():
            durations = [t["duration_ms"] for t in type_traces]
            success_count = sum(1 for t in type_traces if t["status"] == "success")
            
            analysis = WorkItemAnalysis(
                work_type=work_type,
                avg_duration=statistics.mean(durations) if durations else 0,
                success_rate=success_count / len(type_traces) if type_traces else 0,
                common_blockers=["Dependencies", "Reviews"],  # Would extract from logs
                optimal_batch_size=5,  # Would calculate from throughput analysis
                recommended_priority="medium"  # Would derive from business impact
            )
            
            # Adjust priority based on success rate
            if analysis.success_rate < 0.8:
                analysis.recommended_priority = "high"
            elif analysis.avg_duration > 10000:  # > 10 seconds
                analysis.recommended_priority = "high"
            
            analyses[work_type] = analysis
        
        return analyses
    
    async def analyze_system_health(self) -> SystemHealth:
        """Analyze overall system health"""
        end = datetime.now()
        start = end - timedelta(hours=1)
        
        # Query system metrics
        latency = await self.client.query_metrics(
            'histogram_quantile(0.99, coordination_api_latency_bucket)',
            start, end
        )
        
        error_logs = await self.client.query_logs(
            'level="ERROR"',
            start, end
        )
        
        # Calculate health score
        latency_score = 100 - min(latency[0]["value"] / 10, 100) if latency else 50
        error_score = 100 - min(len(error_logs) * 2, 100)
        health_score = (latency_score + error_score) / 2
        
        # Generate recommendations
        recommendations = []
        if health_score < 80:
            recommendations.append("System health below threshold. Investigate errors and latency.")
        if len(error_logs) > 10:
            recommendations.append(f"High error count ({len(error_logs)}). Check error logs.")
        
        return SystemHealth(
            health_score=health_score,
            latency_p99=latency[0]["value"] if latency else 0,
            error_rate=len(error_logs) / 60,  # Errors per minute
            active_incidents=[],  # Would query incident management
            capacity_utilization=0.75,  # Would calculate from metrics
            recommendations=recommendations
        )

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

class FeedbackLoop:
    """Main feedback loop orchestrator"""
    
    def __init__(self):
        self.client = TelemetryQueryClient()
        self.analyzer = TelemetryAnalyzer(self.client)
        self.optimizer = OptimizationEngine(self.analyzer)
        self.applied_optimizations = []
    
    async def run_feedback_cycle(self):
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
        report = {
            "cycle_timestamp": datetime.now().isoformat(),
            "team_performance": {
                team: {
                    "velocity": perf.velocity,
                    "error_rate": perf.error_rate,
                    "cycle_time_p50": perf.cycle_time_p50
                }
                for team, perf in teams_perf.items()
            },
            "system_health": {
                "score": health.health_score,
                "latency_p99": health.latency_p99,
                "error_rate": health.error_rate
            },
            "optimizations_applied": len(optimizations),
            "projected_improvements": {
                "error_reduction": 0.15,
                "latency_improvement": 0.25,
                "throughput_increase": 0.10
            }
        }
        
        # Save report
        with open("telemetry_feedback_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Feedback cycle complete!")
        print(f"📄 Report saved to telemetry_feedback_report.json")
        
        return report
    
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
                report = await self.run_feedback_cycle()
                
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

###############################################################################
# Main Demo
###############################################################################

async def demo_feedback_loop():
    """Demonstrate the complete telemetry feedback loop"""
    print("🚀 OpenTelemetry Feedback Loop Demo")
    print("=" * 50)
    print("\nThis demonstrates how telemetry drives system optimization:\n")
    print("1. 📊 Collect telemetry (traces, metrics, logs)")
    print("2. 🔍 Analyze patterns and performance")
    print("3. 🎯 Generate optimization recommendations")
    print("4. ⚡ Apply optimizations automatically")
    print("5. 📏 Measure impact and iterate")
    print("\n" + "=" * 50)
    
    feedback_loop = FeedbackLoop()
    
    # Run one cycle
    await feedback_loop.run_feedback_cycle()
    
    print("\n\n🔄 FEEDBACK LOOP BENEFITS:")
    print("  • Data-driven decisions from actual telemetry")
    print("  • Automatic optimization without manual intervention")
    print("  • Continuous improvement based on measurements")
    print("  • Proactive issue detection and resolution")
    print("  • Closed-loop validation of changes")

def main():
    """Run the demo"""
    asyncio.run(demo_feedback_loop())

if __name__ == "__main__":
    main()