#!/usr/bin/env python3
"""
Weaver + Hygen + SwarmAgent: Complete 360° E2E Demonstration

This script showcases the complete ecosystem integration:
1. Generate semantic conventions with Weaver templates
2. Create type-safe Pydantic models from conventions
3. Build coordinated agents using SwarmAgent templates  
4. Execute workflows with full telemetry
5. Validate integration with comprehensive testing

Features demonstrated:
- Hygen template-driven rapid development
- Weaver semantic convention generation
- SwarmAgent multi-agent coordination
- OpenTelemetry ecosystem integration
- Type-safe telemetry with Pydantic models
"""

import asyncio
import subprocess
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live

console = Console()


class WeaverHygenE2E360Demo:
    """Complete 360° demonstration of Weaver + Hygen + SwarmAgent ecosystem."""
    
    def __init__(self):
        self.console = Console()
        self.start_time = datetime.now()
        self.demo_feature = "SecurityMonitoring"
        self.demo_domain = "security_monitoring"
        self.results: Dict[str, Any] = {}
        
        # Generated files tracking
        self.generated_files: List[Path] = []
        self.cleanup_files: List[Path] = []
        
        # Demo phases
        self.phases = [
            "prerequisites",
            "weaver_semconv_generation", 
            "pydantic_model_generation",
            "swarm_ecosystem_creation",
            "cli_integration",
            "e2e_workflow_execution",
            "telemetry_validation",
            "performance_benchmarking"
        ]
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check all required dependencies."""
        deps = {}
        
        # Check hygen
        try:
            result = subprocess.run(["hygen", "--version"], capture_output=True, text=True)
            deps["hygen"] = result.returncode == 0
        except FileNotFoundError:
            deps["hygen"] = False
        
        # Check npx (alternative to hygen)
        try:
            result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
            deps["npx"] = result.returncode == 0
        except FileNotFoundError:
            deps["npx"] = False
        
        # Check Python dependencies
        try:
            import pydantic
            deps["pydantic"] = True
        except ImportError:
            deps["pydantic"] = False
        
        try:
            from rich import console
            deps["rich"] = True
        except ImportError:
            deps["rich"] = False
        
        # Check telemetry directory
        telemetry_dir = Path("~/s2s/agent_coordination").expanduser()
        deps["telemetry_dir"] = telemetry_dir.exists() or self._create_telemetry_dir()
        
        return deps
    
    def _create_telemetry_dir(self) -> bool:
        """Create telemetry directory if it doesn't exist."""
        try:
            telemetry_dir = Path("~/s2s/agent_coordination").expanduser()
            telemetry_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    async def run_complete_360_demo(self) -> Dict[str, Any]:
        """Execute the complete 360° demonstration."""
        self.console.print(Panel.fit(
            "[bold magenta]🌟 Weaver + Hygen + SwarmAgent: 360° E2E Demo[/bold magenta]\n"
            f"[dim]Feature: {self.demo_feature}[/dim]\n"
            f"[dim]Domain: {self.demo_domain}[/dim]\n"
            f"[dim]Phases: {len(self.phases)}[/dim]",
            border_style="magenta",
            title="Complete Ecosystem Demonstration"
        ))
        
        # Check dependencies first
        deps = self.check_dependencies()
        missing_deps = [name for name, available in deps.items() if not available]
        
        if missing_deps:
            self.console.print(f"[red]❌ Missing dependencies: {', '.join(missing_deps)}[/red]")
            if "hygen" in missing_deps and deps.get("npx"):
                self.console.print("[yellow]📝 Will use npx instead of hygen[/yellow]")
            else:
                return {"error": "Dependencies not met", "missing": missing_deps}
        
        try:
            # Execute all phases with progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                
                main_task = progress.add_task("360° Demo Progress", total=len(self.phases))
                
                for i, phase in enumerate(self.phases):
                    progress.update(main_task, description=f"Phase {i+1}: {phase.replace('_', ' ').title()}")
                    
                    phase_result = await self._execute_phase(phase, deps)
                    self.results[phase] = phase_result
                    
                    # Check for phase failure
                    if phase_result.get("error"):
                        self.console.print(f"[red]❌ Phase {phase} failed: {phase_result['error']}[/red]")
                        # Continue with other phases for partial demo
                    
                    progress.update(main_task, advance=1)
                    await asyncio.sleep(0.3)  # Brief pause for visualization
            
            # Generate comprehensive report
            final_report = self._generate_360_report()
            self.results["final_report"] = final_report
            
            # Display results
            self._display_360_results()
            
            return self.results
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo interrupted by user[/yellow]")
            return {"error": "Interrupted by user"}
        except Exception as e:
            self.console.print(f"\n[red]Demo failed: {e}[/red]")
            return {"error": str(e)}
        finally:
            # Cleanup if requested
            self._offer_cleanup()
    
    async def _execute_phase(self, phase: str, deps: Dict[str, bool]) -> Dict[str, Any]:
        """Execute a specific demonstration phase."""
        phase_start = time.time()
        
        try:
            if phase == "prerequisites":
                return await self._phase_prerequisites(deps)
            elif phase == "weaver_semconv_generation":
                return await self._phase_weaver_semconv(deps)
            elif phase == "pydantic_model_generation":
                return await self._phase_pydantic_models()
            elif phase == "swarm_ecosystem_creation":
                return await self._phase_swarm_ecosystem(deps)
            elif phase == "cli_integration":
                return await self._phase_cli_integration()
            elif phase == "e2e_workflow_execution":
                return await self._phase_e2e_workflow()
            elif phase == "telemetry_validation":
                return await self._phase_telemetry_validation()
            elif phase == "performance_benchmarking":
                return await self._phase_performance_benchmarking()
            else:
                return {"error": f"Unknown phase: {phase}"}
                
        except Exception as e:
            return {"error": str(e)}
        finally:
            duration = time.time() - phase_start
            self.console.print(f"[dim]  ⏱️  Phase completed in {duration:.2f}s[/dim]")
    
    async def _phase_prerequisites(self, deps: Dict[str, bool]) -> Dict[str, Any]:
        """Phase 1: Validate prerequisites and setup."""
        self.console.print("[blue]🔍 Phase 1: Prerequisites & Setup[/blue]")
        
        # Create necessary directories
        dirs_created = []
        for dir_path in [
            "src/dslmodel/ecosystems",
            "src/dslmodel/weaver", 
            "semconv_registry"
        ]:
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                dirs_created.append(str(path))
        
        return {
            "dependencies": deps,
            "directories_created": dirs_created,
            "hygen_command": "npx hygen" if not deps.get("hygen") and deps.get("npx") else "hygen",
            "ready": all(deps.values()) or (deps.get("npx") and deps.get("pydantic") and deps.get("rich"))
        }
    
    async def _phase_weaver_semconv(self, deps: Dict[str, bool]) -> Dict[str, Any]:
        """Phase 2: Generate Weaver semantic conventions."""
        self.console.print("[blue]🏗️  Phase 2: Weaver Semantic Conventions[/blue]")
        
        hygen_cmd = self.results["prerequisites"]["hygen_command"]
        
        # Generate semantic conventions using Hygen template
        cmd = [
            hygen_cmd.split()[0],  # hygen or npx
        ]
        if "npx" in hygen_cmd:
            cmd.append("hygen")
        
        cmd.extend(["weaver-semconv", "new"])
        
        # Prepare input for interactive prompts
        input_data = "\\n".join([
            self.demo_domain,           # Domain
            "Security monitoring and threat detection",  # Description
            "security",                 # Prefix
            "1.0.0",                   # Version
            "operation,status,severity,threat_level,user_id",  # Attributes
            "y",                       # Include metrics
            "y",                       # Include events
            "y"                        # Generate models
        ])
        
        try:
            # Execute hygen command
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Track generated files
            registry_file = Path(f"semconv_registry/{self.demo_domain}.yaml")
            models_file = Path(f"src/dslmodel/weaver/{self.demo_domain}_models.py")
            
            if registry_file.exists():
                self.generated_files.append(registry_file)
            if models_file.exists():
                self.generated_files.append(models_file)
            
            return {
                "success": result.returncode == 0,
                "registry_generated": registry_file.exists(),
                "models_generated": models_file.exists(),
                "command_output": result.stdout,
                "files_created": [str(f) for f in [registry_file, models_file] if f.exists()]
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Hygen command timed out"}
        except Exception as e:
            return {"error": f"Failed to generate semantic conventions: {e}"}
    
    async def _phase_pydantic_models(self) -> Dict[str, Any]:
        """Phase 3: Validate generated Pydantic models."""
        self.console.print("[blue]🔧 Phase 3: Pydantic Model Validation[/blue]")
        
        models_file = Path(f"src/dslmodel/weaver/{self.demo_domain}_models.py")
        
        if not models_file.exists():
            return {"error": "Models file not found - previous phase may have failed"}
        
        try:
            # Test import of generated models
            import sys
            sys.path.insert(0, str(Path.cwd()))
            
            # Dynamic import
            spec = __import__(f"src.dslmodel.weaver.{self.demo_domain}_models", fromlist=[""])
            
            # Test model instantiation
            models_tested = {}
            
            # Test span attributes
            if hasattr(spec, f"{self.demo_feature}SpanAttributes"):
                span_attrs_class = getattr(spec, f"{self.demo_feature}SpanAttributes")
                span_attrs = span_attrs_class(operation_name="test_operation")
                otel_attrs = span_attrs.to_otel_attributes()
                models_tested["span_attributes"] = {
                    "created": True,
                    "otel_attributes_count": len(otel_attrs)
                }
            
            # Test context creation
            if hasattr(spec, f"create_swarm_{self.demo_domain}_context"):
                context_func = getattr(spec, f"create_swarm_{self.demo_domain}_context")
                context = context_func(
                    agent_name="test_agent",
                    operation_name="test_operation", 
                    service_name="test_service"
                )
                complete_context = context.to_complete_otel_context()
                models_tested["swarm_context"] = {
                    "created": True,
                    "context_keys": list(complete_context.keys())
                }
            
            return {
                "models_importable": True,
                "models_tested": models_tested,
                "file_size": models_file.stat().st_size
            }
            
        except Exception as e:
            return {"error": f"Model validation failed: {e}"}
    
    async def _phase_swarm_ecosystem(self, deps: Dict[str, bool]) -> Dict[str, Any]:
        """Phase 4: Create SwarmAgent ecosystem."""
        self.console.print("[blue]🤖 Phase 4: SwarmAgent Ecosystem Creation[/blue]")
        
        hygen_cmd = self.results["prerequisites"]["hygen_command"]
        
        # Generate complete ecosystem using Hygen template
        cmd = [
            hygen_cmd.split()[0],
        ]
        if "npx" in hygen_cmd:
            cmd.append("hygen")
        
        cmd.extend(["ecosystem-360", "new"])
        
        # Prepare ecosystem input
        input_data = "\\n".join([
            self.demo_feature,          # Feature name
            "Complete security monitoring ecosystem",  # Description
            self.demo_domain,           # Domain
            "detector,analyzer,responder",  # Agents
            "detection,analysis,response",  # Workflows
            "IDLE,MONITORING,PROCESSING,ALERTING,RESOLVED",  # States
            "y",                        # Include CLI
            "y",                        # Include tests
            "y",                        # Include docs
            "y"                         # Include E2E
        ])
        
        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=45
            )
            
            # Track generated ecosystem files
            ecosystem_file = Path(f"src/dslmodel/ecosystems/{self.demo_domain}_ecosystem.py")
            e2e_file = Path(f"e2e_{self.demo_domain}_demo.py")
            
            generated_files = []
            for file_path in [ecosystem_file, e2e_file]:
                if file_path.exists():
                    self.generated_files.append(file_path)
                    generated_files.append(str(file_path))
            
            return {
                "success": result.returncode == 0,
                "ecosystem_generated": ecosystem_file.exists(),
                "e2e_demo_generated": e2e_file.exists(),
                "files_created": generated_files,
                "agents_count": 3,
                "workflows_count": 3
            }
            
        except Exception as e:
            return {"error": f"Ecosystem generation failed: {e}"}
    
    async def _phase_cli_integration(self) -> Dict[str, Any]:
        """Phase 5: Test CLI integration."""
        self.console.print("[blue]⚡ Phase 5: CLI Integration Testing[/blue]")
        
        # Test existing SwarmAgent CLI commands
        cli_tests = {}
        
        commands_to_test = [
            ("python swarm_cli.py --help", "SwarmAgent CLI help"),
            ("python swarm_cli.py status", "System status check"),
            ("python swarm_cli.py list", "Agent listing"),
        ]
        
        for cmd, description in commands_to_test:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(Path.cwd())
                )
                
                cli_tests[description] = {
                    "success": result.returncode == 0,
                    "output_length": len(result.stdout)
                }
                
            except Exception as e:
                cli_tests[description] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "cli_tests": cli_tests,
            "successful_tests": sum(1 for test in cli_tests.values() if test.get("success"))
        }
    
    async def _phase_e2e_workflow(self) -> Dict[str, Any]:
        """Phase 6: Execute end-to-end workflows."""
        self.console.print("[blue]🔄 Phase 6: E2E Workflow Execution[/blue]")
        
        # Check if E2E demo file was generated
        e2e_file = Path(f"e2e_{self.demo_domain}_demo.py")
        
        if not e2e_file.exists():
            # Fallback to existing SwarmAgent workflows
            return await self._fallback_workflow_test()
        
        try:
            # Execute the generated E2E demo
            result = subprocess.run(
                ["python", str(e2e_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "e2e_demo_executed": True,
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
                "duration": "unknown"
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "E2E demo timed out"}
        except Exception as e:
            return {"error": f"E2E execution failed: {e}"}
    
    async def _fallback_workflow_test(self) -> Dict[str, Any]:
        """Fallback workflow testing using existing SwarmAgent commands."""
        workflow_tests = {}
        
        workflows = [
            ("python swarm_cli.py workflow governance --dry-run", "Governance workflow"),
            ("python swarm_cli.py workflow sprint --dry-run", "Sprint workflow"),
            ("python swarm_cli.py emit swarmsh.test.demo --agent test --trigger demo", "Span emission")
        ]
        
        for cmd, name in workflows:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                workflow_tests[name] = {
                    "success": result.returncode == 0,
                    "output_length": len(result.stdout)
                }
                
            except Exception as e:
                workflow_tests[name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "fallback_mode": True,
            "workflow_tests": workflow_tests,
            "successful_workflows": sum(1 for test in workflow_tests.values() if test.get("success"))
        }
    
    async def _phase_telemetry_validation(self) -> Dict[str, Any]:
        """Phase 7: Validate telemetry integration."""
        self.console.print("[blue]📊 Phase 7: Telemetry Validation[/blue]")
        
        telemetry_file = Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
        
        if not telemetry_file.exists():
            return {"error": "Telemetry file not found"}
        
        try:
            # Analyze telemetry spans
            span_count = 0
            span_types = {}
            agent_activity = {}
            
            with telemetry_file.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        span = json.loads(line)
                        span_count += 1
                        
                        # Count span types
                        name = span.get("name", "unknown")
                        span_types[name] = span_types.get(name, 0) + 1
                        
                        # Count agent activity
                        attrs = span.get("attributes", {})
                        agent = attrs.get("swarm.agent", attrs.get("agent", "unknown"))
                        agent_activity[agent] = agent_activity.get(agent, 0) + 1
                        
                    except json.JSONDecodeError:
                        continue
            
            return {
                "telemetry_active": True,
                "total_spans": span_count,
                "unique_span_types": len(span_types),
                "active_agents": len(agent_activity),
                "file_size": telemetry_file.stat().st_size,
                "span_types": dict(list(span_types.items())[:5]),  # Top 5
                "agent_activity": agent_activity
            }
            
        except Exception as e:
            return {"error": f"Telemetry analysis failed: {e}"}
    
    async def _phase_performance_benchmarking(self) -> Dict[str, Any]:
        """Phase 8: Performance benchmarking."""
        self.console.print("[blue]🚀 Phase 8: Performance Benchmarking[/blue]")
        
        demo_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate success metrics
        successful_phases = sum(1 for result in self.results.values() if not result.get("error"))
        success_rate = (successful_phases / len(self.phases)) * 100
        
        # Files generated metric
        files_generated = len(self.generated_files)
        
        # Calculate performance score
        base_score = success_rate
        duration_penalty = max(0, demo_duration - 30) * 0.5  # Penalty for duration > 30s
        file_bonus = min(20, files_generated * 2)  # Bonus for generated files
        
        performance_score = min(100, max(0, base_score - duration_penalty + file_bonus))
        
        return {
            "demo_duration": demo_duration,
            "successful_phases": successful_phases,
            "total_phases": len(self.phases),
            "success_rate": success_rate,
            "files_generated": files_generated,
            "performance_score": performance_score,
            "performance_grade": self._get_performance_grade(performance_score)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score."""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Satisfactory)"
        else:
            return "D (Needs Improvement)"
    
    def _generate_360_report(self) -> Dict[str, Any]:
        """Generate comprehensive 360° report."""
        perf = self.results.get("performance_benchmarking", {})
        telemetry = self.results.get("telemetry_validation", {})
        
        return {
            "demonstration_summary": {
                "feature": self.demo_feature,
                "domain": self.demo_domain,
                "start_time": self.start_time.isoformat(),
                "duration": perf.get("demo_duration", 0),
                "phases_completed": perf.get("successful_phases", 0),
                "total_phases": len(self.phases)
            },
            "generation_results": {
                "semantic_conventions": self.results.get("weaver_semconv_generation", {}).get("success", False),
                "pydantic_models": self.results.get("pydantic_model_generation", {}).get("models_importable", False),
                "swarm_ecosystem": self.results.get("swarm_ecosystem_creation", {}).get("success", False),
                "files_generated": len(self.generated_files)
            },
            "integration_validation": {
                "cli_working": self.results.get("cli_integration", {}).get("successful_tests", 0) > 0,
                "workflows_executable": self.results.get("e2e_workflow_execution", {}).get("success", False),
                "telemetry_active": telemetry.get("telemetry_active", False),
                "total_spans": telemetry.get("total_spans", 0)
            },
            "performance_metrics": {
                "success_rate": perf.get("success_rate", 0),
                "performance_score": perf.get("performance_score", 0),
                "grade": perf.get("performance_grade", "Unknown"),
                "duration": perf.get("demo_duration", 0)
            },
            "ecosystem_health": {
                "all_phases_successful": all(not result.get("error") for result in self.results.values()),
                "core_features_working": (
                    self.results.get("weaver_semconv_generation", {}).get("success", False) and
                    self.results.get("swarm_ecosystem_creation", {}).get("success", False)
                ),
                "telemetry_integration": telemetry.get("total_spans", 0) > 0
            }
        }
    
    def _display_360_results(self):
        """Display comprehensive 360° demonstration results."""
        report = self.results["final_report"]
        
        # Main summary panel
        summary = report["demonstration_summary"]
        self.console.print(Panel.fit(
            f"[bold]Feature:[/bold] {summary['feature']}\n"
            f"[bold]Domain:[/bold] {summary['domain']}\n"
            f"[bold]Duration:[/bold] {summary['duration']:.2f}s\n"
            f"[bold]Completion:[/bold] {summary['phases_completed']}/{summary['total_phases']} phases",
            title="360° Demo Summary",
            border_style="green"
        ))
        
        # Generation results table
        generation_table = Table(title="🏗️  Generation Results")
        generation_table.add_column("Component", style="cyan")
        generation_table.add_column("Status", style="green")
        generation_table.add_column("Details", style="dim")
        
        generation = report["generation_results"]
        generation_table.add_row(
            "Semantic Conventions", 
            "✅ Generated" if generation["semantic_conventions"] else "❌ Failed",
            "Weaver YAML + Pydantic models"
        )
        generation_table.add_row(
            "Pydantic Models",
            "✅ Validated" if generation["pydantic_models"] else "❌ Failed", 
            "Type-safe telemetry attributes"
        )
        generation_table.add_row(
            "SwarmAgent Ecosystem",
            "✅ Created" if generation["swarm_ecosystem"] else "❌ Failed",
            "Multi-agent coordination system"
        )
        generation_table.add_row(
            "Generated Files",
            f"{generation['files_generated']} files",
            "Total artifacts created"
        )
        
        self.console.print(generation_table)
        
        # Integration validation table
        integration_table = Table(title="🔗 Integration Validation")
        integration_table.add_column("System", style="blue")
        integration_table.add_column("Status", style="green")
        integration_table.add_column("Metrics", style="yellow")
        
        integration = report["integration_validation"]
        integration_table.add_row(
            "CLI Commands",
            "✅ Working" if integration["cli_working"] else "❌ Failed",
            "Command execution validated"
        )
        integration_table.add_row(
            "Workflow Execution", 
            "✅ Executed" if integration["workflows_executable"] else "❌ Failed",
            "Multi-agent workflows tested"
        )
        integration_table.add_row(
            "Telemetry System",
            "✅ Active" if integration["telemetry_active"] else "❌ Inactive",
            f"{integration['total_spans']} spans tracked"
        )
        
        self.console.print(integration_table)
        
        # Performance metrics
        performance = report["performance_metrics"]
        perf_text = (
            f"[bold]Success Rate:[/bold] {performance['success_rate']:.1f}%\n"
            f"[bold]Performance Score:[/bold] {performance['performance_score']:.1f}/100\n"
            f"[bold]Grade:[/bold] {performance['grade']}\n"
            f"[bold]Duration:[/bold] {performance['duration']:.2f}s"
        )
        
        self.console.print(Panel(perf_text, title="📊 Performance Metrics", border_style="yellow"))
        
        # Ecosystem health
        health = report["ecosystem_health"]
        health_status = "🟢 HEALTHY" if health["all_phases_successful"] else "🟡 PARTIAL" if health["core_features_working"] else "🔴 ISSUES"
        
        self.console.print(f"\n[bold]Ecosystem Health: {health_status}[/bold]")
        
        health_checks = [
            ("All Phases Successful", health["all_phases_successful"]),
            ("Core Features Working", health["core_features_working"]),
            ("Telemetry Integration", health["telemetry_integration"])
        ]
        
        for check_name, status in health_checks:
            icon = "✅" if status else "❌"
            self.console.print(f"  {icon} {check_name}")
    
    def _offer_cleanup(self):
        """Offer to clean up generated files."""
        if not self.generated_files:
            return
        
        self.console.print(f"\n[yellow]📁 Generated {len(self.generated_files)} files during demo[/yellow]")
        
        # List generated files
        for file_path in self.generated_files[:5]:  # Show first 5
            self.console.print(f"  • {file_path}")
        
        if len(self.generated_files) > 5:
            self.console.print(f"  ... and {len(self.generated_files) - 5} more")
        
        # Note: In a real implementation, you might prompt for cleanup
        self.console.print("[dim]Files remain for inspection. Remove manually if needed.[/dim]")


async def main():
    """Main entry point for 360° demonstration."""
    demo = WeaverHygenE2E360Demo()
    
    console.print("[bold magenta]🌟 Starting Weaver + Hygen + SwarmAgent 360° Demo...[/bold magenta]")
    
    try:
        results = await demo.run_complete_360_demo()
        
        if "error" in results:
            console.print(f"[red]❌ Demo encountered issues: {results['error']}[/red]")
            return 1
        else:
            console.print("\n[green]🎉 360° Demo completed![/green]")
            
            # Save results
            results_file = Path("weaver_hygen_360_results.json")
            results_file.write_text(json.dumps(results, indent=2, default=str))
            console.print(f"[dim]Results saved to: {results_file}[/dim]")
            
            # Show next steps
            console.print("\n[blue]🚀 Next Steps:[/blue]")
            console.print("  • Explore generated semantic conventions in semconv_registry/")
            console.print("  • Review Pydantic models in src/dslmodel/weaver/")
            console.print("  • Test ecosystem components in src/dslmodel/ecosystems/")
            console.print("  • Run E2E demo independently with generated scripts")
            
            return 0
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))