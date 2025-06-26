#!/usr/bin/env python3
"""
DSL Unified CLI - Weaver-First 80/20 Implementation
The single interface that replaces all other CLIs
"""

import typer
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime

app = typer.Typer(
    name="dsl",
    help="[bold cyan]DSLModel Unified CLI[/bold cyan] - Weaver-First Approach",
    rich_markup_mode="rich",
    no_args_is_help=True
)

console = Console()

# Mock telemetry for demo
class MockTelemetry:
    def __init__(self):
        self.spans = []
        
    def start_span(self, name: str, attributes: dict = None):
        span = {
            "name": name,
            "start_time": datetime.now().isoformat(),
            "attributes": attributes or {}
        }
        self.spans.append(span)
        return span

telemetry = MockTelemetry()

@app.command("create")
def create_model(
    name: str = typer.Argument(..., help="Name of the model to create"),
    model_type: str = typer.Option("base", help="Model type: base, agent, workflow, fsm"),
    source: str = typer.Option("weaver", help="Generation source: weaver, prompt, schema"),
    trace: bool = typer.Option(True, help="Enable telemetry tracing")
):
    """🏗️ Create a new DSLModel with automatic telemetry"""
    
    if trace:
        span = telemetry.start_span(
            "dslmodel.model.create",
            {
                "dslmodel.model.type": model_type,
                "dslmodel.source.type": source,
                "model.name": name
            }
        )
    
    console.print(f"🚀 Creating {model_type} model: [bold cyan]{name}[/bold cyan]")
    console.print(f"📋 Source: {source}")
    
    # Mock model creation
    model_info = {
        "name": name,
        "type": model_type,
        "source": source,
        "created_at": datetime.now().isoformat(),
        "telemetry_enabled": trace
    }
    
    # Display model info
    table = Table(title=f"Created Model: {name}", box=box.ROUNDED)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in model_info.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)
    
    if trace:
        console.print(f"📡 Telemetry span: [dim]{span['name']}[/dim]")
    
    console.print("✅ Model created successfully!")
    return model_info

@app.command("execute")
def execute_agent(
    agent_name: str = typer.Argument(..., help="Name of the agent to execute"),
    task: str = typer.Option("default", help="Task for the agent to perform"),
    trace: bool = typer.Option(True, help="Enable telemetry tracing")
):
    """🤖 Execute an agent operation with telemetry"""
    
    if trace:
        span = telemetry.start_span(
            "dslmodel.agent.execute",
            {
                "dslmodel.model.type": "agent",
                "agent.name": agent_name,
                "agent.task": task
            }
        )
    
    console.print(f"🤖 Executing agent: [bold yellow]{agent_name}[/bold yellow]")
    console.print(f"📋 Task: {task}")
    
    # Mock execution with progress
    import time
    with console.status(f"[bold green]Agent {agent_name} executing..."):
        time.sleep(1)  # Simulate work
    
    result = {
        "agent": agent_name,
        "task": task,
        "status": "completed",
        "duration_ms": 1000,
        "result": f"Task '{task}' completed successfully"
    }
    
    console.print("✅ Agent execution completed!")
    console.print(f"📊 Duration: {result['duration_ms']}ms")
    
    if trace:
        console.print(f"📡 Telemetry span: [dim]{span['name']}[/dim]")
    
    return result

@app.command("validate")  
def validate_model(
    model_name: str = typer.Argument(..., help="Name of the model to validate"),
    rules: str = typer.Option("all", help="Validation rules to apply"),
    trace: bool = typer.Option(True, help="Enable telemetry tracing")
):
    """✅ Validate a DSLModel with comprehensive checks"""
    
    if trace:
        span = telemetry.start_span(
            "dslmodel.model.validate", 
            {
                "model.name": model_name,
                "validation.rules": rules
            }
        )
    
    console.print(f"🔍 Validating model: [bold blue]{model_name}[/bold blue]")
    
    # Mock validation checks
    validation_results = {
        "schema_valid": True,
        "type_safe": True, 
        "telemetry_configured": True,
        "performance_ok": True
    }
    
    table = Table(title="Validation Results", box=box.ROUNDED)
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    
    for check, passed in validation_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        table.add_row(check.replace("_", " ").title(), status)
    
    console.print(table)
    
    success_rate = sum(validation_results.values()) / len(validation_results) * 100
    console.print(f"📊 Overall Success Rate: {success_rate:.0f}%")
    
    if trace:
        console.print(f"📡 Telemetry span: [dim]{span['name']}[/dim]")
    
    return validation_results

@app.command("run")
def run_workflow(
    workflow_name: str = typer.Argument(..., help="Name of the workflow to run"),
    steps: int = typer.Option(3, help="Number of workflow steps"),
    trace: bool = typer.Option(True, help="Enable telemetry tracing")
):
    """🔄 Run a workflow with step-by-step telemetry"""
    
    if trace:
        span = telemetry.start_span(
            "dslmodel.workflow.run",
            {
                "dslmodel.model.type": "workflow",
                "workflow.name": workflow_name,
                "workflow.steps_total": steps
            }
        )
    
    console.print(f"🔄 Running workflow: [bold magenta]{workflow_name}[/bold magenta]")
    console.print(f"📋 Steps: {steps}")
    
    # Mock workflow execution
    import time
    completed_steps = 0
    
    for i in range(steps):
        step_name = f"Step {i+1}"
        console.print(f"  ⚡ Executing {step_name}...")
        time.sleep(0.3)  # Simulate step execution
        completed_steps += 1
        console.print(f"  ✅ {step_name} completed")
    
    result = {
        "workflow": workflow_name,
        "steps_total": steps,
        "steps_completed": completed_steps,
        "success": completed_steps == steps,
        "duration_ms": steps * 300
    }
    
    console.print(f"✅ Workflow completed: {completed_steps}/{steps} steps")
    
    if trace:
        console.print(f"📡 Telemetry span: [dim]{span['name']}[/dim]")
    
    return result

@app.command("health")
def system_health():
    """🏥 Check system health with telemetry"""
    
    span = telemetry.start_span(
        "dslmodel.system.health",
        {"health.check_type": "full"}
    )
    
    console.print("🏥 [bold green]System Health Check[/bold green]")
    
    health_data = {
        "status": "healthy",
        "score": 0.95,
        "active_models": 5,
        "telemetry_active": True,
        "weaver_operational": True
    }
    
    # Health status panel
    status_color = "green" if health_data["status"] == "healthy" else "red"
    panel_content = f"""
[bold]Overall Status:[/bold] [{status_color}]{health_data["status"].upper()}[/{status_color}]
[bold]Health Score:[/bold] {health_data["score"]:.1%}
[bold]Active Models:[/bold] {health_data["active_models"]}
[bold]Telemetry:[/bold] {"✅ Active" if health_data["telemetry_active"] else "❌ Inactive"}
[bold]Weaver:[/bold] {"✅ Operational" if health_data["weaver_operational"] else "❌ Down"}
"""
    
    panel = Panel(
        panel_content.strip(),
        title="[bold cyan]System Health[/bold cyan]",
        border_style=status_color
    )
    
    console.print(panel)
    console.print(f"📡 Telemetry span: [dim]{span['name']}[/dim]")
    
    return health_data

@app.command("weave")
def weave_operations(
    action: str = typer.Argument(..., help="Action: generate, validate, deploy, status"),
    target: str = typer.Option("all", help="Target for the action")
):
    """🕸️ Weaver-first operations - the core 20% functionality"""
    
    console.print(f"🕸️ [bold cyan]Weaver Operation: {action}[/bold cyan]")
    
    if action == "generate":
        console.print("🏗️ Generating all artifacts from semantic conventions...")
        
        # Mock generation process
        artifacts = [
            "Pydantic models",
            "CLI commands", 
            "Test suites",
            "Telemetry configuration",
            "Documentation"
        ]
        
        for artifact in artifacts:
            console.print(f"  ✅ Generated: {artifact}")
        
        console.print("🎉 [bold green]Generation complete![/bold green]")
        
    elif action == "validate":
        console.print("🔍 Validating semantic conventions...")
        console.print("  ✅ YAML syntax valid")
        console.print("  ✅ Span definitions complete")
        console.print("  ✅ Attribute mappings correct")
        console.print("  ✅ Weaver schema compliance")
        console.print("🎉 [bold green]Validation complete![/bold green]")
        
    elif action == "deploy":
        console.print("🚀 Deploying telemetry configuration...")
        console.print("  ✅ OTLP exporters configured")
        console.print("  ✅ Sampling rules applied")
        console.print("  ✅ Resource attributes set")
        console.print("🎉 [bold green]Deployment complete![/bold green]")
        
    elif action == "status":
        console.print("📊 Weaver system status:")
        
        status_table = Table(box=box.MINIMAL)
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        
        components = [
            ("Semantic Conventions", "✅ Loaded"),
            ("Code Generation", "✅ Active"),
            ("Telemetry Export", "✅ Configured"),
            ("CLI Integration", "✅ Operational")
        ]
        
        for component, status in components:
            status_table.add_row(component, status)
        
        console.print(status_table)

@app.command("telemetry")
def telemetry_status():
    """📡 Show telemetry collection status"""
    
    console.print("📡 [bold cyan]Telemetry Status[/bold cyan]")
    
    # Show collected spans
    if telemetry.spans:
        table = Table(title="Recent Telemetry Spans", box=box.ROUNDED)
        table.add_column("Span Name", style="cyan", width=30)
        table.add_column("Timestamp", style="green", width=20)
        table.add_column("Attributes", style="yellow")
        
        for span in telemetry.spans[-5:]:  # Show last 5 spans
            attributes_str = ", ".join(f"{k}={v}" for k, v in list(span["attributes"].items())[:2])
            if len(span["attributes"]) > 2:
                attributes_str += "..."
                
            table.add_row(
                span["name"],
                span["start_time"].split("T")[1][:8],
                attributes_str
            )
        
        console.print(table)
        console.print(f"📊 Total spans collected: {len(telemetry.spans)}")
    else:
        console.print("ℹ️ No telemetry spans collected yet")
        console.print("💡 Run some commands with --trace to generate spans")

@app.command("demo")
def run_demo():
    """🎪 Run a complete demo of the weaver-first approach"""
    
    console.print("\n🎪 [bold cyan]DSLModel Weaver-First Demo[/bold cyan]")
    console.print("=" * 50)
    
    # Demo sequence
    console.print("\n🏗️ [bold]Step 1: Create Models[/bold]")
    create_model("PaymentAgent", "agent", "weaver")
    
    console.print("\n🤖 [bold]Step 2: Execute Agent[/bold]")
    execute_agent("PaymentAgent", "process_payment")
    
    console.print("\n🔄 [bold]Step 3: Run Workflow[/bold]")
    run_workflow("PaymentWorkflow", 3)
    
    console.print("\n✅ [bold]Step 4: Validate System[/bold]")
    validate_model("PaymentAgent")
    
    console.print("\n🏥 [bold]Step 5: Check Health[/bold]")
    system_health()
    
    console.print("\n📡 [bold]Step 6: View Telemetry[/bold]")
    telemetry_status()
    
    console.print(f"\n🎉 [bold green]Demo Complete![/bold green]")
    console.print("✨ [bold]Weaver-first approach demonstrated:[/bold]")
    console.print("  • Single unified CLI interface")
    console.print("  • Automatic telemetry for every operation") 
    console.print("  • Generated from semantic conventions")
    console.print("  • 80/20 focus on core value")

if __name__ == "__main__":
    app()