#!/usr/bin/env python3
"""
Universal Conversion Toolkit - Convert Between Multiple Formats

This comprehensive toolkit converts between:
- Weaver YAML ↔ Mermaid diagrams
- OpenTelemetry JSON ↔ Mermaid diagrams  
- Mermaid ↔ Structured data (JSON/YAML/CSV)
- Telemetry data ↔ Visual flows
- Architecture diagrams ↔ Documentation
"""

import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our converters
from .weaver_to_mermaid import WeaverToMermaidConverter
from .otel_to_mermaid import OTELToMermaidConverter
from .mermaid_to_data import MermaidParser

app = typer.Typer()
console = Console()


class UniversalConverter:
    """Universal converter supporting multiple format conversions"""
    
    def __init__(self):
        self.supported_formats = {
            'input': ['yaml', 'json', 'mmd', 'mermaid', 'csv', 'md'],
            'output': ['yaml', 'json', 'mmd', 'mermaid', 'csv', 'html', 'md', 'svg', 'png']
        }
        
        self.conversion_matrix = {
            ('yaml', 'mermaid'): self._weaver_to_mermaid,
            ('json', 'mermaid'): self._otel_to_mermaid,
            ('mermaid', 'json'): self._mermaid_to_json,
            ('mermaid', 'yaml'): self._mermaid_to_yaml,
            ('mermaid', 'csv'): self._mermaid_to_csv,
            ('mermaid', 'html'): self._mermaid_to_html,
            ('json', 'yaml'): self._json_to_yaml,
            ('yaml', 'json'): self._yaml_to_json,
            ('csv', 'json'): self._csv_to_json,
            ('json', 'csv'): self._json_to_csv,
        }
    
    def detect_format(self, file_path: Path) -> str:
        """Auto-detect file format"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.yaml', '.yml']:
            return 'yaml'
        elif suffix == '.json':
            return 'json'
        elif suffix in ['.mmd', '.mermaid']:
            return 'mermaid'
        elif suffix == '.csv':
            return 'csv'
        elif suffix == '.html':
            return 'html'
        elif suffix == '.md':
            # Could be markdown with mermaid or other
            content = file_path.read_text()
            if '```mermaid' in content:
                return 'mermaid'
            return 'md'
        else:
            # Try to detect from content
            try:
                content = file_path.read_text()
                if content.strip().startswith('{'):
                    return 'json'
                elif content.strip().startswith('---') or 'groups:' in content:
                    return 'yaml'
                elif any(keyword in content for keyword in ['graph', 'flowchart', 'sequenceDiagram']):
                    return 'mermaid'
                else:
                    return 'unknown'
            except:
                return 'unknown'
    
    def convert(self, input_file: Path, output_file: Path, 
                input_format: Optional[str] = None, 
                output_format: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None) -> bool:
        """Universal conversion between formats"""
        
        # Auto-detect formats if not specified
        if not input_format:
            input_format = self.detect_format(input_file)
        if not output_format:
            output_format = self.detect_format(output_file) if output_file.suffix else 'json'
        
        if input_format == 'unknown':
            console.print(f"[red]Could not detect format for {input_file}[/red]")
            return False
        
        # Find conversion function
        conversion_key = (input_format, output_format)
        if conversion_key not in self.conversion_matrix:
            console.print(f"[red]No conversion available from {input_format} to {output_format}[/red]")
            return False
        
        try:
            converter_func = self.conversion_matrix[conversion_key]
            result = converter_func(input_file, output_file, options or {})
            
            if result:
                console.print(f"[green]✓ Converted {input_format} → {output_format}[/green]")
                return True
            else:
                console.print(f"[red]✗ Conversion failed[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Conversion error: {e}[/red]")
            return False
    
    def _weaver_to_mermaid(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert Weaver YAML to Mermaid"""
        converter = WeaverToMermaidConverter()
        converter.load_yaml(str(input_file))
        
        diagram_type = options.get('diagram_type', 'hierarchy')
        
        if diagram_type == 'hierarchy':
            mermaid_content = converter.generate_hierarchy_diagram()
        elif diagram_type == 'attributes':
            mermaid_content = converter.generate_attribute_diagram()
        elif diagram_type == 'class':
            mermaid_content = converter.generate_class_diagram()
        elif diagram_type == 'mindmap':
            mermaid_content = converter.generate_mindmap()
        else:
            mermaid_content = converter.generate_hierarchy_diagram()
        
        output_file.write_text(mermaid_content)
        return True
    
    def _otel_to_mermaid(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert OTEL JSON to Mermaid"""
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Handle different formats
        if isinstance(data, dict) and 'spans' in data:
            spans = data['spans']
        elif isinstance(data, list):
            spans = data
        else:
            return False
        
        converter = OTELToMermaidConverter()
        converter.load_spans(spans)
        
        diagram_type = options.get('diagram_type', 'flow')
        trace_id = options.get('trace_id')
        
        if diagram_type == 'flow':
            mermaid_content = converter.generate_trace_flow(trace_id)
        elif diagram_type == 'timeline':
            mermaid_content = converter.generate_trace_timeline(trace_id)
        elif diagram_type == 'attributes':
            mermaid_content = converter.generate_attribute_flow()
        elif diagram_type == 'errors':
            mermaid_content = converter.generate_error_analysis()
        elif diagram_type == 'performance':
            mermaid_content = converter.generate_performance_summary()
        else:
            mermaid_content = converter.generate_trace_flow(trace_id)
        
        output_file.write_text(mermaid_content)
        return True
    
    def _mermaid_to_json(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert Mermaid to JSON"""
        content = input_file.read_text()
        parser = MermaidParser()
        parsed_data = parser.parse_diagram(content)
        
        if "error" in parsed_data:
            return False
        
        output_file.write_text(json.dumps(parsed_data, indent=2))
        return True
    
    def _mermaid_to_yaml(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert Mermaid to YAML"""
        content = input_file.read_text()
        parser = MermaidParser()
        parsed_data = parser.parse_diagram(content)
        
        if "error" in parsed_data:
            return False
        
        output_file.write_text(yaml.dump(parsed_data, default_flow_style=False))
        return True
    
    def _mermaid_to_csv(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert Mermaid to CSV"""
        content = input_file.read_text()
        parser = MermaidParser()
        parsed_data = parser.parse_diagram(content)
        
        if "error" in parsed_data:
            return False
        
        # Convert based on diagram type
        if parser.diagram_type in ["graph", "flowchart"]:
            csv_content = self._graph_to_csv(parsed_data)
        elif parser.diagram_type == "sequence":
            csv_content = self._sequence_to_csv(parsed_data)
        else:
            # Fallback to JSON-like CSV
            csv_content = self._generic_to_csv(parsed_data)
        
        output_file.write_text(csv_content)
        return True
    
    def _mermaid_to_html(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert Mermaid to interactive HTML"""
        content = input_file.read_text()
        title = options.get('title', input_file.stem)
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad: true }});</script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .mermaid {{
            text-align: center;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .source {{
            margin-top: 20px;
            padding: 10px;
            background-color: #e0e0e0;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="mermaid">
{content}
    </div>
    <div class="source">
        <h3>Source:</h3>
        <pre>{content}</pre>
    </div>
</body>
</html>"""
        
        output_file.write_text(html_template)
        return True
    
    def _json_to_yaml(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert JSON to YAML"""
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        output_file.write_text(yaml.dump(data, default_flow_style=False))
        return True
    
    def _yaml_to_json(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert YAML to JSON"""
        with open(input_file, 'r') as f:
            data = yaml.safe_load(f)
        
        indent = options.get('indent', 2)
        output_file.write_text(json.dumps(data, indent=indent))
        return True
    
    def _csv_to_json(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert CSV to JSON"""
        data = []
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        output_file.write_text(json.dumps(data, indent=2))
        return True
    
    def _json_to_csv(self, input_file: Path, output_file: Path, options: Dict[str, Any]) -> bool:
        """Convert JSON to CSV"""
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False
        
        if not data:
            return False
        
        # Get all keys from all objects
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(all_keys))
            writer.writeheader()
            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item)
        
        return True
    
    def _graph_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert graph data to CSV"""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Nodes
        writer.writerow(["Type", "ID", "Label", "Shape", "Subgraph"])
        for node_id, node_data in data.get("nodes", {}).items():
            subgraph = ""
            for sg_id, sg_data in data.get("subgraphs", {}).items():
                if node_id in sg_data.get("nodes", []):
                    subgraph = sg_id
                    break
            
            writer.writerow([
                "Node", node_id, node_data.get("label", ""),
                node_data.get("shape", ""), subgraph
            ])
        
        # Edges
        for edge in data.get("edges", []):
            writer.writerow([
                "Edge", f"{edge['source']}->{edge['target']}",
                edge.get("label", ""), edge.get("type", ""), ""
            ])
        
        return output.getvalue()
    
    def _sequence_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert sequence data to CSV"""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Type", "Source", "Target", "Message", "MessageType"])
        for message in data.get("messages", []):
            writer.writerow([
                "Message", message.get("source", ""), message.get("target", ""),
                message.get("message", ""), message.get("type", "")
            ])
        
        return output.getvalue()
    
    def _generic_to_csv(self, data: Dict[str, Any]) -> str:
        """Generic conversion to CSV for any data structure"""
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Flatten the data structure
        def flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                        else:
                            items.append((f"{new_key}[{i}]", item))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        flattened = flatten_dict(data)
        writer.writerow(["Key", "Value"])
        for key, value in flattened.items():
            writer.writerow([key, str(value)])
        
        return output.getvalue()


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input file to convert"),
    output_file: Path = typer.Argument(..., help="Output file path"),
    input_format: Optional[str] = typer.Option(None, "--from", "-f", help="Input format (auto-detect if not specified)"),
    output_format: Optional[str] = typer.Option(None, "--to", "-t", help="Output format (auto-detect if not specified)"),
    diagram_type: str = typer.Option("hierarchy", "--diagram", "-d", help="Diagram type for Mermaid generation"),
    title: str = typer.Option("", "--title", help="Title for HTML output"),
    trace_id: Optional[str] = typer.Option(None, "--trace", help="Specific trace ID for OTEL diagrams")
):
    """Universal converter between multiple formats"""
    
    if not input_file.exists():
        console.print(f"[red]Error: Input file '{input_file}' not found![/red]")
        raise typer.Exit(1)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    converter = UniversalConverter()
    
    # Show detected formats
    detected_input = converter.detect_format(input_file)
    detected_output = converter.detect_format(output_file) if output_file.suffix else 'json'
    
    actual_input = input_format or detected_input
    actual_output = output_format or detected_output
    
    console.print(f"[cyan]Converting: {actual_input} → {actual_output}[/cyan]")
    
    options = {
        'diagram_type': diagram_type,
        'title': title or input_file.stem,
        'trace_id': trace_id
    }
    
    success = converter.convert(input_file, output_file, actual_input, actual_output, options)
    
    if success:
        console.print(f"[green]✓ Successfully converted to {output_file}[/green]")
    else:
        raise typer.Exit(1)


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Input directory"),
    output_dir: Path = typer.Argument(..., help="Output directory"),
    input_format: Optional[str] = typer.Option(None, "--from", "-f", help="Input format filter"),
    output_format: str = typer.Option("json", "--to", "-t", help="Output format"),
    pattern: str = typer.Option("*", "--pattern", "-p", help="File pattern to match")
):
    """Batch convert multiple files"""
    
    if not input_dir.exists():
        console.print(f"[red]Error: Input directory '{input_dir}' not found![/red]")
        raise typer.Exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find files to convert
    if input_format:
        extensions = {'yaml': ['*.yaml', '*.yml'], 'json': ['*.json'], 
                     'mermaid': ['*.mmd', '*.mermaid'], 'csv': ['*.csv']}
        patterns = extensions.get(input_format, [f"*.{input_format}"])
    else:
        patterns = [pattern]
    
    files = []
    for pat in patterns:
        files.extend(input_dir.glob(pat))
    
    if not files:
        console.print(f"[yellow]No files found matching criteria[/yellow]")
        return
    
    console.print(f"[cyan]Found {len(files)} files to convert[/cyan]")
    
    converter = UniversalConverter()
    success_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Converting files...", total=len(files))
        
        for file_path in files:
            try:
                output_file = output_dir / f"{file_path.stem}.{output_format}"
                progress.update(task, description=f"Converting {file_path.name}")
                
                if converter.convert(file_path, output_file, input_format, output_format):
                    success_count += 1
                
                progress.advance(task)
                
            except Exception as e:
                console.print(f"[red]Error converting {file_path}: {e}[/red]")
    
    console.print(f"\n[green]✓ Successfully converted {success_count}/{len(files)} files[/green]")


@app.command()
def formats():
    """Show supported input and output formats"""
    
    converter = UniversalConverter()
    
    console.print("[bold cyan]Universal Conversion Toolkit - Supported Formats[/bold cyan]")
    console.print("=" * 60)
    
    # Input formats
    input_table = Table(title="Input Formats")
    input_table.add_column("Format", style="cyan")
    input_table.add_column("Extensions", style="yellow")
    input_table.add_column("Description", style="white")
    
    format_info = {
        'yaml': ('.yaml, .yml', 'Weaver semantic conventions'),
        'json': ('.json', 'OpenTelemetry spans, general JSON data'),
        'mermaid': ('.mmd, .mermaid', 'Mermaid diagram source'),
        'csv': ('.csv', 'Comma-separated values'),
        'md': ('.md', 'Markdown with embedded Mermaid'),
        'html': ('.html', 'HTML files')
    }
    
    for fmt, (exts, desc) in format_info.items():
        input_table.add_row(fmt.upper(), exts, desc)
    
    console.print(input_table)
    
    # Output formats
    output_table = Table(title="Output Formats")
    output_table.add_column("Format", style="cyan")
    output_table.add_column("Extensions", style="yellow")
    output_table.add_column("Description", style="white")
    
    output_info = {
        'json': ('.json', 'Structured JSON data'),
        'yaml': ('.yaml', 'YAML format'),
        'mermaid': ('.mmd', 'Mermaid diagram source'),
        'html': ('.html', 'Interactive HTML with Mermaid.js'),
        'csv': ('.csv', 'Tabular data format'),
        'svg': ('.svg', 'Vector graphics (planned)'),
        'png': ('.png', 'Raster images (planned)')
    }
    
    for fmt, (exts, desc) in output_info.items():
        output_table.add_row(fmt.upper(), exts, desc)
    
    console.print(output_table)
    
    # Conversion matrix
    console.print("\n[bold]Supported Conversions:[/bold]")
    matrix_table = Table()
    matrix_table.add_column("From", style="cyan")
    matrix_table.add_column("To", style="yellow")
    matrix_table.add_column("Use Case", style="white")
    
    conversions = [
        ("YAML", "Mermaid", "Visualize Weaver semantic conventions"),
        ("JSON", "Mermaid", "Visualize OpenTelemetry traces"),
        ("Mermaid", "JSON", "Extract structured data from diagrams"),
        ("Mermaid", "HTML", "Create interactive visualizations"),
        ("JSON", "YAML", "Convert between data formats"),
        ("Mermaid", "CSV", "Tabular analysis of diagram data"),
        ("JSON", "CSV", "Flatten JSON for spreadsheet analysis")
    ]
    
    for from_fmt, to_fmt, use_case in conversions:
        matrix_table.add_row(from_fmt, to_fmt, use_case)
    
    console.print(matrix_table)


@app.command()
def pipeline(
    config_file: Path = typer.Argument(..., help="Pipeline configuration file (YAML)")
):
    """Run conversion pipeline from configuration"""
    
    if not config_file.exists():
        console.print(f"[red]Error: Config file '{config_file}' not found![/red]")
        raise typer.Exit(1)
    
    # Load pipeline config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    steps = config.get('steps', [])
    if not steps:
        console.print("[yellow]No conversion steps defined in config[/yellow]")
        return
    
    console.print(f"[cyan]Running conversion pipeline with {len(steps)} steps[/cyan]")
    
    converter = UniversalConverter()
    
    for i, step in enumerate(steps, 1):
        step_name = step.get('name', f'Step {i}')
        input_path = Path(step['input'])
        output_path = Path(step['output'])
        input_format = step.get('input_format')
        output_format = step.get('output_format')
        options = step.get('options', {})
        
        console.print(f"\n[bold]Step {i}: {step_name}[/bold]")
        
        if not input_path.exists():
            console.print(f"[red]✗ Input file not found: {input_path}[/red]")
            continue
        
        try:
            success = converter.convert(input_path, output_path, input_format, output_format, options)
            if success:
                console.print(f"[green]✓ Completed: {input_path} → {output_path}[/green]")
            else:
                console.print(f"[red]✗ Failed: {step_name}[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error in {step_name}: {e}[/red]")
    
    console.print("\n[green]✓ Pipeline execution complete[/green]")


if __name__ == "__main__":
    app()