#!/usr/bin/env python3
"""
Weaver Global Health Check System

Comprehensive health checking using Weaver semantic conventions
and Ollama-powered validation to ensure OpenTelemetry specs match
Weaver requirements across the entire DSLModel ecosystem.
"""

import json
import time
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint

# Import our validation tools
from dslmodel.utils.ollama_validator import OllamaValidator, safe_init_ollama
from dslmodel.utils.dspy_tools import init_lm

console = Console()
app = typer.Typer(help="Weaver-based global health checks with Ollama validation")


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    duration_ms: float
    timestamp: datetime


@dataclass
class SystemHealth:
    """Overall system health assessment"""
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime


class WeaverHealthChecker:
    """Comprehensive health checker using Weaver + Ollama"""
    
    def __init__(self):
        self.console = console
        self.ollama_validator = OllamaValidator()
        self.semconv_registry = Path("semconv_registry")
        self.weaver_schemas = Path("weaver_schemas")
        self.health_results: List[HealthCheckResult] = []
        
    async def run_comprehensive_health_check(self) -> SystemHealth:
        """Run all health checks and return comprehensive results"""
        rprint("🔍 [bold blue]Starting Weaver Global Health Check[/bold blue]")
        rprint("=" * 60)
        
        start_time = time.time()
        
        # Run all health checks
        checks = [
            self._check_ollama_health(),
            self._check_weaver_installation(),
            self._check_semantic_conventions(),
            self._check_otel_compatibility(),
            self._check_llm_powered_validation(),
            self._check_generated_specs(),
            self._check_dslmodel_integration()
        ]
        
        # Wait for all checks to complete
        self.health_results = await asyncio.gather(*checks)
        
        # Calculate overall health
        overall_status = self._calculate_overall_health()
        summary = self._generate_summary()
        recommendations = self._generate_recommendations()
        
        total_duration = (time.time() - start_time) * 1000
        
        return SystemHealth(
            overall_status=overall_status,
            checks=self.health_results,
            summary=summary,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _check_ollama_health(self) -> HealthCheckResult:
        """Check Ollama server and model availability"""
        start_time = time.time()
        
        try:
            # Use our existing Ollama validator
            validation = self.ollama_validator.validate_configuration()
            
            if validation["server_available"] and validation["default_model_available"]:
                status = HealthStatus.HEALTHY
                message = "Ollama server and models available"
                details = {
                    "server_url": self.ollama_validator.config.base_url,
                    "default_model": self.ollama_validator.config.default_model,
                    "models_count": len(self.ollama_validator.get_available_models()[1]),
                    "validation_details": validation
                }
            elif validation["server_available"]:
                status = HealthStatus.WARNING
                message = "Ollama server available but model issues detected"
                details = {"validation_details": validation}
            else:
                status = HealthStatus.CRITICAL
                message = "Ollama server not available"
                details = {"validation_details": validation}
                
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Ollama health check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="Ollama Health",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_weaver_installation(self) -> HealthCheckResult:
        """Check if Weaver is properly installed and accessible"""
        start_time = time.time()
        
        try:
            # Check if weaver command exists
            result = subprocess.run(
                ["weaver", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                status = HealthStatus.HEALTHY
                message = f"Weaver installed and accessible"
                details = {
                    "version_output": result.stdout.strip(),
                    "command_available": True
                }
            else:
                status = HealthStatus.WARNING
                message = "Weaver command exists but returned error"
                details = {
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            status = HealthStatus.WARNING
            message = "Weaver command timed out"
            details = {"timeout": True}
            
        except FileNotFoundError:
            status = HealthStatus.CRITICAL
            message = "Weaver not installed or not in PATH"
            details = {
                "command_available": False,
                "install_instructions": "Install from: https://github.com/open-telemetry/weaver"
            }
            
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Weaver check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="Weaver Installation",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_semantic_conventions(self) -> HealthCheckResult:
        """Check semantic conventions registry"""
        start_time = time.time()
        
        try:
            # Check if semconv registry exists
            if not self.semconv_registry.exists():
                status = HealthStatus.WARNING
                message = "Semantic conventions registry not found"
                details = {
                    "registry_path": str(self.semconv_registry),
                    "exists": False
                }
            else:
                # Count YAML files
                yaml_files = list(self.semconv_registry.glob("**/*.yaml"))
                yaml_files.extend(list(self.semconv_registry.glob("**/*.yml")))
                
                if len(yaml_files) > 0:
                    status = HealthStatus.HEALTHY
                    message = f"Found {len(yaml_files)} semantic convention files"
                    details = {
                        "registry_path": str(self.semconv_registry),
                        "yaml_files_count": len(yaml_files),
                        "sample_files": [str(f) for f in yaml_files[:5]]
                    }
                else:
                    status = HealthStatus.WARNING
                    message = "Semantic conventions registry exists but no YAML files found"
                    details = {
                        "registry_path": str(self.semconv_registry),
                        "yaml_files_count": 0
                    }
                    
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Semantic conventions check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="Semantic Conventions",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_otel_compatibility(self) -> HealthCheckResult:
        """Check OpenTelemetry compatibility with Weaver"""
        start_time = time.time()
        
        try:
            # Try to validate with weaver if available
            if self.semconv_registry.exists():
                result = subprocess.run(
                    ["weaver", "registry", "check", "--registry", str(self.semconv_registry)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    status = HealthStatus.HEALTHY
                    message = "OpenTelemetry specs validated by Weaver"
                    details = {
                        "weaver_validation": "passed",
                        "stdout": result.stdout[:500],  # Limit output
                        "registry_path": str(self.semconv_registry)
                    }
                else:
                    status = HealthStatus.WARNING
                    message = "Weaver validation found issues"
                    details = {
                        "weaver_validation": "failed",
                        "returncode": result.returncode,
                        "stderr": result.stderr[:500],
                        "stdout": result.stdout[:500]
                    }
            else:
                status = HealthStatus.WARNING
                message = "Cannot validate - no semantic conventions registry"
                details = {"registry_missing": True}
                
        except subprocess.TimeoutExpired:
            status = HealthStatus.WARNING
            message = "Weaver validation timed out"
            details = {"timeout": True}
            
        except FileNotFoundError:
            status = HealthStatus.WARNING
            message = "Weaver not available for validation"
            details = {"weaver_missing": True}
            
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"OTEL compatibility check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="OTEL Compatibility",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_llm_powered_validation(self) -> HealthCheckResult:
        """Use Ollama LLM to validate semantic conventions content"""
        start_time = time.time()
        
        try:
            # Initialize LLM for validation
            success, lm, message = safe_init_ollama("ollama/qwen3")
            if not success:
                status = HealthStatus.WARNING
                message = f"LLM validation unavailable: {message}"
                details = {"llm_available": False}
            else:
                # Use LLM to analyze semantic conventions
                import dspy
                
                class SemanticValidation(dspy.Signature):
                    """Validate OpenTelemetry semantic conventions for completeness and consistency."""
                    conventions_content = dspy.InputField(desc="Semantic conventions YAML content")
                    validation_result = dspy.OutputField(desc="Validation assessment and recommendations")
                
                validator = dspy.ChainOfThought(SemanticValidation)
                
                # Get sample semantic convention content
                sample_content = self._get_sample_semconv_content()
                
                if sample_content:
                    with console.status("[bold green]LLM analyzing semantic conventions..."):
                        result = validator(conventions_content=sample_content)
                    
                    status = HealthStatus.HEALTHY
                    message = "LLM validation completed"
                    details = {
                        "llm_available": True,
                        "analysis_result": result.validation_result[:500],  # Limit length
                        "content_analyzed": len(sample_content),
                        "model_used": "qwen3"
                    }
                else:
                    status = HealthStatus.WARNING
                    message = "LLM available but no content to analyze"
                    details = {"llm_available": True, "content_available": False}
                    
        except Exception as e:
            status = HealthStatus.WARNING
            message = f"LLM validation failed: {str(e)}"
            details = {"error": str(e), "llm_available": False}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="LLM-Powered Validation",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_generated_specs(self) -> HealthCheckResult:
        """Check quality of generated specifications"""
        start_time = time.time()
        
        try:
            # Look for generated specifications
            generated_dirs = [
                Path("semconv_registry/generated"),
                Path("generated"),
                Path("output"),
                Path("demo_generated_feature")
            ]
            
            total_files = 0
            found_dirs = []
            
            for gen_dir in generated_dirs:
                if gen_dir.exists():
                    files = list(gen_dir.glob("**/*.yaml")) + list(gen_dir.glob("**/*.yml"))
                    files.extend(list(gen_dir.glob("**/*.py")))
                    total_files += len(files)
                    if files:
                        found_dirs.append(str(gen_dir))
            
            if total_files > 0:
                status = HealthStatus.HEALTHY
                message = f"Found {total_files} generated specification files"
                details = {
                    "generated_files_count": total_files,
                    "directories_with_content": found_dirs,
                    "file_types": ["yaml", "yml", "py"]
                }
            else:
                status = HealthStatus.WARNING
                message = "No generated specifications found"
                details = {
                    "generated_files_count": 0,
                    "searched_directories": [str(d) for d in generated_dirs]
                }
                
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Generated specs check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="Generated Specifications",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    async def _check_dslmodel_integration(self) -> HealthCheckResult:
        """Check DSLModel integration with OpenTelemetry"""
        start_time = time.time()
        
        try:
            # Check if DSLModel modules can be imported
            integration_modules = [
                "dslmodel.weaver.loader",
                "dslmodel.integrations.otel",
                "dslmodel.utils.ollama_validator",
                "dslmodel.commands.weaver_health_check"
            ]
            
            imported_modules = []
            failed_imports = []
            
            for module in integration_modules:
                try:
                    __import__(module)
                    imported_modules.append(module)
                except ImportError as e:
                    failed_imports.append(f"{module}: {str(e)}")
            
            if len(imported_modules) == len(integration_modules):
                status = HealthStatus.HEALTHY
                message = "All DSLModel integrations available"
                details = {
                    "imported_modules": imported_modules,
                    "integration_complete": True
                }
            elif len(imported_modules) > 0:
                status = HealthStatus.WARNING
                message = f"{len(imported_modules)}/{len(integration_modules)} integrations available"
                details = {
                    "imported_modules": imported_modules,
                    "failed_imports": failed_imports,
                    "integration_complete": False
                }
            else:
                status = HealthStatus.CRITICAL
                message = "DSLModel integrations not available"
                details = {
                    "imported_modules": [],
                    "failed_imports": failed_imports,
                    "integration_complete": False
                }
                
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"DSLModel integration check failed: {str(e)}"
            details = {"error": str(e)}
        
        duration = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name="DSLModel Integration",
            status=status,
            message=message,
            details=details,
            duration_ms=duration,
            timestamp=datetime.now()
        )
    
    def _get_sample_semconv_content(self) -> str:
        """Get sample semantic conventions content for LLM analysis"""
        try:
            # Look for YAML files in semconv registry
            if self.semconv_registry.exists():
                yaml_files = list(self.semconv_registry.glob("**/*.yaml"))
                yaml_files.extend(list(self.semconv_registry.glob("**/*.yml")))
                
                if yaml_files:
                    # Read first file found
                    content = yaml_files[0].read_text()
                    return content[:2000]  # Limit content size
            
            # Fallback: create sample content for analysis
            return """
groups:
  - id: trace.swarmsh
    type: span
    brief: SwarmSH agent coordination spans
    spans:
      - id: swarmsh.agent.create
        brief: Agent creation in swarm coordination
        attributes:
          - id: agent.id
            type: string
            requirement_level: required
            brief: Unique identifier for the agent
"""
        except Exception:
            return ""
    
    def _calculate_overall_health(self) -> HealthStatus:
        """Calculate overall system health from individual checks"""
        if not self.health_results:
            return HealthStatus.UNKNOWN
        
        critical_count = sum(1 for r in self.health_results if r.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for r in self.health_results if r.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            return HealthStatus.CRITICAL
        elif warning_count > 0:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate health check summary"""
        status_counts = {}
        for status in HealthStatus:
            status_counts[status.value] = sum(1 for r in self.health_results if r.status == status)
        
        avg_duration = sum(r.duration_ms for r in self.health_results) / len(self.health_results) if self.health_results else 0
        
        return {
            "total_checks": len(self.health_results),
            "status_distribution": status_counts,
            "average_duration_ms": avg_duration,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []
        
        for result in self.health_results:
            if result.status == HealthStatus.CRITICAL:
                if "Ollama" in result.name:
                    recommendations.append("🔧 Install and start Ollama server: https://ollama.com/download")
                    recommendations.append("📥 Pull required models: ollama pull qwen3")
                elif "Weaver" in result.name:
                    recommendations.append("🔧 Install Weaver: https://github.com/open-telemetry/weaver")
                elif "DSLModel" in result.name:
                    recommendations.append("📦 Install DSLModel dependencies: poetry install")
            
            elif result.status == HealthStatus.WARNING:
                if "Semantic" in result.name:
                    recommendations.append("📋 Generate semantic conventions: dsl forge build")
                elif "Generated" in result.name:
                    recommendations.append("🚀 Run feature generation: dsl forge e2e")
        
        # Add general recommendations
        if any(r.status != HealthStatus.HEALTHY for r in self.health_results):
            recommendations.append("🔍 Run detailed diagnostics: dsl weaver-health detailed")
            recommendations.append("📊 Check system logs for errors")
        
        return list(set(recommendations))  # Remove duplicates


@app.command("check")
def run_health_check(
    detailed: bool = typer.Option(False, "--detailed", help="Show detailed results"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    save_report: bool = typer.Option(False, "--save", help="Save report to file")
):
    """Run comprehensive Weaver + Ollama health check"""
    
    async def main():
        checker = WeaverHealthChecker()
        system_health = await checker.run_comprehensive_health_check()
        
        if json_output:
            # JSON output
            health_data = {
                "overall_status": system_health.overall_status.value,
                "summary": system_health.summary,
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "duration_ms": check.duration_ms,
                        "timestamp": check.timestamp.isoformat(),
                        "details": check.details if detailed else {}
                    }
                    for check in system_health.checks
                ],
                "recommendations": system_health.recommendations,
                "timestamp": system_health.timestamp.isoformat()
            }
            
            print(json.dumps(health_data, indent=2))
            
        else:
            # Rich terminal output
            _display_health_results(system_health, detailed)
        
        # Save report if requested
        if save_report:
            report_path = Path(f"weaver_health_report_{int(time.time())}.json")
            health_data = {
                "overall_status": system_health.overall_status.value,
                "summary": system_health.summary,
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "duration_ms": check.duration_ms,
                        "timestamp": check.timestamp.isoformat(),
                        "details": check.details
                    }
                    for check in system_health.checks
                ],
                "recommendations": system_health.recommendations,
                "timestamp": system_health.timestamp.isoformat()
            }
            
            with open(report_path, 'w') as f:
                json.dump(health_data, f, indent=2)
            
            rprint(f"[green]✅ Report saved to: {report_path}[/green]")
    
    asyncio.run(main())


def _display_health_results(system_health: SystemHealth, detailed: bool):
    """Display health check results with Rich formatting"""
    
    # Overall status panel
    status_color = {
        HealthStatus.HEALTHY: "green",
        HealthStatus.WARNING: "yellow", 
        HealthStatus.CRITICAL: "red",
        HealthStatus.UNKNOWN: "dim"
    }[system_health.overall_status]
    
    status_icon = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.WARNING: "⚠️",
        HealthStatus.CRITICAL: "❌", 
        HealthStatus.UNKNOWN: "❓"
    }[system_health.overall_status]
    
    overall_panel = Panel(
        f"[bold {status_color}]{status_icon} System Status: {system_health.overall_status.value.upper()}[/bold {status_color}]\n\n"
        f"Total Checks: {system_health.summary['total_checks']}\n"
        f"Average Duration: {system_health.summary['average_duration_ms']:.1f}ms",
        title="🔍 Weaver Health Check Results",
        border_style=status_color
    )
    
    console.print(overall_panel)
    
    # Individual check results table
    table = Table(title="Health Check Details")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Message", style="dim")
    table.add_column("Duration", style="green")
    
    for check in system_health.checks:
        status_display = f"{status_icon} {check.status.value}"
        table.add_row(
            check.name,
            status_display,
            check.message[:60] + "..." if len(check.message) > 60 else check.message,
            f"{check.duration_ms:.1f}ms"
        )
    
    console.print(table)
    
    # Show detailed information if requested
    if detailed:
        for check in system_health.checks:
            if check.details:
                details_panel = Panel(
                    json.dumps(check.details, indent=2),
                    title=f"🔍 {check.name} Details",
                    border_style="dim"
                )
                console.print(details_panel)
    
    # Recommendations
    if system_health.recommendations:
        rprint("\n💡 [bold yellow]Recommendations:[/bold yellow]")
        for rec in system_health.recommendations:
            rprint(f"  {rec}")


@app.command("monitor")
def monitor_health(
    interval: int = typer.Option(30, "--interval", help="Check interval in seconds"),
    continuous: bool = typer.Option(False, "--continuous", help="Run continuously")
):
    """Monitor system health continuously"""
    
    async def monitor_loop():
        checker = WeaverHealthChecker()
        
        while True:
            try:
                with console.status("[bold green]Running health checks..."):
                    system_health = await checker.run_comprehensive_health_check()
                
                # Clear screen and show results
                console.clear()
                _display_health_results(system_health, detailed=False)
                
                if not continuous:
                    break
                
                rprint(f"\n[dim]Next check in {interval} seconds... (Ctrl+C to stop)[/dim]")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                rprint("\n[yellow]Monitoring stopped by user[/yellow]")
                break
    
    asyncio.run(monitor_loop())


@app.command("validate")
def validate_with_llm(
    model: str = typer.Option("qwen3", "--model", help="Ollama model to use"),
    registry_path: Path = typer.Option(Path("semconv_registry"), "--registry", help="Semantic conventions registry path")
):
    """Use LLM to validate semantic conventions quality"""
    
    async def validate():
        rprint("🧠 [bold blue]LLM-Powered Semantic Convention Validation[/bold blue]")
        rprint("=" * 60)
        
        # Initialize LLM
        success, lm, message = safe_init_ollama(f"ollama/{model}")
        if not success:
            rprint(f"[red]❌ {message}[/red]")
            raise typer.Exit(1)
        
        rprint(f"[green]✅ {message}[/green]")
        
        # Find YAML files
        if not registry_path.exists():
            rprint(f"[red]❌ Registry path not found: {registry_path}[/red]")
            raise typer.Exit(1)
        
        yaml_files = list(registry_path.glob("**/*.yaml"))
        yaml_files.extend(list(registry_path.glob("**/*.yml")))
        
        if not yaml_files:
            rprint(f"[red]❌ No YAML files found in {registry_path}[/red]")
            raise typer.Exit(1)
        
        rprint(f"[cyan]Found {len(yaml_files)} YAML files to validate[/cyan]")
        
        # Validate each file with LLM
        import dspy
        
        class ConventionValidator(dspy.Signature):
            """Validate OpenTelemetry semantic conventions for completeness, consistency, and best practices."""
            yaml_content = dspy.InputField(desc="YAML semantic convention content")
            file_path = dspy.InputField(desc="File path for context")
            validation_report = dspy.OutputField(desc="Detailed validation report with issues and recommendations")
        
        validator = dspy.ChainOfThought(ConventionValidator)
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Validating files...", total=len(yaml_files))
            
            for yaml_file in yaml_files:
                progress.update(task, description=f"Validating {yaml_file.name}")
                
                try:
                    content = yaml_file.read_text()
                    if len(content) > 3000:  # Limit content size
                        content = content[:3000] + "... [truncated]"
                    
                    result = validator(
                        yaml_content=content,
                        file_path=str(yaml_file)
                    )
                    
                    results.append({
                        "file": str(yaml_file),
                        "validation": result.validation_report,
                        "status": "completed"
                    })
                    
                except Exception as e:
                    results.append({
                        "file": str(yaml_file),
                        "validation": f"Error: {str(e)}",
                        "status": "error"
                    })
                
                progress.advance(task)
        
        # Display results
        rprint("\n📊 [bold]Validation Results:[/bold]")
        
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result["status"] == "completed" else "❌"
            file_name = Path(result["file"]).name
            
            result_panel = Panel(
                result["validation"],
                title=f"{status_icon} {i}. {file_name}",
                border_style="green" if result["status"] == "completed" else "red"
            )
            console.print(result_panel)
        
        rprint(f"\n[green]✅ Validated {len(results)} files with LLM[/green]")
    
    asyncio.run(validate())


if __name__ == "__main__":
    app()