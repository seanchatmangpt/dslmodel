#!/usr/bin/env python3
"""
Mock LLM Coordination Agent
Simulates intelligent decision-making without requiring external LLM services
Perfect for testing and demonstrating the coordination loop architecture
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from typer.testing import CliRunner
from coordination_cli_v2 import (
    app,
    generate_work_id,
    generate_agent_id,
    COORDINATION_DIR,
    WORK_CLAIMS_FILE,
    FAST_CLAIMS_FILE,
    Priority,
    WorkStatus
)

runner = CliRunner()

@dataclass
class CoordinationState:
    """Current state of the coordination system"""
    active_work_count: int
    completed_today: int
    team_distribution: Dict[str, int]
    priority_breakdown: Dict[str, int]
    avg_progress: float
    stale_items: int
    system_health: str
    file_sizes: Dict[str, float]

@dataclass
class MockLLMDecision:
    """Decision made by mock LLM with realistic reasoning"""
    action: str
    target: Optional[str]
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float

class MockLLMBrain:
    """Mock LLM that makes intelligent decisions using rule-based logic"""
    
    def __init__(self):
        self.work_templates = {
            "feature": [
                "Implement user authentication system",
                "Add real-time notifications",
                "Create dashboard analytics",
                "Build API rate limiting",
                "Develop file upload service"
            ],
            "bug": [
                "Fix memory leak in data processing",
                "Resolve login timeout issues",
                "Correct timezone handling bugs",
                "Fix race condition in async operations",
                "Resolve database connection pooling"
            ],
            "task": [
                "Update security dependencies",
                "Improve test coverage to 90%",
                "Refactor legacy authentication code",
                "Optimize database queries",
                "Document API endpoints"
            ],
            "refactor": [
                "Extract service layer from controllers",
                "Modernize frontend components",
                "Implement dependency injection",
                "Consolidate error handling",
                "Improve code modularity"
            ]
        }
        
        self.reasoning_patterns = {
            "claim_work": [
                "System is below optimal capacity, claiming {work_type} to balance workload",
                "Team {team} has capacity and specializes in {work_type} work",
                "Priority {priority} item needed to meet sprint goals",
                "Balancing work types - need more {work_type} to diversify portfolio"
            ],
            "update_progress": [
                "Standard progress increment based on work complexity and elapsed time",
                "Accelerated progress due to reduced complexity and team familiarity",
                "Slower progress due to unexpected technical challenges",
                "Steady progress with minor blockers that were resolved"
            ],
            "complete_work": [
                "Work meets completion criteria with {velocity} story points of complexity",
                "Quality standards satisfied, ready for deployment",
                "All acceptance criteria met, tests passing",
                "Technical debt minimized, documentation complete"
            ]
        }
    
    def analyze_system_state(self, state: CoordinationState) -> str:
        """Generate intelligent system analysis"""
        insights = []
        
        if state.active_work_count < 5:
            insights.append("Low work capacity detected - system underutilized")
        elif state.active_work_count > 15:
            insights.append("High work load - risk of bottlenecks")
        
        if state.avg_progress < 30:
            insights.append("Work items in early stages - need progress acceleration")
        elif state.avg_progress > 80:
            insights.append("Many items near completion - focus on finishing")
        
        # Analyze team distribution
        if state.team_distribution:
            max_team = max(state.team_distribution, key=state.team_distribution.get)
            min_team = min(state.team_distribution, key=state.team_distribution.get)
            if state.team_distribution[max_team] > state.team_distribution[min_team] * 2:
                insights.append(f"Work imbalance detected - {max_team} overloaded vs {min_team}")
        
        return "; ".join(insights) if insights else "System operating within normal parameters"
    
    def decide_work_claim(self, state: CoordinationState) -> Optional[MockLLMDecision]:
        """Intelligent work claiming decision"""
        if state.active_work_count >= 8:
            return None  # Don't claim if too much active work
        
        # Choose work type based on current distribution
        work_types = ["feature", "bug", "task", "refactor"]
        weights = [3, 4, 2, 1]  # Bias toward features and bugs
        
        work_type = random.choices(work_types, weights=weights)[0]
        
        # Choose priority based on system state
        if state.avg_progress > 70:
            priority = random.choices(["high", "medium", "low"], weights=[1, 2, 3])[0]
        else:
            priority = random.choices(["critical", "high", "medium"], weights=[1, 3, 2])[0]
        
        # Choose team based on current distribution
        teams = ["backend", "frontend", "qa", "devops", "security"]
        if state.team_distribution:
            # Prefer teams with less work
            team_weights = [max(1, 10 - state.team_distribution.get(team, 0)) for team in teams]
            team = random.choices(teams, weights=team_weights)[0]
        else:
            team = random.choice(teams)
        
        # Generate description
        description = random.choice(self.work_templates[work_type])
        
        # Generate reasoning
        reasoning = random.choice(self.reasoning_patterns["claim_work"]).format(
            work_type=work_type, team=team, priority=priority
        )
        
        return MockLLMDecision(
            action="claim_work",
            target=None,
            parameters={
                "work_type": work_type,
                "priority": priority,
                "team": team,
                "description": description
            },
            reasoning=reasoning,
            confidence=random.uniform(0.7, 0.9)
        )
    
    def decide_progress_update(self, work_item: Dict[str, Any]) -> MockLLMDecision:
        """Intelligent progress update decision"""
        current_progress = work_item.get("progress", 0)
        work_type = work_item.get("work_type", "task")
        
        # Calculate progress increment based on work type and current progress
        if work_type == "bug":
            base_increment = random.randint(15, 30)  # Bugs can be fixed quickly
        elif work_type == "feature":
            base_increment = random.randint(10, 25)  # Features take steady progress
        elif work_type == "refactor":
            base_increment = random.randint(5, 20)   # Refactoring is complex
        else:
            base_increment = random.randint(12, 28)  # Tasks vary
        
        # Apply complexity modifiers
        if current_progress < 25:
            # Early stages - setup and analysis
            increment = int(base_increment * 0.8)
        elif current_progress < 75:
            # Main development phase
            increment = base_increment
        else:
            # Final phase - testing and polish
            increment = int(base_increment * 0.6)
        
        # Add some randomness for realism
        increment += random.randint(-5, 5)
        new_progress = min(100, current_progress + increment)
        
        # Determine status
        if new_progress >= 90:
            status = "in_progress"  # Ready for final review
        elif new_progress >= 50:
            status = "in_progress"  # Active development
        else:
            status = "active"       # Early stages
        
        # Occasional blockers
        if random.random() < 0.1:  # 10% chance of blocker
            new_progress = current_progress  # No progress
            status = "blocked"
            reasoning = "Blocked by external dependency or technical challenge"
        else:
            reasoning = random.choice(self.reasoning_patterns["update_progress"])
        
        return MockLLMDecision(
            action="update_progress",
            target=work_item["work_item_id"],
            parameters={
                "progress": new_progress,
                "status": status
            },
            reasoning=reasoning,
            confidence=random.uniform(0.6, 0.8)
        )
    
    def decide_completion(self, work_item: Dict[str, Any]) -> Optional[MockLLMDecision]:
        """Intelligent completion decision"""
        progress = work_item.get("progress", 0)
        work_type = work_item.get("work_type", "task")
        
        # Only consider completion for high-progress items
        if progress < 85:
            return None
        
        # Completion probability based on progress
        completion_threshold = 90 if work_type in ["feature", "refactor"] else 95
        if progress < completion_threshold:
            return None
        
        # Calculate velocity points based on work type and complexity
        velocity_map = {
            "bug": random.choices([3, 5, 8], weights=[3, 2, 1])[0],
            "task": random.choices([2, 3, 5], weights=[2, 3, 1])[0],
            "feature": random.choices([5, 8, 13], weights=[2, 3, 1])[0],
            "refactor": random.choices([8, 13, 21], weights=[2, 2, 1])[0]
        }
        
        velocity = velocity_map.get(work_type, 5)
        
        # Determine success rate (higher for simpler work)
        success_rate = 0.95 if work_type in ["bug", "task"] else 0.90
        result = "success" if random.random() < success_rate else "partial"
        
        reasoning = random.choice(self.reasoning_patterns["complete_work"]).format(
            velocity=velocity
        )
        
        return MockLLMDecision(
            action="complete_work",
            target=work_item["work_item_id"],
            parameters={
                "velocity": velocity,
                "result": result
            },
            reasoning=reasoning,
            confidence=random.uniform(0.8, 0.95)
        )

class MockLLMCoordinationAgent:
    """Mock LLM coordination agent for testing and demonstration"""
    
    def __init__(self, 
                 max_iterations: int = None,
                 sleep_interval: int = 3,
                 claim_threshold: int = 5):
        
        self.brain = MockLLMBrain()
        self.agent_id = generate_agent_id()
        self.max_iterations = max_iterations
        self.sleep_interval = sleep_interval
        self.claim_threshold = claim_threshold
        
        # State tracking
        self.iteration = 0
        self.decision_history = []
        self.performance_metrics = {
            "decisions_made": 0,
            "work_claimed": 0,
            "work_completed": 0,
            "avg_confidence": 0.0,
            "reasoning_quality": []
        }
    
    def run_intelligent_loop(self):
        """Run the main mock LLM coordination loop"""
        print(f"🧠 Mock LLM Coordination Agent Started")
        print(f"   Agent: {self.agent_id}")
        print(f"   Mode: Intelligent decision simulation")
        print(f"   Settings: threshold={self.claim_threshold}, interval={self.sleep_interval}s")
        print("═" * 70)
        
        try:
            while self.should_continue():
                self.iteration += 1
                print(f"\n🔄 Cycle #{self.iteration} | {datetime.now().strftime('%H:%M:%S')}")
                print("─" * 50)
                
                # 1. Analyze current state
                state = self.analyze_system_state()
                
                # 2. Get mock LLM analysis and recommendations
                analysis = self.brain.analyze_system_state(state)
                print(f"🧠 System Analysis: {analysis}")
                
                decisions = self.get_intelligent_decisions(state)
                
                # 3. Execute decisions
                self.execute_decisions(decisions)
                
                # 4. Update metrics and context
                self.update_performance_metrics(decisions)
                
                # 5. Show cycle summary
                self.show_cycle_summary(state, decisions)
                
                if self.should_continue():
                    print(f"\n⏸️  Sleeping {self.sleep_interval}s...")
                    time.sleep(self.sleep_interval)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Mock LLM Agent stopped by user")
            self.show_final_summary()
    
    def analyze_system_state(self) -> CoordinationState:
        """Analyze current coordination system state"""
        print("📊 Analyzing system state...")
        
        # Get active work count
        active_count = self.get_active_work_count()
        
        # Analyze team distribution
        team_dist = self.analyze_team_distribution()
        
        # Get priority breakdown
        priority_breakdown = self.analyze_priority_breakdown()
        
        # Calculate average progress
        avg_progress = self.calculate_average_progress()
        
        # Check file sizes
        file_sizes = self.check_file_sizes()
        
        state = CoordinationState(
            active_work_count=active_count,
            completed_today=0,
            team_distribution=team_dist,
            priority_breakdown=priority_breakdown,
            avg_progress=avg_progress,
            stale_items=0,
            system_health="healthy" if active_count < 20 else "warning",
            file_sizes=file_sizes
        )
        
        print(f"   Active work: {active_count}")
        print(f"   Teams: {len(team_dist)} active")
        print(f"   Avg progress: {avg_progress:.1f}%")
        print(f"   System health: {state.system_health}")
        
        return state
    
    def get_intelligent_decisions(self, state: CoordinationState) -> List[MockLLMDecision]:
        """Get intelligent decisions from mock LLM"""
        decisions = []
        
        # 1. Decide on work claiming
        if state.active_work_count < self.claim_threshold:
            claim_decision = self.brain.decide_work_claim(state)
            if claim_decision:
                decisions.append(claim_decision)
        
        # 2. Decide on progress updates
        active_items = self.get_active_items()
        # Update 2-4 items per cycle
        items_to_update = random.sample(active_items, min(random.randint(2, 4), len(active_items)))
        
        for item in items_to_update:
            progress_decision = self.brain.decide_progress_update(item)
            decisions.append(progress_decision)
        
        # 3. Decide on completions
        high_progress_items = [item for item in active_items if item.get("progress", 0) >= 85]
        for item in high_progress_items:
            completion_decision = self.brain.decide_completion(item)
            if completion_decision:
                decisions.append(completion_decision)
        
        return decisions
    
    def execute_decisions(self, decisions: List[MockLLMDecision]):
        """Execute mock LLM decisions through the coordination CLI"""
        print(f"⚡ Executing {len(decisions)} intelligent decisions...")
        
        for i, decision in enumerate(decisions, 1):
            try:
                success = False
                if decision.action == "claim_work":
                    success = self.execute_claim_work(decision)
                elif decision.action == "update_progress":
                    success = self.execute_update_progress(decision)
                elif decision.action == "complete_work":
                    success = self.execute_complete_work(decision)
                
                # Track decision with outcome
                self.decision_history.append({
                    "iteration": self.iteration,
                    "action": decision.action,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.performance_metrics["decisions_made"] += 1
                
            except Exception as e:
                print(f"   ❌ Execution error for decision {i}: {e}")
    
    def execute_claim_work(self, decision: MockLLMDecision) -> bool:
        """Execute work claiming decision"""
        params = decision.parameters
        result = runner.invoke(app, [
            "claim", 
            params["work_type"], 
            params["description"],
            "--priority", params["priority"],
            "--team", params["team"]
        ])
        
        if result.exit_code == 0:
            print(f"   ✓ Claimed {params['work_type']} ({params['priority']}) for {params['team']}")
            print(f"     🧠 Reasoning: {decision.reasoning}")
            print(f"     📊 Confidence: {decision.confidence:.2f}")
            self.performance_metrics["work_claimed"] += 1
            return True
        else:
            print(f"   ❌ Failed to claim work: {result.stdout}")
            return False
    
    def execute_update_progress(self, decision: MockLLMDecision) -> bool:
        """Execute progress update decision"""
        params = decision.parameters
        result = runner.invoke(app, [
            "progress",
            decision.target,
            str(params["progress"])
        ])
        
        if result.exit_code == 0:
            status_emoji = "🚧" if params.get("status") == "blocked" else "📈"
            print(f"   {status_emoji} Updated {decision.target[:20]} to {params['progress']}%")
            if decision.confidence < 0.7:
                print(f"     ⚠️ Low confidence: {decision.reasoning}")
            return True
        else:
            print(f"   ❌ Failed to update progress: {result.stdout}")
            return False
    
    def execute_complete_work(self, decision: MockLLMDecision) -> bool:
        """Execute work completion decision"""
        params = decision.parameters
        result = runner.invoke(app, [
            "complete",
            decision.target,
            "--velocity", str(params["velocity"]),
            "--result", params["result"]
        ])
        
        if result.exit_code == 0:
            print(f"   ✅ Completed {decision.target[:20]} ({params['velocity']} pts, {params['result']})")
            print(f"     🧠 Reasoning: {decision.reasoning}")
            self.performance_metrics["work_completed"] += 1
            return True
        else:
            print(f"   ❌ Failed to complete work: {result.stdout}")
            return False
    
    def update_performance_metrics(self, decisions: List[MockLLMDecision]):
        """Update performance tracking metrics"""
        if decisions:
            # Track reasoning quality
            avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
            self.performance_metrics["reasoning_quality"].append(avg_confidence)
            
            # Update overall confidence
            if self.performance_metrics["reasoning_quality"]:
                self.performance_metrics["avg_confidence"] = sum(
                    self.performance_metrics["reasoning_quality"]
                ) / len(self.performance_metrics["reasoning_quality"])
    
    def show_cycle_summary(self, state: CoordinationState, decisions: List[MockLLMDecision]):
        """Show summary of current cycle"""
        print(f"\n💡 Cycle Summary:")
        print(f"   Active work: {state.active_work_count}")
        print(f"   Decisions executed: {len(decisions)}")
        print(f"   Avg confidence: {self.performance_metrics['avg_confidence']:.2f}")
        print(f"   System health: {state.system_health}")
        
        # Show decision breakdown
        if decisions:
            action_counts = {}
            for d in decisions:
                action_counts[d.action] = action_counts.get(d.action, 0) + 1
            
            print(f"   Decision types: {dict(action_counts)}")
            
            # Show high-confidence insights
            high_conf_decisions = [d for d in decisions if d.confidence > 0.8]
            if high_conf_decisions:
                print(f"   🎯 High-confidence insights:")
                for d in high_conf_decisions[:2]:
                    print(f"     • {d.action}: {d.reasoning[:70]}...")
    
    def show_final_summary(self):
        """Show final performance summary"""
        print(f"\n📊 Mock LLM Agent Final Summary")
        print("═" * 70)
        print(f"   Total cycles: {self.iteration}")
        print(f"   Decisions made: {self.performance_metrics['decisions_made']}")
        print(f"   Work claimed: {self.performance_metrics['work_claimed']}")
        print(f"   Work completed: {self.performance_metrics['work_completed']}")
        print(f"   Avg confidence: {self.performance_metrics['avg_confidence']:.2f}")
        
        # Calculate success rate
        successful_decisions = len([d for d in self.decision_history if d.get("success", False)])
        success_rate = successful_decisions / max(1, len(self.decision_history))
        print(f"   Decision success rate: {success_rate:.1%}")
        
        print(f"\n🧠 Reasoning Quality Analysis:")
        if self.performance_metrics["reasoning_quality"]:
            quality_trend = self.performance_metrics["reasoning_quality"]
            print(f"   Confidence trend: {quality_trend[0]:.2f} → {quality_trend[-1]:.2f}")
            print(f"   Quality variance: {max(quality_trend) - min(quality_trend):.2f}")
        
        print(f"\n🔍 Recent High-Quality Decisions:")
        high_quality = [d for d in self.decision_history[-10:] if d["confidence"] > 0.8]
        for decision in high_quality[:3]:
            print(f"   • Cycle {decision['iteration']}: {decision['action']} "
                  f"(conf: {decision['confidence']:.2f})")
            print(f"     Reasoning: {decision['reasoning'][:80]}...")
    
    # Helper methods (same as before)
    def get_active_work_count(self) -> int:
        count = 0
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                count += len([c for c in claims if c.get("status") != "completed"])
        return count
    
    def get_active_items(self) -> List[Dict[str, Any]]:
        items = []
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                items.extend([c for c in claims if c.get("status") != "completed"])
        return items
    
    def analyze_team_distribution(self) -> Dict[str, int]:
        distribution = {}
        for item in self.get_active_items():
            team = item.get("team", "unknown")
            distribution[team] = distribution.get(team, 0) + 1
        return distribution
    
    def analyze_priority_breakdown(self) -> Dict[str, int]:
        breakdown = {}
        for item in self.get_active_items():
            priority = item.get("priority", "medium")
            breakdown[priority] = breakdown.get(priority, 0) + 1
        return breakdown
    
    def calculate_average_progress(self) -> float:
        items = self.get_active_items()
        if not items:
            return 0.0
        total_progress = sum(item.get("progress", 0) for item in items)
        return total_progress / len(items)
    
    def check_file_sizes(self) -> Dict[str, float]:
        sizes = {}
        for file_path in [WORK_CLAIMS_FILE, FAST_CLAIMS_FILE]:
            if file_path.exists():
                sizes[file_path.name] = file_path.stat().st_size / 1024
        return sizes
    
    def should_continue(self) -> bool:
        if self.max_iterations is None:
            return True
        return self.iteration < self.max_iterations

def main():
    """Run mock LLM coordination test"""
    import sys
    
    # Parse arguments
    max_iterations = 8  # Default for demo
    sleep_interval = 3
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "infinite":
            max_iterations = None
            sleep_interval = 5
        elif sys.argv[1] == "quick":
            max_iterations = 3
            sleep_interval = 1
        else:
            max_iterations = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        sleep_interval = int(sys.argv[2])
    
    # Ensure coordination directory exists
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🧠 Mock LLM Coordination Agent")
    print("Simulates intelligent decision-making without external LLM dependencies")
    print("Usage: python mock_llm_coordination_agent.py [iterations|infinite|quick] [sleep_seconds]")
    print(f"       Iterations: {max_iterations or 'infinite'}")
    print(f"       Sleep: {sleep_interval}s")
    print("       Ctrl+C to stop\n")
    
    # Create and run agent
    agent = MockLLMCoordinationAgent(
        max_iterations=max_iterations,
        sleep_interval=sleep_interval,
        claim_threshold=5
    )
    
    agent.run_intelligent_loop()

if __name__ == "__main__":
    main()