#!/usr/bin/env python3
"""
Generate OpenTelemetry semantic convention models using Weaver.

This script uses the existing Weaver integration to generate Pydantic models
from the swarm.yaml semantic conventions.
"""

import sys
from pathlib import Path
import subprocess

# Add the dslmodel source to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from dslmodel.otel.weaver_integration import WeaverIntegration
except ImportError as e:
    print(f"❌ Could not import WeaverIntegration: {e}")
    print("This likely means Weaver is not installed or configured properly.")
    sys.exit(1)


def generate_swarm_models():
    """Generate Pydantic models from swarm semantic conventions."""
    print("🔧 Generating SwarmAgent OpenTelemetry Models with Weaver")
    print("=" * 60)
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent.parent.parent
    registry_path = project_root / "semconv_registry"
    templates_path = project_root / "weaver_templates" / "registry" / "python"
    output_path = project_root / "src" / "dslmodel" / "otel" / "models"
    
    print(f"\n📁 Project root: {project_root}")
    print(f"📋 Registry: {registry_path}")
    print(f"🎨 Templates: {templates_path}")
    print(f"💾 Output: {output_path}")
    
    # Check if swarm.yaml exists
    swarm_yaml = registry_path / "swarm.yaml"
    if not swarm_yaml.exists():
        print(f"\n❌ Swarm semantic conventions not found at: {swarm_yaml}")
        return False
    
    print(f"\n✅ Found swarm conventions: {swarm_yaml}")
    
    # Initialize Weaver integration
    try:
        weaver = WeaverIntegration(
            registry_path=str(registry_path),
            templates_path=str(templates_path) if templates_path.exists() else None,
            output_path=str(output_path),
            target_language="python"
        )
        
        print("\n🔍 Weaver integration initialized")
        
        # Validate Weaver installation
        if not weaver.validate_weaver():
            print("❌ Weaver validation failed")
            return False
        
        print("✅ Weaver installation validated")
        
    except Exception as e:
        print(f"❌ Failed to initialize Weaver: {e}")
        return False
    
    # Generate models
    try:
        print("\n🚀 Generating models...")
        
        # Use the weaver integration to generate models
        result = weaver.generate_models()
        
        if result:
            print("✅ Models generated successfully!")
            
            # List generated files
            if output_path.exists():
                generated_files = list(output_path.glob("*.py"))
                if generated_files:
                    print(f"\n📦 Generated files:")
                    for file in generated_files:
                        print(f"  - {file.name}")
                else:
                    print("\n⚠️  No Python files found in output directory")
            
            return True
        else:
            print("❌ Model generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False


def show_usage_example():
    """Show how to use the generated models."""
    print("\n📚 Usage Example:")
    print("-" * 30)
    
    example_code = '''
# After generation, use the models like this:

from dslmodel.otel.models.swarm_attributes import SwarmSpanAttributes

# Create span attributes with validation
span_attrs = SwarmSpanAttributes(
    swarm_agent="roberts",
    swarm_trigger="vote",
    swarm_state_from="MOTION_OPEN",
    swarm_state_to="VOTING"
)

# Use with OpenTelemetry spans
with tracer.start_as_current_span("swarmsh.roberts.vote") as span:
    span.set_attributes(span_attrs.model_dump())
'''
    
    print(example_code)


def main():
    """Main execution."""
    success = generate_swarm_models()
    
    if success:
        show_usage_example()
        print("\n🎉 Swarm OpenTelemetry models ready for use!")
    else:
        print("\n💡 Manual Generation Alternative:")
        print("-" * 40)
        print("If Weaver is not available, you can manually run:")
        print(f"  weaver registry generate --registry=semconv_registry --output=src/dslmodel/otel/models")
        print(f"  # Or use the coordination CLI to generate models")
    
    return success


if __name__ == "__main__":
    main()