"""Enums for semantic convention definitions."""

from enum import Enum


class AttrType(str, Enum):
    """Attribute types supported by OpenTelemetry."""
    string = "string"
    int = "int"
    double = "double"
    boolean = "boolean"
    string_array = "string[]"
    int_array = "int[]"
    double_array = "double[]"
    boolean_array = "boolean[]"


class Cardinality(str, Enum):
    """Requirement levels for attributes."""
    required = "required"
    recommended = "recommended"
    optional = "opt_in"


class SpanKind(str, Enum):
    """OpenTelemetry span kinds."""
    internal = "internal"
    server = "server"
    client = "client"
    producer = "producer"
    consumer = "consumer"