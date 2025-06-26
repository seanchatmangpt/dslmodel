#!/usr/bin/env python3
"""
Demonstration of Weaver Forge 360 Permutations for DSLModel

This script showcases:
1. Generation of 360 semantic convention permutations
2. Coverage across multiple dimensions (span types, attributes, metrics, languages, frameworks)
3. Validation and testing capabilities
4. Integration with Weaver Forge workflow
"""

import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def demonstrate_forge_360():
    """Demonstrate the 360 permutations feature"""
    
    console.print(Panel.fit(
        "🎯 [bold blue]Weaver Forge 360 Permutations Demo[/bold blue]\n"
        "Comprehensive semantic convention testing across multiple dimensions",
        border_style="blue"
    ))
    
    # Check if permutations exist
    demo_dir = Path("forge_360_demo")
    if not demo_dir.exists():
        console.print("❌ No permutations found. Please run: [cyan]dsl forge permutations generate[/cyan]")
        return
    
    # Load index
    index_file = demo_dir / "permutations_index.yaml"
    with open(index_file) as f:
        index = yaml.safe_load(f)
    
    # Display overview
    console.print("\n📊 [bold]Permutation Overview[/bold]")
    console.print(f"Total Permutations: [green]{index['total_permutations']}[/green]")
    console.print(f"Generated At: {index['generated_at']}")
    
    # Show matrix dimensions
    console.print("\n🔢 [bold]Matrix Dimensions[/bold]")
    
    dim_table = Table(show_header=True, header_style="bold magenta")
    dim_table.add_column("Dimension", style="cyan")
    dim_table.add_column("Values", style="yellow")
    dim_table.add_column("Count", style="green")
    
    dims = index['matrix_dimensions']
    dim_table.add_row("Span Types", ", ".join(dims['span_types'][:3]) + "...", str(len(dims['span_types'])))
    dim_table.add_row("Attribute Sets", ", ".join(dims['attribute_sets']), str(len(dims['attribute_sets'])))
    dim_table.add_row("Metric Types", ", ".join(dims['metric_types'][:3]) + "...", str(len(dims['metric_types'])))
    dim_table.add_row("Languages", ", ".join(dims['languages']), str(len(dims['languages'])))
    
    console.print(dim_table)
    
    # Show language coverage
    console.print("\n🌐 [bold]Language Coverage[/bold]")
    
    lang_table = Table(show_header=True, header_style="bold blue")
    lang_table.add_column("Language", style="cyan")
    lang_table.add_column("Permutations", style="yellow")
    lang_table.add_column("Frameworks", style="green")
    
    for lang, info in index['permutations_by_language'].items():
        frameworks = ", ".join(info['frameworks'])
        lang_table.add_row(lang.capitalize(), str(info['count']), frameworks)
    
    console.print(lang_table)
    
    # Show sample permutations
    console.print("\n📄 [bold]Sample Permutations[/bold]")
    
    # Python sample
    python_sample = demo_dir / "python" / "permutation_060_http_extended_counter_python_pydantic.yaml"
    if python_sample.exists():
        with open(python_sample) as f:
            perm_data = yaml.safe_load(f)
        
        console.print("\n[bold cyan]Python/Pydantic HTTP Extended Counter:[/bold cyan]")
        config = perm_data['configuration']
        console.print(f"  Span Type: {config['span_type']}")
        console.print(f"  Attributes: {config['attribute_set']} set")
        console.print(f"  Metric: {config['metric_type']}")
        
        # Show attributes
        attrs = perm_data['semconv']['groups'][0]['attributes']
        console.print(f"  Attribute Count: {len(attrs)}")
        for attr in attrs[:3]:
            console.print(f"    - {attr['id']}: {attr['type']} ({attr['requirement_level']})")
        if len(attrs) > 3:
            console.print(f"    ... and {len(attrs) - 3} more")
    
    # Rust sample
    rust_sample = demo_dir / "rust" / "permutation_182_database_extended_counter_rust_serde.yaml"
    if rust_sample.exists():
        with open(rust_sample) as f:
            perm_data = yaml.safe_load(f)
        
        console.print("\n[bold red]Rust/Serde Database Extended Counter:[/bold red]")
        config = perm_data['configuration']
        console.print(f"  Span Type: {config['span_type']}")
        console.print(f"  Framework: {config['framework']}")
        template_cfg = config['template_config']
        console.print(f"  Derives: {', '.join(template_cfg['derives'])}")
    
    # Show validation info
    validation_file = demo_dir / "validation" / "validation_matrix.yaml"
    if validation_file.exists():
        with open(validation_file) as f:
            val_data = yaml.safe_load(f)
        
        console.print("\n🧪 [bold]Validation Coverage[/bold]")
        console.print(f"Total Validation Tests: {len(val_data['validation_tests'])}")
        coverage = val_data.get('coverage_percentage', 100)
        console.print(f"Test Coverage: {coverage}%")
    
    # Show forge commands
    console.print("\n🔨 [bold]Forge Generation[/bold]")
    forge_script = demo_dir / "run_all_permutations.sh"
    if forge_script.exists():
        console.print(f"Batch Script: [green]✓[/green] {forge_script}")
        # Show first few commands
        with open(forge_script) as f:
            lines = f.readlines()
        
        console.print("\nSample forge commands:")
        for line in lines[3:6]:  # Skip header
            if line.strip() and line.startswith("weaver"):
                console.print(f"  [dim]{line.strip()}[/dim]")
        console.print(f"  ... and {len(lines) - 10} more commands")
    
    # Usage examples
    console.print("\n💡 [bold]Usage Examples[/bold]")
    console.print("\n1. Generate all permutations:")
    console.print("   [cyan]dsl forge permutations generate[/cyan]")
    
    console.print("\n2. Generate with validation:")
    console.print("   [cyan]dsl forge permutations generate --validate[/cyan]")
    
    console.print("\n3. Check status:")
    console.print("   [cyan]dsl forge permutations status --matrix --coverage[/cyan]")
    
    console.print("\n4. Inspect specific permutation:")
    console.print("   [cyan]dsl forge permutations inspect http_minimal_counter_python_pydantic[/cyan]")
    
    console.print("\n5. Run validation tests:")
    console.print("   [cyan]dsl forge permutations validate --language python[/cyan]")
    
    console.print("\n6. Generate code from permutations:")
    console.print("   [cyan]bash forge_360_demo/run_all_permutations.sh[/cyan]")
    
    # Show benefits
    console.print("\n✨ [bold]Benefits of 360 Permutations[/bold]")
    benefits = [
        "Comprehensive testing across all supported languages and frameworks",
        "Systematic coverage of different span types (HTTP, database, messaging, etc.)",
        "Validation of minimal, standard, extended, and custom attribute sets",
        "Automatic generation of test matrices for CI/CD pipelines",
        "Consistent semantic conventions across polyglot environments",
        "Rapid prototyping of telemetry implementations"
    ]
    
    for benefit in benefits:
        console.print(f"  • {benefit}")
    
    # Architecture diagram
    console.print("\n🏗️  [bold]Architecture[/bold]")
    console.print("""
    ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
    │ Matrix          │────▶│ 360 Permutations │────▶│ Weaver Forge    │
    │ Definition      │     │ Generator        │     │ Commands        │
    └─────────────────┘     └──────────────────┘     └─────────────────┘
            │                        │                         │
            ▼                        ▼                         ▼
    ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
    │ • Span Types    │     │ • YAML Files     │     │ • Python Code   │
    │ • Attributes    │     │ • Validation     │     │ • Rust Code     │
    │ • Metrics       │     │ • Coverage       │     │ • TypeScript    │
    │ • Languages     │     │ • Test Matrix    │     │ • Go Code       │
    │ • Frameworks    │     │                  │     │ • Java Code     │
    └─────────────────┘     └──────────────────┘     └─────────────────┘
    """)
    
    console.print("\n🎯 [bold green]Demo Complete![/bold green]")
    console.print("The 360 permutations provide comprehensive coverage for DSLModel across all target platforms.")


if __name__ == "__main__":
    demonstrate_forge_360()