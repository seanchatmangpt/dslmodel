#!/usr/bin/env python3
"""
Evolution System CLI - Generated from Weaver Forge
==================================================

Demonstrates the complete Weaver Forge pipeline:
1. Semantic conventions defined in evolution_system_spec.py
2. Code generation via Weaver Forge E2E
3. Working CLI with telemetry integration
4. Worktree pipeline support
"""

import typer
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

try:
    from .evolution_system_fixed import EvolutionSystem
except ImportError:
    # Allow running as standalone script
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from evolution_system_fixed import EvolutionSystem


app = typer.Typer(name="evolution", help="Evolution System with Weaver Forge telemetry")
console = Console()


@app.command()
def status():
    """Show evolution system status"""
    console.print("🧬 Evolution System Status")
    console.print("=" * 30)
    
    system = EvolutionSystem()
    status_data = system.get_status()
    
    status_table = Table(title="📊 System Status")
    status_table.add_column("Component", style="cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Trace ID", status_data["trace_id"])
    status_table.add_row("Uptime", f"{status_data['uptime_seconds']}s")
    status_table.add_row("Repository", status_data["repository_path"])
    status_table.add_row("Spans Available", str(status_data["spans_available"]))
    status_table.add_row("Initialized", "✅" if status_data["initialized"] else "❌")
    
    console.print(status_table)


@app.command()
def analyze(
    analysis_type: str = typer.Option("full_analysis", help="Type of analysis to perform"),
    session_id: Optional[str] = typer.Option(None, help="Evolution session ID")
):
    """Run evolution analysis with telemetry"""
    console.print("🔍 Running Evolution Analysis")
    
    system = EvolutionSystem()
    
    if not session_id:
        session_id = system.start_evolution_session()
        console.print(f"📅 Started session: {session_id}")
    
    # Mock analysis with telemetry
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Analyzing system...", total=100)
        
        # Simulate analysis work
        for i in range(100):
            time.sleep(0.02)  # Simulate work
            progress.update(task, advance=1)
        
        analysis_duration = int((time.time() - start_time) * 1000)
        
        # Emit telemetry
        result = system.emit_analyze(
            session_id=session_id,
            analysis_type=analysis_type,
            issues_found=3,  # Mock issues found
            analysis_duration_ms=analysis_duration
        )
    
    console.print(Panel(
        f"📊 Analysis Type: {analysis_type}\n"
        f"🔍 Issues Found: {result['issues_found']}\n"
        f"⏱️  Duration: {analysis_duration}ms\n"
        f"📈 Span: {result['span_name']}\n"
        f"🆔 Session: {session_id}",
        title="✅ Analysis Complete"
    ))


@app.command()
def generate(
    session_id: str = typer.Argument(..., help="Evolution session ID"),
    improvement_type: str = typer.Option("performance_optimization", help="Type of improvement"),
    confidence: float = typer.Option(0.8, min=0.0, max=1.0, help="Confidence score"),
    priority: str = typer.Option("medium", help="Priority level")
):
    """Generate improvement recommendations with telemetry"""
    console.print("💡 Generating Improvements")
    
    system = EvolutionSystem()
    
    # Generate improvement ID
    improvement_id = f"imp_{session_id}_{int(time.time())}"
    
    # Emit telemetry
    result = system.emit_generate(
        session_id=session_id,
        improvement_id=improvement_id,
        improvement_type=improvement_type,
        confidence_score=confidence,
        priority=priority,
        estimated_effort_hours=4,
        target_files=["src/example.py", "tests/test_example.py"]
    )
    
    console.print(Panel(
        f"🆔 Improvement ID: {improvement_id}\n"
        f"🔧 Type: {improvement_type}\n"
        f"🎯 Confidence: {confidence:.1%}\n"
        f"⚡ Priority: {priority}\n"
        f"📈 Span: {result['span_name']}\n"
        f"🆔 Session: {session_id}",
        title="✅ Improvement Generated"
    ))


@app.command()
def apply(
    session_id: str = typer.Argument(..., help="Evolution session ID"),
    improvement_id: str = typer.Argument(..., help="Improvement ID to apply"),
    mode: str = typer.Option("automatic", help="Application mode"),
    dry_run: bool = typer.Option(False, help="Dry run mode")
):
    """Apply improvement with telemetry"""
    console.print("🚀 Applying Improvement")
    
    system = EvolutionSystem()
    
    # Simulate application
    application_result = "success" if not dry_run else "dry_run"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Applying improvement...", total=100)
        
        for i in range(100):
            time.sleep(0.01)
            progress.update(task, advance=1)
    
    # Emit telemetry
    result = system.emit_apply(
        session_id=session_id,
        improvement_id=improvement_id,
        application_mode=mode,
        application_result=application_result,
        files_modified=["src/optimized.py"] if not dry_run else [],
        application_duration_ms=1000
    )
    
    console.print(Panel(
        f"🆔 Improvement ID: {improvement_id}\n"
        f"🔧 Mode: {mode}\n"
        f"✅ Result: {application_result}\n"
        f"📁 Files Modified: {len(result.get('files_modified', []))}\n"
        f"📈 Span: {result['span_name']}\n"
        f"🆔 Session: {session_id}",
        title="✅ Application Complete"
    ))


@app.command()
def validate(
    session_id: str = typer.Argument(..., help="Evolution session ID"),
    improvement_id: str = typer.Argument(..., help="Improvement ID to validate"),
    validation_type: str = typer.Option("test_execution", help="Type of validation")
):
    """Validate improvement with telemetry"""
    console.print("🧪 Validating Improvement")
    
    system = EvolutionSystem()
    
    # Mock validation metrics
    metrics_before = '{"test_duration": 45.2, "memory_usage": 128}'
    metrics_after = '{"test_duration": 32.1, "memory_usage": 115}'
    performance_improvement = 0.29  # 29% improvement
    
    # Emit telemetry
    result = system.emit_validate(
        session_id=session_id,
        improvement_id=improvement_id,
        validation_type=validation_type,
        validation_result="passed",
        metrics_before=metrics_before,
        metrics_after=metrics_after,
        performance_improvement=performance_improvement
    )
    
    console.print(Panel(
        f"🆔 Improvement ID: {improvement_id}\n"
        f"🧪 Validation Type: {validation_type}\n"
        f"✅ Result: {result['validation_result']}\n"
        f"📈 Performance Gain: {performance_improvement:.1%}\n"
        f"📊 Span: {result['span_name']}\n"
        f"🆔 Session: {session_id}",
        title="✅ Validation Complete"
    ))


@app.command()
def full_cycle():
    """Run complete evolution cycle with Weaver Forge telemetry"""
    console.print("🧬 Complete Evolution Cycle")
    console.print("=" * 35)
    
    system = EvolutionSystem()
    
    try:
        # Run full cycle (but handle the span.name issue)
        result = system.run_full_evolution_cycle()
        
        if result["success"]:
            console.print(Panel(
                f"✅ Evolution Successful!\n"
                f"🆔 Session: {result['session_id']}\n"
                f"🔍 Issues Found: {result['issues_found']}\n"
                f"💡 Improvements: {result['improvements_generated']}\n"
                f"⏱️  Duration: {result['total_duration_ms']}ms",
                title="🎉 Evolution Complete",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"❌ Evolution Failed\n"
                f"🆔 Session: {result['session_id']}\n"
                f"🐛 Error: {result['error']}\n"
                f"⏱️  Duration: {result['total_duration_ms']}ms",
                title="💥 Evolution Error",
                border_style="red"
            ))
    
    except Exception as e:
        console.print(Panel(
            f"💥 Unexpected error: {str(e)}\n"
            "This may be due to OTEL configuration",
            title="❌ System Error",
            border_style="red"
        ))


@app.command()
def worktree_demo():
    """Demonstrate evolution with worktree pipeline"""
    console.print("🌿 Evolution Worktree Demo")
    console.print("=" * 30)
    
    system = EvolutionSystem()
    session_id = system.start_evolution_session()
    
    # Mock worktree workflow
    worktree_id = f"wt_{session_id}"
    
    console.print("1️⃣ Creating worktree for isolated testing...")
    result1 = system.emit_worktree(
        session_id=session_id,
        worktree_id=worktree_id,
        worktree_action="create",
        branch_name=f"evolution-{session_id}",
        isolation_level="full"
    )
    
    console.print("2️⃣ Running tests in isolated environment...")
    result2 = system.emit_worktree(
        session_id=session_id,
        worktree_id=worktree_id,
        worktree_action="test",
        test_results='{"passed": 45, "failed": 2, "duration": 23.5}'
    )
    
    console.print("3️⃣ Validating improvements...")
    result3 = system.emit_worktree(
        session_id=session_id,
        worktree_id=worktree_id,
        worktree_action="validate"
    )
    
    console.print("4️⃣ Merging successful improvements...")
    result4 = system.emit_worktree(
        session_id=session_id,
        worktree_id=worktree_id,
        worktree_action="merge"
    )
    
    console.print(Panel(
        f"🌿 Worktree Pipeline Complete\n"
        f"🆔 Session: {session_id}\n"
        f"🌳 Worktree: {worktree_id}\n"
        f"✅ All phases completed with telemetry\n"
        f"📊 4 worktree spans emitted",
        title="🎉 Worktree Demo Success",
        border_style="green"
    ))


if __name__ == "__main__":
    app()