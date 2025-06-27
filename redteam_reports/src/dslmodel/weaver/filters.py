"""
Weaver template filters for DSLModel generation
"""

def to_python_class(value: str) -> str:
    """Convert semantic convention value to Python class name"""
    class_map = {
        'base': 'Base',
        'fsm': 'FSM',
        'workflow': 'Workflow',
        'agent': 'Agent',
        'event': 'Event',
        'template': 'Template'
    }
    return class_map.get(value, value.title())

def to_mixin_imports(value: str) -> str:
    """Convert mixin combination to import statements"""
    if value == 'none':
        return ''
    
    imports = []
    mixin_map = {
        'jinja': 'from dslmodel.mixins import JinjaDSLMixin',
        'tool': 'from dslmodel.mixins import ToolMixin',
        'file': 'from dslmodel.mixins import FileHandlerDSLMixin',
        'fsm': 'from dslmodel.mixins import FSMMixin'
    }
    
    # Handle single mixins
    if value in mixin_map:
        return mixin_map[value]
    
    # Handle combinations
    if '_' in value:
        parts = value.split('_')
        for part in parts:
            if part in mixin_map:
                imports.append(mixin_map[part])
    elif value == 'all':
        imports = [
            'from dslmodel.mixins import JinjaDSLMixin',
            'from dslmodel.mixins import ToolMixin', 
            'from dslmodel.mixins import FileHandlerDSLMixin'
        ]
    
    return '\n'.join(imports)

def to_span_name(model_type: str, operation: str = 'generate') -> str:
    """Generate OpenTelemetry span name"""
    return f"dslmodel.{operation}.{model_type}"

def to_metric_name(model_type: str, metric_type: str = 'count') -> str:
    """Generate metric name"""
    return f"dslmodel.{model_type}.{metric_type}"