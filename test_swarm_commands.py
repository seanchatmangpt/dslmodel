#!/usr/bin/env python3
"""
Comprehensive test loop for all SwarmAgent CLI commands.
Tests both direct CLI and poetry poe integration.
"""

import subprocess
import json
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any

def run_command(cmd: str, timeout: int = 30) -> Dict[str, Any]:
    """Run a command and capture output."""
    print(f"\n🔍 Testing: {cmd}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/Users/sac/dev/dslmodel"
        )
        
        duration = time.time() - start_time
        
        success = result.returncode == 0
        print(f"   {'✅' if success else '❌'} Exit code: {result.returncode} ({duration:.2f}s)")
        
        if result.stdout:
            print(f"   📤 STDOUT: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
        
        if result.stderr and not success:
            print(f"   📥 STDERR: {result.stderr[:200]}{'...' if len(result.stderr) > 200 else ''}")
        
        return {
            "command": cmd,
            "success": success,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": duration
        }
        
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT after {timeout}s")
        return {
            "command": cmd,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "duration": timeout
        }
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        return {
            "command": cmd,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0
        }

def verify_span_file() -> Dict[str, Any]:
    """Verify telemetry spans file exists and has content."""
    span_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
    
    if not span_file.exists():
        return {"exists": False, "count": 0, "size": 0}
    
    # Count spans
    span_count = 0
    try:
        with span_file.open() as f:
            for line in f:
                if line.strip():
                    try:
                        json.loads(line)
                        span_count += 1
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    
    return {
        "exists": True,
        "count": span_count,
        "size": span_file.stat().st_size,
        "path": str(span_file)
    }

def test_direct_cli_commands() -> List[Dict[str, Any]]:
    """Test direct swarm_cli.py commands."""
    print("\n" + "="*60)
    print("🧪 TESTING DIRECT CLI COMMANDS")
    print("="*60)
    
    commands = [
        "python swarm_cli.py --help",
        "python swarm_cli.py demo --scenario minimal",
        "python swarm_cli.py list",
        "python swarm_cli.py status",
        "python swarm_cli.py emit swarmsh.test.span --agent test --trigger manual",
        "python swarm_cli.py workflow governance --dry-run",
        "python swarm_cli.py workflow sprint --dry-run", 
        "python swarm_cli.py workflow improvement --dry-run",
        "python swarm_cli.py generate TestCLI --states INIT,WORK,DONE --triggers start,process,finish",
        "python swarm_cli.py watch --last 3"
    ]
    
    results = []
    for cmd in commands:
        result = run_command(cmd)
        results.append(result)
    
    return results

def test_poetry_commands() -> List[Dict[str, Any]]:
    """Test poetry poe commands."""
    print("\n" + "="*60)
    print("🧪 TESTING POETRY POE COMMANDS")
    print("="*60)
    
    commands = [
        "poetry run poe swarm",
        "poetry run poe swarm-demo",
        "poetry run poe swarm-status", 
        "poetry run poe swarm-list",
        "poetry run poe swarm-emit",
        "poetry run poe swarm-watch"
    ]
    
    results = []
    for cmd in commands:
        result = run_command(cmd, timeout=45)  # Longer timeout for poetry
        results.append(result)
    
    return results

def test_workflow_sequences() -> List[Dict[str, Any]]:
    """Test complete workflow sequences."""
    print("\n" + "="*60)
    print("🧪 TESTING WORKFLOW SEQUENCES")
    print("="*60)
    
    # Clean first
    run_command("python swarm_cli.py emit cleanup --agent system --trigger reset")
    
    sequences = [
        # Test init sequence
        "poetry run poe swarm-init",
        
        # Test cycle sequence
        "poetry run poe swarm-cycle"
    ]
    
    results = []
    for cmd in sequences:
        result = run_command(cmd, timeout=60)
        results.append(result)
        
        # Verify spans after each sequence
        span_info = verify_span_file()
        print(f"   📊 Spans: {span_info['count']} spans, {span_info['size']} bytes")
    
    return results

def test_telemetry_loop() -> Dict[str, Any]:
    """Test the complete telemetry loop."""
    print("\n" + "="*60)
    print("🧪 TESTING TELEMETRY LOOP")
    print("="*60)
    
    # 1. Check initial state
    span_info_before = verify_span_file()
    print(f"📊 Initial spans: {span_info_before['count']}")
    
    # 2. Emit test spans (simplified to avoid JSON escaping issues)
    test_spans = [
        "python swarm_cli.py emit swarmsh.roberts.open --agent roberts --trigger open",
        "python swarm_cli.py emit swarmsh.scrum.plan --agent scrum --trigger plan", 
        "python swarm_cli.py emit swarmsh.lean.define --agent lean --trigger define"
    ]
    
    for span_cmd in test_spans:
        result = run_command(span_cmd)
        if not result["success"]:
            return {"success": False, "error": f"Failed to emit span: {span_cmd}"}
    
    # 3. Check spans were created
    time.sleep(1)  # Allow file write
    span_info_after = verify_span_file()
    print(f"📊 Final spans: {span_info_after['count']}")
    
    # 4. Verify spans can be read
    watch_result = run_command("python swarm_cli.py watch --last 5")
    
    spans_created = span_info_after['count'] - span_info_before['count']
    
    return {
        "success": spans_created >= 3 and watch_result["success"],
        "spans_created": spans_created,
        "span_file_size": span_info_after['size'],
        "watch_success": watch_result["success"]
    }

def test_agent_generation() -> Dict[str, Any]:
    """Test agent generation functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING AGENT GENERATION")
    print("="*60)
    
    # Generate a test agent
    agent_name = f"TestAgent_{int(time.time())}"
    cmd = f"python swarm_cli.py generate {agent_name} --states IDLE,ACTIVE,COMPLETE --triggers start,work,finish"
    
    result = run_command(cmd)
    
    if not result["success"]:
        return {"success": False, "error": "Failed to generate agent"}
    
    # Check if file was created
    expected_file = Path(f"/Users/sac/dev/dslmodel/{agent_name.lower()}_agent.py")
    file_exists = expected_file.exists()
    
    file_content = ""
    if file_exists:
        try:
            file_content = expected_file.read_text()[:500]  # First 500 chars
        except Exception:
            pass
    
    return {
        "success": file_exists and len(file_content) > 100,
        "file_exists": file_exists,
        "file_path": str(expected_file),
        "content_length": len(file_content),
        "agent_name": agent_name
    }

def generate_test_report(all_results: Dict[str, Any]) -> str:
    """Generate a comprehensive test report."""
    
    # Count successes
    direct_cli_success = sum(1 for r in all_results["direct_cli"] if r["success"])
    direct_cli_total = len(all_results["direct_cli"])
    
    poetry_success = sum(1 for r in all_results["poetry"] if r["success"])
    poetry_total = len(all_results["poetry"])
    
    workflow_success = sum(1 for r in all_results["workflow"] if r["success"])
    workflow_total = len(all_results["workflow"])
    
    telemetry_success = all_results["telemetry"]["success"]
    agent_gen_success = all_results["agent_generation"]["success"]
    
    total_success = direct_cli_success + poetry_success + workflow_success + (1 if telemetry_success else 0) + (1 if agent_gen_success else 0)
    total_tests = direct_cli_total + poetry_total + workflow_total + 2
    
    # Calculate total duration
    total_duration = sum(r["duration"] for r in all_results["direct_cli"])
    total_duration += sum(r["duration"] for r in all_results["poetry"])
    total_duration += sum(r["duration"] for r in all_results["workflow"])
    
    report = f"""
🧪 SWARMAGENT CLI TEST REPORT
{'='*80}

📊 SUMMARY:
   Total Tests: {total_tests}
   Passed: {total_success} ✅
   Failed: {total_tests - total_success} ❌
   Success Rate: {(total_success/total_tests)*100:.1f}%
   Total Duration: {total_duration:.2f}s

📋 DETAILED RESULTS:

1️⃣  DIRECT CLI COMMANDS: {direct_cli_success}/{direct_cli_total} ✅
   """
    
    for result in all_results["direct_cli"]:
        status = "✅" if result["success"] else "❌"
        report += f"   {status} {result['command'][:50]}... ({result['duration']:.2f}s)\n"
    
    report += f"""
2️⃣  POETRY POE COMMANDS: {poetry_success}/{poetry_total} ✅
   """
    
    for result in all_results["poetry"]:
        status = "✅" if result["success"] else "❌"
        report += f"   {status} {result['command'][:50]}... ({result['duration']:.2f}s)\n"
    
    report += f"""
3️⃣  WORKFLOW SEQUENCES: {workflow_success}/{workflow_total} ✅
   """
    
    for result in all_results["workflow"]:
        status = "✅" if result["success"] else "❌"
        report += f"   {status} {result['command'][:50]}... ({result['duration']:.2f}s)\n"
    
    report += f"""
4️⃣  TELEMETRY LOOP: {'✅' if telemetry_success else '❌'}
   Spans Created: {all_results['telemetry'].get('spans_created', 0)}
   Span File Size: {all_results['telemetry'].get('span_file_size', 0)} bytes
   Watch Command: {'✅' if all_results['telemetry'].get('watch_success') else '❌'}

5️⃣  AGENT GENERATION: {'✅' if agent_gen_success else '❌'}
   File Created: {'✅' if all_results['agent_generation'].get('file_exists') else '❌'}
   Content Length: {all_results['agent_generation'].get('content_length', 0)} chars
   Agent Name: {all_results['agent_generation'].get('agent_name', 'N/A')}

📁 TELEMETRY FILE INFO:
   """
    
    span_info = verify_span_file()
    if span_info["exists"]:
        report += f"   ✅ File exists: {span_info['path']}\n"
        report += f"   📊 Total spans: {span_info['count']}\n"
        report += f"   📏 File size: {span_info['size']} bytes\n"
    else:
        report += "   ❌ Telemetry file not found\n"
    
    report += f"""
🎯 CONCLUSION:
   {'🎉 ALL TESTS PASSED!' if total_success == total_tests else f'⚠️  {total_tests - total_success} TESTS FAILED'}
   
   SwarmAgent CLI Integration: {'WORKING ✅' if total_success >= total_tests * 0.8 else 'NEEDS FIXES ❌'}
   Poetry Integration: {'WORKING ✅' if poetry_success >= poetry_total * 0.8 else 'NEEDS FIXES ❌'}
   Telemetry Loop: {'WORKING ✅' if telemetry_success else 'NEEDS FIXES ❌'}
"""
    
    return report

def main():
    """Run comprehensive test suite."""
    print("🚀 STARTING COMPREHENSIVE SWARMAGENT CLI TEST SUITE")
    print("="*80)
    
    all_results = {}
    
    # Test 1: Direct CLI commands
    all_results["direct_cli"] = test_direct_cli_commands()
    
    # Test 2: Poetry commands  
    all_results["poetry"] = test_poetry_commands()
    
    # Test 3: Workflow sequences
    all_results["workflow"] = test_workflow_sequences()
    
    # Test 4: Telemetry loop
    all_results["telemetry"] = test_telemetry_loop()
    
    # Test 5: Agent generation
    all_results["agent_generation"] = test_agent_generation()
    
    # Generate and display report
    report = generate_test_report(all_results)
    print(report)
    
    # Save report to file
    report_file = Path("swarm_cli_test_report.txt")
    report_file.write_text(report)
    print(f"\n📄 Report saved to: {report_file}")
    
    # Return success status
    total_tests = len(all_results["direct_cli"]) + len(all_results["poetry"]) + len(all_results["workflow"]) + 2
    total_success = (
        sum(1 for r in all_results["direct_cli"] if r["success"]) +
        sum(1 for r in all_results["poetry"] if r["success"]) +
        sum(1 for r in all_results["workflow"] if r["success"]) +
        (1 if all_results["telemetry"]["success"] else 0) +
        (1 if all_results["agent_generation"]["success"] else 0)
    )
    
    return total_success == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)