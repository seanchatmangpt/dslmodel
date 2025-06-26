"""
Weaver Forge Integration for DSLModel

This module provides integration between OpenTelemetry Weaver Forge and DSLModel,
enabling generation of Pydantic models from semantic conventions.
"""
import subprocess
import yaml
from pathlib import Path
from typing import Optional, List, Dict
from loguru import logger


class WeaverForgeIntegration:
    """Integrates Weaver Forge with DSLModel for code generation."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Weaver integration."""
        self.project_root = project_root or Path.cwd()
        self.weaver_config = self.project_root / "weaver.yaml"
        self.templates_dir = self.project_root / "weaver_templates"
        
    def validate_setup(self) -> bool:
        """Validate that weaver is installed and configured properly."""
        try:
            # Check weaver installation
            result = subprocess.run(
                ["weaver", "--version"], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                logger.error("Weaver is not installed or not in PATH")
                return False
                
            logger.info(f"Found weaver: {result.stdout.strip()}")
            
            # Check config file
            if not self.weaver_config.exists():
                logger.error(f"Weaver config not found at {self.weaver_config}")
                return False
                
            # Check templates directory  
            if not self.templates_dir.exists():
                logger.error(f"Templates directory not found at {self.templates_dir}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate weaver setup: {e}")
            return False
    
    def generate_models(
        self, 
        semconv_path: str,
        target: str = "python",
        output_dir: Optional[str] = None
    ) -> bool:
        """
        Generate models from semantic conventions using Weaver.
        
        Args:
            semconv_path: Path to semantic convention YAML file or directory
            target: Target to generate (default: python)
            output_dir: Output directory (default: ./output)
            
        Returns:
            True if generation succeeded
        """
        if not self.validate_setup():
            return False
            
        if output_dir is None:
            output_dir = str(self.project_root / "output")
            
        try:
            cmd = [
                "weaver", 
                "registry",
                "generate",
                "--registry", semconv_path,
                "--templates", str(self.templates_dir),
                "--config", str(self.weaver_config),
                target,
                output_dir
            ]
                    
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode != 0:
                logger.error(f"Weaver forge failed: {result.stderr}")
                return False
                
            logger.success("Successfully generated models from semantic conventions")
            if result.stdout:
                logger.info(result.stdout)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate models: {e}")
            return False
    
    def create_semconv_example(self) -> Path:
        """Create an example semantic convention YAML for testing."""
        # Create registry directory structure
        registry_dir = self.project_root / "semconv_registry"
        registry_dir.mkdir(exist_ok=True)
        
        example_path = registry_dir / "dslmodel.yaml"
        
        example_content = """groups:
  - id: dslmodel
    prefix: dslmodel
    type: attribute_group
    brief: 'DSLModel workflow execution attributes'
    attributes:
      - id: workflow.name
        type: string
        requirement_level: required
        brief: 'Name of the DSL workflow being executed'
        examples: ['user-registration', 'payment-processing']
        
      - id: workflow.status  
        type: 
          allow_custom_values: false
          members:
            - id: started
              value: 'started'
            - id: completed
              value: 'completed'
            - id: failed
              value: 'failed'
        requirement_level: required
        brief: 'Current status of the workflow execution'
        
      - id: workflow.duration_ms
        type: int
        requirement_level: recommended
        brief: 'Duration of workflow execution in milliseconds'
        examples: [150, 2500]
        
      - id: model.type
        type: string
        requirement_level: recommended
        brief: 'Type of DSL model being used'
        examples: ['pydantic', 'dataclass', 'custom']

  - id: dslmodel.metrics
    type: metric
    metric_name: dslmodel.workflow.duration
    brief: 'Measures the duration of DSL workflow executions'
    instrument: histogram
    unit: 'ms'
    attributes:
      - ref: dslmodel.workflow.name
      - ref: dslmodel.workflow.status
"""
        
        example_path.write_text(example_content)
        logger.info(f"Created example semantic convention at {example_path}")
        return example_path


def main():
    """Example usage of Weaver integration."""
    integration = WeaverForgeIntegration()
    
    # Create example semconv
    example_path = integration.create_semconv_example()
    
    # Generate Python models
    success = integration.generate_models(
        str(example_path.parent),  # Use registry directory
        target="python"
    )
    
    if success:
        logger.success("Integration complete! Check src/dslmodel/otel/ for generated models")
    else:
        logger.error("Integration failed")


if __name__ == "__main__":
    main()