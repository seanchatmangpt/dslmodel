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

class WeaverEngine:
    """Core Weaver engine for schema operations."""
    
    def __init__(self, schema_dir: Optional[Path] = None):
        self.schema_dir = schema_dir or Path("weaver_schemas")
        self.schema_dir.mkdir(exist_ok=True)
        
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