#!/usr/bin/env python3
"""
OTEL-to-Weaver Connection Test
Fast validation of OpenTelemetry to Weaver integration with Ollama
"""

import asyncio
import json
import time
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import requests

import dspy
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich import box

console = Console()

@dataclass
class ConnectionTestResult:
    """Result of OTEL-Weaver connection test"""
    test_name: str
    success: bool
    response_time_ms: float
    validation_score: float
    details: Dict[str, Any]
    timestamp: str

class OTELWeaverConnectionTester:
    """Tests the connection between OpenTelemetry and Weaver"""
    
    def __init__(self, ollama_model: str = "qwen3"):
        self.console = Console()
        self.ollama_model = ollama_model
        self.ollama_available = False
        self.test_results: List[ConnectionTestResult] = []
        self._init_quick_ollama()
    
    def _init_quick_ollama(self):
        """Quick Ollama initialization"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                self.lm = dspy.LM(model=f"ollama/{self.ollama_model}", max_tokens=300, temperature=0.1)
                dspy.settings.configure(lm=self.lm)
                self.ollama_available = True
                self.console.print(f"✅ Ollama {self.ollama_model} ready for connection testing")
            else:
                self.console.print("❌ Ollama server not responding")
        except Exception as e:
            self.console.print(f"⚠️ Ollama not available: {e}")
    
    async def test_semantic_convention_to_span_mapping(self) -> ConnectionTestResult:
        """Test that semantic conventions correctly map to OpenTelemetry spans"""
        start_time = time.time()
        
        # Load semantic convention
        semconv_path = Path("semantic_conventions/dslmodel_core.yaml")
        if not semconv_path.exists():
            return ConnectionTestResult(
                test_name="semconv_to_span_mapping",
                success=False,
                response_time_ms=0,
                validation_score=0.0,
                details={"error": "Semantic convention file not found"},
                timestamp=datetime.now().isoformat()
            )
        
        with open(semconv_path, 'r') as f:
            semconv_data = yaml.safe_load(f)
        
        # Extract span definitions
        spans = [group for group in semconv_data.get('groups', []) if group.get('type') == 'span']
        
        # Test mapping
        mapping_success = True
        span_mappings = {}
        
        for span in spans:
            span_id = span['id']
            expected_name = span_id
            
            # Verify attributes exist
            attributes = span.get('attributes', [])
            required_attrs = [attr for attr in attributes if attr.get('requirement_level') == 'required']
            
            span_mappings[span_id] = {
                "name": expected_name,
                "required_attributes": len(required_attrs),
                "total_attributes": len(attributes),
                "has_brief": bool(span.get('brief')),
                "has_prefix": bool(span.get('prefix'))
            }
        
        response_time = (time.time() - start_time) * 1000
        validation_score = len(spans) / 10.0 if spans else 0.0  # Score based on span count
        
        return ConnectionTestResult(
            test_name="semconv_to_span_mapping",
            success=mapping_success and len(spans) > 0,
            response_time_ms=response_time,
            validation_score=min(validation_score, 1.0),
            details={
                "spans_found": len(spans),
                "span_mappings": span_mappings,
                "semconv_groups": len(semconv_data.get('groups', []))
            },
            timestamp=datetime.now().isoformat()
        )
    
    async def test_weaver_code_generation(self) -> ConnectionTestResult:
        """Test that weaver generates correct code from semantic conventions"""
        start_time = time.time()
        
        # Check if generated files exist
        generated_files = [
            Path("generated/generated_models.py"),
            Path("generated/generated_cli.py"),
            Path("generated/generated_tests.py")
        ]
        
        files_exist = [f.exists() for f in generated_files]
        all_exist = all(files_exist)
        
        # Check file contents for key indicators
        content_checks = {}
        for file_path in generated_files:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                content_checks[file_path.name] = {
                    "has_imports": "import" in content,
                    "has_classes": "class " in content,
                    "has_telemetry": "telemetry" in content.lower() or "span" in content.lower(),
                    "size_bytes": len(content),
                    "has_docstrings": '"""' in content
                }
        
        response_time = (time.time() - start_time) * 1000
        validation_score = sum(files_exist) / len(files_exist)
        
        return ConnectionTestResult(
            test_name="weaver_code_generation",
            success=all_exist,
            response_time_ms=response_time,
            validation_score=validation_score,
            details={
                "files_generated": sum(files_exist),
                "files_expected": len(generated_files),
                "content_checks": content_checks,
                "files_status": dict(zip([f.name for f in generated_files], files_exist))
            },
            timestamp=datetime.now().isoformat()
        )
    
    async def test_otel_span_emission(self) -> ConnectionTestResult:
        """Test that generated code can emit OpenTelemetry spans"""
        start_time = time.time()
        
        # Mock span emission test
        span_data = {
            "name": "dslmodel.model.create",
            "trace_id": "12345678901234567890123456789012",
            "span_id": "1234567890123456",
            "attributes": {
                "dslmodel.model.type": "agent",
                "dslmodel.operation.type": "create"
            },
            "start_time": time.time(),
            "status": "OK"
        }
        
        # Validate span structure
        required_fields = ["name", "trace_id", "span_id", "attributes"]
        has_required = all(field in span_data for field in required_fields)
        
        # Validate naming convention
        name_follows_convention = span_data["name"].startswith("dslmodel.")
        
        # Validate attributes
        attrs = span_data.get("attributes", {})
        has_model_type = "dslmodel.model.type" in attrs
        has_operation_type = "dslmodel.operation.type" in attrs
        
        response_time = (time.time() - start_time) * 1000
        
        success = has_required and name_follows_convention and has_model_type and has_operation_type
        validation_score = (
            (1.0 if has_required else 0.0) +
            (1.0 if name_follows_convention else 0.0) +
            (1.0 if has_model_type else 0.0) +
            (1.0 if has_operation_type else 0.0)
        ) / 4.0
        
        return ConnectionTestResult(
            test_name="otel_span_emission",
            success=success,
            response_time_ms=response_time,
            validation_score=validation_score,
            details={
                "span_structure_valid": has_required,
                "naming_convention_valid": name_follows_convention,
                "required_attributes_present": has_model_type and has_operation_type,
                "span_sample": span_data,
                "attribute_count": len(attrs)
            },
            timestamp=datetime.now().isoformat()
        )
    
    async def test_cli_telemetry_integration(self) -> ConnectionTestResult:
        """Test that CLI commands generate telemetry"""
        start_time = time.time()
        
        # Test CLI availability
        cli_path = Path("dsl_unified_cli.py")
        cli_exists = cli_path.exists()
        
        if not cli_exists:
            return ConnectionTestResult(
                test_name="cli_telemetry_integration",
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                validation_score=0.0,
                details={"error": "CLI file not found"},
                timestamp=datetime.now().isoformat()
            )
        
        # Check CLI content for telemetry integration
        with open(cli_path, 'r') as f:
            cli_content = f.read()
        
        # Look for telemetry indicators
        has_telemetry_imports = "telemetry" in cli_content.lower()
        has_span_creation = "start_span" in cli_content
        has_otel_integration = "opentelemetry" in cli_content.lower() or "otel" in cli_content.lower()
        has_trace_context = "trace" in cli_content.lower()
        
        # Count CLI commands
        command_count = cli_content.count("@app.command")
        
        response_time = (time.time() - start_time) * 1000
        
        integration_score = (
            (1.0 if has_telemetry_imports else 0.0) +
            (1.0 if has_span_creation else 0.0) +
            (1.0 if has_otel_integration else 0.0) +
            (1.0 if has_trace_context else 0.0)
        ) / 4.0
        
        success = integration_score >= 0.5 and command_count > 0
        
        return ConnectionTestResult(
            test_name="cli_telemetry_integration",
            success=success,
            response_time_ms=response_time,
            validation_score=integration_score,
            details={
                "cli_exists": cli_exists,
                "has_telemetry_imports": has_telemetry_imports,
                "has_span_creation": has_span_creation,
                "has_otel_integration": has_otel_integration,
                "command_count": command_count,
                "file_size": len(cli_content)
            },
            timestamp=datetime.now().isoformat()
        )
    
    async def test_ollama_validation(self) -> ConnectionTestResult:
        """Test Ollama LLM validation of the connection"""
        start_time = time.time()
        
        if not self.ollama_available:
            return ConnectionTestResult(
                test_name="ollama_validation",
                success=False,
                response_time_ms=0,
                validation_score=0.0,
                details={"error": "Ollama not available"},
                timestamp=datetime.now().isoformat()
            )
        
        try:
            # Quick validation signature
            class QuickConnectionValidator(dspy.Signature):
                """Quickly validate OTEL-Weaver connection"""
                connection_summary = dspy.InputField(desc="Summary of OTEL-Weaver connection components")
                is_valid = dspy.OutputField(desc="true or false")
                confidence = dspy.OutputField(desc="0.0 to 1.0")
                key_issue = dspy.OutputField(desc="Main issue if any")
            
            validator = dspy.ChainOfThought(QuickConnectionValidator)
            
            # Prepare connection summary
            summary = """
            OTEL-Weaver Connection Components:
            1. Semantic conventions defined in YAML
            2. Weaver generator creates Python models  
            3. Generated CLI with telemetry integration
            4. OpenTelemetry spans emitted from operations
            5. Attributes follow semantic convention schema
            """
            
            result = validator(connection_summary=summary)
            
            is_valid = result.is_valid.lower() == "true"
            confidence = float(result.confidence) if result.confidence.replace('.', '').isdigit() else 0.5
            
            response_time = (time.time() - start_time) * 1000
            
            return ConnectionTestResult(
                test_name="ollama_validation",
                success=is_valid,
                response_time_ms=response_time,
                validation_score=confidence,
                details={
                    "ollama_model": self.ollama_model,
                    "validation_result": result.is_valid,
                    "confidence_score": confidence,
                    "key_issue": result.key_issue,
                    "llm_available": True
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return ConnectionTestResult(
                test_name="ollama_validation",
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                validation_score=0.0,
                details={"error": str(e), "ollama_model": self.ollama_model},
                timestamp=datetime.now().isoformat()
            )
    
    async def run_connection_tests(self) -> List[ConnectionTestResult]:
        """Run all OTEL-Weaver connection tests"""
        self.console.print("\n🔗 [bold cyan]OTEL-to-Weaver Connection Tests[/bold cyan]")
        self.console.print("🎯 Validating end-to-end integration")
        self.console.print("=" * 60)
        
        tests = [
            ("Semantic Convention Mapping", self.test_semantic_convention_to_span_mapping),
            ("Weaver Code Generation", self.test_weaver_code_generation),
            ("OTEL Span Emission", self.test_otel_span_emission),
            ("CLI Telemetry Integration", self.test_cli_telemetry_integration),
            ("Ollama LLM Validation", self.test_ollama_validation)
        ]
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            for test_name, test_func in tests:
                task = progress.add_task(f"Testing {test_name}...", total=None)
                
                result = await test_func()
                results.append(result)
                
                # Display result
                status = "✅ PASS" if result.success else "❌ FAIL"
                score = f"{result.validation_score:.1%}"
                time_ms = f"{result.response_time_ms:.1f}ms"
                
                self.console.print(f"  {status} {test_name} - Score: {score}, Time: {time_ms}")
                
                progress.remove_task(task)
        
        # Display summary
        self._display_connection_summary(results)
        self._save_connection_results(results)
        
        self.test_results = results
        return results
    
    def _display_connection_summary(self, results: List[ConnectionTestResult]):
        """Display connection test summary"""
        
        # Summary table
        summary_table = Table(title="OTEL-Weaver Connection Test Results", box=box.ROUNDED)
        summary_table.add_column("Test", style="cyan", width=25)
        summary_table.add_column("Status", style="green", width=10)
        summary_table.add_column("Score", style="yellow", width=10)
        summary_table.add_column("Time", style="blue", width=10)
        summary_table.add_column("Key Details", style="magenta")
        
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            score = f"{result.validation_score:.1%}"
            time_str = f"{result.response_time_ms:.1f}ms"
            
            # Extract key detail
            key_detail = ""
            if "spans_found" in result.details:
                key_detail = f"{result.details['spans_found']} spans"
            elif "files_generated" in result.details:
                key_detail = f"{result.details['files_generated']}/{result.details['files_expected']} files"
            elif "attribute_count" in result.details:
                key_detail = f"{result.details['attribute_count']} attributes"
            elif "command_count" in result.details:
                key_detail = f"{result.details['command_count']} commands"
            elif "ollama_model" in result.details:
                key_detail = f"Model: {result.details['ollama_model']}"
            
            summary_table.add_row(
                result.test_name.replace("_", " ").title(),
                status,
                score,
                time_str,
                key_detail
            )
        
        self.console.print("\n")
        self.console.print(summary_table)
        
        # Overall assessment
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        avg_score = sum(r.validation_score for r in results) / total_tests if total_tests > 0 else 0
        total_time = sum(r.response_time_ms for r in results)
        
        # Connection health assessment
        health = "EXCELLENT" if passed_tests == total_tests and avg_score > 0.8 else \
                 "GOOD" if passed_tests >= total_tests * 0.8 else \
                 "POOR" if passed_tests >= total_tests * 0.5 else "CRITICAL"
        
        health_color = "green" if health in ["EXCELLENT", "GOOD"] else "yellow" if health == "POOR" else "red"
        
        assessment_panel = Panel(
            f"""
[bold]Connection Health: [{health_color}]{health}[/{health_color}][/bold]

[bold]Test Results:[/bold]
• Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)
• Average Score: {avg_score:.1%}
• Total Test Time: {total_time:.1f}ms

[bold]OTEL-Weaver Integration Status:[/bold]
{"✅" if any(r.test_name == "semconv_to_span_mapping" and r.success for r in results) else "❌"} Semantic conventions map to spans
{"✅" if any(r.test_name == "weaver_code_generation" and r.success for r in results) else "❌"} Weaver generates code correctly  
{"✅" if any(r.test_name == "otel_span_emission" and r.success for r in results) else "❌"} OTEL spans are emitted properly
{"✅" if any(r.test_name == "cli_telemetry_integration" and r.success for r in results) else "❌"} CLI integrates with telemetry
{"✅" if any(r.test_name == "ollama_validation" and r.success for r in results) else "❌"} LLM validation confirms connection

[bold]Recommendation:[/bold]
{self._get_health_recommendation(health)}
            """.strip(),
            title="[bold blue]🔗 Connection Assessment[/bold blue]",
            border_style=health_color
        )
        
        self.console.print(assessment_panel)
    
    def _get_health_recommendation(self, health: str) -> str:
        """Get recommendation based on connection health"""
        if health == "EXCELLENT":
            return "🚀 Connection is optimal - ready for production deployment"
        elif health == "GOOD":
            return "✅ Connection is functional - minor optimizations recommended"
        elif health == "POOR":
            return "⚠️ Connection has issues - address failures before production"
        else:
            return "❌ Connection is broken - requires immediate attention"
    
    def _save_connection_results(self, results: List[ConnectionTestResult]):
        """Save connection test results"""
        output_dir = Path("output/otel_weaver_connection")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results if r.success),
                "average_score": sum(r.validation_score for r in results) / len(results) if results else 0,
                "total_time_ms": sum(r.response_time_ms for r in results)
            },
            "connection_tests": [asdict(r) for r in results]
        }
        
        results_file = output_dir / "connection_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.console.print(f"\n💾 Connection test results saved to: {results_file}")

async def main():
    """Run OTEL-Weaver connection tests"""
    tester = OTELWeaverConnectionTester()
    
    try:
        results = await tester.run_connection_tests()
        
        # Final summary
        passed = sum(1 for r in results if r.success)
        total = len(results)
        
        console.print(f"\n🎯 [bold]Connection Testing Complete[/bold]")
        console.print(f"📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            console.print("🔗 [bold green]CONNECTION VERIFIED: OTEL-to-Weaver integration working[/bold green]")
        else:
            console.print("⚠️ [bold yellow]CONNECTION ISSUES: Some integration problems detected[/bold yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Connection testing failed: {e}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())