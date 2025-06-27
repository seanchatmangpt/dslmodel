"""
80/20 Capability Gap Analysis for DSLModel
Identifies the 20% of missing capabilities that provide 80% of the value.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ImpactLevel(Enum):
    """Impact levels for capability assessment."""
    CRITICAL = "critical"      # 30-40% of total value
    HIGH = "high"             # 20-30% of total value  
    MEDIUM = "medium"         # 10-20% of total value
    LOW = "low"               # 5-10% of total value


class EffortLevel(Enum):
    """Effort levels for implementation."""
    MINIMAL = "minimal"       # 1-2 days
    LOW = "low"              # 3-5 days
    MEDIUM = "medium"        # 1-2 weeks
    HIGH = "high"            # 2-4 weeks


@dataclass
class Capability:
    """Represents a system capability."""
    name: str
    description: str
    impact: ImpactLevel
    effort: EffortLevel
    value_percentage: float
    effort_percentage: float
    dependencies: List[str] = None
    implemented: bool = False


class CapabilityGapAnalysis:
    """Analyzes capability gaps using 80/20 principle."""
    
    def __init__(self):
        self.capabilities = self._define_capabilities()
    
    def _define_capabilities(self) -> List[Capability]:
        """Define all system capabilities and their impact/effort."""
        return [
            # Currently Implemented (✅)
            Capability(
                name="autonomous_decision_engine",
                description="Makes autonomous scaling and coordination decisions",
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                value_percentage=25.0,
                effort_percentage=15.0,
                implemented=True
            ),
            Capability(
                name="e2e_feature_generation", 
                description="Generates complete features from telemetry specs",
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                value_percentage=15.0,
                effort_percentage=8.0,
                implemented=True
            ),
            Capability(
                name="otel_integration",
                description="OpenTelemetry semantic conventions and validation",
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.LOW,
                value_percentage=20.0,
                effort_percentage=5.0,
                implemented=True
            ),
            Capability(
                name="json_output_automation",
                description="Global JSON output for CLI automation",
                impact=ImpactLevel.LOW,
                effort=EffortLevel.MINIMAL,
                value_percentage=5.0,
                effort_percentage=2.0,
                implemented=True
            ),
            
            # High-Impact Missing Capabilities (❌)
            Capability(
                name="realtime_telemetry_processing",
                description="Live telemetry ingestion and stream processing",
                impact=ImpactLevel.CRITICAL,
                effort=EffortLevel.MEDIUM,
                value_percentage=35.0,
                effort_percentage=12.0,
                dependencies=["otel_integration"],
                implemented=False
            ),
            Capability(
                name="auto_remediation_actions",
                description="Automatic issue remediation and self-healing",
                impact=ImpactLevel.CRITICAL,
                effort=EffortLevel.LOW,
                value_percentage=30.0,
                effort_percentage=8.0,
                dependencies=["autonomous_decision_engine", "realtime_telemetry_processing"],
                implemented=False
            ),
            Capability(
                name="system_topology_discovery",
                description="Automatic discovery of service dependencies",
                impact=ImpactLevel.HIGH,
                effort=EffortLevel.MEDIUM,
                value_percentage=20.0,
                effort_percentage=10.0,
                dependencies=["realtime_telemetry_processing"],
                implemented=False
            ),
            Capability(
                name="predictive_analytics",
                description="Pattern recognition and predictive scaling",
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.HIGH,
                value_percentage=15.0,
                effort_percentage=20.0,
                dependencies=["realtime_telemetry_processing", "system_topology_discovery"],
                implemented=False
            ),
            Capability(
                name="external_system_integration",
                description="Integration with Prometheus, Grafana, K8s",
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.MEDIUM,
                value_percentage=12.0,
                effort_percentage=15.0,
                dependencies=["realtime_telemetry_processing"],
                implemented=False
            ),
            Capability(
                name="security_telemetry",
                description="Security-focused telemetry and compliance monitoring",
                impact=ImpactLevel.MEDIUM,
                effort=EffortLevel.LOW,
                value_percentage=10.0,
                effort_percentage=5.0,
                dependencies=["otel_integration"],
                implemented=False
            ),
            Capability(
                name="multi_environment_coordination",
                description="Cross-environment system coordination",
                impact=ImpactLevel.LOW,
                effort=EffortLevel.HIGH,
                value_percentage=8.0,
                effort_percentage=25.0,
                dependencies=["autonomous_decision_engine", "system_topology_discovery"],
                implemented=False
            )
        ]
    
    def get_8020_priorities(self) -> List[Capability]:
        """Get capabilities that provide 80% value with 20% effort."""
        missing_capabilities = [c for c in self.capabilities if not c.implemented]
        
        # Sort by value/effort ratio (bang for buck)
        def value_effort_ratio(cap: Capability) -> float:
            return cap.value_percentage / max(cap.effort_percentage, 1.0)
        
        sorted_caps = sorted(missing_capabilities, key=value_effort_ratio, reverse=True)
        
        # Select top capabilities that sum to ~80% value with ~20% effort
        total_value = 0
        total_effort = 0
        priority_caps = []
        
        for cap in sorted_caps:
            if total_effort + cap.effort_percentage <= 25.0:  # Stay within ~20% effort
                priority_caps.append(cap)
                total_value += cap.value_percentage
                total_effort += cap.effort_percentage
                
                if total_value >= 80.0:  # Reached 80% value
                    break
        
        return priority_caps
    
    def get_implementation_order(self) -> List[Capability]:
        """Get capabilities in optimal implementation order (considering dependencies)."""
        priority_caps = self.get_8020_priorities()
        
        # Topological sort considering dependencies
        implemented_names = {c.name for c in self.capabilities if c.implemented}
        ordered = []
        remaining = priority_caps.copy()
        
        while remaining:
            # Find capabilities with no unmet dependencies
            ready = []
            for cap in remaining:
                if not cap.dependencies:
                    ready.append(cap)
                else:
                    deps_met = all(dep in implemented_names or 
                                 any(o.name == dep for o in ordered) 
                                 for dep in cap.dependencies)
                    if deps_met:
                        ready.append(cap)
            
            if not ready:
                # Break circular dependencies by taking highest value
                ready = [max(remaining, key=lambda c: c.value_percentage)]
            
            # Sort ready capabilities by value and take the best
            ready.sort(key=lambda c: c.value_percentage, reverse=True)
            next_cap = ready[0]
            
            ordered.append(next_cap)
            remaining.remove(next_cap)
        
        return ordered
    
    def get_gap_analysis_report(self) -> Dict[str, any]:
        """Generate comprehensive gap analysis report."""
        total_value = sum(c.value_percentage for c in self.capabilities if not c.implemented)
        implemented_value = sum(c.value_percentage for c in self.capabilities if c.implemented)
        
        priority_caps = self.get_8020_priorities()
        priority_value = sum(c.value_percentage for c in priority_caps)
        priority_effort = sum(c.effort_percentage for c in priority_caps)
        
        return {
            "summary": {
                "total_capabilities": len(self.capabilities),
                "implemented_capabilities": len([c for c in self.capabilities if c.implemented]),
                "missing_capabilities": len([c for c in self.capabilities if not c.implemented]),
                "implemented_value_percentage": implemented_value,
                "missing_value_percentage": total_value,
                "system_completeness": implemented_value / (implemented_value + total_value) * 100
            },
            "8020_analysis": {
                "priority_capabilities": len(priority_caps),
                "priority_value_percentage": priority_value,
                "priority_effort_percentage": priority_effort,
                "value_effort_ratio": priority_value / max(priority_effort, 1.0),
                "efficiency_score": priority_value / priority_effort if priority_effort > 0 else float('inf')
            },
            "implementation_roadmap": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "impact": cap.impact.value,
                    "effort": cap.effort.value,
                    "value_percentage": cap.value_percentage,
                    "effort_percentage": cap.effort_percentage,
                    "dependencies": cap.dependencies or []
                }
                for cap in self.get_implementation_order()
            ],
            "quick_wins": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "value_percentage": cap.value_percentage,
                    "effort_percentage": cap.effort_percentage
                }
                for cap in priority_caps 
                if cap.effort == EffortLevel.MINIMAL or cap.effort == EffortLevel.LOW
            ]
        }


def analyze_capability_gaps() -> Dict[str, any]:
    """Run 80/20 capability gap analysis."""
    analyzer = CapabilityGapAnalysis()
    return analyzer.get_gap_analysis_report()


if __name__ == "__main__":
    import json
    
    analysis = analyze_capability_gaps()
    print(json.dumps(analysis, indent=2))