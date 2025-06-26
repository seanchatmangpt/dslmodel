"""
DSLModel Weaver - OpenTelemetry semantic convention integration.

This module provides:
1. Python-based semantic convention definitions
2. SwarmAgent telemetry semantic conventions
3. Weaver templates and code generation
4. OpenTelemetry compliance validation
"""

from pathlib import Path

# Python-based convention definitions
from .models import ConventionSet, Span, Attribute
from .enums import AttrType, Cardinality, SpanKind

# Export key paths for external access
WEAVER_ROOT = Path(__file__).parent
REGISTRY_PATH = WEAVER_ROOT / "registry"
TEMPLATES_PATH = WEAVER_ROOT / "templates"
CONFIG_PATH = WEAVER_ROOT / "weaver.yaml"

__all__ = [
    # Python-based convention models
    "ConventionSet",
    "Span", 
    "Attribute",
    "AttrType",
    "Cardinality",
    "SpanKind",
    # Weaver integration paths
    "WEAVER_ROOT",
    "REGISTRY_PATH", 
    "TEMPLATES_PATH",
    "CONFIG_PATH"
]