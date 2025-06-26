#!/usr/bin/env python3
"""
Claude Code All Spans Demo - Comprehensive Telemetry Showcase

This script demonstrates ALL possible spans that can be generated for Claude Code tools,
showing the complete telemetry structure and attributes for each tool type.
"""

import json
import time
from typing import Dict, Any, List
from pathlib import Path

# Import our wrapper
from dslmodel.claude_code_weaver_wrapper import ClaudeCodeWeaverWrapper
from dslmodel.claude_code_integration import ClaudeCodeToolMiddleware, weaver_telemetry

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Setup OTEL with in-memory exporter to capture spans
resource = Resource(attributes={SERVICE_NAME: "claude-code-all-spans-demo"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Add both console and in-memory exporters
console_exporter = ConsoleSpanExporter()
memory_exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(console_exporter))
provider.add_span_processor(SimpleSpanProcessor(memory_exporter))

tracer = trace.get_tracer(__name__)


def demonstrate_all_spans():
    """Demonstrate every possible Claude Code span type"""
    
    print("🌟 Claude Code Complete Spans Showcase")
    print("=" * 60)
    print("Demonstrating ALL possible telemetry spans for Claude Code tools\n")
    
    # Create wrapper and middleware
    wrapper = ClaudeCodeWeaverWrapper(session_id="showcase_session_001")
    middleware = ClaudeCodeToolMiddleware(wrapper)
    
    # Track all span types
    span_types = {
        "File Operations": [],
        "Bash Operations": [],
        "Search Operations": [],
        "Web Operations": [],
        "Agent Operations": [],
        "Todo Operations": [],
        "Notebook Operations": [],
        "Grouped Operations": []
    }
    
    # ========== FILE OPERATIONS ==========
    print("📁 FILE OPERATIONS SPANS")
    print("-" * 30)
    
    # 1. Read
    print("1. Read span:")
    wrapper.read("/path/to/file.py", limit=100, offset=50)
    span_types["File Operations"].append("claude_code.file (Read)")
    
    # 2. Write
    print("2. Write span:")
    wrapper.write("/path/to/output.py", "# Generated code\nprint('Hello')")
    span_types["File Operations"].append("claude_code.file (Write)")
    
    # 3. Edit
    print("3. Edit span:")
    middleware.intercept_tool_call("Edit", {
        "file_path": "/path/to/edit.py",
        "old_string": "old_value",
        "new_string": "new_value",
        "replace_all": False
    })
    span_types["File Operations"].append("claude_code.file (Edit)")
    
    # 4. MultiEdit
    print("4. MultiEdit span:")
    middleware.intercept_tool_call("MultiEdit", {
        "file_path": "/path/to/multi.py",
        "edits": [
            {"old_string": "foo", "new_string": "bar"},
            {"old_string": "baz", "new_string": "qux"}
        ]
    })
    span_types["File Operations"].append("claude_code.file (MultiEdit)")
    
    # ========== BASH OPERATIONS ==========
    print("\n\n💻 BASH OPERATIONS SPANS")
    print("-" * 30)
    
    # 5. Bash command
    print("5. Bash span:")
    wrapper.bash("ls -la /tmp", timeout=5000)
    span_types["Bash Operations"].append("claude_code.bash")
    
    # 6. Bash with error
    print("6. Bash error span:")
    try:
        # Simulate error
        with tracer.start_as_current_span("claude_code.bash") as span:
            span.set_attribute("claude_code.tool.name", "Bash")
            span.set_attribute("claude_code.bash.command", "invalid_command")
            raise Exception("Command not found")
    except:
        pass
    span_types["Bash Operations"].append("claude_code.bash (Error)")
    
    # ========== SEARCH OPERATIONS ==========
    print("\n\n🔍 SEARCH OPERATIONS SPANS")
    print("-" * 30)
    
    # 7. Grep
    print("7. Grep span:")
    wrapper.grep("TODO", path="/src", include="*.py")
    span_types["Search Operations"].append("claude_code.search (Grep)")
    
    # 8. Glob
    print("8. Glob span:")
    middleware.intercept_tool_call("Glob", {
        "pattern": "**/*.test.js",
        "path": "/project"
    })
    span_types["Search Operations"].append("claude_code.search (Glob)")
    
    # 9. LS
    print("9. LS span:")
    middleware.intercept_tool_call("LS", {
        "path": "/Users/dev/project",
        "ignore": [".git", "node_modules", "__pycache__"]
    })
    span_types["Search Operations"].append("claude_code.search (LS)")
    
    # ========== WEB OPERATIONS ==========
    print("\n\n🌐 WEB OPERATIONS SPANS")
    print("-" * 30)
    
    # 10. WebFetch
    print("10. WebFetch span:")
    wrapper.web_fetch("https://api.github.com/repos/anthropics/claude-code", 
                     "Get repository information")
    span_types["Web Operations"].append("claude_code.web (WebFetch)")
    
    # 11. WebSearch
    print("11. WebSearch span:")
    middleware.intercept_tool_call("WebSearch", {
        "query": "OpenTelemetry Python SDK",
        "allowed_domains": ["opentelemetry.io"],
        "blocked_domains": ["spam.com"]
    })
    span_types["Web Operations"].append("claude_code.web (WebSearch)")
    
    # ========== AGENT OPERATIONS ==========
    print("\n\n🤖 AGENT OPERATIONS SPANS")
    print("-" * 30)
    
    # 12. Task (Agent)
    print("12. Task/Agent span:")
    wrapper.task("Security Analysis", "Scan codebase for vulnerabilities")
    span_types["Agent Operations"].append("claude_code.agent (Task)")
    
    # ========== TODO OPERATIONS ==========
    print("\n\n📝 TODO OPERATIONS SPANS")
    print("-" * 30)
    
    # 13. TodoRead
    print("13. TodoRead span:")
    middleware.intercept_tool_call("TodoRead", {})
    span_types["Todo Operations"].append("claude_code.todo (TodoRead)")
    
    # 14. TodoWrite
    print("14. TodoWrite span:")
    middleware.intercept_tool_call("TodoWrite", {
        "todos": [
            {"id": "1", "content": "Implement feature X", "status": "pending", "priority": "high"},
            {"id": "2", "content": "Write tests", "status": "in_progress", "priority": "medium"},
            {"id": "3", "content": "Update docs", "status": "completed", "priority": "low"}
        ]
    })
    span_types["Todo Operations"].append("claude_code.todo (TodoWrite)")
    
    # ========== NOTEBOOK OPERATIONS ==========
    print("\n\n📓 NOTEBOOK OPERATIONS SPANS")
    print("-" * 30)
    
    # 15. NotebookRead
    print("15. NotebookRead span:")
    middleware.intercept_tool_call("NotebookRead", {
        "notebook_path": "/notebooks/analysis.ipynb",
        "cell_id": "cell_123"
    })
    span_types["Notebook Operations"].append("claude_code.notebook (NotebookRead)")
    
    # 16. NotebookEdit
    print("16. NotebookEdit span:")
    middleware.intercept_tool_call("NotebookEdit", {
        "notebook_path": "/notebooks/analysis.ipynb",
        "cell_id": "cell_456",
        "new_source": "import pandas as pd\ndf = pd.read_csv('data.csv')",
        "cell_type": "code",
        "edit_mode": "replace"
    })
    span_types["Notebook Operations"].append("claude_code.notebook (NotebookEdit)")
    
    # ========== GROUPED OPERATIONS ==========
    print("\n\n🎯 GROUPED OPERATIONS SPANS")
    print("-" * 30)
    
    # 17. Operation grouping
    print("17. Grouped operation span:")
    with tracer.start_as_current_span("claude_code.operation.refactoring") as parent_span:
        parent_span.set_attribute("operation.type", "code_refactoring")
        parent_span.set_attribute("operation.files_count", 3)
        
        # Child spans within the operation
        with tracer.start_as_current_span("claude_code.file") as child1:
            child1.set_attribute("claude_code.tool.name", "Read")
            child1.set_attribute("claude_code.file.path", "/src/old_module.py")
        
        with tracer.start_as_current_span("claude_code.file") as child2:
            child2.set_attribute("claude_code.tool.name", "Write")
            child2.set_attribute("claude_code.file.path", "/src/new_module.py")
        
        with tracer.start_as_current_span("claude_code.bash") as child3:
            child3.set_attribute("claude_code.tool.name", "Bash")
            child3.set_attribute("claude_code.bash.command", "python -m pytest")
    
    span_types["Grouped Operations"].append("claude_code.operation.* (with child spans)")
    
    # ========== SPECIAL CASES ==========
    print("\n\n⚡ SPECIAL CASE SPANS")
    print("-" * 30)
    
    # 18. Unknown tool
    print("18. Unknown tool span:")
    middleware.intercept_tool_call("CustomTool", {"param": "value"})
    
    # 19. Exit plan mode (special tool)
    print("19. Exit plan mode span:")
    with tracer.start_as_current_span("claude_code.plan") as span:
        span.set_attribute("claude_code.tool.name", "exit_plan_mode")
        span.set_attribute("claude_code.plan.content", "Implementation plan approved")
    
    # ========== SUMMARY ==========
    print("\n\n📊 SPAN TYPES SUMMARY")
    print("=" * 60)
    
    total_spans = 0
    for category, spans in span_types.items():
        print(f"\n{category}:")
        for span_type in spans:
            print(f"  • {span_type}")
            total_spans += 1
    
    print(f"\n📈 Total span types demonstrated: {total_spans}")
    
    # Get all spans from memory
    spans = memory_exporter.get_finished_spans()
    print(f"📊 Total spans generated: {len(spans)}")
    
    # Analyze span attributes
    print("\n🔍 SPAN ATTRIBUTES ANALYSIS")
    print("-" * 30)
    
    attribute_counts = {}
    for span in spans:
        for attr_name in span.attributes:
            if attr_name.startswith("claude_code"):
                category = attr_name.split(".")[1]
                if category not in attribute_counts:
                    attribute_counts[category] = set()
                attribute_counts[category].add(attr_name)
    
    for category, attributes in sorted(attribute_counts.items()):
        print(f"\n{category.upper()} attributes:")
        for attr in sorted(attributes):
            print(f"  • {attr}")
    
    # Show metrics summary
    print("\n\n📊 METRICS SUMMARY")
    print("-" * 30)
    metrics = wrapper.get_metrics_summary()
    print(json.dumps(metrics, indent=2))
    
    return spans


def export_spans_to_json(spans: List[Any], output_file: str = "claude_code_spans.json"):
    """Export all spans to JSON for analysis"""
    
    span_data = []
    for span in spans:
        span_dict = {
            "name": span.name,
            "span_id": format(span.context.span_id, "016x"),
            "trace_id": format(span.context.trace_id, "032x"),
            "parent_id": format(span.parent.span_id, "016x") if span.parent else None,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "duration_ns": span.end_time - span.start_time if span.end_time else None,
            "status": {
                "status_code": span.status.status_code.name,
                "description": span.status.description
            },
            "attributes": dict(span.attributes) if span.attributes else {},
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes) if event.attributes else {}
                }
                for event in span.events
            ],
            "kind": span.kind.name
        }
        span_data.append(span_dict)
    
    with open(output_file, "w") as f:
        json.dump(span_data, f, indent=2, default=str)
    
    print(f"\n💾 Exported {len(span_data)} spans to {output_file}")


if __name__ == "__main__":
    # Run the demonstration
    spans = demonstrate_all_spans()
    
    # Export spans for analysis
    export_spans_to_json(spans)
    
    print("\n✅ Claude Code spans showcase complete!")
    print("🔍 Check claude_code_spans.json for detailed span data")