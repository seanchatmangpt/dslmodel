"""
JSON Output Formatter for DSLModel CLI Commands
Provides consistent JSON output formatting across all commands.
"""

import json
import sys
from typing import Any, Dict, Optional, Union
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


class JSONFormatter:
    """Formats command output as JSON with consistent structure."""
    
    def __init__(self):
        self.json_mode = False
        self.command_result: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "command": None,
            "success": True,
            "data": {},
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
    
    def set_json_mode(self, enabled: bool):
        """Enable or disable JSON output mode."""
        self.json_mode = enabled
    
    def set_command(self, command: str):
        """Set the command name for output."""
        self.command_result["command"] = command
    
    def add_data(self, key: str, value: Any):
        """Add data to the JSON output."""
        self.command_result["data"][key] = value
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the JSON output."""
        self.command_result["metadata"][key] = value
    
    def add_error(self, error: str):
        """Add an error message."""
        self.command_result["errors"].append(error)
        self.command_result["success"] = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.command_result["warnings"].append(warning)
    
    def set_success(self, success: bool):
        """Set the success status."""
        self.command_result["success"] = success
    
    def output(self, data: Optional[Dict[str, Any]] = None):
        """Output the JSON result."""
        if data:
            self.command_result["data"].update(data)
        
        if self.json_mode:
            print(json.dumps(self.command_result, indent=2, default=str))
        
    def print(self, message: str, level: str = "info"):
        """Print a message (only in non-JSON mode)."""
        if not self.json_mode:
            print(message)
        else:
            # In JSON mode, collect messages
            if level == "error":
                self.add_error(message)
            elif level == "warning":
                self.add_warning(message)
            # Info messages are not added to avoid clutter


# Global formatter instance
_formatter = JSONFormatter()


def get_formatter() -> JSONFormatter:
    """Get the global JSON formatter instance."""
    return _formatter


def set_json_mode(enabled: bool):
    """Enable or disable JSON output mode globally."""
    _formatter.set_json_mode(enabled)


@contextmanager
def json_command(command_name: str):
    """Context manager for JSON command execution."""
    _formatter.set_command(command_name)
    _formatter.command_result = {
        "timestamp": datetime.now().isoformat(),
        "command": command_name,
        "success": True,
        "data": {},
        "errors": [],
        "warnings": [],
        "metadata": {}
    }
    
    try:
        yield _formatter
    except Exception as e:
        _formatter.add_error(str(e))
        _formatter.set_success(False)
        if not _formatter.json_mode:
            raise
    finally:
        _formatter.output()


def format_file_list(files: list) -> Dict[str, Any]:
    """Format a list of files for JSON output."""
    return {
        "files": [str(f) for f in files],
        "count": len(files)
    }


def format_validation_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format validation results for JSON output."""
    return {
        "success": result.get("success", False),
        "errors": result.get("errors", []),
        "warnings": result.get("warnings", []),
        "details": result.get("details", {})
    }


def format_generation_result(
    feature_name: str,
    files_generated: list,
    duration_ms: int,
    validation_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Format feature generation results for JSON output."""
    return {
        "feature_name": feature_name,
        "files_generated": format_file_list(files_generated),
        "generation_time_ms": duration_ms,
        "validation": format_validation_result(validation_result)
    }


def format_system_status(status: Dict[str, Any]) -> Dict[str, Any]:
    """Format system status for JSON output."""
    return {
        "health_score": status.get("health_score"),
        "health_state": status.get("health_state"),
        "active_agents": status.get("active_agents"),
        "work_queue_size": status.get("work_queue_size"),
        "completion_rate": status.get("completion_rate"),
        "uptime_seconds": status.get("uptime_seconds"),
        "last_updated": datetime.now().isoformat()
    }


def format_telemetry_spans(spans: list) -> Dict[str, Any]:
    """Format telemetry spans for JSON output."""
    return {
        "spans": [
            {
                "name": span.get("name"),
                "brief": span.get("brief"),
                "attributes": [
                    {
                        "name": attr.get("name"),
                        "type": attr.get("type"),
                        "description": attr.get("description")
                    }
                    for attr in span.get("attributes", [])
                ]
            }
            for span in spans
        ],
        "total_spans": len(spans)
    }


def format_demo_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Format demo execution results for JSON output."""
    return {
        "demo_name": results.get("demo_name"),
        "duration_ms": results.get("duration_ms"),
        "phases_completed": results.get("phases_completed"),
        "success": results.get("success", False),
        "phases": results.get("phases", {}),
        "telemetry_spans": results.get("telemetry_spans", []),
        "trace_id": results.get("trace_id")
    }