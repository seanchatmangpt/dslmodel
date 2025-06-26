#!/usr/bin/env python3
"""
OTEL Telemetry Observer - Capture and analyze autonomous evolution telemetry
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON

# Set up OTEL telemetry collection
span_exporter = InMemorySpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)

console = Console()

async def run_evolution_with_telemetry():
    """Run evolution cycle and capture telemetry"""
    
    console.print("[bold cyan]🔍 Starting OTEL Telemetry Observation[/bold cyan]")
    
    # Clear any existing spans
    span_exporter.clear()
    
    # Import and run evolution daemon
    from src.dslmodel.commands.autonomous_evolution_daemon import AutonomousEvolutionDaemon
    
    daemon = AutonomousEvolutionDaemon()
    daemon.schedule_interval = 5  # Short interval for testing
    
    console.print("📊 Running evolution cycle with OTEL capture...")
    
    # Run one evolution cycle
    start_time = time.time()
    await daemon._run_evolution_cycle()
    cycle_duration = time.time() - start_time
    
    # Get captured spans
    spans = span_exporter.get_finished_spans()
    
    console.print(f"✅ Evolution cycle completed in {cycle_duration:.2f}s")
    console.print(f"📡 Captured {len(spans)} OTEL spans")
    
    return spans, daemon

def analyze_telemetry_spans(spans):
    """Analyze captured telemetry spans for issues"""
    
    console.print("\n[bold yellow]🔬 Analyzing OTEL Telemetry Data[/bold yellow]")
    
    # Group spans by operation
    span_groups = {}
    for span in spans:
        operation = span.name
        if operation not in span_groups:
            span_groups[operation] = []
        span_groups[operation].append(span)
    
    # Create analysis table
    table = Table(title="OTEL Span Analysis")
    table.add_column("Operation", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Duration (ms)", style="yellow")
    table.add_column("Attributes", style="blue")
    table.add_column("Issues", style="red")
    
    issues_found = []
    
    for operation, operation_spans in span_groups.items():
        count = len(operation_spans)
        
        # Calculate average duration
        durations = []
        attribute_counts = []
        
        for span in operation_spans:
            if span.end_time and span.start_time:
                duration_ns = span.end_time - span.start_time
                duration_ms = duration_ns / 1_000_000
                durations.append(duration_ms)
            
            attribute_counts.append(len(span.attributes) if span.attributes else 0)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        avg_attributes = sum(attribute_counts) / len(attribute_counts) if attribute_counts else 0
        
        # Check for issues
        operation_issues = []
        
        # Issue 1: Missing attributes
        if avg_attributes < 3:
            operation_issues.append("Few attributes")
            issues_found.append(f"{operation}: Only {avg_attributes:.1f} avg attributes")
        
        # Issue 2: No duration data
        if not durations:
            operation_issues.append("No timing")
            issues_found.append(f"{operation}: Missing timing data")
        
        # Issue 3: Extremely long operations
        if avg_duration > 10000:  # 10 seconds
            operation_issues.append("Long duration")
            issues_found.append(f"{operation}: Avg duration {avg_duration:.0f}ms")
        
        # Issue 4: Missing spans for expected operations
        expected_operations = [
            "autonomous.evolution.scheduler",
            "autonomous.evolution.cycle", 
            "autonomous.evolution.strategy_selection",
            "autonomous.evolution.meaningful_work"
        ]
        
        table.add_row(
            operation,
            str(count),
            f"{avg_duration:.1f}" if durations else "N/A",
            f"{avg_attributes:.1f}",
            ", ".join(operation_issues) if operation_issues else "✅"
        )
    
    console.print(table)
    
    # Check for missing expected operations
    found_operations = set(span_groups.keys())
    expected_operations = {
        "autonomous.evolution.scheduler",
        "autonomous.evolution.cycle", 
        "autonomous.evolution.strategy_selection",
        "autonomous.evolution.meaningful_work",
        "autonomous.evolution.resource_management"
    }
    
    missing_operations = expected_operations - found_operations
    if missing_operations:
        for op in missing_operations:
            issues_found.append(f"Missing operation: {op}")
    
    return issues_found

def analyze_span_attributes(spans):
    """Analyze span attributes for data quality issues"""
    
    console.print("\n[bold yellow]🔍 Analyzing Span Attributes[/bold yellow]")
    
    attribute_issues = []
    
    for span in spans:
        operation = span.name
        attributes = span.attributes or {}
        
        # Check for empty or None values
        for key, value in attributes.items():
            if value is None:
                attribute_issues.append(f"{operation}: {key} is None")
            elif value == "":
                attribute_issues.append(f"{operation}: {key} is empty string")
            elif isinstance(value, str) and value == "test_value":
                attribute_issues.append(f"{operation}: {key} has test placeholder value")
        
        # Check for missing required attributes based on operation
        required_attrs = {
            "autonomous.evolution.scheduler": ["scheduler_id", "schedule_interval_minutes"],
            "autonomous.evolution.cycle": ["cycle_id", "scheduler_id", "selected_strategy"],
            "autonomous.evolution.strategy_selection": ["cycle_id", "selected_strategy"],
            "autonomous.evolution.meaningful_work": ["cycle_id", "deployment_recommended"],
        }
        
        if operation in required_attrs:
            for required_attr in required_attrs[operation]:
                full_attr_name = f"{operation}.{required_attr}"
                if full_attr_name not in attributes:
                    attribute_issues.append(f"{operation}: Missing required attribute {required_attr}")
    
    # Show sample attributes for inspection
    if spans:
        console.print("\n[bold]Sample Span Attributes:[/bold]")
        sample_span = spans[0]
        if sample_span.attributes:
            json_attrs = json.dumps(dict(sample_span.attributes), indent=2)
            console.print(JSON(json_attrs))
        else:
            console.print("[red]No attributes found in sample span![/red]")
    
    return attribute_issues

async def main():
    """Main OTEL observation and analysis"""
    
    try:
        # Run evolution with telemetry capture
        spans, daemon = await run_evolution_with_telemetry()
        
        if not spans:
            console.print("[red]❌ No OTEL spans captured! Telemetry not working.[/red]")
            return
        
        # Analyze telemetry data
        span_issues = analyze_telemetry_spans(spans)
        attribute_issues = analyze_span_attributes(spans)
        
        # Report findings
        all_issues = span_issues + attribute_issues
        
        if all_issues:
            console.print("\n[bold red]🚨 Issues Found:[/bold red]")
            for i, issue in enumerate(all_issues, 1):
                console.print(f"{i}. {issue}")
        else:
            console.print("\n[bold green]✅ No telemetry issues found![/bold green]")
        
        # Show evolution results
        console.print("\n[bold]Evolution Results:[/bold]")
        console.print(f"  Cycles completed: {daemon.cycle_number}")
        console.print(f"  Meaningful work: {daemon.total_meaningful_work}")
        
        # Save telemetry data for further analysis
        telemetry_data = {
            'timestamp': datetime.now().isoformat(),
            'spans_captured': len(spans),
            'issues_found': len(all_issues),
            'issues': all_issues,
            'spans': [
                {
                    'name': span.name,
                    'duration_ms': (span.end_time - span.start_time) / 1_000_000 if span.end_time and span.start_time else None,
                    'attributes': dict(span.attributes) if span.attributes else {},
                    'status': str(span.status)
                }
                for span in spans
            ]
        }
        
        telemetry_file = Path("telemetry_analysis.json")
        with open(telemetry_file, 'w') as f:
            json.dump(telemetry_data, f, indent=2)
        
        console.print(f"\n📄 Telemetry data saved to {telemetry_file}")
        
        return all_issues
        
    except Exception as e:
        console.print(f"[red]❌ OTEL observation failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return [f"Observation error: {e}"]

if __name__ == "__main__":
    issues = asyncio.run(main())
    if issues:
        exit(1)
    else:
        exit(0)