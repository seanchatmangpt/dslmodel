"""
Test suite for Roberts_rules
Auto-generated from semantic convention - DO NOT EDIT MANUALLY
"""

import pytest
from unittest.mock import Mock, patch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ..models.roberts_rules import *


class TestRoberts_rules:
    """Auto-generated test suite for roberts_rules"""
    
    def setup_method(self):
        """Setup test environment with in-memory span collection"""
        self.span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    def test_roberts_model_creation(self):
        """Test roberts model can be created"""
        model = Roberts(
            motion_id="test_value",
        )
        
        assert model is not None
        assert model.motion_id == "test_value"
    
    def test_roberts_telemetry_emission(self):
        """Test roberts emits correct telemetry"""
        model = Roberts(
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
        assert span.name == "roberts"
        
        # Verify attributes
        assert "roberts.motion.id" in span.attributes
        assert span.attributes["roberts.motion.id"] == "test_value"
    
