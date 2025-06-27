"""OpenTelemetry integration for DSLModel."""

# Try to import real OTEL, fall back to mock implementation
try:
    from .otel_instrumentation import (
        OTelInstrumentation,
        SwarmSpanAttributes,
        init_otel,
        get_otel
    )
    OTEL_AVAILABLE = True
except ImportError:
    from .otel_instrumentation_mock import (
        OTelInstrumentation,
        SwarmSpanAttributes,
        init_otel,
        get_otel
    )
    OTEL_AVAILABLE = False

__all__ = [
    "OTelInstrumentation",
    "SwarmSpanAttributes", 
    "init_otel",
    "get_otel",
    "OTEL_AVAILABLE"
]