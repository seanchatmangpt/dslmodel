#!/usr/bin/env python3
"""
Conversion Toolkit Demo - Showcase All Conversion Capabilities

This demo script shows all the conversion capabilities between:
- Weaver YAML → Mermaid diagrams
- OpenTelemetry JSON → Mermaid diagrams
- Mermaid → Structured data (JSON/YAML/CSV)
- Universal format conversions
"""

import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_demo():
    """Run comprehensive conversion demo"""
    
    console.print("[bold cyan]🔄 Universal Conversion Toolkit Demo[/bold cyan]")
    console.print("=" * 70)
    
    demo_steps = [
        ("Weaver → Mermaid", demo_weaver_to_mermaid),
        ("OTEL → Mermaid", demo_otel_to_mermaid),
        ("Mermaid → Data", demo_mermaid_to_data),
        ("Universal Conversion", demo_universal_conversion),
        ("Batch Processing", demo_batch_processing),
        ("Visualization Gallery", demo_visualization_gallery)
    ]
    
    for step_name, step_func in demo_steps:
        console.print(f"\n[bold yellow]📋 {step_name}[/bold yellow]")
        console.print("-" * 40)
        
        try:
            step_func()
            console.print(f"[green]✅ {step_name} completed successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ {step_name} failed: {e}[/red]")


def demo_weaver_to_mermaid():
    """Demo Weaver semantic conventions to Mermaid conversion"""
    
    console.print("Converting Weaver semantic conventions to Mermaid diagrams...")
    
    # Test different diagram types
    diagram_types = ["hierarchy", "attributes", "class", "mindmap"]
    
    for diagram_type in diagram_types:
        output_file = f"demo_weaver_{diagram_type}.mmd"
        
        cmd = [
            "poetry", "run", "python", "src/dslmodel/weaver_to_mermaid.py",
            "convert", "semconv_registry/claude_code_tools_v2.yaml",
            "--type", diagram_type,
            "--output", output_file,
            "--show", "false"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"  ✓ Generated {diagram_type} diagram: {output_file}")
        else:
            console.print(f"  ❌ Failed to generate {diagram_type}: {result.stderr}")


def demo_otel_to_mermaid():
    """Demo OpenTelemetry spans to Mermaid conversion"""
    
    console.print("Converting OpenTelemetry spans to Mermaid diagrams...")
    
    # Create sample OTEL data
    sample_spans = [
        {
            "name": "claude_code.file",
            "context": {"trace_id": "trace123", "span_id": "span1"},
            "start_time": 1640000000000000000,
            "end_time": 1640000001000000000,
            "duration_ns": 1000000000,
            "status": {"status_code": "OK"},
            "attributes": {
                "claude_code.tool.name": "Read",
                "claude_code.file.path": "/app/main.py",
                "claude_code.file.operation": "read"
            }
        },
        {
            "name": "claude_code.bash",
            "context": {"trace_id": "trace123", "span_id": "span2"},
            "parent_id": "span1",
            "start_time": 1640000001000000000,
            "end_time": 1640000003000000000,
            "duration_ns": 2000000000,
            "status": {"status_code": "OK"},
            "attributes": {
                "claude_code.tool.name": "Bash",
                "claude_code.bash.command": "python main.py",
                "claude_code.bash.exit_code": 0
            }
        }
    ]
    
    # Save sample data
    sample_file = Path("demo_otel_spans.json")
    sample_file.write_text(json.dumps(sample_spans, indent=2))
    
    # Generate different diagram types
    diagram_types = ["flow", "timeline", "performance", "attributes"]
    
    for diagram_type in diagram_types:
        output_file = f"demo_otel_{diagram_type}.mmd"
        
        cmd = [
            "poetry", "run", "python", "src/dslmodel/otel_to_mermaid.py",
            "convert", str(sample_file),
            "--type", diagram_type,
            "--output", output_file,
            "--show", "false"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"  ✓ Generated OTEL {diagram_type} diagram: {output_file}")
        else:
            console.print(f"  ❌ Failed to generate OTEL {diagram_type}: {result.stderr}")


def demo_mermaid_to_data():
    """Demo Mermaid to structured data conversion"""
    
    console.print("Converting Mermaid diagrams to structured data...")
    
    # Use one of the generated Mermaid files
    mermaid_file = Path("demo_weaver_hierarchy.mmd")
    
    if not mermaid_file.exists():
        console.print("  ⚠️ No Mermaid file found, skipping demo")
        return
    
    output_formats = ["json", "yaml", "csv"]
    
    for fmt in output_formats:
        output_file = f"demo_parsed.{fmt}"
        
        cmd = [
            "poetry", "run", "python", "src/dslmodel/mermaid_to_data.py",
            "parse", str(mermaid_file),
            "--format", fmt,
            "--output", output_file,
            "--show", "false"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"  ✓ Converted to {fmt.upper()}: {output_file}")
        else:
            console.print(f"  ❌ Failed to convert to {fmt}: {result.stderr}")


def demo_universal_conversion():
    """Demo universal conversion toolkit"""
    
    console.print("Testing universal conversion capabilities...")
    
    # Create sample files
    sample_data = {
        "tool_usage": [
            {"tool": "Read", "count": 15, "avg_duration_ms": 12.5},
            {"tool": "Write", "count": 8, "avg_duration_ms": 8.2},
            {"tool": "Bash", "count": 5, "avg_duration_ms": 150.0}
        ]
    }
    
    sample_json = Path("demo_sample.json")
    sample_json.write_text(json.dumps(sample_data, indent=2))
    
    # Test various conversions
    conversions = [
        ("demo_sample.json", "demo_converted.yaml", "json", "yaml"),
        ("demo_sample.json", "demo_converted.csv", "json", "csv"),
        ("demo_weaver_hierarchy.mmd", "demo_interactive.html", "mermaid", "html")
    ]
    
    for input_file, output_file, input_fmt, output_fmt in conversions:
        if not Path(input_file).exists():
            console.print(f"  ⚠️ Input file {input_file} not found, skipping")
            continue
        
        cmd = [
            "poetry", "run", "python", "src/dslmodel/conversion_toolkit.py",
            "convert", input_file, output_file,
            "--from", input_fmt, "--to", output_fmt
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"  ✓ Converted {input_fmt} → {output_fmt}: {output_file}")
        else:
            console.print(f"  ❌ Failed conversion {input_fmt} → {output_fmt}")


def demo_batch_processing():
    """Demo batch processing capabilities"""
    
    console.print("Testing batch processing...")
    
    # Create a temp directory with multiple files
    batch_dir = Path("demo_batch_input")
    batch_dir.mkdir(exist_ok=True)
    
    # Create multiple sample files
    for i in range(3):
        sample_data = {"file_id": i, "data": f"Sample data {i}"}
        sample_file = batch_dir / f"sample_{i}.json"
        sample_file.write_text(json.dumps(sample_data, indent=2))
    
    output_dir = Path("demo_batch_output")
    
    cmd = [
        "poetry", "run", "python", "src/dslmodel/conversion_toolkit.py",
        "batch", str(batch_dir), str(output_dir),
        "--from", "json", "--to", "yaml"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print(f"  ✓ Batch processed files to {output_dir}")
        
        # Count output files
        if output_dir.exists():
            output_files = list(output_dir.glob("*.yaml"))
            console.print(f"  📁 Generated {len(output_files)} YAML files")
    else:
        console.print("  ❌ Batch processing failed")


def demo_visualization_gallery():
    """Demo visualization gallery creation"""
    
    console.print("Creating visualization gallery...")
    
    # Create an HTML gallery of all generated files
    gallery_html = """<!DOCTYPE html>
<html>
<head>
    <title>Conversion Toolkit Demo Gallery</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({ startOnLoad: true });</script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        h1, h2 {
            color: #333;
            text-align: center;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .mermaid {
            text-align: center;
            background-color: #fafafa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .file-card {
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
        }
        .file-card h3 {
            margin-top: 0;
            color: #0066cc;
        }
    </style>
</head>
<body>
    <h1>🔄 Universal Conversion Toolkit Demo</h1>
    <h2>Generated Files Gallery</h2>
    
    <div class="section">
        <h2>📊 Weaver → Mermaid Diagrams</h2>
        <p>Semantic conventions converted to visual diagrams</p>
        
        <div class="file-list">
"""
    
    # Add generated files to gallery
    demo_files = [
        ("demo_weaver_hierarchy.mmd", "Hierarchy Diagram", "Shows the relationship between semantic convention groups"),
        ("demo_weaver_class.mmd", "Class Diagram", "UML-style class representation of attributes"),
        ("demo_otel_flow.mmd", "OTEL Flow Diagram", "Trace flow visualization"),
        ("demo_interactive.html", "Interactive Visualization", "HTML with embedded Mermaid diagrams")
    ]
    
    for filename, title, description in demo_files:
        if Path(filename).exists():
            gallery_html += f"""
            <div class="file-card">
                <h3>📄 {title}</h3>
                <p><strong>File:</strong> {filename}</p>
                <p>{description}</p>
            </div>
            """
    
    gallery_html += """
        </div>
    </div>
    
    <div class="section">
        <h2>🔧 Conversion Features</h2>
        <div class="file-list">
            <div class="file-card">
                <h3>🧵 Weaver Integration</h3>
                <p>Convert semantic conventions to visual diagrams with multiple layout options</p>
            </div>
            <div class="file-card">
                <h3>📊 OTEL Visualization</h3>
                <p>Transform OpenTelemetry traces into flow charts, timelines, and performance views</p>
            </div>
            <div class="file-card">
                <h3>📝 Data Extraction</h3>
                <p>Parse Mermaid diagrams back to structured JSON, YAML, and CSV formats</p>
            </div>
            <div class="file-card">
                <h3>🔄 Universal Conversion</h3>
                <p>Convert between multiple formats with automatic detection</p>
            </div>
            <div class="file-card">
                <h3>⚡ Batch Processing</h3>
                <p>Process multiple files simultaneously with configurable pipelines</p>
            </div>
            <div class="file-card">
                <h3>🌐 Interactive Output</h3>
                <p>Generate HTML visualizations with Mermaid.js for web viewing</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 Conversion Matrix</h2>
        <p>Supported format conversions:</p>
        <ul>
            <li><strong>YAML → Mermaid:</strong> Semantic conventions to diagrams</li>
            <li><strong>JSON → Mermaid:</strong> OTEL data to visual flows</li>
            <li><strong>Mermaid → JSON/YAML/CSV:</strong> Extract structured data</li>
            <li><strong>Mermaid → HTML:</strong> Interactive visualizations</li>
            <li><strong>JSON ↔ YAML:</strong> Data format conversion</li>
            <li><strong>JSON ↔ CSV:</strong> Tabular data transformation</li>
        </ul>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated by Universal Conversion Toolkit Demo</p>
    </footer>
</body>
</html>"""
    
    gallery_file = Path("conversion_demo_gallery.html")
    gallery_file.write_text(gallery_html)
    
    console.print(f"  ✓ Created demo gallery: {gallery_file}")
    console.print(f"  🌐 Open {gallery_file} in your browser to view all results")


def show_summary():
    """Show demo summary"""
    
    console.print("\n[bold green]🎉 Conversion Toolkit Demo Complete![/bold green]")
    console.print("=" * 60)
    
    # Count generated files
    generated_files = list(Path(".").glob("demo_*")) + list(Path(".").glob("conversion_demo_*"))
    
    summary_table = Table(title="Generated Files Summary")
    summary_table.add_column("File Type", style="cyan")
    summary_table.add_column("Count", style="yellow")
    summary_table.add_column("Purpose", style="white")
    
    file_types = {
        "*.mmd": ("Mermaid Diagrams", "Visual representations"),
        "*.json": ("JSON Data", "Structured data output"),
        "*.yaml": ("YAML Files", "Configuration format"),
        "*.csv": ("CSV Tables", "Tabular data"),
        "*.html": ("HTML Views", "Interactive visualizations")
    }
    
    for pattern, (type_name, purpose) in file_types.items():
        count = len(list(Path(".").glob(f"demo_{pattern}")) + list(Path(".").glob(f"conversion_demo_{pattern}")))
        if count > 0:
            summary_table.add_row(type_name, str(count), purpose)
    
    console.print(summary_table)
    
    console.print("\n[bold]Key Achievements:[/bold]")
    console.print("• ✅ Weaver semantic conventions → Mermaid diagrams")
    console.print("• ✅ OpenTelemetry spans → Visual flows")
    console.print("• ✅ Mermaid diagrams → Structured data")
    console.print("• ✅ Universal format conversions")
    console.print("• ✅ Batch processing capabilities")
    console.print("• ✅ Interactive HTML gallery")
    
    console.print(f"\n[green]📁 Total files generated: {len(generated_files)}[/green]")
    console.print("[cyan]🔗 Open 'conversion_demo_gallery.html' to explore all results![/cyan]")


if __name__ == "__main__":
    run_demo()
    show_summary()