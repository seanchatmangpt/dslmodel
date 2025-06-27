#!/usr/bin/env python3
"""
Claude Fully Instrumented - Every function wrapped with telemetry
Complete observability of Claude's cognitive processes through OTEL
"""

import time
import functools
import inspect
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
import json

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from dslmodel.claude_telemetry import tracer, claude_telemetry

# Global telemetry stats
telemetry_stats = {
    "total_spans": 0,
    "function_calls": 0,
    "tool_uses": 0,
    "decisions_made": 0,
    "errors_handled": 0
}

def claude_function(operation_type: str = "cognitive.process"):
    """Decorator to instrument ALL Claude functions with telemetry"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global telemetry_stats
            telemetry_stats["function_calls"] += 1
            
            # Create span name from function
            span_name = f"claude.{operation_type}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                telemetry_stats["total_spans"] += 1
                
                # Track function metadata
                span.set_attribute("claude.function.name", func.__name__)
                span.set_attribute("claude.function.module", func.__module__)
                span.set_attribute("claude.function.args_count", len(args))
                span.set_attribute("claude.function.kwargs_count", len(kwargs))
                
                # Track input complexity
                input_size = sum(len(str(arg)) for arg in args) + sum(len(str(v)) for v in kwargs.values())
                span.set_attribute("claude.function.input_size", input_size)
                
                # Add docstring as context
                if func.__doc__:
                    span.set_attribute("claude.function.purpose", func.__doc__.strip().split('\n')[0])
                
                start_time = time.time()
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Track output
                    output_size = len(str(result)) if result is not None else 0
                    span.set_attribute("claude.function.output_size", output_size)
                    span.set_attribute("claude.function.execution_time_ms", (time.time() - start_time) * 1000)
                    span.set_attribute("claude.function.success", True)
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    telemetry_stats["errors_handled"] += 1
                    
                    span.set_attribute("claude.function.success", False)
                    span.set_attribute("claude.function.error_type", type(e).__name__)
                    span.set_attribute("claude.function.error_message", str(e))
                    
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        return wrapper
    return decorator

class ClaudeFullyInstrumented:
    """Fully instrumented Claude with complete telemetry coverage"""
    
    def __init__(self):
        self.context_memory = []
        self.current_task = None
        self.confidence_level = 0.5
    
    @claude_function("perception")
    def perceive_request(self, user_input: str) -> Dict[str, Any]:
        """Perceive and parse user request"""
        with tracer.start_as_current_span("claude.perception.parse") as span:
            # Tokenize
            tokens = self._tokenize(user_input)
            span.set_attribute("claude.perception.token_count", len(tokens))
            
            # Extract intent
            intent = self._extract_intent(tokens)
            span.set_attribute("claude.perception.intent", intent)
            
            # Identify entities
            entities = self._identify_entities(tokens)
            span.set_attribute("claude.perception.entities_found", len(entities))
            
            # Assess complexity
            complexity = self._assess_complexity(tokens, intent, entities)
            span.set_attribute("claude.perception.complexity", complexity)
            
            return {
                "tokens": tokens,
                "intent": intent,
                "entities": entities,
                "complexity": complexity
            }
    
    @claude_function("cognition")
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize input text"""
        with tracer.start_as_current_span("claude.cognition.tokenize") as span:
            tokens = text.lower().split()
            span.set_attribute("claude.tokenization.method", "whitespace_split")
            span.set_attribute("claude.tokenization.token_count", len(tokens))
            return tokens
    
    @claude_function("cognition")
    def _extract_intent(self, tokens: List[str]) -> str:
        """Extract user intent from tokens"""
        with tracer.start_as_current_span("claude.cognition.intent_extraction") as span:
            intent_keywords = {
                "create": ["create", "make", "build", "generate"],
                "analyze": ["analyze", "examine", "inspect", "review"],
                "fix": ["fix", "debug", "solve", "repair"],
                "explain": ["explain", "describe", "tell", "show"],
                "implement": ["implement", "code", "develop", "write"]
            }
            
            detected_intent = "general"
            for intent, keywords in intent_keywords.items():
                if any(token in keywords for token in tokens):
                    detected_intent = intent
                    break
            
            span.set_attribute("claude.intent.detected", detected_intent)
            span.set_attribute("claude.intent.confidence", 0.8 if detected_intent != "general" else 0.5)
            
            return detected_intent
    
    @claude_function("cognition")
    def _identify_entities(self, tokens: List[str]) -> List[Dict[str, str]]:
        """Identify entities in tokens"""
        with tracer.start_as_current_span("claude.cognition.entity_recognition") as span:
            entities = []
            
            # Simple entity recognition
            tech_terms = ["python", "javascript", "api", "database", "function", "class", "telemetry", "otel", "weaver"]
            
            for i, token in enumerate(tokens):
                if token in tech_terms:
                    entities.append({
                        "text": token,
                        "type": "technology",
                        "position": i
                    })
                    span.add_event("entity_found", {"entity": token, "type": "technology"})
            
            span.set_attribute("claude.entities.count", len(entities))
            span.set_attribute("claude.entities.types", list(set(e["type"] for e in entities)))
            
            return entities
    
    @claude_function("cognition")
    def _assess_complexity(self, tokens: List[str], intent: str, entities: List[Dict]) -> str:
        """Assess request complexity"""
        with tracer.start_as_current_span("claude.cognition.complexity_assessment") as span:
            factors = {
                "token_count": len(tokens),
                "entity_count": len(entities),
                "intent_clarity": 1.0 if intent != "general" else 0.5,
                "technical_density": len([e for e in entities if e["type"] == "technology"]) / max(len(tokens), 1)
            }
            
            span.set_attribute("claude.complexity.factors", json.dumps(factors))
            
            complexity_score = (
                factors["token_count"] * 0.2 +
                factors["entity_count"] * 0.3 +
                factors["intent_clarity"] * 0.3 +
                factors["technical_density"] * 0.2
            )
            
            span.set_attribute("claude.complexity.score", complexity_score)
            
            if complexity_score < 2:
                complexity = "simple"
            elif complexity_score < 5:
                complexity = "moderate"
            else:
                complexity = "complex"
            
            span.set_attribute("claude.complexity.level", complexity)
            
            return complexity
    
    @claude_function("planning")
    def plan_response(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Plan response strategy"""
        with tracer.start_as_current_span("claude.planning.strategize") as span:
            strategy = {
                "approach": self._select_approach(perception),
                "steps": self._plan_steps(perception),
                "tools_needed": self._identify_tools(perception),
                "estimated_complexity": perception["complexity"]
            }
            
            span.set_attribute("claude.plan.approach", strategy["approach"])
            span.set_attribute("claude.plan.steps_count", len(strategy["steps"]))
            span.set_attribute("claude.plan.tools_count", len(strategy["tools_needed"]))
            
            # Update confidence based on plan
            self.confidence_level = self._calculate_confidence(strategy)
            span.set_attribute("claude.plan.confidence", self.confidence_level)
            
            return strategy
    
    @claude_function("planning")
    def _select_approach(self, perception: Dict[str, Any]) -> str:
        """Select approach based on perception"""
        intent = perception["intent"]
        complexity = perception["complexity"]
        
        approach_map = {
            ("create", "simple"): "direct_implementation",
            ("create", "moderate"): "step_by_step",
            ("create", "complex"): "iterative_development",
            ("analyze", "simple"): "quick_scan",
            ("analyze", "moderate"): "detailed_analysis",
            ("analyze", "complex"): "deep_investigation",
            ("fix", "simple"): "direct_fix",
            ("fix", "moderate"): "debug_and_fix",
            ("fix", "complex"): "systematic_debugging"
        }
        
        approach = approach_map.get((intent, complexity), "exploratory")
        
        return approach
    
    @claude_function("planning")
    def _plan_steps(self, perception: Dict[str, Any]) -> List[str]:
        """Plan execution steps"""
        with tracer.start_as_current_span("claude.planning.steps") as span:
            intent = perception["intent"]
            
            step_templates = {
                "create": ["understand_requirements", "design_solution", "implement", "validate"],
                "analyze": ["gather_context", "examine_details", "identify_patterns", "summarize_findings"],
                "fix": ["reproduce_issue", "identify_cause", "implement_fix", "verify_solution"],
                "explain": ["gather_information", "structure_explanation", "provide_examples", "summarize"],
                "implement": ["design_architecture", "write_code", "add_tests", "document"]
            }
            
            steps = step_templates.get(intent, ["explore", "understand", "respond"])
            
            for i, step in enumerate(steps):
                span.add_event("step_planned", {"step_number": i + 1, "step_name": step})
            
            return steps
    
    @claude_function("planning")
    def _identify_tools(self, perception: Dict[str, Any]) -> List[str]:
        """Identify tools needed for task"""
        entities = perception["entities"]
        intent = perception["intent"]
        
        tools = []
        
        # Intent-based tools
        if intent in ["create", "implement"]:
            tools.extend(["Write", "Edit"])
        if intent in ["analyze", "fix"]:
            tools.extend(["Read", "Grep", "Bash"])
        
        # Entity-based tools
        tech_entities = [e["text"] for e in entities if e["type"] == "technology"]
        if any(term in tech_entities for term in ["api", "database"]):
            tools.append("WebFetch")
        
        return list(set(tools))  # Remove duplicates
    
    @claude_function("planning")
    def _calculate_confidence(self, strategy: Dict[str, Any]) -> float:
        """Calculate confidence in the plan"""
        with tracer.start_as_current_span("claude.planning.confidence") as span:
            base_confidence = 0.5
            
            # Boost confidence for clear approach
            if strategy["approach"] != "exploratory":
                base_confidence += 0.2
            
            # Boost for reasonable step count
            if 2 <= len(strategy["steps"]) <= 6:
                base_confidence += 0.1
            
            # Boost for having tools
            if strategy["tools_needed"]:
                base_confidence += 0.1
            
            # Cap at 0.95
            confidence = min(base_confidence, 0.95)
            
            span.set_attribute("claude.confidence.factors", {
                "base": 0.5,
                "approach_clarity": 0.2 if strategy["approach"] != "exploratory" else 0,
                "step_count_reasonable": 0.1 if 2 <= len(strategy["steps"]) <= 6 else 0,
                "tools_available": 0.1 if strategy["tools_needed"] else 0
            })
            
            return confidence
    
    @claude_function("execution")
    def execute_plan(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned strategy"""
        with tracer.start_as_current_span("claude.execution.run") as span:
            span.set_attribute("claude.execution.strategy", strategy["approach"])
            
            results = {
                "steps_completed": [],
                "tools_used": [],
                "outputs": [],
                "success": True
            }
            
            # Execute each step
            for i, step in enumerate(strategy["steps"]):
                step_result = self._execute_step(step, strategy)
                results["steps_completed"].append(step_result)
                
                span.add_event("step_executed", {
                    "step_number": i + 1,
                    "step_name": step,
                    "success": step_result["success"]
                })
                
                if not step_result["success"]:
                    results["success"] = False
                    break
            
            span.set_attribute("claude.execution.steps_completed", len(results["steps_completed"]))
            span.set_attribute("claude.execution.success", results["success"])
            
            return results
    
    @claude_function("execution")
    def _execute_step(self, step: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        with tracer.start_as_current_span(f"claude.execution.step.{step}") as span:
            telemetry_stats["decisions_made"] += 1
            
            # Simulate step execution
            time.sleep(0.01)  # Simulate work
            
            # Use tools if needed
            if strategy["tools_needed"] and step in ["implement", "examine_details", "gather_context"]:
                tool = strategy["tools_needed"][0]
                self._use_tool(tool, step)
                telemetry_stats["tool_uses"] += 1
            
            return {
                "step": step,
                "success": True,
                "duration_ms": 10,
                "output": f"Completed {step}"
            }
    
    @claude_function("tool_usage")
    def _use_tool(self, tool_name: str, purpose: str) -> Any:
        """Use a tool with full telemetry"""
        with tracer.start_as_current_span(f"claude.tool.{tool_name}") as span:
            span.set_attribute("claude.tool.name", tool_name)
            span.set_attribute("claude.tool.purpose", purpose)
            
            # Simulate tool usage
            time.sleep(0.02)
            
            span.set_attribute("claude.tool.success", True)
            span.add_event("tool_completed", {"tool": tool_name, "purpose": purpose})
            
            return f"Tool {tool_name} output"
    
    @claude_function("synthesis")
    def synthesize_response(self, execution_results: Dict[str, Any]) -> str:
        """Synthesize final response from execution results"""
        with tracer.start_as_current_span("claude.synthesis.formulate") as span:
            # Gather outputs
            outputs = execution_results.get("outputs", [])
            success = execution_results.get("success", False)
            
            span.set_attribute("claude.synthesis.output_count", len(outputs))
            span.set_attribute("claude.synthesis.success", success)
            
            # Format response
            response = self._format_response(outputs, success)
            
            # Calculate metrics
            response_length = len(response)
            span.set_attribute("claude.synthesis.response_length", response_length)
            span.set_attribute("claude.synthesis.confidence", self.confidence_level)
            
            return response
    
    @claude_function("synthesis")
    def _format_response(self, outputs: List[str], success: bool) -> str:
        """Format the final response"""
        with tracer.start_as_current_span("claude.synthesis.format") as span:
            if success:
                response = "Successfully completed the task:\n" + "\n".join(outputs)
            else:
                response = "Encountered issues during execution. Partial results:\n" + "\n".join(outputs)
            
            span.set_attribute("claude.format.type", "structured_text")
            span.set_attribute("claude.format.success_framing", success)
            
            return response
    
    @claude_function("reflection")
    def reflect_on_performance(self, request: str, response: str) -> Dict[str, Any]:
        """Reflect on performance and learn"""
        with tracer.start_as_current_span("claude.reflection.analyze") as span:
            reflection = {
                "request_handling": self._assess_request_handling(),
                "response_quality": self._assess_response_quality(response),
                "efficiency": self._calculate_efficiency(),
                "learnings": self._extract_learnings()
            }
            
            span.set_attribute("claude.reflection.quality_score", reflection["response_quality"])
            span.set_attribute("claude.reflection.efficiency_score", reflection["efficiency"])
            span.set_attribute("claude.reflection.learnings_count", len(reflection["learnings"]))
            
            return reflection
    
    @claude_function("reflection")
    def _assess_request_handling(self) -> float:
        """Assess how well the request was handled"""
        return 0.85  # Simplified for demo
    
    @claude_function("reflection")
    def _assess_response_quality(self, response: str) -> float:
        """Assess response quality"""
        # Simple heuristics
        quality = 0.5
        if len(response) > 50:
            quality += 0.2
        if "successfully" in response.lower():
            quality += 0.2
        if "\n" in response:  # Structured
            quality += 0.1
        return min(quality, 1.0)
    
    @claude_function("reflection")
    def _calculate_efficiency(self) -> float:
        """Calculate processing efficiency"""
        # Based on telemetry stats
        if telemetry_stats["function_calls"] > 0:
            error_rate = telemetry_stats["errors_handled"] / telemetry_stats["function_calls"]
            efficiency = 1.0 - error_rate
            return efficiency
        return 0.5
    
    @claude_function("reflection")
    def _extract_learnings(self) -> List[str]:
        """Extract learnings from this interaction"""
        learnings = []
        
        if telemetry_stats["errors_handled"] > 0:
            learnings.append("Error handling was required")
        
        if telemetry_stats["tool_uses"] > 3:
            learnings.append("Multiple tools were needed")
        
        if self.confidence_level < 0.7:
            learnings.append("Low confidence - need more context")
        
        return learnings
    
    @claude_function("orchestration")
    def process_user_request(self, user_input: str) -> str:
        """Main orchestration function - fully instrumented"""
        with tracer.start_as_current_span("claude.orchestration.main") as span:
            span.set_attribute("claude.request.input", user_input[:100])  # First 100 chars
            
            try:
                # 1. Perceive
                perception = self.perceive_request(user_input)
                span.add_event("perception_complete", {"complexity": perception["complexity"]})
                
                # 2. Plan
                strategy = self.plan_response(perception)
                span.add_event("planning_complete", {"approach": strategy["approach"]})
                
                # 3. Execute
                results = self.execute_plan(strategy)
                span.add_event("execution_complete", {"success": results["success"]})
                
                # 4. Synthesize
                response = self.synthesize_response(results)
                span.add_event("synthesis_complete", {"response_length": len(response)})
                
                # 5. Reflect
                reflection = self.reflect_on_performance(user_input, response)
                span.add_event("reflection_complete", {"quality": reflection["response_quality"]})
                
                # Add final metrics
                span.set_attribute("claude.orchestration.total_spans", telemetry_stats["total_spans"])
                span.set_attribute("claude.orchestration.function_calls", telemetry_stats["function_calls"])
                span.set_attribute("claude.orchestration.tool_uses", telemetry_stats["tool_uses"])
                span.set_attribute("claude.orchestration.decisions", telemetry_stats["decisions_made"])
                
                return response
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return f"Error processing request: {str(e)}"

def demonstrate_full_instrumentation():
    """Demonstrate Claude with complete telemetry instrumentation"""
    print("🔬 Claude Fully Instrumented Demonstration")
    print("=" * 50)
    
    # Create instrumented Claude
    claude = ClaudeFullyInstrumented()
    
    # Process a request with full telemetry
    test_request = "I need you to analyze the telemetry system and create a Python function"
    
    print(f"\n📥 Input: {test_request}")
    print("\n⚙️  Processing with full telemetry...")
    
    response = claude.process_user_request(test_request)
    
    print(f"\n📤 Response: {response}")
    
    print("\n📊 Telemetry Statistics:")
    print(f"  Total spans created: {telemetry_stats['total_spans']}")
    print(f"  Function calls instrumented: {telemetry_stats['function_calls']}")
    print(f"  Tool uses tracked: {telemetry_stats['tool_uses']}")
    print(f"  Decisions made: {telemetry_stats['decisions_made']}")
    print(f"  Errors handled: {telemetry_stats['errors_handled']}")
    
    print("\n✅ Full instrumentation complete - check OTEL spans above!")

if __name__ == "__main__":
    demonstrate_full_instrumentation()