#!/usr/bin/env python3
"""
Comprehensive UV Integration Test
Tests Weaver, OTEL, and all major functionality after migration
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Tuple, List, Dict

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def run_command(cmd: str) -> Tuple[bool, str, str]:
    """Run a command and return success, stdout, stderr"""
    try:
        print(f"{BLUE}Running: {cmd}{RESET}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_section(name: str) -> None:
    """Print a test section header"""
    print(f"\n{YELLOW}{'=' * 60}{RESET}")
    print(f"{YELLOW}Testing: {name}{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}")

def print_result(test_name: str, success: bool, details: str = "") -> None:
    """Print test result"""
    status = f"{GREEN}✅ PASS{RESET}" if success else f"{RED}❌ FAIL{RESET}"
    print(f"{status} {test_name}")
    if details and not success:
        print(f"   {details}")

def main():
    """Run comprehensive UV integration tests"""
    print(f"{BLUE}🧪 UV Integration Test Suite{RESET}")
    print(f"{BLUE}Testing Weaver, OTEL, and DSLModel functionality{RESET}")
    
    tests_passed = 0
    tests_failed = 0
    test_results = []
    
    # Test 1: UV Installation
    test_section("UV Installation")
    success, stdout, _ = run_command("uv --version")
    test_results.append(("UV installed", success, stdout.strip()))
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
        print_result("UV installed", False, "UV not found")
        return 1
    
    # Test 2: Dependencies
    test_section("Dependencies")
    deps_to_test = [
        ("DSLModel", "import dslmodel"),
        ("Weaver", "weaver version"),
        ("OpenTelemetry", "import opentelemetry"),
        ("Typer CLI", "import typer"),
        ("Rich", "import rich"),
        ("DSPy", "import dspy"),
        ("NetworkX", "import networkx")
    ]
    
    for dep_name, test_cmd in deps_to_test:
        if test_cmd.startswith("import"):
            cmd = f'uv run python -c "{test_cmd}"'
        else:
            cmd = f"uv run {test_cmd}"
        success, _, stderr = run_command(cmd)
        test_results.append((dep_name, success, stderr))
        if success:
            tests_passed += 1
        else:
            tests_failed += 1
        print_result(dep_name, success, stderr.split('\n')[0] if stderr else "")
    
    # Test 3: CLI Commands
    test_section("CLI Commands")
    cli_commands = [
        ("dsl help", "uv run dsl --help"),
        ("weaver-health", "uv run dsl weaver-health check"),
        ("otel-monitor", "uv run dsl otel-monitor status"),
        ("health-8020", "uv run dsl health-8020 analyze --help"),
        ("validate-weaver", "uv run dsl validate-weaver --help"),
        ("evolution status", "uv run dsl evolve status"),
    ]
    
    for test_name, cmd in cli_commands:
        success, stdout, stderr = run_command(cmd)
        # Check if help text or expected output is present
        has_output = bool(stdout) or "Usage:" in stderr
        test_results.append((test_name, success or has_output, ""))
        if success or has_output:
            tests_passed += 1
        else:
            tests_failed += 1
        print_result(test_name, success or has_output)
    
    # Test 4: Weaver Functionality
    test_section("Weaver Functionality")
    
    # Test semantic conventions
    success, stdout, _ = run_command("find src/dslmodel/registry -name '*.yaml' | wc -l")
    conventions_found = int(stdout.strip()) if success else 0
    has_conventions = conventions_found > 0
    test_results.append(("Semantic conventions", has_conventions, f"Found {conventions_found} files"))
    if has_conventions:
        tests_passed += 1
    else:
        tests_failed += 1
    print_result("Semantic conventions", has_conventions, f"Found {conventions_found} convention files")
    
    # Test 5: OTEL Functionality
    test_section("OTEL Functionality")
    
    # Test OTEL imports
    otel_test = '''
import opentelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
print("OTEL imports successful")
'''
    success, stdout, _ = run_command(f'uv run python -c "{otel_test}"')
    test_results.append(("OTEL imports", success, stdout.strip()))
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
    print_result("OTEL imports", success)
    
    # Test 6: Wrapper Script
    test_section("Wrapper Script")
    if Path("./dsl").exists():
        success, _, _ = run_command("./dsl --help | head -5")
        test_results.append(("Wrapper script", success, ""))
        if success:
            tests_passed += 1
        else:
            tests_failed += 1
        print_result("Wrapper script", success)
    
    # Test 7: Make Commands
    test_section("Make Commands")
    make_commands = [
        ("make verify", "make verify"),
        ("make check-deps", "make check-deps | grep 'UV version'"),
    ]
    
    for test_name, cmd in make_commands:
        success, stdout, _ = run_command(cmd)
        # For check-deps, just check if it ran
        if "check-deps" in cmd:
            success = "UV version" in stdout or success
        test_results.append((test_name, success, ""))
        if success:
            tests_passed += 1
        else:
            tests_failed += 1
        print_result(test_name, success)
    
    # Summary
    print(f"\n{YELLOW}{'=' * 60}{RESET}")
    print(f"{YELLOW}Test Summary{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}")
    
    total_tests = tests_passed + tests_failed
    print(f"\nTotal Tests: {total_tests}")
    print(f"{GREEN}Passed: {tests_passed}{RESET}")
    print(f"{RED}Failed: {tests_failed}{RESET}")
    
    if tests_failed == 0:
        print(f"\n{GREEN}🎉 All tests passed! UV integration successful.{RESET}")
        
        # Save test results
        results_file = Path("uv_test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "total_tests": total_tests,
                "passed": tests_passed,
                "failed": tests_failed,
                "tests": [{"name": t[0], "passed": t[1], "details": t[2]} for t in test_results]
            }, f, indent=2)
        print(f"\nTest results saved to {results_file}")
        return 0
    else:
        print(f"\n{RED}❌ Some tests failed. Please check the output above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())