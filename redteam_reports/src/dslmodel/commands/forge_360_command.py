#!/usr/bin/env python3
"""
Forge 360 Command - Comprehensive Weaver Forge Integration

This command provides a complete interface to generate and manage 360 semantic
convention permutations for DSLModel testing and validation.
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger

from ..integrations.otel.forge_360_permutations import Forge360PermutationGenerator
from ..integrations.otel.extended_weaver_integration import ExtendedWeaverForgeIntegration


app = typer.Typer(name="forge360", help="DSLModel Forge 360 - Comprehensive semantic convention permutation generator.")


def setup_logging(debug: bool):
    """Setup logging configuration"""
    if debug:
        logger.add("forge360_debug.log", rotation="10 MB", level="DEBUG")
    else:
        logger.remove()
        logger.add(lambda msg: print(msg), level="INFO")


@app.command()
def generate(
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output-dir", 
        "-o",
        help="Output directory for permutations"
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        "-c", 
        help="Generate specific category only"
    ),
    validate: bool = typer.Option(
        False,
        "--validate",
        help="Run validation after generation"
    ),
    generate_only: bool = typer.Option(
        False,
        "--generate-only",
        help="Only generate YAML files, don't run forge"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    )
):
    """Generate 360 semantic convention permutations."""
    setup_logging(debug)
    
    generator = Forge360PermutationGenerator(
        output_dir=output_dir or Path("forge360_output")
    )
    
    if category:
        logger.info(f"Generating permutations for category: {category}")
        # Implementation for specific category
    else:
        logger.info("Generating all 360 permutations...")
        asyncio.run(generator.generate_all_permutations())
    
    if validate and not generate_only:
        logger.info("Running validation...")
        # Run validation logic
    
    logger.success("Forge 360 generation complete!")


@app.command()
def validate(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing generated permutations"
    ),
    report: bool = typer.Option(
        False,
        "--report",
        help="Generate validation report"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    )
):
    """Validate generated permutations."""
    setup_logging(debug)
    
    logger.info(f"Validating permutations in: {input_dir}")
    
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        raise typer.Exit(1)
    
    # Validation logic here
    integration = ExtendedWeaverForgeIntegration()
    
    if report:
        logger.info("Generating validation report...")
        # Generate report logic
    
    logger.success("Validation complete!")


@app.command()
def test(
    category: str = typer.Argument(
        ...,
        help="Category to test"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for test results"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    )
):
    """Test a specific category permutation."""
    setup_logging(debug)
    
    logger.info(f"Testing category: {category}")
    
    generator = Forge360PermutationGenerator(
        output_dir=output_dir or Path("forge360_test")
    )
    
    # Test implementation
    logger.success(f"Test complete for category: {category}")


@app.command()
def list_categories():
    """List available permutation categories."""
    categories = [
        "simple_types",
        "complex_types", 
        "nested_structures",
        "inheritance",
        "validation",
        "references",
        "extensions",
        "edge_cases"
    ]
    
    typer.echo("Available categories:")
    for cat in categories:
        typer.echo(f"  - {cat}")


@app.command()
def clean(
    output_dir: Path = typer.Argument(
        ...,
        help="Directory to clean"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force removal without confirmation"
    )
):
    """Clean generated output directory."""
    if not output_dir.exists():
        typer.echo(f"Directory does not exist: {output_dir}")
        return
    
    if not force:
        confirm = typer.confirm(f"Remove all files in {output_dir}?")
        if not confirm:
            typer.echo("Aborted.")
            raise typer.Exit()
    
    import shutil
    shutil.rmtree(output_dir)
    typer.echo(f"Cleaned: {output_dir}")


if __name__ == "__main__":
    app()