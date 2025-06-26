#!/usr/bin/env python3
"""
Simplified Agent Coordination CLI - 80/20 Implementation
Core functionality without complex dependencies
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
COORDINATION_DIR = os.environ.get("COORDINATION_DIR", "/tmp/coordination")
os.makedirs(COORDINATION_DIR, exist_ok=True)

WORK_CLAIMS_FILE = os.path.join(COORDINATION_DIR, "work_claims.json")
FAST_CLAIMS_FILE = os.path.join(COORDINATION_DIR, "work_claims_fast.jsonl")

def generate_id(prefix):
    """Generate nanosecond-precision ID"""
    return f"{prefix}_{int(time.time() * 1e9)}"

def claim_work(work_type, description, priority="medium", team="autonomous_team", fast=True):
    """Claim work atomically"""
    agent_id = os.environ.get("AGENT_ID", generate_id("agent"))
    work_id = generate_id("work")
    
    print(f"🤖 Agent {agent_id} claiming work: {work_id}")
    
    claim_data = {
        "work_item_id": work_id,
        "agent_id": agent_id,
        "claimed_at": datetime.now().isoformat() + "Z",
        "work_type": work_type,
        "description": description,
        "priority": priority,
        "status": "active",
        "team": team
    }
    
    if fast:
        # Fast-path: Append to JSONL
        with open(FAST_CLAIMS_FILE, 'a') as f:
            f.write(json.dumps(claim_data) + '\n')
        print(f"✅ Fast-path claimed {work_id}")
    else:
        # Regular JSON update
        try:
            with open(WORK_CLAIMS_FILE, 'r') as f:
                claims = json.load(f)
        except:
            claims = []
        
        claims.append(claim_data)
        
        with open(WORK_CLAIMS_FILE, 'w') as f:
            json.dump(claims, f, indent=2)
        print(f"✅ Claimed {work_id}")
    
    print(f"   Type: {work_type}, Priority: {priority}, Team: {team}")
    os.environ["CURRENT_WORK_ITEM"] = work_id
    os.environ["AGENT_ID"] = agent_id

def show_dashboard():
    """Show coordination dashboard"""
    print("\n🚀 COORDINATION DASHBOARD")
    print("=" * 50)
    
    # Fast-path items
    fast_count = 0
    if os.path.exists(FAST_CLAIMS_FILE):
        with open(FAST_CLAIMS_FILE, 'r') as f:
            fast_items = [json.loads(line) for line in f if line.strip()]
        fast_count = len([i for i in fast_items if i.get("status") == "active"])
        print(f"\n⚡ Fast-path active items: {fast_count}")
    
    # Regular items
    regular_count = 0
    if os.path.exists(WORK_CLAIMS_FILE):
        with open(WORK_CLAIMS_FILE, 'r') as f:
            try:
                claims = json.load(f)
                regular_count = len([c for c in claims if c.get("status") == "active"])
            except:
                pass
    
    print(f"📊 Regular active items: {regular_count}")
    print(f"📈 Total active work: {fast_count + regular_count}")

def main():
    if len(sys.argv) < 2:
        print("Usage: coordination_cli_simple.py <command> [args...]")
        print("Commands: claim, dashboard")
        return
    
    command = sys.argv[1]
    
    if command == "claim":
        if len(sys.argv) < 4:
            print("Usage: claim <work_type> <description> [priority] [team]")
            return
        work_type = sys.argv[2]
        description = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
        team = sys.argv[5] if len(sys.argv) > 5 else "autonomous_team"
        claim_work(work_type, description, priority, team)
    
    elif command == "dashboard":
        show_dashboard()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()