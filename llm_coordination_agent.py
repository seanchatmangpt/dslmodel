#!/usr/bin/env python3
"""
LLM-Integrated Coordination Agent
Demonstrates intelligent autonomous coordination using LLM decision-making
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import dspy
from typer.testing import CliRunner

# Simple init_lm function for this test
def init_lm(model: str = "ollama/qwen3", **kwargs) -> dspy.LM:
    """Initialize language model"""
    return dspy.LM(model=model, **kwargs)

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
class LLMDecision:
    """Decision made by LLM with reasoning"""
    action: str
    target: Optional[str]
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float

class CoordinationAnalyzer(dspy.Signature):
    """Analyze coordination system state and recommend actions"""
    
    system_state = dspy.InputField(desc="Current coordination system state as JSON")
    context = dspy.InputField(desc="Historical context and previous decisions")
    
    analysis = dspy.OutputField(desc="System analysis with insights")
    recommendations = dspy.OutputField(desc="Specific action recommendations as JSON")
    reasoning = dspy.OutputField(desc="Detailed reasoning for decisions")

class WorkClaimDecider(dspy.Signature):
    """Decide what work to claim based on system analysis"""
    
    system_state = dspy.InputField(desc="Current system state")
    available_work_types = dspy.InputField(desc="Available work types and priorities")
    team_capacity = dspy.InputField(desc="Current team capacity and workload")
    
    should_claim = dspy.OutputField(desc="Boolean: should claim new work")
    work_type = dspy.OutputField(desc="Type of work to claim")
    priority = dspy.OutputField(desc="Priority level to assign")
    team = dspy.OutputField(desc="Team to assign work to")
    description = dspy.OutputField(desc="Specific work description")
    reasoning = dspy.OutputField(desc="Reasoning for this decision")

class ProgressUpdater(dspy.Signature):
    """Decide how to update progress on active work"""
    
    work_item = dspy.InputField(desc="Work item details and current progress")
    elapsed_time = dspy.InputField(desc="Time since last update")
    complexity_factors = dspy.InputField(desc="Factors affecting work complexity")
    
    new_progress = dspy.OutputField(desc="New progress percentage (0-100)")
    status = dspy.OutputField(desc="Work status (active, in_progress, blocked)")
    reasoning = dspy.OutputField(desc="Reasoning for progress update")
    blockers = dspy.OutputField(desc="Any identified blockers or issues")

class CompletionDecider(dspy.Signature):
    """Decide if work is ready for completion"""
    
    work_item = dspy.InputField(desc="Work item at high progress")
    quality_indicators = dspy.InputField(desc="Quality and readiness indicators")
    team_standards = dspy.InputField(desc="Team completion standards")
    
    ready_to_complete = dspy.OutputField(desc="Boolean: ready for completion")
    velocity_points = dspy.OutputField(desc="Story points to assign (1-21)")
    result_status = dspy.OutputField(desc="Completion result (success, partial, failed)")
    reasoning = dspy.OutputField(desc="Reasoning for completion decision")

class LLMCoordinationAgent:
    """Intelligent coordination agent using LLM decision-making"""
    
    def __init__(self, 
                 model: str = "ollama/qwen3",
                 max_iterations: int = None,
                 sleep_interval: int = 10,
                 claim_threshold: int = 5):
        
        # Initialize LLM with init_lm helper
        self.lm = init_lm(model)
        dspy.settings.configure(lm=self.lm)
        
        # Initialize coordination modules
        self.analyzer = dspy.ChainOfThought(CoordinationAnalyzer)
        self.claim_decider = dspy.ChainOfThought(WorkClaimDecider)
        self.progress_updater = dspy.ChainOfThought(ProgressUpdater)
        self.completion_decider = dspy.ChainOfThought(CompletionDecider)
        
        # Agent configuration
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
            "avg_confidence": 0.0
        }
        
    def run_intelligent_loop(self):
        """Run the main LLM-integrated coordination loop"""
        print(f"🧠 LLM Coordination Agent Started")
        print(f"   Agent: {self.agent_id}")
        print(f"   Model: {self.lm.model}")
        print(f"   Settings: threshold={self.claim_threshold}, interval={self.sleep_interval}s")
        print("═" * 70)
        
        try:
            while self.should_continue():
                self.iteration += 1
                print(f"\n🔄 Cycle #{self.iteration} | {datetime.now().strftime('%H:%M:%S')}")
                print("─" * 50)
                
                # 1. Analyze current state
                state = self.analyze_system_state()
                
                # 2. Get LLM analysis and recommendations
                decisions = self.get_llm_recommendations(state)
                
                # 3. Execute decisions
                self.execute_decisions(decisions)
                
                # 4. Update metrics and context
                self.update_performance_metrics()
                
                # 5. Show cycle summary
                self.show_cycle_summary(state, decisions)
                
                if self.should_continue():
                    print(f"\n⏸️  Sleeping {self.sleep_interval}s...")
                    time.sleep(self.sleep_interval)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 LLM Agent stopped by user")
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
            completed_today=0,  # TODO: calculate from logs
            team_distribution=team_dist,
            priority_breakdown=priority_breakdown,
            avg_progress=avg_progress,
            stale_items=0,  # TODO: identify stale items
            system_health="healthy" if active_count < 50 else "warning",
            file_sizes=file_sizes
        )
        
        print(f"   Active work: {active_count}")
        print(f"   Avg progress: {avg_progress:.1f}%")
        print(f"   System health: {state.system_health}")
        
        return state
        
    def get_llm_recommendations(self, state: CoordinationState) -> List[LLMDecision]:
        """Get LLM analysis and action recommendations"""
        print("🧠 Getting LLM recommendations...")
        
        # Prepare context
        system_state_json = json.dumps({
            "active_work": state.active_work_count,
            "team_distribution": state.team_distribution,
            "priority_breakdown": state.priority_breakdown,
            "avg_progress": state.avg_progress,
            "system_health": state.system_health
        }, indent=2)
        
        context = json.dumps({
            "iteration": self.iteration,
            "recent_decisions": self.decision_history[-5:],
            "performance": self.performance_metrics
        }, indent=2)
        
        try:
            # Get overall analysis
            analysis_result = self.analyzer(
                system_state=system_state_json,
                context=context
            )
            
            print(f"   Analysis: {analysis_result.analysis[:100]}...")
            print(f"   Reasoning: {analysis_result.reasoning[:100]}...")
            
            decisions = []
            
            # Decide on work claiming
            if state.active_work_count < self.claim_threshold:
                claim_decision = self.decide_work_claim(state)
                if claim_decision:
                    decisions.append(claim_decision)
            
            # Decide on progress updates
            progress_decisions = self.decide_progress_updates(state)
            decisions.extend(progress_decisions)
            
            # Decide on completions
            completion_decisions = self.decide_completions(state)
            decisions.extend(completion_decisions)
            
            return decisions
            
        except Exception as e:
            print(f"   ⚠️ LLM error: {e}")
            return self.get_fallback_decisions(state)
    
    def decide_work_claim(self, state: CoordinationState) -> Optional[LLMDecision]:
        """Use LLM to decide what work to claim"""
        try:
            available_types = ["feature", "bug", "task", "refactor", "docs"]
            teams = list(state.team_distribution.keys()) or ["backend", "frontend", "qa"]
            
            result = self.claim_decider(
                system_state=json.dumps(state.__dict__),
                available_work_types=json.dumps(available_types),
                team_capacity=json.dumps(state.team_distribution)
            )
            
            if result.should_claim.lower() == "true":
                return LLMDecision(
                    action="claim_work",
                    target=None,
                    parameters={
                        "work_type": result.work_type,
                        "priority": result.priority,
                        "team": result.team,
                        "description": result.description
                    },
                    reasoning=result.reasoning,
                    confidence=0.8
                )
        except Exception as e:
            print(f"   ⚠️ Claim decision error: {e}")
            
        return None
    
    def decide_progress_updates(self, state: CoordinationState) -> List[LLMDecision]:
        """Use LLM to decide progress updates"""
        decisions = []
        active_items = self.get_active_items()
        
        # Update a few items each cycle
        items_to_update = random.sample(active_items, min(3, len(active_items)))
        
        for item in items_to_update:
            try:
                result = self.progress_updater(
                    work_item=json.dumps(item),
                    elapsed_time="1 cycle",
                    complexity_factors=json.dumps(["standard", "no_blockers"])
                )
                
                decisions.append(LLMDecision(
                    action="update_progress",
                    target=item["work_item_id"],
                    parameters={
                        "progress": int(result.new_progress),
                        "status": result.status
                    },
                    reasoning=result.reasoning,
                    confidence=0.7
                ))
                
            except Exception as e:
                print(f"   ⚠️ Progress decision error: {e}")
                # Fallback to simple increment
                current = item.get("progress", 0)
                new_progress = min(100, current + random.randint(10, 25))
                decisions.append(LLMDecision(
                    action="update_progress",
                    target=item["work_item_id"],
                    parameters={"progress": new_progress, "status": "in_progress"},
                    reasoning="Fallback increment due to LLM error",
                    confidence=0.3
                ))
        
        return decisions
    
    def decide_completions(self, state: CoordinationState) -> List[LLMDecision]:
        """Use LLM to decide what work to complete"""
        decisions = []
        ready_items = [item for item in self.get_active_items() 
                      if item.get("progress", 0) >= 90]
        
        for item in ready_items:
            try:
                result = self.completion_decider(
                    work_item=json.dumps(item),
                    quality_indicators=json.dumps(["tests_passing", "reviewed"]),
                    team_standards=json.dumps(["90%_complete", "quality_checked"])
                )
                
                if result.ready_to_complete.lower() == "true":
                    decisions.append(LLMDecision(
                        action="complete_work",
                        target=item["work_item_id"],
                        parameters={
                            "velocity": int(result.velocity_points),
                            "result": result.result_status
                        },
                        reasoning=result.reasoning,
                        confidence=0.8
                    ))
                    
            except Exception as e:
                print(f"   ⚠️ Completion decision error: {e}")
                # Auto-complete items at 100%
                if item.get("progress", 0) >= 100:
                    decisions.append(LLMDecision(
                        action="complete_work",
                        target=item["work_item_id"],
                        parameters={"velocity": 5, "result": "success"},
                        reasoning="Auto-complete at 100% due to LLM error",
                        confidence=0.5
                    ))
        
        return decisions
    
    def execute_decisions(self, decisions: List[LLMDecision]):
        """Execute LLM decisions through the coordination CLI"""
        print(f"⚡ Executing {len(decisions)} LLM decisions...")
        
        for decision in decisions:
            try:
                if decision.action == "claim_work":
                    self.execute_claim_work(decision)
                elif decision.action == "update_progress":
                    self.execute_update_progress(decision)
                elif decision.action == "complete_work":
                    self.execute_complete_work(decision)
                    
                # Track decision
                self.decision_history.append({
                    "iteration": self.iteration,
                    "action": decision.action,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning[:50] + "..."
                })
                
                self.performance_metrics["decisions_made"] += 1
                
            except Exception as e:
                print(f"   ❌ Execution error: {e}")
    
    def execute_claim_work(self, decision: LLMDecision):
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
            print(f"   ✓ Claimed {params['work_type']} for {params['team']}")
            print(f"     Reasoning: {decision.reasoning[:80]}...")
            self.performance_metrics["work_claimed"] += 1
        else:
            print(f"   ❌ Failed to claim work")
    
    def execute_update_progress(self, decision: LLMDecision):
        """Execute progress update decision"""
        params = decision.parameters
        result = runner.invoke(app, [
            "progress",
            decision.target,
            str(params["progress"])
        ])
        
        if result.exit_code == 0:
            print(f"   ✓ Updated {decision.target[:20]} to {params['progress']}%")
        else:
            print(f"   ❌ Failed to update progress")
    
    def execute_complete_work(self, decision: LLMDecision):
        """Execute work completion decision"""
        params = decision.parameters
        result = runner.invoke(app, [
            "complete",
            decision.target,
            "--velocity", str(params["velocity"]),
            "--result", params["result"]
        ])
        
        if result.exit_code == 0:
            print(f"   ✓ Completed {decision.target[:20]} ({params['velocity']} pts)")
            print(f"     Reasoning: {decision.reasoning[:80]}...")
            self.performance_metrics["work_completed"] += 1
        else:
            print(f"   ❌ Failed to complete work")
    
    def get_fallback_decisions(self, state: CoordinationState) -> List[LLMDecision]:
        """Generate fallback decisions when LLM fails"""
        decisions = []
        
        # Simple claiming fallback
        if state.active_work_count < self.claim_threshold:
            decisions.append(LLMDecision(
                action="claim_work",
                target=None,
                parameters={
                    "work_type": random.choice(["feature", "bug", "task"]),
                    "priority": "medium",
                    "team": "backend",
                    "description": f"Fallback work item {self.iteration}"
                },
                reasoning="Fallback decision due to LLM unavailability",
                confidence=0.2
            ))
        
        return decisions
    
    # Helper methods (reusing from previous implementation)
    def get_active_work_count(self) -> int:
        """Get count of active work items"""
        count = 0
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                count += len([c for c in claims if c.get("status") != "completed"])
        return count
    
    def get_active_items(self) -> List[Dict[str, Any]]:
        """Get list of active work items"""
        items = []
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                items.extend([c for c in claims if c.get("status") != "completed"])
        return items
    
    def analyze_team_distribution(self) -> Dict[str, int]:
        """Analyze work distribution across teams"""
        distribution = {}
        for item in self.get_active_items():
            team = item.get("team", "unknown")
            distribution[team] = distribution.get(team, 0) + 1
        return distribution
    
    def analyze_priority_breakdown(self) -> Dict[str, int]:
        """Analyze priority distribution"""
        breakdown = {}
        for item in self.get_active_items():
            priority = item.get("priority", "medium")
            breakdown[priority] = breakdown.get(priority, 0) + 1
        return breakdown
    
    def calculate_average_progress(self) -> float:
        """Calculate average progress across active items"""
        items = self.get_active_items()
        if not items:
            return 0.0
        total_progress = sum(item.get("progress", 0) for item in items)
        return total_progress / len(items)
    
    def check_file_sizes(self) -> Dict[str, float]:
        """Check file sizes in KB"""
        sizes = {}
        for file_path in [WORK_CLAIMS_FILE, FAST_CLAIMS_FILE]:
            if file_path.exists():
                sizes[file_path.name] = file_path.stat().st_size / 1024
        return sizes
    
    def update_performance_metrics(self):
        """Update performance tracking metrics"""
        if self.performance_metrics["decisions_made"] > 0:
            # Calculate average confidence from recent decisions
            recent_decisions = self.decision_history[-10:]
            if recent_decisions:
                avg_conf = sum(d["confidence"] for d in recent_decisions) / len(recent_decisions)
                self.performance_metrics["avg_confidence"] = avg_conf
    
    def show_cycle_summary(self, state: CoordinationState, decisions: List[LLMDecision]):
        """Show summary of current cycle"""
        print(f"\n💡 Cycle Summary:")
        print(f"   Active work: {state.active_work_count}")
        print(f"   Decisions made: {len(decisions)}")
        print(f"   Avg confidence: {self.performance_metrics['avg_confidence']:.2f}")
        print(f"   System health: {state.system_health}")
        
        if decisions:
            print(f"   Key decisions:")
            for d in decisions[:3]:
                print(f"     • {d.action}: {d.reasoning[:60]}...")
    
    def show_final_summary(self):
        """Show final performance summary"""
        print(f"\n📊 LLM Agent Final Summary")
        print("═" * 70)
        print(f"   Total cycles: {self.iteration}")
        print(f"   Decisions made: {self.performance_metrics['decisions_made']}")
        print(f"   Work claimed: {self.performance_metrics['work_claimed']}")
        print(f"   Work completed: {self.performance_metrics['work_completed']}")
        print(f"   Avg confidence: {self.performance_metrics['avg_confidence']:.2f}")
        
        print(f"\n🧠 Recent Decision History:")
        for decision in self.decision_history[-5:]:
            print(f"   Cycle {decision['iteration']}: {decision['action']} "
                  f"(conf: {decision['confidence']:.2f}) - {decision['reasoning']}")
    
    def should_continue(self) -> bool:
        """Check if loop should continue"""
        if self.max_iterations is None:
            return True
        return self.iteration < self.max_iterations

def main():
    """Run LLM-integrated coordination test"""
    import sys
    
    # Parse arguments
    model = "ollama/qwen3"  # Default model
    max_iterations = 5  # Default to 5 for testing
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "infinite":
            max_iterations = None
        else:
            max_iterations = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        model = sys.argv[2]
    
    # Ensure coordination directory exists
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🧠 LLM-Integrated Coordination Agent")
    print("Usage: python llm_coordination_agent.py [iterations|infinite] [model]")
    print(f"       Model: {model}")
    print(f"       Iterations: {max_iterations or 'infinite'}")
    print("       Ctrl+C to stop\n")
    
    # Create and run agent
    agent = LLMCoordinationAgent(
        model=model,
        max_iterations=max_iterations,
        sleep_interval=8,
        claim_threshold=5
    )
    
    agent.run_intelligent_loop()

if __name__ == "__main__":
    main()