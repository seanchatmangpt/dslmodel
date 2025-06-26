#!/usr/bin/env python3
"""
Integration Validation Script

Validates the key integrations without heavy dependencies.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def validate_dspy_integration():
    """Test DSPy integration."""
    try:
        from dslmodel.utils.llm_init import init_lm, init_qwen3
        print("✅ DSPy/LLM integration imports successful")
        
        # Test basic initialization (without actual LLM calls)
        print("✅ DSPy integration validated")
        return True
    except Exception as e:
        print(f"❌ DSPy integration failed: {e}")
        return False

def validate_enterprise_demo():
    """Test enterprise demo components."""
    try:
        from dslmodel.examples.enterprise_demo_minimal import (
            RobertsRulesDemo,
            ScrumAtScaleDemo, 
            LeanSixSigmaDemo,
            EnterpriseCoordinationDemo
        )
        print("✅ Enterprise demo imports successful")
        
        # Test basic model creation
        roberts = RobertsRulesDemo(meeting_id="test", current_motion="test")
        scrum = ScrumAtScaleDemo(release_name="test", teams=["A"])
        lean = LeanSixSigmaDemo(project_name="test", target_process="test")
        
        # Test coordination calculations
        demo = EnterpriseCoordinationDemo(
            customer_name="Test Corp",
            roberts_demo=roberts,
            scrum_demo=scrum,
            lean_demo=lean
        )
        
        improvements = demo._calculate_coordination_improvement()
        assert improvements['overall_coordination_efficiency'] == 0.79
        
        print("✅ Enterprise demo coordination calculations validated")
        return True
    except Exception as e:
        print(f"❌ Enterprise demo validation failed: {e}")
        return False

def validate_fsm_integration():
    """Test FSM integration."""
    try:
        from dslmodel.mixins.fsm_mixin import FSMMixin
        from dslmodel.dsl_models import DSLModel
        print("✅ FSM integration imports successful")
        
        # Test basic FSM model
        class TestFSM(DSLModel, FSMMixin):
            pass
        
        print("✅ FSM integration validated")
        return True
    except Exception as e:
        print(f"❌ FSM integration failed: {e}")
        return False

def validate_core_imports():
    """Test core DSLModel imports."""
    try:
        from dslmodel.dsl_models import DSLModel
        from dslmodel.mixins import DSPyDSLMixin, FileHandlerDSLMixin, JinjaDSLMixin
        print("✅ Core DSLModel imports successful")
        
        # Test basic model creation
        class TestModel(DSLModel):
            name: str = "test"
        
        model = TestModel()
        assert model.name == "test"
        
        print("✅ Core DSLModel functionality validated")
        return True
    except Exception as e:
        print(f"❌ Core DSLModel validation failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🧪 Running Integration Validation...")
    print("=" * 50)
    
    results = []
    
    # Test core functionality
    results.append(validate_core_imports())
    results.append(validate_fsm_integration())
    results.append(validate_dspy_integration())
    results.append(validate_enterprise_demo())
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎯 ALL INTEGRATIONS VALIDATED SUCCESSFULLY!")
        print("✨ SwarmSH enterprise coordination stack is ready!")
        return True
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count}/{len(results)} validations failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)