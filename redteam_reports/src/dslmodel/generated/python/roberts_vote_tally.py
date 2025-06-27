"""Roberts Rules vote tally span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class roberts_vote_tally_span:
    @staticmethod
    def span():
        return trace.get_current_span()