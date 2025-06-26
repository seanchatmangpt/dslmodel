#!/usr/bin/env python3
"""
OTEL-Weaver Integration Demo

This demonstrates the complete integration between:
- Multi-layer Weaver semantic conventions
- OpenTelemetry span generation
- Real-time validation against conventions
- Feedback-driven telemetry improvement
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

from .weaver_multilayer import WeaverMultiLayerSystem

console = Console()


@dataclass
class OTELValidationResult:
    span_name: str
    convention_matched: bool
    missing_attributes: List[str]
    extra_attributes: List[str]
    compliance_score: float
    suggestions: List[str]


class OTELWeaverValidator:
    """Validates OTEL spans against Weaver semantic conventions in real-time"""
    
    def __init__(self, weaver_system: WeaverMultiLayerSystem):
        self.weaver_system = weaver_system
        self.span_conventions = self._extract_span_conventions()
        self.validation_results: List[OTELValidationResult] = []
        
    def _extract_span_conventions(self) -> Dict[str, Dict[str, Any]]:
        """Extract span conventions from all layers"""
        conventions = {}
        
        for layer in self.weaver_system.layers.values():
            for group in layer.groups:
                if group.get('type') == 'span':
                    conventions[group['id']] = {
                        'group': group,
                        'layer': layer.name,
                        'required_attrs': self._get_required_attributes(group),
                        'recommended_attrs': self._get_recommended_attributes(group),
                        'optional_attrs': self._get_optional_attributes(group)
                    }
        
        return conventions
    
    def _get_required_attributes(self, group: Dict[str, Any]) -> List[str]:
        """Get required attributes for a span group"""
        required = []
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'required':
                required.append(attr.get('id') or attr.get('ref', ''))
        return required
    
    def _get_recommended_attributes(self, group: Dict[str, Any]) -> List[str]:
        """Get recommended attributes for a span group"""
        recommended = []
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'recommended':
                recommended.append(attr.get('id') or attr.get('ref', ''))
        return recommended
    
    def _get_optional_attributes(self, group: Dict[str, Any]) -> List[str]:
        """Get optional attributes for a span group"""
        optional = []
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'optional':
                optional.append(attr.get('id') or attr.get('ref', ''))
        return optional
    
    def validate_span(self, span_name: str, span_attributes: Dict[str, Any]) -> OTELValidationResult:
        """Validate a single span against conventions"""
        
        # Find matching convention
        matched_convention = None
        for conv_name, conv_data in self.span_conventions.items():
            if span_name.startswith(conv_name) or conv_name in span_name:
                matched_convention = conv_data
                break
        
        if not matched_convention:
            return OTELValidationResult(
                span_name=span_name,
                convention_matched=False,
                missing_attributes=[],
                extra_attributes=list(span_attributes.keys()),
                compliance_score=0.0,
                suggestions=["No matching semantic convention found"]
            )
        
        # Validate attributes
        required_attrs = set(matched_convention['required_attrs'])
        recommended_attrs = set(matched_convention['recommended_attrs'])
        optional_attrs = set(matched_convention['optional_attrs'])
        span_attr_keys = set(span_attributes.keys())
        
        # Check compliance
        missing_required = required_attrs - span_attr_keys
        missing_recommended = recommended_attrs - span_attr_keys
        extra_attrs = span_attr_keys - required_attrs - recommended_attrs - optional_attrs
        
        # Calculate compliance score
        total_expected = len(required_attrs) + len(recommended_attrs)
        total_present = len(required_attrs - missing_required) + len(recommended_attrs - missing_recommended)
        compliance_score = (total_present / total_expected * 100) if total_expected > 0 else 100.0
        
        # Generate suggestions
        suggestions = []
        if missing_required:
            suggestions.append(f"Add required attributes: {', '.join(missing_required)}")
        if missing_recommended:
            suggestions.append(f"Consider adding recommended attributes: {', '.join(missing_recommended)}")
        if extra_attrs:
            suggestions.append(f"Review extra attributes: {', '.join(extra_attrs)}")
        
        result = OTELValidationResult(
            span_name=span_name,
            convention_matched=True,
            missing_attributes=list(missing_required | missing_recommended),
            extra_attributes=list(extra_attrs),
            compliance_score=compliance_score,
            suggestions=suggestions
        )
        
        self.validation_results.append(result)
        return result


class WeaverSpanProcessor(SimpleSpanProcessor):
    """Custom span processor that validates spans against Weaver conventions"""
    
    def __init__(self, validator: OTELWeaverValidator):
        super().__init__(ConsoleSpanExporter())
        self.validator = validator
        
    def on_end(self, span):
        """Called when a span ends - validate against conventions"""
        span_name = span.name
        span_attributes = dict(span.attributes) if span.attributes else {}
        
        # Validate span
        result = self.validator.validate_span(span_name, span_attributes)
        
        # Log validation result
        if result.compliance_score >= 90:
            status_color = "green"
            status_symbol = "✅"
        elif result.compliance_score >= 70:
            status_color = "yellow"
            status_symbol = "⚠️"
        else:
            status_color = "red"
            status_symbol = "❌"
        
        console.print(f"[{status_color}]{status_symbol} Span: {span_name} - Compliance: {result.compliance_score:.1f}%[/{status_color}]")
        
        # Call parent processor
        super().on_end(span)


def setup_otel_with_weaver_validation():
    """Setup OpenTelemetry with Weaver validation"""
    
    # Load Weaver system
    console.print("[cyan]Loading Weaver semantic conventions...[/cyan]")
    weaver_system = WeaverMultiLayerSystem()
    
    layer_files = [
        "semconv_layers/base_layer.yaml",
        "semconv_layers/file_domain.yaml", 
        "semconv_layers/web_domain.yaml",
        "semconv_layers/claude_code_application.yaml"
    ]
    
    for file_path in layer_files:
        if Path(file_path).exists():
            weaver_system.load_layer(Path(file_path))
    
    console.print(f"[green]✓ Loaded {len(weaver_system.layers)} semantic convention layers[/green]")
    
    # Create validator
    validator = OTELWeaverValidator(weaver_system)
    console.print(f"[green]✓ Created validator with {len(validator.span_conventions)} span conventions[/green]")
    
    # Setup OTEL
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Add custom span processor with Weaver validation
    span_processor = WeaverSpanProcessor(validator)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer, validator, weaver_system


def simulate_claude_code_operations(tracer, validator: OTELWeaverValidator):
    """Simulate Claude Code operations with OTEL telemetry"""
    
    console.print("\n[bold cyan]🔄 Simulating Claude Code Operations with OTEL Telemetry[/bold cyan]")
    
    operations = [
        {
            "name": "claude_code.file.read",
            "attributes": {
                "claude_code.tool.name": "Read",
                "claude_code.tool.category": "file",
                "file.path": "/Users/dev/project/main.py",
                "file.size_bytes": 2048,
                "operation.name": "file.read",
                "operation.status": "success",
                "operation.duration_ms": 12.5
            },
            "duration": 0.1
        },
        {
            "name": "claude_code.bash",
            "attributes": {
                "claude_code.tool.name": "Bash",
                "claude_code.tool.category": "bash",
                "bash.command": "python -m pytest tests/",
                "bash.exit_code": 0,
                "operation.name": "bash.execute",
                "operation.status": "success",
                "operation.duration_ms": 2500.0
            },
            "duration": 2.5
        },
        {
            "name": "claude_code.web.fetch",
            "attributes": {
                "claude_code.tool.name": "WebFetch",
                "claude_code.tool.category": "web",
                "http.url": "https://docs.python.org/3/library/asyncio.html",
                "http.method": "GET",
                "http.status_code": 200,
                "http.response_size_bytes": 102400,
                "operation.name": "web.fetch",
                "operation.status": "success"
            },
            "duration": 1.8
        },
        {
            "name": "claude_code.search",
            "attributes": {
                "claude_code.tool.name": "Grep",
                "claude_code.tool.category": "search",
                "search.pattern": "async def.*",
                "search.path": "./src",
                "search.results_count": 15,
                "operation.name": "search.grep",
                "operation.status": "success"
            },
            "duration": 0.3
        }
    ]
    
    # Execute operations with telemetry
    for i, operation in enumerate(operations, 1):
        console.print(f"\n[yellow]Operation {i}/{len(operations)}: {operation['name']}[/yellow]")
        
        with tracer.start_as_current_span(operation["name"]) as span:
            # Set span attributes
            for key, value in operation["attributes"].items():
                span.set_attribute(key, value)
            
            # Simulate operation duration
            time.sleep(operation["duration"])
            
            # Set span status
            span.set_status(Status(StatusCode.OK))


def analyze_validation_results(validator: OTELWeaverValidator):
    """Analyze and display validation results"""
    
    console.print("\n[bold cyan]📊 Validation Results Analysis[/bold cyan]")
    
    if not validator.validation_results:
        console.print("[yellow]No validation results available[/yellow]")
        return
    
    # Create results table
    results_table = Table(title="OTEL Span Validation Results")
    results_table.add_column("Span", style="cyan")
    results_table.add_column("Matched", style="green")
    results_table.add_column("Compliance", style="bold")
    results_table.add_column("Missing Attrs", style="yellow")
    results_table.add_column("Extra Attrs", style="blue")
    
    total_compliance = 0
    for result in validator.validation_results:
        # Color compliance score
        if result.compliance_score >= 90:
            compliance_color = "bright_green"
        elif result.compliance_score >= 70:
            compliance_color = "yellow"
        else:
            compliance_color = "red"
        
        results_table.add_row(
            result.span_name,
            "✅" if result.convention_matched else "❌",
            f"[{compliance_color}]{result.compliance_score:.1f}%[/{compliance_color}]",
            str(len(result.missing_attributes)),
            str(len(result.extra_attributes))
        )
        total_compliance += result.compliance_score
    
    console.print(results_table)
    
    # Summary statistics
    avg_compliance = total_compliance / len(validator.validation_results)
    matched_count = sum(1 for r in validator.validation_results if r.convention_matched)
    
    summary_text = f"""
📈 Average Compliance Score: {avg_compliance:.1f}%
✅ Conventions Matched: {matched_count}/{len(validator.validation_results)}
🎯 Overall Health: {"Excellent" if avg_compliance >= 90 else "Good" if avg_compliance >= 70 else "Needs Improvement"}
"""
    
    console.print(Panel(summary_text, title="Validation Summary", border_style="green"))
    
    # Show detailed suggestions
    console.print("\n[bold]💡 Improvement Suggestions:[/bold]")
    for i, result in enumerate(validator.validation_results, 1):
        if result.suggestions:
            console.print(f"\n{i}. [cyan]{result.span_name}[/cyan]:")
            for suggestion in result.suggestions:
                console.print(f"   • {suggestion}")


def generate_weaver_feedback_report(validator: OTELWeaverValidator, weaver_system: WeaverMultiLayerSystem):
    """Generate comprehensive feedback report combining OTEL and Weaver validation"""
    
    console.print("\n[bold cyan]📋 Generating Comprehensive Feedback Report[/bold cyan]")
    
    # Weaver layer validation
    weaver_results = weaver_system.validate_all_layers()
    weaver_feedback = weaver_system.generate_feedback()
    
    # OTEL validation summary
    otel_summary = {
        "total_spans": len(validator.validation_results),
        "matched_conventions": sum(1 for r in validator.validation_results if r.convention_matched),
        "average_compliance": sum(r.compliance_score for r in validator.validation_results) / len(validator.validation_results) if validator.validation_results else 0,
        "spans_with_issues": sum(1 for r in validator.validation_results if r.missing_attributes or r.extra_attributes)
    }
    
    # Combined report
    combined_report = {
        "timestamp": time.time(),
        "weaver_validation": {
            "total_issues": len(weaver_results),
            "layer_health": weaver_feedback["layer_health"],
            "improvement_suggestions": weaver_feedback.get("improvement_suggestions", [])
        },
        "otel_validation": otel_summary,
        "span_validations": [asdict(r) for r in validator.validation_results],
        "integration_health": {
            "weaver_otel_alignment": "Good" if otel_summary["average_compliance"] >= 70 else "Needs Work",
            "recommendations": []
        }
    }
    
    # Add integration recommendations
    if otel_summary["average_compliance"] < 70:
        combined_report["integration_health"]["recommendations"].append(
            "Improve OTEL span attribute compliance with Weaver conventions"
        )
    
    if weaver_feedback["summary"]["total_issues"] > 10:
        combined_report["integration_health"]["recommendations"].append(
            "Address Weaver semantic convention validation issues"
        )
    
    # Save report
    report_file = Path("weaver_otel_integration_report.json")
    report_file.write_text(json.dumps(combined_report, indent=2))
    
    console.print(f"[green]✓ Comprehensive report saved to {report_file}[/green]")
    
    # Display key metrics
    metrics_table = Table(title="Integration Health Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="yellow")
    metrics_table.add_column("Status", style="green")
    
    metrics = [
        ("Weaver Layers Loaded", len(weaver_system.layers), "✅"),
        ("Weaver Validation Issues", len(weaver_results), "⚠️" if len(weaver_results) > 5 else "✅"),
        ("OTEL Spans Validated", otel_summary["total_spans"], "✅"),
        ("Average OTEL Compliance", f"{otel_summary['average_compliance']:.1f}%", "✅" if otel_summary["average_compliance"] >= 70 else "⚠️"),
        ("Convention Matches", f"{otel_summary['matched_conventions']}/{otel_summary['total_spans']}", "✅")
    ]
    
    for metric, value, status in metrics:
        metrics_table.add_row(metric, str(value), status)
    
    console.print(metrics_table)


def main():
    """Main demo function"""
    
    console.print("[bold green]🚀 OTEL-Weaver Integration Demo[/bold green]")
    console.print("=" * 70)
    
    # Setup
    tracer, validator, weaver_system = setup_otel_with_weaver_validation()
    
    # Simulate operations
    simulate_claude_code_operations(tracer, validator)
    
    # Analyze results
    analyze_validation_results(validator)
    
    # Generate comprehensive report
    generate_weaver_feedback_report(validator, weaver_system)
    
    console.print("\n[bold green]🎉 OTEL-Weaver Integration Demo Complete![/bold green]")
    console.print("\n[bold]Key Achievements:[/bold]")
    console.print("• ✅ Real-time OTEL span validation against Weaver conventions")
    console.print("• ✅ Multi-layer semantic convention compliance checking")
    console.print("• ✅ Automated feedback generation from telemetry data")
    console.print("• ✅ Integration health monitoring and reporting")
    console.print("• ✅ Continuous validation feedback loop operational")


if __name__ == "__main__":
    main()