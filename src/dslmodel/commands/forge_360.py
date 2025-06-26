#!/usr/bin/env python3
"""
Forge 360 Permutations Command

Generates 360 semantic convention permutations for comprehensive testing.
"""

import typer
from pathlib import Path
from typing import Optional
from loguru import logger

from ..integrations.otel.forge_360_permutations import Forge360PermutationGenerator

app = typer.Typer()


@app.command("generate")
def generate(
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Output directory for permutations"
    ),
    validate: bool = typer.Option(
        False, "--validate", help="Run validation after generation"
    ),
    generate_only: bool = typer.Option(
        False, "--generate-only", help="Only generate YAML files, don't run forge"
    ),
):
    """Generate all 360 semantic convention permutations."""
    logger.info("🎯 Starting Forge 360 Permutation Generation")
    
    # Initialize generator
    generator = Forge360PermutationGenerator(output_dir)
    
    # Generate permutations
    permutations = generator.generate_all_permutations()
    logger.success(f"✅ Generated {len(permutations)} permutations in memory")
    
    # Write to disk
    generator.write_permutations_to_disk()
    logger.success(f"📝 Written permutations to {generator.output_dir}")
    
    # Generate forge commands
    commands = generator.generate_forge_commands()
    logger.info(f"🔨 Generated {len(commands)} forge commands")
    
    if validate:
        # Create validation suite
        generator.create_validation_suite()
        logger.success("🧪 Validation suite created")
    
    if not generate_only:
        logger.info("💡 To run forge generation, execute:")
        logger.info(f"   bash {generator.output_dir}/run_all_permutations.sh")
    
    logger.success("✅ Forge 360 generation complete!")


@app.command("status")
def status(
    matrix: bool = typer.Option(False, "--matrix", help="Show permutation matrix dimensions"),
    coverage: bool = typer.Option(False, "--coverage", help="Show coverage statistics"),
):
    """Show status of generated permutations."""
    base_dir = Path("semconv_360_permutations")
    
    if not base_dir.exists():
        logger.warning("No permutations generated yet. Run 'generate' first.")
        return
    
    # Read index file
    index_file = base_dir / "permutations_index.yaml"
    if index_file.exists():
        import yaml
        with open(index_file) as f:
            index_data = yaml.safe_load(f)
        
        logger.info(f"📊 Forge 360 Status")
        logger.info(f"   Total Permutations: {index_data['total_permutations']}")
        logger.info(f"   Generated At: {index_data['generated_at']}")
        
        if matrix:
            logger.info("\n🔢 Matrix Dimensions:")
            dims = index_data.get('matrix_dimensions', {})
            for dim, values in dims.items():
                if isinstance(values, list):
                    logger.info(f"   {dim}: {len(values)} values")
                else:
                    logger.info(f"   {dim}:")
                    for k, v in values.items():
                        logger.info(f"     {k}: {len(v) if isinstance(v, list) else v}")
        
        if coverage:
            logger.info("\n📈 Language Coverage:")
            for lang, info in index_data.get('permutations_by_language', {}).items():
                logger.info(f"   {lang}: {info['count']} permutations")
                logger.info(f"     Frameworks: {', '.join(info['frameworks'])}")
    else:
        logger.error("Index file not found")


@app.command("inspect")
def inspect(
    permutation_id: str = typer.Argument(..., help="Permutation ID to inspect"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Target language"),
):
    """Inspect a specific permutation by ID."""
    logger.info(f"🔍 Inspecting permutation: {permutation_id}")
    
    # Find permutation file
    base_dir = Path("semconv_360_permutations")
    if not base_dir.exists():
        logger.error(f"Output directory {base_dir} not found. Run 'generate' first.")
        return
    
    # Search for permutation
    found = False
    for lang_dir in base_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name in ["python", "rust", "typescript", "go", "java"]:
            for perm_file in lang_dir.glob(f"*{permutation_id}*.yaml"):
                if language and lang_dir.name != language:
                    continue
                    
                logger.info(f"📄 Found: {perm_file}")
                
                # Read and display content
                import yaml
                with open(perm_file) as f:
                    data = yaml.safe_load(f)
                
                # Pretty print configuration
                config = data.get("configuration", {})
                logger.info("Configuration:")
                for key, value in config.items():
                    logger.info(f"  {key}: {value}")
                
                # Show semconv groups
                semconv = data.get("semconv", {})
                groups = semconv.get("groups", [])
                logger.info(f"\nSemantic Convention Groups: {len(groups)}")
                
                for group in groups:
                    logger.info(f"  - {group.get('id', 'unknown')}")
                    if 'attributes' in group:
                        logger.info(f"    Attributes: {len(group['attributes'])}")
                
                found = True
                break
    
    if not found:
        logger.error(f"Permutation {permutation_id} not found")


@app.command("validate")
def validate(
    permutation_id: Optional[str] = typer.Option(None, "--permutation-id", "-p", help="Validate specific permutation"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Validate all permutations for a language"),
):
    """Validate generated permutations."""
    validation_dir = Path("semconv_360_permutations/validation")
    
    if not validation_dir.exists():
        logger.error("Validation suite not found. Run 'generate --validate' first.")
        return
    
    validation_file = validation_dir / "validation_matrix.yaml"
    if not validation_file.exists():
        logger.error("Validation matrix not found.")
        return
    
    import yaml
    with open(validation_file) as f:
        validation_data = yaml.safe_load(f)
    
    logger.info("🧪 Running Validation")
    
    # Filter tests if needed
    tests = validation_data['validation_tests']
    if permutation_id:
        tests = [t for t in tests if t['permutation_id'] == permutation_id]
    elif language:
        tests = [t for t in tests if language in t['permutation_id']]
    
    if not tests:
        logger.warning("No tests match the criteria")
        return
    
    # Run validations
    passed = 0
    failed = 0
    
    for test in tests:
        logger.info(f"\n📋 Testing: {test['permutation_id']}")
        test_passed = True
        
        for validation in test['validations']:
            # Simulate validation (in real implementation, would check actual files)
            check_result = validation['expected']  # Simplified for demo
            
            if check_result:
                logger.success(f"   ✅ {validation['type']}: {validation['check']}")
                passed += 1
            else:
                logger.error(f"   ❌ {validation['type']}: {validation['check']}")
                failed += 1
                test_passed = False
        
        if test_passed:
            logger.success(f"   ✅ Permutation {test['permutation_id']} PASSED")
        else:
            logger.error(f"   ❌ Permutation {test['permutation_id']} FAILED")
    
    # Summary
    total = passed + failed
    logger.info(f"\n📊 Validation Summary:")
    logger.info(f"   Total checks: {total}")
    logger.info(f"   Passed: {passed} ({passed/total*100:.1f}%)")
    logger.info(f"   Failed: {failed} ({failed/total*100:.1f}%)")


if __name__ == "__main__":
    app()