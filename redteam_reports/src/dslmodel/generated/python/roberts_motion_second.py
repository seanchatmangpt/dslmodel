"""Roberts Rules motion second span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class roberts_motion_second_span:
    @staticmethod
    def span():
        return trace.get_current_span()