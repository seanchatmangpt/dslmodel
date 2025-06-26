#!/usr/bin/env python3
"""Test script for coordination_cli.py"""

import subprocess
import json
import time

def run_cmd(cmd):
    """Run command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def test_basic_workflow():
    """Test the 80/20 core functionality"""
    print("🧪 Testing coordination CLI...")
    
    # 1. Test help
    print("\n1️⃣ Testing help system...")
    out, code = run_cmd("python coordination_cli.py --help")
    assert code == 0 and "SwarmSH" in out
    print("✅ Help works")
    
    # 2. Test work claim
    print("\n2️⃣ Testing work claim...")
    out, code = run_cmd('python coordination_cli.py work claim task "Test task" --priority low')
    assert code == 0
    data = json.loads(out)
    work_id = data["work_item_id"]
    print(f"✅ Claimed work: {work_id}")
    
    # 3. Test work list
    print("\n3️⃣ Testing work list...")
    out, code = run_cmd("python coordination_cli.py work list")
    assert code == 0 and work_id in out
    print("✅ List shows active work")
    
    # 4. Test scrum dashboard
    print("\n4️⃣ Testing scrum dashboard...")
    out, code = run_cmd("python coordination_cli.py scrum dashboard")
    assert code == 0 and "Scrum Dashboard" in out
    print("✅ Dashboard displays")
    
    # 5. Test AI priorities
    print("\n5️⃣ Testing AI priorities...")
    out, code = run_cmd("python coordination_cli.py ai priorities")
    assert code == 0
    data = json.loads(out)
    assert "analysis" in data
    print("✅ AI priorities returns data")
    
    # 6. Test ID generation
    print("\n6️⃣ Testing ID generation...")
    out, code = run_cmd("python coordination_cli.py util generate-id")
    assert code == 0 and out.startswith("agent_")
    print(f"✅ Generated ID: {out}")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_basic_workflow()