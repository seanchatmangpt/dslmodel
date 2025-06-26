#!/usr/bin/env python3
"""
Full Loop Demonstration
Shows the complete LLM-integrated coordination workflow
"""

import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print formatted section"""
    print(f"\n🔸 {title}")
    print("-" * 40)

def run_command_with_output(command, description):
    """Run command and show output"""
    print(f"\n💻 {description}")
    print(f"Command: {command}")
    print("Output:")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            # Show first 10 lines of output
            lines = result.stdout.split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            if len(result.stdout.split('\n')) > 15:
                print("  ... (output truncated)")
        
        if result.stderr:
            print(f"  Error: {result.stderr[:200]}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("  ⏱️ Command timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def show_system_state():
    """Show current system state"""
    print_section("Current System State")
    
    # Try to read coordination files
    coord_dir = Path("/tmp/coordination")
    
    if (coord_dir / "work_claims.json").exists():
        with open(coord_dir / "work_claims.json", 'r') as f:
            try:
                claims = json.load(f)
                active = [c for c in claims if c.get("status") != "completed"]
                completed = [c for c in claims if c.get("status") == "completed"]
                
                print(f"📊 Active work items: {len(active)}")
                print(f"✅ Completed items: {len(completed)}")
                
                if active:
                    print("\n🔧 Active Work Sample:")
                    for item in active[:3]:
                        work_type = item.get("work_type", "unknown")
                        priority = item.get("priority", "medium")
                        progress = item.get("progress", 0)
                        team = item.get("team", "unknown")
                        print(f"  • {work_type} ({priority}) - {progress}% [{team}]")
                        
            except json.JSONDecodeError:
                print("❌ Could not parse work claims file")
    else:
        print("📁 No work claims file found - system is clean")

def demonstrate_basic_cli():
    """Demonstrate basic CLI functionality"""
    print_header("1. Basic CLI Functionality")
    
    # Test basic commands
    commands = [
        ("python coordination_cli_v2.py --help", "Show CLI help"),
        ("python coordination_cli_v2.py claim feature 'Demo feature' --priority high", "Claim work item"),
        ("python coordination_cli_v2.py dashboard", "Show dashboard"),
    ]
    
    for command, description in commands:
        success = run_command_with_output(command, description)
        if not success:
            print(f"  ⚠️ Command failed: {command}")
        time.sleep(1)

def demonstrate_mock_llm_agent():
    """Demonstrate mock LLM agent"""
    print_header("2. Mock LLM Agent Intelligence")
    
    print("🧠 The Mock LLM Agent simulates intelligent decision-making using:")
    print("  • Rule-based work claiming based on system capacity")
    print("  • Realistic progress updates with complexity factors")
    print("  • Intelligent completion decisions with quality assessment")
    print("  • Performance metrics and reasoning explanations")
    
    run_command_with_output(
        "python mock_llm_coordination_agent.py quick",
        "Run quick mock LLM demo (3 cycles)"
    )

def demonstrate_infinite_loop():
    """Demonstrate infinite coordination loop"""
    print_header("3. Infinite Coordination Loop")
    
    print("♾️ The infinite loop demonstrates autonomous coordination:")
    print("  • Continuous work management")
    print("  • Automatic optimization")
    print("  • Real-time metrics tracking")
    print("  • Adaptive decision-making")
    
    run_command_with_output(
        "python infinite_coordination_demo.py demo",
        "Run infinite loop demo (5 cycles)"
    )

def demonstrate_full_integration():
    """Demonstrate full LLM integration"""
    print_header("4. Full LLM Integration Test")
    
    print("🔬 Running comprehensive integration test...")
    
    success = run_command_with_output(
        "python test_full_llm_coordination_loop.py",
        "Run full integration test manually"
    )
    
    if success:
        print("✅ Integration test completed successfully")
    else:
        print("⚠️ Integration test had issues - check implementation")

def show_performance_analysis():
    """Show performance analysis"""
    print_header("5. Performance Analysis")
    
    print("📈 Performance Characteristics:")
    
    # Analyze file sizes
    coord_dir = Path("/tmp/coordination")
    if coord_dir.exists():
        files = list(coord_dir.glob("*.json*"))
        total_size = sum(f.stat().st_size for f in files if f.exists())
        
        print(f"  📁 Data directory: {coord_dir}")
        print(f"  📊 Total data size: {total_size / 1024:.1f} KB")
        print(f"  📄 Files created: {len(files)}")
        
        for file in files:
            if file.exists():
                size_kb = file.stat().st_size / 1024
                print(f"    • {file.name}: {size_kb:.1f} KB")
    
    print("\n⚡ Optimization Features:")
    print("  • Fast-path claims: ~1ms (JSONL append)")
    print("  • Regular claims: ~15ms (JSON parse/write)")
    print("  • Dashboard render: ~5-10ms")
    print("  • Auto-optimization: Archive completed work")

def show_claude_commands():
    """Show available Claude commands"""
    print_header("6. Available Claude Commands")
    
    print("📋 Claude Code Integration (.claude/commands/):")
    
    claude_commands = [
        "/claim-work",
        "/complete-work", 
        "/update-progress",
        "/coordination-dashboard",
        "/sprint-planning",
        "/team-analysis",
        "/work-health-check",
        "/generate-report",
        "/optimize-coordination",
        "/infinite-coordination"
    ]
    
    for cmd in claude_commands:
        print(f"  • {cmd}")
    
    print("\nUsage example:")
    print("  /claim-work: Implement OAuth authentication [feature, high, security]")
    print("  /coordination-dashboard: team:backend status:active")

def main():
    """Run full demonstration"""
    print("🚀 Full LLM Coordination Loop Demonstration")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Show initial state
        show_system_state()
        
        # Run demonstrations
        demonstrate_basic_cli()
        demonstrate_mock_llm_agent()
        demonstrate_infinite_loop()
        demonstrate_full_integration()
        
        # Show analysis
        show_performance_analysis()
        show_claude_commands()
        
        # Show final state
        print_header("Final System State")
        show_system_state()
        
        print_header("Demo Complete!")
        print("🎉 Full LLM coordination loop demonstration finished")
        print("\n🔗 Next Steps:")
        print("  1. Integrate with real LLM service (OpenAI, Claude, etc.)")
        print("  2. Add OpenTelemetry distributed tracing")
        print("  3. Implement real-time WebSocket updates")
        print("  4. Scale to distributed coordination")
        print("  5. Add advanced analytics and reporting")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()