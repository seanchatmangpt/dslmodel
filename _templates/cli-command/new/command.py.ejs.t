---
to: src/dslmodel/commands/<%= fileName %>.py
---
"""
<%= name.charAt(0).toUpperCase() + name.slice(1) %> Command - <%= description %>

This module implements the '<%= name %>' command for the <%= parent_command %> CLI group.
"""

import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import time
<% if (async_command) { %>import asyncio<% } %>
<% if (uses_rich) { %>from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
<% } %>

<% if (has_subcommands) { %>app = typer.Typer(help="<%= description %>")
<% } %>

<% if (!has_subcommands) { %><% if (async_command) { %>async def <%= functionName %>_async(<% } else { %>def <%= functionName %>(<% } %>
<% arguments.forEach(function(arg) { %>    <%= arg.replace(/-/g, '_') %>: str = typer.Argument(..., help="<%= arg.charAt(0).toUpperCase() + arg.slice(1) %> to process"),
<% }); %><% options.forEach(function(opt) { %>    <%= opt.replace(/-/g, '_') %>: <% if (opt === 'verbose') { %>bool = typer.Option(False, "--<%= opt %>", "-v", help="Verbose output")<% } else if (opt === 'format') { %>str = typer.Option("table", "--<%= opt %>", "-f", help="Output format (table, json, yaml)")<% } else { %>str = typer.Option(None, "--<%= opt %>", help="<%= opt.charAt(0).toUpperCase() + opt.slice(1) %> option")<% } %>,
<% }); %>):
    """<%= description %>"""
<% if (uses_rich) { %>    
    console.print(Panel.fit(
        f"[bold blue]<%= name.charAt(0).toUpperCase() + name.slice(1) %> Command[/bold blue]",
        border_style="blue"
    ))
<% } else { %>    
    typer.echo(f"Executing <%= name %> command...")
<% } %>
<% if (arguments.length > 0) { %>    
    # Process arguments
<% arguments.forEach(function(arg) { %>    if <%= arg.replace(/-/g, '_') %>:
<% if (uses_rich) { %>        console.print(f"[green]<%= arg %>:[/green] {<%= arg.replace(/-/g, '_') %>}")<% } else { %>        typer.echo(f"<%= arg %>: {<%= arg.replace(/-/g, '_') %>}")<% } %>
<% }); %><% } %>
<% if (options.includes('verbose')) { %>    
    if verbose:
<% if (uses_rich) { %>        console.print("[dim]Verbose mode enabled[/dim]")<% } else { %>        typer.echo("Verbose mode enabled")<% } %>
<% } %>    
    try:
<% if (async_command) { %>        # Async implementation
        await process_<%= name %>_async(<% arguments.map(a => a.replace(/-/g, '_')).join(', ') %>)
<% } else { %>        # Main implementation
        result = process_<%= name %>(<% arguments.map(a => a.replace(/-/g, '_')).join(', ') %>)
        
        # Display results
        display_results(result<% if (options.includes('format')) { %>, format=<%= options.includes('format') ? 'format' : '' %><% } %>)
<% } %>        
<% if (uses_rich) { %>        console.print("[green]✅ Command completed successfully[/green]")<% } else { %>        typer.echo("Command completed successfully")<% } %>
        
    except Exception as e:
<% if (uses_rich) { %>        console.print(f"[red]❌ Error: {e}[/red]")<% } else { %>        typer.echo(f"Error: {e}", err=True)<% } %>
        raise typer.Exit(1)
<% } %>

<% if (!has_subcommands) { %>def process_<%= name %>(<% arguments.forEach(function(arg, index) { %><%= arg.replace(/-/g, '_') %>: str<% if (index < arguments.length - 1) { %>, <% } %><% }); %>) -> Dict[str, Any]:
    """Process <%= name %> operation.
    
    Args:
<% arguments.forEach(function(arg) { %>        <%= arg.replace(/-/g, '_') %>: <%= arg.charAt(0).toUpperCase() + arg.slice(1) %> to process
<% }); %>    
    Returns:
        Dictionary containing operation results
    """
    # TODO: Implement <%= name %> logic
    results = {
        "status": "success",
        "operation": "<%= name %>",
<% arguments.forEach(function(arg) { %>        "<%= arg %>": <%= arg.replace(/-/g, '_') %>,
<% }); %>        "timestamp": time.time(),
        "data": {
            # Add operation-specific data here
            "processed_items": 0,
            "duration": 0.0
        }
    }
    
    # Simulate processing
    time.sleep(0.5)
    
    return results
<% } %>

<% if (async_command && !has_subcommands) { %>async def process_<%= name %>_async(<% arguments.forEach(function(arg, index) { %><%= arg.replace(/-/g, '_') %>: str<% if (index < arguments.length - 1) { %>, <% } %><% }); %>) -> Dict[str, Any]:
    """Async process <%= name %> operation.
    
    Args:
<% arguments.forEach(function(arg) { %>        <%= arg.replace(/-/g, '_') %>: <%= arg.charAt(0).toUpperCase() + arg.slice(1) %> to process
<% }); %>    
    Returns:
        Dictionary containing operation results
    """
    # TODO: Implement async <%= name %> logic
    results = {
        "status": "success",
        "operation": "<%= name %>",
<% arguments.forEach(function(arg) { %>        "<%= arg %>": <%= arg.replace(/-/g, '_') %>,
<% }); %>        "timestamp": time.time(),
        "data": {}
    }
    
    # Simulate async processing
    await asyncio.sleep(0.5)
    
    return results
<% } %>

<% if (!has_subcommands && options.includes('format')) { %>def display_results(results: Dict[str, Any], format: str = "table"):
    """Display results in the specified format.
    
    Args:
        results: Results dictionary to display
        format: Output format (table, json, yaml)
    """
    if format == "json":
<% if (uses_rich) { %>        console.print_json(json.dumps(results, indent=2))<% } else { %>        typer.echo(json.dumps(results, indent=2))<% } %>
    elif format == "yaml":
        # Convert to YAML-like format
        yaml_output = []
        for key, value in results.items():
            if isinstance(value, dict):
                yaml_output.append(f"{key}:")
                for k, v in value.items():
                    yaml_output.append(f"  {k}: {v}")
            else:
                yaml_output.append(f"{key}: {value}")
<% if (uses_rich) { %>        console.print("\n".join(yaml_output))<% } else { %>        typer.echo("\n".join(yaml_output))<% } %>
    else:
<% if (uses_rich) { %>        # Table format
        table = Table(title="<%= name.charAt(0).toUpperCase() + name.slice(1) %> Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in results.items():
            if isinstance(value, dict):
                table.add_row(key, "")
                for k, v in value.items():
                    table.add_row(f"  {k}", str(v))
            else:
                table.add_row(key, str(value))
        
        console.print(table)
<% } else { %>        # Simple text format
        typer.echo("<%= name.charAt(0).toUpperCase() + name.slice(1) %> Results:")
        for key, value in results.items():
            if isinstance(value, dict):
                typer.echo(f"\n{key}:")
                for k, v in value.items():
                    typer.echo(f"  {k}: {v}")
            else:
                typer.echo(f"{key}: {value}")
<% } %>
<% } %>

<% if (has_subcommands) { %>@app.command("list")
def list_<%= name %>(
    filter: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter results"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of results")
):
    """List <%= name %> items."""
<% if (uses_rich) { %>    console.print(f"[blue]Listing <%= name %> items (limit: {limit})[/blue]")<% } else { %>    typer.echo(f"Listing <%= name %> items (limit: {limit})")<% } %>
    
    # TODO: Implement list logic
    items = []
    
    if filter:
<% if (uses_rich) { %>        console.print(f"[dim]Filter: {filter}[/dim]")<% } else { %>        typer.echo(f"Filter: {filter}")<% } %>
    
<% if (uses_rich) { %>    if not items:
        console.print("[yellow]No items found[/yellow]")
    else:
        table = Table(title="<%= name.charAt(0).toUpperCase() + name.slice(1) %> Items")
        # Add columns based on item structure
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="blue")
        
        for item in items[:limit]:
            table.add_row(
                str(item.get("id", "")),
                item.get("name", ""),
                item.get("status", "")
            )
        
        console.print(table)
<% } else { %>    if not items:
        typer.echo("No items found")
    else:
        for item in items[:limit]:
            typer.echo(f"- {item}")
<% } %>

@app.command("create")
def create_<%= name %>(
    name: str = typer.Argument(..., help="Name of the <%= name %> to create"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file")
):
    """Create a new <%= name %>."""
<% if (uses_rich) { %>    console.print(f"[green]Creating <%= name %>:[/green] {name}")<% } else { %>    typer.echo(f"Creating <%= name %>: {name}")<% } %>
    
    if config and config.exists():
<% if (uses_rich) { %>        console.print(f"[dim]Using config: {config}[/dim]")<% } else { %>        typer.echo(f"Using config: {config}")<% } %>
    
    # TODO: Implement create logic
    
<% if (uses_rich) { %>    console.print(f"[green]✅ Created {name} successfully[/green]")<% } else { %>    typer.echo(f"Created {name} successfully")<% } %>

@app.command("delete")
def delete_<%= name %>(
    name: str = typer.Argument(..., help="Name of the <%= name %> to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Delete a <%= name %>."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete {name}?")
        if not confirm:
            raise typer.Abort()
    
<% if (uses_rich) { %>    console.print(f"[red]Deleting <%= name %>:[/red] {name}")<% } else { %>    typer.echo(f"Deleting <%= name %>: {name}")<% } %>
    
    # TODO: Implement delete logic
    
<% if (uses_rich) { %>    console.print(f"[green]✅ Deleted {name} successfully[/green]")<% } else { %>    typer.echo(f"Deleted {name} successfully")<% } %>
<% } %>

<% if (async_command && !has_subcommands) { %># Wrapper for async command
def <%= functionName %>(
<% arguments.forEach(function(arg) { %>    <%= arg.replace(/-/g, '_') %>: str = typer.Argument(..., help="<%= arg.charAt(0).toUpperCase() + arg.slice(1) %> to process"),
<% }); %><% options.forEach(function(opt) { %>    <%= opt.replace(/-/g, '_') %>: <% if (opt === 'verbose') { %>bool = typer.Option(False, "--<%= opt %>", "-v", help="Verbose output")<% } else if (opt === 'format') { %>str = typer.Option("table", "--<%= opt %>", "-f", help="Output format")<% } else { %>str = typer.Option(None, "--<%= opt %>", help="<%= opt %> option")<% } %>,
<% }); %>):
    """<%= description %>"""
    asyncio.run(<%= functionName %>_async(
<% arguments.forEach(function(arg, index) { %>        <%= arg.replace(/-/g, '_') %><% if (index < arguments.length - 1 || options.length > 0) { %>,<% } %>
<% }); %><% options.forEach(function(opt, index) { %>        <%= opt.replace(/-/g, '_') %>=<%= opt.replace(/-/g, '_') %><% if (index < options.length - 1) { %>,<% } %>
<% }); %>    ))
<% } %>

# Export for CLI integration
__all__ = ["<%= has_subcommands ? 'app' : functionName %>"]