"""Governance federated vote span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class governance_federated_vote_span:
    @staticmethod
    def span():
        return trace.get_current_span()