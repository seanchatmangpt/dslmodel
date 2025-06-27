"""Merge oracle span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class merge_oracle_span:
    @staticmethod
    def span():
        return trace.get_current_span()