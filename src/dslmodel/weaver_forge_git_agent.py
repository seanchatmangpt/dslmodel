#!/usr/bin/env python3
"""
Weaver Forge Git Agent Auto DX Loop

An intelligent git agent that automates the entire developer experience loop
using Weaver semantic conventions, autonomous decision-making, and continuous
feedback optimization.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .weaver_multilayer import WeaverMultiLayerSystem
from .otel_gap_analyzer import OTELGapAnalyzer
from .claude_code_otel_monitor import ClaudeCodeOTELMonitor

console = Console()

class GitAgentAction(Enum):
    """Types of actions the git agent can perform"""
    COMMIT = "commit"
    BRANCH = "branch"
    MERGE = "merge"
    TAG = "tag"
    PUSH = "push"
    PULL = "pull"
    REBASE = "rebase"
    STASH = "stash"
    CHERRY_PICK = "cherry_pick"
    RESET = "reset"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"

class DXLoopPhase(Enum):
    """Phases of the Developer Experience loop"""
    DETECTION = "detection"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    FEEDBACK = "feedback"

@dataclass
class GitAgentDecision:
    """Represents a decision made by the git agent"""
    action: GitAgentAction
    phase: DXLoopPhase
    confidence: float
    reasoning: str
    commands: List[str]
    expected_outcome: str
    rollback_plan: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DXMetrics:
    """Developer Experience metrics"""
    commit_frequency: float
    branch_health: float
    merge_success_rate: float
    conflict_rate: float
    deployment_speed: float
    test_coverage: float
    code_quality_score: float
    developer_satisfaction: float
    automation_efficiency: float

@dataclass
class WeaverForgeConfig:
    """Configuration for Weaver Forge Git Agent"""
    auto_commit: bool = True
    auto_branch: bool = True
    auto_merge: bool = False  # Requires approval
    auto_tag: bool = True
    auto_push: bool = False   # Requires approval
    min_confidence: float = 0.8
    max_daily_commits: int = 50
    semantic_conventions_path: str = "semconv_layers"
    git_hooks_enabled: bool = True
    dx_optimization_enabled: bool = True

class WeaverForgeGitAgent:
    """Intelligent Git Agent with Weaver Forge Integration"""
    
    def __init__(self, config: WeaverForgeConfig = None):
        self.config = config or WeaverForgeConfig()
        self.weaver_system = WeaverMultiLayerSystem()
        self.gap_analyzer = OTELGapAnalyzer()
        self.otel_monitor = ClaudeCodeOTELMonitor()
        
        self.dx_metrics = DXMetrics(
            commit_frequency=0.0,
            branch_health=0.0,
            merge_success_rate=0.0,
            conflict_rate=0.0,
            deployment_speed=0.0,
            test_coverage=0.0,
            code_quality_score=0.0,
            developer_satisfaction=0.0,
            automation_efficiency=0.0
        )
        
        self.decision_history: List[GitAgentDecision] = []
        self.loop_iterations = 0
        self.start_time = time.time()
        
    async def start_auto_dx_loop(self, duration_minutes: int = 60):
        """Start the automated Developer Experience loop"""
        console.print(Panel("🤖 Starting Weaver Forge Git Agent Auto DX Loop", style="bold cyan"))
        
        end_time = time.time() + (duration_minutes * 60)
        
        # Initialize systems
        await self._initialize_weaver_forge()
        
        try:
            while time.time() < end_time:
                self.loop_iterations += 1
                
                console.print(f"[cyan]🔄 DX Loop Iteration {self.loop_iterations}[/cyan]")
                
                # Execute DX Loop phases
                for phase in DXLoopPhase:
                    await self._execute_dx_phase(phase)
                    await asyncio.sleep(1)  # Brief pause between phases
                
                # Display current metrics
                self._display_dx_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30-second intervals
                
        except KeyboardInterrupt:
            console.print("[yellow]🛑 Auto DX Loop stopped by user[/yellow]")
        finally:
            await self._finalize_dx_loop()
    
    async def _initialize_weaver_forge(self):
        """Initialize Weaver Forge systems"""
        console.print("[cyan]⚙️ Initializing Weaver Forge Git Agent...[/cyan]")
        
        # Load semantic conventions
        semconv_path = Path(self.config.semantic_conventions_path)
        if semconv_path.exists():
            for yaml_file in semconv_path.glob("*.yaml"):
                try:
                    self.weaver_system.load_layer(yaml_file)
                    console.print(f"[green]✅ Loaded {yaml_file.name}[/green]")
                except Exception as e:
                    console.print(f"[red]❌ Failed to load {yaml_file}: {e}[/red]")
        
        # Initialize OTEL monitoring
        self.otel_monitor.start_monitoring()
        console.print("[green]✅ OTEL monitoring started[/green]")
        
        # Create git agent semantic conventions
        await self._create_git_agent_semconv()
    
    async def _create_git_agent_semconv(self):
        """Create semantic conventions for git agent operations"""
        git_agent_semconv = {
            "layer_type": "application",
            "version": "1.0.0",
            "metadata": {
                "name": "Git Agent Operations",
                "description": "Semantic conventions for Weaver Forge Git Agent automation"
            },
            "groups": [
                {
                    "id": "git_agent.decision",
                    "type": "span",
                    "span_kind": "internal",
                    "brief": "Git agent decision-making operations",
                    "attributes": [
                        {
                            "id": "git_agent.action",
                            "type": "string",
                            "requirement_level": "required",
                            "brief": "Action type being considered",
                            "examples": ["commit", "branch", "merge", "tag"]
                        },
                        {
                            "id": "git_agent.confidence",
                            "type": "double",
                            "requirement_level": "required",
                            "brief": "Confidence score for the decision (0.0-1.0)"
                        },
                        {
                            "id": "git_agent.phase",
                            "type": "string",
                            "requirement_level": "required",
                            "brief": "DX loop phase",
                            "examples": ["detection", "analysis", "planning", "execution"]
                        }
                    ]
                },
                {
                    "id": "git_agent.dx_loop",
                    "type": "span",
                    "span_kind": "internal",
                    "brief": "Developer Experience loop iteration",
                    "attributes": [
                        {
                            "id": "dx_loop.iteration",
                            "type": "int",
                            "requirement_level": "required",
                            "brief": "Loop iteration number"
                        },
                        {
                            "id": "dx_loop.metrics.commit_frequency",
                            "type": "double",
                            "requirement_level": "recommended",
                            "brief": "Commits per hour metric"
                        },
                        {
                            "id": "dx_loop.metrics.automation_efficiency",
                            "type": "double",
                            "requirement_level": "recommended",
                            "brief": "Automation efficiency score (0.0-1.0)"
                        }
                    ]
                }
            ]
        }
        
        # Save git agent semantic conventions
        semconv_file = Path("semconv_layers/git_agent_operations.yaml")
        semconv_file.parent.mkdir(exist_ok=True)
        with open(semconv_file, 'w') as f:
            yaml.dump(git_agent_semconv, f, default_flow_style=False)
        
        console.print(f"[green]✅ Created git agent semantic conventions: {semconv_file}[/green]")
    
    async def _execute_dx_phase(self, phase: DXLoopPhase):
        """Execute a specific phase of the DX loop"""
        console.print(f"[yellow]📋 Executing {phase.value.title()} Phase[/yellow]")
        
        if phase == DXLoopPhase.DETECTION:
            await self._detect_git_opportunities()
        elif phase == DXLoopPhase.ANALYSIS:
            await self._analyze_repository_state()
        elif phase == DXLoopPhase.PLANNING:
            await self._plan_git_actions()
        elif phase == DXLoopPhase.EXECUTION:
            await self._execute_git_actions()
        elif phase == DXLoopPhase.VALIDATION:
            await self._validate_git_operations()
        elif phase == DXLoopPhase.OPTIMIZATION:
            await self._optimize_dx_metrics()
        elif phase == DXLoopPhase.FEEDBACK:
            await self._collect_dx_feedback()
    
    async def _detect_git_opportunities(self):
        """Detect opportunities for git automation"""
        opportunities = []
        
        # Check for uncommitted changes
        result = await self._run_git_command("git status --porcelain")
        if result.returncode == 0 and result.stdout.strip():
            opportunities.append({
                "type": "uncommitted_changes",
                "priority": "high",
                "action": GitAgentAction.COMMIT,
                "files": len(result.stdout.strip().split('\n'))
            })
        
        # Check for unpushed commits
        result = await self._run_git_command("git log @{u}..HEAD --oneline")
        if result.returncode == 0 and result.stdout.strip():
            opportunities.append({
                "type": "unpushed_commits",
                "priority": "medium",
                "action": GitAgentAction.PUSH,
                "commits": len(result.stdout.strip().split('\n'))
            })
        
        # Check for stale branches
        result = await self._run_git_command("git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads")
        if result.returncode == 0:
            # Analyze branch staleness (simplified)
            branches = result.stdout.strip().split('\n')
            if len(branches) > 5:  # More than 5 branches
                opportunities.append({
                    "type": "branch_cleanup",
                    "priority": "low",
                    "action": GitAgentAction.ANALYZE,
                    "branches": len(branches)
                })
        
        console.print(f"[dim]🔍 Detected {len(opportunities)} git opportunities[/dim]")
        return opportunities
    
    async def _analyze_repository_state(self):
        """Analyze current repository state"""
        state = {}
        
        # Repository health metrics
        commands = [
            ("commit_count", "git rev-list --count HEAD"),
            ("branch_count", "git branch -a | wc -l"),
            ("tag_count", "git tag --list | wc -l"),
            ("remote_count", "git remote | wc -l"),
            ("current_branch", "git branch --show-current"),
            ("repo_size", "git count-objects -vH")
        ]
        
        for metric, command in commands:
            result = await self._run_git_command(command)
            if result.returncode == 0:
                state[metric] = result.stdout.strip()
        
        # Update DX metrics based on repository state
        await self._update_dx_metrics_from_state(state)
        
        console.print(f"[dim]📊 Analyzed repository state: {len(state)} metrics[/dim]")
        return state
    
    async def _plan_git_actions(self):
        """Plan git actions based on analysis"""
        planned_actions = []
        
        # Get repository opportunities
        opportunities = await self._detect_git_opportunities()
        
        for opportunity in opportunities:
            confidence = self._calculate_action_confidence(opportunity)
            
            if confidence >= self.config.min_confidence:
                decision = GitAgentDecision(
                    action=opportunity["action"],
                    phase=DXLoopPhase.PLANNING,
                    confidence=confidence,
                    reasoning=f"Detected {opportunity['type']} with {opportunity['priority']} priority",
                    commands=self._generate_commands_for_action(opportunity),
                    expected_outcome=f"Improved DX through {opportunity['action'].value}",
                    rollback_plan=self._generate_rollback_plan(opportunity)
                )
                planned_actions.append(decision)
        
        console.print(f"[dim]📋 Planned {len(planned_actions)} git actions[/dim]")
        return planned_actions
    
    async def _execute_git_actions(self):
        """Execute planned git actions"""
        executed_count = 0
        
        # Get planned actions
        planned_actions = await self._plan_git_actions()
        
        for decision in planned_actions:
            if self._should_execute_action(decision):
                try:
                    success = await self._execute_decision(decision)
                    if success:
                        executed_count += 1
                        self.decision_history.append(decision)
                        console.print(f"[green]✅ Executed: {decision.action.value}[/green]")
                    else:
                        console.print(f"[red]❌ Failed: {decision.action.value}[/red]")
                except Exception as e:
                    console.print(f"[red]💥 Error executing {decision.action.value}: {e}[/red]")
        
        console.print(f"[dim]⚡ Executed {executed_count} git actions[/dim]")
    
    async def _validate_git_operations(self):
        """Validate git operations were successful"""
        validation_results = {
            "repository_healthy": True,
            "commits_valid": True,
            "branches_clean": True,
            "remotes_synced": True
        }
        
        # Validate repository integrity
        result = await self._run_git_command("git fsck --no-progress")
        validation_results["repository_healthy"] = result.returncode == 0
        
        # Validate recent commits
        result = await self._run_git_command("git log --oneline -5")
        validation_results["commits_valid"] = result.returncode == 0 and result.stdout.strip()
        
        # Check for merge conflicts
        result = await self._run_git_command("git status --porcelain")
        validation_results["branches_clean"] = "UU " not in result.stdout
        
        all_valid = all(validation_results.values())
        status = "✅ Valid" if all_valid else "⚠️ Issues"
        console.print(f"[dim]🔍 Validation: {status}[/dim]")
        
        return validation_results
    
    async def _optimize_dx_metrics(self):
        """Optimize developer experience metrics"""
        optimizations = []
        
        # Analyze DX metrics for optimization opportunities
        if self.dx_metrics.commit_frequency < 1.0:  # Less than 1 commit per hour
            optimizations.append("increase_commit_frequency")
        
        if self.dx_metrics.automation_efficiency < 0.8:  # Less than 80% automation
            optimizations.append("improve_automation")
        
        if self.dx_metrics.conflict_rate > 0.1:  # More than 10% conflicts
            optimizations.append("reduce_conflicts")
        
        # Apply optimizations
        for optimization in optimizations:
            await self._apply_optimization(optimization)
        
        console.print(f"[dim]⚡ Applied {len(optimizations)} DX optimizations[/dim]")
    
    async def _collect_dx_feedback(self):
        """Collect feedback on developer experience"""
        feedback = {
            "loop_iteration": self.loop_iterations,
            "execution_time": time.time() - self.start_time,
            "decisions_made": len(self.decision_history),
            "success_rate": self._calculate_success_rate(),
            "dx_improvement": self._calculate_dx_improvement(),
            "recommendations": self._generate_recommendations()
        }
        
        # Store feedback for learning
        feedback_file = Path("weaver_forge_dx_feedback.json")
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                existing_feedback = json.load(f)
        else:
            existing_feedback = []
        
        existing_feedback.append(feedback)
        
        with open(feedback_file, 'w') as f:
            json.dump(existing_feedback, f, indent=2)
        
        console.print(f"[dim]📝 Collected DX feedback: {feedback['success_rate']:.1%} success rate[/dim]")
        
        return feedback
    
    async def _run_git_command(self, command: str) -> subprocess.CompletedProcess:
        """Run a git command and return the result"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            return result
        except Exception as e:
            console.print(f"[red]Error running command '{command}': {e}[/red]")
            return subprocess.CompletedProcess(command.split(), 1, "", str(e))
    
    def _calculate_action_confidence(self, opportunity: Dict[str, Any]) -> float:
        """Calculate confidence score for an action"""
        base_confidence = 0.5
        
        # Increase confidence based on opportunity type
        confidence_modifiers = {
            "uncommitted_changes": 0.3,
            "unpushed_commits": 0.2,
            "branch_cleanup": 0.1
        }
        
        confidence = base_confidence + confidence_modifiers.get(opportunity["type"], 0.0)
        
        # Adjust based on priority
        if opportunity["priority"] == "high":
            confidence += 0.2
        elif opportunity["priority"] == "medium":
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_commands_for_action(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate git commands for an action"""
        action = opportunity["action"]
        
        if action == GitAgentAction.COMMIT:
            return [
                "git add -A",
                "git commit -m 'feat(auto): automated commit by Weaver Forge Git Agent'"
            ]
        elif action == GitAgentAction.PUSH:
            return ["git push origin HEAD"]
        elif action == GitAgentAction.ANALYZE:
            return ["git status", "git log --oneline -10", "git branch -a"]
        
        return []
    
    def _generate_rollback_plan(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate rollback plan for an action"""
        action = opportunity["action"]
        
        if action == GitAgentAction.COMMIT:
            return ["git reset HEAD~1"]
        elif action == GitAgentAction.PUSH:
            return ["git reset --hard HEAD~1", "git push origin HEAD --force"]
        
        return []
    
    def _should_execute_action(self, decision: GitAgentDecision) -> bool:
        """Determine if an action should be executed"""
        if decision.confidence < self.config.min_confidence:
            return False
        
        # Check daily limits
        today_decisions = [d for d in self.decision_history 
                          if d.action == decision.action and 
                          time.time() - d.metadata.get("timestamp", 0) < 86400]
        
        if decision.action == GitAgentAction.COMMIT:
            return len(today_decisions) < self.config.max_daily_commits
        
        # Check configuration permissions
        if decision.action == GitAgentAction.COMMIT and not self.config.auto_commit:
            return False
        if decision.action == GitAgentAction.PUSH and not self.config.auto_push:
            return False
        if decision.action == GitAgentAction.MERGE and not self.config.auto_merge:
            return False
        
        return True
    
    async def _execute_decision(self, decision: GitAgentDecision) -> bool:
        """Execute a git agent decision"""
        decision.metadata["timestamp"] = time.time()
        
        for command in decision.commands:
            result = await self._run_git_command(command)
            if result.returncode != 0:
                console.print(f"[red]Command failed: {command}[/red]")
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False
        
        return True
    
    async def _update_dx_metrics_from_state(self, state: Dict[str, Any]):
        """Update DX metrics based on repository state"""
        # Calculate commit frequency (simplified)
        commit_count = int(state.get("commit_count", "0"))
        hours_elapsed = (time.time() - self.start_time) / 3600
        self.dx_metrics.commit_frequency = commit_count / max(hours_elapsed, 1)
        
        # Calculate automation efficiency
        automated_actions = len([d for d in self.decision_history if d.confidence > 0.8])
        total_actions = len(self.decision_history)
        self.dx_metrics.automation_efficiency = automated_actions / max(total_actions, 1)
        
        # Update other metrics (simplified)
        self.dx_metrics.branch_health = min(100 / max(int(state.get("branch_count", "1")), 1), 1.0)
        
    async def _apply_optimization(self, optimization: str):
        """Apply a specific DX optimization"""
        if optimization == "increase_commit_frequency":
            # Enable more aggressive auto-commit
            self.config.auto_commit = True
            self.config.min_confidence = max(self.config.min_confidence - 0.1, 0.5)
        elif optimization == "improve_automation":
            # Increase automation scope
            self.config.auto_branch = True
            self.config.auto_tag = True
        elif optimization == "reduce_conflicts":
            # Enable conflict prevention
            self.config.git_hooks_enabled = True
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate of git agent decisions"""
        if not self.decision_history:
            return 0.0
        
        successful = len([d for d in self.decision_history 
                         if d.metadata.get("timestamp", 0) > 0])
        return successful / len(self.decision_history)
    
    def _calculate_dx_improvement(self) -> float:
        """Calculate overall DX improvement"""
        metrics = [
            self.dx_metrics.commit_frequency / 10,  # Normalize to 0-1
            self.dx_metrics.automation_efficiency,
            self.dx_metrics.branch_health,
            1.0 - self.dx_metrics.conflict_rate  # Invert conflict rate
        ]
        return sum(metrics) / len(metrics)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for DX improvement"""
        recommendations = []
        
        if self.dx_metrics.commit_frequency < 0.5:
            recommendations.append("Consider more frequent commits for better tracking")
        
        if self.dx_metrics.automation_efficiency < 0.7:
            recommendations.append("Enable more automated git operations")
        
        if len(self.decision_history) < 5:
            recommendations.append("Allow git agent to make more autonomous decisions")
        
        return recommendations
    
    def _display_dx_metrics(self):
        """Display current DX metrics"""
        table = Table(title="Developer Experience Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Status", style="green")
        
        metrics = [
            ("Commit Frequency", f"{self.dx_metrics.commit_frequency:.2f}/hr", "🟢" if self.dx_metrics.commit_frequency > 1 else "🟡"),
            ("Automation Efficiency", f"{self.dx_metrics.automation_efficiency:.1%}", "🟢" if self.dx_metrics.automation_efficiency > 0.8 else "🟡"),
            ("Branch Health", f"{self.dx_metrics.branch_health:.1%}", "🟢" if self.dx_metrics.branch_health > 0.8 else "🟡"),
            ("Loop Iterations", str(self.loop_iterations), "🟢"),
            ("Decisions Made", str(len(self.decision_history)), "🟢"),
            ("Success Rate", f"{self._calculate_success_rate():.1%}", "🟢" if self._calculate_success_rate() > 0.8 else "🟡")
        ]
        
        for metric, value, status in metrics:
            table.add_row(metric, value, status)
        
        console.print(table)
    
    async def _finalize_dx_loop(self):
        """Finalize the DX loop and generate report"""
        console.print(Panel("📊 Weaver Forge Git Agent Auto DX Loop Complete", style="bold green"))
        
        # Generate final report
        report = {
            "execution_time": time.time() - self.start_time,
            "loop_iterations": self.loop_iterations,
            "decisions_made": len(self.decision_history),
            "success_rate": self._calculate_success_rate(),
            "dx_improvement": self._calculate_dx_improvement(),
            "final_metrics": {
                "commit_frequency": self.dx_metrics.commit_frequency,
                "automation_efficiency": self.dx_metrics.automation_efficiency,
                "branch_health": self.dx_metrics.branch_health
            },
            "recommendations": self._generate_recommendations()
        }
        
        # Save final report
        report_file = Path("weaver_forge_git_agent_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[green]📄 Final report saved to: {report_file}[/green]")
        
        # Stop OTEL monitoring
        self.otel_monitor.stop_monitoring()
        
        # Display final summary
        summary = f"""
🎯 **Weaver Forge Git Agent Summary:**
• Execution Time: {report['execution_time']:.1f} seconds
• Loop Iterations: {report['loop_iterations']}
• Decisions Made: {report['decisions_made']}
• Success Rate: {report['success_rate']:.1%}
• DX Improvement: {report['dx_improvement']:.1%}
• Automation Efficiency: {report['final_metrics']['automation_efficiency']:.1%}
"""
        
        console.print(Panel(summary, title="Auto DX Loop Results", border_style="green"))

async def main():
    """Main entry point for Weaver Forge Git Agent"""
    config = WeaverForgeConfig(
        auto_commit=True,
        auto_branch=True,
        auto_tag=True,
        min_confidence=0.7,
        max_daily_commits=20
    )
    
    agent = WeaverForgeGitAgent(config)
    await agent.start_auto_dx_loop(duration_minutes=5)

if __name__ == "__main__":
    asyncio.run(main())