"""Extended Weaver Forge Integration with Python module support."""

from pathlib import Path
from typing import Optional, List
from loguru import logger

from .weaver_integration import WeaverForgeIntegration
from ...weaver.loader import PythonConventionLoader


class ExtendedWeaverForgeIntegration(WeaverForgeIntegration):
    """Extended Weaver integration with Python-based convention support."""
    
    def __init__(self, project_root: Optional[Path] = None, authoring_modules: Optional[List[str]] = None):
        """Initialize with optional authoring modules."""
        super().__init__(project_root)
        self.authoring_modules = authoring_modules or []
        self.python_loader = PythonConventionLoader(self.authoring_modules)
        
    def build_from_python_modules(self, target: str = "python", output_dir: Optional[str] = None) -> bool:
        """
        Build models from Python-based semantic conventions.
        
        Args:
            target: Target to generate (default: python)
            output_dir: Output directory (default: ./output)
            
        Returns:
            True if generation succeeded
        """
        # First, generate YAML files from Python modules
        semconv_dir = self.project_root / "semconv_registry" / "generated"
        
        logger.info("Generating YAML conventions from Python modules...")
        self.python_loader.generate_yaml_from_modules(semconv_dir)
        
        # Then use regular weaver generation
        return self.generate_models(
            str(semconv_dir),
            target=target,
            output_dir=output_dir
        )
        
    def forge_workflow_build(self) -> bool:
        """
        Emulate 'python -m weaver_forge.forge_workflow build' command.
        """
        logger.info("Running forge workflow build...")
        
        # Generate YAML from Python modules
        if self.authoring_modules:
            success = self.build_from_python_modules()
            if not success:
                logger.error("Failed to build from Python modules")
                return False
                
        # Run standard weaver generation for any existing YAML files
        registry_dir = self.project_root / "semconv_registry"
        if registry_dir.exists():
            success = self.generate_models(
                str(registry_dir),
                target="python"
            )
            if not success:
                logger.error("Failed to generate from YAML conventions")
                return False
                
        logger.success("Forge workflow build completed successfully")
        return True


def main():
    """Example usage with Python modules."""
    # Configure authoring modules
    AUTHORING_MODULES = [
        "dslmodel.weaver.telemetry_inversion_spec",
        "dslmodel.weaver.autonomous_decision_spec",
    ]
    
    integration = ExtendedWeaverForgeIntegration(
        authoring_modules=AUTHORING_MODULES
    )
    
    # Run the forge workflow
    success = integration.forge_workflow_build()
    
    if success:
        logger.success("Build complete! Check output directory for generated files")
    else:
        logger.error("Build failed")
        

if __name__ == "__main__":
    main()