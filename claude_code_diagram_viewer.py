#!/usr/bin/env python3
"""
Claude Code Diagram Viewer - Interactive Mermaid Diagram Display

This script provides an interactive way to view all Claude Code Mermaid diagrams
with syntax highlighting and export capabilities.
"""

import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
import typer

app = typer.Typer()
console = Console()


def extract_mermaid_diagrams(file_path: str) -> dict:
    """Extract all Mermaid diagrams from the markdown file"""
    content = Path(file_path).read_text()
    
    # Find all headers and their associated diagrams
    pattern = r'## (\d+\. .+?)\n\n```mermaid\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    diagrams = {}
    for title, diagram_content in matches:
        diagrams[title] = diagram_content.strip()
    
    return diagrams


def display_diagram_menu(diagrams: dict):
    """Display an interactive menu for diagram selection"""
    console.clear()
    console.print("[bold cyan]Claude Code Mermaid Diagrams[/bold cyan]")
    console.print("=" * 50)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Diagram Title", style="white")
    
    titles = list(diagrams.keys())
    for i, title in enumerate(titles, 1):
        table.add_row(str(i), title)
    
    console.print(table)
    console.print("\n[yellow]0. Exit[/yellow]")
    
    return titles


def display_diagram(title: str, content: str):
    """Display a single diagram with syntax highlighting"""
    console.clear()
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print("=" * len(title))
    
    # Display the Mermaid diagram with syntax highlighting
    syntax = Syntax(content, "mermaid", theme="monokai", line_numbers=True)
    panel = Panel(syntax, title="Mermaid Diagram", border_style="green")
    console.print(panel)
    
    # Show diagram stats
    lines = content.split('\n')
    nodes = len(re.findall(r'[A-Z]+\[', content))
    edges = len(re.findall(r'-->', content)) + len(re.findall(r'-.->|', content))
    
    stats_table = Table(show_header=False)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="yellow")
    stats_table.add_row("Lines", str(len(lines)))
    stats_table.add_row("Nodes (approx)", str(nodes))
    stats_table.add_row("Edges (approx)", str(edges))
    
    console.print("\n[bold]Diagram Statistics:[/bold]")
    console.print(stats_table)


def export_diagram_html(title: str, content: str, output_file: str):
    """Export diagram as HTML with Mermaid.js"""
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
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="mermaid">
{content}
    </div>
</body>
</html>"""
    
    Path(output_file).write_text(html_template)
    console.print(f"[green]✅ Exported to {output_file}[/green]")


@app.command()
def view(
    file_path: str = typer.Option(
        "claude_code_mermaid_diagrams.md",
        "--file", "-f",
        help="Path to the Mermaid diagrams markdown file"
    ),
    export: bool = typer.Option(
        False,
        "--export", "-e",
        help="Export diagrams as HTML files"
    )
):
    """Interactive viewer for Claude Code Mermaid diagrams"""
    
    # Check if file exists
    if not Path(file_path).exists():
        console.print(f"[red]Error: File '{file_path}' not found![/red]")
        raise typer.Exit(1)
    
    # Extract diagrams
    diagrams = extract_mermaid_diagrams(file_path)
    
    if not diagrams:
        console.print("[red]No Mermaid diagrams found in the file![/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]Found {len(diagrams)} diagrams[/green]")
    
    # Interactive menu loop
    while True:
        titles = display_diagram_menu(diagrams)
        
        choice = IntPrompt.ask("\nSelect diagram number", default=0)
        
        if choice == 0:
            console.print("[yellow]Exiting...[/yellow]")
            break
        
        if 1 <= choice <= len(titles):
            selected_title = titles[choice - 1]
            display_diagram(selected_title, diagrams[selected_title])
            
            if export:
                export_choice = Prompt.ask("\nExport this diagram? [y/N]", default="n")
                if export_choice.lower() == 'y':
                    filename = f"claude_code_diagram_{choice}.html"
                    export_diagram_html(selected_title, diagrams[selected_title], filename)
            
            Prompt.ask("\nPress Enter to continue")
        else:
            console.print("[red]Invalid choice![/red]")


@app.command()
def export_all(
    file_path: str = typer.Option(
        "claude_code_mermaid_diagrams.md",
        "--file", "-f",
        help="Path to the Mermaid diagrams markdown file"
    ),
    output_dir: str = typer.Option(
        "claude_code_diagrams",
        "--output", "-o",
        help="Output directory for HTML files"
    )
):
    """Export all diagrams as HTML files"""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract and export all diagrams
    diagrams = extract_mermaid_diagrams(file_path)
    
    for i, (title, content) in enumerate(diagrams.items(), 1):
        clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = output_path / f"{i:02d}_{clean_title}.html"
        export_diagram_html(title, content, str(filename))
    
    # Create index file
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Diagrams Index</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        a {
            text-decoration: none;
            color: #0066cc;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Claude Code Mermaid Diagrams</h1>
    <ul>
"""
    
    for i, (title, _) in enumerate(diagrams.items(), 1):
        clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = f"{i:02d}_{clean_title}.html"
        index_html += f'        <li><a href="{filename}">{title}</a></li>\n'
    
    index_html += """    </ul>
</body>
</html>"""
    
    (output_path / "index.html").write_text(index_html)
    console.print(f"[green]✅ Exported {len(diagrams)} diagrams to {output_dir}/[/green]")
    console.print(f"[green]📄 Open {output_dir}/index.html to view all diagrams[/green]")


@app.command()
def stats(
    file_path: str = typer.Option(
        "claude_code_mermaid_diagrams.md",
        "--file", "-f",
        help="Path to the Mermaid diagrams markdown file"
    )
):
    """Show statistics about all diagrams"""
    
    diagrams = extract_mermaid_diagrams(file_path)
    
    console.print("[bold cyan]Claude Code Diagram Statistics[/bold cyan]")
    console.print("=" * 50)
    
    stats_table = Table(show_header=True)
    stats_table.add_column("Diagram", style="cyan")
    stats_table.add_column("Type", style="yellow")
    stats_table.add_column("Lines", style="green")
    stats_table.add_column("Nodes", style="magenta")
    
    total_lines = 0
    total_nodes = 0
    
    for title, content in diagrams.items():
        # Detect diagram type
        if content.startswith("graph"):
            diagram_type = "Graph"
        elif content.startswith("flowchart"):
            diagram_type = "Flowchart"
        elif content.startswith("sequenceDiagram"):
            diagram_type = "Sequence"
        elif content.startswith("stateDiagram"):
            diagram_type = "State"
        elif content.startswith("classDiagram"):
            diagram_type = "Class"
        else:
            diagram_type = "Other"
        
        lines = len(content.split('\n'))
        nodes = len(re.findall(r'[A-Z]+\[', content))
        
        stats_table.add_row(
            title[:40] + "..." if len(title) > 40 else title,
            diagram_type,
            str(lines),
            str(nodes)
        )
        
        total_lines += lines
        total_nodes += nodes
    
    console.print(stats_table)
    console.print(f"\n[bold]Total Diagrams:[/bold] {len(diagrams)}")
    console.print(f"[bold]Total Lines:[/bold] {total_lines}")
    console.print(f"[bold]Total Nodes:[/bold] {total_nodes}")


if __name__ == "__main__":
    app()