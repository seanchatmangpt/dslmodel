#!/usr/bin/env python3
"""Example usage of the coordination CLI showing 80/20 functionality"""

import subprocess
import json

def demo():
    """Demonstrate the core 80% functionality"""
    print("🚀 Coordination CLI Demo - 80/20 Functionality\n")
    
    # Core work management (80% of use cases)
    print("1. Core Work Management:")
    subprocess.run(['python', 'coordination_cli.py', 'work', 'claim', 'bug', 
                    'Memory leak in auth module', '--priority', 'critical', '--team', 'backend'])
    subprocess.run(['python', 'coordination_cli.py', 'work', 'claim', 'feature', 
                    'Add OAuth2 support', '--priority', 'high', '--team', 'backend'])
    subprocess.run(['python', 'coordination_cli.py', 'work', 'claim', 'refactor', 
                    'Clean up user service', '--priority', 'low'])
    
    print("\n2. View Active Work:")
    subprocess.run(['python', 'coordination_cli.py', 'work', 'list'])
    
    print("\n3. Team Dashboard:")
    subprocess.run(['python', 'coordination_cli.py', 'scrum', 'dashboard'])
    
    print("\n4. AI Analysis (stub for now):")
    subprocess.run(['python', 'coordination_cli.py', 'ai', 'priorities'])
    
    print("\n✨ This covers 80% of typical coordination needs!")
    print("   - Claim work items with priorities")
    print("   - List active work") 
    print("   - View team dashboard")
    print("   - AI-assisted prioritization (ready for real implementation)")

if __name__ == "__main__":
    demo()