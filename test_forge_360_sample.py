#!/usr/bin/env python3
"""
Test a single 360 permutation to demonstrate code generation
"""

import yaml
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def test_single_permutation():
    """Test generating code from a single permutation"""
    
    console.print("🧪 [bold blue]Testing Single Permutation Code Generation[/bold blue]")
    
    # Load a sample permutation
    perm_file = Path("forge_360_demo/python/permutation_060_http_extended_counter_python_pydantic.yaml")
    if not perm_file.exists():
        console.print("❌ Permutation file not found")
        return
    
    with open(perm_file) as f:
        perm_data = yaml.safe_load(f)
    
    # Show the permutation configuration
    console.print("\n📄 [bold]Permutation Configuration[/bold]")
    config = perm_data['configuration']
    console.print(f"ID: {config['span_type']}_{config['attribute_set']}_{config['metric_type']}_{config['language']}_{config['framework']}")
    console.print(f"Span Type: {config['span_type']}")
    console.print(f"Attribute Set: {config['attribute_set']}")
    console.print(f"Metric Type: {config['metric_type']}")
    console.print(f"Language: {config['language']}")
    console.print(f"Framework: {config['framework']}")
    
    # Show semantic convention structure
    console.print("\n🏷️  [bold]Semantic Convention[/bold]")
    semconv = perm_data['semconv']
    span_group = semconv['groups'][0]
    metric_group = semconv['groups'][1]
    
    console.print(f"Span Group: {span_group['id']}")
    console.print(f"Attributes: {len(span_group['attributes'])}")
    console.print(f"Metric: {metric_group['metric_name']}")
    
    # Generate sample Python code based on the configuration
    console.print("\n🐍 [bold]Generated Python Code Preview[/bold]")
    
    attributes = span_group['attributes']
    template_config = config['template_config']
    
    # Generate the Python class
    python_code = generate_python_class(
        span_type=config['span_type'],
        attributes=attributes,
        template_config=template_config,
        metric_config=metric_group
    )
    
    syntax = Syntax(python_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    console.print("\n✨ [bold green]Code Generation Complete![/bold green]")
    console.print("This shows how one of the 360 permutations generates concrete, usable code.")

def generate_python_class(span_type, attributes, template_config, metric_config):
    """Generate Python class code for the permutation"""
    
    # Class name
    class_name = f"{span_type.capitalize()}Span"
    
    # Imports
    imports = "\n".join(template_config['imports'])
    
    # Field definitions
    fields = []
    for attr in attributes:
        field_name = attr['id'].replace(f"{span_type}.", "").replace(".", "_")
        python_type = {
            'string': 'str',
            'int': 'int', 
            'double': 'float',
            'boolean': 'bool'
        }.get(attr['type'], 'str')
        
        optional = "Optional[" + python_type + "]" if attr['requirement_level'] == 'optional' else python_type
        field_template = template_config['field_template'].replace('{brief}', attr['brief'])
        
        fields.append(f"    {field_name}: {optional} = {field_template}")
    
    # Metric method
    metric_method = f"""
    @classmethod
    def create_metric(cls):
        \"\"\"Create OpenTelemetry metric for {span_type} operations\"\"\"
        from opentelemetry import metrics
        
        meter = metrics.get_meter(__name__)
        return meter.create_{metric_config['instrument']}(
            name="{metric_config['metric_name']}", 
            description="{metric_config['brief']}",
            unit="{metric_config['unit']}"
        )"""
    
    # Combine everything
    return f'''{imports}
from typing import Optional

class {class_name}({template_config['base_class']}):
    """DSLModel span attributes for {span_type} operations
    
    This class represents telemetry attributes for {span_type} spans
    as defined by the 360 permutation matrix.
    """
    
{chr(10).join(fields)}
{metric_method}

    def to_span_attributes(self) -> dict:
        """Convert to OpenTelemetry span attributes"""
        return {{
            key: value for key, value in self.dict().items() 
            if value is not None
        }}
'''

if __name__ == "__main__":
    test_single_permutation()