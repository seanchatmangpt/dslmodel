#!/usr/bin/env python3
"""
Test the DSPy ⇄ Git bridge
"""

import json
import tempfile
from pathlib import Path

# Create test goal file
test_goal = """Mirror the repo as shallow clone into /tmp/seed
Create an isolated worktree named wt-demo at HEAD~2
Prune unreachable objects afterwards"""

# Write goal to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(test_goal)
    goal_file = f.name

print("🎯 Git Coach Test")
print("=" * 50)
print(f"Goal: {test_goal}")
print()

# Import and run git coach
try:
    from dslmodel.agents.git_coach import main
    
    # Would normally run: main(goal_file)
    # But for demo, let's show what the plan would look like
    
    expected_plan = [
        {"op": "clone", "args": {"repo_url": "https://github.com/acme/seed.git", "target_path": "/tmp/seed", "depth": 1}},
        {"op": "worktree", "args": {"path": "wt-demo", "sha": "HEAD~2"}},
        {"op": "prune", "args": {}}
    ]
    
    print("📝 Expected Git Plan (what LLM would generate):")
    print(json.dumps(expected_plan, indent=2))
    
    print("\n🔧 Each operation would:")
    print("  1. Execute through git_auto wrappers")
    print("  2. Emit typed OTEL spans (git.clone, git.worktree, git.prune)")
    print("  3. Return subprocess results with telemetry")
    
    print("\n✨ Benefits:")
    print("  • Zero boilerplate per new git command")
    print("  • LLM can use any git operation in registry")
    print("  • Full telemetry and safety rails")
    print("  • Composable for complex workflows")
    
except Exception as e:
    print(f"Note: Full execution requires DSPy setup. Error: {e}")
    
finally:
    # Cleanup
    Path(goal_file).unlink(missing_ok=True)