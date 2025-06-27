"""Simple span decorator for OTEL integration"""

from contextlib import contextmanager
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@contextmanager
def span(name):
    """Context manager for creating OTEL spans"""
    with tracer.start_as_current_span(name) as s:
        yield s

def span_decorator(name):
    """Decorator version of span"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with span(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Alias for backward compatibility
span_fn = span_decorator