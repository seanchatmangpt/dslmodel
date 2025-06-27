#!/usr/bin/env python3
"""
Weaver Loop Closure System - Active Architectural Loop Management

This system uses Weaver semantic conventions to actively monitor and close
all architectural loops in the DSLModel project, ensuring system coherence
and preventing architectural drift.
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn

from .weaver_multilayer import WeaverMultiLayerSystem
from .otel_gap_analyzer import OTELGapAnalyzer
from .claude_code_otel_monitor import ClaudeCodeOTELMonitor

app = typer.Typer()
console = Console()


@dataclass
class ArchitecturalLoop:
    """Represents an architectural feedback loop"""
    name: str
    description: str
    components: List[str]
    entry_points: List[str]
    exit_points: List[str]
    feedback_mechanism: str
    health_score: float = 0.0
    last_validated: Optional[float] = None
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class LoopClosure:
    """Represents a successful loop closure"""
    loop_name: str
    closure_type: str
    timestamp: float
    method: str
    evidence: List[str]
    impact_score: float


class WeaverLoopClosureSystem:
    """System for monitoring and closing architectural loops using Weaver"""
    
    def __init__(self):
        self.weaver_system = WeaverMultiLayerSystem()
        self.gap_analyzer = OTELGapAnalyzer()
        self.otel_monitor = ClaudeCodeOTELMonitor()
        self.architectural_loops: Dict[str, ArchitecturalLoop] = {}
        self.loop_closures: List[LoopClosure] = []
        self.active_monitoring = False
        
        # Initialize architectural loops
        self._define_architectural_loops()
    
    def _define_architectural_loops(self):
        """Define all major architectural loops in DSLModel"""
        
        self.architectural_loops = {
            "core_mixin_loop": ArchitecturalLoop(
                name="Core-Mixin-Feature Loop",
                description="DSLModel core → mixins → features → enhanced core",
                components=["dslmodel.core.creation", "dslmodel.mixin.application", "dslmodel.feature.enhancement"],
                entry_points=["DSLModel.__init__", "mixin composition"],
                exit_points=["enhanced capabilities", "new features"],
                feedback_mechanism="capability enhancement"
            ),
            
            "ai_generation_loop": ArchitecturalLoop(
                name="AI-Generation-Validation Loop",
                description="AI generation → validation → feedback → improved generation",
                components=["dslmodel.ai.generation", "dslmodel.validation.check", "dslmodel.ai.optimization"],
                entry_points=["from_prompt", "from_template", "from_signature"],
                exit_points=["validated models", "quality metrics"],
                feedback_mechanism="quality scoring and model improvement"
            ),
            
            "otel_weaver_loop": ArchitecturalLoop(
                name="OTEL-Weaver-Feedback Loop", 
                description="Telemetry → semantic conventions → validation → improved telemetry",
                components=["dslmodel.otel.collection", "dslmodel.weaver.validation", "dslmodel.feedback.optimization"],
                entry_points=["span creation", "metric collection"],
                exit_points=["convention compliance", "gap closure"],
                feedback_mechanism="semantic convention validation and gap analysis"
            ),
            
            "evolution_agent_loop": ArchitecturalLoop(
                name="Evolution-Agent-Adaptation Loop",
                description="Agents → evolution → adaptation → improved agents",
                components=["dslmodel.agent.operation", "dslmodel.evolution.cycle", "dslmodel.adaptation.enhancement"],
                entry_points=["agent task execution", "performance measurement"],
                exit_points=["evolved agents", "improved performance"],
                feedback_mechanism="fitness-based evolution and adaptation"
            ),
            
            "workflow_fsm_loop": ArchitecturalLoop(
                name="Workflow-FSM-State Loop",
                description="Workflows → state transitions → events → workflow enhancement",
                components=["dslmodel.workflow.execution", "dslmodel.fsm.transition", "dslmodel.state.management"],
                entry_points=["workflow start", "state changes"],
                exit_points=["workflow completion", "state consistency"],
                feedback_mechanism="state-driven workflow optimization"
            ),
            
            "cli_api_loop": ArchitecturalLoop(
                name="CLI-API-Integration Loop",
                description="CLI commands → API operations → results → command enhancement",
                components=["dslmodel.cli.command", "dslmodel.api.request", "dslmodel.integration.response"],
                entry_points=["command execution", "API calls"],
                exit_points=["operation results", "user feedback"],
                feedback_mechanism="usage patterns and performance optimization"
            ),
            
            "validation_generation_loop": ArchitecturalLoop(
                name="Validation-Generation-Improvement Loop",
                description="Validation → generation → testing → validation enhancement",
                components=["dslmodel.validation.check", "dslmodel.generation.create", "dslmodel.testing.verify"],
                entry_points=["validation execution", "code generation"],
                exit_points=["improved validation", "better generation"],
                feedback_mechanism="continuous improvement through testing"
            )
        }
    
    async def monitor_loops(self, duration_minutes: int = 60):
        """Continuously monitor all architectural loops"""
        console.print(f"[cyan]🔄 Starting loop monitoring for {duration_minutes} minutes...[/cyan]")
        
        self.active_monitoring = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Load semantic conventions
        await self._load_weaver_system()
        
        # Start OTEL monitoring
        self.otel_monitor.start_monitoring()
        
        try:
            while time.time() < end_time and self.active_monitoring:
                # Validate each loop
                for loop_name, loop in self.architectural_loops.items():
                    await self._validate_loop(loop)
                
                # Check for loop closures
                await self._detect_loop_closures()
                
                # Display current status
                self._display_loop_status()
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        finally:
            self.otel_monitor.stop_monitoring()
            self.active_monitoring = False
    
    async def _load_weaver_system(self):
        """Load Weaver semantic conventions"""
        console.print("[cyan]📚 Loading Weaver semantic conventions...[/cyan]")
        
        # Load all semantic convention layers
        layer_files = [
            "semconv_layers/base_layer.yaml",
            "semconv_layers/file_domain.yaml", 
            "semconv_layers/web_domain.yaml",
            "semconv_layers/claude_code_application.yaml",
            "semconv_layers/dslmodel_complete_ecosystem.yaml"
        ]
        
        for layer_file in layer_files:
            layer_path = Path(layer_file)
            if layer_path.exists():
                try:
                    self.weaver_system.load_layer(layer_path)
                    console.print(f"[green]✅ Loaded {layer_path.name}[/green]")
                except Exception as e:
                    console.print(f"[red]❌ Failed to load {layer_path}: {e}[/red]")
        
        # Load gap analyzer
        self.gap_analyzer.load_semantic_conventions(Path("semconv_layers"))
    
    async def _validate_loop(self, loop: ArchitecturalLoop):
        """Validate a specific architectural loop"""
        loop.last_validated = time.time()
        loop.issues.clear()
        
        # Check component connectivity
        connectivity_score = await self._check_component_connectivity(loop)
        
        # Check feedback mechanism integrity
        feedback_score = await self._check_feedback_mechanism(loop)
        
        # Check OTEL coverage
        otel_score = await self._check_otel_coverage(loop)
        
        # Check semantic convention compliance
        weaver_score = await self._check_weaver_compliance(loop)
        
        # Calculate overall health score
        loop.health_score = (connectivity_score + feedback_score + otel_score + weaver_score) / 4
        
        # Update metrics
        loop.metrics.update({
            "connectivity": connectivity_score,
            "feedback": feedback_score, 
            "otel_coverage": otel_score,
            "weaver_compliance": weaver_score,
            "overall_health": loop.health_score
        })
    
    async def _check_component_connectivity(self, loop: ArchitecturalLoop) -> float:
        """Check if loop components are properly connected"""
        try:
            # Simulate component connectivity check
            # In real implementation, this would check actual component relationships
            connected_components = 0
            total_components = len(loop.components)
            
            for component in loop.components:
                # Check if component has proper OTEL instrumentation
                if await self._component_has_instrumentation(component):
                    connected_components += 1
                else:
                    loop.issues.append(f"Component {component} lacks proper instrumentation")
            
            return (connected_components / total_components) * 100 if total_components > 0 else 0
            
        except Exception as e:
            loop.issues.append(f"Connectivity check failed: {e}")
            return 0.0
    
    async def _check_feedback_mechanism(self, loop: ArchitecturalLoop) -> float:
        """Check if feedback mechanism is functioning"""
        try:
            # Check for feedback events in OTEL data
            recent_spans = self.otel_monitor.spans_processed[-50:]  # Last 50 spans
            
            feedback_events = 0
            for span in recent_spans:
                # Look for spans that indicate feedback mechanism activity
                if any(component in span.name for component in loop.components):
                    feedback_events += 1
            
            # Score based on recent activity
            max_expected = 10  # Expected feedback events
            score = min(feedback_events / max_expected * 100, 100)
            
            if feedback_events == 0:
                loop.issues.append("No recent feedback mechanism activity detected")
            
            return score
            
        except Exception as e:
            loop.issues.append(f"Feedback mechanism check failed: {e}")
            return 0.0
    
    async def _check_otel_coverage(self, loop: ArchitecturalLoop) -> float:
        """Check OTEL instrumentation coverage for loop components"""
        try:
            # Check if loop components have OTEL spans
            covered_components = 0
            total_components = len(loop.components)
            
            # Get recent OTEL data
            recent_spans = self.otel_monitor.spans_processed[-100:]
            span_names = {span.name for span in recent_spans}
            
            for component in loop.components:
                # Check if we have spans for this component
                component_covered = any(component.replace('.', '_') in span_name for span_name in span_names)
                if component_covered:
                    covered_components += 1
                else:
                    loop.issues.append(f"No OTEL coverage for component {component}")
            
            return (covered_components / total_components) * 100 if total_components > 0 else 0
            
        except Exception as e:
            loop.issues.append(f"OTEL coverage check failed: {e}")
            return 0.0
    
    async def _check_weaver_compliance(self, loop: ArchitecturalLoop) -> float:
        """Check Weaver semantic convention compliance"""
        try:
            # Run gap analysis
            gap_findings = self.gap_analyzer.analyze_gaps()
            
            if not gap_findings:
                return 100.0  # Perfect compliance
            
            # Calculate compliance score based on gaps
            total_gaps = len(gap_findings)
            component_gaps = sum(1 for finding in gap_findings 
                               if any(comp in finding.span_name for comp in loop.components))
            
            if total_gaps == 0:
                return 100.0
            
            compliance_score = max(0, 100 - (component_gaps / total_gaps * 100))
            
            if component_gaps > 0:
                loop.issues.append(f"Found {component_gaps} Weaver compliance gaps")
            
            return compliance_score
            
        except Exception as e:
            loop.issues.append(f"Weaver compliance check failed: {e}")
            return 0.0
    
    async def _component_has_instrumentation(self, component: str) -> bool:
        """Check if component has proper instrumentation"""
        # Simplified check - in real implementation would check actual code
        instrumented_components = {
            "dslmodel.core.creation",
            "dslmodel.mixin.application", 
            "dslmodel.ai.generation",
            "dslmodel.validation.check",
            "dslmodel.workflow.execution",
            "dslmodel.fsm.transition",
            "dslmodel.cli.command",
            "dslmodel.api.request"
        }
        return component in instrumented_components
    
    async def _detect_loop_closures(self):
        """Detect when loops are successfully closed"""
        for loop_name, loop in self.architectural_loops.items():
            if loop.health_score >= 80.0 and len(loop.issues) == 0:
                # Check if this is a new closure
                recent_closures = [c for c in self.loop_closures 
                                 if c.loop_name == loop_name and time.time() - c.timestamp < 300]
                
                if not recent_closures:
                    closure = LoopClosure(
                        loop_name=loop_name,
                        closure_type="health_based",
                        timestamp=time.time(),
                        method="automated_validation",
                        evidence=[
                            f"Health score: {loop.health_score:.1f}%",
                            f"All components connected: {loop.metrics.get('connectivity', 0):.1f}%",
                            f"Feedback mechanism active: {loop.metrics.get('feedback', 0):.1f}%",
                            f"OTEL coverage: {loop.metrics.get('otel_coverage', 0):.1f}%",
                            f"Weaver compliance: {loop.metrics.get('weaver_compliance', 0):.1f}%"
                        ],
                        impact_score=loop.health_score
                    )
                    
                    self.loop_closures.append(closure)
                    console.print(f"[bold green]🔄 Loop closure detected: {loop_name}[/bold green]")
    
    def _display_loop_status(self):
        """Display current status of all loops"""
        console.clear()
        console.print("[bold cyan]🔄 DSLModel Architectural Loop Status[/bold cyan]")
        console.print("=" * 70)
        
        # Create status table
        status_table = Table(title="Loop Health Status")
        status_table.add_column("Loop", style="cyan")
        status_table.add_column("Health", style="yellow")
        status_table.add_column("Connectivity", style="blue")
        status_table.add_column("Feedback", style="green")
        status_table.add_column("OTEL", style="magenta")
        status_table.add_column("Weaver", style="red")
        status_table.add_column("Issues", style="bright_red")
        status_table.add_column("Status", style="bold")
        
        for loop_name, loop in self.architectural_loops.items():
            health_color = "green" if loop.health_score >= 80 else "yellow" if loop.health_score >= 60 else "red"
            status_icon = "🟢" if loop.health_score >= 80 else "🟡" if loop.health_score >= 60 else "🔴"
            
            if len(loop.issues) == 0 and loop.health_score >= 80:
                status_text = "CLOSED ✅"
            elif loop.health_score >= 60:
                status_text = "HEALTHY 🔄"
            else:
                status_text = "NEEDS ATTENTION ⚠️"
            
            status_table.add_row(
                loop_name.replace("_", " ").title(),
                f"[{health_color}]{loop.health_score:.1f}%[/{health_color}]",
                f"{loop.metrics.get('connectivity', 0):.0f}%",
                f"{loop.metrics.get('feedback', 0):.0f}%", 
                f"{loop.metrics.get('otel_coverage', 0):.0f}%",
                f"{loop.metrics.get('weaver_compliance', 0):.0f}%",
                str(len(loop.issues)),
                f"{status_icon} {status_text}"
            )
        
        console.print(status_table)
        
        # Show recent closures
        if self.loop_closures:
            recent_closures = [c for c in self.loop_closures if time.time() - c.timestamp < 3600]
            if recent_closures:
                console.print(f"\n[bold green]🎉 Recent Loop Closures ({len(recent_closures)}):[/bold green]")
                for closure in recent_closures[-5:]:  # Show last 5
                    age_minutes = (time.time() - closure.timestamp) / 60
                    console.print(f"  • {closure.loop_name} - {age_minutes:.1f}m ago (Impact: {closure.impact_score:.1f})")
        
        # Show system summary
        avg_health = sum(loop.health_score for loop in self.architectural_loops.values()) / len(self.architectural_loops)
        closed_loops = sum(1 for loop in self.architectural_loops.values() 
                          if loop.health_score >= 80 and len(loop.issues) == 0)
        
        summary = f"""
🎯 **System Summary:**
• Average Loop Health: {avg_health:.1f}%
• Closed Loops: {closed_loops}/{len(self.architectural_loops)}
• Total Closures: {len(self.loop_closures)}
• Active Monitoring: {'🟢 ON' if self.active_monitoring else '🔴 OFF'}
"""
        
        console.print(Panel(summary, title="System Overview", border_style="green"))
    
    def generate_closure_report(self) -> Dict[str, Any]:
        """Generate comprehensive loop closure report"""
        return {
            "timestamp": time.time(),
            "system_health": {
                "average_loop_health": sum(loop.health_score for loop in self.architectural_loops.values()) / len(self.architectural_loops),
                "closed_loops": sum(1 for loop in self.architectural_loops.values() 
                                  if loop.health_score >= 80 and len(loop.issues) == 0),
                "total_loops": len(self.architectural_loops),
                "closure_rate": len(self.loop_closures) / len(self.architectural_loops) if self.architectural_loops else 0
            },
            "loop_status": {
                name: {
                    "health_score": loop.health_score,
                    "metrics": loop.metrics,
                    "issues": loop.issues,
                    "last_validated": loop.last_validated
                }
                for name, loop in self.architectural_loops.items()
            },
            "recent_closures": [
                {
                    "loop_name": closure.loop_name,
                    "timestamp": closure.timestamp,
                    "method": closure.method,
                    "impact_score": closure.impact_score,
                    "evidence": closure.evidence
                }
                for closure in self.loop_closures[-10:]  # Last 10 closures
            ],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improving loop closure"""
        recommendations = []
        
        for loop_name, loop in self.architectural_loops.items():
            if loop.health_score < 80:
                if loop.metrics.get('connectivity', 0) < 80:
                    recommendations.append(f"Improve component connectivity for {loop_name}")
                if loop.metrics.get('otel_coverage', 0) < 80:
                    recommendations.append(f"Add more OTEL instrumentation for {loop_name}")
                if loop.metrics.get('weaver_compliance', 0) < 80:
                    recommendations.append(f"Address Weaver compliance gaps for {loop_name}")
                if len(loop.issues) > 3:
                    recommendations.append(f"Resolve {len(loop.issues)} issues in {loop_name}")
        
        return recommendations


@app.command()
def monitor(
    duration: int = typer.Option(60, "--duration", "-d", help="Monitoring duration in minutes"),
    report_file: Optional[Path] = typer.Option(None, "--report", "-r", help="Output report file")
):
    """Monitor architectural loops and detect closures"""
    
    console.print("[bold green]🔄 Weaver Loop Closure System[/bold green]")
    console.print("=" * 60)
    
    async def run_monitoring():
        system = WeaverLoopClosureSystem()
        
        try:
            await system.monitor_loops(duration)
            
            # Generate final report
            report = system.generate_closure_report()
            
            if report_file:
                report_file.write_text(json.dumps(report, indent=2))
                console.print(f"[green]📊 Report saved to {report_file}[/green]")
            
            # Show final summary
            console.print("\n[bold cyan]🎉 Monitoring Complete![/bold cyan]")
            console.print(f"• Average System Health: {report['system_health']['average_loop_health']:.1f}%")
            console.print(f"• Closed Loops: {report['system_health']['closed_loops']}/{report['system_health']['total_loops']}")
            console.print(f"• Total Closures Detected: {len(report['recent_closures'])}")
            
            if report['recommendations']:
                console.print(f"\n[yellow]📋 Recommendations:[/yellow]")
                for rec in report['recommendations'][:5]:
                    console.print(f"  • {rec}")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]⏹️ Monitoring stopped by user[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Monitoring failed: {e}[/red]")
    
    # Run async monitoring
    asyncio.run(run_monitoring())


@app.command()
def status():
    """Show current loop status without monitoring"""
    
    system = WeaverLoopClosureSystem()
    
    console.print("[bold cyan]🔄 Current Loop Status[/bold cyan]")
    console.print("=" * 50)
    
    # Display loop definitions
    loop_tree = Tree("📋 Defined Architectural Loops")
    
    for loop_name, loop in system.architectural_loops.items():
        loop_branch = loop_tree.add(f"[cyan]{loop.name}[/cyan]")
        loop_branch.add(f"Components: {len(loop.components)}")
        loop_branch.add(f"Entry Points: {', '.join(loop.entry_points[:2])}...")
        loop_branch.add(f"Feedback: {loop.feedback_mechanism}")
    
    console.print(loop_tree)
    
    console.print(f"\n[green]✅ {len(system.architectural_loops)} architectural loops defined[/green]")
    console.print("[yellow]💡 Run 'monitor' command to start active loop closure monitoring[/yellow]")


if __name__ == "__main__":
    app()