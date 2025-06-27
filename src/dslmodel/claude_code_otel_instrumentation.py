#!/usr/bin/env python3
"""
Claude Code OTEL Instrumentation

This module provides real OpenTelemetry instrumentation for Claude Code tools,
implementing the semantic conventions we defined and validated.
"""

import time
import os
import json
import functools
from pathlib import Path
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
# Jaeger exporter commented out to avoid dependency issues
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from opentelemetry.util.types import AttributeValue
from rich.console import Console

console = Console()


@dataclass
class ClaudeCodeSession:
    """Represents a Claude Code session for telemetry context"""
    session_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    turn_number: int = 1


class ClaudeCodeTelemetry:
    """OTEL instrumentation for Claude Code tools following semantic conventions"""
    
    def __init__(self, service_name: str = "claude-code", session: Optional[ClaudeCodeSession] = None):
        self.service_name = service_name
        self.session = session or ClaudeCodeSession(session_id=f"sess_{int(time.time())}")
        self.tracer_provider = None
        self.tracer = None
        self._setup_telemetry()
    
    def _setup_telemetry(self):
        """Setup OpenTelemetry instrumentation"""
        # Create resource with service info
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("CLAUDE_CODE_ENV", "development")
        })
        
        # Setup tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
        
        # Setup exporters
        self._setup_exporters()
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        console.print(f"[green]✓ OTEL instrumentation initialized for {self.service_name}[/green]")
    
    def _setup_exporters(self):
        """Setup OTEL exporters (console and optionally Jaeger)"""
        # Console exporter for development
        console_exporter = ConsoleSpanExporter()
        console_processor = SimpleSpanProcessor(console_exporter)
        self.tracer_provider.add_span_processor(console_processor)
        
        # Jaeger exporter if configured (commented out to avoid dependency issues)
        # jaeger_endpoint = os.getenv("JAEGER_ENDPOINT")
        # if jaeger_endpoint:
        #     try:
        #         jaeger_exporter = JaegerExporter(
        #             agent_host_name=jaeger_endpoint.split("://")[1].split(":")[0],
        #             agent_port=int(jaeger_endpoint.split(":")[-1])
        #         )
        #         jaeger_processor = BatchSpanProcessor(jaeger_exporter)
        #         self.tracer_provider.add_span_processor(jaeger_processor)
        #         console.print(f"[green]✓ Jaeger exporter configured: {jaeger_endpoint}[/green]")
        #     except Exception as e:
        #         console.print(f"[yellow]Warning: Could not setup Jaeger exporter: {e}[/yellow]")
    
    def instrument_file_operation(self, operation: str):
        """Decorator for file operations (Read, Write, Edit, MultiEdit)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract file path from arguments
                file_path = None
                if args and hasattr(args[0], '__dict__') and hasattr(args[0], 'file_path'):
                    file_path = str(args[0].file_path)
                elif 'file_path' in kwargs:
                    file_path = str(kwargs['file_path'])
                elif len(args) > 1 and isinstance(args[1], (str, Path)):
                    file_path = str(args[1])
                
                span_name = f"claude_code.file.{operation}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Set base attributes
                    self._set_base_attributes(span, "file")
                    
                    # Set file-specific attributes
                    if file_path:
                        span.set_attribute("file.path", file_path)
                        span.set_attribute("file.name", Path(file_path).name)
                        span.set_attribute("file.extension", Path(file_path).suffix.lstrip('.'))
                        
                        # Get file size if it exists
                        if Path(file_path).exists():
                            span.set_attribute("file.size_bytes", Path(file_path).stat().st_size)
                    
                    span.set_attribute("operation.name", f"file.{operation}")
                    span.set_attribute("operation.type", "io")
                    span.set_attribute("span.kind", "internal")
                    
                    # Execute the function
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        # Set success attributes
                        span.set_attribute("operation.status", "success")
                        span.set_status(Status(StatusCode.OK))
                        
                        # Set result-specific attributes
                        if operation in ["write", "edit"] and hasattr(result, '__len__'):
                            span.set_attribute("file.lines_affected", len(str(result).split('\n')))
                        
                        return result
                        
                    except Exception as e:
                        # Set error attributes
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_status(Status(StatusCode.ERROR, description=str(e)))
                        raise
                    
                    finally:
                        # Set duration
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("operation.duration_ms", duration_ms)
            
            return wrapper
        return decorator
    
    def instrument_bash_operation(self):
        """Decorator for bash operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract command from arguments
                command = None
                if 'command' in kwargs:
                    command = kwargs['command']
                elif len(args) > 1 and isinstance(args[1], str):
                    command = args[1]
                
                span_name = "claude_code.bash"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Set base attributes
                    self._set_base_attributes(span, "bash")
                    
                    # Set bash-specific attributes
                    if command:
                        span.set_attribute("bash.command", command)
                    
                    span.set_attribute("operation.name", "bash.execute")
                    span.set_attribute("operation.type", "system")
                    span.set_attribute("span.kind", "internal")
                    span.set_attribute("bash.working_directory", os.getcwd())
                    
                    # Set timeout if specified
                    timeout = kwargs.get('timeout', 120000)  # Default 2 minutes
                    span.set_attribute("bash.timeout_ms", timeout)
                    
                    # Execute the function
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        # Extract exit code from result
                        exit_code = 0
                        if hasattr(result, 'returncode'):
                            exit_code = result.returncode
                        elif isinstance(result, dict) and 'exit_code' in result:
                            exit_code = result['exit_code']
                        
                        span.set_attribute("bash.exit_code", exit_code)
                        
                        # Set status based on exit code
                        if exit_code == 0:
                            span.set_attribute("operation.status", "success")
                            span.set_status(Status(StatusCode.OK))
                        else:
                            span.set_attribute("operation.status", "error")
                            span.set_status(Status(StatusCode.ERROR, description=f"Command failed with exit code {exit_code}"))
                        
                        # Set output size if available
                        if hasattr(result, 'stdout') and result.stdout:
                            span.set_attribute("bash.output_size_bytes", len(result.stdout.encode('utf-8')))
                        
                        return result
                        
                    except Exception as e:
                        # Set error attributes
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_status(Status(StatusCode.ERROR, description=str(e)))
                        raise
                    
                    finally:
                        # Set duration
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("operation.duration_ms", duration_ms)
            
            return wrapper
        return decorator
    
    def instrument_web_operation(self, operation: str):
        """Decorator for web operations (WebFetch, WebSearch)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract URL from arguments
                url = None
                if 'url' in kwargs:
                    url = kwargs['url']
                elif len(args) > 1 and isinstance(args[1], str) and args[1].startswith('http'):
                    url = args[1]
                
                span_name = f"claude_code.web.{operation}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Set base attributes
                    self._set_base_attributes(span, "web")
                    
                    # Set web-specific attributes
                    if url:
                        span.set_attribute("http.url", url)
                        span.set_attribute("http.method", "GET")  # Default for Claude Code operations
                    
                    span.set_attribute("operation.name", f"web.{operation}")
                    span.set_attribute("operation.type", "network")
                    span.set_attribute("span.kind", "client")
                    
                    # Set timeout if specified
                    timeout = kwargs.get('timeout', 30000)  # Default 30 seconds
                    span.set_attribute("http.timeout_ms", timeout)
                    
                    # Execute the function
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        # Set success attributes
                        span.set_attribute("operation.status", "success")
                        span.set_attribute("http.status_code", 200)  # Assume success
                        span.set_status(Status(StatusCode.OK))
                        
                        # Set response size if available
                        if isinstance(result, str):
                            span.set_attribute("http.response_size_bytes", len(result.encode('utf-8')))
                        elif isinstance(result, dict) and 'content' in result:
                            span.set_attribute("http.response_size_bytes", len(str(result['content']).encode('utf-8')))
                        
                        # Set content type
                        span.set_attribute("http.content_type", "text/html")  # Default assumption
                        
                        # Web-specific attributes
                        if operation == "fetch":
                            span.set_attribute("web.ai_processing", kwargs.get('ai_processing', True))
                            span.set_attribute("web.content_extraction", kwargs.get('content_extraction', 'text_only'))
                            if 'prompt' in kwargs:
                                span.set_attribute("web.prompt", kwargs['prompt'])
                        
                        return result
                        
                    except Exception as e:
                        # Set error attributes
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_attribute("http.status_code", 500)  # Internal error
                        span.set_status(Status(StatusCode.ERROR, description=str(e)))
                        raise
                    
                    finally:
                        # Set duration
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("operation.duration_ms", duration_ms)
            
            return wrapper
        return decorator
    
    def instrument_search_operation(self):
        """Decorator for search operations (Grep, Glob, LS)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract search parameters
                pattern = kwargs.get('pattern', '')
                path = kwargs.get('path', os.getcwd())
                
                span_name = "claude_code.search"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Set base attributes
                    self._set_base_attributes(span, "search")
                    
                    # Set search-specific attributes
                    span.set_attribute("search.pattern", pattern)
                    span.set_attribute("search.path", str(path))
                    span.set_attribute("operation.name", "search.grep")
                    span.set_attribute("operation.type", "compute")
                    span.set_attribute("span.kind", "internal")
                    
                    # Set search options
                    span.set_attribute("search.recursive", kwargs.get('recursive', True))
                    span.set_attribute("search.case_sensitive", kwargs.get('case_sensitive', False))
                    
                    # Execute the function
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        
                        # Set success attributes
                        span.set_attribute("operation.status", "success")
                        span.set_status(Status(StatusCode.OK))
                        
                        # Set result metrics
                        if isinstance(result, list):
                            span.set_attribute("search.results_count", len(result))
                        elif isinstance(result, dict) and 'results' in result:
                            span.set_attribute("search.results_count", len(result['results']))
                        else:
                            span.set_attribute("search.results_count", 0)
                        
                        # Estimate files scanned (simplified)
                        span.set_attribute("search.files_scanned", max(1, len(result) if isinstance(result, list) else 10))
                        
                        return result
                        
                    except Exception as e:
                        # Set error attributes
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_status(Status(StatusCode.ERROR, description=str(e)))
                        raise
                    
                    finally:
                        # Set duration
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("operation.duration_ms", duration_ms)
            
            return wrapper
        return decorator
    
    def instrument_agent_operation(self):
        """Decorator for agent operations (Task)"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract agent parameters
                task_description = kwargs.get('description', 'Unknown task')
                agent_id = kwargs.get('agent_id', f"agent_{int(time.time())}")
                
                span_name = "claude_code.agent"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Set base attributes
                    self._set_base_attributes(span, "agent")
                    
                    # Set agent-specific attributes
                    span.set_attribute("claude_code.agent.id", agent_id)
                    span.set_attribute("claude_code.agent.task", task_description)
                    span.set_attribute("claude_code.agent.status", "started")
                    span.set_attribute("operation.name", "agent.execute")
                    span.set_attribute("operation.type", "compute")
                    span.set_attribute("span.kind", "internal")
                    
                    # Execute the function
                    start_time = time.time()
                    try:
                        # Update status to running
                        span.set_attribute("claude_code.agent.status", "running")
                        
                        result = func(*args, **kwargs)
                        
                        # Set success attributes
                        span.set_attribute("claude_code.agent.status", "completed")
                        span.set_attribute("operation.status", "success")
                        span.set_status(Status(StatusCode.OK))
                        
                        # Set agent metrics
                        if isinstance(result, dict):
                            if 'tools_used' in result:
                                span.set_attribute("agent.tools_used", result['tools_used'])
                            if 'sub_tasks' in result:
                                span.set_attribute("agent.sub_tasks", len(result['sub_tasks']))
                            if 'artifacts_created' in result:
                                span.set_attribute("agent.artifacts_created", result['artifacts_created'])
                        
                        return result
                        
                    except Exception as e:
                        # Set error attributes
                        span.set_attribute("claude_code.agent.status", "failed")
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        span.set_status(Status(StatusCode.ERROR, description=str(e)))
                        raise
                    
                    finally:
                        # Set duration
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("operation.duration_ms", duration_ms)
            
            return wrapper
        return decorator
    
    def _set_base_attributes(self, span, tool_category: str):
        """Set base attributes for all Claude Code spans"""
        # Tool identification
        span.set_attribute("claude_code.tool.category", tool_category)
        
        # Session context
        span.set_attribute("session.id", self.session.session_id)
        if self.session.user_id:
            span.set_attribute("user.id", self.session.user_id)
        if self.session.conversation_id:
            span.set_attribute("claude_code.context.conversation_id", self.session.conversation_id)
        span.set_attribute("claude_code.context.turn_number", self.session.turn_number)
        
        # User request context (would normally come from the actual request)
        span.set_attribute("claude_code.user.request", f"Simulated {tool_category} operation")


# Example usage and testing
def demonstrate_claude_code_instrumentation():
    """Demonstrate Claude Code OTEL instrumentation"""
    console.print("[bold green]🔧 Claude Code OTEL Instrumentation Demo[/bold green]")
    console.print("=" * 60)
    
    # Initialize telemetry
    session = ClaudeCodeSession(
        session_id="demo_session_001",
        user_id="demo_user",
        conversation_id="conv_123",
        turn_number=5
    )
    
    telemetry = ClaudeCodeTelemetry(session=session)
    
    # Mock Claude Code tool functions
    @telemetry.instrument_file_operation("read")
    def mock_read_file(file_path: str) -> str:
        """Mock file read operation"""
        time.sleep(0.01)  # Simulate I/O delay
        return f"Content of {file_path}"
    
    @telemetry.instrument_bash_operation()
    def mock_bash_command(command: str) -> Dict[str, Any]:
        """Mock bash command execution"""
        time.sleep(0.1)  # Simulate execution time
        return {"exit_code": 0, "stdout": "Command output", "stderr": ""}
    
    @telemetry.instrument_web_operation("fetch")
    def mock_web_fetch(url: str, prompt: str = None) -> str:
        """Mock web fetch operation"""
        time.sleep(0.5)  # Simulate network delay
        return f"<html>Content from {url}</html>"
    
    @telemetry.instrument_search_operation()
    def mock_search(pattern: str, path: str = ".") -> List[str]:
        """Mock search operation"""
        time.sleep(0.05)  # Simulate search time
        return [f"match1.py", f"match2.py"]
    
    @telemetry.instrument_agent_operation()
    def mock_agent_task(description: str, agent_id: str = None) -> Dict[str, Any]:
        """Mock agent task execution"""
        time.sleep(0.2)  # Simulate processing time
        return {
            "tools_used": ["Read", "Grep"],
            "sub_tasks": ["analyze", "summarize"],
            "artifacts_created": 2
        }
    
    # Execute instrumented operations
    console.print("\n[cyan]Executing instrumented Claude Code operations...[/cyan]")
    
    try:
        # File operations
        content = mock_read_file("/Users/dev/project/main.py")
        
        # Bash operations
        result = mock_bash_command("python -m pytest tests/")
        
        # Web operations
        html_content = mock_web_fetch("https://docs.python.org/3/", prompt="Extract key information")
        
        # Search operations
        search_results = mock_search("async def.*", path="./src")
        
        # Agent operations
        agent_result = mock_agent_task("Analyze code structure", agent_id="analyzer_001")
        
        console.print("\n[green]✅ All operations completed successfully![/green]")
        console.print(f"[green]📊 Generated telemetry for {telemetry.session.session_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during execution: {e}[/red]")


if __name__ == "__main__":
    demonstrate_claude_code_instrumentation()