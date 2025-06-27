#!/usr/bin/env python3
"""
Weaver CLI Commands - 80/20 refactor interface

Provides commands to use the WeaverEngine for auto-generating everything
from semantic conventions.
"""

import typer
from pathlib import Path
from typing import Optional
from loguru import logger
from rich.table import Table
from rich.console import Console

from ..core.weaver_engine import WeaverEngine, GenerationType
from ..utils.json_output import json_command
from .hyper_weaver import app as hyper_app


app = typer.Typer(help="Weaver-first auto-generation commands")
console = Console()

# Add hyper-advanced decorator commands
app.add_typer(hyper_app, name="hyper", help="Hyper-Advanced AI-Driven Weaver Commands")


@app.command("generate")
def generate(
    convention_name: str = typer.Argument(..., help="Name of semantic convention to generate from"),
    artifact_type: str = typer.Option(
        "all", "--type", "-t", 
        help="Type of artifact to generate (model, cli, test, doc, all)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output directory (default: src/dslmodel/generated)"
    )
):
    """Generate artifacts from semantic convention - 80/20 core command"""
    
    with json_command("weaver-generate") as formatter:
        formatter.add_data("convention_name", convention_name)
        formatter.add_data("artifact_type", artifact_type)
        
        formatter.print(f"🚀 Generating {artifact_type} from semantic convention: {convention_name}")
        
        try:
            engine = WeaverEngine()
            if output_dir:
                engine.output_path = output_dir
            
            # Validate convention first
            validation = engine.validate_convention(convention_name)
            formatter.add_data("validation", validation)
            
            if not validation["valid"]:
                formatter.print("❌ Convention validation failed:")
                for error in validation["errors"]:
                    formatter.print(f"  - {error}")
                formatter.add_data("generation_successful", False)
                raise typer.Exit(1)
            
            formatter.print(f"✅ Convention validated: {validation['spans_count']} spans")
            
            # Generate artifacts
            if artifact_type == "all":
                results = engine.generate_all(convention_name)
            elif artifact_type == "model":
                results = [engine.generate_model(convention_name)]
            elif artifact_type == "cli":
                results = [engine.generate_cli(convention_name)]
            elif artifact_type == "test":
                results = [engine.generate_tests(convention_name)]
            elif artifact_type == "doc":
                results = [engine.generate_docs(convention_name)]
            else:
                formatter.print(f"❌ Unknown artifact type: {artifact_type}")
                formatter.add_data("generation_successful", False)
                raise typer.Exit(1)
            
            # Process results
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            formatter.add_data("results_successful", len(successful))
            formatter.add_data("results_failed", len(failed))
            formatter.add_data("generation_successful", len(failed) == 0)
            
            # Show results table
            table = Table(title=f"Generation Results for {convention_name}")
            table.add_column("Artifact", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("File", style="blue")
            table.add_column("Spans", style="yellow")
            
            for result in results:
                status = "✅ Success" if result.success else "❌ Failed"
                spans_count = str(len(result.telemetry_spans))
                table.add_row(
                    result.artifact_type,
                    status,
                    str(result.file_path),
                    spans_count
                )
            
            console.print(table)
            
            if successful:
                formatter.print(f"\n🎯 Generated {len(successful)} artifacts successfully!")
                formatter.print("Next steps:")
                
                if any(r.artifact_type == "cli" for r in successful):
                    cli_file = next(r.file_path for r in successful if r.artifact_type == "cli")
                    formatter.print(f"  • Try CLI: python {cli_file} --help")
                
                if any(r.artifact_type == "test" for r in successful):
                    test_file = next(r.file_path for r in successful if r.artifact_type == "test")
                    formatter.print(f"  • Run tests: pytest {test_file}")
                
                if any(r.artifact_type == "model" for r in successful):
                    formatter.print(f"  • Import models: from dslmodel.generated.models.{convention_name} import *")
            
            if failed:
                formatter.print(f"\n⚠️ {len(failed)} artifacts failed to generate")
                for result in failed:
                    if result.validation_errors:
                        for error in result.validation_errors:
                            formatter.print(f"  - {result.artifact_type}: {error}")
        
        except Exception as e:
            formatter.add_error(f"Generation failed: {e}")
            formatter.print(f"❌ Generation failed: {e}")
            raise typer.Exit(1)


@app.command("list")
def list_conventions():
    """List available semantic conventions"""
    
    with json_command("weaver-list") as formatter:
        try:
            engine = WeaverEngine()
            conventions = engine.list_conventions()
            
            formatter.add_data("conventions_count", len(conventions))
            formatter.add_data("conventions", conventions)
            
            if conventions:
                formatter.print(f"📋 Found {len(conventions)} semantic conventions:")
                
                table = Table(title="Available Semantic Conventions")
                table.add_column("Convention", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Spans", style="yellow")
                
                for conv in conventions:
                    try:
                        validation = engine.validate_convention(conv)
                        status = "✅ Valid" if validation["valid"] else "❌ Invalid"
                        spans = str(validation.get("spans_count", 0))
                    except Exception:
                        status = "❓ Unknown"
                        spans = "?"
                    
                    table.add_row(conv, status, spans)
                
                console.print(table)
                
                formatter.print(f"\nTo generate from a convention:")
                formatter.print(f"  dsl weaver generate <convention_name>")
            else:
                formatter.print("No semantic conventions found in registry/semantic/")
                formatter.print("Create a .yaml file in src/dslmodel/registry/semantic/ to get started")
        
        except Exception as e:
            formatter.add_error(f"List failed: {e}")
            formatter.print(f"❌ Failed to list conventions: {e}")
            raise typer.Exit(1)


@app.command("validate")
def validate_convention(
    convention_name: str = typer.Argument(..., help="Name of convention to validate")
):
    """Validate a semantic convention"""
    
    with json_command("weaver-validate") as formatter:
        formatter.add_data("convention_name", convention_name)
        
        try:
            engine = WeaverEngine()
            validation = engine.validate_convention(convention_name)
            
            formatter.add_data("validation", validation)
            
            if validation["valid"]:
                formatter.print(f"✅ Convention '{convention_name}' is valid")
                formatter.print(f"   Groups: {validation['groups_count']}")
                formatter.print(f"   Spans: {validation['spans_count']}")
                
                if validation.get("warnings"):
                    formatter.print("⚠️  Warnings:")
                    for warning in validation["warnings"]:
                        formatter.print(f"   - {warning}")
            else:
                formatter.print(f"❌ Convention '{convention_name}' has errors:")
                for error in validation["errors"]:
                    formatter.print(f"   - {error}")
                
                formatter.add_data("validation_successful", False)
                raise typer.Exit(1)
            
            formatter.add_data("validation_successful", True)
        
        except FileNotFoundError:
            formatter.add_error(f"Convention not found: {convention_name}")
            formatter.print(f"❌ Convention not found: {convention_name}")
            formatter.print(f"Available conventions: {engine.list_conventions()}")
            raise typer.Exit(1)
        except Exception as e:
            formatter.add_error(f"Validation failed: {e}")
            formatter.print(f"❌ Validation failed: {e}")
            raise typer.Exit(1)


@app.command("demo")
def demo():
    """Run a demonstration of Weaver-first generation"""
    
    with json_command("weaver-demo") as formatter:
        formatter.print("🎯 Weaver-First 80/20 Refactor Demo")
        formatter.print("=" * 50)
        
        try:
            engine = WeaverEngine()
            
            # Check if we have the demo convention
            conventions = engine.list_conventions()
            demo_convention = "user_workflow"
            
            if demo_convention not in conventions:
                formatter.print(f"❌ Demo convention '{demo_convention}' not found")
                formatter.print("Available conventions:", conventions)
                formatter.add_data("demo_successful", False)
                raise typer.Exit(1)
            
            formatter.print(f"📋 Using demo convention: {demo_convention}")
            
            # Validate first
            validation = engine.validate_convention(demo_convention)
            formatter.add_data("validation", validation)
            
            if not validation["valid"]:
                formatter.print("❌ Demo convention is invalid:")
                for error in validation["errors"]:
                    formatter.print(f"  - {error}")
                formatter.add_data("demo_successful", False)
                raise typer.Exit(1)
            
            formatter.print(f"✅ Convention validated: {validation['spans_count']} spans")
            
            # Generate all artifacts
            formatter.print("\n🚀 Generating all artifacts...")
            results = engine.generate_all(demo_convention)
            
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            formatter.add_data("artifacts_generated", len(successful))
            formatter.add_data("artifacts_failed", len(failed))
            formatter.add_data("demo_successful", len(failed) == 0)
            
            # Show what was generated
            formatter.print(f"\n📊 Generated {len(successful)} artifacts:")
            for result in successful:
                formatter.print(f"  ✅ {result.artifact_type}: {result.file_path}")
            
            if failed:
                formatter.print(f"\n❌ Failed to generate {len(failed)} artifacts:")
                for result in failed:
                    formatter.print(f"  ❌ {result.artifact_type}: {result.content_preview}")
            
            # Show usage examples
            formatter.print("\n🎯 Demo Complete! Next steps:")
            formatter.print("1. Check generated files in src/dslmodel/generated/")
            formatter.print("2. Try the generated CLI:")
            formatter.print(f"   python src/dslmodel/generated/cli/{demo_convention}_cli.py --help")
            formatter.print("3. Run the generated tests:")
            formatter.print(f"   pytest src/dslmodel/generated/tests/test_{demo_convention}.py")
            formatter.print("4. View the documentation:")
            formatter.print(f"   cat src/dslmodel/generated/docs/{demo_convention}.md")
            
            formatter.print("\n✨ This is the power of Weaver-first development:")
            formatter.print("   Define telemetry once → Generate everything automatically!")
        
        except Exception as e:
            formatter.add_error(f"Demo failed: {e}")
            formatter.print(f"❌ Demo failed: {e}")
            formatter.add_data("demo_successful", False)
            raise typer.Exit(1)


@app.command("init")
def init_registry():
    """Initialize a new semantic convention registry"""
    
    with json_command("weaver-init") as formatter:
        try:
            registry_path = Path("src/dslmodel/registry")
            
            # Create directory structure
            directories = [
                registry_path / "semantic",
                registry_path / "templates" / "python",
                registry_path / "templates" / "cli", 
                registry_path / "templates" / "tests",
                registry_path / "templates" / "docs"
            ]
            
            for dir_path in directories:
                dir_path.mkdir(parents=True, exist_ok=True)
                formatter.print(f"📁 Created: {dir_path}")
            
            # Initialize WeaverEngine to create default templates
            engine = WeaverEngine(registry_path)
            
            formatter.print("🎯 Registry initialized successfully!")
            formatter.print("Next steps:")
            formatter.print("1. Create semantic conventions in registry/semantic/")
            formatter.print("2. Run 'dsl weaver generate <convention_name>'")
            formatter.print("3. Use generated artifacts in your application")
            
            formatter.add_data("directories_created", len(directories))
            formatter.add_data("registry_path", str(registry_path))
            formatter.add_data("init_successful", True)
        
        except Exception as e:
            formatter.add_error(f"Initialization failed: {e}")
            formatter.print(f"❌ Initialization failed: {e}")
            formatter.add_data("init_successful", False)
            raise typer.Exit(1)


if __name__ == "__main__":
    app()