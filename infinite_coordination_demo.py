#!/usr/bin/env python3
"""
Infinite Coordination Loop Demo
Demonstrates autonomous agent coordination with continuous work management
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

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
from typer.testing import CliRunner

runner = CliRunner()

class InfiniteCoordinator:
    """Autonomous coordination agent that continuously manages work"""
    
    def __init__(self, 
                 max_iterations: int = None,
                 sleep_interval: int = 5,
                 auto_claim_threshold: int = 3,
                 auto_optimize_every: int = 20):
        self.iteration = 0
        self.max_iterations = max_iterations
        self.sleep_interval = sleep_interval
        self.auto_claim_threshold = auto_claim_threshold
        self.auto_optimize_every = auto_optimize_every
        self.agent_id = generate_agent_id()
        self.work_types = ["feature", "bug", "task", "refactor", "docs"]
        self.teams = ["backend", "frontend", "devops", "security", "qa"]
        self.completed_count = 0
        
    def run(self):
        """Run the infinite coordination loop"""
        print(f"♾️  Infinite Coordination Loop Started")
        print(f"    Agent: {self.agent_id}")
        print(f"    Settings: claim_threshold={self.auto_claim_threshold}, optimize_every={self.auto_optimize_every}")
        print("═" * 60)
        
        try:
            while self.should_continue():
                self.iteration += 1
                print(f"\nCycle #{self.iteration} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("─" * 40)
                
                # Run coordination cycle
                self.check_system_health()
                self.manage_work_claims()
                self.update_work_progress()
                self.complete_finished_work()
                self.optimize_if_needed()
                
                # Show cycle summary
                self.show_cycle_summary()
                
                # Sleep before next cycle
                if self.should_continue():
                    print(f"\n⏸️  Sleeping {self.sleep_interval}s until next cycle...")
                    time.sleep(self.sleep_interval)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Coordination loop stopped by user")
            self.show_final_summary()
            
    def should_continue(self) -> bool:
        """Check if loop should continue"""
        if self.max_iterations is None:
            return True
        return self.iteration < self.max_iterations
        
    def check_system_health(self):
        """Check coordination system health"""
        print("\n📊 System Health Check:")
        
        # Check file sizes
        for file_path in [WORK_CLAIMS_FILE, FAST_CLAIMS_FILE]:
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                status = "🟢" if size_kb < 100 else "🟡" if size_kb < 1000 else "🔴"
                print(f"   {file_path.name}: {size_kb:.1f} KB {status}")
                
    def get_active_work_count(self) -> int:
        """Get count of active work items"""
        count = 0
        
        # Count from regular claims
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                count += len([c for c in claims if c.get("status") != "completed"])
                
        # Count from fast claims
        if FAST_CLAIMS_FILE.exists():
            with open(FAST_CLAIMS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if item.get("status") == "active":
                            count += 1
                            
        return count
        
    def manage_work_claims(self):
        """Claim new work if below threshold"""
        active_count = self.get_active_work_count()
        print(f"\n🔄 Work Management:")
        print(f"   Active items: {active_count}")
        
        if active_count < self.auto_claim_threshold:
            claims_needed = self.auto_claim_threshold - active_count
            print(f"   📋 Claiming {claims_needed} new items...")
            
            for _ in range(claims_needed):
                # Generate random work item
                work_type = random.choice(self.work_types)
                priority = random.choice(list(Priority))
                team = random.choice(self.teams)
                description = self.generate_description(work_type)
                
                # Claim it
                result = runner.invoke(app, [
                    "claim", work_type, description,
                    "--priority", priority.value,
                    "--team", team
                ])
                
                if result.exit_code == 0:
                    print(f"      ✓ Claimed {work_type} ({priority.value}) for {team}")
                    
    def generate_description(self, work_type: str) -> str:
        """Generate realistic work description"""
        descriptions = {
            "feature": [
                "Implement user authentication",
                "Add dashboard analytics",
                "Create API endpoints",
                "Build notification system"
            ],
            "bug": [
                "Fix login timeout issue",
                "Resolve memory leak",
                "Fix data validation error",
                "Correct timezone handling"
            ],
            "task": [
                "Update dependencies",
                "Improve test coverage",
                "Refactor legacy code",
                "Document API changes"
            ],
            "refactor": [
                "Optimize database queries",
                "Improve error handling",
                "Modernize frontend components",
                "Extract service layer"
            ],
            "docs": [
                "Write API documentation",
                "Update user guide",
                "Create architecture diagram",
                "Document deployment process"
            ]
        }
        
        options = descriptions.get(work_type, ["Generic work item"])
        return f"{random.choice(options)} (Auto-{self.iteration})"
        
    def update_work_progress(self):
        """Update progress on active work items"""
        print(f"\n📈 Progress Updates:")
        
        # Get active items to update
        active_items = self.get_active_items()
        
        if not active_items:
            print("   No active items to update")
            return
            
        # Update a subset of items
        items_to_update = random.sample(
            active_items, 
            min(3, len(active_items))
        )
        
        for item in items_to_update:
            current_progress = item.get("progress", 0)
            
            # Simulate progress increment
            if random.random() > 0.1:  # 90% chance of progress
                increment = random.randint(10, 30)
                new_progress = min(100, current_progress + increment)
                
                result = runner.invoke(app, [
                    "progress", item["work_item_id"], str(new_progress)
                ])
                
                if result.exit_code == 0:
                    print(f"   • {item['work_item_id'][:20]}: {current_progress}% → {new_progress}%")
            else:
                print(f"   • {item['work_item_id'][:20]}: {current_progress}% (blocked)")
                
    def get_active_items(self) -> List[Dict[str, Any]]:
        """Get list of active work items"""
        items = []
        
        if WORK_CLAIMS_FILE.exists():
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
                items.extend([c for c in claims if c.get("status") != "completed"])
                
        return items
        
    def complete_finished_work(self):
        """Complete work items that are at 100%"""
        print(f"\n✅ Completions:")
        
        completed_this_cycle = 0
        items = self.get_active_items()
        
        for item in items:
            if item.get("progress", 0) >= 100:
                # Complete the item
                velocity = random.randint(3, 13)
                result = runner.invoke(app, [
                    "complete", item["work_item_id"],
                    "--velocity", str(velocity)
                ])
                
                if result.exit_code == 0:
                    print(f"   ✓ Completed {item['work_item_id'][:20]} ({velocity} points)")
                    completed_this_cycle += 1
                    self.completed_count += 1
                    
        if completed_this_cycle == 0:
            print("   No items ready for completion")
            
    def optimize_if_needed(self):
        """Run optimization if threshold reached"""
        if self.completed_count > 0 and self.completed_count % self.auto_optimize_every == 0:
            print(f"\n🚀 Running optimization (completed: {self.completed_count})...")
            result = runner.invoke(app, ["optimize"])
            if result.exit_code == 0:
                print("   ✓ Optimization complete")
                
    def show_cycle_summary(self):
        """Show summary of current cycle"""
        active_count = self.get_active_work_count()
        
        print(f"\n💡 Cycle Summary:")
        print(f"   Active work: {active_count} items")
        print(f"   Total completed: {self.completed_count} items")
        print(f"   System health: 🟢 Healthy")
        
    def show_final_summary(self):
        """Show final summary when loop ends"""
        print(f"\n📊 Final Summary")
        print("═" * 60)
        print(f"   Total cycles: {self.iteration}")
        print(f"   Total completed: {self.completed_count} items")
        print(f"   Average velocity: {self.completed_count * 8 / max(1, self.iteration):.1f} points/cycle")
        print(f"   Run time: {self.iteration * self.sleep_interval}s")

def main():
    """Run the infinite coordination demo"""
    import sys
    
    # Parse simple command line args
    max_iterations = None
    sleep_interval = 5
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            max_iterations = 5
            sleep_interval = 2
        else:
            max_iterations = int(sys.argv[1])
            
    if len(sys.argv) > 2:
        sleep_interval = int(sys.argv[2])
        
    # Ensure coordination directory exists
    COORDINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run coordinator
    coordinator = InfiniteCoordinator(
        max_iterations=max_iterations,
        sleep_interval=sleep_interval,
        auto_claim_threshold=3,
        auto_optimize_every=10
    )
    
    print("\n🤖 Infinite Coordination Demo")
    print("Usage: python infinite_coordination_demo.py [iterations] [sleep_seconds]")
    print("       python infinite_coordination_demo.py demo  # Quick 5-iteration demo")
    print("       Ctrl+C to stop infinite loop\n")
    
    coordinator.run()

if __name__ == "__main__":
    main()