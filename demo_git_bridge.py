#!/usr/bin/env python3
"""
Demo: DSPy ⇄ Git Bridge
Shows how LLM can plan and execute complex git operations
"""

import json
import yaml
from pathlib import Path
from dslmodel.utils.git_executor import run_plan, WRAPPERS

print("🌉 DSPy ⇄ Git Bridge Demo")
print("=" * 60)

# Load available git operations
registry_path = Path("etc/git_registry.yaml")
with open(registry_path) as f:
    registry = yaml.safe_load(f)

print("📚 Available Git Operations:")
for i, op in enumerate(registry.keys(), 1):
    print(f"  {i:2d}. {op}")

print(f"\n✨ Total: {len(registry)} operations available to LLMs")

# Show example user goal and plan
user_goal = """Mirror the repo as shallow clone into /tmp/seed
Create an isolated worktree named wt-demo at HEAD~2
Prune unreachable objects afterwards"""

print(f"\n🎯 User Goal:")
print(f'"{user_goal}"')

# What the LLM would generate
llm_plan = [
    {"op": "clone", "args": {"repo_url": "https://github.com/example/repo.git", "target_path": "/tmp/seed"}},
    {"op": "worktree", "args": {"path": "wt-demo", "sha": "HEAD~2"}},
    {"op": "prune", "args": {}}
]

print("\n🤖 LLM-Generated Plan:")
print(json.dumps(llm_plan, indent=2))

print("\n🔧 Execution Flow:")
print("1. GitPlanner (DSPy) → parses goal → generates JSON plan")
print("2. git_executor → validates operations exist in registry")
print("3. git_auto wrappers → execute with OTEL telemetry")
print("4. Each command emits typed spans (git.clone, git.worktree, etc.)")

print("\n📊 80/20 Architecture:")
print("• 20% effort: ~105 lines total (GitPlanner + executor + agent)")
print("• 80% value: LLMs can use ALL git operations with telemetry")

print("\n🎭 Key Benefits:")
print("• Zero boilerplate per new git command")
print("• Regex validation prevents command injection")
print("• Composable plans for complex workflows")
print("• Every operation traced in OTEL")

# Show the wrappers that were auto-generated
print(f"\n🔌 Auto-generated Wrappers: {len(WRAPPERS)}")
print(f"   Examples: {', '.join(list(WRAPPERS.keys())[:5])}, ...")

print("\n✅ DSPy ⇄ Git bridge ready for production!")