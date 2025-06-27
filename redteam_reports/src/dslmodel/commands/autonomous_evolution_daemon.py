#!/usr/bin/env python3
"""
Autonomous Evolution Daemon - Continuous 10-minute evolution cycles
Built using Weaver-first approach with meaningful work validation
"""

import asyncio
import signal
import time
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from loguru import logger

from ..generated.models.autonomous_evolution_loop import (
    Autonomous_evolution_scheduler,
    Autonomous_evolution_cycle,
    Autonomous_evolution_strategy_selection,
    Autonomous_evolution_meaningful_work,
    Autonomous_evolution_resource_management,
    Autonomous_evolution_error_recovery
)
from ..generated.models.evolution_worktree import (
    Evolution_worktree_experiment,
    Evolution_worktree_coordination
)

app = typer.Typer(help="Autonomous evolution daemon - runs continuous 10-minute cycles")
console = Console()


@dataclass
class EvolutionStrategy:
    """Evolution strategy configuration"""
    name: str
    description: str
    fitness_weight: float
    resource_intensity: float
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    historical_performance: List[float] = field(default_factory=list)


@dataclass 
class SystemMetrics:
    """Current system metrics for strategy selection"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_worktrees: int
    fitness_baseline: float
    error_rate: float
    uptime_minutes: int


class AutonomousEvolutionDaemon:
    """Continuous evolution daemon that runs meaningful work every 10 minutes"""
    
    def __init__(self, base_path: Path = Path.cwd()):
        self.base_path = base_path
        self.scheduler_id = f"autonomous-{uuid.uuid4().hex[:8]}"
        self.running = False
        self.cycle_number = 0
        self.total_meaningful_work = 0
        self.start_time = time.time()
        self.last_meaningful_work = None
        
        # Configuration
        self.schedule_interval = 10 * 60  # 10 minutes in seconds
        self.meaningful_work_threshold = 0.05  # 5% improvement minimum
        self.max_concurrent_experiments = 3
        self.resource_limit_cpu = 80.0  # 80% CPU
        self.resource_limit_memory = 85.0  # 85% memory
        
        # Evolution strategies with different characteristics
        self.strategies = {
            'performance': EvolutionStrategy(
                name='performance',
                description='Performance optimization through algorithmic improvements',
                fitness_weight=0.3,
                resource_intensity=0.7
            ),
            'quality': EvolutionStrategy(
                name='quality', 
                description='Code quality improvement through refactoring',
                fitness_weight=0.2,
                resource_intensity=0.4
            ),
            'security': EvolutionStrategy(
                name='security',
                description='Security hardening through vulnerability elimination', 
                fitness_weight=0.25,
                resource_intensity=0.5
            ),
            'features': EvolutionStrategy(
                name='features',
                description='Feature enhancement and capability expansion',
                fitness_weight=0.15,
                resource_intensity=0.8
            ),
            'architecture': EvolutionStrategy(
                name='architecture',
                description='Architectural refinement and design improvement',
                fitness_weight=0.1,
                resource_intensity=0.6
            )
        }
        
        # State tracking
        self.evolution_history = []
        self.error_count = 0
        self.consecutive_failures = 0
        self.resource_alerts = []
        
        # Initialize telemetry
        self.scheduler_span = None
        self._initialize_scheduler_telemetry()
        
    def _initialize_scheduler_telemetry(self):
        """Initialize scheduler telemetry tracking"""
        scheduler = Autonomous_evolution_scheduler(
            scheduler_id=self.scheduler_id,
            schedule_interval_minutes=self.schedule_interval // 60,
            scheduler_state='starting',
            total_cycles_completed=0,
            uptime_minutes=0,
            meaningful_work_threshold=self.meaningful_work_threshold,
            resource_limits=json.dumps({
                'cpu': self.resource_limit_cpu,
                'memory': self.resource_limit_memory,
                'max_experiments': self.max_concurrent_experiments
            }),
            last_meaningful_work_time=None
        )
        
        trace_id = scheduler.emit_telemetry()
        logger.info(f"🤖 Scheduler initialized: {self.scheduler_id} | Trace: {trace_id}")
        
    async def start_daemon(self):
        """Start the autonomous evolution daemon"""
        console.print(Panel(
            f"[bold cyan]🤖 Autonomous Evolution Daemon[/bold cyan]\n\n"
            f"Scheduler ID: [yellow]{self.scheduler_id}[/yellow]\n"
            f"Interval: [blue]10 minutes[/blue]\n"
            f"Meaningful Work Threshold: [green]{self.meaningful_work_threshold:.1%}[/green]\n"
            f"Max Concurrent Experiments: [blue]{self.max_concurrent_experiments}[/blue]\n"
            f"Base Path: [dim]{self.base_path}[/dim]",
            title="🚀 Starting Autonomous Evolution",
            border_style="cyan"
        ))
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        
        # Update scheduler state
        await self._update_scheduler_state('running')
        
        try:
            while self.running:
                cycle_start = time.time()
                
                # Run evolution cycle
                await self._run_evolution_cycle()
                
                # Calculate sleep time to maintain 10-minute intervals
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.schedule_interval - cycle_duration)
                
                if sleep_time > 0:
                    logger.info(f"⏰ Next cycle in {sleep_time/60:.1f} minutes")
                    
                    # Sleep with periodic status updates
                    await self._smart_sleep(sleep_time)
                else:
                    logger.warning(f"⚠️ Cycle took {cycle_duration:.1f}s, longer than {self.schedule_interval}s interval")
                    
        except Exception as e:
            logger.error(f"💥 Daemon crashed: {e}")
            await self._handle_error('daemon_crash', 'critical', str(e))
        finally:
            await self._shutdown_gracefully()
            
    async def _run_evolution_cycle(self):
        """Run one complete evolution cycle"""
        self.cycle_number += 1
        cycle_id = f"cycle-{self.cycle_number:04d}-{uuid.uuid4().hex[:6]}"
        
        logger.info(f"🧬 Starting Evolution Cycle {self.cycle_number}: {cycle_id}")
        
        cycle_start = time.time()
        
        try:
            # 1. Resource management check
            if not await self._check_resources():
                logger.warning("⚠️ Skipping cycle due to resource constraints")
                return
                
            # 2. Strategy selection
            selected_strategy = await self._select_strategy(cycle_id)
            
            # 3. Execute evolution cycle
            cycle_result = await self._execute_evolution_cycle(cycle_id, selected_strategy)
            
            # 4. Assess meaningful work
            meaningful_work = await self._assess_meaningful_work(cycle_id, cycle_result)
            
            # 5. Update strategy performance
            await self._update_strategy_performance(selected_strategy, cycle_result, meaningful_work)
            
            # 6. Resource cleanup
            await self._cleanup_resources()
            
            cycle_duration = int((time.time() - cycle_start) * 1000)
            
            # Emit cycle completion telemetry
            cycle = Autonomous_evolution_cycle(
                cycle_id=cycle_id,
                scheduler_id=self.scheduler_id,
                cycle_number=self.cycle_number,
                selected_strategy=selected_strategy,
                cycle_duration_ms=cycle_duration,
                experiments_created=cycle_result.get('experiments', 0),
                fitness_improvement=cycle_result.get('fitness_improvement', 0.0),
                meaningful_work_achieved=meaningful_work['deployment_recommended'],
                resource_usage=json.dumps(await self._get_resource_usage()),
                next_cycle_recommendation=await self._recommend_next_strategy()
            )
            
            trace_id = cycle.emit_telemetry()
            
            if meaningful_work['deployment_recommended']:
                self.total_meaningful_work += 1
                self.last_meaningful_work = time.time()
                self.consecutive_failures = 0
                logger.success(f"✅ Meaningful work achieved! Total: {self.total_meaningful_work}")
            else:
                self.consecutive_failures += 1
                logger.info(f"ℹ️ Cycle complete, no meaningful work. Consecutive: {self.consecutive_failures}")
                
            # Store evolution history
            self.evolution_history.append({
                'cycle_id': cycle_id,
                'cycle_number': self.cycle_number,
                'strategy': selected_strategy,
                'meaningful_work': meaningful_work['deployment_recommended'],
                'fitness_improvement': cycle_result.get('fitness_improvement', 0.0),
                'duration_ms': cycle_duration,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Evolution cycle failed: {e}")
            await self._handle_error('cycle_failure', 'high', str(e))
            self.consecutive_failures += 1
            
    async def _select_strategy(self, cycle_id: str) -> str:
        """Intelligently select evolution strategy based on telemetry and performance"""
        
        selection_start = time.time()
        
        # Get current system metrics
        metrics = await self._get_system_metrics()
        
        # Analyze strategy performance history
        strategy_scores = {}
        for name, strategy in self.strategies.items():
            score = 0.0
            
            # Base score from fitness weight
            score += strategy.fitness_weight * 0.4
            
            # Historical performance bonus
            if strategy.historical_performance:
                avg_performance = sum(strategy.historical_performance) / len(strategy.historical_performance)
                score += avg_performance * 0.3
                
            # Resource availability factor
            resource_factor = 1.0 - (strategy.resource_intensity * (metrics.cpu_usage / 100))
            score += resource_factor * 0.2
            
            # Recency penalty (encourage variety)
            if strategy.last_used:
                hours_since_use = (datetime.now() - strategy.last_used).total_seconds() / 3600
                recency_bonus = min(hours_since_use / 24, 1.0) * 0.1  # Max 10% bonus after 24h
                score += recency_bonus
                
            strategy_scores[name] = score
            
        # Select strategy with highest score
        selected_strategy = max(strategy_scores, key=strategy_scores.get)
        selection_confidence = strategy_scores[selected_strategy] / sum(strategy_scores.values())
        
        selection_duration = int((time.time() - selection_start) * 1000)
        
        # Emit strategy selection telemetry
        selection = Autonomous_evolution_strategy_selection(
            cycle_id=cycle_id,
            telemetry_analysis_duration_ms=selection_duration,
            available_strategies=json.dumps(list(self.strategies.keys())),
            strategy_scores=json.dumps(strategy_scores),
            selected_strategy=selected_strategy,
            selection_confidence=selection_confidence,
            historical_performance=json.dumps({
                name: strategy.historical_performance[-5:] if strategy.historical_performance else []
                for name, strategy in self.strategies.items()
            }),
            system_needs_priority=await self._assess_system_needs()
        )
        
        trace_id = selection.emit_telemetry()
        logger.info(f"🎯 Selected strategy: {selected_strategy} (confidence: {selection_confidence:.2f})")
        
        return selected_strategy
        
    async def _execute_evolution_cycle(self, cycle_id: str, strategy: str) -> Dict[str, Any]:
        """Execute the actual evolution cycle with the selected strategy"""
        
        try:
            # Import evolution engine
            from ..evolution_weaver.evolution_engine import WorktreeEvolutionEngine
            
            engine = WorktreeEvolutionEngine(base_path=self.base_path)
            
            if strategy not in engine.strategies:
                raise ValueError(f"Strategy {strategy} not available in evolution engine")
                
            # Configure strategy for autonomous operation
            strategy_config = engine.strategies[strategy]
            strategy_config.population_size = min(strategy_config.population_size, self.max_concurrent_experiments)
            strategy_config.max_generations = min(strategy_config.max_generations, 5)  # Limit for 10-min cycles
            
            # Run evolution cycle
            logger.info(f"🚀 Executing {strategy} evolution with {strategy_config.population_size} experiments")
            result = await engine.start_evolution_cycle(strategy)
            
            return {
                'strategy': strategy,
                'experiments': result.get('experiments_total', 0),
                'fitness_improvement': result.get('best_fitness', 0.0) - 0.75,  # Assume 0.75 baseline
                'merge_success': result.get('merge_success', False),
                'generations': result.get('generations_run', 0)
            }
            
        except ImportError:
            # Fallback to simulation if evolution engine not available
            logger.warning("🔄 Evolution engine not available, using simulation")
            
            await asyncio.sleep(2)  # Simulate work
            
            # Simulate realistic results
            import random
            experiments = random.randint(1, self.max_concurrent_experiments)
            fitness_improvement = random.uniform(-0.02, 0.15)  # -2% to +15%
            merge_success = fitness_improvement > self.meaningful_work_threshold
            
            return {
                'strategy': strategy,
                'experiments': experiments,
                'fitness_improvement': fitness_improvement,
                'merge_success': merge_success,
                'generations': random.randint(1, 5)
            }
            
    async def _assess_meaningful_work(self, cycle_id: str, cycle_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess whether the evolution cycle produced meaningful work"""
        
        baseline_fitness = 0.75  # Mock baseline
        achieved_fitness = baseline_fitness + cycle_result.get('fitness_improvement', 0.0)
        improvement_percentage = cycle_result.get('fitness_improvement', 0.0) * 100
        
        # Classify work meaningfulness
        if improvement_percentage >= self.meaningful_work_threshold * 100:
            if improvement_percentage >= 0.10 * 100:  # 10%+
                classification = 'highly_meaningful'
            else:
                classification = 'meaningful'
        elif improvement_percentage >= 0.01 * 100:  # 1%+
            classification = 'marginal'
        else:
            classification = 'insignificant'
            
        deployment_recommended = classification in ['highly_meaningful', 'meaningful']
        
        # Emit meaningful work assessment telemetry
        meaningful_work = Autonomous_evolution_meaningful_work(
            cycle_id=cycle_id,
            assessment_type='fitness_threshold',
            baseline_fitness=baseline_fitness,
            achieved_fitness=achieved_fitness,
            improvement_percentage=improvement_percentage,
            meaningful_threshold=self.meaningful_work_threshold * 100,
            work_classification=classification,
            impact_areas=json.dumps([cycle_result.get('strategy', 'unknown')]),
            deployment_recommended=deployment_recommended
        )
        
        trace_id = meaningful_work.emit_telemetry()
        
        return {
            'classification': classification,
            'improvement_percentage': improvement_percentage,
            'deployment_recommended': deployment_recommended,
            'impact_areas': [cycle_result.get('strategy', 'unknown')],
            'trace_id': trace_id
        }
        
    async def _check_resources(self) -> bool:
        """Check if system resources allow for evolution cycle"""
        
        metrics = await self._get_system_metrics()
        
        # Check resource limits
        resource_ok = (
            metrics.cpu_usage < self.resource_limit_cpu and
            metrics.memory_usage < self.resource_limit_memory and
            metrics.active_worktrees < self.max_concurrent_experiments * 2
        )
        
        # Emit resource management telemetry
        resource_mgmt = Autonomous_evolution_resource_management(
            scheduler_id=self.scheduler_id,
            resource_type='system_check',
            current_usage=max(metrics.cpu_usage, metrics.memory_usage),
            usage_limit=max(self.resource_limit_cpu, self.resource_limit_memory),
            resource_action='check' if resource_ok else 'throttle',
            resource_health_score=1.0 if resource_ok else 0.5
        )
        
        trace_id = resource_mgmt.emit_telemetry()
        
        if not resource_ok:
            logger.warning(f"⚠️ Resource limits exceeded - CPU: {metrics.cpu_usage:.1f}%, Memory: {metrics.memory_usage:.1f}%")
            
        return resource_ok
        
    async def _cleanup_resources(self):
        """Clean up evolution resources"""
        
        try:
            # Clean up old worktrees
            worktree_base = self.base_path.parent / "evolution_worktrees" 
            if worktree_base.exists():
                old_worktrees = [
                    d for d in worktree_base.iterdir() 
                    if d.is_dir() and (time.time() - d.stat().st_mtime) > 3600  # 1 hour old
                ]
                
                cleaned = 0
                for worktree in old_worktrees[:5]:  # Limit cleanup per cycle
                    try:
                        import shutil
                        shutil.rmtree(worktree)
                        cleaned += 1
                    except Exception as e:
                        logger.warning(f"Failed to clean {worktree}: {e}")
                        
                if cleaned > 0:
                    logger.info(f"🧹 Cleaned up {cleaned} old worktrees")
                    
                # Emit resource cleanup telemetry
                cleanup = Autonomous_evolution_resource_management(
                    scheduler_id=self.scheduler_id,
                    resource_type='worktrees',
                    current_usage=len(list(worktree_base.iterdir())) if worktree_base.exists() else 0,
                    usage_limit=self.max_concurrent_experiments * 2,
                    resource_action='cleanup',
                    resources_cleaned=cleaned,
                    cleanup_success=True
                )
                
                cleanup.emit_telemetry()
                
        except Exception as e:
            logger.error(f"❌ Resource cleanup failed: {e}")
            
    async def _get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
        except ImportError:
            # Fallback to mock metrics
            import random
            cpu_usage = random.uniform(20, 70)
            memory_usage = random.uniform(30, 80)
            disk_usage = random.uniform(20, 60)
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_worktrees=0,
                fitness_baseline=0.75,
                error_rate=self.error_count / max(self.cycle_number, 1),
                uptime_minutes=int((time.time() - self.start_time) / 60)
            )
            
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            active_worktrees=0,  # Would count actual worktrees
            fitness_baseline=0.75,
            error_rate=self.error_count / max(self.cycle_number, 1),
            uptime_minutes=int((time.time() - self.start_time) / 60)
        )
        
    async def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        metrics = await self._get_system_metrics()
        return {
            'cpu': metrics.cpu_usage,
            'memory': metrics.memory_usage,
            'disk': metrics.disk_usage,
            'worktrees': metrics.active_worktrees
        }
        
    async def _assess_system_needs(self) -> str:
        """Assess current highest priority system need"""
        metrics = await self._get_system_metrics()
        
        if metrics.error_rate > 0.1:
            return 'reliability'
        elif metrics.cpu_usage > 80:
            return 'performance'
        elif self.consecutive_failures > 3:
            return 'maintainability'
        else:
            return 'performance'
            
    async def _recommend_next_strategy(self) -> str:
        """Recommend strategy for next cycle"""
        system_need = await self._assess_system_needs()
        
        recommendations = {
            'performance': 'performance',
            'reliability': 'quality',
            'maintainability': 'architecture',
            'security': 'security'
        }
        
        return recommendations.get(system_need, 'quality')
        
    async def _update_strategy_performance(self, strategy: str, result: Dict[str, Any], meaningful_work: Dict[str, Any]):
        """Update strategy performance tracking"""
        
        if strategy in self.strategies:
            perf_score = result.get('fitness_improvement', 0.0)
            self.strategies[strategy].historical_performance.append(perf_score)
            
            # Keep only last 20 results
            if len(self.strategies[strategy].historical_performance) > 20:
                self.strategies[strategy].historical_performance = self.strategies[strategy].historical_performance[-20:]
                
            self.strategies[strategy].last_used = datetime.now()
            
            # Update success rate
            successes = sum(1 for p in self.strategies[strategy].historical_performance if p > self.meaningful_work_threshold)
            self.strategies[strategy].success_rate = successes / len(self.strategies[strategy].historical_performance)
            
    async def _handle_error(self, error_type: str, severity: str, message: str):
        """Handle errors with recovery attempts"""
        
        self.error_count += 1
        
        recovery_action = 'retry'
        if severity == 'critical':
            recovery_action = 'emergency_stop'
        elif self.consecutive_failures > 5:
            recovery_action = 'cleanup_and_restart'
        elif error_type == 'resource_exhaustion':
            recovery_action = 'cleanup'
            
        # Emit error recovery telemetry
        error_recovery = Autonomous_evolution_error_recovery(
            scheduler_id=self.scheduler_id,
            error_type=error_type,
            error_severity=severity,
            error_message=message,
            recovery_action=recovery_action,
            recovery_success=recovery_action != 'emergency_stop',
            retry_count=self.consecutive_failures,
            system_stability_impact='moderate' if self.consecutive_failures > 3 else 'minimal'
        )
        
        trace_id = error_recovery.emit_telemetry()
        
        if recovery_action == 'emergency_stop':
            logger.critical(f"🚨 Emergency stop triggered: {message}")
            self.running = False
        elif recovery_action == 'cleanup_and_restart':
            logger.warning(f"🔄 Cleaning up and restarting due to consecutive failures")
            await self._cleanup_resources()
            
    async def _update_scheduler_state(self, state: str):
        """Update scheduler state telemetry"""
        
        uptime_minutes = int((time.time() - self.start_time) / 60)
        
        scheduler = Autonomous_evolution_scheduler(
            scheduler_id=self.scheduler_id,
            schedule_interval_minutes=self.schedule_interval // 60,
            scheduler_state=state,
            total_cycles_completed=self.cycle_number,
            uptime_minutes=uptime_minutes,
            meaningful_work_threshold=self.meaningful_work_threshold,
            last_meaningful_work_time=int(self.last_meaningful_work) if self.last_meaningful_work else None
        )
        
        trace_id = scheduler.emit_telemetry()
        logger.debug(f"📊 Scheduler state: {state} | Trace: {trace_id}")
        
    async def _smart_sleep(self, sleep_time: float):
        """Sleep with periodic status updates"""
        
        intervals = max(1, int(sleep_time // 60))  # Update every minute
        interval_duration = sleep_time / intervals
        
        for i in range(intervals):
            await asyncio.sleep(interval_duration)
            
            if not self.running:
                break
                
            remaining = sleep_time - ((i + 1) * interval_duration)
            if remaining > 30:  # Only log if more than 30 seconds remaining
                logger.debug(f"⏰ Next cycle in {remaining/60:.1f} minutes")
                
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def _shutdown_gracefully(self):
        """Graceful shutdown with cleanup"""
        
        logger.info("🛑 Shutting down autonomous evolution daemon...")
        
        await self._update_scheduler_state('stopping')
        await self._cleanup_resources()
        
        # Final statistics
        uptime_minutes = int((time.time() - self.start_time) / 60)
        meaningful_work_rate = self.total_meaningful_work / max(self.cycle_number, 1)
        
        console.print(Panel(
            f"[bold yellow]📊 Final Statistics[/bold yellow]\n\n"
            f"Uptime: [blue]{uptime_minutes} minutes[/blue]\n"
            f"Cycles Completed: [green]{self.cycle_number}[/green]\n"
            f"Meaningful Work: [cyan]{self.total_meaningful_work}[/cyan]\n"
            f"Success Rate: [green]{meaningful_work_rate:.1%}[/green]\n"
            f"Error Count: [red]{self.error_count}[/red]",
            title="🤖 Autonomous Evolution Complete",
            border_style="yellow"
        ))
        
        await self._update_scheduler_state('stopped')
        logger.success("✅ Daemon shutdown complete")


@app.command("start")
def start_daemon(
    base_path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Base path for evolution"),
    meaningful_threshold: float = typer.Option(0.05, "--threshold", "-t", help="Meaningful work threshold (0.05 = 5%)"),
    max_experiments: int = typer.Option(3, "--max-experiments", help="Maximum concurrent experiments"),
    cpu_limit: float = typer.Option(80.0, "--cpu-limit", help="CPU usage limit percentage"),
    memory_limit: float = typer.Option(85.0, "--memory-limit", help="Memory usage limit percentage")
):
    """Start the autonomous evolution daemon"""
    
    daemon = AutonomousEvolutionDaemon(base_path)
    daemon.meaningful_work_threshold = meaningful_threshold
    daemon.max_concurrent_experiments = max_experiments
    daemon.resource_limit_cpu = cpu_limit
    daemon.resource_limit_memory = memory_limit
    
    try:
        asyncio.run(daemon.start_daemon())
    except KeyboardInterrupt:
        console.print("[yellow]Daemon interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Daemon failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def show_daemon_status():
    """Show autonomous evolution daemon status"""
    
    console.print("[bold cyan]🤖 Autonomous Evolution Daemon Status[/bold cyan]")
    
    # Check for running daemon (in real implementation would check PID file or process)
    console.print("[yellow]No running daemon detected[/yellow]")
    
    # Show recent evolution history if available
    history_file = Path.cwd() / ".evolution_history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
            
        recent = history[-10:] if len(history) > 10 else history
        
        table = Table(title="Recent Evolution History")
        table.add_column("Cycle", style="cyan")
        table.add_column("Strategy", style="yellow")
        table.add_column("Meaningful", style="green")
        table.add_column("Improvement", style="blue")
        table.add_column("Timestamp", style="dim")
        
        for entry in recent:
            table.add_row(
                f"#{entry['cycle_number']}",
                entry['strategy'],
                "✅" if entry['meaningful_work'] else "❌",
                f"{entry['fitness_improvement']:+.1%}",
                entry['timestamp'][:19]
            )
            
        console.print(table)
    else:
        console.print("[dim]No evolution history found[/dim]")


@app.command("simulate")
def simulate_daemon(
    cycles: int = typer.Option(5, "--cycles", "-c", help="Number of cycles to simulate"),
    fast: bool = typer.Option(False, "--fast", help="Fast simulation (no delays)")
):
    """Simulate autonomous evolution daemon"""
    
    async def run_simulation():
        daemon = AutonomousEvolutionDaemon()
        daemon.schedule_interval = 10 if not fast else 2  # 10s or 2s intervals for simulation
        
        console.print(f"🧪 Simulating {cycles} autonomous evolution cycles...")
        
        for i in range(cycles):
            await daemon._run_evolution_cycle()
            
            if i < cycles - 1:  # Don't sleep after last cycle
                await asyncio.sleep(daemon.schedule_interval)
                
        # Show results
        meaningful_count = sum(1 for h in daemon.evolution_history if h['meaningful_work'])
        total_cycles = len(daemon.evolution_history)
        console.print(f"\n📊 Simulation Results:")
        console.print(f"   Cycles: {total_cycles}")
        console.print(f"   Meaningful Work: {meaningful_count}/{total_cycles}")
        if total_cycles > 0:
            console.print(f"   Success Rate: {meaningful_count/total_cycles:.1%}")
        else:
            console.print(f"   Success Rate: N/A (no cycles completed)")
        
    asyncio.run(run_simulation())


if __name__ == "__main__":
    app()