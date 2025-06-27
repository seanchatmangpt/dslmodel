#!/usr/bin/env python3
"""Weaver System Test Suite
Tests for semantic conventions, auto-generation, and Weaver-first functionality.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import Weaver components
from dslmodel.weaver.weaver_engine import WeaverEngine
from dslmodel.weaver.semantic_conventions import SemanticConvention
from dslmodel.weaver.generators import CodeGenerator, ModelGenerator
from dslmodel.weaver.validators import ConventionValidator
from dslmodel.weaver.multilayer import MultiLayerWeaver
from dslmodel.weaver.loop import WeaverLoop


class TestSemanticConventions:
    """Test semantic convention handling"""
    
    def test_convention_creation(self):
        """Test semantic convention model creation"""
        convention = SemanticConvention(
            name="test_convention",
            version="1.0.0",
            description="A test semantic convention",
            attributes={
                "service.name": {"type": "string", "description": "Service name"},
                "service.version": {"type": "string", "description": "Service version"}
            }
        )
        
        assert convention.name == "test_convention"
        assert convention.version == "1.0.0"
        assert len(convention.attributes) == 2
        assert "service.name" in convention.attributes
    
    def test_convention_validation(self):
        """Test semantic convention validation"""
        convention = SemanticConvention(
            name="valid_convention",
            version="1.0.0",
            description="Valid convention",
            attributes={
                "valid.attribute": {"type": "string", "description": "Valid attribute"}
            }
        )
        
        validator = ConventionValidator()
        result = validator.validate(convention)
        assert result.is_valid == True
    
    def test_convention_serialization(self):
        """Test convention serialization to/from JSON"""
        convention = SemanticConvention(
            name="serializable",
            version="1.0.0",
            description="Test serialization",
            attributes={"test.attr": {"type": "string"}}
        )
        
        # Test serialization
        json_data = convention.model_dump_json()
        data = json.loads(json_data)
        
        assert data["name"] == "serializable"
        assert "test.attr" in data["attributes"]
        
        # Test deserialization
        new_convention = SemanticConvention.model_validate(data)
        assert new_convention.name == "serializable"


class TestWeaverEngine:
    """Test Weaver engine functionality"""
    
    def test_engine_initialization(self):
        """Test Weaver engine initialization"""
        engine = WeaverEngine()
        
        assert engine is not None
        assert hasattr(engine, 'conventions')
        assert hasattr(engine, 'generators')
    
    def test_convention_registration(self):
        """Test convention registration in engine"""
        engine = WeaverEngine()
        
        convention = SemanticConvention(
            name="test_registration",
            version="1.0.0",
            description="Test registration",
            attributes={}
        )
        
        engine.register_convention(convention)
        assert "test_registration" in engine.conventions
    
    def test_convention_lookup(self):
        """Test convention lookup functionality"""
        engine = WeaverEngine()
        
        convention = SemanticConvention(
            name="lookup_test",
            version="1.0.0",
            description="Lookup test",
            attributes={}
        )
        
        engine.register_convention(convention)
        found = engine.get_convention("lookup_test")
        
        assert found is not None
        assert found.name == "lookup_test"
    
    def test_convention_listing(self):
        """Test convention listing functionality"""
        engine = WeaverEngine()
        
        conventions = [
            SemanticConvention(name="conv1", version="1.0.0", description="First", attributes={}),
            SemanticConvention(name="conv2", version="1.0.0", description="Second", attributes={})
        ]
        
        for conv in conventions:
            engine.register_convention(conv)
        
        listed = engine.list_conventions()
        assert len(listed) == 2
        assert "conv1" in [c.name for c in listed]
        assert "conv2" in [c.name for c in listed]


class TestCodeGeneration:
    """Test code generation functionality"""
    
    def test_model_generator(self):
        """Test model generation from conventions"""
        generator = ModelGenerator()
        
        convention = SemanticConvention(
            name="user_service",
            version="1.0.0",
            description="User service convention",
            attributes={
                "user.id": {"type": "string", "description": "User ID"},
                "user.email": {"type": "string", "description": "User email"},
                "user.created_at": {"type": "datetime", "description": "Creation time"}
            }
        )
        
        generated_code = generator.generate_model(convention)
        
        assert "class" in generated_code
        assert "user_id" in generated_code.lower()
        assert "user_email" in generated_code.lower()
    
    def test_code_generator(self):
        """Test general code generation"""
        generator = CodeGenerator()
        
        template_data = {
            "class_name": "TestClass",
            "attributes": [
                {"name": "attr1", "type": "str"},
                {"name": "attr2", "type": "int"}
            ]
        }
        
        code = generator.generate_from_template("class_template", template_data)
        
        assert "class TestClass" in code
        assert "attr1" in code
        assert "attr2" in code
    
    def test_generator_with_custom_templates(self):
        """Test generator with custom template handling"""
        generator = CodeGenerator()
        
        # Test with custom template
        custom_template = """
        class {{ class_name }}:
            def __init__(self):
                {% for attr in attributes %}
                self.{{ attr.name }} = None
                {% endfor %}
        """
        
        template_data = {
            "class_name": "CustomClass",
            "attributes": [{"name": "custom_attr"}]
        }
        
        code = generator.generate_from_custom_template(custom_template, template_data)
        
        assert "class CustomClass" in code
        assert "self.custom_attr" in code


class TestWeaverValidation:
    """Test Weaver validation functionality"""
    
    def test_convention_validator(self):
        """Test convention validation"""
        validator = ConventionValidator()
        
        # Test valid convention
        valid_convention = SemanticConvention(
            name="valid",
            version="1.0.0",
            description="Valid convention",
            attributes={
                "valid.attr": {"type": "string", "description": "Valid attribute"}
            }
        )
        
        result = validator.validate(valid_convention)
        assert result.is_valid == True
        assert len(result.errors) == 0
    
    def test_convention_validation_errors(self):
        """Test convention validation error detection"""
        validator = ConventionValidator()
        
        # Test invalid convention (missing required fields)
        invalid_convention = SemanticConvention(
            name="",  # Empty name
            version="invalid_version",  # Invalid version
            description="",
            attributes={
                "invalid.attr": {}  # Missing type
            }
        )
        
        result = validator.validate(invalid_convention)
        assert result.is_valid == False
        assert len(result.errors) > 0
    
    def test_attribute_validation(self):
        """Test attribute validation"""
        validator = ConventionValidator()
        
        # Test valid attributes
        valid_attributes = {
            "service.name": {"type": "string", "description": "Service name"},
            "service.version": {"type": "string", "description": "Service version"},
            "service.instance.id": {"type": "string", "description": "Instance ID"}
        }
        
        result = validator.validate_attributes(valid_attributes)
        assert result.is_valid == True
    
    def test_attribute_validation_errors(self):
        """Test attribute validation error detection"""
        validator = ConventionValidator()
        
        # Test invalid attributes
        invalid_attributes = {
            "invalid.attr": {},  # Missing type
            "another.invalid": {"type": "invalid_type"},  # Invalid type
            "": {"type": "string"}  # Empty name
        }
        
        result = validator.validate_attributes(invalid_attributes)
        assert result.is_valid == False
        assert len(result.errors) > 0


class TestMultiLayerWeaver:
    """Test multi-layer Weaver functionality"""
    
    def test_multilayer_initialization(self):
        """Test multi-layer Weaver initialization"""
        multilayer = MultiLayerWeaver()
        
        assert multilayer is not None
        assert hasattr(multilayer, 'layers')
        assert hasattr(multilayer, 'feedback_loop')
    
    def test_layer_creation(self):
        """Test layer creation in multi-layer system"""
        multilayer = MultiLayerWeaver()
        
        layer = multilayer.create_layer("test_layer", "Test layer description")
        
        assert layer.name == "test_layer"
        assert layer.description == "Test layer description"
        assert layer in multilayer.layers
    
    def test_layer_interaction(self):
        """Test interaction between layers"""
        multilayer = MultiLayerWeaver()
        
        # Create layers
        layer1 = multilayer.create_layer("layer1", "First layer")
        layer2 = multilayer.create_layer("layer2", "Second layer")
        
        # Test layer communication
        result = multilayer.communicate_between_layers(layer1, layer2, "test_message")
        
        assert result is not None
    
    def test_feedback_loop(self):
        """Test feedback loop functionality"""
        multilayer = MultiLayerWeaver()
        
        # Create a simple feedback scenario
        feedback_data = {
            "layer": "test_layer",
            "performance": 0.85,
            "suggestions": ["optimize_algorithm", "reduce_complexity"]
        }
        
        result = multilayer.process_feedback(feedback_data)
        
        assert result is not None
        assert result.processed == True


class TestWeaverLoop:
    """Test Weaver autonomous loop functionality"""
    
    def test_loop_initialization(self):
        """Test Weaver loop initialization"""
        loop = WeaverLoop()
        
        assert loop is not None
        assert hasattr(loop, 'cycle_count')
        assert hasattr(loop, 'is_running')
    
    def test_single_cycle_execution(self):
        """Test single cycle execution"""
        loop = WeaverLoop()
        
        # Mock cycle execution
        with patch.object(loop, 'execute_cycle') as mock_execute:
            mock_execute.return_value = {"status": "completed", "features": 1}
            
            result = loop.run_single_cycle()
            
            assert result["status"] == "completed"
            assert result["features"] == 1
            mock_execute.assert_called_once()
    
    def test_continuous_loop_execution(self):
        """Test continuous loop execution"""
        loop = WeaverLoop()
        
        # Mock continuous execution
        with patch.object(loop, 'execute_cycle') as mock_execute:
            mock_execute.side_effect = [
                {"status": "completed", "features": 1},
                {"status": "completed", "features": 2},
                {"status": "stopped", "features": 0}
            ]
            
            results = loop.run_continuous(max_cycles=3)
            
            assert len(results) == 3
            assert results[0]["features"] == 1
            assert results[1]["features"] == 2
            assert results[2]["status"] == "stopped"
    
    def test_loop_monitoring(self):
        """Test loop monitoring and metrics"""
        loop = WeaverLoop()
        
        # Run some cycles
        with patch.object(loop, 'execute_cycle') as mock_execute:
            mock_execute.return_value = {"status": "completed", "features": 1}
            
            loop.run_single_cycle()
            loop.run_single_cycle()
            
            metrics = loop.get_metrics()
            
            assert metrics["total_cycles"] == 2
            assert metrics["successful_cycles"] == 2
            assert metrics["total_features"] == 2


class TestWeaverIntegration:
    """Test Weaver system integration"""
    
    def test_full_generation_workflow(self):
        """Test complete generation workflow"""
        engine = WeaverEngine()
        generator = ModelGenerator()
        validator = ConventionValidator()
        
        # Create and register convention
        convention = SemanticConvention(
            name="integration_test",
            version="1.0.0",
            description="Integration test",
            attributes={
                "test.attribute": {"type": "string", "description": "Test attribute"}
            }
        )
        
        # Validate convention
        validation_result = validator.validate(convention)
        assert validation_result.is_valid == True
        
        # Register with engine
        engine.register_convention(convention)
        
        # Generate code
        generated_code = generator.generate_model(convention)
        
        assert "class" in generated_code
        assert "integration_test" in generated_code.lower()
    
    def test_weaver_with_external_data(self):
        """Test Weaver with external data sources"""
        engine = WeaverEngine()
        
        # Mock external data source
        external_data = {
            "service_name": "test_service",
            "version": "1.0.0",
            "attributes": [
                {"name": "external.attr1", "type": "string"},
                {"name": "external.attr2", "type": "integer"}
            ]
        }
        
        # Convert external data to convention
        convention = engine.create_convention_from_external_data(external_data)
        
        assert convention.name == "test_service"
        assert len(convention.attributes) == 2
        assert "external.attr1" in convention.attributes


class TestWeaverPerformance:
    """Test Weaver system performance"""
    
    def test_large_convention_processing(self):
        """Test processing of large conventions"""
        engine = WeaverEngine()
        generator = ModelGenerator()
        
        # Create large convention
        large_attributes = {}
        for i in range(100):
            large_attributes[f"attr.{i}"] = {
                "type": "string",
                "description": f"Attribute {i}"
            }
        
        convention = SemanticConvention(
            name="large_convention",
            version="1.0.0",
            description="Large convention test",
            attributes=large_attributes
        )
        
        # Test processing performance
        import time
        start_time = time.time()
        
        engine.register_convention(convention)
        generated_code = generator.generate_model(convention)
        
        end_time = time.time()
        
        # Should complete in reasonable time (< 5 seconds)
        assert (end_time - start_time) < 5.0
        assert len(generated_code) > 0
    
    def test_concurrent_generation(self):
        """Test concurrent code generation"""
        import threading
        import time
        
        generator = ModelGenerator()
        results = []
        
        def generate_convention(convention_id):
            convention = SemanticConvention(
                name=f"convention_{convention_id}",
                version="1.0.0",
                description=f"Convention {convention_id}",
                attributes={"test.attr": {"type": "string"}}
            )
            
            code = generator.generate_model(convention)
            results.append((convention_id, len(code)))
        
        # Run concurrent generations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_convention, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all generations completed
        assert len(results) == 5
        for convention_id, code_length in results:
            assert code_length > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 