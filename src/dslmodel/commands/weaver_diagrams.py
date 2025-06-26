#!/usr/bin/env python3
"""
Weaver Architecture Diagrams CLI
===============================

Command-line interface to view Mermaid diagrams of all Weaver aspects
in the Claude Code (DSLModel) system.

Usage: dsl weaver-diagrams <diagram_type>
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

app = typer.Typer(help="View Weaver architecture diagrams")
console = Console()


def get_diagram_files() -> dict:
    """Get available diagram files and their descriptions"""
    base_path = Path(__file__).parent.parent.parent.parent
    
    return {
        "architecture": {
            "file": base_path / "weaver_architecture_diagrams.md",
            "description": "Core Weaver architecture and workflow diagrams",
            "diagrams": [
                "1. Weaver Architecture Overview",
                "2. Weaver Forge Workflow", 
                "3. Semantic Convention Flow",
                "4. Weaver-OTEL Integration",
                "5. Weaver Validation Pipeline",
                "6. Weaver Health Check System",
                "7. Weaver Template System",
                "8. Weaver E2E Feature Generation",
                "9. Weaver-FSM Integration",
                "10. Weaver Development Workflow"
            ]
        },
        "advanced": {
            "file": base_path / "weaver_advanced_diagrams.md",
            "description": "Advanced Weaver patterns and system interactions",
            "diagrams": [
                "11. Weaver Convention Registry Structure",
                "12. Weaver-Driven Development Lifecycle",
                "13. Weaver Multi-Language Support",
                "14. Weaver Convention Inheritance",
                "15. Weaver Error Handling and Recovery",
                "16. Weaver Performance Optimization",
                "17. Weaver Security Model",
                "18. Weaver Plugin Architecture",
                "19. Weaver Telemetry Collection",
                "20. Weaver Convention Evolution"
            ]
        },
        "integration": {
            "file": base_path / "claude_code_weaver_integration.md",
            "description": "Complete Claude Code + Weaver integration overview",
            "diagrams": [
                "Claude Code Weaver Ecosystem Overview",
                "Claude Code Telemetry-First Development Flow",
                "Claude Code Convention Categories",
                "Claude Code Weaver Command Matrix",
                "Claude Code Observability Stack",
                "Claude Code Feature Generation Workflow",
                "Claude Code Evolution System with Weaver",
                "Claude Code Quality Assurance with Weaver"
            ]
        }
    }


@app.command("list")
def list_diagrams():
    """List all available Weaver diagram categories"""
    
    console.print("🧵 Weaver Architecture Diagrams")
    console.print("=" * 35)
    
    diagrams = get_diagram_files()
    
    for category, info in diagrams.items():
        console.print(Panel(
            f"📂 **File**: {info['file'].name}\n"
            f"📝 **Description**: {info['description']}\n"
            f"📊 **Diagrams**: {len(info['diagrams'])} diagrams\n\n"
            f"**Contents**:\n" + 
            "\n".join([f"  • {diagram}" for diagram in info['diagrams']]),
            title=f"🔧 {category.title()} Diagrams",
            border_style="cyan"
        ))
        console.print()


@app.command("show")
def show_diagram(
    category: str = typer.Argument(..., help="Diagram category: architecture, advanced, integration"),
    diagram: Optional[int] = typer.Option(None, help="Specific diagram number to show"),
    format: str = typer.Option("info", help="Output format: info, mermaid, file")
):
    """Show specific Weaver diagram(s)"""
    
    diagrams = get_diagram_files()
    
    if category not in diagrams:
        console.print(f"❌ Unknown category: {category}")
        console.print(f"Available categories: {', '.join(diagrams.keys())}")
        raise typer.Exit(1)
    
    diagram_info = diagrams[category]
    
    if not diagram_info["file"].exists():
        console.print(f"❌ Diagram file not found: {diagram_info['file']}")
        raise typer.Exit(1)
    
    if format == "file":
        console.print(f"📂 File location: {diagram_info['file']}")
        return
    
    content = diagram_info["file"].read_text()
    
    if format == "mermaid":
        # Extract Mermaid code blocks
        lines = content.split('\n')
        in_mermaid = False
        mermaid_blocks = []
        current_block = []
        block_title = ""
        
        for line in lines:
            if line.startswith('```mermaid'):
                in_mermaid = True
                current_block = []
            elif line.startswith('```') and in_mermaid:
                in_mermaid = False
                if current_block:
                    mermaid_blocks.append((block_title, '\n'.join(current_block)))
                current_block = []
            elif in_mermaid:
                current_block.append(line)
            elif line.startswith('## ') and not in_mermaid:
                block_title = line[3:]  # Remove "## "
        
        if diagram:
            if 1 <= diagram <= len(mermaid_blocks):
                title, code = mermaid_blocks[diagram - 1]
                console.print(Panel(
                    Syntax(code, "mermaid", theme="monokai"),
                    title=f"🧵 {title}",
                    border_style="blue"
                ))
            else:
                console.print(f"❌ Diagram {diagram} not found. Available: 1-{len(mermaid_blocks)}")
        else:
            for i, (title, code) in enumerate(mermaid_blocks, 1):
                console.print(Panel(
                    Syntax(code, "mermaid", theme="monokai"),
                    title=f"🧵 {i}. {title}",
                    border_style="blue"
                ))
                console.print()
    
    else:  # format == "info"
        console.print(f"🧵 {category.title()} Weaver Diagrams")
        console.print("=" * 40)
        console.print(f"📂 File: {diagram_info['file'].name}")
        console.print(f"📝 Description: {diagram_info['description']}")
        console.print()
        
        console.print("📊 Available Diagrams:")
        for i, diag in enumerate(diagram_info['diagrams'], 1):
            console.print(f"  {i:2d}. {diag}")
        
        console.print()
        console.print("💡 Usage:")
        console.print(f"  • View all: dsl weaver-diagrams show {category}")
        console.print(f"  • View specific: dsl weaver-diagrams show {category} --diagram 1")
        console.print(f"  • Get Mermaid code: dsl weaver-diagrams show {category} --format mermaid")
        console.print(f"  • Get file path: dsl weaver-diagrams show {category} --format file")


@app.command("overview")
def show_overview():
    """Show comprehensive overview of all Weaver diagrams"""
    
    console.print("🧵 Complete Weaver Architecture Visualization")
    console.print("=" * 50)
    
    console.print(Panel(
        "🎯 **Weaver in Claude Code**:\n\n"
        "Weaver implements the 'Define Once, Generate Everything' philosophy\n"
        "for telemetry-first development in Claude Code (DSLModel).\n\n"
        "**Architecture Overview**:\n"
        "• Semantic conventions drive all code generation\n"
        "• OTEL integration is automatic and type-safe\n"
        "• Multi-language support from single definitions\n"
        "• Comprehensive validation and health checking\n"
        "• Evolution-ready with automatic propagation\n\n"
        "**Generated Artifacts**:\n"
        "• Pydantic models with full type safety\n"
        "• CLI commands with automatic help\n"
        "• Test suites with coverage validation\n"
        "• Documentation with live examples\n"
        "• OTEL instrumentation with semantic conventions",
        title="🧬 Weaver Integration Overview",
        border_style="blue"
    ))
    
    # Summary table
    diagrams = get_diagram_files()
    table = Table(title="📊 Diagram Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Diagrams", style="yellow")
    table.add_column("Focus Area", style="green")
    
    focus_areas = {
        "architecture": "Core architecture and workflows",
        "advanced": "Advanced patterns and optimizations", 
        "integration": "Claude Code specific integration"
    }
    
    for category, info in diagrams.items():
        table.add_row(
            category.title(),
            str(len(info['diagrams'])),
            focus_areas[category]
        )
    
    console.print(table)
    
    console.print()
    console.print("🚀 Quick Start:")
    console.print("  • dsl weaver-diagrams list                     # List all categories")
    console.print("  • dsl weaver-diagrams show architecture        # Core diagrams")
    console.print("  • dsl weaver-diagrams show integration         # Claude Code integration")
    console.print("  • dsl weaver-diagrams show advanced --diagram 1 # Specific diagram")


@app.command("export")
def export_diagrams(
    output_dir: Path = typer.Option(Path("weaver_diagrams"), help="Output directory"),
    format: str = typer.Option("markdown", help="Export format: markdown, mermaid, html")
):
    """Export all Weaver diagrams to specified directory"""
    
    output_dir.mkdir(exist_ok=True)
    diagrams = get_diagram_files()
    
    console.print(f"📤 Exporting Weaver diagrams to {output_dir}...")
    
    exported_files = []
    
    for category, info in diagrams.items():
        if not info["file"].exists():
            console.print(f"⚠️ Skipping {category}: file not found")
            continue
        
        if format == "markdown":
            # Copy markdown files directly
            output_file = output_dir / f"weaver_{category}_diagrams.md"
            output_file.write_text(info["file"].read_text())
            exported_files.append(output_file)
        
        elif format == "mermaid":
            # Extract just Mermaid code blocks
            content = info["file"].read_text()
            lines = content.split('\n')
            mermaid_content = []
            in_mermaid = False
            
            for line in lines:
                if line.startswith('```mermaid'):
                    in_mermaid = True
                    mermaid_content.append(line)
                elif line.startswith('```') and in_mermaid:
                    in_mermaid = False
                    mermaid_content.append(line)
                    mermaid_content.append('')  # Add spacing
                elif in_mermaid:
                    mermaid_content.append(line)
                elif line.startswith('##') and not in_mermaid:
                    mermaid_content.append('')
                    mermaid_content.append(f"// {line}")
                    mermaid_content.append('')
            
            output_file = output_dir / f"weaver_{category}_diagrams.mmd"
            output_file.write_text('\n'.join(mermaid_content))
            exported_files.append(output_file)
        
        elif format == "html":
            # Create HTML with embedded Mermaid
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Weaver {category.title()} Diagrams</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; }}
        .diagram {{ margin: 2rem 0; padding: 1rem; border: 1px solid #ddd; border-radius: 8px; }}
        h1, h2 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>🧵 Weaver {category.title()} Diagrams</h1>
    <p>{info['description']}</p>
"""
            
            # Extract and embed Mermaid diagrams
            content = info["file"].read_text()
            lines = content.split('\n')
            in_mermaid = False
            current_block = []
            block_title = ""
            
            for line in lines:
                if line.startswith('```mermaid'):
                    in_mermaid = True
                    current_block = []
                elif line.startswith('```') and in_mermaid:
                    in_mermaid = False
                    if current_block:
                        html_content += f"""
    <div class="diagram">
        <h2>{block_title}</h2>
        <div class="mermaid">
{chr(10).join(current_block)}
        </div>
    </div>
"""
                    current_block = []
                elif in_mermaid:
                    current_block.append(line)
                elif line.startswith('## ') and not in_mermaid:
                    block_title = line[3:]
            
            html_content += """
</body>
</html>"""
            
            output_file = output_dir / f"weaver_{category}_diagrams.html"
            output_file.write_text(html_content)
            exported_files.append(output_file)
    
    console.print(f"✅ Exported {len(exported_files)} files:")
    for file in exported_files:
        console.print(f"  📄 {file}")
    
    console.print()
    console.print("💡 To view HTML files, open them in a web browser")
    console.print("💡 To render Mermaid files, use: https://mermaid.live/")


if __name__ == "__main__":
    app()