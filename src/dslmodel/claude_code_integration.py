#!/usr/bin/env python3
"""
Claude Code Integration with Weaver Telemetry

This script demonstrates how to integrate Weaver telemetry into Claude Code's
actual tool execution flow, providing comprehensive observability.

The wrapper can be integrated at different levels:
1. Direct wrapper around tool functions
2. Middleware interceptor for all tool calls
3. Decorator-based approach for selective instrumentation
"""

import functools
import time
from typing import Any, Dict, Callable, Optional, List, TypeVar, cast
from pathlib import Path

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Import our wrapper
from dslmodel.claude_code_weaver_wrapper import ClaudeCodeWeaverWrapper, tracer

T = TypeVar('T', bound=Callable[..., Any])


def weaver_telemetry(
    tool_name: str,
    tool_category: str,
    extract_attributes: Optional[Callable[[Any], Dict[str, Any]]] = None
) -> Callable[[T], T]:
    """
    Decorator to add Weaver telemetry to any Claude Code tool function
    
    Args:
        tool_name: Name of the tool (e.g., "Read", "Write", "Bash")
        tool_category: Category of tool (e.g., "file", "bash", "search")
        extract_attributes: Optional function to extract additional attributes from arguments
    
    Example:
        @weaver_telemetry("Read", "file", lambda args: {"path": args[0]})
        def read_file(path: str) -> str:
            return Path(path).read_text()
    """
    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create span name based on category and operation
            span_name = f"claude_code.{tool_category}"
            
            with tracer.start_as_current_span(span_name) as span:
                start_time = time.time()
                
                # Set base attributes
                span.set_attribute("claude_code.tool.name", tool_name)
                span.set_attribute("claude_code.tool.category", tool_category)
                span.set_attribute("claude_code.function.name", func.__name__)
                
                # Extract additional attributes if provided
                if extract_attributes:
                    try:
                        extra_attrs = extract_attributes(args)
                        for key, value in extra_attrs.items():
                            span.set_attribute(f"claude_code.{tool_category}.{key}", value)
                    except Exception as e:
                        span.add_event("Failed to extract attributes", {"error": str(e)})
                
                try:
                    # Execute the actual function
                    result = func(*args, **kwargs)
                    
                    # Calculate duration
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("claude_code.duration_ms", duration_ms)
                    
                    # Set success status
                    span.set_status(Status(StatusCode.OK))
                    span.set_attribute("claude_code.result.success", True)
                    
                    return result
                    
                except Exception as e:
                    # Record exception
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("claude_code.result.success", False)
                    
                    # Calculate duration even on failure
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("claude_code.duration_ms", duration_ms)
                    
                    raise
        
        return cast(T, wrapper)
    return decorator


class ClaudeCodeToolMiddleware:
    """
    Middleware that intercepts all Claude Code tool calls and adds telemetry
    
    This can be integrated into Claude Code's tool execution pipeline to
    automatically instrument all tool usage.
    """
    
    def __init__(self, wrapper: Optional[ClaudeCodeWeaverWrapper] = None):
        self.wrapper = wrapper or ClaudeCodeWeaverWrapper()
        self.tool_mapping = {
            "Read": (self.wrapper.read, "file"),
            "Write": (self.wrapper.write, "file"),
            "Edit": (self._wrap_edit, "file"),
            "MultiEdit": (self._wrap_multi_edit, "file"),
            "Bash": (self.wrapper.bash, "bash"),
            "Grep": (self.wrapper.grep, "search"),
            "Glob": (self._wrap_glob, "search"),
            "LS": (self._wrap_ls, "search"),
            "WebFetch": (self.wrapper.web_fetch, "web"),
            "WebSearch": (self._wrap_web_search, "web"),
            "Task": (self.wrapper.task, "agent"),
            "TodoRead": (self._wrap_todo_read, "todo"),
            "TodoWrite": (self._wrap_todo_write, "todo"),
            "NotebookRead": (self._wrap_notebook_read, "notebook"),
            "NotebookEdit": (self._wrap_notebook_edit, "notebook")
        }
    
    def intercept_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        Intercept a tool call and execute it with telemetry
        
        Args:
            tool_name: Name of the tool being called
            tool_args: Arguments passed to the tool
            
        Returns:
            Result from the tool execution
        """
        if tool_name in self.tool_mapping:
            wrapped_func, category = self.tool_mapping[tool_name]
            
            # Execute with telemetry
            return wrapped_func(**tool_args)
        else:
            # Unknown tool, execute without telemetry but log
            with tracer.start_as_current_span("claude_code.unknown") as span:
                span.set_attribute("claude_code.tool.name", tool_name)
                span.set_attribute("claude_code.tool.category", "unknown")
                span.add_event(f"Unknown tool called: {tool_name}")
                
                # Would execute the actual tool here
                return {"error": f"Unknown tool: {tool_name}"}
    
    def _wrap_edit(self, file_path: str, old_string: str, new_string: str, **kwargs) -> Dict[str, Any]:
        """Wrapper for Edit tool"""
        with tracer.start_as_current_span("claude_code.file") as span:
            span.set_attribute("claude_code.tool.name", "Edit")
            span.set_attribute("claude_code.file.path", file_path)
            span.set_attribute("claude_code.file.operation", "edit")
            span.set_attribute("claude_code.file.old_string_length", len(old_string))
            span.set_attribute("claude_code.file.new_string_length", len(new_string))
            
            # Simulate edit
            return {"success": True, "message": f"Edited {file_path}"}
    
    def _wrap_multi_edit(self, file_path: str, edits: List[Dict[str, str]]) -> Dict[str, Any]:
        """Wrapper for MultiEdit tool"""
        with tracer.start_as_current_span("claude_code.file") as span:
            span.set_attribute("claude_code.tool.name", "MultiEdit")
            span.set_attribute("claude_code.file.path", file_path)
            span.set_attribute("claude_code.file.operation", "multi_edit")
            span.set_attribute("claude_code.file.edit_count", len(edits))
            
            # Simulate multi-edit
            return {"success": True, "edits_applied": len(edits)}
    
    def _wrap_glob(self, pattern: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Wrapper for Glob tool"""
        with tracer.start_as_current_span("claude_code.search") as span:
            span.set_attribute("claude_code.tool.name", "Glob")
            span.set_attribute("claude_code.search.pattern", pattern)
            if path:
                span.set_attribute("claude_code.search.path", path)
            
            # Simulate glob
            results = ["file1.py", "file2.py", "test/file3.py"]
            span.set_attribute("claude_code.search.results_count", len(results))
            
            return {"success": True, "files": results}
    
    def _wrap_ls(self, path: str, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
        """Wrapper for LS tool"""
        with tracer.start_as_current_span("claude_code.search") as span:
            span.set_attribute("claude_code.tool.name", "LS")
            span.set_attribute("claude_code.search.path", path)
            if ignore:
                span.set_attribute("claude_code.search.ignore_patterns", len(ignore))
            
            # Simulate ls
            entries = ["file1.py", "file2.py", "subdir/", "README.md"]
            span.set_attribute("claude_code.search.results_count", len(entries))
            
            return {"success": True, "entries": entries}
    
    def _wrap_web_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Wrapper for WebSearch tool"""
        with tracer.start_as_current_span("claude_code.web") as span:
            span.set_attribute("claude_code.tool.name", "WebSearch")
            span.set_attribute("claude_code.web.operation", "search")
            span.set_attribute("claude_code.web.query", query)
            
            # Simulate search
            results = [
                {"title": "Result 1", "url": "https://example.com/1"},
                {"title": "Result 2", "url": "https://example.com/2"}
            ]
            span.set_attribute("claude_code.web.results_count", len(results))
            
            return {"success": True, "results": results}
    
    def _wrap_todo_read(self) -> Dict[str, Any]:
        """Wrapper for TodoRead tool"""
        with tracer.start_as_current_span("claude_code.todo") as span:
            span.set_attribute("claude_code.tool.name", "TodoRead")
            span.set_attribute("claude_code.todo.operation", "read")
            
            # Simulate todo read
            todos = [
                {"id": "1", "task": "Implement feature", "status": "pending"},
                {"id": "2", "task": "Write tests", "status": "completed"}
            ]
            span.set_attribute("claude_code.todo.count", len(todos))
            
            return {"success": True, "todos": todos}
    
    def _wrap_todo_write(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wrapper for TodoWrite tool"""
        with tracer.start_as_current_span("claude_code.todo") as span:
            span.set_attribute("claude_code.tool.name", "TodoWrite")
            span.set_attribute("claude_code.todo.operation", "write")
            span.set_attribute("claude_code.todo.count", len(todos))
            
            # Count by status
            status_counts = {}
            for todo in todos:
                status = todo.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                span.set_attribute(f"claude_code.todo.{status}_count", count)
            
            return {"success": True, "todos_written": len(todos)}
    
    def _wrap_notebook_read(self, notebook_path: str, cell_id: Optional[str] = None) -> Dict[str, Any]:
        """Wrapper for NotebookRead tool"""
        with tracer.start_as_current_span("claude_code.notebook") as span:
            span.set_attribute("claude_code.tool.name", "NotebookRead")
            span.set_attribute("claude_code.notebook.path", notebook_path)
            span.set_attribute("claude_code.notebook.operation", "read")
            if cell_id:
                span.set_attribute("claude_code.notebook.cell_id", cell_id)
            
            # Simulate notebook read
            cells = [
                {"id": "cell1", "type": "code", "content": "import pandas as pd"},
                {"id": "cell2", "type": "markdown", "content": "# Analysis"}
            ]
            span.set_attribute("claude_code.notebook.cell_count", len(cells))
            
            return {"success": True, "cells": cells}
    
    def _wrap_notebook_edit(self, notebook_path: str, cell_id: str, new_source: str, **kwargs) -> Dict[str, Any]:
        """Wrapper for NotebookEdit tool"""
        with tracer.start_as_current_span("claude_code.notebook") as span:
            span.set_attribute("claude_code.tool.name", "NotebookEdit")
            span.set_attribute("claude_code.notebook.path", notebook_path)
            span.set_attribute("claude_code.notebook.operation", "edit")
            span.set_attribute("claude_code.notebook.cell_id", cell_id)
            span.set_attribute("claude_code.notebook.new_source_length", len(new_source))
            
            return {"success": True, "cell_updated": cell_id}


def demonstrate_integration():
    """Demonstrate different integration approaches"""
    print("🔌 Claude Code + Weaver Integration Demo")
    print("=" * 50)
    
    # 1. Decorator-based approach
    print("\n1️⃣ Decorator-based Telemetry")
    
    @weaver_telemetry("CustomRead", "file", lambda args: {"path": args[0], "encoding": args[1] if len(args) > 1 else "utf-8"})
    def custom_read_file(path: str, encoding: str = "utf-8") -> str:
        """Custom file reader with automatic telemetry"""
        return f"[Content of {path} with {encoding} encoding]"
    
    content = custom_read_file("/tmp/test.txt")
    print(f"   ✅ Read with telemetry: {content[:50]}...")
    
    # 2. Middleware approach
    print("\n2️⃣ Middleware Integration")
    middleware = ClaudeCodeToolMiddleware()
    
    # Simulate tool calls through middleware
    tools_to_test = [
        ("Read", {"file_path": "/tmp/data.csv"}),
        ("Bash", {"command": "echo 'Hello Weaver'"}),
        ("Grep", {"pattern": "TODO", "path": "/src"}),
        ("Task", {"description": "Analyze code", "prompt": "Find all TODOs"})
    ]
    
    for tool_name, tool_args in tools_to_test:
        result = middleware.intercept_tool_call(tool_name, tool_args)
        print(f"   ✅ {tool_name}: {result.get('success', False)}")
    
    # 3. Context manager approach
    print("\n3️⃣ Context Manager for Tool Groups")
    
    class WeaverToolContext:
        """Context manager for grouped tool operations"""
        def __init__(self, operation_name: str):
            self.operation_name = operation_name
            self.span = None
            
        def __enter__(self):
            self.span = tracer.start_span(f"claude_code.operation.{self.operation_name}")
            self.span.__enter__()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            else:
                self.span.set_status(Status(StatusCode.OK))
            self.span.__exit__(exc_type, exc_val, exc_tb)
    
    with WeaverToolContext("code_analysis"):
        # Multiple related tool calls within one operation
        middleware.intercept_tool_call("Glob", {"pattern": "*.py"})
        middleware.intercept_tool_call("Grep", {"pattern": "class"})
        middleware.intercept_tool_call("Task", {"description": "Analyze", "prompt": "Find patterns"})
    
    print("   ✅ Grouped operation with telemetry")
    
    print("\n🎯 Integration Patterns:")
    print("   • Decorators for individual functions")
    print("   • Middleware for all tool calls")
    print("   • Context managers for grouped operations")
    print("   • Direct wrapper usage for fine control")
    
    print("\n✅ All integration patterns demonstrated!")


if __name__ == "__main__":
    demonstrate_integration()