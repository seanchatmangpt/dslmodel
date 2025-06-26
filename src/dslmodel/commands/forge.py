"""Forge command for building from Python-based semantic conventions."""

import typer
from pathlib import Path
from typing import Optional, List
from loguru import logger

from ..integrations.otel.extended_weaver_integration import ExtendedWeaverForgeIntegration
from ..weaver.loader import PythonConventionLoader
from ..utils.json_output import json_command, get_formatter, format_file_list, format_generation_result

app = typer.Typer(help="Weaver Forge workflow commands")

# Import forge360 subcommands
try:
    from .forge_360 import app as forge360_app
    app.add_typer(forge360_app, name="permutations", help="Generate 360 DSLModel permutations")
except ImportError:
    pass  # forge360 command not available


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


@app.command("e2e")
def e2e_generate(
    spec_module: str = typer.Argument(
        ...,
        help="Python module containing telemetry specification"
    ),
    feature_name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name for the generated feature"
    ),
    output_dir: Path = typer.Option(
        Path("generated_features"),
        "--output",
        "-o",
        help="Output directory for generated files"
    ),
    model: str = typer.Option(
        "ollama/qwen3",
        "--model",
        "-m",
        help="LLM model to use for generation"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be generated without creating files"
    )
):
    """Generate a complete feature from telemetry specification."""
    
    with json_command("forge-e2e") as formatter:
        formatter.add_data("spec_module", spec_module)
        formatter.add_data("feature_name", feature_name)
        formatter.add_data("output_dir", str(output_dir))
        formatter.add_data("model", model)
        formatter.add_data("dry_run", dry_run)
        
        formatter.print(f"🚀 Starting E2E feature generation from {spec_module}")
        
        try:
            from ..forge.e2e_feature_generator import E2EFeatureGenerator
            
            generator = E2EFeatureGenerator(model=model)
            
            if dry_run:
                # Just show what would be generated
                loader = PythonConventionLoader([spec_module])
                convention_sets = []
                for module in [spec_module]:
                    convention_sets.extend(loader.load_module(module))
                
                if convention_sets:
                    cs = convention_sets[0]
                    formatter.add_data("preview", {
                        "title": cs.title,
                        "version": cs.version,
                        "spans_count": len(cs.spans),
                        "sample_spans": [
                            {"name": span.name, "brief": span.brief}
                            for span in cs.spans[:3]
                        ]
                    })
                    formatter.print(f"Would generate feature from: {cs.title} v{cs.version}")
                    formatter.print(f"Spans to implement: {len(cs.spans)}")
                    for span in cs.spans[:3]:  # Show first 3
                        formatter.print(f"  - {span.name}: {span.brief}")
                    if len(cs.spans) > 3:
                        formatter.print(f"  ... and {len(cs.spans) - 3} more")
                return
            
            # Generate the feature
            result = generator.generate_feature_from_spec(
                spec_module=spec_module,
                feature_name=feature_name,
                output_dir=output_dir
            )
            
            # Add results to JSON output
            formatter.add_data("generation_result", result)
            
            # Display results
            formatter.print(f"✅ Feature '{result['feature_name']}' generated successfully!")
            formatter.print(f"📁 Output directory: {result['output_dir']}")
            formatter.print(f"📊 Telemetry spans: {result['spans_count']}")
            formatter.print(f"⏱️  Duration: {result['duration_ms']}ms")
            formatter.print(f"🔍 Trace ID: {result['trace_id']}")
            
            formatter.print("\nGenerated components:")
            for component in result['components_generated']:
                formatter.print(f"  ✓ {component}")
            
            if result['validation']['success']:
                formatter.print("✅ All validations passed")
            else:
                formatter.print("⚠️  Validation issues found:", level="warning")
                for error in result['validation'].get('errors', []):
                    formatter.print(f"  - {error}", level="error")
            
            # Show next steps
            formatter.add_data("next_steps", [
                f"Review generated files in {output_dir}",
                f"Run tests: pytest {output_dir}/test_{result['feature_name']}.py",
                f"Try the CLI: python {output_dir}/{result['feature_name']}_cli.py --help"
            ])
            
        except Exception as e:
            formatter.add_error(f"E2E generation failed: {e}")
            formatter.print(f"❌ E2E generation failed: {e}", level="error")
            raise typer.Exit(1)


@app.command("e2e-demo")
def e2e_demo(
    model: str = typer.Option(
        "ollama/qwen3",
        "--model",
        "-m",
        help="LLM model to use"
    )
):
    """Run a demonstration of E2E feature generation."""
    
    with json_command("forge-e2e-demo") as formatter:
        formatter.add_data("model", model)
        formatter.print("🎯 Running E2E Feature Generation Demo")
        
        try:
            # First generate the E2E automation spec YAML
            formatter.print("\n1️⃣ Generating E2E automation telemetry spec...")
            from ..weaver.loader import PythonConventionLoader
            
            loader = PythonConventionLoader(["dslmodel.weaver.e2e_automation_spec"])
            output_dir = Path("semconv_registry/generated")
            output_dir.mkdir(parents=True, exist_ok=True)
            loader.generate_yaml_from_modules(output_dir)
            
            # Now generate a feature from our autonomous decision spec
            formatter.print("\n2️⃣ Generating feature from autonomous decision spec...")
            from ..forge.e2e_feature_generator import E2EFeatureGenerator
            
            generator = E2EFeatureGenerator(model=model)
            result = generator.generate_feature_from_spec(
                spec_module="dslmodel.weaver.autonomous_decision_spec",
                feature_name="auto_decision",
                output_dir=Path("demo_generated_feature")
            )
            
            formatter.add_data("feature_name", result['feature_name'])
            formatter.add_data("output_dir", result['output_dir'])
            formatter.add_data("spans_count", result['spans_count'])
            formatter.add_data("duration_ms", result['duration_ms'])
            formatter.add_data("validation", result['validation'])
            formatter.add_data("trace_id", result['trace_id'])
            
            formatter.print(f"\n✅ Demo completed!")
            formatter.print(f"Generated feature: {result['feature_name']}")
            formatter.print(f"Files created in: demo_generated_feature/")
            
            # Show sample of generated code
            impl_file = Path("demo_generated_feature/auto_decision.py")
            if impl_file.exists():
                formatter.print("\n📄 Sample of generated implementation:")
                lines = impl_file.read_text().split("\n")[:20]
                formatter.add_data("sample_code_lines", len(lines))
                for line in lines:
                    formatter.print(f"  {line}")
                formatter.print("  ...")
            
        except Exception as e:
            formatter.add_error(f"Demo failed: {e}")
            formatter.print(f"❌ Demo failed: {e}", level="error")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()