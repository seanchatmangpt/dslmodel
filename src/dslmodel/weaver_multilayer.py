#!/usr/bin/env python3
"""
Multi-Layer Weaver Semantic Convention System

This system implements a hierarchical approach to semantic conventions with:
- Base layer: Core foundational attributes
- Domain layers: Specific domain conventions (file, web, etc.)
- Application layers: Implementation-specific conventions
- Validation engine: Cross-layer consistency checking
- Feedback system: Automated improvement suggestions
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

app = typer.Typer()
console = Console()


class LayerType(Enum):
    BASE = "base"
    DOMAIN = "domain" 
    APPLICATION = "application"
    VALIDATION = "validation"


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class ValidationResult:
    level: ValidationLevel
    message: str
    layer: str
    group_id: Optional[str] = None
    attribute_id: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SemanticLayer:
    name: str
    layer_type: LayerType
    version: str
    extends: Optional[str] = None
    groups: List[Dict[str, Any]] = field(default_factory=list)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WeaverMultiLayerSystem:
    """Multi-layer semantic convention system with validation and feedback"""
    
    def __init__(self):
        self.layers: Dict[str, SemanticLayer] = {}
        self.validation_results: List[ValidationResult] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
        
    def load_layer(self, file_path: Path, layer_name: Optional[str] = None) -> SemanticLayer:
        """Load a semantic convention layer from YAML"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Extract layer metadata
        layer_name = layer_name or file_path.stem
        layer_type = LayerType(data.get('layer_type', 'application'))
        version = data.get('version', '1.0.0')
        extends = data.get('extends')
        dependencies = data.get('dependencies', [])
        metadata = data.get('metadata', {})
        
        layer = SemanticLayer(
            name=layer_name,
            layer_type=layer_type,
            version=version,
            extends=extends,
            groups=data.get('groups', []),
            attributes=data.get('attributes', []),
            dependencies=dependencies,
            metadata=metadata
        )
        
        self.layers[layer_name] = layer
        self._update_dependency_graph(layer_name, dependencies)
        
        return layer
    
    def _update_dependency_graph(self, layer_name: str, dependencies: List[str]):
        """Update the dependency graph for layer ordering"""
        if layer_name not in self.dependency_graph:
            self.dependency_graph[layer_name] = set()
        
        for dep in dependencies:
            self.dependency_graph[layer_name].add(dep)
    
    def validate_all_layers(self) -> List[ValidationResult]:
        """Comprehensive validation across all layers"""
        self.validation_results = []
        
        # Validate layer dependencies
        self._validate_dependencies()
        
        # Validate each layer individually
        for layer_name, layer in self.layers.items():
            self._validate_layer(layer)
        
        # Validate cross-layer consistency
        self._validate_cross_layer_consistency()
        
        # Validate OTEL compliance
        self._validate_otel_compliance()
        
        return self.validation_results
    
    def _validate_dependencies(self):
        """Validate that all layer dependencies exist and are valid"""
        for layer_name, layer in self.layers.items():
            for dep in layer.dependencies:
                if dep not in self.layers:
                    self.validation_results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"Missing dependency: {dep}",
                        layer=layer_name,
                        suggestion=f"Create layer '{dep}' or remove from dependencies"
                    ))
        
        # Check for circular dependencies
        self._check_circular_dependencies()
    
    def _check_circular_dependencies(self):
        """Detect circular dependencies in layer graph"""
        def visit(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if visit(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for layer in self.dependency_graph:
            if layer not in visited:
                if visit(layer, visited, set()):
                    self.validation_results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"Circular dependency detected involving {layer}",
                        layer=layer,
                        suggestion="Restructure layer dependencies to remove cycles"
                    ))
    
    def _validate_layer(self, layer: SemanticLayer):
        """Validate individual layer structure and content"""
        layer_name = layer.name
        
        # Validate groups
        group_ids = set()
        for group in layer.groups:
            group_id = group.get('id')
            if not group_id:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="Group missing required 'id' field",
                    layer=layer_name,
                    suggestion="Add unique 'id' field to group"
                ))
                continue
            
            if group_id in group_ids:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Duplicate group ID: {group_id}",
                    layer=layer_name,
                    group_id=group_id,
                    suggestion=f"Make group ID unique within layer"
                ))
            
            group_ids.add(group_id)
            self._validate_group(group, layer_name)
        
        # Validate global attributes
        for attr in layer.attributes:
            self._validate_attribute(attr, layer_name, None)
    
    def _validate_group(self, group: Dict[str, Any], layer_name: str):
        """Validate individual group structure"""
        group_id = group.get('id')
        group_type = group.get('type')
        
        # Check required fields
        if not group.get('brief'):
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Group {group_id} missing 'brief' description",
                layer=layer_name,
                group_id=group_id,
                suggestion="Add descriptive 'brief' field"
            ))
        
        # Validate type
        valid_types = ['span', 'metric', 'attribute_group', 'event']
        if group_type and group_type not in valid_types:
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Unknown group type: {group_type}",
                layer=layer_name,
                group_id=group_id,
                suggestion=f"Use one of: {', '.join(valid_types)}"
            ))
        
        # Validate attributes within group
        attr_ids = set()
        for attr in group.get('attributes', []):
            attr_id = attr.get('id') or attr.get('ref', 'unknown')
            if attr_id in attr_ids:
                self.validation_results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Duplicate attribute in group {group_id}: {attr_id}",
                    layer=layer_name,
                    group_id=group_id,
                    attribute_id=attr_id
                ))
            attr_ids.add(attr_id)
            self._validate_attribute(attr, layer_name, group_id)
    
    def _validate_attribute(self, attr: Dict[str, Any], layer_name: str, group_id: Optional[str]):
        """Validate individual attribute"""
        attr_id = attr.get('id') or attr.get('ref')
        
        if not attr_id:
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="Attribute missing 'id' or 'ref' field",
                layer=layer_name,
                group_id=group_id,
                suggestion="Add 'id' field for new attributes or 'ref' for references"
            ))
            return
        
        # Validate type
        attr_type = attr.get('type')
        valid_types = ['string', 'int', 'double', 'boolean', 'string[]', 'int[]', 'double[]', 'boolean[]']
        if attr_type and attr_type not in valid_types:
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Unknown attribute type: {attr_type}",
                layer=layer_name,
                group_id=group_id,
                attribute_id=attr_id,
                suggestion=f"Use one of: {', '.join(valid_types)}"
            ))
        
        # Validate requirement level
        req_level = attr.get('requirement_level')
        valid_req_levels = ['required', 'recommended', 'optional']
        if req_level and req_level not in valid_req_levels:
            self.validation_results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Invalid requirement level: {req_level}",
                layer=layer_name,
                group_id=group_id,
                attribute_id=attr_id,
                suggestion=f"Use one of: {', '.join(valid_req_levels)}"
            ))
    
    def _validate_cross_layer_consistency(self):
        """Validate consistency across multiple layers"""
        # Check for conflicting definitions
        all_groups = {}
        all_attributes = {}
        
        for layer_name, layer in self.layers.items():
            # Track group definitions across layers
            for group in layer.groups:
                group_id = group.get('id')
                if group_id:
                    if group_id in all_groups:
                        # Check for conflicts
                        existing = all_groups[group_id]
                        if existing['type'] != group.get('type'):
                            self.validation_results.append(ValidationResult(
                                level=ValidationLevel.ERROR,
                                message=f"Conflicting group type for {group_id}: {existing['type']} vs {group.get('type')}",
                                layer=layer_name,
                                group_id=group_id,
                                suggestion="Ensure consistent group types across layers"
                            ))
                    all_groups[group_id] = {'type': group.get('type'), 'layer': layer_name}
            
            # Track attribute definitions
            for attr in layer.attributes:
                attr_id = attr.get('id')
                if attr_id:
                    if attr_id in all_attributes:
                        existing = all_attributes[attr_id]
                        if existing['type'] != attr.get('type'):
                            self.validation_results.append(ValidationResult(
                                level=ValidationLevel.ERROR,
                                message=f"Conflicting attribute type for {attr_id}: {existing['type']} vs {attr.get('type')}",
                                layer=layer_name,
                                attribute_id=attr_id,
                                suggestion="Ensure consistent attribute types across layers"
                            ))
                    all_attributes[attr_id] = {'type': attr.get('type'), 'layer': layer_name}
    
    def _validate_otel_compliance(self):
        """Validate OpenTelemetry specification compliance"""
        for layer_name, layer in self.layers.items():
            for group in layer.groups:
                group_id = group.get('id')
                group_type = group.get('type')
                
                # Validate span naming conventions
                if group_type == 'span':
                    if not group_id or '.' not in group_id:
                        self.validation_results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"Span group {group_id} should follow dot notation naming",
                            layer=layer_name,
                            group_id=group_id,
                            suggestion="Use format like 'namespace.operation' for span names"
                        ))
                
                # Check for required span attributes
                if group_type == 'span':
                    required_attrs = {'operation.name', 'span.kind'}
                    group_attrs = {attr.get('id', attr.get('ref', '')) for attr in group.get('attributes', [])}
                    missing_attrs = required_attrs - group_attrs
                    
                    if missing_attrs:
                        self.validation_results.append(ValidationResult(
                            level=ValidationLevel.INFO,
                            message=f"Span group {group_id} missing recommended attributes: {missing_attrs}",
                            layer=layer_name,
                            group_id=group_id,
                            suggestion="Consider adding standard OTEL span attributes"
                        ))
    
    def generate_feedback(self) -> Dict[str, Any]:
        """Generate improvement feedback based on validation results"""
        feedback = {
            'summary': {
                'total_issues': len(self.validation_results),
                'errors': len([r for r in self.validation_results if r.level == ValidationLevel.ERROR]),
                'warnings': len([r for r in self.validation_results if r.level == ValidationLevel.WARNING]),
                'suggestions': len([r for r in self.validation_results if r.level == ValidationLevel.SUGGESTION])
            },
            'layer_health': {},
            'improvement_suggestions': [],
            'auto_fixes': []
        }
        
        # Analyze per-layer health
        for layer_name in self.layers:
            layer_results = [r for r in self.validation_results if r.layer == layer_name]
            feedback['layer_health'][layer_name] = {
                'issues': len(layer_results),
                'errors': len([r for r in layer_results if r.level == ValidationLevel.ERROR]),
                'health_score': max(0, 100 - len(layer_results) * 10)  # Simple scoring
            }
        
        # Generate improvement suggestions
        error_patterns = {}
        for result in self.validation_results:
            if result.level == ValidationLevel.ERROR:
                pattern = result.message.split(':')[0]  # Extract error type
                if pattern not in error_patterns:
                    error_patterns[pattern] = []
                error_patterns[pattern].append(result)
        
        for pattern, results in error_patterns.items():
            if len(results) > 1:
                feedback['improvement_suggestions'].append({
                    'pattern': pattern,
                    'frequency': len(results),
                    'suggestion': f"Consider creating a base template to avoid repeated {pattern} errors",
                    'affected_layers': list(set(r.layer for r in results))
                })
        
        # Generate auto-fix suggestions
        for result in self.validation_results:
            if result.suggestion and result.level == ValidationLevel.ERROR:
                feedback['auto_fixes'].append({
                    'layer': result.layer,
                    'group_id': result.group_id,
                    'attribute_id': result.attribute_id,
                    'fix': result.suggestion,
                    'automation_possible': 'Add' in result.suggestion or 'missing' in result.message.lower()
                })
        
        return feedback
    
    def auto_improve_layers(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic improvements based on feedback"""
        improvements = {
            'applied_fixes': [],
            'suggested_changes': [],
            'new_conventions': []
        }
        
        # Apply automatic fixes where possible
        for fix in feedback.get('auto_fixes', []):
            if fix.get('automation_possible'):
                layer = self.layers.get(fix['layer'])
                if layer:
                    improvement = self._apply_auto_fix(layer, fix)
                    if improvement:
                        improvements['applied_fixes'].append(improvement)
        
        # Generate new convention suggestions
        self._suggest_new_conventions(feedback, improvements)
        
        return improvements
    
    def _apply_auto_fix(self, layer: SemanticLayer, fix: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply an individual automatic fix"""
        if 'missing' in fix['fix'].lower() and 'brief' in fix['fix']:
            # Auto-add missing brief descriptions
            for group in layer.groups:
                if group.get('id') == fix.get('group_id') and not group.get('brief'):
                    group['brief'] = f"Automatically generated description for {group['id']}"
                    return {
                        'type': 'added_brief',
                        'layer': layer.name,
                        'group_id': fix['group_id'],
                        'description': 'Added missing brief description'
                    }
        
        return None
    
    def _suggest_new_conventions(self, feedback: Dict[str, Any], improvements: Dict[str, Any]):
        """Suggest new semantic conventions based on patterns"""
        # Analyze common attribute patterns
        all_attributes = []
        for layer in self.layers.values():
            for group in layer.groups:
                all_attributes.extend(group.get('attributes', []))
            all_attributes.extend(layer.attributes)
        
        # Common attribute types
        type_frequency = {}
        for attr in all_attributes:
            attr_type = attr.get('type', 'string')
            type_frequency[attr_type] = type_frequency.get(attr_type, 0) + 1
        
        # Suggest base conventions for common patterns
        if type_frequency.get('string', 0) > 10:
            improvements['new_conventions'].append({
                'type': 'base_attribute',
                'name': 'common.identifier',
                'suggestion': 'Create base string identifier attribute used across multiple groups',
                'frequency': type_frequency['string']
            })


@app.command()
def validate(
    layer_dir: Path = typer.Argument(..., help="Directory containing layer YAML files"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for validation report"),
    auto_fix: bool = typer.Option(False, "--auto-fix", help="Attempt automatic fixes"),
    feedback: bool = typer.Option(True, "--feedback", help="Generate improvement feedback")
):
    """Validate multi-layer semantic conventions"""
    
    if not layer_dir.exists():
        console.print(f"[red]Error: Layer directory '{layer_dir}' not found![/red]")
        raise typer.Exit(1)
    
    system = WeaverMultiLayerSystem()
    
    # Load all layers
    yaml_files = list(layer_dir.glob("*.yaml")) + list(layer_dir.glob("*.yml"))
    if not yaml_files:
        console.print(f"[yellow]No YAML files found in {layer_dir}[/yellow]")
        return
    
    console.print(f"[cyan]Loading {len(yaml_files)} semantic convention layers...[/cyan]")
    
    for yaml_file in yaml_files:
        try:
            layer = system.load_layer(yaml_file)
            console.print(f"  ✓ Loaded {layer.name} ({layer.layer_type.value})")
        except Exception as e:
            console.print(f"  ✗ Failed to load {yaml_file}: {e}")
    
    # Validate all layers
    console.print(f"\n[cyan]Validating {len(system.layers)} layers...[/cyan]")
    results = system.validate_all_layers()
    
    # Display results
    _display_validation_results(results)
    
    # Generate feedback if requested
    if feedback:
        console.print(f"\n[cyan]Generating improvement feedback...[/cyan]")
        feedback_data = system.generate_feedback()
        _display_feedback(feedback_data)
        
        # Auto-improve if requested
        if auto_fix:
            console.print(f"\n[cyan]Applying automatic improvements...[/cyan]")
            improvements = system.auto_improve_layers(feedback_data)
            _display_improvements(improvements)
    
    # Save report if requested
    if output_file:
        report = {
            'validation_results': [
                {
                    'level': r.level.value,
                    'message': r.message,
                    'layer': r.layer,
                    'group_id': r.group_id,
                    'attribute_id': r.attribute_id,
                    'suggestion': r.suggestion
                } for r in results
            ],
            'feedback': feedback_data if feedback else None,
            'improvements': improvements if auto_fix else None
        }
        
        output_file.write_text(json.dumps(report, indent=2))
        console.print(f"\n[green]✓ Validation report saved to {output_file}[/green]")


def _display_validation_results(results: List[ValidationResult]):
    """Display validation results in a formatted table"""
    if not results:
        console.print("[green]✓ All layers passed validation![/green]")
        return
    
    table = Table(title="Validation Results")
    table.add_column("Level", style="bold")
    table.add_column("Layer", style="cyan")
    table.add_column("Group", style="yellow")
    table.add_column("Attribute", style="magenta")
    table.add_column("Message", style="white")
    
    # Color mapping for levels
    level_colors = {
        ValidationLevel.ERROR: "red",
        ValidationLevel.WARNING: "yellow", 
        ValidationLevel.INFO: "blue",
        ValidationLevel.SUGGESTION: "green"
    }
    
    for result in results:
        level_style = level_colors.get(result.level, "white")
        table.add_row(
            f"[{level_style}]{result.level.value.upper()}[/{level_style}]",
            result.layer,
            result.group_id or "-",
            result.attribute_id or "-",
            result.message
        )
    
    console.print(table)


def _display_feedback(feedback: Dict[str, Any]):
    """Display improvement feedback"""
    summary = feedback['summary']
    
    # Summary panel
    summary_text = f"""
Total Issues: {summary['total_issues']}
Errors: {summary['errors']}
Warnings: {summary['warnings']}
Suggestions: {summary['suggestions']}
"""
    
    console.print(Panel(summary_text, title="Validation Summary", border_style="blue"))
    
    # Layer health
    if feedback['layer_health']:
        health_table = Table(title="Layer Health Scores")
        health_table.add_column("Layer", style="cyan")
        health_table.add_column("Health Score", style="green")
        health_table.add_column("Issues", style="yellow")
        health_table.add_column("Errors", style="red")
        
        for layer_name, health in feedback['layer_health'].items():
            score = health['health_score']
            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            health_table.add_row(
                layer_name,
                f"[{score_color}]{score}%[/{score_color}]",
                str(health['issues']),
                str(health['errors'])
            )
        
        console.print(health_table)


def _display_improvements(improvements: Dict[str, Any]):
    """Display applied improvements"""
    if improvements['applied_fixes']:
        console.print("[green]✓ Applied automatic fixes:[/green]")
        for fix in improvements['applied_fixes']:
            console.print(f"  • {fix['description']} in {fix['layer']}")
    
    if improvements['new_conventions']:
        console.print("\n[cyan]💡 Suggested new conventions:[/cyan]")
        for suggestion in improvements['new_conventions']:
            console.print(f"  • {suggestion['suggestion']} (frequency: {suggestion['frequency']})")


if __name__ == "__main__":
    app()