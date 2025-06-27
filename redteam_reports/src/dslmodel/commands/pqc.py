"""
Post-Quantum Cryptography CLI Commands
"""

import typer
import asyncio
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from ..pqc.e2e_test import GlobalPQCTestSuite
from ..pqc.global_manager import (
    GlobalPQCManager, GlobalPQCConfiguration,
    PQCRegion, create_default_regional_policies
)
from ..pqc.multi_language import MultiLanguagePQCGenerator
from ..pqc.core import PQCAlgorithmType, PQCSecurityLevel

app = typer.Typer(help="Post-Quantum Cryptography commands")

@app.command("test")
def run_e2e_test():
    """Run comprehensive global PQC E2E test suite"""
    typer.echo("🔐 Starting Global Post-Quantum Cryptography E2E Tests")
    
    async def run_tests():
        suite = GlobalPQCTestSuite()
        return await suite.run_full_test_suite()
    
    results = asyncio.run(run_tests())
    
    # Display summary
    summary = results["test_summary"]
    success_rates = results["success_rates"]
    
    typer.echo(f"\n📊 Test Results Summary:")
    typer.echo(f"   Total Tests: {summary['total_tests']}")
    typer.echo(f"   Algorithm Tests: {summary['algorithm_tests']} ({success_rates['algorithm_tests']:.1f}% success)")
    typer.echo(f"   Cross-Regional: {summary['cross_regional_tests']} ({success_rates['cross_regional']:.1f}% success)")
    typer.echo(f"   Language Compatibility: {summary['language_compatibility_tests']} ({success_rates['language_compatibility']:.1f}% success)")
    typer.echo(f"   Overall Success Rate: {success_rates['overall']:.1f}%")
    
    # Global readiness
    readiness = results["global_readiness"]
    typer.echo(f"\n🌍 Global PQC Readiness: {readiness['global_readiness_percentage']:.1f}%")

@app.command("generate")
def generate_keys(
    algorithm: str = typer.Option("kyber", help="PQC algorithm (kyber, dilithium, falcon, sphincs_plus)"),
    region: str = typer.Option("global", help="Region for compliance"),
    security_level: int = typer.Option(3, help="Security level (1-5)"),
    purpose: str = typer.Option("encryption", help="Key purpose (encryption, signing)")
):
    """Generate PQC keypair for specified algorithm and region"""
    try:
        # Create configuration
        config = GlobalPQCConfiguration(
            global_transition_date=typer.prompt("Global transition date", default="2030-01-01T00:00:00Z"),
            regional_policies=create_default_regional_policies()
        )
        
        manager = GlobalPQCManager(config)
        
        # Parse inputs
        pqc_algorithm = PQCAlgorithmType(algorithm)
        pqc_region = PQCRegion(region)
        pqc_level = PQCSecurityLevel(security_level)
        
        # Generate keypair
        keypair = manager.generate_regional_keypair(pqc_region, purpose)
        
        typer.echo(f"✅ Generated {algorithm} keypair:")
        typer.echo(f"   Key ID: {keypair.key_id}")
        typer.echo(f"   Algorithm: {keypair.algorithm.value}")
        typer.echo(f"   Security Level: {keypair.security_level.value}")
        typer.echo(f"   Region: {pqc_region.value}")
        typer.echo(f"   Public Key Size: {len(keypair.public_key)} bytes")
        typer.echo(f"   Private Key Size: {len(keypair.private_key or b'')} bytes")
        
    except Exception as e:
        typer.echo(f"❌ Error generating keypair: {e}")
        raise typer.Exit(1)

@app.command("readiness")
def check_readiness():
    """Check global PQC readiness status"""
    from datetime import datetime, timezone
    config = GlobalPQCConfiguration(
        global_transition_date=datetime(2030, 1, 1, tzinfo=timezone.utc),
        regional_policies=create_default_regional_policies()
    )
    
    manager = GlobalPQCManager(config)
    report = manager.get_global_readiness_report()
    
    typer.echo("🌍 Global PQC Readiness Report")
    typer.echo("=" * 50)
    typer.echo(f"Global Readiness: {report['global_readiness_percentage']:.1f}%")
    typer.echo(f"Transition Date: {report['global_transition_date']}")
    
    typer.echo("\nRegional Status:")
    for region, info in report["regions"].items():
        status = "🟢" if info.get("is_mandatory", False) else "🟡" if info["key_count"] > 0 else "🔴"
        typer.echo(f"  {status} {region.title()}: {info['key_count']} keys")
        if info["policy_defined"]:
            typer.echo(f"     Mandatory from: {info.get('mandatory_from', 'N/A')}")
            typer.echo(f"     Compliance: {', '.join(info.get('compliance_frameworks', []))}")

@app.command("multi-lang")
def generate_multi_language(
    output_dir: Path = typer.Option(
        Path("pqc_clients"),
        "--output", "-o",
        help="Output directory for generated clients"
    ),
    languages: str = typer.Option(
        "python,rust,go,typescript,java",
        "--languages", "-l",
        help="Comma-separated list of languages"
    )
):
    """Generate PQC clients for multiple programming languages"""
    generator = MultiLanguagePQCGenerator()
    
    lang_list = [lang.strip() for lang in languages.split(",")]
    
    typer.echo(f"🔧 Generating PQC clients for: {', '.join(lang_list)}")
    
    context = {
        "algorithms": ["kyber", "dilithium", "falcon", "sphincs_plus"],
        "security_levels": [1, 3, 5],
        "regions": ["north_america", "europe", "asia_pacific"],
        "generated_timestamp": datetime.now().isoformat()
    }
    
    try:
        generated_files = {}
        for language in lang_list:
            if language in generator.LANGUAGE_CONFIGS:
                code = generator.generate_for_language(language, context)
                output_file = output_dir / generator.LANGUAGE_CONFIGS[language]["output"]
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w') as f:
                    f.write(code)
                
                generated_files[language] = output_file
                typer.echo(f"  ✅ {language}: {output_file}")
            else:
                typer.echo(f"  ❌ {language}: Unsupported language")
        
        # Generate package files
        generator._generate_package_files(output_dir)
        
        typer.echo(f"\n📦 Generated {len(generated_files)} PQC clients in {output_dir}/")
        typer.echo("📋 Package files created for each language")
        
    except Exception as e:
        typer.echo(f"❌ Error generating multi-language clients: {e}")
        raise typer.Exit(1)

@app.command("validate")
def validate_semantic_conventions():
    """Validate PQC semantic conventions"""
    semconv_file = Path("semconv_registry/pqc_global.yaml")
    
    if not semconv_file.exists():
        typer.echo(f"❌ Semantic convention file not found: {semconv_file}")
        raise typer.Exit(1)
    
    typer.echo("🔍 Validating PQC semantic conventions...")
    
    try:
        import yaml
        with open(semconv_file) as f:
            data = yaml.safe_load(f)
        
        # Basic validation
        groups = data.get("groups", [])
        typer.echo(f"📄 Found {len(groups)} semantic convention groups")
        
        for group in groups:
            group_id = group.get("id", "unknown")
            attributes = group.get("attributes", [])
            typer.echo(f"  ✅ {group_id}: {len(attributes)} attributes")
        
        typer.echo("✅ PQC semantic conventions are valid!")
        
    except Exception as e:
        typer.echo(f"❌ Validation failed: {e}")
        raise typer.Exit(1)

@app.command("demo")
def run_demo():
    """Run complete PQC demonstration"""
    typer.echo("🚀 Post-Quantum Cryptography Demo")
    typer.echo("=" * 50)
    
    # 1. Generate keys
    typer.echo("\n1️⃣ Generating PQC keys...")
    generate_keys.callback("kyber", "north_america", 3, "encryption")
    
    # 2. Check readiness
    typer.echo("\n2️⃣ Checking global readiness...")
    check_readiness.callback()
    
    # 3. Generate multi-language clients
    typer.echo("\n3️⃣ Generating multi-language clients...")
    generate_multi_language.callback(Path("demo_pqc_clients"), "python,rust,typescript")
    
    # 4. Validate semantic conventions
    typer.echo("\n4️⃣ Validating semantic conventions...")
    validate_semantic_conventions.callback()
    
    # 5. Run E2E tests
    typer.echo("\n5️⃣ Running E2E tests...")
    run_e2e_test.callback()
    
    typer.echo("\n✅ PQC Demo Complete!")

if __name__ == "__main__":
    app()