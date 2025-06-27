"""Roberts Rules agenda item span"""
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class roberts_agenda_item_span:
    @staticmethod
    def span():
        return trace.get_current_span()