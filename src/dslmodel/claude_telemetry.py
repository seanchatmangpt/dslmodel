#!/usr/bin/env python3
"""
Claude Self-Telemetry System
Generated from semantic conventions using weaver-first approach
Maps Claude's cognitive processes into OTEL spans
"""

import time
import functools
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# OTEL imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace import Status, StatusCode

# Setup Claude telemetry
if not hasattr(trace, '_claude_initialized'):
    resource = Resource(attributes={SERVICE_NAME: "claude-assistant"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(console_processor)
    trace._claude_initialized = True

tracer = trace.get_tracer("claude.cognitive")

@dataclass
class ClaudeRequest:
    """Tracks Claude's request processing"""
    request_id: str
    input_tokens: int = 0
    complexity: str = "moderate"
    domain: str = "general"
    
    def __enter__(self):
        self.span = tracer.start_span("claude.request.process")
        self.span.set_attribute("claude.request.id", self.request_id)
        self.span.set_attribute("claude.request.input_tokens", self.input_tokens)
        self.span.set_attribute("claude.request.complexity", self.complexity)
        self.span.set_attribute("claude.request.domain", self.domain)
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        thinking_duration = (time.time() - self.start_time) * 1000
        self.span.set_attribute("claude.thinking.duration_ms", thinking_duration)
        
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()

@dataclass 
class ClaudeThinking:
    """Tracks Claude's analysis and thinking phase"""
    approach: str = "step_by_step"
    context_pieces: int = 0
    assumptions_identified: int = 0
    
    def __enter__(self):
        self.span = tracer.start_span("claude.thinking.analyze")
        self.span.set_attribute("claude.thinking.approach", self.approach)
        self.span.set_attribute("claude.thinking.context_pieces", self.context_pieces)
        self.span.set_attribute("claude.thinking.assumptions_identified", self.assumptions_identified)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()
    
    def add_risk(self, risk: str):
        """Add identified risk"""
        self.span.add_event("risk_identified", {"risk": risk})

@dataclass
class ClaudeToolUse:
    """Tracks Claude's tool usage"""
    tool_name: str
    purpose: str = ""
    
    def __enter__(self):
        self.span = tracer.start_span("claude.tool.use")
        self.span.set_attribute("claude.tool.name", self.tool_name)
        self.span.set_attribute("claude.tool.purpose", self.purpose)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        self.span.set_attribute("claude.tool.success", success)
        
        if exc_type:
            self.span.set_attribute("claude.tool.error_type", type(exc_val).__name__)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()

@dataclass
class ClaudeProblemSolve:
    """Tracks Claude's problem-solving process"""
    problem_type: str = "implement"
    steps_planned: int = 1
    
    def __enter__(self):
        self.span = tracer.start_span("claude.problem.solve")
        self.span.set_attribute("claude.problem.type", self.problem_type)
        self.span.set_attribute("claude.problem.steps_planned", self.steps_planned)
        self.iterations = 0
        self.blockers = 0
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.span.set_attribute("claude.problem.iterations", self.iterations)
        self.span.set_attribute("claude.problem.blockers_encountered", self.blockers)
        
        confidence = 0.8 if exc_type is None else 0.3
        self.span.set_attribute("claude.problem.solution_confidence", confidence)
        
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()
    
    def iterate(self):
        """Track iteration in problem solving"""
        self.iterations += 1
        self.span.add_event("iteration", {"iteration_number": self.iterations})
    
    def encounter_blocker(self, blocker: str):
        """Track blocker encountered"""
        self.blockers += 1
        self.span.add_event("blocker_encountered", {"blocker": blocker, "blocker_count": self.blockers})

@dataclass
class ClaudeValidation:
    """Tracks Claude's validation and verification"""
    validation_type: str = "logic_review"
    
    def __enter__(self):
        self.span = tracer.start_span("claude.validation.check")
        self.span.set_attribute("claude.validation.type", self.validation_type)
        self.tests_performed = 0
        self.issues_found = 0
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.span.set_attribute("claude.validation.tests_performed", self.tests_performed)
        self.span.set_attribute("claude.validation.issues_found", self.issues_found)
        
        confidence = max(0.2, 1.0 - (self.issues_found * 0.2))
        self.span.set_attribute("claude.validation.confidence_level", confidence)
        
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()
    
    def perform_test(self, test_name: str, passed: bool):
        """Track validation test"""
        self.tests_performed += 1
        if not passed:
            self.issues_found += 1
        
        self.span.add_event("validation_test", {
            "test_name": test_name,
            "passed": passed,
            "test_number": self.tests_performed
        })

@dataclass
class ClaudeResponse:
    """Tracks Claude's response formulation"""
    format_type: str = "text"
    output_tokens: int = 0
    
    def __enter__(self):
        self.span = tracer.start_span("claude.communication.respond")
        self.span.set_attribute("claude.response.format", self.format_type)
        self.span.set_attribute("claude.response.output_tokens", self.output_tokens)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        confidence = 0.8 if exc_type is None else 0.4
        self.span.set_attribute("claude.response.confidence", confidence)
        
        # Predict if follow-up will be needed
        follow_up_needed = self.output_tokens > 2000 or exc_type is not None
        self.span.set_attribute("claude.response.follow_up_needed", follow_up_needed)
        
        # Predict user satisfaction
        satisfaction = confidence * 0.9 if exc_type is None else 0.3
        self.span.set_attribute("claude.response.user_satisfaction_prediction", satisfaction)
        
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()

class ClaudeTelemetry:
    """Main telemetry interface for Claude's cognitive processes"""
    
    @staticmethod
    def request(request_id: str, input_tokens: int = 0, complexity: str = "moderate", domain: str = "general"):
        """Track request processing"""
        return ClaudeRequest(request_id, input_tokens, complexity, domain)
    
    @staticmethod
    def thinking(approach: str = "step_by_step", context_pieces: int = 0, assumptions: int = 0):
        """Track thinking and analysis"""
        return ClaudeThinking(approach, context_pieces, assumptions)
    
    @staticmethod
    def tool_use(tool_name: str, purpose: str = ""):
        """Track tool usage"""
        return ClaudeToolUse(tool_name, purpose)
    
    @staticmethod
    def problem_solve(problem_type: str = "implement", steps_planned: int = 1):
        """Track problem solving"""
        return ClaudeProblemSolve(problem_type, steps_planned)
    
    @staticmethod
    def validate(validation_type: str = "logic_review"):
        """Track validation"""
        return ClaudeValidation(validation_type)
    
    @staticmethod
    def respond(format_type: str = "text", output_tokens: int = 0):
        """Track response generation"""
        return ClaudeResponse(format_type, output_tokens)

# Decorator for automatic telemetry
def claude_telemetry(span_type: str = "claude.operation", **span_attrs):
    """Decorator to automatically add telemetry to functions"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_type) as span:
                # Set attributes
                for key, value in span_attrs.items():
                    span.set_attribute(key, value)
                
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.args_count", len(args))
                span.set_attribute("function.kwargs_count", len(kwargs))
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator

# Example usage and self-mapping demonstration
def demonstrate_claude_telemetry():
    """Demonstrate Claude's self-telemetry capabilities"""
    
    print("🧠 Claude Self-Telemetry Demonstration")
    print("=" * 40)
    
    # Simulate Claude processing a request
    with ClaudeTelemetry.request("demo_request_001", input_tokens=150, complexity="complex", domain="code"):
        
        # Thinking phase
        with ClaudeTelemetry.thinking(approach="research_first", context_pieces=5, assumptions=2) as thinking:
            thinking.add_risk("Complexity might require multiple iterations")
            time.sleep(0.1)  # Simulate thinking time
        
        # Problem solving
        with ClaudeTelemetry.problem_solve("implement", steps_planned=4) as solver:
            solver.iterate()
            time.sleep(0.05)
            
            solver.encounter_blocker("Missing dependency information")
            solver.iterate()
            time.sleep(0.05)
        
        # Tool usage
        with ClaudeTelemetry.tool_use("Read", "Examine existing code structure"):
            time.sleep(0.02)  # Simulate tool usage
        
        with ClaudeTelemetry.tool_use("Write", "Create new implementation"):
            time.sleep(0.03)  # Simulate tool usage
        
        # Validation
        with ClaudeTelemetry.validate("syntax_check") as validator:
            validator.perform_test("syntax_valid", True)
            validator.perform_test("logic_sound", True)
            validator.perform_test("performance_acceptable", False)  # Found issue
        
        # Response generation
        with ClaudeTelemetry.respond("code", output_tokens=500):
            time.sleep(0.02)  # Simulate response generation
    
    print("\n✅ Claude telemetry demonstration complete!")
    print("Check the OTEL spans above to see Claude's cognitive processes mapped to telemetry.")

if __name__ == "__main__":
    demonstrate_claude_telemetry()