#!/usr/bin/env python3
"""
OpenTelemetry to Mermaid Converter - Visualize Traces and Spans

This script converts OpenTelemetry trace data into Mermaid diagrams
for visualization of distributed traces, span relationships, and timing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from collections import defaultdict

app = typer.Typer()
console = Console()


class OTELToMermaidConverter:
    """Convert OpenTelemetry trace data to Mermaid diagrams"""
    
    def __init__(self):
        self.spans = []
        self.traces = defaultdict(list)
        
    def load_spans(self, data: List[Dict[str, Any]]):
        """Load span data from JSON"""
        self.spans = data
        
        # Group by trace ID
        for span in self.spans:
            trace_id = span.get('context', {}).get('trace_id', 'unknown')
            self.traces[trace_id].append(span)
    
    def _format_duration(self, duration_ns: int) -> str:
        """Format duration in human-readable form"""
        if duration_ns < 1000:
            return f"{duration_ns}ns"
        elif duration_ns < 1000000:
            return f"{duration_ns/1000:.1f}μs"
        elif duration_ns < 1000000000:
            return f"{duration_ns/1000000:.1f}ms"
        else:
            return f"{duration_ns/1000000000:.2f}s"
    
    def _get_span_label(self, span: Dict[str, Any]) -> str:
        """Get a concise label for a span"""
        name = span.get('name', 'unknown')
        attrs = span.get('attributes', {})
        
        # Extract key attributes based on span type
        if 'claude_code' in name:
            tool_name = attrs.get('claude_code.tool.name', '')
            tool_category = attrs.get('claude_code.tool.category', '')
            
            if 'file' in name:
                path = attrs.get('claude_code.file.path', '')
                path = path.split('/')[-1] if path else ''
                return f"{tool_name}\\n{path}"
            elif 'bash' in name:
                cmd = attrs.get('claude_code.bash.command', '')[:30]
                return f"{tool_name}\\n{cmd}"
            elif 'search' in name:
                pattern = attrs.get('claude_code.search.pattern', '')
                return f"{tool_name}\\n{pattern}"
            else:
                return f"{tool_name}\\n{tool_category}"
        
        return name.replace('.', '\\n')
    
    def generate_trace_timeline(self, trace_id: Optional[str] = None) -> str:
        """Generate timeline diagram for a trace"""
        mermaid = ["gantt", "    title Trace Timeline", "    dateFormat X", "    axisFormat %L"]
        
        # Get spans for trace
        if trace_id:
            spans = self.traces.get(trace_id, [])
        else:
            # Use first trace
            spans = list(self.traces.values())[0] if self.traces else []
        
        if not spans:
            return "graph LR\n    NoSpans[No spans found]"
        
        # Sort by start time
        spans.sort(key=lambda s: s.get('start_time', 0))
        
        # Find min start time
        min_start = min(s.get('start_time', 0) for s in spans)
        
        # Add spans to gantt
        for i, span in enumerate(spans):
            span_id = f"span{i}"
            name = self._get_span_label(span)
            start = span.get('start_time', 0) - min_start
            duration = span.get('duration_ns', 0)
            
            # Gantt expects milliseconds from epoch
            start_ms = start // 1000000
            duration_ms = max(1, duration // 1000000)  # Minimum 1ms for visibility
            
            mermaid.append(f"    {name} :{span_id}, {start_ms}, {duration_ms}")
        
        return '\n'.join(mermaid)
    
    def generate_trace_flow(self, trace_id: Optional[str] = None) -> str:
        """Generate flow diagram showing span relationships"""
        mermaid = ["flowchart TD"]
        
        # Get spans for trace
        if trace_id:
            spans = self.traces.get(trace_id, [])
        else:
            spans = list(self.traces.values())[0] if self.traces else []
        
        if not spans:
            return "graph LR\n    NoSpans[No spans found]"
        
        # Create span map
        span_map = {}
        for span in spans:
            span_id = span.get('context', {}).get('span_id', 'unknown')
            span_map[span_id] = span
        
        # Build hierarchy
        for span in spans:
            span_id = span.get('context', {}).get('span_id', 'unknown')
            parent_id = span.get('parent_id')
            
            # Create node
            label = self._get_span_label(span)
            duration = span.get('duration_ns', 0)
            duration_str = self._format_duration(duration)
            status = span.get('status', {}).get('status_code', 'UNSET')
            
            # Style based on status
            if status == 'ERROR':
                style = "fill:#f99,stroke:#333,stroke-width:2px"
                node = f'    {span_id}["{label}\\n⚠️ ERROR\\n{duration_str}"]'
            elif status == 'OK':
                style = "fill:#9f9,stroke:#333,stroke-width:2px"
                node = f'    {span_id}["{label}\\n✓ {duration_str}"]'
            else:
                style = "fill:#ff9,stroke:#333,stroke-width:2px"
                node = f'    {span_id}["{label}\\n{duration_str}"]'
            
            mermaid.append(node)
            mermaid.append(f'    style {span_id} {style}')
            
            # Connect to parent
            if parent_id and parent_id in span_map:
                mermaid.append(f'    {parent_id} --> {span_id}')
        
        return '\n'.join(mermaid)
    
    def generate_attribute_flow(self) -> str:
        """Generate flow showing how attributes propagate through spans"""
        mermaid = ["flowchart LR"]
        
        # Track attribute usage
        attr_usage = defaultdict(list)
        
        for span in self.spans:
            span_name = span.get('name', 'unknown')
            attrs = span.get('attributes', {})
            
            for attr_key, attr_value in attrs.items():
                if attr_key.startswith('claude_code'):
                    attr_usage[attr_key].append((span_name, attr_value))
        
        # Create nodes for common attributes
        mermaid.append("    subgraph Base[Base Attributes]")
        base_attrs = ['claude_code.tool.name', 'claude_code.tool.category', 
                      'claude_code.session.id', 'claude_code.user.request']
        for attr in base_attrs:
            if attr in attr_usage:
                count = len(attr_usage[attr])
                mermaid.append(f'        {attr.replace(".", "_")}["{attr}\\nUsed: {count}x"]')
        mermaid.append("    end")
        
        # Create nodes for category-specific attributes
        categories = defaultdict(list)
        for attr in attr_usage:
            if '.' in attr and attr.count('.') >= 2:
                category = attr.split('.')[1]
                categories[category].append(attr)
        
        for category, attrs in categories.items():
            if category not in ['tool', 'session', 'user']:
                mermaid.append(f"    subgraph {category}[{category.title()} Attributes]")
                for attr in attrs:
                    count = len(attr_usage[attr])
                    mermaid.append(f'        {attr.replace(".", "_")}["{attr}\\nUsed: {count}x"]')
                mermaid.append("    end")
        
        # Connect base to specific
        mermaid.append("    Base --> file")
        mermaid.append("    Base --> bash")
        mermaid.append("    Base --> search")
        mermaid.append("    Base --> web")
        mermaid.append("    Base --> agent")
        
        return '\n'.join(mermaid)
    
    def generate_error_analysis(self) -> str:
        """Generate diagram showing error patterns"""
        mermaid = ["flowchart TD"]
        
        # Find error spans
        error_spans = [s for s in self.spans if s.get('status', {}).get('status_code') == 'ERROR']
        
        if not error_spans:
            return "graph LR\n    NoErrors[No errors found ✨]"
        
        # Group errors by type
        error_types = defaultdict(list)
        for span in error_spans:
            name = span.get('name', 'unknown')
            events = span.get('events', [])
            exception = None
            
            for event in events:
                if 'exception' in event.get('name', '').lower():
                    exception = event.get('attributes', {}).get('exception.message', 'Unknown error')
                    break
            
            error_types[name].append(exception or 'No exception details')
        
        # Create diagram
        mermaid.append("    Errors[Error Analysis]")
        
        for span_type, errors in error_types.items():
            type_node = span_type.replace('.', '_')
            mermaid.append(f'    {type_node}["{span_type}\\nCount: {len(errors)}"]')
            mermaid.append(f'    Errors --> {type_node}')
            
            # Add unique error messages
            unique_errors = list(set(errors))[:3]  # Show up to 3 unique errors
            for i, error in enumerate(unique_errors):
                error_node = f"{type_node}_err{i}"
                error_text = error[:50] + '...' if len(error) > 50 else error
                mermaid.append(f'    {error_node}["{error_text}"]')
                mermaid.append(f'    {type_node} --> {error_node}')
                mermaid.append(f'    style {error_node} fill:#fdd,stroke:#f00,stroke-width:2px')
        
        mermaid.append("    style Errors fill:#f99,stroke:#333,stroke-width:3px")
        
        return '\n'.join(mermaid)
    
    def generate_performance_summary(self) -> str:
        """Generate performance summary diagram"""
        mermaid = ["graph TB"]
        
        # Calculate statistics by span type
        stats = defaultdict(lambda: {'count': 0, 'total_duration': 0, 'min': float('inf'), 'max': 0})
        
        for span in self.spans:
            name = span.get('name', 'unknown')
            duration = span.get('duration_ns', 0)
            
            stats[name]['count'] += 1
            stats[name]['total_duration'] += duration
            stats[name]['min'] = min(stats[name]['min'], duration)
            stats[name]['max'] = max(stats[name]['max'], duration)
        
        # Create diagram
        mermaid.append("    Perf[Performance Summary]")
        
        for span_type, data in stats.items():
            if data['count'] > 0:
                avg_duration = data['total_duration'] / data['count']
                type_node = span_type.replace('.', '_')
                
                label = f"{span_type}\\nCount: {data['count']}\\n"
                label += f"Avg: {self._format_duration(int(avg_duration))}\\n"
                label += f"Min: {self._format_duration(data['min'])}\\n"
                label += f"Max: {self._format_duration(data['max'])}"
                
                mermaid.append(f'    {type_node}["{label}"]')
                mermaid.append(f'    Perf --> {type_node}')
                
                # Color based on average duration
                if avg_duration < 1000000:  # < 1ms
                    style = "fill:#9f9,stroke:#333,stroke-width:2px"
                elif avg_duration < 100000000:  # < 100ms
                    style = "fill:#ff9,stroke:#333,stroke-width:2px"
                else:  # >= 100ms
                    style = "fill:#f99,stroke:#333,stroke-width:2px"
                
                mermaid.append(f'    style {type_node} {style}')
        
        mermaid.append("    style Perf fill:#bbf,stroke:#333,stroke-width:3px")
        
        return '\n'.join(mermaid)


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="JSON file containing OTEL span data"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for Mermaid diagram"),
    diagram_type: str = typer.Option("flow", "--type", "-t", help="Diagram type: flow, timeline, attributes, errors, performance"),
    trace_id: Optional[str] = typer.Option(None, "--trace", help="Specific trace ID to visualize"),
    show: bool = typer.Option(True, "--show", "-s", help="Display the generated diagram")
):
    """Convert OpenTelemetry span data to Mermaid diagrams"""
    
    if not input_file.exists():
        console.print(f"[red]Error: File '{input_file}' not found![/red]")
        raise typer.Exit(1)
    
    # Load span data
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Handle different formats
        if isinstance(data, dict) and 'spans' in data:
            spans = data['spans']
        elif isinstance(data, list):
            spans = data
        else:
            console.print("[red]Error: Unexpected JSON format[/red]")
            raise typer.Exit(1)
        
        converter = OTELToMermaidConverter()
        converter.load_spans(spans)
        
        console.print(f"[green]✓ Loaded {len(spans)} spans from {len(converter.traces)} traces[/green]")
        
    except Exception as e:
        console.print(f"[red]Error loading JSON: {e}[/red]")
        raise typer.Exit(1)
    
    # Generate diagram based on type
    diagram_generators = {
        "flow": lambda: converter.generate_trace_flow(trace_id),
        "timeline": lambda: converter.generate_trace_timeline(trace_id),
        "attributes": converter.generate_attribute_flow,
        "errors": converter.generate_error_analysis,
        "performance": converter.generate_performance_summary
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
        panel = Panel(syntax, title=f"OTEL {diagram_type.title()} Diagram", border_style="green")
        console.print(panel)
    
    return mermaid_content


@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="JSON file containing OTEL span data")
):
    """Analyze OTEL span data and show summary"""
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'spans' in data:
            spans = data['spans']
        elif isinstance(data, list):
            spans = data
        else:
            spans = []
        
        converter = OTELToMermaidConverter()
        converter.load_spans(spans)
        
    except Exception as e:
        console.print(f"[red]Error loading JSON: {e}[/red]")
        raise typer.Exit(1)
    
    # Analysis
    console.print("[bold cyan]OpenTelemetry Span Analysis[/bold cyan]")
    console.print("=" * 50)
    
    console.print(f"\n[bold]Overview:[/bold]")
    console.print(f"  Total Spans: {len(spans)}")
    console.print(f"  Total Traces: {len(converter.traces)}")
    
    # Span types
    span_types = defaultdict(int)
    for span in spans:
        span_types[span.get('name', 'unknown')] += 1
    
    console.print(f"\n[bold]Span Types:[/bold]")
    for span_type, count in sorted(span_types.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {span_type}: {count}")
    
    # Status summary
    status_counts = defaultdict(int)
    for span in spans:
        status = span.get('status', {}).get('status_code', 'UNSET')
        status_counts[status] += 1
    
    console.print(f"\n[bold]Status Summary:[/bold]")
    for status, count in status_counts.items():
        console.print(f"  {status}: {count}")
    
    # Performance summary
    total_duration = sum(s.get('duration_ns', 0) for s in spans)
    if spans:
        avg_duration = total_duration / len(spans)
        console.print(f"\n[bold]Performance:[/bold]")
        console.print(f"  Total Duration: {total_duration/1e9:.3f}s")
        console.print(f"  Average Duration: {avg_duration/1e6:.2f}ms")


@app.command()
def live(
    port: int = typer.Option(8080, "--port", "-p", help="Port for web server")
):
    """Create live updating OTEL visualization dashboard"""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>OTEL Live Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({ startOnLoad: true });</script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #fff;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .panel {
            background-color: #2d2d2d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .panel h2 {
            margin-top: 0;
            color: #4CAF50;
        }
        .mermaid {
            text-align: center;
            background-color: white;
            border-radius: 4px;
            padding: 10px;
        }
        .stats {
            font-family: monospace;
            font-size: 14px;
        }
        .stats-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #444;
        }
        #status {
            text-align: center;
            padding: 10px;
            background-color: #4CAF50;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 OpenTelemetry Live Visualization</h1>
        <div id="status">Waiting for span data...</div>
        
        <div class="grid">
            <div class="panel">
                <h2>Trace Flow</h2>
                <div id="trace-flow" class="mermaid">
                    graph LR
                    Waiting[Waiting for data...]
                </div>
            </div>
            
            <div class="panel">
                <h2>Performance Summary</h2>
                <div id="performance" class="mermaid">
                    graph TB
                    Waiting[Waiting for data...]
                </div>
            </div>
            
            <div class="panel">
                <h2>Real-time Stats</h2>
                <div class="stats" id="stats">
                    <div class="stats-row">
                        <span>Total Spans:</span>
                        <span id="total-spans">0</span>
                    </div>
                    <div class="stats-row">
                        <span>Active Traces:</span>
                        <span id="active-traces">0</span>
                    </div>
                    <div class="stats-row">
                        <span>Error Rate:</span>
                        <span id="error-rate">0%</span>
                    </div>
                    <div class="stats-row">
                        <span>Avg Duration:</span>
                        <span id="avg-duration">0ms</span>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>Error Analysis</h2>
                <div id="errors" class="mermaid">
                    graph LR
                    NoErrors[No errors ✨]
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Simulate live updates (replace with actual WebSocket or polling)
        setInterval(() => {
            // This would fetch real data in production
            document.getElementById('status').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>"""
    
    # Save HTML
    html_file = Path("otel_live_viz.html")
    html_file.write_text(html_content)
    
    console.print(f"[green]✓ Created live visualization: {html_file}[/green]")
    console.print(f"[cyan]Open {html_file} in your browser[/cyan]")
    console.print(f"[yellow]Note: For real-time updates, integrate with your OTEL collector[/yellow]")


if __name__ == "__main__":
    app()