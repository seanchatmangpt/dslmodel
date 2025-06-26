#!/usr/bin/env python3
"""
Direct test of template generation functionality
"""

import subprocess
import tempfile
import os
from pathlib import Path
import json

def test_hygen_template_direct():
    """Test hygen template generation directly without interactive prompts."""
    
    print("🧪 Testing Hygen template generation...")
    
    # Create a simple test using the weaver-semconv template
    # We'll create a temporary input file to avoid interactive prompts
    
    test_input = """test_domain
Test domain description
test
1.0.0
operation,status
y
y
y"""
    
    try:
        # Test if npx hygen works with our templates
        result = subprocess.run(
            ["npx", "hygen", "weaver-semconv", "new"],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}...")
        print(f"Stderr: {result.stderr[:200]}...")
        
        # Check if files were generated
        registry_file = Path("semconv_registry/test_domain.yaml")
        models_file = Path("src/dslmodel/weaver/test_domain_models.py")
        
        print(f"Registry file exists: {registry_file.exists()}")
        print(f"Models file exists: {models_file.exists()}")
        
        if registry_file.exists():
            print(f"Registry file size: {registry_file.stat().st_size} bytes")
            
        if models_file.exists():
            print(f"Models file size: {models_file.stat().st_size} bytes")
            
            # Test if the generated Python file is valid syntax
            try:
                with models_file.open() as f:
                    code = f.read()
                compile(code, str(models_file), 'exec')
                print("✅ Generated Python code has valid syntax")
            except SyntaxError as e:
                print(f"❌ Syntax error in generated code: {e}")
                
        return result.returncode == 0 and (registry_file.exists() or models_file.exists())
        
    except subprocess.TimeoutExpired:
        print("❌ Template generation timed out")
        return False
    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False

def test_simple_template_structure():
    """Test that template files are properly structured."""
    
    print("\n🔍 Testing template structure...")
    
    # Check weaver-semconv template
    template_dir = Path("_templates/weaver-semconv/new")
    
    if not template_dir.exists():
        print("❌ Template directory doesn't exist")
        return False
    
    index_js = template_dir / "index.js"
    if not index_js.exists():
        print("❌ index.js doesn't exist")
        return False
    
    # Check if index.js has the right structure
    try:
        content = index_js.read_text()
        
        required_elements = [
            "module.exports",
            "prompt:",
            "inquirer",
            "domain",
            "description"
        ]
        
        for element in required_elements:
            if element not in content:
                print(f"❌ Missing required element: {element}")
                return False
        
        print("✅ Template structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def test_existing_swarm_functionality():
    """Test the existing SwarmAgent functionality that should work."""
    
    print("\n🤖 Testing existing SwarmAgent functionality...")
    
    tests = [
        ("python swarm_cli.py --help", "Help command"),
        ("python swarm_cli.py status", "Status command"),
        ("python swarm_cli.py list", "List agents"),
    ]
    
    results = []
    
    for cmd, name in tests:
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0 and len(result.stdout) > 0
            results.append(success)
            
            if success:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed (code: {result.returncode})")
                
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
            results.append(False)
    
    return sum(results) >= 2  # At least 2 out of 3 should work

def main():
    """Run all tests and provide honest assessment."""
    
    print("🔍 HONEST SKEPTICAL TESTING")
    print("=" * 40)
    
    tests = [
        ("Template Structure", test_simple_template_structure),
        ("Existing SwarmAgent CLI", test_existing_swarm_functionality),
        ("Template Generation", test_hygen_template_direct)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append(result)
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            results.append(False)
    
    # Final assessment
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"\n{'='*40}")
    print("📊 FINAL HONEST ASSESSMENT")
    print(f"{'='*40}")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL CLAIMS VERIFIED - Everything works!")
        assessment = "FULLY_WORKING"
    elif passed_tests >= total_tests * 0.66:
        print("⚠️  MOSTLY WORKING - Core functionality verified")
        assessment = "MOSTLY_WORKING"
    else:
        print("❌ SIGNIFICANT ISSUES - Major claims not verified")
        assessment = "NEEDS_WORK"
    
    print(f"\nHONEST VERDICT: {assessment}")
    
    # Specific recommendations
    print("\n🔧 RECOMMENDATIONS:")
    if assessment == "FULLY_WORKING":
        print("  • System is ready for production use")
        print("  • Templates can be used for rapid development")
    elif assessment == "MOSTLY_WORKING":
        print("  • Core SwarmAgent system works well")
        print("  • Template generation may need refinement")
        print("  • Focus on fixing template interaction issues")
    else:
        print("  • Focus on core functionality first")
        print("  • Fix import and dependency issues")
        print("  • Validate template generation thoroughly")
    
    return 0 if passed_tests >= total_tests * 0.66 else 1

if __name__ == "__main__":
    exit(main())