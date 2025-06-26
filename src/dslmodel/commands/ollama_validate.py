#!/usr/bin/env python3
"""
Ollama Validation CLI Commands

Provides CLI interface for validating and managing Ollama configuration
throughout the DSLModel system.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from pathlib import Path
from typing import Optional

from dslmodel.utils.ollama_validator import OllamaValidator, safe_init_ollama

console = Console()
app = typer.Typer(help="Ollama configuration validation and management")


@app.command("check")
def check_ollama(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Specific model to test"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """Check Ollama server status and model availability"""
    
    rprint("🔍 [bold blue]Ollama Configuration Check[/bold blue]")
    rprint("=" * 50)
    
    validator = OllamaValidator()
    validation = validator.validate_configuration()
    
    # Create status table
    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    checks = [
        ("URL Format", validation["url_valid"], validator.config.base_url),
        ("Server Available", validation["server_available"], f"Timeout: {validator.config.timeout}s"),
        ("Models Accessible", validation["models_accessible"], "API endpoint responding"),
        ("Default Model", validation["default_model_available"], validator.config.default_model)
    ]
    
    for check_name, passed, details in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        table.add_row(check_name, status, details)
    
    console.print(table)
    
    # Show messages
    if verbose or validation["errors"] or validation["warnings"]:
        for info in validation["info"]:
            rprint(f"[green]{info}[/green]")
        
        for warning in validation["warnings"]:
            rprint(f"[yellow]{warning}[/yellow]")
        
        for error in validation["errors"]:
            rprint(f"[red]{error}[/red]")
    
    # Test specific model if requested
    if model:
        rprint(f"\n🎯 [bold]Testing Model: {model}[/bold]")
        success, result, message = safe_init_ollama(model)
        status_color = "green" if success else "red"
        rprint(f"[{status_color}]{message}[/{status_color}]")
    
    # Show suggestions if needed
    if validation["errors"] or validation["warnings"]:
        suggestions = validator.suggest_fixes(validation)
        if suggestions:
            rprint("\n💡 [bold yellow]Suggested Fixes:[/bold yellow]")
            for suggestion in suggestions:
                rprint(f"  {suggestion}")


@app.command("models")
def list_models(
    available_only: bool = typer.Option(True, "--available/--all", help="Show only available models"),
    recommended: bool = typer.Option(False, "--recommended", help="Show recommended models for DSLModel")
):
    """List available Ollama models"""
    
    validator = OllamaValidator()
    
    if recommended:
        rprint("🎯 [bold blue]Recommended Models for DSLModel[/bold blue]")
        models = validator.get_recommended_models()
        if models:
            for i, model in enumerate(models[:10]):  # Show top 10
                icon = "⭐" if i < 3 else "📦"  # Star for top 3
                rprint(f"  {icon} {model}")
            if len(models) > 10:
                rprint(f"  ... and {len(models) - 10} more")
        else:
            rprint("[yellow]No models available[/yellow]")
        return
    
    success, models = validator.get_available_models()
    if not success:
        rprint("[red]❌ Could not retrieve model list from Ollama[/red]")
        return
    
    if not models:
        rprint("[yellow]No models found[/yellow]")
        return
    
    # Create models table
    table = Table(title=f"Available Ollama Models ({len(models)})")
    table.add_column("Model", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Modified", style="dim")
    table.add_column("Family", style="magenta")
    
    for model in models:
        # Parse size
        size_bytes = model.get("size", 0)
        if size_bytes > 1e9:
            size_str = f"{size_bytes / 1e9:.1f} GB"
        elif size_bytes > 1e6:
            size_str = f"{size_bytes / 1e6:.1f} MB"
        else:
            size_str = f"{size_bytes} bytes"
        
        # Parse date
        modified = model.get("modified_at", "")[:19] if model.get("modified_at") else "Unknown"
        
        # Parse family
        family = model.get("details", {}).get("family", "Unknown")
        
        table.add_row(
            model["name"],
            size_str,
            modified,
            family
        )
    
    console.print(table)


@app.command("test")
def test_model(
    model: str = typer.Argument(..., help="Model to test (e.g., qwen3, ollama/qwen3)"),
    prompt: str = typer.Option("Hello, how are you?", "--prompt", "-p", help="Test prompt"),
    max_tokens: int = typer.Option(50, "--max-tokens", help="Maximum tokens to generate")
):
    """Test a specific Ollama model with a prompt"""
    
    rprint(f"🧪 [bold blue]Testing Model: {model}[/bold blue]")
    rprint(f"📝 Prompt: [dim]{prompt}[/dim]")
    rprint("=" * 50)
    
    # Initialize model
    success, lm_instance, message = safe_init_ollama(model)
    if not success:
        rprint(f"[red]❌ {message}[/red]")
        raise typer.Exit(1)
    
    rprint(f"[green]✅ {message}[/green]")
    
    try:
        # Test with DSPy
        import dspy
        
        # Simple test generation
        with console.status("[bold green]Generating response..."):
            # Create a simple signature for testing
            class TestSignature(dspy.Signature):
                """Generate a helpful response to the user's input."""
                input = dspy.InputField()
                output = dspy.OutputField()
            
            # Use chain of thought
            generator = dspy.ChainOfThought(TestSignature)
            response = generator(input=prompt)
        
        # Display response
        response_panel = Panel(
            response.output,
            title="🤖 Model Response",
            border_style="green"
        )
        console.print(response_panel)
        
        rprint(f"\n[green]✅ Model test completed successfully![/green]")
        
    except Exception as e:
        rprint(f"[red]❌ Model test failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("config")
def show_config(
    create_env: bool = typer.Option(False, "--create-env", help="Create environment template"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for env template")
):
    """Show current Ollama configuration"""
    
    validator = OllamaValidator()
    config = validator.config
    
    if create_env:
        output_path = Path(output_file) if output_file else None
        result = validator.create_env_template(output_path)
        rprint(f"[green]✅ {result}[/green]")
        return
    
    # Display current configuration
    config_table = Table(title="Current Ollama Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Source", style="dim")
    
    import os
    
    settings = [
        ("Base URL", config.base_url, "OLLAMA_BASE_URL" if os.getenv("OLLAMA_BASE_URL") else "default"),
        ("Default Model", config.default_model, "OLLAMA_DEFAULT_MODEL" if os.getenv("OLLAMA_DEFAULT_MODEL") else "default"),
        ("Timeout", f"{config.timeout}s", "OLLAMA_TIMEOUT" if os.getenv("OLLAMA_TIMEOUT") else "default"),
        ("Max Retries", str(config.max_retries), "OLLAMA_MAX_RETRIES" if os.getenv("OLLAMA_MAX_RETRIES") else "default"),
    ]
    
    for setting, value, source in settings:
        config_table.add_row(setting, value, source)
    
    console.print(config_table)
    
    # Show environment variables
    rprint("\n📋 [bold]Environment Variables:[/bold]")
    env_vars = ["OLLAMA_BASE_URL", "OLLAMA_DEFAULT_MODEL", "OLLAMA_TIMEOUT", "OLLAMA_MAX_RETRIES", "OLLAMA_API_KEY"]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            rprint(f"  ✅ {var}={value}")
        else:
            rprint(f"  ⚪ {var}=<not set>")


@app.command("fix")
def auto_fix(
    pull_model: bool = typer.Option(True, "--pull/--no-pull", help="Automatically pull missing models"),
    model: Optional[str] = typer.Option(None, "--model", help="Specific model to pull")
):
    """Automatically fix common Ollama issues"""
    
    rprint("🔧 [bold blue]Auto-fixing Ollama Issues[/bold blue]")
    rprint("=" * 50)
    
    validator = OllamaValidator()
    validation = validator.validate_configuration()
    
    if not validation["server_available"]:
        rprint("[red]❌ Ollama server not available[/red]")
        rprint("Please start Ollama server manually:")
        rprint("  [cyan]ollama serve[/cyan]")
        raise typer.Exit(1)
    
    if not validation["default_model_available"] and pull_model:
        target_model = model or validator.config.default_model.replace("ollama/", "")
        
        rprint(f"📥 [yellow]Pulling model: {target_model}[/yellow]")
        
        import subprocess
        try:
            result = subprocess.run(
                ["ollama", "pull", target_model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                rprint(f"[green]✅ Successfully pulled {target_model}[/green]")
            else:
                rprint(f"[red]❌ Failed to pull {target_model}[/red]")
                rprint(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            rprint(f"[yellow]⚠️ Pull operation timed out for {target_model}[/yellow]")
        except FileNotFoundError:
            rprint("[red]❌ ollama command not found[/red]")
            rprint("Please install Ollama from: https://ollama.com/download")
    
    # Re-validate after fixes
    rprint("\n🔍 [bold]Re-validating configuration...[/bold]")
    validation = validator.validate_configuration()
    
    if all([validation["server_available"], validation["models_accessible"], validation["default_model_available"]]):
        rprint("[green]✅ All issues resolved![/green]")
    else:
        rprint("[yellow]⚠️ Some issues remain. Run 'dsl ollama check --verbose' for details[/yellow]")


@app.command("benchmark")
def benchmark_model(
    model: str = typer.Option("qwen3", "--model", "-m", help="Model to benchmark"),
    iterations: int = typer.Option(5, "--iterations", "-i", help="Number of test iterations"),
    prompt: str = typer.Option("Generate a hello world program in Python.", "--prompt", help="Benchmark prompt")
):
    """Benchmark Ollama model performance"""
    
    rprint(f"⏱️ [bold blue]Benchmarking Model: {model}[/bold blue]")
    rprint(f"🔁 Iterations: {iterations}")
    rprint("=" * 50)
    
    # Initialize model
    success, lm_instance, message = safe_init_ollama(model)
    if not success:
        rprint(f"[red]❌ {message}[/red]")
        raise typer.Exit(1)
    
    import time
    import statistics
    
    times = []
    tokens = []
    
    try:
        import dspy
        
        class BenchmarkSignature(dspy.Signature):
            """Generate code based on the user's request."""
            request = dspy.InputField()
            code = dspy.OutputField()
        
        generator = dspy.ChainOfThought(BenchmarkSignature)
        
        for i in range(iterations):
            with console.status(f"[bold green]Running iteration {i+1}/{iterations}..."):
                start_time = time.time()
                response = generator(request=prompt)
                end_time = time.time()
                
                duration = end_time - start_time
                times.append(duration)
                tokens.append(len(response.code.split()))
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        avg_tokens = statistics.mean(tokens)
        tokens_per_sec = avg_tokens / avg_time
        
        # Display results
        results_table = Table(title="Benchmark Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Average Response Time", f"{avg_time:.2f}s")
        results_table.add_row("Min Response Time", f"{min_time:.2f}s")
        results_table.add_row("Max Response Time", f"{max_time:.2f}s")
        results_table.add_row("Average Token Count", f"{avg_tokens:.1f}")
        results_table.add_row("Tokens per Second", f"{tokens_per_sec:.1f}")
        
        console.print(results_table)
        
        rprint(f"\n[green]✅ Benchmark completed successfully![/green]")
        
    except Exception as e:
        rprint(f"[red]❌ Benchmark failed: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()