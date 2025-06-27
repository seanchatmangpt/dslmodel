"""
Git Hook Pipeline Integration for Forge Validation
Connects Git hooks to Weaver/OTEL ecosystem for comprehensive validation
"""

import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from opentelemetry import trace
from opentelemetry.trace import Span
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from dslmodel.core.weaver_engine import WeaverEngine
from dslmodel.validation.weaver_otel_validator import WeaverOtelValidator

console = Console()
tracer = trace.get_tracer(__name__)

class GitHookPipeline:
    """Git hook pipeline for comprehensive validation and automation"""
    
    def __init__(self):
        self.weaver = WeaverEngine()
        self.validator = WeaverOtelValidator()
        self.hook_configs = self._load_hook_configs()
    
    def _load_hook_configs(self) -> Dict[str, Any]:
        """Load hook pipeline configurations"""
        try:
            with open("git_registry.yaml", 'r') as f:
                registry = yaml.safe_load(f)
                return registry.get("hook_pipeline", {})
        except FileNotFoundError:
            return self._default_hook_configs()
    
    def _default_hook_configs(self) -> Dict[str, Any]:
        """Default hook pipeline configuration"""
        return {
            "pre_commit": {
                "validators": [
                    "forge validate",
                    "ruff check --fix",
                    "pytest tests/essential/"
                ],
                "span": "git.hook.run"
            },
            "pre_push": {
                "validators": [
                    "weaver registry check", 
                    "dsl health-8020 analyze"
                ],
                "span": "git.hook.run"
            },
            "post_commit": {
                "actions": [
                    "dsl otel-monitor emit-commit"
                ],
                "span": "git.hook.run"
            }
        }
    
    def _emit_hook_span(self, hook_type: str, command: str, exit_code: int, 
                       duration_ms: int, files_checked: Optional[int] = None) -> str:
        """Emit telemetry span for hook execution"""
        with tracer.start_as_current_span("git.hook.run") as span:
            span.set_attribute("git.hook.type", hook_type)
            span.set_attribute("git.hook.script", command)
            span.set_attribute("git.hook.exit_code", exit_code)
            span.set_attribute("git.hook.duration_ms", duration_ms)
            
            if files_checked is not None:
                span.set_attribute("git.hook.files_checked", files_checked)
            
            # Determine validation type
            if "forge" in command.lower():
                span.set_attribute("git.hook.validation_type", "forge")
                span.set_attribute("forge.validation_result", exit_code == 0)
            elif "ruff" in command.lower():
                span.set_attribute("git.hook.validation_type", "lint")
            elif "pytest" in command.lower():
                span.set_attribute("git.hook.validation_type", "test")
            elif "weaver" in command.lower():
                span.set_attribute("git.hook.validation_type", "weaver")
            elif "health" in command.lower():
                span.set_attribute("git.hook.validation_type", "health")
            
            return span.get_span_context().trace_id
    
    def _run_command_with_telemetry(self, command: str, hook_type: str) -> Tuple[int, str, str, int]:
        """Run command with telemetry collection"""
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Emit telemetry span
            self._emit_hook_span(
                hook_type, command, result.returncode, duration_ms
            )
            
            return result.returncode, result.stdout, result.stderr, duration_ms
            
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            self._emit_hook_span(hook_type, command, -1, duration_ms)
            return -1, "", "Command timed out", duration_ms
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._emit_hook_span(hook_type, command, -2, duration_ms)
            return -2, "", str(e), duration_ms
    
    def run_validation_pipeline(self, hook_type: str, 
                              commands: Optional[List[str]] = None) -> bool:
        """Run complete validation pipeline for hook type"""
        if commands is None:
            hook_config = self.hook_configs.get(hook_type, {})
            commands = hook_config.get("validators", []) + hook_config.get("actions", [])
        
        if not commands:
            console.print(f"⚠️ No commands configured for {hook_type}")
            return True
        
        console.print(f"🔧 Running {hook_type} validation pipeline...")
        
        results = []
        total_success = True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for i, command in enumerate(commands, 1):
                task = progress.add_task(f"Running: {command}", total=1)
                
                exit_code, stdout, stderr, duration = self._run_command_with_telemetry(
                    command, hook_type
                )
                
                success = exit_code == 0
                total_success = total_success and success
                
                results.append({
                    "command": command,
                    "exit_code": exit_code,
                    "success": success,
                    "duration_ms": duration,
                    "stdout": stdout[:500],  # Truncate for display
                    "stderr": stderr[:500]
                })
                
                if success:
                    progress.update(task, completed=1, description=f"✅ {command}")
                else:
                    progress.update(task, completed=1, description=f"❌ {command}")
                    if stderr:
                        console.print(f"[red]Error in {command}:[/red] {stderr[:200]}")
        
        # Summary
        self._display_pipeline_results(hook_type, results, total_success)
        
        return total_success
    
    def _display_pipeline_results(self, hook_type: str, results: List[Dict], 
                                 total_success: bool):
        """Display pipeline execution results"""
        table = Table(title=f"{hook_type.replace('_', '-').title()} Pipeline Results")
        table.add_column("Command", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Duration", style="yellow")
        table.add_column("Exit Code", style="dim")
        
        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = f"{result['duration_ms']}ms"
            
            table.add_row(
                result["command"][:40] + "..." if len(result["command"]) > 40 else result["command"],
                status,
                duration,
                str(result["exit_code"])
            )
        
        console.print(table)
        
        if total_success:
            console.print(f"\n✅ {hook_type} pipeline completed successfully")
        else:
            console.print(f"\n❌ {hook_type} pipeline failed")
    
    def install_hook_script(self, hook_type: str) -> bool:
        """Install optimized hook script for pipeline execution"""
        hook_path = Path(f".git/hooks/{hook_type}")
        
        # Create hook script that calls this pipeline
        hook_script = f"""#!/bin/bash
# Auto-generated Git hook for {hook_type}
# Executes validation pipeline with telemetry

set -e

echo "🔧 Executing {hook_type} validation pipeline..."

# Run pipeline through DSLModel
if command -v uv &> /dev/null; then
    uv run python -m dslmodel.commands.git_hook_pipeline run-pipeline {hook_type}
else
    python -m dslmodel.commands.git_hook_pipeline run-pipeline {hook_type}
fi

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ {hook_type} validation passed"
else
    echo "❌ {hook_type} validation failed"
    exit $exit_code
fi
"""
        
        try:
            hook_path.parent.mkdir(exist_ok=True)
            hook_path.write_text(hook_script)
            hook_path.chmod(0o755)
            
            console.print(f"✅ Hook installed: {hook_type}")
            return True
            
        except Exception as e:
            console.print(f"❌ Hook installation failed: {e}")
            return False
    
    def install_all_hooks(self) -> bool:
        """Install all configured validation hooks"""
        success = True
        
        for hook_type in self.hook_configs.keys():
            if not self.install_hook_script(hook_type):
                success = False
        
        return success
    
    def validate_forge_integration(self) -> bool:
        """Validate forge integration with hook pipeline"""
        try:
            # Test forge validation
            console.print("🔧 Testing forge validation integration...")
            
            # Run basic forge validation
            exit_code, stdout, stderr, duration = self._run_command_with_telemetry(
                "forge validate", "test"
            )
            
            if exit_code == 0:
                console.print("✅ Forge validation integration working")
                return True
            else:
                console.print(f"❌ Forge validation failed: {stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Forge integration test failed: {e}")
            return False
    
    def validate_weaver_integration(self) -> bool:
        """Validate Weaver integration with hook pipeline"""
        try:
            # Test Weaver validation
            console.print("🔧 Testing Weaver validation integration...")
            
            # Run Weaver registry check
            exit_code, stdout, stderr, duration = self._run_command_with_telemetry(
                "weaver registry check", "test"
            )
            
            if exit_code == 0:
                console.print("✅ Weaver validation integration working")
                return True
            else:
                console.print(f"❌ Weaver validation failed: {stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Weaver integration test failed: {e}")
            return False
    
    def validate_otel_integration(self) -> bool:
        """Validate OTEL integration with hook pipeline"""
        try:
            # Test OTEL monitoring
            console.print("🔧 Testing OTEL integration...")
            
            # Run OTEL health check
            exit_code, stdout, stderr, duration = self._run_command_with_telemetry(
                "dsl otel-monitor status", "test"
            )
            
            if exit_code == 0:
                console.print("✅ OTEL integration working")
                return True
            else:
                console.print(f"❌ OTEL integration failed: {stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ OTEL integration test failed: {e}")
            return False
    
    def comprehensive_validation(self) -> Dict[str, bool]:
        """Run comprehensive validation of all integrations"""
        results = {
            "forge": self.validate_forge_integration(),
            "weaver": self.validate_weaver_integration(),
            "otel": self.validate_otel_integration()
        }
        
        # Display results
        table = Table(title="Integration Validation Results")
        table.add_column("Integration", style="cyan")
        table.add_column("Status", style="bold")
        
        for integration, success in results.items():
            status = "✅ WORKING" if success else "❌ FAILED"
            table.add_row(integration.upper(), status)
        
        console.print(table)
        
        all_success = all(results.values())
        if all_success:
            console.print("\n✅ All integrations validated successfully")
        else:
            console.print("\n❌ Some integrations failed validation")
        
        return results


# CLI interface
app = typer.Typer(name="git-hook-pipeline", help="Git hook pipeline for validation")
pipeline = GitHookPipeline()

@app.command("run-pipeline")
def run_pipeline(hook_type: str):
    """Run validation pipeline for specific hook type"""
    success = pipeline.run_validation_pipeline(hook_type)
    if not success:
        raise typer.Exit(1)

@app.command("install")
def install_hooks():
    """Install all validation hooks"""
    pipeline.install_all_hooks()

@app.command("validate")
def validate_integrations():
    """Validate all integrations"""
    results = pipeline.comprehensive_validation()
    if not all(results.values()):
        raise typer.Exit(1)

@app.command("test-hook")
def test_hook(hook_type: str):
    """Test specific hook type"""
    success = pipeline.run_validation_pipeline(hook_type)
    if not success:
        raise typer.Exit(1)

if __name__ == "__main__":
    app()