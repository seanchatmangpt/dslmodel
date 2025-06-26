#!/usr/bin/env python3
"""
Auto-Evolution CLI - Automatic evolution with SwarmAgent integration

This CLI provides advanced evolution capabilities that integrate with agent coordination,
enabling autonomous system improvement through distributed agent collaboration.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from loguru import logger

from ..utils.json_output import json_command
from ..evolution.autonomous_evolution_engine import AutonomousEvolutionEngine
from ..agents.worktree_agent_coordinator import (
    WorktreeAgentCoordinator,
    AgentCapability,
    FeatureSpec
)
from ..telemetry.realtime_processor import TelemetryStreamProcessor


app = typer.Typer(help="Automatic evolution with SwarmAgent integration")
console = Console()


class AutoEvolutionCoordinator:
    """Coordinates evolution with agent development"""
    
    def __init__(self, telemetry_dir: Path, coordination_dir: Path):
        self.telemetry_dir = telemetry_dir
        self.coordination_dir = coordination_dir
        
        # Initialize subsystems
        self.evolution_engine = AutonomousEvolutionEngine(telemetry_dir)
        self.agent_coordinator = WorktreeAgentCoordinator(Path.cwd(), coordination_dir)
        self.telemetry_processor = TelemetryStreamProcessor()
        
        # Evolution agents
        self._register_evolution_agents()
    
    def _register_evolution_agents(self):
        """Register specialized evolution agents"""
        evolution_agents = [
            AgentCapability(
                agent_id="evolution-performance-001",
                languages=["python"],
                frameworks=["numpy", "pandas"],
                expertise_areas=["performance", "optimization", "telemetry"],
                preferred_complexity="high"
            ),
            AgentCapability(
                agent_id="evolution-pattern-001",
                languages=["python"],
                frameworks=["scikit-learn", "tensorflow"],
                expertise_areas=["pattern-detection", "machine-learning", "analysis"],
                preferred_complexity="high"
            ),
            AgentCapability(
                agent_id="evolution-remediation-001",
                languages=["python", "bash"],
                frameworks=["ansible", "kubernetes"],
                expertise_areas=["remediation", "automation", "infrastructure"],
                preferred_complexity="medium"
            )
        ]
        
        for agent in evolution_agents:
            self.agent_coordinator.register_agent(agent)
    
    def create_evolution_features(self, patterns: List[Any]) -> List[FeatureSpec]:
        """Create feature requests from discovered patterns"""
        features = []
        
        for pattern in patterns:
            if pattern.pattern_type == "performance_degradation":
                feature = FeatureSpec(
                    name=f"optimize-{pattern.conditions.get('operation', 'unknown')}",
                    description=f"Optimize performance for {pattern.conditions.get('operation', 'operation')} "
                               f"which shows {pattern.performance_impact:.1%} degradation",
                    requirements=[
                        "Analyze current implementation",
                        "Identify performance bottlenecks",
                        "Implement optimizations",
                        "Validate improvements with benchmarks"
                    ],
                    acceptance_criteria=[
                        f"Performance improvement of at least {abs(pattern.performance_impact) * 0.5:.1%}",
                        "No regression in other operations",
                        "Updated telemetry monitoring"
                    ],
                    estimated_effort=5,
                    priority="high"
                )
                features.append(feature)
                
            elif pattern.pattern_type == "recurring_error":
                feature = FeatureSpec(
                    name=f"fix-{pattern.conditions.get('error_type', 'error')}",
                    description=f"Fix recurring {pattern.conditions.get('error_type', 'error')} "
                               f"occurring {pattern.occurrence_count} times",
                    requirements=[
                        "Root cause analysis",
                        "Implement error handling",
                        "Add preventive measures",
                        "Create monitoring alerts"
                    ],
                    acceptance_criteria=[
                        "Error rate reduced by 90%",
                        "Proper error handling in place",
                        "Monitoring configured"
                    ],
                    estimated_effort=3,
                    priority="high"
                )
                features.append(feature)
        
        return features
    
    async def run_auto_evolution_cycle(self) -> Dict[str, Any]:
        """Run one complete auto-evolution cycle"""
        cycle_start = time.time()
        
        # 1. Analyze telemetry for patterns
        patterns = self.evolution_engine.analyze_telemetry_for_patterns()
        
        # 2. Evolve system parameters
        generation = self.evolution_engine.evolve_generation()
        
        # 3. Create features from patterns
        features = self.create_evolution_features(patterns)
        
        # 4. Assign features to agents
        assignments_made = 0
        for feature in features:
            self.agent_coordinator.add_feature_request(feature)
            
        # Run coordination cycle
        coordination_result = self.agent_coordinator.run_coordination_cycle()
        assignments_made = coordination_result["assignments_made"]
        
        # 5. Process real-time telemetry
        telemetry_metrics = self.telemetry_processor.get_current_metrics()
        
        cycle_duration = int((time.time() - cycle_start) * 1000)
        
        return {
            "generation": generation.generation_id,
            "fitness_score": generation.fitness_score,
            "patterns_discovered": len(patterns),
            "features_created": len(features),
            "assignments_made": assignments_made,
            "telemetry_health": telemetry_metrics.get("health_score", 0.0),
            "cycle_duration_ms": cycle_duration
        }


@app.command("start")
def start_auto_evolution(
    telemetry_dir: Path = typer.Option(Path("./telemetry"), "--telemetry", "-t", help="Telemetry data directory"),
    coordination_dir: Path = typer.Option(Path("./coordination"), "--coord", "-c", help="Coordination directory"),
    interval: int = typer.Option(60, "--interval", "-i", help="Seconds between evolution cycles"),
    max_cycles: int = typer.Option(0, "--max-cycles", help="Maximum cycles (0 = unlimited)"),
    target_fitness: float = typer.Option(0.95, "--target", help="Target fitness score")
):
    """Start automatic evolution with agent coordination"""
    
    async def auto_evolution_loop():
        coordinator = AutoEvolutionCoordinator(telemetry_dir, coordination_dir)
        cycle_count = 0
        
        with json_command("auto-evolution-start") as formatter:
            try:
                formatter.print("🚀 Starting Auto-Evolution System")
                formatter.print(f"📊 Telemetry: {telemetry_dir}")
                formatter.print(f"🤖 Coordination: {coordination_dir}")
                formatter.print(f"🎯 Target Fitness: {target_fitness}")
                formatter.print(f"⏱️ Cycle Interval: {interval}s")
                
                with Live(console=console, refresh_per_second=1) as live:
                    while max_cycles == 0 or cycle_count < max_cycles:
                        # Run evolution cycle
                        result = await coordinator.run_auto_evolution_cycle()
                        cycle_count += 1
                        
                        # Update display
                        evolution_status = coordinator.evolution_engine.get_evolution_status()
                        agent_status = coordinator.agent_coordinator.get_coordination_status()
                        
                        display_panel = Panel(
                            f"🧬 Generation: {result['generation']}\n"
                            f"💪 Fitness: {result['fitness_score']:.3f} / {target_fitness:.3f}\n"
                            f"📈 Trajectory: {evolution_status['evolution_trajectory']}\n"
                            f"🔍 Patterns: {result['patterns_discovered']}\n"
                            f"📋 Features Created: {result['features_created']}\n"
                            f"🤖 Active Agents: {agent_status['active_agents']}\n"
                            f"🔄 Assignments: {result['assignments_made']}\n"
                            f"💚 System Health: {result['telemetry_health']:.2f}",
                            title=f"🌟 Auto-Evolution Cycle {cycle_count}",
                            expand=False
                        )
                        
                        live.update(display_panel)
                        
                        # Check target fitness
                        if result['fitness_score'] >= target_fitness:
                            formatter.print(f"\n🎯 Target fitness {target_fitness} reached!")
                            break
                        
                        await asyncio.sleep(interval)
                
                formatter.add_data("cycles_completed", cycle_count)
                formatter.add_data("final_fitness", coordinator.evolution_engine._calculate_fitness_score())
                formatter.print(f"\n✅ Auto-evolution completed after {cycle_count} cycles")
                
            except KeyboardInterrupt:
                formatter.print("\n⏹️ Auto-evolution stopped by user")
            except Exception as e:
                formatter.add_error(f"Auto-evolution failed: {e}")
                formatter.print(f"❌ Auto-evolution failed: {e}")
                raise typer.Exit(1)
    
    asyncio.run(auto_evolution_loop())


@app.command("status")
def show_auto_evolution_status(
    telemetry_dir: Path = typer.Option(Path("./telemetry"), "--telemetry", "-t", help="Telemetry data directory"),
    coordination_dir: Path = typer.Option(Path("./coordination"), "--coord", "-c", help="Coordination directory")
):
    """Show auto-evolution system status"""
    with json_command("auto-evolution-status") as formatter:
        try:
            coordinator = AutoEvolutionCoordinator(telemetry_dir, coordination_dir)
            
            # Get status from all subsystems
            evolution_status = coordinator.evolution_engine.get_evolution_status()
            agent_status = coordinator.agent_coordinator.get_coordination_status()
            telemetry_metrics = coordinator.telemetry_processor.get_current_metrics()
            
            formatter.add_data("evolution_status", evolution_status)
            formatter.add_data("agent_status", agent_status)
            formatter.add_data("telemetry_metrics", telemetry_metrics)
            
            # Display comprehensive status
            console.print(Panel("🌟 Auto-Evolution System Status", expand=False))
            
            # Evolution status
            evolution_panel = Panel(
                f"Generation: {evolution_status['generation']}\n"
                f"Fitness Score: {evolution_status['fitness_score']:.3f}\n"
                f"Improvement: {evolution_status['fitness_improvement']:.1%}\n"
                f"Patterns: {evolution_status['patterns_discovered']}\n"
                f"Trajectory: {evolution_status['evolution_trajectory']}",
                title="🧬 Evolution Engine",
                expand=False
            )
            console.print(evolution_panel)
            
            # Agent coordination status
            agent_panel = Panel(
                f"Total Agents: {agent_status['total_agents']}\n"
                f"Active: {agent_status['active_agents']}\n"
                f"Features in Queue: {agent_status['features_in_queue']}\n"
                f"Features Completed: {agent_status['features_completed']}\n"
                f"Coordination Health: {agent_status['coordination_health']:.2f}",
                title="🤖 Agent Coordination",
                expand=False
            )
            console.print(agent_panel)
            
            # Telemetry status
            telemetry_panel = Panel(
                f"Health Score: {telemetry_metrics.get('health_score', 0.0):.2f}\n"
                f"Error Rate: {telemetry_metrics.get('error_rate', 0.0):.2%}\n"
                f"Avg Response Time: {telemetry_metrics.get('avg_response_time', 0):.0f}ms\n"
                f"Active Patterns: {telemetry_metrics.get('active_patterns', 0)}",
                title="📊 Telemetry Processing",
                expand=False
            )
            console.print(telemetry_panel)
            
        except Exception as e:
            formatter.add_error(f"Status check failed: {e}")
            formatter.print(f"❌ Status check failed: {e}")
            raise typer.Exit(1)


@app.command("configure")
def configure_auto_evolution(
    telemetry_dir: Path = typer.Option(Path("./telemetry"), "--telemetry", "-t", help="Telemetry data directory"),
    mutation_rate: Optional[float] = typer.Option(None, "--mutation-rate", help="Global mutation rate"),
    learning_rate: Optional[str] = typer.Option(None, "--learning-rate", help="Learning rate strategy"),
    pattern_threshold: Optional[float] = typer.Option(None, "--pattern-threshold", help="Pattern confidence threshold"),
    agent_count: Optional[int] = typer.Option(None, "--agents", help="Number of evolution agents")
):
    """Configure auto-evolution parameters"""
    with json_command("auto-evolution-configure") as formatter:
        try:
            engine = AutonomousEvolutionEngine(telemetry_dir)
            
            changes_made = []
            
            if mutation_rate is not None:
                engine.evolution_config["mutation_probability"] = mutation_rate
                changes_made.append(f"Mutation rate: {mutation_rate}")
            
            if learning_rate is not None:
                # Map string to enum
                learning_rates = {
                    "conservative": 0.01,
                    "moderate": 0.05,
                    "aggressive": 0.1
                }
                if learning_rate.lower() in learning_rates:
                    for gene in engine.genes.values():
                        gene.mutation_rate = learning_rates[learning_rate.lower()]
                    changes_made.append(f"Learning rate: {learning_rate}")
            
            if pattern_threshold is not None:
                engine.evolution_config["pattern_confidence_threshold"] = pattern_threshold
                if "pattern_detection_threshold" in engine.genes:
                    engine.genes["pattern_detection_threshold"].current_value = pattern_threshold
                changes_made.append(f"Pattern threshold: {pattern_threshold}")
            
            if changes_made:
                engine._save_evolution_state()
                
                formatter.add_data("changes_made", changes_made)
                formatter.print("✅ Auto-evolution configuration updated:")
                for change in changes_made:
                    formatter.print(f"  • {change}")
            else:
                formatter.print("ℹ️ No configuration changes specified")
                
        except Exception as e:
            formatter.add_error(f"Configuration failed: {e}")
            formatter.print(f"❌ Configuration failed: {e}")
            raise typer.Exit(1)


@app.command("simulate")
def simulate_evolution_scenarios(
    telemetry_dir: Path = typer.Option(Path("./telemetry"), "--telemetry", "-t", help="Telemetry data directory"),
    scenario: str = typer.Option("performance", "--scenario", "-s", help="Simulation scenario"),
    duration: int = typer.Option(10, "--duration", "-d", help="Simulation duration in cycles")
):
    """Simulate evolution scenarios"""
    
    async def run_simulation():
        with json_command("auto-evolution-simulate") as formatter:
            try:
                console.print(Panel(f"🎮 Simulating Evolution Scenario: {scenario}", expand=False))
                
                # Create simulation telemetry
                telemetry_dir.mkdir(exist_ok=True)
                simulation_data = []
                
                if scenario == "performance":
                    # Simulate performance degradation
                    for i in range(100):
                        simulation_data.append({
                            "timestamp": time.time() - i * 10,
                            "operation": "api_call",
                            "duration_ms": 150 + i * 2,  # Degrading performance
                            "success": True,
                            "error": False
                        })
                elif scenario == "errors":
                    # Simulate recurring errors
                    for i in range(100):
                        simulation_data.append({
                            "timestamp": time.time() - i * 10,
                            "operation": "db_query",
                            "duration_ms": 100,
                            "success": i % 5 != 0,  # 20% error rate
                            "error": i % 5 == 0,
                            "error_type": "connection_timeout" if i % 5 == 0 else None
                        })
                elif scenario == "complex":
                    # Complex scenario with multiple patterns
                    import random
                    for i in range(200):
                        operation = ["api_call", "db_query", "cache_read"][i % 3]
                        simulation_data.append({
                            "timestamp": time.time() - i * 10,
                            "operation": operation,
                            "duration_ms": random.gauss(150 + i * 0.5, 20),
                            "success": random.random() > 0.1,
                            "error": random.random() < 0.1
                        })
                
                # Save simulation telemetry
                with open(telemetry_dir / "simulation_telemetry.jsonl", 'w') as f:
                    for span in simulation_data:
                        f.write(json.dumps(span) + '\n')
                
                # Run evolution simulation
                coordinator = AutoEvolutionCoordinator(telemetry_dir, Path("./coordination_sim"))
                
                console.print(f"📊 Running {duration} simulation cycles...")
                
                results = []
                for cycle in range(duration):
                    result = await coordinator.run_auto_evolution_cycle()
                    results.append(result)
                    
                    console.print(f"Cycle {cycle + 1}: "
                                f"Fitness {result['fitness_score']:.3f}, "
                                f"Patterns {result['patterns_discovered']}")
                    
                    await asyncio.sleep(0.5)
                
                # Analyze results
                fitness_improvement = results[-1]['fitness_score'] - results[0]['fitness_score']
                total_patterns = sum(r['patterns_discovered'] for r in results)
                total_features = sum(r['features_created'] for r in results)
                
                formatter.add_data("simulation_results", {
                    "scenario": scenario,
                    "cycles": duration,
                    "fitness_improvement": fitness_improvement,
                    "total_patterns": total_patterns,
                    "total_features": total_features
                })
                
                console.print("\n📈 Simulation Results:")
                console.print(f"  Scenario: {scenario}")
                console.print(f"  Fitness Improvement: {fitness_improvement:+.3f}")
                console.print(f"  Total Patterns: {total_patterns}")
                console.print(f"  Features Generated: {total_features}")
                
                formatter.print("✅ Simulation completed successfully")
                
            except Exception as e:
                formatter.add_error(f"Simulation failed: {e}")
                console.print(f"❌ Simulation failed: {e}")
                raise typer.Exit(1)
    
    asyncio.run(run_simulation())


@app.command("report")
def generate_evolution_report(
    telemetry_dir: Path = typer.Option(Path("./telemetry"), "--telemetry", "-t", help="Telemetry data directory"),
    coordination_dir: Path = typer.Option(Path("./coordination"), "--coord", "-c", help="Coordination directory"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for report")
):
    """Generate comprehensive evolution report"""
    with json_command("auto-evolution-report") as formatter:
        try:
            coordinator = AutoEvolutionCoordinator(telemetry_dir, coordination_dir)
            
            # Gather comprehensive data
            evolution_status = coordinator.evolution_engine.get_evolution_status()
            agent_status = coordinator.agent_coordinator.get_coordination_status()
            
            # Create report
            report = {
                "timestamp": time.time(),
                "evolution": {
                    "current_generation": evolution_status["generation"],
                    "fitness_score": evolution_status["fitness_score"],
                    "fitness_improvement": evolution_status["fitness_improvement"],
                    "patterns_discovered": evolution_status["patterns_discovered"],
                    "trajectory": evolution_status["evolution_trajectory"],
                    "recent_mutations": evolution_status["recent_mutations"][:5]
                },
                "agents": {
                    "total_agents": agent_status["total_agents"],
                    "active_agents": agent_status["active_agents"],
                    "features_completed": agent_status["features_completed"],
                    "features_in_progress": agent_status["features_in_progress"],
                    "coordination_health": agent_status["coordination_health"]
                },
                "performance_metrics": evolution_status["performance_metrics"],
                "recommendations": []
            }
            
            # Add recommendations
            if evolution_status["fitness_score"] < 0.7:
                report["recommendations"].append("Consider increasing evolution interval for better convergence")
            
            if agent_status["features_in_queue"] > 10:
                report["recommendations"].append("Add more evolution agents to handle feature backlog")
            
            if evolution_status["evolution_trajectory"] == "degrading":
                report["recommendations"].append("Review recent mutations and consider rollback")
            
            # Display report
            console.print(Panel("📊 Auto-Evolution Report", expand=False))
            
            # Evolution summary
            console.print("\n🧬 Evolution Summary:")
            console.print(f"  Generation: {report['evolution']['current_generation']}")
            console.print(f"  Fitness: {report['evolution']['fitness_score']:.3f}")
            console.print(f"  Improvement: {report['evolution']['fitness_improvement']:.1%}")
            console.print(f"  Trajectory: {report['evolution']['trajectory']}")
            
            # Agent summary
            console.print("\n🤖 Agent Summary:")
            console.print(f"  Active Agents: {report['agents']['active_agents']}/{report['agents']['total_agents']}")
            console.print(f"  Features Completed: {report['agents']['features_completed']}")
            console.print(f"  Coordination Health: {report['agents']['coordination_health']:.2f}")
            
            # Recommendations
            if report["recommendations"]:
                console.print("\n💡 Recommendations:")
                for rec in report["recommendations"]:
                    console.print(f"  • {rec}")
            
            # Save report if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                formatter.print(f"\n✅ Report saved to {output_file}")
            
            formatter.add_data("report", report)
            
        except Exception as e:
            formatter.add_error(f"Report generation failed: {e}")
            formatter.print(f"❌ Report generation failed: {e}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()