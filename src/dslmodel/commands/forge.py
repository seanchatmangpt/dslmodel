"""Forge command for building from Python-based semantic conventions."""

import typer
from pathlib import Path
from typing import Optional, List
from loguru import logger

from ..integrations.otel.extended_weaver_integration import ExtendedWeaverForgeIntegration
from ..weaver.loader import PythonConventionLoader

app = typer.Typer(help="Weaver Forge workflow commands")


@app.command()
def build(
    authoring_modules: Optional[List[str]] = typer.Option(
        None,
        "--module",
        "-m",
        help="Python module containing convention definitions (can be specified multiple times)"
    ),
    target: str = typer.Option(
        "python",
        "--target",
        "-t", 
        help="Target to generate (python, docs, etc.)"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for generated files"
    )
):
    """Build semantic conventions from Python modules and/or YAML files."""
    
    # Default authoring modules if none specified
    if authoring_modules is None:
        # Check for weaver modules in src/dslmodel/weaver/
        from pathlib import Path
        import os
        
        # Try to find weaver modules relative to this package
        try:
            from dslmodel.weaver import WEAVER_ROOT
            weaver_dir = WEAVER_ROOT
        except ImportError:
            # Fallback to relative path
            weaver_dir = Path(__file__).parent.parent / "weaver"
        
        if weaver_dir.exists():
            authoring_modules = []
            # Look for convention spec files
            for spec_file in weaver_dir.glob("*_spec.py"):
                if spec_file.stem not in ["__init__", "models", "enums", "loader"]:
                    authoring_modules.append(f"dslmodel.weaver.{spec_file.stem}")
            
            if authoring_modules:
                logger.info(f"Found weaver modules: {authoring_modules}")
        else:
            authoring_modules = []
    
    integration = ExtendedWeaverForgeIntegration(
        authoring_modules=authoring_modules
    )
    
    if authoring_modules:
        logger.info(f"Building from Python modules: {authoring_modules}")
        success = integration.build_from_python_modules(
            target=target,
            output_dir=output_dir
        )
    else:
        logger.info("Building from YAML conventions only")
        success = integration.forge_workflow_build()
        
    if success:
        logger.success("✨ Build completed successfully!")
        logger.info("Generated files:")
        
        # Show generated files
        output_path = Path(output_dir or "output")
        if output_path.exists():
            for file in output_path.glob("**/*"):
                if file.is_file():
                    logger.info(f"  📄 {file}")
    else:
        logger.error("❌ Build failed")
        raise typer.Exit(1)


@app.command()
def validate(
    authoring_modules: Optional[List[str]] = typer.Option(
        None,
        "--module",
        "-m",
        help="Python module to validate"
    )
):
    """Validate Python-based convention definitions."""
    
    if not authoring_modules:
        # Check for weaver modules in src/dslmodel/weaver/
        try:
            from dslmodel.weaver import WEAVER_ROOT
            weaver_dir = WEAVER_ROOT
        except ImportError:
            weaver_dir = Path(__file__).parent.parent / "weaver"
        
        if weaver_dir.exists():
            authoring_modules = []
            for spec_file in weaver_dir.glob("*_spec.py"):
                if spec_file.stem not in ["__init__", "models", "enums", "loader"]:
                    authoring_modules.append(f"dslmodel.weaver.{spec_file.stem}")
            
    if not authoring_modules:
        logger.error("No authoring modules found")
        raise typer.Exit(1)
        
    loader = PythonConventionLoader(authoring_modules)
    
    all_valid = True
    for module in authoring_modules:
        try:
            convention_sets = loader.load_module(module)
            logger.success(f"✅ {module}: Valid ({len(convention_sets)} convention sets)")
            
            # Show details
            for cs in convention_sets:
                logger.info(f"    - {cs.title} v{cs.version}: {len(cs.spans)} spans")
                
        except Exception as e:
            logger.error(f"❌ {module}: Invalid - {e}")
            all_valid = False
            
    if not all_valid:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()