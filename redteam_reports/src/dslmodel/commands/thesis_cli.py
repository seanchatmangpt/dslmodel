"""
Thesis CLI Commands
SwarmSH thesis implementation and demonstration commands
"""

import typer
from pathlib import Path
from typing import Optional
from rich import print
from rich.console import Console
from rich.table import Table

from dslmodel.thesis import ThesisComplete
from dslmodel.utils.dspy_tools import init_lm

app = typer.Typer(help="SwarmSH Thesis commands")
console = Console()


@app.command("generate")
def generate_thesis(
    output_dir: Path = typer.Option(Path.cwd(), "--output", "-o", help="Output directory"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, both"),
    model: str = typer.Option("ollama/qwen2.5", "--model", "-m", help="LLM model to use")
):
    """Generate complete SwarmSH thesis with all artifacts"""
    
    console.print("🎓 [bold blue]Generating SwarmSH Thesis[/bold blue]")
    
    # Initialize LLM
    init_lm(model=model)
    
    # Create thesis
    thesis = ThesisComplete.create_default_thesis()
    
    # Save in requested formats
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files_created = []
    
    if format in ["json", "both"]:
        json_path = output_dir / "thesis_complete.json"
        thesis.to_json(file_path=str(json_path))
        files_created.append(str(json_path))
    
    if format in ["yaml", "both"]:
        yaml_path = output_dir / "thesis_complete.yaml"
        thesis.to_yaml(file_path=str(yaml_path))
        files_created.append(str(yaml_path))
    
    # Generate OTEL semantic conventions
    semconv_path = output_dir / "thesis_semconv.yaml"
    with open(semconv_path, "w") as f:
        f.write(thesis.generate_otel_yaml())
    files_created.append(str(semconv_path))
    
    # Generate Rust implementation
    rust_path = output_dir / "thesis_spans.rs"
    with open(rust_path, "w") as f:
        f.write(thesis.generate_forge_rust())
    files_created.append(str(rust_path))
    
    console.print("✅ [green]Thesis generated successfully![/green]")
    
    # Show summary
    table = Table(title="Generated Files")
    table.add_column("File", style="cyan")
    table.add_column("Description", style="magenta")
    
    for file_path in files_created:
        if "json" in file_path:
            table.add_row(file_path, "Complete thesis data (JSON)")
        elif "yaml" in file_path and "semconv" not in file_path:
            table.add_row(file_path, "Complete thesis data (YAML)")
        elif "semconv" in file_path:
            table.add_row(file_path, "OTEL semantic conventions")
        elif "spans.rs" in file_path:
            table.add_row(file_path, "Rust span implementation")
    
    console.print(table)
    
    # Show thesis summary
    console.print(f"\n📊 [bold]Thesis Summary:[/bold]")
    console.print(f"   • Span claims: {len(thesis.span_claims)}")
    console.print(f"   • Belief inversions: {len(thesis.inversion_matrix)}")
    console.print(f"   • TRIZ mappings: {len(thesis.triz_mapping)}")
    console.print(f"   • Feedback loop phases: {len(thesis.auto_triz_feedback_loop)}")


@app.command("demo")
def demo_feedback_loop(
    iterations: int = typer.Option(3, "--iterations", "-i", help="Number of feedback loop iterations"),
    model: str = typer.Option("ollama/qwen2.5", "--model", "-m", help="LLM model to use")
):
    """Demonstrate the auto-TRIZ feedback loop"""
    
    console.print("🔄 [bold blue]SwarmSH Auto-TRIZ Feedback Loop Demo[/bold blue]")
    
    # Initialize LLM
    init_lm(model=model)
    
    try:
        from dslmodel.thesis.otel_loop import demo_otel_loop
        demo_otel_loop()
    except Exception as e:
        console.print(f"❌ [red]Demo failed: {e}[/red]")
        console.print("Running simplified demonstration...")
        
        # Simplified demo
        for i in range(iterations):
            console.print(f"\n🔄 [yellow]Iteration {i+1}/{iterations}[/yellow]")
            console.print("📡 PERCEPTION: Collecting telemetry...")
            console.print("🔍 ANALYZING: Detecting contradictions...")
            console.print("🤖 RESOLUTION: LLM analyzing with TRIZ...")
            console.print("⚙️  GENERATION: Updating semantic conventions...")
            console.print("🚀 DEPLOYMENT: Code generation via WeaverForge...")
            console.print("✓ VALIDATION: Checking effectiveness...")


@app.command("validate")
def validate_thesis(
    thesis_file: Path = typer.Argument(..., help="Path to thesis JSON/YAML file")
):
    """Validate thesis file structure and content"""
    
    console.print(f"🔍 [bold blue]Validating thesis file:[/bold blue] {thesis_file}")
    
    if not thesis_file.exists():
        console.print(f"❌ [red]File not found: {thesis_file}[/red]")
        raise typer.Exit(1)
    
    try:
        if thesis_file.suffix.lower() == '.json':
            thesis = ThesisComplete.from_json(file_path=str(thesis_file))
        elif thesis_file.suffix.lower() in ['.yaml', '.yml']:
            # Would need YAML loading implementation
            console.print("❌ [red]YAML validation not yet implemented[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"❌ [red]Unsupported file format: {thesis_file.suffix}[/red]")
            raise typer.Exit(1)
        
        # Validation checks
        errors = []
        
        if len(thesis.span_claims) < 5:
            errors.append(f"Expected at least 5 span claims, got {len(thesis.span_claims)}")
        
        if len(thesis.inversion_matrix) < 5:
            errors.append(f"Expected at least 5 inversions, got {len(thesis.inversion_matrix)}")
        
        if len(thesis.triz_mapping) < 10:
            errors.append(f"Expected at least 10 TRIZ mappings, got {len(thesis.triz_mapping)}")
        
        if len(thesis.auto_triz_feedback_loop) != 5:
            errors.append(f"Expected exactly 5 feedback phases, got {len(thesis.auto_triz_feedback_loop)}")
        
        if errors:
            console.print("❌ [red]Validation failed:[/red]")
            for error in errors:
                console.print(f"   • {error}")
            raise typer.Exit(1)
        else:
            console.print("✅ [green]Thesis validation passed![/green]")
            
            table = Table(title="Thesis Content")
            table.add_column("Component", style="cyan")
            table.add_column("Count", style="magenta")
            
            table.add_row("Span Claims", str(len(thesis.span_claims)))
            table.add_row("Belief Inversions", str(len(thesis.inversion_matrix)))
            table.add_row("TRIZ Mappings", str(len(thesis.triz_mapping)))
            table.add_row("Feedback Phases", str(len(thesis.auto_triz_feedback_loop)))
            
            console.print(table)
    
    except Exception as e:
        console.print(f"❌ [red]Validation error: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def thesis_status():
    """Show thesis implementation status"""
    
    console.print("📊 [bold blue]SwarmSH Thesis Implementation Status[/bold blue]")
    
    # Check components
    status_table = Table(title="Component Status")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Status", style="magenta")
    status_table.add_column("Description", style="white")
    
    try:
        from dslmodel.thesis import ThesisComplete
        status_table.add_row("Core Thesis", "✅ Available", "ThesisComplete model")
    except ImportError:
        status_table.add_row("Core Thesis", "❌ Missing", "Import failed")
    
    try:
        from dslmodel.thesis.otel_loop import OTELFeedbackLoop
        status_table.add_row("Feedback Loop", "✅ Available", "Auto-TRIZ implementation")
    except ImportError:
        status_table.add_row("Feedback Loop", "❌ Missing", "Import failed")
    
    try:
        from dslmodel.thesis.weaver_templates import WeaverTemplateManager
        status_table.add_row("Code Generation", "✅ Available", "WeaverForge templates")
    except ImportError:
        status_table.add_row("Code Generation", "❌ Missing", "Import failed")
    
    # Check LLM availability
    try:
        from dslmodel.utils.dspy_tools import init_lm
        status_table.add_row("LLM Integration", "✅ Available", "DSPy integration")
    except ImportError:
        status_table.add_row("LLM Integration", "❌ Missing", "DSPy not available")
    
    console.print(status_table)
    
    console.print("\n🎯 [bold]Key Capabilities:[/bold]")
    console.print("   • Telemetry-as-System paradigm")
    console.print("   • Auto-TRIZ contradiction resolution")
    console.print("   • OTEL semantic convention generation")
    console.print("   • Code generation via WeaverForge")
    console.print("   • Self-evolving system architecture")


if __name__ == "__main__":
    app()