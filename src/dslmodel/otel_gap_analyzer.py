#!/usr/bin/env python3
"""
OTEL Gap Analyzer - 80/20 Approach to Identifying and Closing Semantic Convention Gaps

This system identifies gaps between semantic conventions and real-world OTEL usage,
prioritizes them using the 80/20 principle, and provides automated gap closure.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from .weaver_multilayer import WeaverMultiLayerSystem

app = typer.Typer()
console = Console()


@dataclass
class GapAnalysis:
    gap_type: str
    description: str
    frequency: int
    impact_score: float
    effort_score: float
    pareto_ratio: float
    affected_tools: List[str]
    affected_spans: List[str]
    recommended_action: str
    automation_possible: bool
    priority: str


@dataclass
class OTELGapFinding:
    finding_type: str
    tool_name: str
    span_name: str
    missing_attributes: List[str]
    extra_attributes: List[str]
    convention_match: bool
    compliance_score: float


class OTELGapAnalyzer:
    """Analyzes gaps between semantic conventions and real OTEL usage"""
    
    def __init__(self):
        self.weaver_system = WeaverMultiLayerSystem()
        self.span_conventions: Dict[str, Dict[str, Any]] = {}
        self.real_otel_data: List[Dict[str, Any]] = []
        self.gap_findings: List[OTELGapFinding] = []
        self.gap_analysis: List[GapAnalysis] = []
        
    def load_semantic_conventions(self, layer_dir: Path) -> int:
        """Load semantic conventions from layer directory"""
        console.print("[cyan]📚 Loading semantic conventions...[/cyan]")
        
        yaml_files = list(layer_dir.glob("*.yaml")) + list(layer_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                self.weaver_system.load_layer(yaml_file)
            except Exception as e:
                console.print(f"[red]Failed to load {yaml_file}: {e}[/red]")
        
        # Extract span conventions
        for layer in self.weaver_system.layers.values():
            for group in layer.groups:
                if group.get('type') == 'span':
                    self.span_conventions[group['id']] = {
                        'group': group,
                        'layer': layer.name,
                        'required_attrs': self._get_required_attributes(group),
                        'recommended_attrs': self._get_recommended_attributes(group),
                        'optional_attrs': self._get_optional_attributes(group)
                    }
        
        console.print(f"[green]✓ Loaded {len(self.weaver_system.layers)} layers with {len(self.span_conventions)} span conventions[/green]")
        return len(self.span_conventions)
    
    def _get_required_attributes(self, group: Dict[str, Any]) -> Set[str]:
        """Get required attributes for a span group"""
        required = set()
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'required':
                attr_id = attr.get('id') or attr.get('ref', '')
                if attr_id:
                    required.add(attr_id)
        return required
    
    def _get_recommended_attributes(self, group: Dict[str, Any]) -> Set[str]:
        """Get recommended attributes for a span group"""
        recommended = set()
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'recommended':
                attr_id = attr.get('id') or attr.get('ref', '')
                if attr_id:
                    recommended.add(attr_id)
        return recommended
    
    def _get_optional_attributes(self, group: Dict[str, Any]) -> Set[str]:
        """Get optional attributes for a span group"""
        optional = set()
        for attr in group.get('attributes', []):
            if attr.get('requirement_level') == 'optional':
                attr_id = attr.get('id') or attr.get('ref', '')
                if attr_id:
                    optional.add(attr_id)
        return optional
    
    def simulate_real_claude_code_otel_data(self) -> List[Dict[str, Any]]:
        """Simulate real Claude Code OTEL telemetry data to find gaps"""
        console.print("[cyan]🔬 Simulating real Claude Code OTEL telemetry...[/cyan]")
        
        # Simulate realistic Claude Code tool usage patterns
        self.real_otel_data = [
            # File operations
            {
                "name": "claude_code.file.read",
                "attributes": {
                    "claude_code.tool.name": "Read",
                    "claude_code.tool.category": "file", 
                    "file.path": "/Users/dev/project/main.py",
                    "file.size_bytes": 2048,
                    # Missing: operation.name, span.kind
                    "session.id": "sess_123",
                    "user.context": "code_review"  # Extra attribute not in conventions
                },
                "duration_ms": 12.5,
                "status": "OK"
            },
            {
                "name": "claude_code.file.write", 
                "attributes": {
                    "claude_code.tool.name": "Write",
                    "claude_code.tool.category": "file",
                    "file.path": "/Users/dev/project/output.py",
                    "file.size_bytes": 1536,
                    "operation.name": "file.write",
                    "span.kind": "internal",
                    "write.mode": "overwrite",
                    # Missing: operation.status
                    "ai.model": "claude-3"  # Extra attribute
                },
                "duration_ms": 8.2,
                "status": "OK"
            },
            
            # Bash operations
            {
                "name": "claude_code.bash",
                "attributes": {
                    "claude_code.tool.name": "Bash",
                    "claude_code.tool.category": "bash",
                    "bash.command": "python -m pytest tests/",
                    "bash.exit_code": 0,
                    # Missing: operation.name, span.kind, operation.status
                    "execution.environment": "local"  # Extra attribute
                },
                "duration_ms": 2500.0,
                "status": "OK"
            },
            
            # Web operations  
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
                    "span.kind": "client",
                    # Missing: operation.status, http.content_type
                    "cache.provider": "cloudflare",  # Extra attribute
                    "user.agent.custom": "Claude-Code/1.0"  # Extra attribute
                },
                "duration_ms": 1800.0,
                "status": "OK"
            },
            
            # Search operations
            {
                "name": "claude_code.search.grep",
                "attributes": {
                    "claude_code.tool.name": "Grep",
                    "claude_code.tool.category": "search",
                    "search.pattern": "async def.*",
                    "search.path": "./src",
                    "search.results_count": 15,
                    # Missing: operation.name, span.kind, operation.status
                    "search.engine": "ripgrep",  # Extra attribute  
                    "performance.memory_peak": 45678  # Extra attribute
                },
                "duration_ms": 300.0,
                "status": "OK"
            },
            
            # Agent operations
            {
                "name": "claude_code.agent",
                "attributes": {
                    "claude_code.tool.name": "Task",
                    "claude_code.tool.category": "agent",
                    "claude_code.agent.id": "research_agent_001",
                    "claude_code.agent.task": "Analyze code structure for patterns",
                    "claude_code.agent.status": "completed",
                    "operation.name": "agent.execute",
                    "span.kind": "internal",
                    "operation.status": "success",
                    # All required attributes present
                    "agent.reasoning_time_ms": 5400,  # Extra attribute
                    "agent.confidence_score": 0.92   # Extra attribute
                },
                "duration_ms": 8700.0,
                "status": "OK"
            }
        ]
        
        console.print(f"[green]✓ Generated {len(self.real_otel_data)} realistic OTEL spans[/green]")
        return self.real_otel_data
    
    def analyze_gaps(self) -> List[OTELGapFinding]:
        """Analyze gaps between conventions and real OTEL data"""
        console.print("[cyan]🔍 Analyzing gaps between conventions and real usage...[/cyan]")
        
        self.gap_findings = []
        
        for span_data in self.real_otel_data:
            span_name = span_data["name"]
            span_attrs = set(span_data.get("attributes", {}).keys())
            
            # Find matching convention
            matched_convention = None
            for conv_name, conv_data in self.span_conventions.items():
                if conv_name in span_name or span_name.startswith(conv_name.replace('.', '_')):
                    matched_convention = conv_data
                    break
            
            if matched_convention:
                # Calculate gaps
                required_attrs = matched_convention['required_attrs']
                recommended_attrs = matched_convention['recommended_attrs']
                all_expected_attrs = required_attrs | recommended_attrs
                
                missing_attrs = list(all_expected_attrs - span_attrs)
                extra_attrs = list(span_attrs - all_expected_attrs - matched_convention['optional_attrs'])
                
                # Calculate compliance score
                total_expected = len(all_expected_attrs)
                total_present = len(all_expected_attrs & span_attrs)
                compliance_score = (total_present / total_expected * 100) if total_expected > 0 else 100.0
                
                finding = OTELGapFinding(
                    finding_type="convention_gap",
                    tool_name=span_data["attributes"].get("claude_code.tool.name", "unknown"),
                    span_name=span_name,
                    missing_attributes=missing_attrs,
                    extra_attributes=extra_attrs,
                    convention_match=True,
                    compliance_score=compliance_score
                )
                
                self.gap_findings.append(finding)
            else:
                # No matching convention found
                finding = OTELGapFinding(
                    finding_type="no_convention",
                    tool_name=span_data["attributes"].get("claude_code.tool.name", "unknown"),
                    span_name=span_name,
                    missing_attributes=[],
                    extra_attributes=list(span_attrs),
                    convention_match=False,
                    compliance_score=0.0
                )
                
                self.gap_findings.append(finding)
        
        console.print(f"[green]✓ Analyzed {len(self.gap_findings)} gap findings[/green]")
        return self.gap_findings
    
    def perform_pareto_gap_analysis(self) -> List[GapAnalysis]:
        """Perform 80/20 Pareto analysis on identified gaps"""
        console.print("[cyan]📊 Performing 80/20 Pareto analysis on gaps...[/cyan]")
        
        # Aggregate gap patterns
        gap_patterns = defaultdict(list)
        
        for finding in self.gap_findings:
            # Missing attribute patterns
            for missing_attr in finding.missing_attributes:
                pattern = f"missing_attribute_{missing_attr}"
                gap_patterns[pattern].append(finding)
            
            # Extra attribute patterns
            for extra_attr in finding.extra_attributes:
                pattern = f"extra_attribute_{extra_attr}"
                gap_patterns[pattern].append(finding)
            
            # No convention patterns
            if not finding.convention_match:
                pattern = "no_convention_found"
                gap_patterns[pattern].append(finding)
        
        # Calculate Pareto scores for each gap pattern
        self.gap_analysis = []
        total_findings = len(self.gap_findings)
        
        for pattern, findings in gap_patterns.items():
            frequency = len(findings)
            affected_tools = list(set(f.tool_name for f in findings))
            affected_spans = list(set(f.span_name for f in findings))
            
            # Impact score: frequency + tool diversity + compliance impact
            impact_score = (frequency / total_findings * 100) + (len(affected_tools) * 5) + (len(affected_spans) * 2)
            
            # Effort score based on gap type
            effort_score = self._calculate_gap_effort_score(pattern, findings)
            
            # Pareto ratio
            pareto_ratio = impact_score / effort_score if effort_score > 0 else 0
            
            # Determine priority
            if pareto_ratio >= 20:
                priority = "high"
            elif pareto_ratio >= 10:
                priority = "medium"
            else:
                priority = "low"
            
            # Generate recommendation
            recommendation = self._generate_gap_recommendation(pattern, findings)
            
            # Check if automatable
            automation_possible = self._is_gap_automatable(pattern)
            
            gap_analysis = GapAnalysis(
                gap_type=pattern,
                description=self._describe_gap(pattern, findings),
                frequency=frequency,
                impact_score=impact_score,
                effort_score=effort_score,
                pareto_ratio=pareto_ratio,
                affected_tools=affected_tools,
                affected_spans=affected_spans,
                recommended_action=recommendation,
                automation_possible=automation_possible,
                priority=priority
            )
            
            self.gap_analysis.append(gap_analysis)
        
        # Sort by Pareto ratio
        self.gap_analysis.sort(key=lambda x: x.pareto_ratio, reverse=True)
        
        console.print(f"[green]✓ Identified {len(self.gap_analysis)} gap patterns for 80/20 analysis[/green]")
        return self.gap_analysis
    
    def _calculate_gap_effort_score(self, pattern: str, findings: List[OTELGapFinding]) -> float:
        """Calculate effort score for closing a gap pattern"""
        if "missing_attribute_" in pattern:
            # Missing attributes are usually easy to add
            if "operation.name" in pattern or "span.kind" in pattern:
                return 1.0  # Very easy - standard OTEL attributes
            elif "operation.status" in pattern:
                return 1.5  # Easy - status mapping
            else:
                return 2.0  # Medium - custom attributes
        elif "extra_attribute_" in pattern:
            # Extra attributes might need convention updates
            return 3.0  # Medium effort - need to evaluate if useful
        elif "no_convention" in pattern:
            # No convention needs new convention creation
            return 5.0  # High effort - new semantic convention needed
        else:
            return 2.0  # Default medium effort
    
    def _is_gap_automatable(self, pattern: str) -> bool:
        """Determine if a gap can be automatically closed"""
        automatable_patterns = [
            "missing_attribute_operation.name",
            "missing_attribute_span.kind", 
            "missing_attribute_operation.status",
            "missing_attribute_session.id"
        ]
        return any(auto_pattern in pattern for auto_pattern in automatable_patterns)
    
    def _describe_gap(self, pattern: str, findings: List[OTELGapFinding]) -> str:
        """Generate description for a gap pattern"""
        if "missing_attribute_" in pattern:
            attr_name = pattern.replace("missing_attribute_", "")
            return f"Missing required/recommended attribute '{attr_name}' in OTEL spans"
        elif "extra_attribute_" in pattern:
            attr_name = pattern.replace("extra_attribute_", "")
            return f"Extra attribute '{attr_name}' not defined in semantic conventions"
        elif "no_convention" in pattern:
            return "OTEL spans without matching semantic conventions"
        else:
            return f"Gap pattern: {pattern}"
    
    def _generate_gap_recommendation(self, pattern: str, findings: List[OTELGapFinding]) -> str:
        """Generate recommendation for closing a gap"""
        if "missing_attribute_operation.name" in pattern:
            return "Add operation.name attribute to all Claude Code spans with tool-specific values"
        elif "missing_attribute_span.kind" in pattern:
            return "Add span.kind attribute with appropriate values (internal/client/server)"
        elif "missing_attribute_operation.status" in pattern:
            return "Add operation.status attribute mapping from OTEL status to semantic convention values"
        elif "extra_attribute_" in pattern:
            attr_name = pattern.replace("extra_attribute_", "")
            return f"Evaluate '{attr_name}' for inclusion in semantic conventions or remove from instrumentation"
        elif "no_convention" in pattern:
            return "Create new semantic conventions for unmatched span patterns"
        else:
            return f"Review and address {pattern} gap"
    
    def display_gap_analysis(self):
        """Display comprehensive gap analysis results"""
        console.print("\n[bold cyan]📈 80/20 Gap Analysis Results[/bold cyan]")
        
        if not self.gap_analysis:
            console.print("[yellow]No gaps identified[/yellow]")
            return
        
        # Create gap analysis table
        gap_table = Table(title="Gap Analysis - Ranked by 80/20 Pareto Impact")
        gap_table.add_column("Rank", style="bold")
        gap_table.add_column("Gap Type", style="cyan")
        gap_table.add_column("Frequency", style="yellow")
        gap_table.add_column("Impact", style="green") 
        gap_table.add_column("Effort", style="red")
        gap_table.add_column("Pareto Ratio", style="bold")
        gap_table.add_column("Priority", style="blue")
        gap_table.add_column("Auto-Fix", style="magenta")
        
        # Show top 10 gaps
        for i, gap in enumerate(self.gap_analysis[:10], 1):
            priority_color = {
                "high": "red",
                "medium": "yellow", 
                "low": "green"
            }.get(gap.priority, "white")
            
            gap_table.add_row(
                str(i),
                gap.gap_type,
                str(gap.frequency),
                f"{gap.impact_score:.1f}",
                f"{gap.effort_score:.1f}",
                f"{gap.pareto_ratio:.1f}",
                f"[{priority_color}]{gap.priority.upper()}[/{priority_color}]",
                "🤖" if gap.automation_possible else "👤"
            )
        
        console.print(gap_table)
        
        # Show 80/20 insights
        total_frequency = sum(gap.frequency for gap in self.gap_analysis)
        cumulative_frequency = 0
        pareto_20_count = 0
        
        for gap in self.gap_analysis:
            cumulative_frequency += gap.frequency
            pareto_20_count += 1
            if cumulative_frequency >= total_frequency * 0.8:
                break
        
        pareto_text = f"""
📊 **80/20 Gap Analysis Summary:**

🎯 **Top {pareto_20_count} gaps** ({pareto_20_count/len(self.gap_analysis)*100:.1f}% of patterns) 
   account for **{cumulative_frequency}/{total_frequency}** issues ({cumulative_frequency/total_frequency*100:.1f}% of total)

🤖 **{sum(1 for gap in self.gap_analysis[:pareto_20_count] if gap.automation_possible)} of top {pareto_20_count}** can be automated

💡 **Recommended Focus:** Address top 3 highest-ratio gaps for maximum impact
"""
        
        console.print(Panel(pareto_text, title="80/20 Gap Insights", border_style="green"))
        
        # Show detailed recommendations for top gaps
        console.print("\n[bold]🎯 Top Priority Gap Recommendations:[/bold]")
        for i, gap in enumerate(self.gap_analysis[:3], 1):
            console.print(f"\n{i}. [cyan]{gap.gap_type}[/cyan] (Pareto Ratio: {gap.pareto_ratio:.1f})")
            console.print(f"   📝 {gap.description}")
            console.print(f"   💡 {gap.recommended_action}")
            console.print(f"   🔧 Affected tools: {', '.join(gap.affected_tools)}")
            if gap.automation_possible:
                console.print(f"   🤖 [green]Can be automated[/green]")
        
        return self.gap_analysis[:pareto_20_count]


@app.command()
def analyze(
    layer_dir: Path = typer.Argument("semconv_layers", help="Directory containing semantic convention layers"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for gap analysis"),
    simulate_data: bool = typer.Option(True, "--simulate", help="Simulate realistic OTEL data")
):
    """Analyze gaps between semantic conventions and real OTEL usage using 80/20 approach"""
    
    console.print("[bold green]🔍 OTEL Gap Analysis - 80/20 Approach[/bold green]")
    console.print("=" * 70)
    
    analyzer = OTELGapAnalyzer()
    
    # Load semantic conventions
    convention_count = analyzer.load_semantic_conventions(layer_dir)
    
    # Generate or load real OTEL data
    if simulate_data:
        otel_data = analyzer.simulate_real_claude_code_otel_data()
    else:
        # Could load from actual OTEL export files
        console.print("[yellow]Real OTEL data loading not implemented yet, using simulation[/yellow]")
        otel_data = analyzer.simulate_real_claude_code_otel_data()
    
    # Analyze gaps
    gap_findings = analyzer.analyze_gaps()
    
    # Perform 80/20 Pareto analysis
    gap_analysis = analyzer.perform_pareto_gap_analysis()
    
    # Display results
    top_gaps = analyzer.display_gap_analysis()
    
    # Save results if requested
    if output_file:
        results = {
            "timestamp": time.time(),
            "summary": {
                "conventions_loaded": convention_count,
                "otel_spans_analyzed": len(otel_data),
                "gap_findings": len(gap_findings),
                "gap_patterns": len(gap_analysis)
            },
            "gap_findings": [
                {
                    "finding_type": finding.finding_type,
                    "tool_name": finding.tool_name,
                    "span_name": finding.span_name,
                    "missing_attributes": finding.missing_attributes,
                    "extra_attributes": finding.extra_attributes,
                    "convention_match": finding.convention_match,
                    "compliance_score": finding.compliance_score
                }
                for finding in gap_findings
            ],
            "gap_analysis": [
                {
                    "gap_type": gap.gap_type,
                    "description": gap.description,
                    "frequency": gap.frequency,
                    "impact_score": gap.impact_score,
                    "effort_score": gap.effort_score,
                    "pareto_ratio": gap.pareto_ratio,
                    "affected_tools": gap.affected_tools,
                    "affected_spans": gap.affected_spans,
                    "recommended_action": gap.recommended_action,
                    "automation_possible": gap.automation_possible,
                    "priority": gap.priority
                }
                for gap in gap_analysis
            ]
        }
        
        output_file.write_text(json.dumps(results, indent=2))
        console.print(f"\n[green]✓ Gap analysis saved to {output_file}[/green]")
    
    # Summary
    console.print(f"\n[bold green]🎯 Gap Analysis Complete![/bold green]")
    console.print(f"[green]✓ {convention_count} semantic conventions analyzed[/green]")
    console.print(f"[green]✓ {len(otel_data)} OTEL spans processed[/green]")
    console.print(f"[green]✓ {len(gap_findings)} gap findings identified[/green]")
    console.print(f"[green]✓ {len(gap_analysis)} gap patterns analyzed[/green]")
    if top_gaps:
        console.print(f"[yellow]⚠️ {len(top_gaps)} high-priority gaps need attention[/yellow]")


if __name__ == "__main__":
    app()