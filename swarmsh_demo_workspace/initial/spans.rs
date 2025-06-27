// Auto-generated from thesis_complete.py
use opentelemetry::{trace::Tracer, KeyValue};

pub fn emit_thesis_spans(tracer: &dyn Tracer) {
    let swarmsh_thesis_telemetry_as_system = tracer
        .span_builder("swarmsh.thesis.telemetry_as_system")
        .with_attributes(vec![
            KeyValue::new("brief", "Telemetry is the system, not an add-on."),
        ])
        .start(tracer);
    swarmsh_thesis_telemetry_as_system.end();

    let swarmsh_thesis_span_drives_code = tracer
        .span_builder("swarmsh.thesis.span_drives_code")
        .with_attributes(vec![
            KeyValue::new("brief", "Spans generate code & CLI."),
        ])
        .start(tracer);
    swarmsh_thesis_span_drives_code.end();

    let swarmsh_thesis_trace_to_prompt_emergence = tracer
        .span_builder("swarmsh.thesis.trace_to_prompt_emergence")
        .with_attributes(vec![
            KeyValue::new("brief", "Traces → LLM prompts (emergent)."),
        ])
        .start(tracer);
    swarmsh_thesis_trace_to_prompt_emergence.end();

    let swarmsh_thesis_telemetry_communication_channel = tracer
        .span_builder("swarmsh.thesis.telemetry_communication_channel")
        .with_attributes(vec![
            KeyValue::new("brief", "Spans are the agent messaging bus."),
        ])
        .start(tracer);
    swarmsh_thesis_telemetry_communication_channel.end();

    let swarmsh_thesis_system_models_itself = tracer
        .span_builder("swarmsh.thesis.system_models_itself")
        .with_attributes(vec![
            KeyValue::new("brief", "Trace graph is a live self-model."),
        ])
        .start(tracer);
    swarmsh_thesis_system_models_itself.end();

}