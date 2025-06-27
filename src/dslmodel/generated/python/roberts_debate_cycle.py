"""Roberts Rules debate cycle span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class roberts_debate_cycle_span:
    @staticmethod
    def span():
        return trace.get_current_span()