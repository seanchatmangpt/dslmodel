"""
Test suite for Merge_oracle
Auto-generated from semantic convention - DO NOT EDIT MANUALLY
"""

import pytest
from unittest.mock import Mock, patch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ..models.merge_oracle import *


class TestMerge_oracle:
    """Auto-generated test suite for merge_oracle"""
    
    def setup_method(self):
        """Setup test environment with in-memory span collection"""
        self.span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    def test_merge_oracle_model_creation(self):
        """Test merge_oracle model can be created"""
        model = Merge_oracle(
            motion_id="test_value",
        )
        
        assert model is not None
        assert model.motion_id == "test_value"
    
    def test_merge_oracle_telemetry_emission(self):
        """Test merge_oracle emits correct telemetry"""
        model = Merge_oracle(
            motion_id="test_value",
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "merge_oracle"
        
        # Verify attributes
        assert "merge_oracle.motion.id" in span.attributes
        assert span.attributes["merge_oracle.motion.id"] == "test_value"
    
