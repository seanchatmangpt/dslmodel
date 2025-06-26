#!/usr/bin/env python3
"""
Mermaid to Data Converter - Extract Structured Data from Mermaid Diagrams

This script parses Mermaid diagrams and converts them back to structured
data formats like JSON, YAML, or CSV for further processing.
"""

import re
import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer()
console = Console()


class MermaidParser:
    """Parse Mermaid diagrams and extract structured data"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.subgraphs = {}
        self.styles = {}
        self.diagram_type = ""
        
    def parse_diagram(self, content: str) -> Dict[str, Any]:
        """Parse Mermaid diagram content"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return {}
        
        # Detect diagram type
        first_line = lines[0].lower()
        if first_line.startswith('graph'):
            self.diagram_type = "graph"
            return self._parse_graph(lines)
        elif first_line.startswith('flowchart'):
            self.diagram_type = "flowchart"
            return self._parse_flowchart(lines)
        elif first_line.startswith('sequencediagram'):
            self.diagram_type = "sequence"
            return self._parse_sequence(lines)
        elif first_line.startswith('statediagram'):
            self.diagram_type = "state"
            return self._parse_state(lines)
        elif first_line.startswith('classdiagram'):
            self.diagram_type = "class"
            return self._parse_class(lines)
        elif first_line.startswith('gantt'):
            self.diagram_type = "gantt"
            return self._parse_gantt(lines)
        elif first_line.startswith('mindmap'):
            self.diagram_type = "mindmap"
            return self._parse_mindmap(lines)
        else:
            self.diagram_type = "unknown"
            return {"error": "Unknown diagram type"}
    
    def _parse_graph(self, lines: List[str]) -> Dict[str, Any]:
        """Parse graph/flowchart diagram"""
        result = {
            "type": "graph",
            "direction": "TD",
            "nodes": {},
            "edges": [],
            "subgraphs": {},
            "styles": {}
        }
        
        # Extract direction from first line
        first_line = lines[0]
        if ' ' in first_line:
            parts = first_line.split()
            if len(parts) > 1:
                result["direction"] = parts[1]
        
        # Parse content
        current_subgraph = None
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Subgraph detection
            if line.startswith('subgraph'):
                match = re.match(r'subgraph\s+(\w+)\[?"?([^"]*)"?\]?', line)
                if match:
                    subgraph_id = match.group(1)
                    subgraph_label = match.group(2) or subgraph_id
                    current_subgraph = subgraph_id
                    result["subgraphs"][subgraph_id] = {
                        "label": subgraph_label,
                        "nodes": []
                    }
                continue
            
            if line == 'end':
                current_subgraph = None
                continue
            
            # Style detection
            if line.startswith('style '):
                style_match = re.match(r'style\s+(\w+)\s+(.+)', line)
                if style_match:
                    node_id = style_match.group(1)
                    style_def = style_match.group(2)
                    result["styles"][node_id] = style_def
                continue
            
            if line.startswith('class '):
                class_match = re.match(r'class\s+(\w+)\s+(\w+)', line)
                if class_match:
                    node_id = class_match.group(1)
                    class_name = class_match.group(2)
                    if node_id not in result["styles"]:
                        result["styles"][node_id] = {}
                    result["styles"][node_id]["class"] = class_name
                continue
            
            # Edge detection
            edge_patterns = [
                r'(\w+)\s*-->\s*(\w+)(?:\s*\|\s*(.+?)\s*\|)?',  # A --> B |label|
                r'(\w+)\s*-\.->\s*(\w+)(?:\s*\|\s*(.+?)\s*\|)?',  # A -.-> B |label|
                r'(\w+)\s*==>\s*(\w+)(?:\s*\|\s*(.+?)\s*\|)?',  # A ==> B |label|
                r'(\w+)\s*---\s*(\w+)',  # A --- B
                r'(\w+)\s*-\.\.-\s*(\w+)',  # A -..- B
            ]
            
            edge_found = False
            for pattern in edge_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    label = match.group(3) if len(match.groups()) > 2 else None
                    
                    result["edges"].append({
                        "source": source,
                        "target": target,
                        "label": label,
                        "type": "arrow" if "-->" in line else "dotted" if "-.>" in line else "thick" if "==>" in line else "line"
                    })
                    edge_found = True
                    break
            
            if edge_found:
                continue
            
            # Node detection
            node_patterns = [
                r'(\w+)\[(.+?)\]',  # A[Label]
                r'(\w+)\((.+?)\)',  # A(Label)
                r'(\w+)\{(.+?)\}',  # A{Label}
                r'(\w+)\(\((.+?)\)\)',  # A((Label))
                r'(\w+)\[\[(.+?)\]\]',  # A[[Label]]
            ]
            
            for pattern in node_patterns:
                match = re.match(pattern, line)
                if match:
                    node_id = match.group(1)
                    node_label = match.group(2)
                    
                    # Determine shape from pattern
                    if '[' in pattern:
                        shape = "rectangle"
                    elif '(' in pattern and ')' in pattern:
                        shape = "circle" if "((" in pattern else "rounded"
                    elif '{' in pattern:
                        shape = "diamond"
                    elif '[[' in pattern:
                        shape = "subroutine"
                    else:
                        shape = "rectangle"
                    
                    result["nodes"][node_id] = {
                        "label": node_label,
                        "shape": shape
                    }
                    
                    # Add to current subgraph
                    if current_subgraph and current_subgraph in result["subgraphs"]:
                        result["subgraphs"][current_subgraph]["nodes"].append(node_id)
                    
                    break
        
        return result
    
    def _parse_flowchart(self, lines: List[str]) -> Dict[str, Any]:
        """Parse flowchart diagram (similar to graph)"""
        return self._parse_graph(lines)
    
    def _parse_sequence(self, lines: List[str]) -> Dict[str, Any]:
        """Parse sequence diagram"""
        result = {
            "type": "sequence",
            "participants": [],
            "messages": [],
            "notes": [],
            "loops": []
        }
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Participant
            participant_match = re.match(r'participant\s+(\w+)(?:\s+as\s+(.+))?', line)
            if participant_match:
                participant_id = participant_match.group(1)
                participant_label = participant_match.group(2) or participant_id
                result["participants"].append({
                    "id": participant_id,
                    "label": participant_label
                })
                continue
            
            # Message
            message_patterns = [
                r'(\w+)\s*->>\s*(\w+)\s*:\s*(.+)',  # A->>B: message
                r'(\w+)\s*->\s*(\w+)\s*:\s*(.+)',   # A->B: message
                r'(\w+)\s*-->\s*(\w+)\s*:\s*(.+)', # A-->B: message
            ]
            
            for pattern in message_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    message = match.group(3)
                    
                    arrow_type = "sync" if "->>" in line else "async" if "-->" in line else "call"
                    
                    result["messages"].append({
                        "source": source,
                        "target": target,
                        "message": message,
                        "type": arrow_type
                    })
                    break
            
            # Note
            note_match = re.match(r'note\s+(left|right|over)\s+(\w+)\s*:\s*(.+)', line)
            if note_match:
                position = note_match.group(1)
                participant = note_match.group(2)
                text = note_match.group(3)
                
                result["notes"].append({
                    "position": position,
                    "participant": participant,
                    "text": text
                })
        
        return result
    
    def _parse_state(self, lines: List[str]) -> Dict[str, Any]:
        """Parse state diagram"""
        result = {
            "type": "state",
            "states": {},
            "transitions": [],
            "notes": []
        }
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # State definition
            state_match = re.match(r'(\w+)\s*:\s*(.+)', line)
            if state_match:
                state_id = state_match.group(1)
                state_label = state_match.group(2)
                result["states"][state_id] = {
                    "label": state_label
                }
                continue
            
            # Transition
            transition_patterns = [
                r'(\w+|\[\*\])\s*-->\s*(\w+|\[\*\])\s*:\s*(.+)',
                r'(\w+|\[\*\])\s*-->\s*(\w+|\[\*\])'
            ]
            
            for pattern in transition_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    trigger = match.group(3) if len(match.groups()) > 2 else ""
                    
                    result["transitions"].append({
                        "source": source,
                        "target": target,
                        "trigger": trigger
                    })
                    break
        
        return result
    
    def _parse_class(self, lines: List[str]) -> Dict[str, Any]:
        """Parse class diagram"""
        result = {
            "type": "class",
            "classes": {},
            "relationships": []
        }
        
        current_class = None
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Class definition start
            class_match = re.match(r'class\s+(\w+)\s*\{', line)
            if class_match:
                current_class = class_match.group(1)
                result["classes"][current_class] = {
                    "name": current_class,
                    "attributes": [],
                    "methods": []
                }
                continue
            
            # Class definition end
            if line == '}':
                current_class = None
                continue
            
            # Class members
            if current_class:
                # Attribute or method
                member_match = re.match(r'([+\-#~]?)(\w+)(?:\s*:\s*(\w+))?(?:\s*\[(\w+)\])?', line)
                if member_match:
                    visibility = member_match.group(1) or '+'
                    name = member_match.group(2)
                    type_info = member_match.group(3)
                    modifier = member_match.group(4)
                    
                    if '(' in line:  # Method
                        result["classes"][current_class]["methods"].append({
                            "name": name,
                            "visibility": visibility,
                            "type": type_info,
                            "modifier": modifier
                        })
                    else:  # Attribute
                        result["classes"][current_class]["attributes"].append({
                            "name": name,
                            "visibility": visibility,
                            "type": type_info,
                            "modifier": modifier
                        })
                continue
            
            # Relationships
            relationship_patterns = [
                r'(\w+)\s*<\|\-\-\s*(\w+)',  # Inheritance
                r'(\w+)\s*\*\-\-\s*(\w+)',   # Composition
                r'(\w+)\s*o\-\-\s*(\w+)',    # Aggregation
                r'(\w+)\s*\-\-\s*(\w+)',     # Association
            ]
            
            for pattern in relationship_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    
                    if '<|--' in line:
                        rel_type = "inheritance"
                    elif '*--' in line:
                        rel_type = "composition"
                    elif 'o--' in line:
                        rel_type = "aggregation"
                    else:
                        rel_type = "association"
                    
                    result["relationships"].append({
                        "source": source,
                        "target": target,
                        "type": rel_type
                    })
                    break
        
        return result
    
    def _parse_gantt(self, lines: List[str]) -> Dict[str, Any]:
        """Parse Gantt chart"""
        result = {
            "type": "gantt",
            "title": "",
            "dateFormat": "",
            "axisFormat": "",
            "tasks": []
        }
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Title
            if line.startswith('title'):
                result["title"] = line.replace('title', '').strip()
                continue
            
            # Date format
            if line.startswith('dateFormat'):
                result["dateFormat"] = line.replace('dateFormat', '').strip()
                continue
            
            # Axis format
            if line.startswith('axisFormat'):
                result["axisFormat"] = line.replace('axisFormat', '').strip()
                continue
            
            # Task
            task_match = re.match(r'(.+?)\s*:\s*(\w+),\s*(.+)', line)
            if task_match:
                name = task_match.group(1)
                task_id = task_match.group(2)
                schedule = task_match.group(3)
                
                result["tasks"].append({
                    "name": name,
                    "id": task_id,
                    "schedule": schedule
                })
        
        return result
    
    def _parse_mindmap(self, lines: List[str]) -> Dict[str, Any]:
        """Parse mindmap"""
        result = {
            "type": "mindmap",
            "root": None,
            "nodes": {}
        }
        
        for line in lines[1:]:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('%%'):
                continue
            
            # Count indentation to determine level
            indent_level = (len(line) - len(line.lstrip())) // 2
            
            # Extract node content
            node_match = re.match(r'(.+?)(?:\(\((.+?)\)\)|\[(.+?)\]|(.+))', line_stripped)
            if node_match:
                content = (node_match.group(2) or node_match.group(3) or 
                          node_match.group(4) or node_match.group(1)).strip()
                
                if indent_level == 0:  # Root
                    result["root"] = content
                else:
                    if indent_level not in result["nodes"]:
                        result["nodes"][indent_level] = []
                    result["nodes"][indent_level].append(content)
        
        return result


@app.command()
def parse(
    input_file: Path = typer.Argument(..., help="Mermaid diagram file to parse"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for structured data"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, csv"),
    show: bool = typer.Option(True, "--show", "-s", help="Display the parsed data")
):
    """Parse Mermaid diagram and extract structured data"""
    
    if not input_file.exists():
        console.print(f"[red]Error: File '{input_file}' not found![/red]")
        raise typer.Exit(1)
    
    # Read Mermaid content
    content = input_file.read_text()
    
    # Parse diagram
    parser = MermaidParser()
    parsed_data = parser.parse_diagram(content)
    
    if "error" in parsed_data:
        console.print(f"[red]Error: {parsed_data['error']}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]✓ Parsed {parser.diagram_type} diagram[/green]")
    
    # Convert to requested format
    if output_format == "json":
        output_content = json.dumps(parsed_data, indent=2)
    elif output_format == "yaml":
        output_content = yaml.dump(parsed_data, default_flow_style=False)
    elif output_format == "csv":
        # CSV output depends on diagram type
        if parser.diagram_type in ["graph", "flowchart"]:
            output_content = _convert_graph_to_csv(parsed_data)
        elif parser.diagram_type == "sequence":
            output_content = _convert_sequence_to_csv(parsed_data)
        else:
            console.print(f"[yellow]CSV format not supported for {parser.diagram_type} diagrams[/yellow]")
            output_content = json.dumps(parsed_data, indent=2)
    else:
        console.print(f"[red]Unsupported format: {output_format}[/red]")
        raise typer.Exit(1)
    
    # Save if output file specified
    if output_file:
        output_file.write_text(output_content)
        console.print(f"[green]✓ Saved {output_format.upper()} to {output_file}[/green]")
    
    # Display if requested
    if show:
        if output_format == "json":
            from rich.syntax import Syntax
            syntax = Syntax(output_content, "json", theme="monokai")
            panel = Panel(syntax, title="Parsed Data (JSON)", border_style="green")
            console.print(panel)
        else:
            console.print(output_content)
    
    return parsed_data


def _convert_graph_to_csv(data: Dict[str, Any]) -> str:
    """Convert graph data to CSV format"""
    import io
    
    output = io.StringIO()
    
    # Write nodes
    writer = csv.writer(output)
    writer.writerow(["Type", "ID", "Label", "Shape", "Subgraph"])
    
    for node_id, node_data in data.get("nodes", {}).items():
        subgraph = ""
        for sg_id, sg_data in data.get("subgraphs", {}).items():
            if node_id in sg_data.get("nodes", []):
                subgraph = sg_id
                break
        
        writer.writerow([
            "Node",
            node_id,
            node_data.get("label", ""),
            node_data.get("shape", ""),
            subgraph
        ])
    
    # Write edges
    for edge in data.get("edges", []):
        writer.writerow([
            "Edge",
            f"{edge['source']}->{edge['target']}",
            edge.get("label", ""),
            edge.get("type", ""),
            ""
        ])
    
    return output.getvalue()


def _convert_sequence_to_csv(data: Dict[str, Any]) -> str:
    """Convert sequence diagram to CSV format"""
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Type", "Source", "Target", "Message", "MessageType"])
    
    for message in data.get("messages", []):
        writer.writerow([
            "Message",
            message.get("source", ""),
            message.get("target", ""),
            message.get("message", ""),
            message.get("type", "")
        ])
    
    return output.getvalue()


@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="Mermaid diagram file to analyze")
):
    """Analyze Mermaid diagram and show statistics"""
    
    content = input_file.read_text()
    parser = MermaidParser()
    parsed_data = parser.parse_diagram(content)
    
    console.print(f"[bold cyan]Mermaid Diagram Analysis: {input_file.name}[/bold cyan]")
    console.print("=" * 60)
    
    # Basic info
    table = Table(title="Diagram Overview")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Diagram Type", parser.diagram_type.title())
    
    if parser.diagram_type in ["graph", "flowchart"]:
        table.add_row("Direction", parsed_data.get("direction", "Unknown"))
        table.add_row("Nodes", str(len(parsed_data.get("nodes", {}))))
        table.add_row("Edges", str(len(parsed_data.get("edges", []))))
        table.add_row("Subgraphs", str(len(parsed_data.get("subgraphs", {}))))
        table.add_row("Styled Nodes", str(len(parsed_data.get("styles", {}))))
    
    elif parser.diagram_type == "sequence":
        table.add_row("Participants", str(len(parsed_data.get("participants", []))))
        table.add_row("Messages", str(len(parsed_data.get("messages", []))))
        table.add_row("Notes", str(len(parsed_data.get("notes", []))))
    
    elif parser.diagram_type == "class":
        table.add_row("Classes", str(len(parsed_data.get("classes", {}))))
        table.add_row("Relationships", str(len(parsed_data.get("relationships", []))))
    
    console.print(table)
    
    # Line count
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('%%')]
    console.print(f"\n[bold]Content Statistics:[/bold]")
    console.print(f"  Total Lines: {len(lines)}")
    console.print(f"  Content Lines: {len([l for l in lines if l])}")
    console.print(f"  Empty Lines: {content.count('\\n\\n')}")


@app.command()
def convert_batch(
    input_dir: Path = typer.Argument(..., help="Directory containing Mermaid files"),
    output_dir: Path = typer.Option("./parsed", "--output", "-o", help="Output directory"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml, csv")
):
    """Parse multiple Mermaid files in batch"""
    
    if not input_dir.exists():
        console.print(f"[red]Error: Directory '{input_dir}' not found![/red]")
        raise typer.Exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find Mermaid files
    extensions = ["*.mmd", "*.mermaid", "*.md"]
    mermaid_files = []
    for ext in extensions:
        mermaid_files.extend(input_dir.glob(ext))
    
    if not mermaid_files:
        console.print(f"[yellow]No Mermaid files found in {input_dir}[/yellow]")
        return
    
    console.print(f"[cyan]Found {len(mermaid_files)} Mermaid files[/cyan]")
    
    # Process each file
    success_count = 0
    for mermaid_file in mermaid_files:
        try:
            output_file = output_dir / f"{mermaid_file.stem}.{output_format}"
            parse(mermaid_file, output_file, output_format, show=False)
            success_count += 1
        except Exception as e:
            console.print(f"[red]Error processing {mermaid_file}: {e}[/red]")
    
    console.print(f"\n[green]✓ Successfully processed {success_count}/{len(mermaid_files)} files[/green]")


if __name__ == "__main__":
    app()