#!/usr/bin/env python3
"""
80/20 Pareto Improvement Engine for Weaver Semantic Conventions

This engine identifies the 20% of changes that will fix 80% of validation issues,
applies them automatically, tests the improvements, and iterates.

Key principles:
- Focus on high-impact, low-effort improvements first
- Measure before/after health metrics  
- Automate the most common fixes
- Iterate based on results
"""

import yaml
import json
import copy
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.bar import Bar

from .weaver_multilayer import WeaverMultiLayerSystem, ValidationResult, ValidationLevel

app = typer.Typer()
console = Console()


@dataclass
class ImprovementOpportunity:
    issue_pattern: str
    frequency: int
    impact_score: float
    effort_score: float
    pareto_ratio: float
    affected_layers: List[str]
    suggested_fix: str
    automation_possible: bool


@dataclass
class ImprovementResult:
    opportunity: ImprovementOpportunity
    before_health: Dict[str, float]
    after_health: Dict[str, float]
    health_improvement: float
    issues_fixed: int
    success: bool


class ParetoImprovementEngine:
    """Engine that applies 80/20 principle to improve semantic conventions"""
    
    def __init__(self):
        self.weaver_system = WeaverMultiLayerSystem()
        self.baseline_results: List[ValidationResult] = []
        self.baseline_health: Dict[str, float] = {}
        self.improvement_history: List[ImprovementResult] = []
        
    def load_layers(self, layer_dir: Path) -> int:
        """Load all semantic convention layers"""
        yaml_files = list(layer_dir.glob("*.yaml")) + list(layer_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                self.weaver_system.load_layer(yaml_file)
            except Exception as e:
                console.print(f"[red]Failed to load {yaml_file}: {e}[/red]")
        
        return len(self.weaver_system.layers)
    
    def establish_baseline(self) -> Tuple[List[ValidationResult], Dict[str, float]]:
        """Establish baseline health metrics"""
        console.print("[cyan]🔍 Establishing baseline health metrics...[/cyan]")
        
        # Run validation
        self.baseline_results = self.weaver_system.validate_all_layers()
        
        # Calculate baseline health
        feedback = self.weaver_system.generate_feedback()
        self.baseline_health = {
            layer: health['health_score'] 
            for layer, health in feedback['layer_health'].items()
        }
        
        # Display baseline
        baseline_table = Table(title="Baseline Health Metrics")
        baseline_table.add_column("Layer", style="cyan")
        baseline_table.add_column("Health Score", style="yellow")
        baseline_table.add_column("Issues", style="red")
        baseline_table.add_column("Status", style="green")
        
        total_health = 0
        total_issues = len(self.baseline_results)
        
        for layer, health in self.baseline_health.items():
            layer_issues = len([r for r in self.baseline_results if r.layer == layer])
            status = "🟢" if health >= 80 else "🟡" if health >= 60 else "🔴"
            
            baseline_table.add_row(
                layer,
                f"{health:.1f}%",
                str(layer_issues),
                status
            )
            total_health += health
        
        avg_health = total_health / len(self.baseline_health) if self.baseline_health else 0
        baseline_table.add_row(
            "[bold]AVERAGE[/bold]",
            f"[bold]{avg_health:.1f}%[/bold]",
            f"[bold]{total_issues}[/bold]",
            "[bold]📊[/bold]"
        )
        
        console.print(baseline_table)
        
        return self.baseline_results, self.baseline_health
    
    def analyze_pareto_opportunities(self) -> List[ImprovementOpportunity]:
        """Analyze validation results to find 80/20 improvement opportunities"""
        console.print("[cyan]📊 Analyzing 80/20 improvement opportunities...[/cyan]")
        
        # Pattern analysis
        issue_patterns = defaultdict(list)
        
        for result in self.baseline_results:
            # Extract pattern from message
            if "missing recommended attributes" in result.message:
                # Extract missing attributes
                if "{" in result.message and "}" in result.message:
                    attrs_str = result.message.split("{")[1].split("}")[0]
                    attrs = [attr.strip("'\"") for attr in attrs_str.split(",")]
                    for attr in attrs:
                        attr = attr.strip()
                        pattern = f"missing_attribute_{attr}"
                        issue_patterns[pattern].append(result)
            else:
                # Generic pattern
                pattern = result.message.split(":")[0] if ":" in result.message else result.message
                issue_patterns[pattern].append(result)
        
        # Calculate impact and effort scores
        opportunities = []
        total_issues = len(self.baseline_results)
        
        for pattern, results in issue_patterns.items():
            frequency = len(results)
            affected_layers = list(set(r.layer for r in results))
            
            # Impact score: frequency + affected layers + health impact
            impact_score = (frequency / total_issues * 100) + (len(affected_layers) * 10)
            
            # Effort score: complexity of fix (lower is better)
            effort_score = self._calculate_effort_score(pattern, results)
            
            # Pareto ratio: impact / effort
            pareto_ratio = impact_score / effort_score if effort_score > 0 else 0
            
            # Determine if automation is possible
            automation_possible = self._can_automate_fix(pattern)
            
            # Generate suggested fix
            suggested_fix = self._generate_fix_suggestion(pattern, results)
            
            opportunity = ImprovementOpportunity(
                issue_pattern=pattern,
                frequency=frequency,
                impact_score=impact_score,
                effort_score=effort_score,
                pareto_ratio=pareto_ratio,
                affected_layers=affected_layers,
                suggested_fix=suggested_fix,
                automation_possible=automation_possible
            )
            
            opportunities.append(opportunity)
        
        # Sort by Pareto ratio (highest impact/effort first)
        opportunities.sort(key=lambda x: x.pareto_ratio, reverse=True)
        
        return opportunities
    
    def _calculate_effort_score(self, pattern: str, results: List[ValidationResult]) -> float:
        """Calculate effort score for fixing a pattern (lower = easier)"""
        if "missing_attribute_" in pattern:
            return 1.0  # Adding attributes is easy
        elif "naming" in pattern.lower():
            return 3.0  # Naming changes are medium effort
        elif "type" in pattern.lower():
            return 5.0  # Type changes are harder
        else:
            return 2.0  # Default medium effort
    
    def _can_automate_fix(self, pattern: str) -> bool:
        """Determine if a fix can be automated"""
        automatable_patterns = [
            "missing_attribute_span.kind",
            "missing_attribute_operation.name", 
            "missing brief",
            "missing requirement_level"
        ]
        return any(auto_pattern in pattern for auto_pattern in automatable_patterns)
    
    def _generate_fix_suggestion(self, pattern: str, results: List[ValidationResult]) -> str:
        """Generate specific fix suggestion for a pattern"""
        if "missing_attribute_span.kind" in pattern:
            return "Add span.kind attribute to all span groups with appropriate values"
        elif "missing_attribute_operation.name" in pattern:
            return "Add operation.name attribute to all span groups"
        elif "missing brief" in pattern:
            return "Add brief descriptions to groups and attributes"
        else:
            return f"Address {pattern} across {len(set(r.layer for r in results))} layers"
    
    def display_pareto_analysis(self, opportunities: List[ImprovementOpportunity]):
        """Display Pareto analysis results"""
        console.print("\n[bold cyan]📈 80/20 Pareto Analysis Results[/bold cyan]")
        
        # Create opportunities table
        opp_table = Table(title="Improvement Opportunities (Ranked by Impact/Effort)")
        opp_table.add_column("Rank", style="bold")
        opp_table.add_column("Issue Pattern", style="cyan")
        opp_table.add_column("Frequency", style="yellow")
        opp_table.add_column("Impact", style="green")
        opp_table.add_column("Effort", style="red")
        opp_table.add_column("Pareto Ratio", style="bold")
        opp_table.add_column("Auto-Fix", style="blue")
        
        # Show top 10 opportunities
        for i, opp in enumerate(opportunities[:10], 1):
            auto_symbol = "🤖" if opp.automation_possible else "👤"
            impact_color = "bright_green" if opp.impact_score >= 50 else "yellow" if opp.impact_score >= 25 else "white"
            effort_color = "green" if opp.effort_score <= 2 else "yellow" if opp.effort_score <= 4 else "red"
            
            opp_table.add_row(
                str(i),
                opp.issue_pattern,
                str(opp.frequency),
                f"[{impact_color}]{opp.impact_score:.1f}[/{impact_color}]",
                f"[{effort_color}]{opp.effort_score:.1f}[/{effort_color}]",
                f"{opp.pareto_ratio:.1f}",
                auto_symbol
            )
        
        console.print(opp_table)
        
        # Show 80/20 analysis
        total_frequency = sum(opp.frequency for opp in opportunities)
        cumulative_frequency = 0
        pareto_20_count = 0
        
        for opp in opportunities:
            cumulative_frequency += opp.frequency
            pareto_20_count += 1
            if cumulative_frequency >= total_frequency * 0.8:
                break
        
        pareto_text = f"""
📊 **Pareto Analysis Summary:**

🎯 **Top {pareto_20_count} issues** ({pareto_20_count/len(opportunities)*100:.1f}% of patterns) 
   account for **{cumulative_frequency}/{total_frequency}** issues ({cumulative_frequency/total_frequency*100:.1f}% of total)

🤖 **{sum(1 for opp in opportunities[:pareto_20_count] if opp.automation_possible)} of top {pareto_20_count}** can be automated

💡 **Recommended Focus:** Fix top 3 highest-ratio opportunities for maximum impact
"""
        
        console.print(Panel(pareto_text, title="80/20 Pareto Insights", border_style="green"))
        
        return opportunities[:pareto_20_count]
    
    def apply_automated_improvements(self, opportunities: List[ImprovementOpportunity]) -> List[ImprovementResult]:
        """Apply automated improvements for the highest-impact opportunities"""
        console.print("\n[cyan]🔧 Applying Automated Improvements...[/cyan]")
        
        results = []
        
        # Focus on top automatable opportunities
        automatable_opps = [opp for opp in opportunities if opp.automation_possible][:3]
        
        for opp in automatable_opps:
            console.print(f"\n[yellow]🎯 Fixing: {opp.issue_pattern}[/yellow]")
            
            # Record before state
            before_health = copy.deepcopy(self.baseline_health)
            
            # Apply fix
            success = self._apply_specific_fix(opp)
            
            if success:
                # Measure after state
                new_results = self.weaver_system.validate_all_layers()
                new_feedback = self.weaver_system.generate_feedback()
                after_health = {
                    layer: health['health_score'] 
                    for layer, health in new_feedback['layer_health'].items()
                }
                
                # Calculate improvement
                health_improvement = sum(after_health.values()) - sum(before_health.values())
                issues_fixed = len(self.baseline_results) - len(new_results)
                
                result = ImprovementResult(
                    opportunity=opp,
                    before_health=before_health,
                    after_health=after_health,
                    health_improvement=health_improvement,
                    issues_fixed=issues_fixed,
                    success=True
                )
                
                # Update baseline for next iteration
                self.baseline_results = new_results
                self.baseline_health = after_health
                
                console.print(f"[green]✅ Fixed {issues_fixed} issues, improved health by {health_improvement:.1f} points[/green]")
            else:
                result = ImprovementResult(
                    opportunity=opp,
                    before_health=before_health,
                    after_health=before_health,
                    health_improvement=0,
                    issues_fixed=0,
                    success=False
                )
                console.print(f"[red]❌ Failed to apply fix for {opp.issue_pattern}[/red]")
            
            results.append(result)
        
        return results
    
    def _apply_specific_fix(self, opportunity: ImprovementOpportunity) -> bool:
        """Apply a specific automated fix"""
        try:
            if "missing_attribute_span.kind" in opportunity.issue_pattern:
                return self._add_span_kind_attributes()
            elif "missing_attribute_operation.name" in opportunity.issue_pattern:
                return self._add_operation_name_attributes()
            else:
                return False
        except Exception as e:
            console.print(f"[red]Error applying fix: {e}[/red]")
            return False
    
    def _add_span_kind_attributes(self) -> bool:
        """Add span.kind attributes to all span groups"""
        console.print("  Adding span.kind attributes to span groups...")
        
        span_kind_mapping = {
            "file": "internal",
            "bash": "internal", 
            "search": "internal",
            "web": "client",
            "agent": "internal",
            "todo": "internal",
            "notebook": "internal"
        }
        
        for layer in self.weaver_system.layers.values():
            for group in layer.groups:
                if group.get('type') == 'span':
                    # Check if span.kind already exists
                    has_span_kind = any(
                        attr.get('id') == 'span.kind' or attr.get('ref') == 'span.kind'
                        for attr in group.get('attributes', [])
                    )
                    
                    if not has_span_kind:
                        # Determine appropriate span kind
                        group_id = group.get('id', '')
                        span_kind = "internal"  # default
                        
                        for category, kind in span_kind_mapping.items():
                            if category in group_id:
                                span_kind = kind
                                break
                        
                        # Add span.kind attribute
                        if 'attributes' not in group:
                            group['attributes'] = []
                        
                        group['attributes'].append({
                            'id': 'span.kind',
                            'type': 'string',
                            'requirement_level': 'required',
                            'brief': 'The kind of span',
                            'examples': [span_kind]
                        })
        
        return True
    
    def _add_operation_name_attributes(self) -> bool:
        """Add operation.name attributes to all span groups"""
        console.print("  Adding operation.name attributes to span groups...")
        
        for layer in self.weaver_system.layers.values():
            for group in layer.groups:
                if group.get('type') == 'span':
                    # Check if operation.name already exists
                    has_operation_name = any(
                        attr.get('id') == 'operation.name' or attr.get('ref') == 'operation.name'
                        for attr in group.get('attributes', [])
                    )
                    
                    if not has_operation_name:
                        # Add operation.name attribute
                        if 'attributes' not in group:
                            group['attributes'] = []
                        
                        group_id = group.get('id', '')
                        operation_name = group_id  # Use group ID as operation name
                        
                        group['attributes'].append({
                            'ref': 'operation.name',
                            'requirement_level': 'required'
                        })
        
        return True
    
    def test_and_validate_improvements(self, improvements: List[ImprovementResult]):
        """Test and validate the applied improvements"""
        console.print("\n[cyan]🧪 Testing and Validating Improvements...[/cyan]")
        
        # Create improvement summary table
        summary_table = Table(title="Improvement Results Summary")
        summary_table.add_column("Fix Applied", style="cyan")
        summary_table.add_column("Issues Fixed", style="green")
        summary_table.add_column("Health Improvement", style="yellow")
        summary_table.add_column("Success", style="bold")
        summary_table.add_column("ROI", style="blue")
        
        total_issues_fixed = 0
        total_health_improvement = 0
        
        for improvement in improvements:
            roi = improvement.health_improvement / improvement.opportunity.effort_score if improvement.opportunity.effort_score > 0 else 0
            success_symbol = "✅" if improvement.success else "❌"
            
            summary_table.add_row(
                improvement.opportunity.issue_pattern,
                str(improvement.issues_fixed),
                f"{improvement.health_improvement:.1f}",
                success_symbol,
                f"{roi:.1f}"
            )
            
            total_issues_fixed += improvement.issues_fixed
            total_health_improvement += improvement.health_improvement
        
        # Add totals row
        summary_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_issues_fixed}[/bold]",
            f"[bold]{total_health_improvement:.1f}[/bold]",
            "[bold]📊[/bold]",
            "[bold]-[/bold]"
        )
        
        console.print(summary_table)
        
        # Show before/after health comparison
        if improvements:
            console.print("\n[bold]📊 Before/After Health Comparison:[/bold]")
            
            health_table = Table()
            health_table.add_column("Layer", style="cyan")
            health_table.add_column("Before", style="red")
            health_table.add_column("After", style="green")
            health_table.add_column("Improvement", style="bold")
            
            # Use the last improvement's health data
            final_improvement = improvements[-1]
            before_health = final_improvement.before_health
            after_health = final_improvement.after_health
            
            for layer in before_health.keys():
                before_score = before_health.get(layer, 0)
                after_score = after_health.get(layer, 0)
                improvement = after_score - before_score
                
                improvement_color = "bright_green" if improvement > 0 else "red" if improvement < 0 else "white"
                improvement_symbol = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
                
                health_table.add_row(
                    layer,
                    f"{before_score:.1f}%",
                    f"{after_score:.1f}%",
                    f"[{improvement_color}]{improvement_symbol} {improvement:+.1f}[/{improvement_color}]"
                )
            
            console.print(health_table)
    
    def save_improvement_results(self, improvements: List[ImprovementResult], opportunities: List[ImprovementOpportunity]):
        """Save improvement results for future iterations"""
        
        # Save updated layers
        for layer_name, layer in self.weaver_system.layers.items():
            if layer_name != "validation_rules":  # Don't overwrite validation rules
                layer_file = Path(f"semconv_layers/{layer_name}.yaml")
                if layer_file.exists():
                    # Convert layer back to YAML format
                    layer_data = {
                        'layer_type': layer.layer_type.value,
                        'version': layer.version,
                        'extends': layer.extends,
                        'dependencies': layer.dependencies,
                        'metadata': layer.metadata,
                        'groups': layer.groups,
                        'attributes': layer.attributes
                    }
                    
                    # Remove None values
                    layer_data = {k: v for k, v in layer_data.items() if v is not None}
                    
                    with open(layer_file, 'w') as f:
                        yaml.dump(layer_data, f, default_flow_style=False, sort_keys=False)
                    
                    console.print(f"[green]✓ Updated {layer_file}[/green]")
        
        # Save improvement report
        report = {
            'timestamp': '2024-01-01T00:00:00Z',
            'pareto_opportunities': [
                {
                    'pattern': opp.issue_pattern,
                    'frequency': opp.frequency,
                    'impact_score': opp.impact_score,
                    'effort_score': opp.effort_score,
                    'pareto_ratio': opp.pareto_ratio,
                    'affected_layers': opp.affected_layers,
                    'suggested_fix': opp.suggested_fix,
                    'automation_possible': opp.automation_possible
                }
                for opp in opportunities
            ],
            'improvements_applied': [
                {
                    'pattern': imp.opportunity.issue_pattern,
                    'issues_fixed': imp.issues_fixed,
                    'health_improvement': imp.health_improvement,
                    'success': imp.success,
                    'before_health': imp.before_health,
                    'after_health': imp.after_health
                }
                for imp in improvements
            ]
        }
        
        report_file = Path("pareto_improvement_report.json")
        report_file.write_text(json.dumps(report, indent=2))
        console.print(f"[green]✓ Saved improvement report to {report_file}[/green]")


@app.command()
def improve(
    layer_dir: Path = typer.Argument("semconv_layers", help="Directory containing semantic convention layers"),
    iterations: int = typer.Option(3, "--iterations", "-i", help="Number of improvement iterations"),
    auto_apply: bool = typer.Option(True, "--auto-apply", help="Automatically apply improvements")
):
    """Run 80/20 improvement analysis and apply fixes"""
    
    console.print("[bold green]🚀 80/20 Pareto Improvement Engine[/bold green]")
    console.print("=" * 70)
    
    engine = ParetoImprovementEngine()
    
    # Load layers
    console.print(f"[cyan]📂 Loading layers from {layer_dir}...[/cyan]")
    layer_count = engine.load_layers(layer_dir)
    console.print(f"[green]✓ Loaded {layer_count} layers[/green]")
    
    # Run improvement iterations
    all_improvements = []
    
    for iteration in range(1, iterations + 1):
        console.print(f"\n[bold yellow]🔄 Iteration {iteration}/{iterations}[/bold yellow]")
        console.print("-" * 50)
        
        # Establish baseline
        baseline_results, baseline_health = engine.establish_baseline()
        
        # Find 80/20 opportunities
        opportunities = engine.analyze_pareto_opportunities()
        top_opportunities = engine.display_pareto_analysis(opportunities)
        
        if not top_opportunities:
            console.print("[yellow]No more improvement opportunities found[/yellow]")
            break
        
        # Apply improvements
        if auto_apply:
            improvements = engine.apply_automated_improvements(top_opportunities)
            
            if improvements:
                # Test and validate
                engine.test_and_validate_improvements(improvements)
                all_improvements.extend(improvements)
            else:
                console.print("[yellow]No automatable improvements available[/yellow]")
                break
        else:
            console.print("[cyan]Auto-apply disabled. Showing opportunities only.[/cyan]")
            break
    
    # Save results
    if all_improvements:
        engine.save_improvement_results(all_improvements, opportunities)
    
    # Final summary
    console.print(f"\n[bold green]🎉 80/20 Improvement Process Complete![/bold green]")
    if all_improvements:
        total_issues_fixed = sum(imp.issues_fixed for imp in all_improvements)
        total_health_improvement = sum(imp.health_improvement for imp in all_improvements)
        
        console.print(f"[green]✅ Total Issues Fixed: {total_issues_fixed}[/green]")
        console.print(f"[green]✅ Total Health Improvement: {total_health_improvement:.1f} points[/green]")
        console.print(f"[green]✅ Successful Improvements: {sum(1 for imp in all_improvements if imp.success)}/{len(all_improvements)}[/green]")


if __name__ == "__main__":
    app()