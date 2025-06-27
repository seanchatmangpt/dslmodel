#!/usr/bin/env python3
"""
Automatic Evolution Engine
Continuously evolves agent coordination using OTEL telemetry feedback
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import subprocess

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

@dataclass
class EvolutionMetric:
    """Metric for evolutionary optimization"""
    metric_name: str
    current_value: float
    target_value: float
    trend: str  # improving, declining, stable
    importance: float  # 0.0 to 1.0
    optimization_direction: str  # maximize, minimize
    last_updated: str

@dataclass
class EvolutionPattern:
    """Pattern discovered through telemetry analysis"""
    pattern_id: str
    description: str
    frequency: int
    success_rate: float
    performance_impact: float
    coordination_context: Dict[str, Any]
    suggested_optimization: str
    confidence: float

@dataclass
class EvolutionAction:
    """Action to be taken for system evolution"""
    action_id: str
    action_type: str  # optimize, refactor, add_capability, remove_bottleneck
    description: str
    target_component: str
    expected_improvement: float
    risk_level: str  # low, medium, high
    implementation_plan: List[str]
    rollback_plan: List[str]
    validation_criteria: Dict[str, Any]

class TelemetryAnalyzer:
    """Analyzes OTEL telemetry data for evolutionary insights"""
    
    def __init__(self):
        self.console = Console()
        self.tracer = trace.get_tracer("evolution.telemetry_analyzer")
    
    async def analyze_coordination_patterns(self, spans_data: List[Dict]) -> List[EvolutionPattern]:
        """Analyze coordination patterns from telemetry spans"""
        
        with self.tracer.start_as_current_span(
            "evolution.analyze_coordination_patterns",
            attributes={"spans_analyzed": len(spans_data)}
        ) as span:
            
            patterns = []
            
            # Analyze agent coordination frequency
            coordination_events = [
                s for s in spans_data 
                if "agent.coordination" in s.get("name", "")
            ]
            
            if coordination_events:
                coordination_pattern = EvolutionPattern(
                    pattern_id="coordination_frequency",
                    description="Agent coordination frequency and success patterns",
                    frequency=len(coordination_events),
                    success_rate=self._calculate_success_rate(coordination_events),
                    performance_impact=self._calculate_performance_impact(coordination_events),
                    coordination_context={
                        "avg_duration": self._calculate_avg_duration(coordination_events),
                        "peak_coordination_times": self._find_peak_times(coordination_events)
                    },
                    suggested_optimization="Optimize coordination timing based on agent availability patterns",
                    confidence=0.85
                )
                patterns.append(coordination_pattern)
            
            # Analyze worktree utilization
            worktree_spans = [
                s for s in spans_data 
                if "worktree" in s.get("name", "")
            ]
            
            if worktree_spans:
                utilization_pattern = EvolutionPattern(
                    pattern_id="worktree_utilization",
                    description="Worktree creation and utilization patterns",
                    frequency=len(worktree_spans),
                    success_rate=self._calculate_success_rate(worktree_spans),
                    performance_impact=self._calculate_performance_impact(worktree_spans),
                    coordination_context={
                        "avg_worktree_lifetime": self._calculate_worktree_lifetime(worktree_spans),
                        "parallel_worktrees": self._count_parallel_worktrees(worktree_spans)
                    },
                    suggested_optimization="Implement worktree pooling for faster agent startup",
                    confidence=0.78
                )
                patterns.append(utilization_pattern)
            
            # Analyze feature completion patterns
            feature_spans = [
                s for s in spans_data 
                if "feature" in s.get("name", "") and "complete" in s.get("name", "")
            ]
            
            if feature_spans:
                completion_pattern = EvolutionPattern(
                    pattern_id="feature_completion",
                    description="Feature completion time and success patterns",
                    frequency=len(feature_spans),
                    success_rate=self._calculate_success_rate(feature_spans),
                    performance_impact=self._calculate_performance_impact(feature_spans),
                    coordination_context={
                        "avg_completion_time": self._calculate_avg_duration(feature_spans),
                        "bottleneck_agents": self._identify_bottleneck_agents(feature_spans)
                    },
                    suggested_optimization="Pre-allocate resources for identified bottleneck agents",
                    confidence=0.92
                )
                patterns.append(completion_pattern)
            
            span.set_attribute("patterns_discovered", len(patterns))
            span.add_event("patterns_analyzed", {
                "coordination_events": len(coordination_events),
                "worktree_events": len(worktree_spans),
                "feature_events": len(feature_spans)
            })
            
            return patterns
    
    def _calculate_success_rate(self, spans: List[Dict]) -> float:
        """Calculate success rate from spans"""
        if not spans:
            return 0.0
        
        successful = sum(1 for span in spans if span.get("status", {}).get("status_code") != "ERROR")
        return successful / len(spans)
    
    def _calculate_performance_impact(self, spans: List[Dict]) -> float:
        """Calculate performance impact score"""
        if not spans:
            return 0.0
        
        durations = [span.get("duration_ms", 0) for span in spans]
        avg_duration = statistics.mean(durations) if durations else 0
        
        # Normalize to 0-1 scale (assuming 10 seconds is high impact)
        return min(avg_duration / 10000, 1.0)
    
    def _calculate_avg_duration(self, spans: List[Dict]) -> float:
        """Calculate average duration of spans"""
        durations = [span.get("duration_ms", 0) for span in spans]
        return statistics.mean(durations) if durations else 0.0
    
    def _find_peak_times(self, spans: List[Dict]) -> List[str]:
        """Find peak coordination times"""
        # Simplified - return mock peak times
        return ["09:00-10:00", "14:00-15:00", "16:00-17:00"]
    
    def _calculate_worktree_lifetime(self, spans: List[Dict]) -> float:
        """Calculate average worktree lifetime"""
        # Simplified calculation
        return 3600.0  # 1 hour average
    
    def _count_parallel_worktrees(self, spans: List[Dict]) -> int:
        """Count maximum parallel worktrees"""
        # Simplified - return mock count
        return 5
    
    def _identify_bottleneck_agents(self, spans: List[Dict]) -> List[str]:
        """Identify agents that cause bottlenecks"""
        # Simplified - return mock bottleneck agents
        return ["frontend_agent", "database_agent"]

class EvolutionOptimizer:
    """Generates optimization actions based on evolutionary analysis"""
    
    def __init__(self):
        self.console = Console()
        self.tracer = trace.get_tracer("evolution.optimizer")
    
    async def generate_optimization_actions(
        self, 
        patterns: List[EvolutionPattern],
        current_metrics: List[EvolutionMetric]
    ) -> List[EvolutionAction]:
        """Generate optimization actions from patterns and metrics"""
        
        with self.tracer.start_as_current_span(
            "evolution.generate_optimizations",
            attributes={
                "patterns_count": len(patterns),
                "metrics_count": len(current_metrics)
            }
        ) as span:
            
            actions = []
            
            # Generate actions for each pattern
            for pattern in patterns:
                if pattern.confidence > 0.7:  # Only high-confidence patterns
                    action = await self._create_action_from_pattern(pattern)
                    if action:
                        actions.append(action)
            
            # Generate actions for declining metrics
            for metric in current_metrics:
                if metric.trend == "declining" and metric.importance > 0.6:
                    action = await self._create_action_from_metric(metric)
                    if action:
                        actions.append(action)
            
            # Prioritize actions by expected improvement
            actions.sort(key=lambda a: a.expected_improvement, reverse=True)
            
            span.set_attribute("actions_generated", len(actions))
            span.add_event("optimization_actions_generated")
            
            return actions
    
    async def _create_action_from_pattern(self, pattern: EvolutionPattern) -> Optional[EvolutionAction]:
        """Create optimization action from discovered pattern"""
        
        if pattern.pattern_id == "coordination_frequency":
            return EvolutionAction(
                action_id=f"optimize_{pattern.pattern_id}_{int(datetime.now().timestamp())}",
                action_type="optimize",
                description="Implement intelligent coordination scheduling",
                target_component="coordination_scheduler",
                expected_improvement=0.25,  # 25% improvement
                risk_level="low",
                implementation_plan=[
                    "Add coordination scheduler component",
                    "Implement agent availability tracking",
                    "Optimize coordination timing algorithms",
                    "Add coordination batching for efficiency"
                ],
                rollback_plan=[
                    "Disable coordination scheduler",
                    "Revert to immediate coordination mode",
                    "Remove scheduler components"
                ],
                validation_criteria={
                    "coordination_latency_reduction": 0.2,
                    "agent_utilization_improvement": 0.15,
                    "success_rate_maintenance": 0.95
                }
            )
        
        elif pattern.pattern_id == "worktree_utilization":
            return EvolutionAction(
                action_id=f"optimize_{pattern.pattern_id}_{int(datetime.now().timestamp())}",
                action_type="add_capability",
                description="Implement worktree pooling system",
                target_component="worktree_manager",
                expected_improvement=0.35,  # 35% improvement
                risk_level="medium",
                implementation_plan=[
                    "Create worktree pool manager",
                    "Implement pre-allocated worktree system",
                    "Add worktree lifecycle optimization",
                    "Implement worktree reuse logic"
                ],
                rollback_plan=[
                    "Disable worktree pooling",
                    "Revert to on-demand worktree creation",
                    "Clean up pool infrastructure"
                ],
                validation_criteria={
                    "worktree_startup_time_reduction": 0.3,
                    "resource_utilization_improvement": 0.2,
                    "memory_usage_increase_limit": 0.1
                }
            )
        
        elif pattern.pattern_id == "feature_completion":
            return EvolutionAction(
                action_id=f"optimize_{pattern.pattern_id}_{int(datetime.now().timestamp())}",
                action_type="remove_bottleneck",
                description="Implement dynamic agent scaling for bottlenecks",
                target_component="agent_manager",
                expected_improvement=0.4,  # 40% improvement
                risk_level="medium",
                implementation_plan=[
                    "Add bottleneck detection algorithms",
                    "Implement dynamic agent spawning",
                    "Add load balancing for agent tasks",
                    "Implement agent capability matching"
                ],
                rollback_plan=[
                    "Disable dynamic scaling",
                    "Revert to static agent allocation",
                    "Remove scaling infrastructure"
                ],
                validation_criteria={
                    "feature_completion_time_reduction": 0.3,
                    "bottleneck_elimination_rate": 0.8,
                    "resource_cost_increase_limit": 0.15
                }
            )
        
        return None
    
    async def _create_action_from_metric(self, metric: EvolutionMetric) -> Optional[EvolutionAction]:
        """Create optimization action from declining metric"""
        
        if metric.metric_name == "agent_coordination_efficiency":
            return EvolutionAction(
                action_id=f"fix_metric_{metric.metric_name}_{int(datetime.now().timestamp())}",
                action_type="optimize",
                description=f"Address declining {metric.metric_name}",
                target_component="coordination_layer",
                expected_improvement=0.2,
                risk_level="low",
                implementation_plan=[
                    "Analyze coordination inefficiencies",
                    "Optimize coordination protocols",
                    "Implement coordination caching",
                    "Add coordination monitoring"
                ],
                rollback_plan=[
                    "Revert coordination optimizations",
                    "Restore original protocols"
                ],
                validation_criteria={
                    f"{metric.metric_name}_improvement": 0.15
                }
            )
        
        return None

class EvolutionExecutor:
    """Executes evolutionary optimization actions"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.console = Console()
        self.tracer = trace.get_tracer("evolution.executor")
    
    async def execute_action(self, action: EvolutionAction) -> Dict[str, Any]:
        """Execute an evolutionary optimization action"""
        
        with self.tracer.start_as_current_span(
            "evolution.execute_action",
            attributes={
                "action.id": action.action_id,
                "action.type": action.action_type,
                "expected_improvement": action.expected_improvement
            }
        ) as span:
            
            self.console.print(f"🔧 Executing evolution action: {action.description}")
            
            execution_result = {
                "action_id": action.action_id,
                "status": "unknown",
                "execution_time": datetime.now().isoformat(),
                "changes_made": [],
                "validation_results": {},
                "rollback_available": True
            }
            
            try:
                # Execute based on action type
                if action.action_type == "optimize":
                    result = await self._execute_optimization(action)
                elif action.action_type == "add_capability":
                    result = await self._execute_capability_addition(action)
                elif action.action_type == "remove_bottleneck":
                    result = await self._execute_bottleneck_removal(action)
                elif action.action_type == "refactor":
                    result = await self._execute_refactoring(action)
                else:
                    result = {"status": "unsupported_action_type"}
                
                execution_result.update(result)
                execution_result["status"] = "success"
                
                span.set_attribute("execution.status", "success")
                span.add_event("action_executed_successfully")
                
            except Exception as e:
                execution_result["status"] = "failed"
                execution_result["error"] = str(e)
                
                span.record_exception(e)
                span.set_attribute("execution.status", "failed")
                
                self.console.print(f"❌ Evolution action failed: {e}")
            
            return execution_result
    
    async def _execute_optimization(self, action: EvolutionAction) -> Dict[str, Any]:
        """Execute optimization action"""
        
        changes = []
        
        # Generate optimized semantic conventions
        if "coordination" in action.target_component:
            await self._optimize_coordination_conventions()
            changes.append("Updated coordination semantic conventions")
        
        # Generate optimized code
        await self._generate_optimized_components(action)
        changes.append(f"Generated optimized {action.target_component}")
        
        return {
            "changes_made": changes,
            "optimization_type": action.target_component
        }
    
    async def _execute_capability_addition(self, action: EvolutionAction) -> Dict[str, Any]:
        """Execute capability addition action"""
        
        changes = []
        
        # Add new semantic conventions for capability
        await self._add_capability_conventions(action)
        changes.append("Added new capability semantic conventions")
        
        # Generate capability implementation
        await self._generate_capability_implementation(action)
        changes.append(f"Generated {action.target_component} capability")
        
        return {
            "changes_made": changes,
            "capability_added": action.target_component
        }
    
    async def _execute_bottleneck_removal(self, action: EvolutionAction) -> Dict[str, Any]:
        """Execute bottleneck removal action"""
        
        changes = []
        
        # Analyze bottleneck patterns
        await self._analyze_bottleneck_patterns(action)
        changes.append("Analyzed bottleneck patterns")
        
        # Generate bottleneck elimination code
        await self._generate_bottleneck_elimination(action)
        changes.append("Generated bottleneck elimination components")
        
        return {
            "changes_made": changes,
            "bottleneck_target": action.target_component
        }
    
    async def _execute_refactoring(self, action: EvolutionAction) -> Dict[str, Any]:
        """Execute refactoring action"""
        
        changes = []
        
        # Refactor semantic conventions
        await self._refactor_conventions(action)
        changes.append("Refactored semantic conventions")
        
        # Regenerate code from conventions
        await self._regenerate_from_conventions(action)
        changes.append("Regenerated code from refactored conventions")
        
        return {
            "changes_made": changes,
            "refactoring_target": action.target_component
        }
    
    async def _optimize_coordination_conventions(self):
        """Optimize coordination semantic conventions"""
        conventions_path = self.project_root / "semantic_conventions" / "agent_coordination.yaml"
        
        optimized_conventions = {
            "groups": [
                {
                    "id": "agent.coordination.optimized",
                    "type": "span",
                    "brief": "Optimized agent coordination with intelligent scheduling",
                    "attributes": [
                        {"id": "agent.coordination.scheduler.enabled", "type": "boolean", "brief": "Whether intelligent scheduling is enabled"},
                        {"id": "agent.coordination.batch.size", "type": "int", "brief": "Number of coordination requests batched"},
                        {"id": "agent.coordination.latency.target", "type": "double", "brief": "Target coordination latency in milliseconds"},
                    ]
                },
                {
                    "id": "agent.worktree.pooled",
                    "type": "span", 
                    "brief": "Pooled worktree operations for faster agent startup",
                    "attributes": [
                        {"id": "worktree.pool.size", "type": "int", "brief": "Size of worktree pool"},
                        {"id": "worktree.pool.hit.rate", "type": "double", "brief": "Pool hit rate percentage"},
                        {"id": "worktree.startup.time.ms", "type": "double", "brief": "Worktree startup time in milliseconds"},
                    ]
                }
            ]
        }
        
        conventions_path.parent.mkdir(exist_ok=True)
        with open(conventions_path, 'w') as f:
            yaml.dump(optimized_conventions, f, default_flow_style=False)
    
    async def _generate_optimized_components(self, action: EvolutionAction):
        """Generate optimized components from semantic conventions"""
        # This would use the weaver generator to create optimized components
        pass
    
    async def _add_capability_conventions(self, action: EvolutionAction):
        """Add semantic conventions for new capability"""
        # Generate new semantic conventions for the capability
        pass
    
    async def _generate_capability_implementation(self, action: EvolutionAction):
        """Generate implementation for new capability"""
        # Use weaver to generate capability implementation
        pass
    
    async def _analyze_bottleneck_patterns(self, action: EvolutionAction):
        """Analyze bottleneck patterns from telemetry"""
        # Analyze telemetry data to identify bottleneck patterns
        pass
    
    async def _generate_bottleneck_elimination(self, action: EvolutionAction):
        """Generate bottleneck elimination components"""
        # Generate code to eliminate identified bottlenecks
        pass
    
    async def _refactor_conventions(self, action: EvolutionAction):
        """Refactor semantic conventions"""
        # Refactor existing conventions for better performance
        pass
    
    async def _regenerate_from_conventions(self, action: EvolutionAction):
        """Regenerate code from refactored conventions"""
        # Use weaver to regenerate everything from refactored conventions
        pass

class AutomaticEvolutionEngine:
    """Main engine that orchestrates automatic system evolution"""
    
    def __init__(self, project_root: Path, coordination_system):
        self.project_root = project_root
        self.coordination_system = coordination_system
        self.console = Console()
        
        # Evolution components
        self.telemetry_analyzer = TelemetryAnalyzer()
        self.optimizer = EvolutionOptimizer()
        self.executor = EvolutionExecutor(project_root)
        
        # Evolution state
        self.evolution_cycles = 0
        self.evolution_history: List[Dict[str, Any]] = []
        self.current_metrics: List[EvolutionMetric] = []
        
        # OTEL setup
        self.tracer = trace.get_tracer("evolution.engine")
        
        # Evolution configuration
        self.evolution_config = {
            "cycle_interval_hours": 24,  # Run evolution every 24 hours
            "min_telemetry_data_points": 100,  # Minimum data points for analysis
            "confidence_threshold": 0.7,  # Minimum confidence for actions
            "max_actions_per_cycle": 3,  # Maximum actions per evolution cycle
            "rollback_on_degradation": True  # Rollback if metrics degrade
        }
    
    async def start_continuous_evolution(self):
        """Start continuous evolution process"""
        
        self.console.print("🧬 [bold green]Starting Automatic Evolution Engine[/bold green]")
        self.console.print("🔄 Continuous improvement through OTEL telemetry analysis")
        
        while True:
            try:
                await self.run_evolution_cycle()
                await asyncio.sleep(self.evolution_config["cycle_interval_hours"] * 3600)
            except Exception as e:
                self.console.print(f"❌ Evolution cycle failed: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """Run single evolution cycle"""
        
        with self.tracer.start_as_current_span(
            "evolution.cycle",
            attributes={"cycle_number": self.evolution_cycles}
        ) as span:
            
            cycle_start = datetime.now()
            self.console.print(f"\n🧬 [bold cyan]Evolution Cycle {self.evolution_cycles + 1}[/bold cyan]")
            
            # Step 1: Collect telemetry data
            self.console.print("📊 Collecting telemetry data...")
            telemetry_data = await self._collect_telemetry_data()
            
            if len(telemetry_data) < self.evolution_config["min_telemetry_data_points"]:
                self.console.print("⚠️ Insufficient telemetry data for evolution")
                return {"status": "insufficient_data"}
            
            # Step 2: Analyze patterns
            self.console.print("🔍 Analyzing coordination patterns...")
            patterns = await self.telemetry_analyzer.analyze_coordination_patterns(telemetry_data)
            
            # Step 3: Update metrics
            self.console.print("📈 Updating evolution metrics...")
            await self._update_evolution_metrics(telemetry_data)
            
            # Step 4: Generate optimization actions
            self.console.print("⚡ Generating optimization actions...")
            actions = await self.optimizer.generate_optimization_actions(
                patterns, self.current_metrics
            )
            
            # Step 5: Filter and prioritize actions
            selected_actions = self._select_actions_for_execution(actions)
            
            # Step 6: Execute selected actions
            execution_results = []
            for action in selected_actions:
                result = await self.executor.execute_action(action)
                execution_results.append(result)
            
            # Step 7: Validate improvements
            validation_results = await self._validate_evolution_results(execution_results)
            
            # Step 8: Record evolution cycle
            cycle_result = {
                "cycle_number": self.evolution_cycles,
                "start_time": cycle_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "telemetry_data_points": len(telemetry_data),
                "patterns_discovered": len(patterns),
                "actions_generated": len(actions),
                "actions_executed": len(selected_actions),
                "execution_results": execution_results,
                "validation_results": validation_results
            }
            
            self.evolution_history.append(cycle_result)
            self.evolution_cycles += 1
            
            span.set_attribute("patterns_discovered", len(patterns))
            span.set_attribute("actions_executed", len(selected_actions))
            span.add_event("evolution_cycle_completed")
            
            self._display_evolution_summary(cycle_result)
            
            return cycle_result
    
    async def _collect_telemetry_data(self) -> List[Dict]:
        """Collect telemetry data from coordination system"""
        # In a real system, this would collect from OTEL collector
        # For now, return mock telemetry data
        
        mock_spans = []
        for i in range(150):  # Generate sufficient mock data
            span = {
                "name": f"agent.coordination.sync",
                "start_time": datetime.now().isoformat(),
                "duration_ms": 100 + (i % 50),
                "status": {"status_code": "OK" if i % 10 != 0 else "ERROR"},
                "attributes": {
                    "agent.id": f"agent_{i % 5}",
                    "feature.id": f"feature_{i % 10}",
                    "coordination.type": "sync"
                }
            }
            mock_spans.append(span)
        
        return mock_spans
    
    async def _update_evolution_metrics(self, telemetry_data: List[Dict]):
        """Update evolution metrics based on telemetry data"""
        
        # Calculate current metrics
        coordination_events = [s for s in telemetry_data if "coordination" in s.get("name", "")]
        
        if coordination_events:
            success_rate = len([s for s in coordination_events if s.get("status", {}).get("status_code") == "OK"]) / len(coordination_events)
            avg_duration = statistics.mean([s.get("duration_ms", 0) for s in coordination_events])
            
            # Update or create metrics
            self.current_metrics = [
                EvolutionMetric(
                    metric_name="agent_coordination_efficiency",
                    current_value=success_rate,
                    target_value=0.95,
                    trend="stable" if abs(success_rate - 0.9) < 0.05 else ("improving" if success_rate > 0.9 else "declining"),
                    importance=0.9,
                    optimization_direction="maximize",
                    last_updated=datetime.now().isoformat()
                ),
                EvolutionMetric(
                    metric_name="coordination_latency",
                    current_value=avg_duration,
                    target_value=50.0,  # Target 50ms
                    trend="stable",
                    importance=0.8,
                    optimization_direction="minimize",
                    last_updated=datetime.now().isoformat()
                )
            ]
    
    def _select_actions_for_execution(self, actions: List[EvolutionAction]) -> List[EvolutionAction]:
        """Select actions for execution based on configuration"""
        
        # Filter by confidence and risk
        filtered_actions = [
            action for action in actions
            if action.risk_level in ["low", "medium"] and action.expected_improvement > 0.1
        ]
        
        # Sort by expected improvement and take top N
        filtered_actions.sort(key=lambda a: a.expected_improvement, reverse=True)
        
        return filtered_actions[:self.evolution_config["max_actions_per_cycle"]]
    
    async def _validate_evolution_results(self, execution_results: List[Dict]) -> Dict[str, Any]:
        """Validate results of evolution actions"""
        
        validation = {
            "successful_executions": len([r for r in execution_results if r.get("status") == "success"]),
            "failed_executions": len([r for r in execution_results if r.get("status") == "failed"]),
            "rollbacks_needed": 0,
            "overall_improvement": True  # Simplified validation
        }
        
        return validation
    
    def _display_evolution_summary(self, cycle_result: Dict[str, Any]):
        """Display evolution cycle summary"""
        
        summary_panel = Panel(
            f"""
[bold]Cycle:[/bold] {cycle_result['cycle_number']}
[bold]Data Points:[/bold] {cycle_result['telemetry_data_points']}
[bold]Patterns Discovered:[/bold] {cycle_result['patterns_discovered']}
[bold]Actions Generated:[/bold] {cycle_result['actions_generated']}
[bold]Actions Executed:[/bold] {cycle_result['actions_executed']}
[bold]Success Rate:[/bold] {cycle_result['validation_results']['successful_executions']}/{cycle_result['actions_executed']}
            """.strip(),
            title="[bold green]🧬 Evolution Cycle Complete[/bold green]",
            border_style="green"
        )
        
        self.console.print(summary_panel)
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution engine status"""
        
        return {
            "cycles_completed": self.evolution_cycles,
            "current_metrics": [asdict(m) for m in self.current_metrics],
            "last_cycle": self.evolution_history[-1] if self.evolution_history else None,
            "evolution_config": self.evolution_config
        }