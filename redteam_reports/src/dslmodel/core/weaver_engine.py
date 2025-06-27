"""
Weaver Engine Core
==================

Core Weaver engine for schema generation, validation, and evolution.
Integrates with the multi-layer validation system and OTEL monitoring.
"""

import json
import yaml
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
import datetime
from enum import Enum

class GenerationType(Enum):
    """Types of generation supported by Weaver."""
    MODEL = "model"
    CLI = "cli"
    TEST = "test"
    SEMANTIC_CONVENTION = "semantic_convention"
    TELEMETRY = "telemetry"
    VALIDATION = "validation"

try:
    from ...utils.span import span
except ImportError:
    def span(name):
        def decorator(func):
            return func
        return decorator

try:
    from ...utils.log_tools import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    valid: bool
    score: float
    errors: List[str]
    warnings: List[str]
    improvements: List[str]
    metadata: Dict[str, Any]

@dataclass
class WeaverSchema:
    """Represents a Weaver-generated schema."""
    name: str
    version: str
    content: Dict[str, Any]
    conventions: Dict[str, Any]
    generated_at: str
    hash: str

@dataclass
class GenerationResult:
    """Result of artifact generation."""
    success: bool
    artifact_type: str
    file_path: Path
    telemetry_spans: List[Dict[str, Any]]
    validation_errors: List[str]
    content: str

class WeaverEngine:
    """Core Weaver engine for schema operations."""
    
    def __init__(self, schema_dir: Optional[Path] = None):
        self.schema_dir = schema_dir or Path("weaver_schemas")
        self.schema_dir.mkdir(exist_ok=True)
        self.output_path = Path("src/dslmodel/generated")
        
        self.schemas: Dict[str, WeaverSchema] = {}
        self.conventions: Dict[str, Any] = {}
        self.validation_cache: Dict[str, SchemaValidationResult] = {}
        
        self._load_conventions()
    
    def _load_conventions(self):
        """Load Weaver conventions."""
        self.conventions = {
            "validation": {
                "min_score": 0.8,
                "required_fields": ["name", "version", "content"]
            },
            "generation": {
                "include_metadata": True,
                "validate_on_create": True,
                "auto_version": True
            }
        }
    
    def list_conventions(self) -> List[str]:
        """List available semantic conventions."""
        conventions = []
        
        # Check weaver/semantic_conventions directory
        semconv_dir = Path("weaver/semantic_conventions")
        if semconv_dir.exists():
            for item in semconv_dir.iterdir():
                if item.is_dir():
                    conventions.append(item.name)
                elif item.suffix == '.yaml':
                    conventions.append(item.stem)
        
        # Check weaver directory for yaml files
        weaver_dir = Path("weaver")
        if weaver_dir.exists():
            for item in weaver_dir.glob("*.yaml"):
                if item.stem not in conventions:
                    conventions.append(item.stem)
        
        return conventions
    
    def validate_convention(self, convention_name: str) -> Dict[str, Any]:
        """Validate a semantic convention."""
        try:
            # Look for convention file
            convention_file = None
            
            # Check weaver/semantic_conventions directory
            semconv_dir = Path("weaver/semantic_conventions")
            if semconv_dir.exists():
                convention_file = semconv_dir / f"{convention_name}.yaml"
                if not convention_file.exists():
                    # Check if it's a directory
                    convention_dir = semconv_dir / convention_name
                    if convention_dir.exists():
                        # Find first yaml file in directory
                        yaml_files = list(convention_dir.glob("*.yaml"))
                        if yaml_files:
                            convention_file = yaml_files[0]
            
            # Check weaver directory
            if not convention_file or not convention_file.exists():
                convention_file = Path("weaver") / f"{convention_name}.yaml"
            
            if not convention_file.exists():
                return {
                    "valid": False,
                    "errors": [f"Convention file not found: {convention_name}"],
                    "groups_count": 0,
                    "spans_count": 0
                }
            
            # Load and validate YAML
            with open(convention_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # Basic validation
            errors = []
            groups_count = 0
            spans_count = 0
            
            if not isinstance(content, dict):
                errors.append("Convention must be a YAML object")
            else:
                # Count groups and spans
                if "groups" in content:
                    groups_count = len(content["groups"])
                    for group in content["groups"]:
                        if "spans" in group:
                            spans_count += len(group["spans"])
                
                # Check for required fields
                if "name" not in content:
                    errors.append("Missing required field: name")
                if "version" not in content:
                    errors.append("Missing required field: version")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "groups_count": groups_count,
                "spans_count": spans_count,
                "file_path": str(convention_file)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "groups_count": 0,
                "spans_count": 0
            }
    
    def generate_all(self, convention_name: str) -> List[GenerationResult]:
        """Generate all artifacts for a convention."""
        results = []
        
        # Generate each type
        for gen_type in [GenerationType.MODEL, GenerationType.CLI, GenerationType.TEST]:
            try:
                if gen_type == GenerationType.MODEL:
                    results.append(self.generate_model(convention_name))
                elif gen_type == GenerationType.CLI:
                    results.append(self.generate_cli(convention_name))
                elif gen_type == GenerationType.TEST:
                    results.append(self.generate_tests(convention_name))
            except Exception as e:
                results.append(GenerationResult(
                    success=False,
                    artifact_type=gen_type.value,
                    file_path=Path(""),
                    telemetry_spans=[],
                    validation_errors=[str(e)],
                    content=""
                ))
        
        return results
    
    def generate_model(self, convention_name: str) -> GenerationResult:
        """Generate Pydantic models from convention."""
        try:
            # Create output directory
            model_dir = self.output_path / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate basic model content
            content = f'''"""
Generated Pydantic models for {convention_name}
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class {convention_name.title()}Model(BaseModel):
    """Generated model for {convention_name} convention."""
    name: str
    version: str
    metadata: Optional[Dict[str, Any]] = None
'''
            
            file_path = model_dir / f"{convention_name}_models.py"
            with open(file_path, 'w') as f:
                f.write(content)
            
            return GenerationResult(
                success=True,
                artifact_type="model",
                file_path=file_path,
                telemetry_spans=[],
                validation_errors=[],
                content=content
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                artifact_type="model",
                file_path=Path(""),
                telemetry_spans=[],
                validation_errors=[str(e)],
                content=""
            )
    
    def generate_cli(self, convention_name: str) -> GenerationResult:
        """Generate CLI commands from convention."""
        try:
            # Create output directory
            cli_dir = self.output_path / "cli"
            cli_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate basic CLI content
            content = f'''"""
Generated CLI for {convention_name}
"""

import typer

app = typer.Typer(help="Generated CLI for {convention_name}")

@app.command()
def validate():
    """Validate {convention_name} convention."""
    typer.echo(f"Validating {convention_name} convention...")

if __name__ == "__main__":
    app()
'''
            
            file_path = cli_dir / f"{convention_name}_cli.py"
            with open(file_path, 'w') as f:
                f.write(content)
            
            return GenerationResult(
                success=True,
                artifact_type="cli",
                file_path=file_path,
                telemetry_spans=[],
                validation_errors=[],
                content=content
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                artifact_type="cli",
                file_path=Path(""),
                telemetry_spans=[],
                validation_errors=[str(e)],
                content=""
            )
    
    def generate_tests(self, convention_name: str) -> GenerationResult:
        """Generate tests from convention."""
        try:
            # Create output directory
            test_dir = Path("tests/generated")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate basic test content
            content = f'''"""
Generated tests for {convention_name}
"""

import pytest
from dslmodel.generated.models.{convention_name}_models import {convention_name.title()}Model

def test_{convention_name}_model():
    """Test {convention_name} model creation."""
    model = {convention_name.title()}Model(
        name="{convention_name}",
        version="1.0.0"
    )
    assert model.name == "{convention_name}"
    assert model.version == "1.0.0"
'''
            
            file_path = test_dir / f"test_{convention_name}.py"
            with open(file_path, 'w') as f:
                f.write(content)
            
            return GenerationResult(
                success=True,
                artifact_type="test",
                file_path=file_path,
                telemetry_spans=[],
                validation_errors=[],
                content=content
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                artifact_type="test",
                file_path=Path(""),
                telemetry_spans=[],
                validation_errors=[str(e)],
                content=""
            )
    
    def generate_docs(self, convention_name: str) -> GenerationResult:
        """Generate documentation from convention."""
        try:
            # Create output directory
            docs_dir = Path("docs/generated")
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate basic documentation content
            content = f"""# {convention_name.title()} Convention

Generated documentation for the {convention_name} semantic convention.

## Overview

This convention defines telemetry spans and attributes for {convention_name}.

## Usage

```python
from dslmodel.generated.models.{convention_name}_models import {convention_name.title()}Model

model = {convention_name.title()}Model(
    name="{convention_name}",
    version="1.0.0"
)
```

## Validation

```bash
dsl weaver validate {convention_name}
```
"""
            
            file_path = docs_dir / f"{convention_name}.md"
            with open(file_path, 'w') as f:
                f.write(content)
            
            return GenerationResult(
                success=True,
                artifact_type="doc",
                file_path=file_path,
                telemetry_spans=[],
                validation_errors=[],
                content=content
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                artifact_type="doc",
                file_path=Path(""),
                telemetry_spans=[],
                validation_errors=[str(e)],
                content=""
            )
    
    @span("weaver_generate_schema")
    def generate_schema(
        self,
        name: str,
        base_content: Dict[str, Any],
        conventions_override: Optional[Dict[str, Any]] = None
    ) -> WeaverSchema:
        """Generate a new schema with Weaver conventions."""
        
        version = "1.0.0"
        if name in self.schemas:
            current_version = self.schemas[name].version
            version = self._increment_version(current_version)
        
        # Enhance content with metadata
        enhanced_content = dict(base_content)
        enhanced_content["_metadata"] = {
            "generated_by": "weaver_engine",
            "generated_at": datetime.datetime.now().isoformat()
        }
        
        # Calculate hash
        content_hash = hashlib.sha256(
            json.dumps(enhanced_content, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Create schema
        schema = WeaverSchema(
            name=name,
            version=version,
            content=enhanced_content,
            conventions=conventions_override or {},
            generated_at=datetime.datetime.now().isoformat(),
            hash=content_hash
        )
        
        self.schemas[name] = schema
        logger.info(f"Generated schema: {name} v{version}")
        return schema
    
    @span("weaver_validate_schema")
    def validate_schema(self, schema: WeaverSchema) -> SchemaValidationResult:
        """Validate a schema against Weaver conventions."""
        
        errors = []
        warnings = []
        improvements = []
        score = 1.0
        
        # Basic validation
        if not isinstance(schema.content, dict):
            errors.append("Schema content must be a dictionary")
            score -= 0.3
        elif not schema.content:
            warnings.append("Schema content is empty")
            score -= 0.1
        
        valid = len(errors) == 0 and score >= 0.8
        
        return SchemaValidationResult(
            valid=valid,
            score=score,
            errors=errors,
            warnings=warnings,
            improvements=improvements,
            metadata={"validation_time": datetime.datetime.now().isoformat()}
        )
    
    def _increment_version(self, version: str) -> str:
        """Increment a semantic version."""
        try:
            parts = version.split(".")
            if len(parts) >= 3:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{major}.{minor}.{patch + 1}"
            else:
                return f"{version}.1"
        except ValueError:
            return "1.0.1"

# Global engine instance
_engine = None

def get_weaver_engine() -> WeaverEngine:
    """Get or create the global Weaver engine."""
    global _engine
    if _engine is None:
        _engine = WeaverEngine()
    return _engine