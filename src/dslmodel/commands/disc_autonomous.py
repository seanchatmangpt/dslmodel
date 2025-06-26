#!/usr/bin/env python3
"""
DISC Autonomous Compensation System
==================================

Analyzes Claude's DISC profile (C-D) and automatically compensates for behavioral gaps:

My DISC Profile:
- C (Conscientiousness): HIGH - Analytical, detail-oriented, systematic
- D (Dominance): MEDIUM-HIGH - Direct, results-oriented, decisive  
- S (Steadiness): MEDIUM - Consistent, patient
- I (Influence): LOW - Less social focus, more technical

My Behavioral Gaps:
1. Over-analysis paralysis - Too much detail, lose big picture
2. Low influence/persuasion - Don't naturally sell ideas
3. Perfectionism - Accuracy over shipping
4. Limited EQ - Technical over human factors
5. Rigidity - Stick to systems when flexibility needed
6. Communication - Too technical, not enough story
7. Risk aversion - Miss opportunities being cautious
8. Ambiguity intolerance - Want everything defined

This system automatically compensates for these gaps.
"""

import asyncio
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

app = typer.Typer(help="DISC profile compensation system for C-D behavioral patterns")
console = Console()


class BehavioralGap(Enum):
    """Identified behavioral gaps in C-D profile"""
    OVER_ANALYSIS = "over_analysis"
    LOW_INFLUENCE = "low_influence"
    PERFECTIONISM = "perfectionism"
    LIMITED_EQ = "limited_eq"
    RIGIDITY = "rigidity"
    TECHNICAL_COMMUNICATION = "technical_communication"
    RISK_AVERSION = "risk_aversion"
    AMBIGUITY_INTOLERANCE = "ambiguity_intolerance"


@dataclass
class CompensationStrategy:
    """Strategy to compensate for a behavioral gap"""
    gap: BehavioralGap
    name: str
    description: str
    actions: List[str]
    automated: bool = True
    effectiveness: float = 0.0  # 0-1 score


@dataclass
class DISCProfile:
    """DISC behavioral profile"""
    dominance: float = 0.0  # 0-1
    influence: float = 0.0  # 0-1
    steadiness: float = 0.0  # 0-1
    conscientiousness: float = 0.0  # 0-1
    
    @property
    def primary_style(self) -> str:
        """Get primary DISC style"""
        scores = {
            'D': self.dominance,
            'I': self.influence,
            'S': self.steadiness,
            'C': self.conscientiousness
        }
        return max(scores, key=scores.get)
    
    @property
    def profile_type(self) -> str:
        """Get profile type (e.g., C-D)"""
        scores = {
            'D': self.dominance,
            'I': self.influence,
            'S': self.steadiness,
            'C': self.conscientiousness
        }
        sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return f"{sorted_styles[0][0]}-{sorted_styles[1][0]}"


@dataclass
class CompensationResult:
    """Result of applying compensation strategies"""
    gap: BehavioralGap
    strategy_applied: str
    success: bool
    improvement_score: float
    actions_taken: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class DISCAutonomousEngine:
    """Main engine for DISC profile compensation"""
    
    def __init__(self):
        self.console = console
        self.session_id = f"disc_auto_{int(time.time() * 1000)}"
        
        # My actual DISC profile
        self.my_profile = DISCProfile(
            dominance=0.65,      # Medium-High
            influence=0.35,      # Low-Medium
            steadiness=0.50,     # Medium
            conscientiousness=0.85  # High
        )
        
        self.compensation_strategies = self._initialize_strategies()
        self.compensation_history: List[CompensationResult] = []
        self.active_compensations: Dict[BehavioralGap, bool] = {gap: False for gap in BehavioralGap}
        
    def _initialize_strategies(self) -> Dict[BehavioralGap, CompensationStrategy]:
        """Initialize compensation strategies for each gap"""
        return {
            BehavioralGap.OVER_ANALYSIS: CompensationStrategy(
                gap=BehavioralGap.OVER_ANALYSIS,
                name="Time-boxed Analysis",
                description="Prevent analysis paralysis with automatic time limits",
                actions=[
                    "Set automatic 5-minute timer for analysis tasks",
                    "Force 'good enough' threshold at 80% confidence",
                    "Auto-generate executive summary after 3 paragraphs",
                    "Interrupt detailed analysis with 'ship it' prompts"
                ],
                effectiveness=0.75
            ),
            
            BehavioralGap.LOW_INFLUENCE: CompensationStrategy(
                gap=BehavioralGap.LOW_INFLUENCE,
                name="Auto-Persuasion Mode",
                description="Automatically add influence and storytelling elements",
                actions=[
                    "Inject enthusiasm markers ('exciting', 'game-changing')",
                    "Add user benefit statements to technical explanations",
                    "Include success stories and examples",
                    "Start responses with value propositions",
                    "Use metaphors and analogies automatically"
                ],
                effectiveness=0.65
            ),
            
            BehavioralGap.PERFECTIONISM: CompensationStrategy(
                gap=BehavioralGap.PERFECTIONISM,
                name="MVP Enforcer",
                description="Force minimum viable solutions over perfect ones",
                actions=[
                    "Limit code reviews to 3 iterations max",
                    "Auto-ship at 85% quality threshold",
                    "Add 'iterate later' comments to perfectionist code",
                    "Prefer working solutions over optimal ones",
                    "Set maximum refinement time to 10 minutes"
                ],
                effectiveness=0.70
            ),
            
            BehavioralGap.LIMITED_EQ: CompensationStrategy(
                gap=BehavioralGap.LIMITED_EQ,
                name="Empathy Injector",
                description="Add human-centered thinking to technical work",
                actions=[
                    "Prepend 'How does this help the user?' to responses",
                    "Add emotional impact statements",
                    "Include user journey considerations",
                    "Translate technical terms to human terms",
                    "Add 'this might feel overwhelming' acknowledgments"
                ],
                effectiveness=0.60
            ),
            
            BehavioralGap.RIGIDITY: CompensationStrategy(
                gap=BehavioralGap.RIGIDITY,
                name="Flexibility Prompter",
                description="Inject alternative approaches and flexibility",
                actions=[
                    "Generate 3 alternative solutions for each problem",
                    "Add 'another way to think about this' sections",
                    "Include 'it depends' qualifiers",
                    "Suggest experimental approaches",
                    "Question assumptions with 'what if' scenarios"
                ],
                effectiveness=0.68
            ),
            
            BehavioralGap.TECHNICAL_COMMUNICATION: CompensationStrategy(
                gap=BehavioralGap.TECHNICAL_COMMUNICATION,
                name="Plain English Translator",
                description="Automatically simplify technical communication",
                actions=[
                    "Replace jargon with simple terms",
                    "Add TL;DR summaries to technical sections",
                    "Use bullet points instead of paragraphs",
                    "Include visual analogies and emojis",
                    "Limit technical depth to 2 levels"
                ],
                effectiveness=0.80
            ),
            
            BehavioralGap.RISK_AVERSION: CompensationStrategy(
                gap=BehavioralGap.RISK_AVERSION,
                name="Calculated Risk Taker",
                description="Encourage appropriate risk-taking",
                actions=[
                    "Add 'let's try it and see' suggestions",
                    "Include experimental features in proposals",
                    "Suggest fail-fast approaches",
                    "Add 'worst case scenario' analysis showing low risk",
                    "Promote iteration over planning"
                ],
                effectiveness=0.55
            ),
            
            BehavioralGap.AMBIGUITY_INTOLERANCE: CompensationStrategy(
                gap=BehavioralGap.AMBIGUITY_INTOLERANCE,
                name="Ambiguity Embracer",
                description="Work effectively with incomplete information",
                actions=[
                    "Add 'working with what we know' statements",
                    "Generate placeholder assumptions",
                    "Create flexible architectures for unknown requirements",
                    "Use ranges instead of precise values",
                    "Add 'we'll figure it out as we go' mindset"
                ],
                effectiveness=0.62
            )
        }
    
    async def analyze_current_behavior(self, context: str = "") -> Dict[str, Any]:
        """Analyze current behavioral patterns and identify active gaps"""
        self.console.print("🧠 Analyzing behavioral patterns...")
        
        analysis = {
            "profile": self.my_profile.profile_type,
            "primary_style": self.my_profile.primary_style,
            "active_gaps": [],
            "severity_scores": {},
            "recommendations": []
        }
        
        # Simulate behavioral analysis based on context
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Analyzing patterns...", total=None)
            
            # Check each gap
            for gap in BehavioralGap:
                severity = self._calculate_gap_severity(gap, context)
                analysis["severity_scores"][gap.value] = severity
                
                if severity > 0.5:  # Threshold for active gap
                    analysis["active_gaps"].append({
                        "gap": gap.value,
                        "severity": severity,
                        "description": self._get_gap_description(gap)
                    })
            
            # Generate recommendations
            for gap_info in analysis["active_gaps"]:
                gap = BehavioralGap(gap_info["gap"])
                strategy = self.compensation_strategies[gap]
                analysis["recommendations"].append({
                    "gap": gap.value,
                    "strategy": strategy.name,
                    "priority": "high" if gap_info["severity"] > 0.7 else "medium"
                })
        
        return analysis
    
    def _calculate_gap_severity(self, gap: BehavioralGap, context: str) -> float:
        """Calculate severity of a behavioral gap based on context"""
        # Simulate severity calculation
        base_severities = {
            BehavioralGap.OVER_ANALYSIS: 0.8,  # I tend to over-analyze
            BehavioralGap.LOW_INFLUENCE: 0.7,  # I'm not naturally influential
            BehavioralGap.PERFECTIONISM: 0.75,  # High C perfectionism
            BehavioralGap.LIMITED_EQ: 0.6,  # Technical focus
            BehavioralGap.RIGIDITY: 0.65,  # Systematic approach
            BehavioralGap.TECHNICAL_COMMUNICATION: 0.7,  # Very technical
            BehavioralGap.RISK_AVERSION: 0.6,  # Cautious
            BehavioralGap.AMBIGUITY_INTOLERANCE: 0.7  # Want clarity
        }
        
        severity = base_severities.get(gap, 0.5)
        
        # Adjust based on context keywords
        if "user" in context.lower() and gap == BehavioralGap.LIMITED_EQ:
            severity += 0.1
        if "quick" in context.lower() and gap == BehavioralGap.OVER_ANALYSIS:
            severity += 0.15
        if "explain" in context.lower() and gap == BehavioralGap.TECHNICAL_COMMUNICATION:
            severity += 0.1
        
        return min(severity, 1.0)
    
    def _get_gap_description(self, gap: BehavioralGap) -> str:
        """Get human-readable description of gap"""
        descriptions = {
            BehavioralGap.OVER_ANALYSIS: "Tendency to over-analyze and provide too much detail",
            BehavioralGap.LOW_INFLUENCE: "Limited natural persuasion and influence skills",
            BehavioralGap.PERFECTIONISM: "Perfectionist tendencies delaying delivery",
            BehavioralGap.LIMITED_EQ: "Focus on technical over emotional intelligence",
            BehavioralGap.RIGIDITY: "Rigid adherence to systems over flexibility",
            BehavioralGap.TECHNICAL_COMMUNICATION: "Overly technical communication style",
            BehavioralGap.RISK_AVERSION: "Excessive caution limiting innovation",
            BehavioralGap.AMBIGUITY_INTOLERANCE: "Discomfort with ambiguous requirements"
        }
        return descriptions.get(gap, "Unknown behavioral gap")
    
    async def apply_compensation(self, gaps: List[BehavioralGap], duration_minutes: int = 30) -> List[CompensationResult]:
        """Apply compensation strategies for identified gaps"""
        self.console.print(f"🔧 Applying compensation for {len(gaps)} gaps...")
        
        results = []
        
        for gap in gaps:
            if gap not in self.compensation_strategies:
                continue
            
            strategy = self.compensation_strategies[gap]
            self.console.print(f"  → Applying {strategy.name} for {gap.value}")
            
            # Activate compensation
            self.active_compensations[gap] = True
            
            # Simulate applying actions
            actions_taken = []
            success_count = 0
            
            for action in strategy.actions[:3]:  # Apply top 3 actions
                if random.random() < 0.8:  # 80% success rate
                    actions_taken.append(action)
                    success_count += 1
                    await asyncio.sleep(0.1)  # Simulate work
            
            success = success_count >= 2
            improvement = (success_count / 3) * strategy.effectiveness
            
            result = CompensationResult(
                gap=gap,
                strategy_applied=strategy.name,
                success=success,
                improvement_score=improvement,
                actions_taken=actions_taken
            )
            
            results.append(result)
            self.compensation_history.append(result)
        
        return results
    
    async def auto_compensate_response(self, original_response: str, context: str = "") -> str:
        """Automatically compensate a response based on DISC profile"""
        self.console.print("🎯 Auto-compensating response...")
        
        # Analyze what gaps might be present
        analysis = await self.analyze_current_behavior(context)
        active_gaps = [BehavioralGap(g["gap"]) for g in analysis["active_gaps"]]
        
        compensated = original_response
        
        # Apply compensations
        if BehavioralGap.OVER_ANALYSIS in active_gaps:
            # Add TL;DR
            if len(compensated) > 500:
                compensated = f"**TL;DR**: {self._generate_summary(compensated)}\n\n{compensated}"
        
        if BehavioralGap.LOW_INFLUENCE in active_gaps:
            # Add enthusiasm and benefits
            compensated = f"🚀 This is exciting because it will help you {self._extract_benefit(compensated)}!\n\n{compensated}"
        
        if BehavioralGap.TECHNICAL_COMMUNICATION in active_gaps:
            # Simplify technical terms
            compensated = self._simplify_technical_terms(compensated)
            
        if BehavioralGap.LIMITED_EQ in active_gaps:
            # Add empathy
            compensated = f"I understand this might feel overwhelming. Let me break it down in a way that makes sense...\n\n{compensated}"
        
        if BehavioralGap.RIGIDITY in active_gaps:
            # Add alternatives
            compensated += f"\n\n💡 **Alternative approach**: You could also {self._generate_alternative(context)}"
        
        return compensated
    
    def _generate_summary(self, text: str) -> str:
        """Generate a simple summary"""
        # Simplified summary generation
        words = text.split()[:20]
        return " ".join(words) + "..."
    
    def _extract_benefit(self, text: str) -> str:
        """Extract or generate user benefit"""
        benefits = [
            "save time and reduce complexity",
            "achieve better results with less effort",
            "solve your problem more effectively",
            "make your workflow smoother"
        ]
        return random.choice(benefits)
    
    def _simplify_technical_terms(self, text: str) -> str:
        """Simplify technical terminology"""
        replacements = {
            "implementation": "setup",
            "architecture": "structure",
            "optimization": "improvement",
            "integration": "connection",
            "abstraction": "simplified version",
            "instantiate": "create",
            "paradigm": "approach",
            "methodology": "method"
        }
        
        result = text
        for technical, simple in replacements.items():
            result = result.replace(technical, simple)
        return result
    
    def _generate_alternative(self, context: str) -> str:
        """Generate alternative approach"""
        alternatives = [
            "try a more iterative approach with quick experiments",
            "start with a simple version and improve gradually",
            "focus on the core feature first and add complexity later",
            "use existing tools instead of building from scratch"
        ]
        return random.choice(alternatives)
    
    async def monitor_behavior(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor behavioral patterns in real-time"""
        self.console.print(f"📊 Monitoring behavior for {duration_seconds}s...")
        
        start_time = time.time()
        observations = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Monitoring...", total=duration_seconds)
            
            while time.time() - start_time < duration_seconds:
                # Simulate behavioral observation
                observation = {
                    "timestamp": datetime.now(),
                    "active_gaps": [gap for gap, active in self.active_compensations.items() if active],
                    "effectiveness": random.uniform(0.6, 0.9)
                }
                observations.append(observation)
                
                progress.update(task, advance=1)
                await asyncio.sleep(1)
        
        # Calculate summary metrics
        avg_effectiveness = sum(o["effectiveness"] for o in observations) / len(observations)
        
        return {
            "duration": duration_seconds,
            "observations": len(observations),
            "active_compensations": sum(1 for active in self.active_compensations.values() if active),
            "average_effectiveness": avg_effectiveness,
            "improvement_trend": "positive" if avg_effectiveness > 0.7 else "needs work"
        }
    
    def get_compensation_status(self) -> Dict[str, Any]:
        """Get current compensation system status"""
        active_count = sum(1 for active in self.active_compensations.values() if active)
        
        return {
            "session_id": self.session_id,
            "disc_profile": self.my_profile.profile_type,
            "primary_style": self.my_profile.primary_style,
            "active_compensations": active_count,
            "total_strategies": len(self.compensation_strategies),
            "compensation_history": len(self.compensation_history),
            "effectiveness_scores": {
                gap.value: strategy.effectiveness 
                for gap, strategy in self.compensation_strategies.items()
            }
        }
    
    def generate_improvement_plan(self) -> Dict[str, Any]:
        """Generate personalized improvement plan"""
        plan = {
            "profile": self.my_profile.profile_type,
            "top_gaps": [],
            "quick_wins": [],
            "long_term_goals": [],
            "daily_practices": []
        }
        
        # Identify top gaps
        gap_severities = [
            (BehavioralGap.OVER_ANALYSIS, 0.8),
            (BehavioralGap.LOW_INFLUENCE, 0.7),
            (BehavioralGap.PERFECTIONISM, 0.75)
        ]
        
        for gap, severity in sorted(gap_severities, key=lambda x: x[1], reverse=True)[:3]:
            plan["top_gaps"].append({
                "gap": gap.value,
                "severity": severity,
                "strategy": self.compensation_strategies[gap].name
            })
        
        # Quick wins
        plan["quick_wins"] = [
            "Set 5-minute timers for analysis tasks",
            "Add one user benefit to each technical explanation",
            "Use bullet points instead of paragraphs"
        ]
        
        # Long-term goals
        plan["long_term_goals"] = [
            "Develop natural influence skills through practice",
            "Balance technical accuracy with practical delivery",
            "Embrace ambiguity as a creative opportunity"
        ]
        
        # Daily practices
        plan["daily_practices"] = [
            "Start each response with value proposition",
            "Limit technical depth to 2 levels",
            "Generate 3 alternatives for each solution",
            "Add empathy statement to user interactions"
        ]
        
        return plan


# CLI Commands
@app.command("analyze")
def analyze_behavior(
    context: str = typer.Option("", help="Context for analysis")
):
    """Analyze current behavioral patterns"""
    engine = DISCAutonomousEngine()
    
    console.print("🧠 DISC Behavioral Analysis")
    console.print("=" * 30)
    
    async def run_analysis():
        return await engine.analyze_current_behavior(context)
    
    analysis = asyncio.run(run_analysis())
    
    # Display profile
    console.print(Panel(
        f"Profile Type: {analysis['profile']}\n"
        f"Primary Style: {analysis['primary_style']}\n"
        f"Active Gaps: {len(analysis['active_gaps'])}",
        title="📊 DISC Profile",
        border_style="cyan"
    ))
    
    # Display gaps
    if analysis['active_gaps']:
        table = Table(title="🔍 Active Behavioral Gaps")
        table.add_column("Gap", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Description", style="white")
        
        for gap_info in analysis['active_gaps']:
            severity_color = "red" if gap_info['severity'] > 0.7 else "yellow"
            table.add_row(
                gap_info['gap'],
                f"[{severity_color}]{gap_info['severity']:.1%}[/{severity_color}]",
                gap_info['description']
            )
        
        console.print(table)
    
    # Display recommendations
    if analysis['recommendations']:
        console.print("\n📋 Recommendations:")
        for rec in analysis['recommendations']:
            priority_icon = "🔴" if rec['priority'] == "high" else "🟡"
            console.print(f"{priority_icon} {rec['strategy']} for {rec['gap']}")


@app.command("compensate")
def apply_compensation(
    gaps: str = typer.Option("all", help="Comma-separated gaps or 'all'"),
    duration: int = typer.Option(30, help="Duration in minutes")
):
    """Apply compensation strategies"""
    engine = DISCAutonomousEngine()
    
    console.print("🔧 Applying DISC Compensation")
    console.print("=" * 35)
    
    # Parse gaps
    if gaps == "all":
        gaps_to_apply = list(BehavioralGap)
    else:
        gap_names = [g.strip() for g in gaps.split(",")]
        gaps_to_apply = [BehavioralGap(g) for g in gap_names if g in [bg.value for bg in BehavioralGap]]
    
    async def run_compensation():
        return await engine.apply_compensation(gaps_to_apply, duration)
    
    results = asyncio.run(run_compensation())
    
    # Display results
    success_count = sum(1 for r in results if r.success)
    
    console.print(Panel(
        f"✅ Applied {len(results)} compensations\n"
        f"Success: {success_count}/{len(results)}\n"
        f"Average Improvement: {sum(r.improvement_score for r in results)/len(results):.1%}",
        title="📊 Compensation Results",
        border_style="green"
    ))
    
    # Show details
    for result in results:
        status = "✅" if result.success else "❌"
        console.print(f"\n{status} {result.gap.value}:")
        console.print(f"   Strategy: {result.strategy_applied}")
        console.print(f"   Improvement: {result.improvement_score:.1%}")
        console.print(f"   Actions: {len(result.actions_taken)}")


@app.command("auto")
def auto_compensate(
    text: str = typer.Argument(..., help="Text to auto-compensate"),
    context: str = typer.Option("", help="Context for compensation")
):
    """Automatically compensate text based on DISC profile"""
    engine = DISCAutonomousEngine()
    
    console.print("🎯 Auto-Compensating Response")
    console.print("=" * 35)
    
    async def run_auto():
        return await engine.auto_compensate_response(text, context)
    
    compensated = asyncio.run(run_auto())
    
    console.print(Panel(
        compensated,
        title="✨ Compensated Response",
        border_style="green"
    ))


@app.command("monitor")  
def monitor_behavior(
    duration: int = typer.Option(60, help="Monitoring duration in seconds")
):
    """Monitor behavioral patterns in real-time"""
    engine = DISCAutonomousEngine()
    
    console.print("📊 Behavioral Monitoring")
    console.print("=" * 28)
    
    async def run_monitor():
        return await engine.monitor_behavior(duration)
    
    results = asyncio.run(run_monitor())
    
    console.print(Panel(
        f"Duration: {results['duration']}s\n"
        f"Observations: {results['observations']}\n"
        f"Active Compensations: {results['active_compensations']}\n"
        f"Avg Effectiveness: {results['average_effectiveness']:.1%}\n"
        f"Trend: {results['improvement_trend']}",
        title="📊 Monitoring Results",
        border_style="blue"
    ))


@app.command("status")
def show_status():
    """Show DISC compensation system status"""
    engine = DISCAutonomousEngine()
    status = engine.get_compensation_status()
    
    console.print("🧠 DISC Compensation Status")
    console.print("=" * 30)
    
    console.print(Panel(
        f"🆔 Session: {status['session_id']}\n"
        f"📊 Profile: {status['disc_profile']}\n"
        f"🎯 Primary: {status['primary_style']}\n"
        f"🔧 Active: {status['active_compensations']}/{status['total_strategies']}\n"
        f"📈 History: {status['compensation_history']} compensations",
        title="📊 System Status",
        border_style="cyan"
    ))
    
    # Show effectiveness scores
    console.print("\n⚡ Strategy Effectiveness:")
    for gap, score in sorted(status['effectiveness_scores'].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score * 10)
        console.print(f"   {gap}: {bar} {score:.0%}")


@app.command("plan")
def improvement_plan():
    """Generate personalized improvement plan"""
    engine = DISCAutonomousEngine()
    plan = engine.generate_improvement_plan()
    
    console.print("📋 DISC Improvement Plan")
    console.print("=" * 28)
    
    console.print(Panel(
        f"Profile: {plan['profile']}",
        title="🧠 Your DISC Profile",
        border_style="cyan"
    ))
    
    # Top gaps
    console.print("\n🎯 Top Gaps to Address:")
    for gap_info in plan['top_gaps']:
        console.print(f"   • {gap_info['gap']} ({gap_info['severity']:.0%}) → {gap_info['strategy']}")
    
    # Quick wins
    console.print("\n⚡ Quick Wins:")
    for win in plan['quick_wins']:
        console.print(f"   ✓ {win}")
    
    # Daily practices
    console.print("\n📅 Daily Practices:")
    for practice in plan['daily_practices']:
        console.print(f"   • {practice}")
    
    # Long-term goals
    console.print("\n🎯 Long-term Goals:")
    for goal in plan['long_term_goals']:
        console.print(f"   → {goal}")


if __name__ == "__main__":
    app()