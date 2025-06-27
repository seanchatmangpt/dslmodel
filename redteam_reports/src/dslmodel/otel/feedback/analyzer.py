"""
Telemetry Analysis - Extract insights from OTEL data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

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