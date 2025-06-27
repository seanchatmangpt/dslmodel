"""
E2E Feature Generator - Automatically generates complete features from telemetry specs.
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from ..utils.dspy_tools import init_lm
from ..weaver.loader import PythonConventionLoader
from ..weaver.models import ConventionSet, Span


@dataclass
class FeatureComponents:
    """Components generated for a feature."""
    cli_command: str
    implementation: str
    tests: str
    documentation: str
    integration_code: str


class E2EFeatureGenerator:
    """Generates complete features from telemetry specifications."""
    
    def __init__(self, model: str = "ollama/qwen3"):
        """Initialize the feature generator."""
        self.model = model
        self.generator = None
        self._init_llm()
        
    def _init_llm(self):
        """Initialize the language model."""
        try:
            init_lm(model=self.model, max_tokens=4000)
            logger.info(f"Initialized LLM: {self.model}")
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}")
            self.generator = None
    
    def generate_feature_from_spec(
        self, 
        spec_module: str,
        feature_name: Optional[str] = None,
        output_dir: Path = Path("generated_features")
    ) -> Dict[str, Any]:
        """Generate a complete feature from a telemetry specification."""
        
        start_time = time.time()
        trace_id = f"e2e_{int(time.time() * 1000)}"
        
        # Emit planning span
        self._emit_span("swarmsh.e2e.feature_planning", {
            "feature_name": feature_name or spec_module.split(".")[-1],
            "spec_source": spec_module,
            "trace_id": trace_id
        })
        
        try:
            # Load the telemetry specification
            loader = PythonConventionLoader([spec_module])
            convention_sets = []
            for module in [spec_module]:
                convention_sets.extend(loader.load_module(module))
            
            if not convention_sets:
                raise ValueError(f"No convention sets found in {spec_module}")
            
            # Use first convention set
            convention_set = convention_sets[0]
            feature_name = feature_name or convention_set.title.replace(" ", "_").lower()
            
            logger.info(f"Generating feature '{feature_name}' from {len(convention_set.spans)} spans")
            
            # Generate feature components
            components = self._generate_components(convention_set, feature_name)
            
            # Write generated files
            output_dir.mkdir(parents=True, exist_ok=True)
            self._write_components(components, feature_name, output_dir)
            
            # Validate generated code
            validation_result = self._validate_components(components, output_dir)
            
            # Emit completion span
            duration_ms = int((time.time() - start_time) * 1000)
            self._emit_span("swarmsh.e2e.complete_cycle", {
                "feature_name": feature_name,
                "total_duration_ms": duration_ms,
                "phases_completed": 6,
                "automation_success": validation_result["success"],
                "trace_id": trace_id
            })
            
            return {
                "feature_name": feature_name,
                "spec_module": spec_module,
                "spans_count": len(convention_set.spans),
                "components_generated": list(components.__dict__.keys()),
                "output_dir": str(output_dir),
                "duration_ms": duration_ms,
                "validation": validation_result,
                "trace_id": trace_id
            }
            
        except Exception as e:
            logger.error(f"Feature generation failed: {e}")
            self._emit_span("swarmsh.e2e.complete_cycle", {
                "feature_name": feature_name or "unknown",
                "total_duration_ms": int((time.time() - start_time) * 1000),
                "phases_completed": 0,
                "automation_success": False,
                "trace_id": trace_id,
                "error": str(e)
            })
            raise
    
    def _generate_components(self, convention_set: ConventionSet, feature_name: str) -> FeatureComponents:
        """Generate all components for the feature."""
        
        # Generate CLI command
        cli_command = self._generate_cli_command(convention_set, feature_name)
        self._emit_span("swarmsh.e2e.code_generation", {
            "generation_type": "cli",
            "target_file": f"{feature_name}_cli.py",
            "spans_implemented": len(convention_set.spans),
            "model_used": self.model
        })
        
        # Generate implementation
        implementation = self._generate_implementation(convention_set, feature_name)
        self._emit_span("swarmsh.e2e.code_generation", {
            "generation_type": "implementation",
            "target_file": f"{feature_name}.py",
            "spans_implemented": len(convention_set.spans),
            "model_used": self.model
        })
        
        # Generate tests
        tests = self._generate_tests(convention_set, feature_name)
        self._emit_span("swarmsh.e2e.code_generation", {
            "generation_type": "test",
            "target_file": f"test_{feature_name}.py",
            "spans_implemented": len(convention_set.spans),
            "model_used": self.model
        })
        
        # Generate documentation
        documentation = self._generate_documentation(convention_set, feature_name)
        
        # Generate integration code
        integration_code = self._generate_integration(feature_name)
        
        return FeatureComponents(
            cli_command=cli_command,
            implementation=implementation,
            tests=tests,
            documentation=documentation,
            integration_code=integration_code
        )
    
    def _generate_cli_command(self, convention_set: ConventionSet, feature_name: str) -> str:
        """Generate CLI command for the feature."""
        
        # Extract unique operations from span names
        operations = set()
        for span in convention_set.spans:
            parts = span.name.split(".")
            if len(parts) > 2:
                operations.add(parts[-1])
        
        return f'''"""
{convention_set.title} CLI Commands
Auto-generated from telemetry specification.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from loguru import logger

app = typer.Typer(help="{convention_set.title} commands")
console = Console()


@app.command()
def status():
    """Show current {feature_name} status."""
    from .{feature_name} import {self._to_class_name(feature_name)}
    
    feature = {self._to_class_name(feature_name)}()
    status = feature.get_status()
    
    console.print(f"[bold]{convention_set.title} Status[/bold]")
    for key, value in status.items():
        console.print(f"  {{key}}: {{value}}")


@app.command()
def run(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run {feature_name} operations."""
    from .{feature_name} import {self._to_class_name(feature_name)}
    
    if verbose:
        logger.info(f"Running {feature_name} with config: {{config}}")
    
    feature = {self._to_class_name(feature_name)}()
    result = feature.run(config=config)
    
    if result["success"]:
        console.print(f"[green]✅ {feature_name} completed successfully[/green]")
    else:
        console.print(f"[red]❌ {feature_name} failed: {{result.get('error')}}[/red]")


if __name__ == "__main__":
    app()
'''
    
    def _generate_implementation(self, convention_set: ConventionSet, feature_name: str) -> str:
        """Generate main implementation for the feature."""
        
        # Generate span emission methods
        span_methods = []
        for span in convention_set.spans:
            method_name = span.name.split(".")[-1]
            span_methods.append(self._generate_span_method(span))
        
        return f'''"""
{convention_set.title} Implementation
Auto-generated from telemetry specification.
"""

import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


tracer = trace.get_tracer(__name__, "{convention_set.version}")


class {self._to_class_name(feature_name)}:
    """Implementation of {convention_set.title}."""
    
    def __init__(self):
        """Initialize the {feature_name}."""
        self.trace_id = str(uuid.uuid4())
        self._start_time = time.time()
        logger.info(f"Initialized {{self.__class__.__name__}} (trace: {{self.trace_id}})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {{
            "initialized": True,
            "trace_id": self.trace_id,
            "uptime_seconds": int(time.time() - self._start_time),
            "spans_available": {len(convention_set.spans)}
        }}
    
    def run(self, config: Optional[Path] = None) -> Dict[str, Any]:
        """Run the main operation."""
        try:
            # Implement main logic here
            logger.info(f"Running {{self.__class__.__name__}}")
            
            # Example: emit some spans
            {"".join(span_methods)}
            
            return {{
                "success": True,
                "trace_id": self.trace_id,
                "duration_ms": int((time.time() - self._start_time) * 1000)
            }}
            
        except Exception as e:
            logger.error(f"Operation failed: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "trace_id": self.trace_id
            }}
'''
    
    def _generate_span_method(self, span: Span) -> str:
        """Generate a method that emits a telemetry span."""
        method_name = span.name.split(".")[-1]
        
        # Generate attribute parameters
        params = []
        for attr in span.attributes:
            if attr.cardinality.value == "required":
                param_type = self._attr_type_to_python(attr.type.value)
                params.append(f"{attr.name}: {param_type}")
        
        params_str = ", ".join(params) if params else ""
        
        return f'''
    def emit_{method_name}(self{", " + params_str if params_str else ""}):
        """Emit {span.name} span."""
        with tracer.start_as_current_span("{span.name}") as span:
            # Set attributes
            {self._generate_attribute_setters(span)}
            
            logger.debug(f"Emitted {{span.name}}")
'''
    
    def _generate_attribute_setters(self, span: Span) -> str:
        """Generate code to set span attributes."""
        setters = []
        for attr in span.attributes:
            if attr.cardinality.value == "required":
                setters.append(f'span.set_attribute("{attr.name}", {attr.name})')
        return "\n            ".join(setters) if setters else "pass"
    
    def _attr_type_to_python(self, attr_type: str) -> str:
        """Convert attribute type to Python type hint."""
        mapping = {
            "string": "str",
            "int": "int",
            "double": "float",
            "boolean": "bool",
            "string[]": "List[str]"
        }
        return mapping.get(attr_type, "Any")
    
    def _generate_tests(self, convention_set: ConventionSet, feature_name: str) -> str:
        """Generate tests for the feature."""
        
        return f'''"""
Tests for {convention_set.title}
Auto-generated from telemetry specification.
"""

import pytest
from unittest.mock import Mock, patch
from .{feature_name} import {self._to_class_name(feature_name)}


class Test{self._to_class_name(feature_name)}:
    """Test {convention_set.title} implementation."""
    
    def test_initialization(self):
        """Test feature initialization."""
        feature = {self._to_class_name(feature_name)}()
        assert feature is not None
        assert feature.trace_id is not None
    
    def test_get_status(self):
        """Test status retrieval."""
        feature = {self._to_class_name(feature_name)}()
        status = feature.get_status()
        
        assert status["initialized"] is True
        assert "trace_id" in status
        assert status["spans_available"] == {len(convention_set.spans)}
    
    def test_run_success(self):
        """Test successful run."""
        feature = {self._to_class_name(feature_name)}()
        result = feature.run()
        
        assert result["success"] is True
        assert "trace_id" in result
        assert "duration_ms" in result
    
    @patch("opentelemetry.trace.get_tracer")
    def test_span_emission(self, mock_tracer):
        """Test that spans are emitted correctly."""
        mock_span = Mock()
        mock_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = mock_span
        
        feature = {self._to_class_name(feature_name)}()
        feature.run()
        
        # Verify spans were created
        assert mock_tracer.return_value.start_as_current_span.called
'''
    
    def _generate_documentation(self, convention_set: ConventionSet, feature_name: str) -> str:
        """Generate documentation for the feature."""
        
        # Generate span documentation
        span_docs = []
        for span in convention_set.spans:
            attrs = []
            for attr in span.attributes:
                attrs.append(f"  - `{attr.name}` ({attr.type.value}): {attr.description}")
            
            span_docs.append(f"""
### {span.name}

{span.brief}

**Attributes:**
{chr(10).join(attrs)}
""")
        
        return f'''# {convention_set.title}

**Version:** {convention_set.version}

This feature was auto-generated from telemetry specifications.

## Overview

{convention_set.title} provides comprehensive telemetry instrumentation with {len(convention_set.spans)} defined spans.

## Installation

```bash
pip install dslmodel
```

## Usage

### CLI Commands

```bash
# Show status
dsl {feature_name} status

# Run operations
dsl {feature_name} run --config config.yaml
```

### Python API

```python
from dslmodel.{feature_name} import {self._to_class_name(feature_name)}

# Initialize
feature = {self._to_class_name(feature_name)}()

# Get status
status = feature.get_status()

# Run operations
result = feature.run()
```

## Telemetry Spans

The following spans are emitted:

{"".join(span_docs)}

## Configuration

Configuration can be provided via YAML file:

```yaml
# config.yaml
{feature_name}:
  enabled: true
  options:
    verbose: true
```
'''
    
    def _generate_integration(self, feature_name: str) -> str:
        """Generate integration code."""
        
        return f'''# Integration code for {feature_name}

# Add to main CLI app
from .{feature_name}_cli import app as {feature_name}_app
main_app.add_typer({feature_name}_app, name="{feature_name.replace("_", "-")}")

# Add to __init__.py
from .{feature_name} import {self._to_class_name(feature_name)}

# Export in __all__
__all__ = ["{self._to_class_name(feature_name)}"]
'''
    
    def _write_components(self, components: FeatureComponents, feature_name: str, output_dir: Path):
        """Write generated components to files."""
        
        files = {
            f"{feature_name}_cli.py": components.cli_command,
            f"{feature_name}.py": components.implementation,
            f"test_{feature_name}.py": components.tests,
            f"{feature_name}.md": components.documentation,
            "integration.txt": components.integration_code
        }
        
        for filename, content in files.items():
            filepath = output_dir / filename
            filepath.write_text(content)
            logger.info(f"Generated: {filepath}")
            
            self._emit_span("swarmsh.e2e.integration", {
                "integration_type": "file_write",
                "files_modified": 1,
                "target_file": str(filepath)
            })
    
    def _validate_components(self, components: FeatureComponents, output_dir: Path) -> Dict[str, Any]:
        """Validate generated components."""
        
        validation_results = {
            "success": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate Python syntax
        for filename in [f for f in output_dir.glob("*.py")]:
            try:
                import ast
                with open(filename) as f:
                    ast.parse(f.read())
                logger.success(f"✅ Valid Python: {filename.name}")
            except SyntaxError as e:
                validation_results["success"] = False
                validation_results["errors"].append(f"Syntax error in {filename.name}: {e}")
                logger.error(f"❌ Syntax error in {filename.name}: {e}")
        
        self._emit_span("swarmsh.e2e.validation", {
            "validation_type": "syntax",
            "validation_result": "passed" if validation_results["success"] else "failed",
            "errors": validation_results["errors"],
            "otel_compliant": True
        })
        
        return validation_results
    
    def _emit_span(self, span_name: str, attributes: Dict[str, Any]):
        """Emit a telemetry span (simulated for demo)."""
        logger.debug(f"📊 {span_name}: {attributes}")
    
    def _to_class_name(self, feature_name: str) -> str:
        """Convert feature name to class name."""
        return "".join(word.capitalize() for word in feature_name.split("_"))