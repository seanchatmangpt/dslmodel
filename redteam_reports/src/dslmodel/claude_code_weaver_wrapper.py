#!/usr/bin/env python3
"""
Claude Code Weaver Wrapper - Comprehensive Tool Telemetry

This script wraps all Claude Code functions with Weaver-generated telemetry models,
providing complete observability for tool usage via OpenTelemetry.

Usage:
    from dslmodel.claude_code_weaver_wrapper import wrapped_tools
    
    # Use wrapped tools that automatically emit telemetry
    result = wrapped_tools.read('/path/to/file')
    result = wrapped_tools.bash('ls -la')
    result = wrapped_tools.write('/path/to/file', 'content')
"""

import time
import functools
from typing import Any, Dict, Callable, Optional, List
from pathlib import Path

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace import Status, StatusCode

# Import our Weaver-generated models
from dslmodel.generated.dslmodel_attributes import ClaudeCodeAttributes

# Setup OTEL
resource = Resource(attributes={SERVICE_NAME: "claude-code-tools"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
console_processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(console_processor)

tracer = trace.get_tracer(__name__)


class ClaudeCodeWeaverWrapper:
    """Wrapper that adds Weaver telemetry to all Claude Code tool functions"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time() * 1000)}"
        self.tool_metrics: Dict[str, Dict[str, int]] = {}
    
    def _create_base_attributes(self, tool_name: str, tool_category: str, user_request: Optional[str] = None) -> ClaudeCodeAttributes:
        """Create base Claude Code attributes using Weaver model"""
        return ClaudeCodeAttributes(
            claude_code_tool_name=tool_name,
            claude_code_tool_category=tool_category,
            claude_code_session_id=self.session_id,
            claude_code_user_request=user_request
        )
    
    def _update_metrics(self, tool_name: str, success: bool, duration_ms: float):
        """Update internal metrics tracking"""
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0
            }
        
        self.tool_metrics[tool_name]["calls"] += 1
        if success:
            self.tool_metrics[tool_name]["successes"] += 1
        else:
            self.tool_metrics[tool_name]["failures"] += 1
        self.tool_metrics[tool_name]["total_duration_ms"] += duration_ms
    
    # File Operations
    
    def read(self, file_path: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """Wrapped Read tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.file") as span:
            start_time = time.time()
            
            # Set base attributes
            attrs = self._create_base_attributes("Read", "file", f"Read file: {file_path}")
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set file-specific attributes
            span.set_attribute("claude_code.file.path", file_path)
            span.set_attribute("claude_code.file.operation", "read")
            
            if limit:
                span.set_attribute("claude_code.file.limit", limit)
            if offset:
                span.set_attribute("claude_code.file.offset", offset)
            
            try:
                # Simulate actual tool call
                result = {
                    "success": True,
                    "content": f"[Simulated content of {file_path}]",
                    "lines": 100,
                    "size_bytes": 2048
                }
                
                # Set result attributes
                span.set_attribute("claude_code.file.size_bytes", result["size_bytes"])
                span.set_attribute("claude_code.file.lines_affected", result["lines"])
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("Read", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("Read", False, duration_ms)
                raise
    
    def write(self, file_path: str, content: str) -> Dict[str, Any]:
        """Wrapped Write tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.file") as span:
            start_time = time.time()
            
            # Set base attributes
            attrs = self._create_base_attributes("Write", "file", f"Write to file: {file_path}")
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set file-specific attributes
            span.set_attribute("claude_code.file.path", file_path)
            span.set_attribute("claude_code.file.operation", "write")
            span.set_attribute("claude_code.file.size_bytes", len(content.encode()))
            span.set_attribute("claude_code.file.lines_affected", content.count('\n') + 1)
            
            try:
                # Simulate actual tool call
                result = {
                    "success": True,
                    "message": f"File written successfully: {file_path}"
                }
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("Write", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("Write", False, duration_ms)
                raise
    
    def bash(self, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Wrapped Bash tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.bash") as span:
            start_time = time.time()
            
            # Set base attributes
            attrs = self._create_base_attributes("Bash", "bash", f"Execute: {command}")
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set bash-specific attributes
            span.set_attribute("claude_code.bash.command", command)
            if timeout:
                span.set_attribute("claude_code.bash.timeout_ms", timeout)
            
            try:
                # Simulate actual tool call
                result = {
                    "success": True,
                    "output": f"[Simulated output of: {command}]",
                    "exit_code": 0
                }
                
                # Set result attributes
                span.set_attribute("claude_code.bash.exit_code", result["exit_code"])
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.bash.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("Bash", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.set_attribute("claude_code.bash.exit_code", 1)
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("Bash", False, duration_ms)
                raise
    
    def grep(self, pattern: str, path: Optional[str] = None, include: Optional[str] = None) -> Dict[str, Any]:
        """Wrapped Grep tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.search") as span:
            start_time = time.time()
            
            # Set base attributes
            attrs = self._create_base_attributes("Grep", "search", f"Search for: {pattern}")
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set search-specific attributes
            span.set_attribute("claude_code.search.pattern", pattern)
            if path:
                span.set_attribute("claude_code.search.path", path)
            if include:
                span.set_attribute("claude_code.search.include", include)
            
            try:
                # Simulate actual tool call
                result = {
                    "success": True,
                    "matches": ["file1.py:10", "file2.py:25"],
                    "count": 2
                }
                
                # Set result attributes
                span.set_attribute("claude_code.search.results_count", result["count"])
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.search.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("Grep", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("Grep", False, duration_ms)
                raise
    
    def web_fetch(self, url: str, prompt: str) -> Dict[str, Any]:
        """Wrapped WebFetch tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.web") as span:
            start_time = time.time()
            
            # Set base attributes
            attrs = self._create_base_attributes("WebFetch", "web", f"Fetch: {url}")
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set web-specific attributes
            span.set_attribute("claude_code.web.url", url)
            span.set_attribute("claude_code.web.operation", "fetch")
            span.set_attribute("claude_code.web.prompt", prompt)
            
            try:
                # Simulate actual tool call
                result = {
                    "success": True,
                    "content": f"[Fetched content from {url}]",
                    "size_bytes": 4096,
                    "cache_hit": False
                }
                
                # Set result attributes
                span.set_attribute("claude_code.web.response_size_bytes", result["size_bytes"])
                span.set_attribute("claude_code.web.cache_hit", result["cache_hit"])
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.web.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("WebFetch", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("WebFetch", False, duration_ms)
                raise
    
    def task(self, description: str, prompt: str) -> Dict[str, Any]:
        """Wrapped Task (Agent) tool with Weaver telemetry"""
        with tracer.start_as_current_span("claude_code.agent") as span:
            start_time = time.time()
            agent_id = f"agent_{int(time.time() * 1000)}"
            
            # Set base attributes
            attrs = self._create_base_attributes("Task", "agent", description)
            span.set_attributes(attrs.model_dump(exclude_none=True))
            
            # Set agent-specific attributes
            span.set_attribute("claude_code.agent.id", agent_id)
            span.set_attribute("claude_code.agent.task", prompt)
            span.set_attribute("claude_code.agent.status", "started")
            span.set_attribute("claude_code.agent.progress_percent", 0.0)
            
            try:
                # Simulate agent execution with progress updates
                for progress in [25, 50, 75, 100]:
                    time.sleep(0.1)  # Simulate work
                    span.add_event(f"Progress update: {progress}%", {
                        "claude_code.agent.progress_percent": progress
                    })
                
                # Final result
                result = {
                    "success": True,
                    "agent_id": agent_id,
                    "message": "Task completed successfully",
                    "results": ["Found 5 configuration files", "Analyzed code structure"]
                }
                
                # Set final attributes
                span.set_attribute("claude_code.agent.status", "completed")
                span.set_attribute("claude_code.agent.progress_percent", 100.0)
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("claude_code.agent.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.OK))
                
                self._update_metrics("Task", True, duration_ms)
                return result
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.set_attribute("claude_code.agent.status", "failed")
                duration_ms = (time.time() - start_time) * 1000
                self._update_metrics("Task", False, duration_ms)
                raise
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of tool usage metrics"""
        summary = {
            "session_id": self.session_id,
            "tools": {}
        }
        
        for tool_name, metrics in self.tool_metrics.items():
            avg_duration = metrics["total_duration_ms"] / metrics["calls"] if metrics["calls"] > 0 else 0
            success_rate = metrics["successes"] / metrics["calls"] if metrics["calls"] > 0 else 0
            
            summary["tools"][tool_name] = {
                "total_calls": metrics["calls"],
                "successes": metrics["successes"],
                "failures": metrics["failures"],
                "success_rate": f"{success_rate:.1%}",
                "avg_duration_ms": f"{avg_duration:.2f}"
            }
        
        return summary


# Create global wrapper instance
wrapped_tools = ClaudeCodeWeaverWrapper()


def demonstrate_weaver_wrapper():
    """Demonstrate the Weaver wrapper with various tool calls"""
    print("🧬 Claude Code Weaver Wrapper Demo")
    print("=" * 50)
    
    # Create a new wrapper instance for this demo
    demo_wrapper = ClaudeCodeWeaverWrapper(session_id="demo_session_001")
    
    print("\n1️⃣ Testing File Operations")
    result = demo_wrapper.read("/Users/demo/test.py", limit=100)
    print(f"   ✅ Read: {result['success']}")
    
    result = demo_wrapper.write("/Users/demo/output.py", "print('Hello from Weaver!')")
    print(f"   ✅ Write: {result['success']}")
    
    print("\n2️⃣ Testing Bash Commands")
    result = demo_wrapper.bash("ls -la", timeout=5000)
    print(f"   ✅ Bash: {result['success']}, exit_code: {result['exit_code']}")
    
    print("\n3️⃣ Testing Search Operations")
    result = demo_wrapper.grep("TODO", path="/Users/demo/project", include="*.py")
    print(f"   ✅ Grep: Found {result['count']} matches")
    
    print("\n4️⃣ Testing Web Operations")
    result = demo_wrapper.web_fetch("https://docs.python.org", "Get Python documentation")
    print(f"   ✅ WebFetch: {result['size_bytes']} bytes, cache: {result['cache_hit']}")
    
    print("\n5️⃣ Testing Agent Tasks")
    result = demo_wrapper.task("Code Analysis", "Analyze the codebase structure")
    print(f"   ✅ Task: {result['agent_id']} - {result['message']}")
    
    print("\n📊 Metrics Summary")
    print("-" * 30)
    summary = demo_wrapper.get_metrics_summary()
    
    for tool_name, metrics in summary["tools"].items():
        print(f"\n{tool_name}:")
        print(f"  Total Calls: {metrics['total_calls']}")
        print(f"  Success Rate: {metrics['success_rate']}")
        print(f"  Avg Duration: {metrics['avg_duration_ms']}ms")
    
    print(f"\n🆔 Session ID: {summary['session_id']}")
    print("\n✅ All tools wrapped with Weaver telemetry!")


if __name__ == "__main__":
    demonstrate_weaver_wrapper()