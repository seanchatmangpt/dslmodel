#!/usr/bin/env python3
"""
Pre-commit hook for Weaver template/binding synchronization
Prevents prompt version drift by validating and regenerating bindings
"""

import subprocess
import sys
from pathlib import Path


def check_weaver_sync() -> bool:
    """Check if Weaver templates and bindings are synchronized"""
    repo_root = Path.cwd()
    
    # Check if any Weaver-related files changed
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    
    changed_files = result.stdout.strip().split('\n')
    weaver_changed = any(
        'weaver/templates' in f or 'semantic_conventions' in f or 'registry' in f
        for f in changed_files if f
    )
    
    if not weaver_changed:
        return True
    
    print("🧵 Weaver files changed, validating and regenerating...")
    
    # Run forge validate using uv run to ensure correct environment
    validate_result = subprocess.run(
        ["uv", "run", "python", "-m", "dslmodel.cli", "weaver", "validate"],
        capture_output=True,
        text=True
    )
    
    if validate_result.returncode != 0:
        print("❌ Weaver validation failed:")
        print(validate_result.stderr)
        return False
    
    # Run forge generate using uv run to ensure correct environment
    generate_result = subprocess.run(
        ["uv", "run", "python", "-m", "dslmodel.cli", "weaver", "generate"],
        capture_output=True,
        text=True
    )
    
    if generate_result.returncode != 0:
        print("❌ Weaver generation failed:")
        print(generate_result.stderr)
        return False
    
    # Auto-stage generated files
    subprocess.run(["git", "add", "src/dslmodel/generated/"])
    
    print("✅ Weaver templates and bindings synchronized")
    return True


if __name__ == "__main__":
    if not check_weaver_sync():
        sys.exit(1)
    sys.exit(0)