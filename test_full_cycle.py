#!/usr/bin/env python3
"""
Test script for full cycle demo functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all components can be imported successfully"""
    print("🧪 Testing imports...")
    
    try:
        from dslmodel.commands.swarm import SwarmCoordinator
        print("  ✓ SwarmCoordinator imported successfully")
    except Exception as e:
        print(f"  ❌ SwarmCoordinator import failed: {e}")
        return False
    
    try:
        from dslmodel.commands.full_cycle_demo import FullCycleDemo
        print("  ✓ FullCycleDemo imported successfully")
    except Exception as e:
        print(f"  ❌ FullCycleDemo import failed: {e}")
        return False
    
    return True

def test_swarm_coordinator():
    """Test basic SwarmCoordinator functionality"""
    print("\n🤖 Testing SwarmCoordinator...")
    
    try:
        from dslmodel.commands.swarm import SwarmCoordinator
        
        coordinator = SwarmCoordinator(data_dir="./test_swarm_data")
        print("  ✓ SwarmCoordinator created")
        
        # Test creating an agent
        agent_id = coordinator.create_agent("TestAgent", "test_team")
        print(f"  ✓ Agent created: {agent_id}")
        
        # Test creating work
        work_id = coordinator.assign_work("Test work item", "medium")
        print(f"  ✓ Work created: {work_id}")
        
        # Test processing work
        result = coordinator.process_work()
        print(f"  ✓ Work processed: {result}")
        
        # Test status
        status = coordinator.get_status()
        print(f"  ✓ Status retrieved: {status}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SwarmCoordinator test failed: {e}")
        return False

def test_full_cycle_components():
    """Test individual components of the full cycle demo"""
    print("\n🔄 Testing FullCycleDemo components...")
    
    try:
        from dslmodel.commands.full_cycle_demo import FullCycleDemo
        
        demo = FullCycleDemo()
        print("  ✓ FullCycleDemo created")
        
        # Test domain model generation
        models = demo.generate_domain_models()
        print(f"  ✓ Generated {len(models)} domain models")
        
        # Test agent generation
        agents = demo.generate_agents(models)
        print(f"  ✓ Generated {len(agents)} agents")
        
        # Test work generation
        work_items = demo.generate_work_items(models)
        print(f"  ✓ Generated {len(work_items)} work items")
        
        # Test monitoring initialization
        demo.initialize_monitoring()
        print("  ✓ Monitoring initialized")
        
        print(f"  ✓ Cycle metrics: {demo.cycle_metrics}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FullCycleDemo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    import shutil
    from pathlib import Path
    
    test_dirs = ["./test_swarm_data", "./full_cycle_data"]
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print(f"  ✓ Cleaned {test_dir}")

def main():
    """Run all tests"""
    print("🚀 Testing Full Cycle Demo Implementation")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed - stopping")
        return False
    
    # Test SwarmCoordinator
    if not test_swarm_coordinator():
        print("\n❌ SwarmCoordinator tests failed")
        return False
    
    # Test FullCycleDemo components
    if not test_full_cycle_components():
        print("\n❌ FullCycleDemo tests failed")
        return False
    
    # Clean up
    cleanup_test_data()
    
    print("\n✅ All tests passed! Full cycle demo is ready to use.")
    print("\n📋 Available poe tasks:")
    print("  poe demo-full          - Run complete demo (3 cycles)")
    print("  poe demo-full-fast     - Run quick demo (1 cycle)")  
    print("  poe demo-full-extended - Run extended demo (5 cycles)")
    print("  poe demo-status        - Show demo status")
    print("  poe demo-clean         - Clean demo data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)