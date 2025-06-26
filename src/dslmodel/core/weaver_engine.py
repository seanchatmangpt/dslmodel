#!/usr/bin/env python3
"""
Weaver Engine - Core auto-generation engine for DSLModel

This is the heart of the Weaver-first architecture. It takes semantic conventions
and auto-generates models, CLI commands, tests, and documentation.

80/20 Principle: This single file enables 80% of the value by automating
everything from telemetry specifications.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import json
from loguru import logger
from jinja2 import Environment, FileSystemLoader, Template
from dataclasses import dataclass
from enum import Enum

from dslmodel import DSLModel
from dslmodel.utils.dspy_tools import init_lm


class GenerationType(Enum):
    """Types of artifacts to generate"""
    MODEL = "model"
    CLI = "cli" 
    TEST = "test"
    DOC = "doc"
    ALL = "all"


@dataclass
class GenerationResult:
    """Result of generation process"""
    artifact_type: str
    file_path: Path
    success: bool
    content_preview: str
    telemetry_spans: List[str]
    validation_errors: List[str] = None


class WeaverEngine:
    """
    Core engine that transforms semantic conventions into working code.
    
    Philosophy: Define telemetry once, generate everything else automatically.
    """
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("src/dslmodel/registry")
        self.templates_path = self.registry_path / "templates"
        self.output_path = Path("src/dslmodel/generated")
        
        # Ensure directories exist
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        logger.info(f"🏗️  WeaverEngine initialized")
        logger.info(f"   Registry: {self.registry_path}")
        logger.info(f"   Templates: {self.templates_path}")
        logger.info(f"   Output: {self.output_path}")
    
    def load_semantic_convention(self, convention_name: str) -> Dict[str, Any]:
        """Load semantic convention from YAML file"""
        convention_file = self.registry_path / "semantic" / f"{convention_name}.yaml"
        
        if not convention_file.exists():
            raise FileNotFoundError(f"Semantic convention not found: {convention_file}")
        
        with open(convention_file, 'r') as f:
            convention = yaml.safe_load(f)
        
        logger.debug(f"📋 Loaded convention: {convention_name}")
        return convention
    
    def generate_model(self, convention_name: str) -> GenerationResult:
        """Generate Pydantic model from semantic convention"""
        convention = self.load_semantic_convention(convention_name)
        
        # Load model template
        try:
            template = self.jinja_env.get_template("python/model.py.j2")
        except Exception:
            # Create default template if not exists
            self._create_default_templates()
            template = self.jinja_env.get_template("python/model.py.j2")
        
        # Generate model code
        code = template.render(
            convention=convention,
            convention_name=convention_name,
            groups=convention.get('groups', [])
        )
        
        # Write to output
        output_file = self.output_path / "models" / f"{convention_name}.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)
        
        # Extract telemetry spans
        spans = []
        for group in convention.get('groups', []):
            if group.get('type') == 'span':
                spans.append(group.get('id', 'unknown'))
        
        return GenerationResult(
            artifact_type="model",
            file_path=output_file,
            success=True,
            content_preview=code[:200] + "...",
            telemetry_spans=spans
        )
    
    def generate_cli(self, convention_name: str) -> GenerationResult:
        """Generate CLI commands from semantic convention"""
        convention = self.load_semantic_convention(convention_name)
        
        template = self.jinja_env.get_template("cli/commands.py.j2")
        
        code = template.render(
            convention=convention,
            convention_name=convention_name,
            groups=convention.get('groups', [])
        )
        
        output_file = self.output_path / "cli" / f"{convention_name}_cli.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)
        
        spans = [g.get('id') for g in convention.get('groups', []) if g.get('type') == 'span']
        
        return GenerationResult(
            artifact_type="cli",
            file_path=output_file,
            success=True,
            content_preview=code[:200] + "...",
            telemetry_spans=spans
        )
    
    def generate_tests(self, convention_name: str) -> GenerationResult:
        """Generate test suite from semantic convention"""
        convention = self.load_semantic_convention(convention_name)
        
        template = self.jinja_env.get_template("tests/test_suite.py.j2")
        
        code = template.render(
            convention=convention,
            convention_name=convention_name,
            groups=convention.get('groups', [])
        )
        
        output_file = self.output_path / "tests" / f"test_{convention_name}.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)
        
        spans = [g.get('id') for g in convention.get('groups', []) if g.get('type') == 'span']
        
        return GenerationResult(
            artifact_type="test",
            file_path=output_file,
            success=True,
            content_preview=code[:200] + "...",
            telemetry_spans=spans
        )
    
    def generate_docs(self, convention_name: str) -> GenerationResult:
        """Generate documentation from semantic convention"""
        convention = self.load_semantic_convention(convention_name)
        
        template = self.jinja_env.get_template("docs/feature.md.j2")
        
        content = template.render(
            convention=convention,
            convention_name=convention_name,
            groups=convention.get('groups', [])
        )
        
        output_file = self.output_path / "docs" / f"{convention_name}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
        
        spans = [g.get('id') for g in convention.get('groups', []) if g.get('type') == 'span']
        
        return GenerationResult(
            artifact_type="doc",
            file_path=output_file,
            success=True,
            content_preview=content[:200] + "...",
            telemetry_spans=spans
        )
    
    def generate_all(self, convention_name: str) -> List[GenerationResult]:
        """Generate all artifacts for a semantic convention"""
        logger.info(f"🚀 Generating all artifacts for: {convention_name}")
        
        results = []
        
        try:
            # Generate in dependency order
            model_result = self.generate_model(convention_name)
            results.append(model_result)
            logger.success(f"✅ Generated model: {model_result.file_path}")
            
            cli_result = self.generate_cli(convention_name)
            results.append(cli_result)
            logger.success(f"✅ Generated CLI: {cli_result.file_path}")
            
            test_result = self.generate_tests(convention_name)
            results.append(test_result)
            logger.success(f"✅ Generated tests: {test_result.file_path}")
            
            doc_result = self.generate_docs(convention_name)
            results.append(doc_result)
            logger.success(f"✅ Generated docs: {doc_result.file_path}")
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            results.append(GenerationResult(
                artifact_type="error",
                file_path=Path("error"),
                success=False,
                content_preview=str(e),
                telemetry_spans=[],
                validation_errors=[str(e)]
            ))
        
        # Summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        logger.info(f"📊 Generation complete: {len(successful)} success, {len(failed)} failed")
        
        return results
    
    def validate_convention(self, convention_name: str) -> Dict[str, Any]:
        """Validate semantic convention structure"""
        try:
            convention = self.load_semantic_convention(convention_name)
            
            errors = []
            warnings = []
            
            # Check required fields
            if 'groups' not in convention:
                errors.append("Missing 'groups' field")
            
            for group in convention.get('groups', []):
                if 'id' not in group:
                    errors.append(f"Group missing 'id' field")
                if 'type' not in group:
                    warnings.append(f"Group {group.get('id', 'unknown')} missing 'type' field")
                
                # Validate attributes
                for attr in group.get('attributes', []):
                    if 'id' not in attr:
                        errors.append(f"Attribute missing 'id' in group {group.get('id')}")
                    if 'type' not in attr:
                        errors.append(f"Attribute {attr.get('id')} missing 'type'")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "groups_count": len(convention.get('groups', [])),
                "spans_count": len([g for g in convention.get('groups', []) if g.get('type') == 'span'])
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "groups_count": 0,
                "spans_count": 0
            }
    
    def list_conventions(self) -> List[str]:
        """List all available semantic conventions"""
        semantic_dir = self.registry_path / "semantic"
        if not semantic_dir.exists():
            return []
        
        conventions = []
        for yaml_file in semantic_dir.glob("*.yaml"):
            conventions.append(yaml_file.stem)
        
        return sorted(conventions)
    
    def _create_default_templates(self):
        """Create default Jinja templates for generation"""
        templates = {
            "python/model.py.j2": '''"""
{{ convention_name|title }} - Auto-generated from semantic convention
Generated by WeaverEngine - DO NOT EDIT MANUALLY
"""

from typing import Optional, List, Literal, Dict, Any
from pydantic import Field
from opentelemetry import trace
from dslmodel import DSLModel


{% for group in groups %}
{% if group.type == 'span' %}
class {{ group.id|replace('.', '_')|replace('-', '_')|title }}(DSLModel):
    """{{ group.brief or 'Generated telemetry model' }}"""
    
    {% for attr in group.attributes %}
    {% if attr.type == 'string' %}
    {{ attr.id|replace('.', '_') }}: {% if attr.requirement_level == 'required' %}str{% else %}Optional[str] = None{% endif %} = Field(
        {% if attr.requirement_level == 'required' %}...{% else %}None{% endif %},
        description="{{ attr.brief or 'Generated attribute' }}"
        {% if attr.examples %}, examples={{ attr.examples }}{% endif %}
    )
    {% elif attr.type == 'int' %}
    {{ attr.id|replace('.', '_') }}: {% if attr.requirement_level == 'required' %}int{% else %}Optional[int] = None{% endif %} = Field(
        {% if attr.requirement_level == 'required' %}...{% else %}None{% endif %},
        description="{{ attr.brief or 'Generated attribute' }}"
    )
    {% elif attr.type == 'boolean' %}
    {{ attr.id|replace('.', '_') }}: {% if attr.requirement_level == 'required' %}bool{% else %}Optional[bool] = None{% endif %} = Field(
        {% if attr.requirement_level == 'required' %}...{% else %}None{% endif %},
        description="{{ attr.brief or 'Generated attribute' }}"
    )
    {% else %}
    {{ attr.id|replace('.', '_') }}: {% if attr.requirement_level == 'required' %}str{% else %}Optional[str] = None{% endif %} = Field(
        {% if attr.requirement_level == 'required' %}...{% else %}None{% endif %},
        description="{{ attr.brief or 'Generated attribute' }}"
    )
    {% endif %}
    {% endfor %}
    
    def emit_telemetry(self) -> str:
        """Emit telemetry span for this model"""
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span("{{ group.id }}") as span:
            {% for attr in group.attributes %}
            if self.{{ attr.id|replace('.', '_') }} is not None:
                span.set_attribute("{{ group.prefix or group.id }}.{{ attr.id }}", self.{{ attr.id|replace('.', '_') }})
            {% endfor %}
            
            return span.get_span_context().trace_id.to_bytes(16, 'big').hex()
        
{% endif %}
{% endfor %}
''',
            "cli/commands.py.j2": '''"""
{{ convention_name|title }} CLI - Auto-generated from semantic convention
Generated by WeaverEngine - DO NOT EDIT MANUALLY
"""

import typer
from typing import Optional
from loguru import logger
from pathlib import Path

from ..models.{{ convention_name }} import *

app = typer.Typer(help="{{ convention_name|title }} commands")

{% for group in groups %}
{% if group.type == 'span' %}
@app.command("{{ group.id|replace('.', '-')|replace('_', '-') }}")
def {{ group.id|replace('.', '_')|replace('-', '_') }}_command(
    {% for attr in group.attributes %}
    {% if attr.requirement_level == 'required' %}
    {{ attr.id|replace('.', '_')|replace('-', '_') }}: str = typer.Argument(..., help="{{ attr.brief or 'Generated parameter' }}"),
    {% else %}
    {{ attr.id|replace('.', '_')|replace('-', '_') }}: Optional[str] = typer.Option(None, help="{{ attr.brief or 'Generated parameter' }}"),
    {% endif %}
    {% endfor %}
):
    """{{ group.brief or 'Generated command' }}"""
    
    # Create model instance
    model = {{ group.id|replace('.', '_')|replace('-', '_')|title }}(
        {% for attr in group.attributes %}
        {{ attr.id|replace('.', '_') }}={{ attr.id|replace('.', '_')|replace('-', '_') }},
        {% endfor %}
    )
    
    # Emit telemetry
    trace_id = model.emit_telemetry()
    
    logger.success(f"✅ {{ group.id }} executed successfully!")
    logger.info(f"📊 Trace ID: {trace_id}")
    
    return model.model_dump()

{% endif %}
{% endfor %}

if __name__ == "__main__":
    app()
''',
            "tests/test_suite.py.j2": '''"""
Test suite for {{ convention_name|title }}
Auto-generated from semantic convention - DO NOT EDIT MANUALLY
"""

import pytest
from unittest.mock import Mock, patch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ..models.{{ convention_name }} import *


class Test{{ convention_name|title }}:
    """Auto-generated test suite for {{ convention_name }}"""
    
    def setup_method(self):
        """Setup test environment with in-memory span collection"""
        self.span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    {% for group in groups %}
    {% if group.type == 'span' %}
    def test_{{ group.id|replace('.', '_')|replace('-', '_') }}_model_creation(self):
        """Test {{ group.id }} model can be created"""
        model = {{ group.id|replace('.', '_')|replace('-', '_')|title }}(
            {% for attr in group.attributes %}
            {% if attr.requirement_level == 'required' %}
            {{ attr.id|replace('.', '_') }}="test_value",
            {% endif %}
            {% endfor %}
        )
        
        assert model is not None
        {% for attr in group.attributes %}
        {% if attr.requirement_level == 'required' %}
        assert model.{{ attr.id|replace('.', '_') }} == "test_value"
        {% endif %}
        {% endfor %}
    
    def test_{{ group.id|replace('.', '_')|replace('-', '_') }}_telemetry_emission(self):
        """Test {{ group.id }} emits correct telemetry"""
        model = {{ group.id|replace('.', '_')|replace('-', '_')|title }}(
            {% for attr in group.attributes %}
            {% if attr.requirement_level == 'required' %}
            {{ attr.id|replace('.', '_') }}="test_value",
            {% endif %}
            {% endfor %}
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "{{ group.id }}"
        
        # Verify attributes
        {% for attr in group.attributes %}
        {% if attr.requirement_level == 'required' %}
        assert "{{ group.prefix or group.id }}.{{ attr.id }}" in span.attributes
        assert span.attributes["{{ group.prefix or group.id }}.{{ attr.id }}"] == "test_value"
        {% endif %}
        {% endfor %}
    
    {% endif %}
    {% endfor %}
''',
            "docs/feature.md.j2": '''# {{ convention_name|title }}

**Auto-generated from semantic convention** - Last updated: {{ "now"|strftime("%Y-%m-%d %H:%M") }}

## Overview

{% if groups %}
{% for group in groups %}
{% if group.brief %}
{{ group.brief }}
{% endif %}
{% endfor %}
{% endif %}

## Telemetry Spans

{% for group in groups %}
{% if group.type == 'span' %}
### {{ group.id }}

**Type:** {{ group.type }}  
**Brief:** {{ group.brief or 'No description' }}

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
{% for attr in group.attributes %}
| `{{ attr.id }}` | {{ attr.type }} | {{ attr.requirement_level }} | {{ attr.brief or 'No description' }} |
{% endfor %}

#### Example Usage

```python
from dslmodel.generated.models.{{ convention_name }} import {{ group.id|replace('.', '_')|replace('-', '_')|title }}

# Create model
model = {{ group.id|replace('.', '_')|replace('-', '_')|title }}(
    {% for attr in group.attributes %}
    {% if attr.requirement_level == 'required' %}
    {{ attr.id|replace('.', '_') }}="example_value",
    {% endif %}
    {% endfor %}
)

# Emit telemetry
trace_id = model.emit_telemetry()
print(f"Telemetry emitted: {trace_id}")
```

#### CLI Usage

```bash
dsl {{ convention_name|replace('_', '-') }} {{ group.id|replace('.', '-')|replace('_', '-') }} \\
    {% for attr in group.attributes %}
    {% if attr.requirement_level == 'required' %}
    --{{ attr.id|replace('.', '-')|replace('_', '-') }} "value" \\
    {% endif %}
    {% endfor %}
```

{% endif %}
{% endfor %}

## Validation

All generated code includes automatic validation:

- ✅ Type safety through Pydantic models
- ✅ Required attribute validation
- ✅ OpenTelemetry span emission
- ✅ Comprehensive test coverage

## Files Generated

- `models/{{ convention_name }}.py` - Pydantic models
- `cli/{{ convention_name }}_cli.py` - CLI commands  
- `tests/test_{{ convention_name }}.py` - Test suite
- `docs/{{ convention_name }}.md` - This documentation

---

*Generated by WeaverEngine from semantic convention `{{ convention_name }}.yaml`*
'''
        }
        
        # Create template files
        for template_path, content in templates.items():
            full_path = self.templates_path / template_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        logger.info("📄 Created default templates")


def main():
    """CLI interface for WeaverEngine"""
    engine = WeaverEngine()
    
    # Example usage
    conventions = engine.list_conventions()
    logger.info(f"Available conventions: {conventions}")
    
    if conventions:
        # Generate all artifacts for first convention
        results = engine.generate_all(conventions[0])
        for result in results:
            logger.info(f"Generated: {result.artifact_type} -> {result.file_path}")


if __name__ == "__main__":
    main()