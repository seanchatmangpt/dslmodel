"""
Test suite for User_workflow
Auto-generated from semantic convention - DO NOT EDIT MANUALLY
"""

import pytest
from unittest.mock import Mock, patch
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ..models.user_workflow import *


class TestUser_workflow:
    """Auto-generated test suite for user_workflow"""
    
    def setup_method(self):
        """Setup test environment with in-memory span collection"""
        self.span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    def test_user_authentication_model_creation(self):
        """Test user.authentication model can be created"""
        model = User_authentication(
            operation="test_value",
            user_id="test_value",
            success="test_value",
        )
        
        assert model is not None
        assert model.operation == "test_value"
        assert model.user_id == "test_value"
        assert model.success == "test_value"
    
    def test_user_authentication_telemetry_emission(self):
        """Test user.authentication emits correct telemetry"""
        model = User_authentication(
            operation="test_value",
            user_id="test_value",
            success="test_value",
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "user.authentication"
        
        # Verify attributes
        assert "app.user.operation" in span.attributes
        assert span.attributes["app.user.operation"] == "test_value"
        assert "app.user.user_id" in span.attributes
        assert span.attributes["app.user.user_id"] == "test_value"
        assert "app.user.success" in span.attributes
        assert span.attributes["app.user.success"] == "test_value"
    
    def test_user_profile_management_model_creation(self):
        """Test user.profile_management model can be created"""
        model = User_profile_management(
            operation="test_value",
            user_id="test_value",
        )
        
        assert model is not None
        assert model.operation == "test_value"
        assert model.user_id == "test_value"
    
    def test_user_profile_management_telemetry_emission(self):
        """Test user.profile_management emits correct telemetry"""
        model = User_profile_management(
            operation="test_value",
            user_id="test_value",
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "user.profile_management"
        
        # Verify attributes
        assert "app.user.operation" in span.attributes
        assert span.attributes["app.user.operation"] == "test_value"
        assert "app.user.user_id" in span.attributes
        assert span.attributes["app.user.user_id"] == "test_value"
    
    def test_user_preference_sync_model_creation(self):
        """Test user.preference_sync model can be created"""
        model = User_preference_sync(
            user_id="test_value",
            sync_direction="test_value",
            sync_success="test_value",
        )
        
        assert model is not None
        assert model.user_id == "test_value"
        assert model.sync_direction == "test_value"
        assert model.sync_success == "test_value"
    
    def test_user_preference_sync_telemetry_emission(self):
        """Test user.preference_sync emits correct telemetry"""
        model = User_preference_sync(
            user_id="test_value",
            sync_direction="test_value",
            sync_success="test_value",
        )
        
        # Clear previous spans
        self.span_exporter.clear()
        
        # Emit telemetry
        trace_id = model.emit_telemetry()
        
        # Verify span was created
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "user.preference_sync"
        
        # Verify attributes
        assert "app.user.user_id" in span.attributes
        assert span.attributes["app.user.user_id"] == "test_value"
        assert "app.user.sync_direction" in span.attributes
        assert span.attributes["app.user.sync_direction"] == "test_value"
        assert "app.user.sync_success" in span.attributes
        assert span.attributes["app.user.sync_success"] == "test_value"
    
