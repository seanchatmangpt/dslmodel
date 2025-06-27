"""
Test suite for Git_operations
Auto-generated from semantic convention - DO NOT EDIT MANUALLY
"""

import pytest
from unittest.mock import Mock, patch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ..models.git_operations import *


class TestGit_operations:
    """Auto-generated test suite for git_operations"""
    
    def setup_method(self):
        """Setup test environment with in-memory span collection"""
        self.span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    def test_git_model_creation(self):
        """Test git model can be created"""
        model = Git(
            operation="test_value",
        )
        
        assert model is not None
        assert model.operation == "test_value"
    
    def test_git_telemetry_emission(self):
        """Test git emits correct telemetry"""
        model = Git(
            operation="test_value",
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "git"
        
        # Verify attributes
        assert "git.operation" in span.attributes
        assert span.attributes["git.operation"] == "test_value"
    
