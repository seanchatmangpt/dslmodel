#!/usr/bin/env python3
"""
Demo script for Agent Coordination CLI v2.0
Shows 80/20 implementation in action
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd):
    """Run a coordination CLI command"""
    print(f"\n🚀 Running: {cmd}")
    result = subprocess.run(f"python coordination_cli_v2.py {cmd}", 
                          shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"⚠️  Error: {result.stderr}")
    return result

def main():
    print("=" * 60)
    print("AGENT COORDINATION CLI v2.0 - 80/20 DEMO")
    print("=" * 60)
    
    # 1. Show help
    print("\n1️⃣  HELP COMMAND:")
    run_command("--help")
    
    # 2. Claim some work (fast-path)
    print("\n2️⃣  CLAIMING WORK (Fast-path):")
    run_command('claim "feature" "Implement user authentication" --priority high --team security')
    run_command('claim "bug" "Fix login timeout issue" --priority critical')
    run_command('claim "task" "Update documentation" --priority low --team docs')
    
    # 3. Show dashboard
    print("\n3️⃣  DASHBOARD VIEW:")
    run_command("dashboard")
    
    # 4. Update progress
    print("\n4️⃣  UPDATING PROGRESS:")
    # First, we need to get a work ID - let's read from the fast claims file
    coord_dir = Path("/Users/sac/dev/ai-self-sustaining-system/agent_coordination")
    fast_file = coord_dir / "work_claims_fast.jsonl"
    
    if fast_file.exists():
        with open(fast_file, 'r') as f:
            first_line = f.readline()
            if first_line:
                work_item = json.loads(first_line)
                work_id = work_item["work_item_id"]
                run_command(f'progress "{work_id}" 50')
                run_command(f'progress "{work_id}" 75 --status in_progress')
    
    # 5. List work with filters
    print("\n5️⃣  LISTING WORK:")
    run_command("list-work")
    run_command("list-work --team security")
    run_command("list-work --status active")
    
    # 6. Complete work
    print("\n6️⃣  COMPLETING WORK:")
    if 'work_id' in locals():
        run_command(f'complete "{work_id}" --result success --velocity 8')
    
    # 7. Final dashboard
    print("\n7️⃣  FINAL DASHBOARD:")
    run_command("dashboard")
    
    # 8. Optimize (archive completed)
    print("\n8️⃣  OPTIMIZATION:")
    run_command("optimize")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()