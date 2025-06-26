"""OpenTelemetry integration for DSLModel."""

from .otel_instrumentation import (
    OTelInstrumentation,
    SwarmSpanAttributes,
    init_otel,
    get_otel
)

__all__ = [
    "OTelInstrumentation",
    "SwarmSpanAttributes", 
    "init_otel",
    "get_otel"
]