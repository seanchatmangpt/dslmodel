#!/usr/bin/env python3
"""
Weaver to Mermaid Converter - Convert Semantic Conventions to Visual Diagrams

This script converts Weaver semantic convention YAML files into various
Mermaid diagram formats for visualization and documentation.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

app = typer.Typer()
console = Console()


class WeaverToMermaidConverter:
    """Convert Weaver semantic conventions to Mermaid diagrams"""
    
    def __init__(self):
        self.groups = []
        self.attributes = []
        
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load Weaver YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.groups = data.get('groups', [])
        self.attributes = data.get('attributes', [])
        
        return data
    
    def generate_hierarchy_diagram(self) -> str:
        """Generate hierarchy diagram showing groups and their relationships"""
        mermaid = ["graph TD"]
        
        # Add root node
        mermaid.append("    ROOT[Semantic Conventions]")
        
        # Process groups
        for group in self.groups:
            group_id = group['id']
            group_type = group.get('type', 'unknown')
            brief = group.get('brief', '')[:50] + '...' if len(group.get('brief', '')) > 50 else group.get('brief', '')
            
            # Create node
            node_label = f"{group_id}<br/>{group_type}<br/>{brief}"
            mermaid.append(f'    {group_id.replace(".", "_")}["{node_label}"]')
            
            # Connect to parent
            if 'extends' in group:
                parent = group['extends'].replace(".", "_")
                mermaid.append(f'    {parent} --> {group_id.replace(".", "_")}')
            elif '.' in group_id:
                # Infer parent from ID
                parent_id = '.'.join(group_id.split('.')[:-1]).replace(".", "_")
                mermaid.append(f'    {parent_id} --> {group_id.replace(".", "_")}')
            else:
                mermaid.append(f'    ROOT --> {group_id.replace(".", "_")}')
        
        # Add styling
        mermaid.extend([
            "    style ROOT fill:#f9f,stroke:#333,stroke-width:4px",
            "    classDef span fill:#bbf,stroke:#333,stroke-width:2px",
            "    classDef attribute_group fill:#bfb,stroke:#333,stroke-width:2px"
        ])
        
        # Apply styles based on type
        for group in self.groups:
            if group.get('type') == 'span':
                mermaid.append(f'    class {group["id"].replace(".", "_")} span')
            elif group.get('type') == 'attribute_group':
                mermaid.append(f'    class {group["id"].replace(".", "_")} attribute_group')
        
        return '\n'.join(mermaid)
    
    def generate_attribute_diagram(self) -> str:
        """Generate diagram showing attributes and their relationships"""
        mermaid = ["graph LR"]
        
        # Group attributes by their group
        attr_by_group = {}
        for group in self.groups:
            group_id = group['id']
            attrs = []
            
            # Get direct attributes
            for attr in group.get('attributes', []):
                if 'id' in attr:
                    attrs.append(attr)
                elif 'ref' in attr:
                    # Find referenced attribute
                    ref_id = attr['ref']
                    for global_attr in self.attributes:
                        if global_attr['id'] == ref_id or ref_id.endswith(global_attr['id']):
                            attrs.append(global_attr)
                            break
            
            if attrs:
                attr_by_group[group_id] = attrs
        
        # Create nodes for each group and its attributes
        for group_id, attrs in attr_by_group.items():
            group_node = group_id.replace(".", "_")
            mermaid.append(f'    {group_node}["{group_id}"]')
            
            for i, attr in enumerate(attrs):
                attr_id = attr.get('id', attr.get('ref', f'attr_{i}'))
                attr_type = attr.get('type', 'unknown')
                attr_node = f"{group_node}_{attr_id.replace('.', '_')}"
                
                label = f"{attr_id}<br/>{attr_type}"
                mermaid.append(f'    {attr_node}["{label}"]')
                mermaid.append(f'    {group_node} --> {attr_node}')
        
        # Add styling
        mermaid.extend([
            "    classDef group fill:#bbf,stroke:#333,stroke-width:2px",
            "    classDef attribute fill:#ffd,stroke:#333,stroke-width:1px"
        ])
        
        return '\n'.join(mermaid)
    
    def generate_span_lifecycle_diagram(self) -> str:
        """Generate state diagram for span lifecycle"""
        mermaid = ["stateDiagram-v2"]
        
        # Find span groups
        span_groups = [g for g in self.groups if g.get('type') == 'span']
        
        if not span_groups:
            return "graph LR\n    NoSpans[No span groups found]"
        
        # Create state diagram
        mermaid.extend([
            "    [*] --> Created: Span Created",
            "    Created --> AttributesSet: Set Attributes",
            "    AttributesSet --> Active: Start Recording",
            "    Active --> Events: Add Events",
            "    Events --> Active: Continue",
            "    Active --> Ending: End Span",
            "    Ending --> StatusSet: Set Status",
            "    StatusSet --> Closed: Export",
            "    Closed --> [*]",
            "",
            "    note right of AttributesSet"
        ])
        
        # Add attributes from first span as example
        if span_groups:
            span = span_groups[0]
            attrs = span.get('attributes', [])[:5]  # First 5 attributes
            mermaid.append(f"        Attributes for {span['id']}:")
            for attr in attrs:
                if 'id' in attr:
                    mermaid.append(f"        - {attr['id']}")
                elif 'ref' in attr:
                    mermaid.append(f"        - {attr['ref']}")
        
        mermaid.append("    end note")
        
        return '\n'.join(mermaid)
    
    def generate_class_diagram(self) -> str:
        """Generate class diagram showing attribute types"""
        mermaid = ["classDiagram"]
        
        # Create base class
        mermaid.append("    class SemanticConvention {")
        mermaid.append("        +id: string")
        mermaid.append("        +type: string")
        mermaid.append("        +brief: string")
        mermaid.append("    }")
        
        # Create classes for each group
        for group in self.groups:
            group_id = group['id'].replace(".", "_")
            mermaid.append(f"    class {group_id} {{")
            
            # Add attributes
            for attr in group.get('attributes', []):
                if 'id' in attr:
                    attr_name = attr['id']
                    attr_type = attr.get('type', 'string')
                    requirement = attr.get('requirement_level', 'optional')
                    mermaid.append(f"        +{attr_name}: {attr_type} [{requirement}]")
                elif 'ref' in attr:
                    ref_name = attr['ref'].split('.')[-1]
                    mermaid.append(f"        +{ref_name}: ref")
            
            mermaid.append("    }")
            
            # Add inheritance
            if 'extends' in group:
                parent = group['extends'].replace(".", "_")
                mermaid.append(f"    {parent} <|-- {group_id}")
            else:
                mermaid.append(f"    SemanticConvention <|-- {group_id}")
        
        return '\n'.join(mermaid)
    
    def generate_requirement_flow(self) -> str:
        """Generate flowchart showing requirement levels"""
        mermaid = ["flowchart TD"]
        
        # Count requirement levels
        req_counts = {
            'required': [],
            'recommended': [],
            'optional': []
        }
        
        for group in self.groups:
            for attr in group.get('attributes', []):
                req_level = attr.get('requirement_level', 'optional')
                if req_level in req_counts:
                    attr_id = attr.get('id', attr.get('ref', 'unknown'))
                    req_counts[req_level].append(f"{group['id']}.{attr_id}")
        
        # Create flowchart
        mermaid.append("    Start[Attribute Definition]")
        mermaid.append("    Start --> ReqCheck{Requirement Level?}")
        mermaid.append("    ReqCheck -->|required| Required[Required Attributes]")
        mermaid.append("    ReqCheck -->|recommended| Recommended[Recommended Attributes]")
        mermaid.append("    ReqCheck -->|optional| Optional[Optional Attributes]")
        
        # Add counts
        mermaid.append(f"    Required --> ReqCount[Count: {len(req_counts['required'])}]")
        mermaid.append(f"    Recommended --> RecCount[Count: {len(req_counts['recommended'])}]")
        mermaid.append(f"    Optional --> OptCount[Count: {len(req_counts['optional'])}]")
        
        # Add styling
        mermaid.extend([
            "    style Required fill:#f99,stroke:#333,stroke-width:2px",
            "    style Recommended fill:#ff9,stroke:#333,stroke-width:2px",
            "    style Optional fill:#9f9,stroke:#333,stroke-width:2px"
        ])
        
        return '\n'.join(mermaid)
    
    def generate_mindmap(self) -> str:
        """Generate mindmap of the semantic conventions"""
        mermaid = ["mindmap"]
        mermaid.append("  root((Semantic Conventions))")
        
        # Group by prefix
        prefixes = {}
        for group in self.groups:
            parts = group['id'].split('.')
            if parts[0] not in prefixes:
                prefixes[parts[0]] = []
            prefixes[parts[0]].append(group)
        
        # Build mindmap
        for prefix, groups in prefixes.items():
            mermaid.append(f"    {prefix}")
            for group in groups:
                indent = "      " * (len(group['id'].split('.')) - 1)
                brief = group.get('brief', '')[:30] + '...' if len(group.get('brief', '')) > 30 else group.get('brief', '')
                mermaid.append(f"{indent}{group['id'].split('.')[-1]}")
                
                # Add some attributes
                attrs = group.get('attributes', [])[:3]
                for attr in attrs:
                    attr_id = attr.get('id', attr.get('ref', ''))
                    if attr_id:
                        mermaid.append(f"{indent}  {attr_id.split('.')[-1]}")
        
        return '\n'.join(mermaid)


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Weaver YAML file to convert"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for Mermaid diagram"),
    diagram_type: str = typer.Option("hierarchy", "--type", "-t", help="Diagram type: hierarchy, attributes, lifecycle, class, requirements, mindmap"),
    show: bool = typer.Option(True, "--show", "-s", help="Display the generated diagram")
):
    """Convert Weaver semantic conventions to Mermaid diagrams"""
    
    if not input_file.exists():
        console.print(f"[red]Error: File '{input_file}' not found![/red]")
        raise typer.Exit(1)
    
    converter = WeaverToMermaidConverter()
    
    try:
        data = converter.load_yaml(str(input_file))
        console.print(f"[green]✓ Loaded {len(converter.groups)} groups and {len(converter.attributes)} attributes[/green]")
    except Exception as e:
        console.print(f"[red]Error loading YAML: {e}[/red]")
        raise typer.Exit(1)
    
    # Generate diagram based on type
    diagram_generators = {
        "hierarchy": converter.generate_hierarchy_diagram,
        "attributes": converter.generate_attribute_diagram,
        "lifecycle": converter.generate_span_lifecycle_diagram,
        "class": converter.generate_class_diagram,
        "requirements": converter.generate_requirement_flow,
        "mindmap": converter.generate_mindmap
    }
    
    if diagram_type not in diagram_generators:
        console.print(f"[red]Error: Unknown diagram type '{diagram_type}'[/red]")
        console.print(f"Available types: {', '.join(diagram_generators.keys())}")
        raise typer.Exit(1)
    
    # Generate diagram
    console.print(f"[cyan]Generating {diagram_type} diagram...[/cyan]")
    mermaid_content = diagram_generators[diagram_type]()
    
    # Save if output file specified
    if output_file:
        output_file.write_text(mermaid_content)
        console.print(f"[green]✓ Saved diagram to {output_file}[/green]")
    
    # Display if requested
    if show:
        syntax = Syntax(mermaid_content, "mermaid", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title=f"{diagram_type.title()} Diagram", border_style="green")
        console.print(panel)
    
    return mermaid_content


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Directory containing Weaver YAML files"),
    output_dir: Path = typer.Option("./diagrams", "--output", "-o", help="Output directory for diagrams"),
    types: str = typer.Option("all", "--types", "-t", help="Comma-separated diagram types or 'all'")
):
    """Convert multiple Weaver files to diagrams"""
    
    if not input_dir.exists():
        console.print(f"[red]Error: Directory '{input_dir}' not found![/red]")
        raise typer.Exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get diagram types
    all_types = ["hierarchy", "attributes", "lifecycle", "class", "requirements", "mindmap"]
    if types == "all":
        diagram_types = all_types
    else:
        diagram_types = [t.strip() for t in types.split(",")]
    
    # Find all YAML files
    yaml_files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml"))
    
    if not yaml_files:
        console.print(f"[yellow]No YAML files found in {input_dir}[/yellow]")
        return
    
    console.print(f"[cyan]Found {len(yaml_files)} YAML files[/cyan]")
    
    # Process each file
    total_diagrams = 0
    for yaml_file in yaml_files:
        console.print(f"\n[bold]Processing {yaml_file.name}[/bold]")
        converter = WeaverToMermaidConverter()
        
        try:
            converter.load_yaml(str(yaml_file))
            
            # Generate each diagram type
            for diagram_type in diagram_types:
                output_file = output_dir / f"{yaml_file.stem}_{diagram_type}.mmd"
                convert(yaml_file, output_file, diagram_type, show=False)
                total_diagrams += 1
                
        except Exception as e:
            console.print(f"[red]Error processing {yaml_file}: {e}[/red]")
    
    console.print(f"\n[green]✓ Generated {total_diagrams} diagrams in {output_dir}[/green]")


@app.command()
def visualize(
    input_file: Path = typer.Argument(..., help="Weaver YAML file"),
    port: int = typer.Option(8080, "--port", "-p", help="Port for web server")
):
    """Create interactive HTML visualization of all diagram types"""
    
    converter = WeaverToMermaidConverter()
    converter.load_yaml(str(input_file))
    
    # Generate all diagram types
    diagrams = {}
    diagram_generators = {
        "hierarchy": converter.generate_hierarchy_diagram,
        "attributes": converter.generate_attribute_diagram,
        "lifecycle": converter.generate_span_lifecycle_diagram,
        "class": converter.generate_class_diagram,
        "requirements": converter.generate_requirement_flow,
        "mindmap": converter.generate_mindmap
    }
    
    for diagram_type, generator in diagram_generators.items():
        try:
            diagrams[diagram_type] = generator()
        except:
            diagrams[diagram_type] = converter.generate_hierarchy_diagram()
    
    # Create HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Weaver Semantic Conventions - {input_file.name}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad: true }});</script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .tabs {{
            display: flex;
            background-color: #333;
            border-radius: 5px 5px 0 0;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            color: white;
            border: none;
            background: none;
            font-size: 16px;
        }}
        .tab.active {{
            background-color: #555;
        }}
        .tab:hover {{
            background-color: #444;
        }}
        .content {{
            background-color: white;
            padding: 20px;
            border-radius: 0 0 5px 5px;
            min-height: 500px;
        }}
        .diagram {{
            display: none;
            text-align: center;
        }}
        .diagram.active {{
            display: block;
        }}
        .stats {{
            background-color: #e0e0e0;
            padding: 10px;
            margin-top: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Weaver Semantic Conventions Visualization</h1>
        <h2>{input_file.name}</h2>
        
        <div class="tabs">
            {"".join(f'<button class="tab" onclick="showDiagram(\'{dt}\')">{dt.title()}</button>' for dt in diagrams.keys())}
        </div>
        
        <div class="content">
            {"".join(f'<div id="{dt}" class="diagram"><div class="mermaid">{content}</div></div>' for dt, content in diagrams.items())}
        </div>
        
        <div class="stats">
            <strong>Statistics:</strong>
            Groups: {len(converter.groups)} | 
            Attributes: {len(converter.attributes)} |
            Generated: {len(diagrams)} diagrams
        </div>
    </div>
    
    <script>
        function showDiagram(type) {{
            // Hide all diagrams
            document.querySelectorAll('.diagram').forEach(d => {{
                d.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(t => {{
                t.classList.remove('active');
            }});
            
            // Show selected diagram
            document.getElementById(type).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Show first diagram by default
        document.querySelector('.tab').click();
    </script>
</body>
</html>"""
    
    # Save HTML
    html_file = Path(f"weaver_viz_{input_file.stem}.html")
    html_file.write_text(html_content)
    
    console.print(f"[green]✓ Created visualization: {html_file}[/green]")
    console.print(f"[cyan]Open {html_file} in your browser to view[/cyan]")


if __name__ == "__main__":
    app()