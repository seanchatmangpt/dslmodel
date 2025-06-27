"""OpenTelemetry ecosystem setup and configuration."""

from .setup import setup_otel, create_tracer, create_meter, OTEL_AVAILABLE

__all__ = ["setup_otel", "create_tracer", "create_meter", "OTEL_AVAILABLE"]