#!/usr/bin/env python3
"""
SwarmSH Thesis Example App
Emits thesis spans to demonstrate the OTEL ecosystem loop
"""

import time
import random
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OTEL
resource = Resource.create({
    "service.name": "swarmsh-thesis",
    "service.version": "1.0.0"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("swarmsh.thesis")

def emit_thesis_spans():
    """Emit thesis demonstration spans"""
    with tracer.start_as_current_span("swarmsh.thesis.demo") as demo_span:
        demo_span.set_attribute("swarmsh.thesis.enabled", True)
        
        # Telemetry as system
        with tracer.start_as_current_span("swarmsh.thesis.telemetry_as_system") as span:
            span.set_attribute("validated", True)
            span.set_attribute("brief", "Telemetry is the system, not an add-on.")
            time.sleep(0.1)
        
        # Span drives code
        with tracer.start_as_current_span("swarmsh.thesis.span_drives_code") as span:
            span.set_attribute("code_generated", True)
            span.set_attribute("brief", "Spans generate code & CLI.")
            time.sleep(0.05)
            
            # Simulate slow operation sometimes
            if random.random() < 0.3:
                time.sleep(1.5)
                span.set_attribute("slow_operation", True)
        
        # Trace to prompt emergence
        with tracer.start_as_current_span("swarmsh.thesis.trace_to_prompt_emergence") as span:
            span.set_attribute("prompts_generated", random.randint(1, 5))
            span.set_attribute("brief", "Traces → LLM prompts (emergent).")
            time.sleep(0.08)
        
        # Communication channel
        with tracer.start_as_current_span("swarmsh.thesis.telemetry_communication_channel") as span:
            span.set_attribute("messages_passed", random.randint(10, 100))
            span.set_attribute("brief", "Spans are the agent messaging bus.")
            time.sleep(0.06)
            
            # Simulate errors sometimes
            if random.random() < 0.2:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Simulated error"))
                span.set_attribute("error", True)
        
        # System models itself
        with tracer.start_as_current_span("swarmsh.thesis.system_models_itself") as span:
            span.set_attribute("model_accuracy", random.uniform(0.8, 1.0))
            span.set_attribute("brief", "Trace graph is a live self-model.")
            time.sleep(0.07)

if __name__ == "__main__":
    print("SwarmSH Thesis Demo - Emitting spans...")
    for i in range(10):
        print(f"  Iteration {i+1}/10")
        emit_thesis_spans()
        time.sleep(1)
    print("Done!")
