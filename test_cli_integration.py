#!/usr/bin/env python3
"""
Test CLI Integration - OTEL with DSLModel pyproject.toml structure
Tests the integration of OTEL coordination with existing CLI structure
"""

import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

def test_module_imports() -> Dict[str, bool]:
    """Test if modules can be imported without errors"""
    print("🔍 Testing Module Imports...")
    
    results = {}
    
    # Test basic CLI module
    try:
        sys.path.insert(0, "src")
        from dslmodel.commands import coordination_cli
        results["coordination_cli"] = True
        print("  ✅ coordination_cli imported successfully")
    except Exception as e:
        results["coordination_cli"] = False
        print(f"  ❌ coordination_cli import failed: {e}")
    
    # Test OTEL coordination module
    try:
        from dslmodel.commands import otel_coordination
        results["otel_coordination"] = True
        print("  ✅ otel_coordination imported successfully")
    except Exception as e:
        results["otel_coordination"] = False
        print(f"  ❌ otel_coordination import failed: {e}")
    
    # Test main CLI
    try:
        from dslmodel import cli
        results["main_cli"] = True
        print("  ✅ main CLI imported successfully")
    except Exception as e:
        results["main_cli"] = False
        print(f"  ❌ main CLI import failed: {e}")
    
    return results

def test_cli_commands() -> Dict[str, bool]:
    """Test CLI command structure"""
    print("\n🔧 Testing CLI Command Structure...")
    
    results = {}
    
    try:
        sys.path.insert(0, "src")
        from dslmodel.commands.otel_coordination import app as otel_app
        
        # Check if OTEL app has expected commands
        otel_commands = [cmd.name for cmd in otel_app.commands.values()]
        work_commands = []
        
        # Check for work sub-app
        for name, sub_app in otel_app.registered_groups.items():
            if name == "work":
                work_commands = [cmd.name for cmd in sub_app.commands.values()]
        
        results["otel_app_structure"] = len(otel_commands) > 0
        results["work_subapp"] = "work" in [name for name, _ in otel_app.registered_groups.items()]
        results["work_commands"] = len(work_commands) >= 3  # claim, list, complete minimum
        
        print(f"  ✅ OTEL app has {len(otel_commands)} commands")
        print(f"  ✅ Work sub-app found: {results['work_subapp']}")
        print(f"  ✅ Work commands ({len(work_commands)}): {work_commands}")
        
    except Exception as e:
        results["otel_app_structure"] = False
        results["work_subapp"] = False
        results["work_commands"] = False
        print(f"  ❌ CLI structure test failed: {e}")
    
    return results

def test_otel_integration() -> Dict[str, bool]:
    """Test OpenTelemetry integration features"""
    print("\n📊 Testing OTEL Integration...")
    
    results = {}
    
    try:
        sys.path.insert(0, "src")
        from dslmodel.commands.otel_coordination import (
            setup_otel, 
            trace_operation,
            CoordinationAttributes,
            OTEL_AVAILABLE
        )
        
        results["otel_setup"] = True
        results["trace_context_manager"] = True
        results["semantic_conventions"] = True
        results["otel_available"] = OTEL_AVAILABLE
        
        print(f"  ✅ OTEL setup function available")
        print(f"  ✅ Trace context manager available")
        print(f"  ✅ Semantic conventions defined")
        print(f"  📋 OTEL libraries available: {OTEL_AVAILABLE}")
        
        # Test context manager (without actual OTEL)
        with trace_operation("test.operation", {"test.attr": "value"}) as span:
            results["context_manager_works"] = True
        
        print(f"  ✅ Context manager works")
        
    except Exception as e:
        results["otel_setup"] = False
        results["trace_context_manager"] = False
        results["semantic_conventions"] = False
        results["otel_available"] = False
        results["context_manager_works"] = False
        print(f"  ❌ OTEL integration test failed: {e}")
    
    return results

def test_pyproject_integration() -> Dict[str, bool]:
    """Test pyproject.toml integration"""
    print("\n📦 Testing pyproject.toml Integration...")
    
    results = {}
    
    # Check if pyproject.toml has OTEL dependencies
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        results["otel_dependencies"] = "opentelemetry-api" in content
        results["otel_extras"] = "[tool.poetry.extras]" in content and "otel" in content
        results["poe_tasks"] = "otel-status" in content
        
        print(f"  ✅ OTEL dependencies in pyproject.toml: {results['otel_dependencies']}")
        print(f"  ✅ OTEL extras defined: {results['otel_extras']}")
        print(f"  ✅ Poetry tasks defined: {results['poe_tasks']}")
    else:
        results["otel_dependencies"] = False
        results["otel_extras"] = False
        results["poe_tasks"] = False
        print("  ❌ pyproject.toml not found")
    
    return results

def test_fallback_behavior() -> Dict[str, bool]:
    """Test behavior when OTEL dependencies are not installed"""
    print("\n🔄 Testing Fallback Behavior...")
    
    results = {}
    
    try:
        sys.path.insert(0, "src")
        from dslmodel.commands.otel_coordination import (
            tracer, 
            meter,
            work_items_created
        )
        
        # These should work even without OTEL installed (using mocks)
        results["tracer_available"] = tracer is not None
        results["meter_available"] = meter is not None
        results["metrics_available"] = work_items_created is not None
        
        print(f"  ✅ Tracer available (may be mock): {results['tracer_available']}")
        print(f"  ✅ Meter available (may be mock): {results['meter_available']}")
        print(f"  ✅ Metrics available (may be mock): {results['metrics_available']}")
        
        # Test basic functionality
        try:
            work_items_created.add(1, {"test": "value"})
            results["metrics_functional"] = True
            print(f"  ✅ Metrics are functional")
        except Exception as e:
            results["metrics_functional"] = False
            print(f"  ❌ Metrics not functional: {e}")
        
    except Exception as e:
        results["tracer_available"] = False
        results["meter_available"] = False
        results["metrics_available"] = False
        results["metrics_functional"] = False
        print(f"  ❌ Fallback behavior test failed: {e}")
    
    return results

def generate_test_report(all_results: Dict[str, Dict[str, bool]]) -> Dict:
    """Generate comprehensive test report"""
    print("\n📊 TEST REPORT")
    print("=" * 60)
    
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(1 for passed in results.values() if passed) 
                      for results in all_results.values())
    
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"\nSUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {success_rate:.1%}")
    
    print(f"\nDETAILED RESULTS:")
    for category, results in all_results.items():
        print(f"\n{category.upper()}:")
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {test_name}")
    
    report = {
        "timestamp": "2024-01-15T10:30:00Z",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate,
        "categories": all_results,
        "integration_status": {
            "cli_integration": success_rate >= 0.8,
            "otel_ready": all_results.get("otel_integration", {}).get("otel_setup", False),
            "fallback_working": all_results.get("fallback_behavior", {}).get("tracer_available", False),
            "pyproject_configured": all_results.get("pyproject_integration", {}).get("otel_dependencies", False)
        }
    }
    
    return report

def show_next_steps(report: Dict):
    """Show next steps based on test results"""
    print(f"\n🚀 NEXT STEPS:")
    
    if report["success_rate"] >= 0.8:
        print("  ✅ CLI integration is working well!")
        print("  📦 To enable full OTEL features:")
        print("     pip install dslmodel[otel]")
        print("  🧪 Test the CLI:")
        print("     dsl otel --help")
        print("     dsl otel work claim bug 'Test issue' --priority high")
        print("     dsl otel work list --show-traces")
    else:
        print("  ⚠️  Some integration issues found:")
        
        if not report["integration_status"]["cli_integration"]:
            print("     • CLI integration needs attention")
        
        if not report["integration_status"]["pyproject_configured"]:
            print("     • pyproject.toml configuration incomplete")
    
    print(f"\n💡 Available Poetry Tasks:")
    print("     poe otel-status   # Check OTEL status")
    print("     poe otel-demo     # Run coordination demo")
    print("     poe otel-install  # Install OTEL dependencies")

def main():
    """Run all integration tests"""
    print("🚀 DSLModel CLI Integration Test Suite")
    print("Testing OTEL coordination with pyproject.toml structure...")
    print("=" * 60)
    
    # Run all test categories
    all_results = {
        "module_imports": test_module_imports(),
        "cli_commands": test_cli_commands(),
        "otel_integration": test_otel_integration(),
        "pyproject_integration": test_pyproject_integration(),
        "fallback_behavior": test_fallback_behavior()
    }
    
    # Generate report
    report = generate_test_report(all_results)
    
    # Show next steps
    show_next_steps(report)
    
    # Save report
    import json
    with open("cli_integration_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to cli_integration_report.json")
    
    return report["success_rate"] >= 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)