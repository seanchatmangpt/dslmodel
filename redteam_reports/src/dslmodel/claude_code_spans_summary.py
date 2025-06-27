#!/usr/bin/env python3
"""
Claude Code Spans Summary - Visual Overview of All Telemetry Spans

This script provides a visual summary of all Claude Code spans and their attributes.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def show_claude_code_spans_hierarchy():
    """Display the complete hierarchy of Claude Code spans"""
    
    console.print("\n🌟 [bold cyan]Claude Code OpenTelemetry Spans Overview[/bold cyan]")
    console.print("=" * 70)
    
    # Create main tree
    tree = Tree("📊 claude_code.*")
    
    # File Operations
    file_branch = tree.add("📁 claude_code.file")
    file_branch.add("[green]Read[/green] - Read file contents")
    file_branch.add("[green]Write[/green] - Write file contents")
    file_branch.add("[green]Edit[/green] - Edit file (find/replace)")
    file_branch.add("[green]MultiEdit[/green] - Multiple edits in one file")
    
    # Bash Operations
    bash_branch = tree.add("💻 claude_code.bash")
    bash_branch.add("[yellow]Bash[/yellow] - Execute shell commands")
    
    # Search Operations
    search_branch = tree.add("🔍 claude_code.search")
    search_branch.add("[blue]Grep[/blue] - Search file contents")
    search_branch.add("[blue]Glob[/blue] - Find files by pattern")
    search_branch.add("[blue]LS[/blue] - List directory contents")
    
    # Web Operations
    web_branch = tree.add("🌐 claude_code.web")
    web_branch.add("[magenta]WebFetch[/magenta] - Fetch and process web content")
    web_branch.add("[magenta]WebSearch[/magenta] - Search the web")
    
    # Agent Operations
    agent_branch = tree.add("🤖 claude_code.agent")
    agent_branch.add("[cyan]Task[/cyan] - Launch autonomous agent task")
    
    # Todo Operations
    todo_branch = tree.add("📝 claude_code.todo")
    todo_branch.add("[yellow]TodoRead[/yellow] - Read todo list")
    todo_branch.add("[yellow]TodoWrite[/yellow] - Update todo list")
    
    # Notebook Operations
    notebook_branch = tree.add("📓 claude_code.notebook")
    notebook_branch.add("[green]NotebookRead[/green] - Read Jupyter notebook")
    notebook_branch.add("[green]NotebookEdit[/green] - Edit notebook cells")
    
    # Special Operations
    special_branch = tree.add("⚡ Special Spans")
    special_branch.add("[red]claude_code.unknown[/red] - Unknown tool calls")
    special_branch.add("[red]claude_code.plan[/red] - Planning mode exit")
    special_branch.add("[red]claude_code.operation.*[/red] - Grouped operations")
    
    console.print(tree)
    
    # Show attributes table
    console.print("\n📋 [bold]Common Span Attributes[/bold]")
    
    attr_table = Table(title="Claude Code Span Attributes", show_header=True)
    attr_table.add_column("Attribute", style="cyan")
    attr_table.add_column("Type", style="yellow")
    attr_table.add_column("Description", style="white")
    attr_table.add_column("Example", style="green")
    
    # Base attributes
    attr_table.add_section()
    attr_table.add_row("📌 Base Attributes", "", "", "")
    attr_table.add_row("claude_code.tool.name", "string", "Tool being used", "Read, Write, Bash")
    attr_table.add_row("claude_code.tool.category", "string", "Tool category", "file, bash, search")
    attr_table.add_row("claude_code.session.id", "string", "Session identifier", "session_123456")
    attr_table.add_row("claude_code.user.request", "string", "Original user request", "Read main.py")
    attr_table.add_row("claude_code.duration_ms", "double", "Execution duration", "125.5")
    
    # File attributes
    attr_table.add_section()
    attr_table.add_row("📁 File Attributes", "", "", "")
    attr_table.add_row("claude_code.file.path", "string", "File path", "/path/to/file.py")
    attr_table.add_row("claude_code.file.operation", "string", "Operation type", "read, write, edit")
    attr_table.add_row("claude_code.file.size_bytes", "int", "File size", "2048")
    attr_table.add_row("claude_code.file.lines_affected", "int", "Lines changed", "42")
    
    # Bash attributes
    attr_table.add_section()
    attr_table.add_row("💻 Bash Attributes", "", "", "")
    attr_table.add_row("claude_code.bash.command", "string", "Command executed", "ls -la")
    attr_table.add_row("claude_code.bash.exit_code", "int", "Exit code", "0")
    attr_table.add_row("claude_code.bash.timeout_ms", "double", "Timeout setting", "5000")
    
    # Search attributes
    attr_table.add_section()
    attr_table.add_row("🔍 Search Attributes", "", "", "")
    attr_table.add_row("claude_code.search.pattern", "string", "Search pattern", "*.py")
    attr_table.add_row("claude_code.search.path", "string", "Search directory", "/src")
    attr_table.add_row("claude_code.search.results_count", "int", "Results found", "25")
    
    # Web attributes
    attr_table.add_section()
    attr_table.add_row("🌐 Web Attributes", "", "", "")
    attr_table.add_row("claude_code.web.url", "string", "URL accessed", "https://api.example.com")
    attr_table.add_row("claude_code.web.operation", "string", "Web operation", "fetch, search")
    attr_table.add_row("claude_code.web.response_size_bytes", "int", "Response size", "4096")
    attr_table.add_row("claude_code.web.cache_hit", "boolean", "Cache hit", "true/false")
    
    # Agent attributes
    attr_table.add_section()
    attr_table.add_row("🤖 Agent Attributes", "", "", "")
    attr_table.add_row("claude_code.agent.id", "string", "Agent identifier", "agent_123")
    attr_table.add_row("claude_code.agent.task", "string", "Task description", "Analyze code")
    attr_table.add_row("claude_code.agent.status", "string", "Current status", "completed")
    attr_table.add_row("claude_code.agent.progress_percent", "double", "Progress", "75.0")
    
    console.print(attr_table)
    
    # Show span examples
    console.print("\n📝 [bold]Example Span Structures[/bold]")
    
    # File operation example
    file_example = Panel(
        """[cyan]Span Name:[/cyan] claude_code.file
[cyan]Attributes:[/cyan]
  claude_code.tool.name: "Read"
  claude_code.tool.category: "file"
  claude_code.session.id: "session_123"
  claude_code.user.request: "Read config.yaml"
  claude_code.file.path: "/app/config.yaml"
  claude_code.file.operation: "read"
  claude_code.file.size_bytes: 1024
  claude_code.file.lines_affected: 45
  claude_code.duration_ms: 12.5
[cyan]Status:[/cyan] OK""",
        title="📁 File Read Span Example",
        border_style="green"
    )
    console.print(file_example)
    
    # Agent task example
    agent_example = Panel(
        """[cyan]Span Name:[/cyan] claude_code.agent
[cyan]Attributes:[/cyan]
  claude_code.tool.name: "Task"
  claude_code.tool.category: "agent"
  claude_code.session.id: "session_123"
  claude_code.user.request: "Analyze security"
  claude_code.agent.id: "agent_456"
  claude_code.agent.task: "Security vulnerability scan"
  claude_code.agent.status: "completed"
  claude_code.agent.progress_percent: 100.0
  claude_code.duration_ms: 3500.0
[cyan]Events:[/cyan]
  - Progress update: 25% (timestamp: T+500ms)
  - Progress update: 50% (timestamp: T+1500ms)
  - Progress update: 75% (timestamp: T+2500ms)
  - Progress update: 100% (timestamp: T+3500ms)
[cyan]Status:[/cyan] OK""",
        title="🤖 Agent Task Span Example",
        border_style="cyan"
    )
    console.print(agent_example)
    
    # Error span example
    error_example = Panel(
        """[cyan]Span Name:[/cyan] claude_code.bash
[cyan]Attributes:[/cyan]
  claude_code.tool.name: "Bash"
  claude_code.tool.category: "bash"
  claude_code.session.id: "session_123"
  claude_code.user.request: "Run invalid command"
  claude_code.bash.command: "invalid_command"
  claude_code.bash.exit_code: 127
  claude_code.duration_ms: 15.2
[cyan]Status:[/cyan] ERROR
[cyan]Exception:[/cyan] Command not found: invalid_command""",
        title="❌ Error Span Example",
        border_style="red"
    )
    console.print(error_example)
    
    # Show span relationships
    console.print("\n🔗 [bold]Span Relationships[/bold]")
    
    relationship_tree = Tree("🎯 claude_code.operation.refactoring")
    child1 = relationship_tree.add("📁 claude_code.file (Read old_module.py)")
    child2 = relationship_tree.add("📁 claude_code.file (Write new_module.py)")
    child3 = relationship_tree.add("💻 claude_code.bash (Run tests)")
    
    console.print(Panel(
        relationship_tree,
        title="Parent-Child Span Relationship",
        border_style="yellow"
    ))
    
    # Summary statistics
    console.print("\n📊 [bold]Span Categories Summary[/bold]")
    
    summary_table = Table(show_header=True)
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Span Count", style="yellow")
    summary_table.add_column("Tools", style="green")
    
    summary_table.add_row("File Operations", "4", "Read, Write, Edit, MultiEdit")
    summary_table.add_row("Bash Operations", "1", "Bash")
    summary_table.add_row("Search Operations", "3", "Grep, Glob, LS")
    summary_table.add_row("Web Operations", "2", "WebFetch, WebSearch")
    summary_table.add_row("Agent Operations", "1", "Task")
    summary_table.add_row("Todo Operations", "2", "TodoRead, TodoWrite")
    summary_table.add_row("Notebook Operations", "2", "NotebookRead, NotebookEdit")
    summary_table.add_row("Special Operations", "3+", "Unknown, Plan, Operation.*")
    
    console.print(summary_table)
    
    console.print("\n✅ [bold green]Total Claude Code Tool Types: 18+[/bold green]")
    console.print("🔍 Each tool creates spans with specific attributes for complete observability")


if __name__ == "__main__":
    show_claude_code_spans_hierarchy()