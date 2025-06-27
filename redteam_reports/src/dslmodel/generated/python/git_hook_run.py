"""Git hook run span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class git_hook_run_span:
    @staticmethod
    def span():
        return trace.get_current_span()