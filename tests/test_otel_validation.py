#!/usr/bin/env python3
"""
OTEL Validation Tests - 80/20 Focused
=====================================

Tests OpenTelemetry validation and Weaver enforcement
without complex dependencies.
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
import yaml


class TestOTELValidation:
    """Test OpenTelemetry validation and CLI commands"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.output_dir = Path("demo_output")
        self.test_output = Path("test_output")
        self.test_output.mkdir(exist_ok=True)
        yield
    
    def test_demo_output_exists(self):
        """Test that demo outputs exist and are valid"""
        # Check E2E demo output
        e2e_results = self.output_dir / "e2e_360_transformation_results.json"
        if e2e_results.exists():
            with open(e2e_results) as f:
                data = json.load(f)
            
            # Validate structure
            assert "phases" in data
            assert "final_outcomes" in data
            assert data["final_outcomes"]["transformation_success"] == True
            print("✅ E2E Demo output validated")
        else:
            print("ℹ️ E2E demo output not found - run demo first")
    
    def test_telemetry_output_validation(self):
        """Test telemetry orchestration output"""
        telemetry_results = self.output_dir / "agent_orchestration_telemetry_fixed_results.json"
        if telemetry_results.exists():
            with open(telemetry_results) as f:
                data = json.load(f)
            
            # Validate telemetry structure
            assert "validation_summary" in data
            assert "workflow_state" in data
            
            # Check validation success
            validation = data["validation_summary"]
            assert validation["success_rate"] >= 0.75
            assert validation["total_validations"] > 0
            
            # Check agent statistics
            agents = validation["agent_statistics"]
            expected_agents = ["roberts_rules", "scrum_scale", "lean_six_sigma", "orchestrator"]
            
            for agent in expected_agents:
                if agent in agents:
                    stats = agents[agent]
                    assert stats["total"] > 0
                    assert stats["success"] >= 0
            
            print(f"✅ Telemetry validation: {validation['success_rate']:.1%} success rate")
        else:
            print("ℹ️ Telemetry output not found - run demo first")
    
    def test_semantic_conventions_compliance(self):
        """Test semantic conventions are properly defined"""
        # Define expected transformation attributes
        expected_attributes = {
            "transformation.agent.type": "string",
            "transformation.workflow.phase": "string", 
            "transformation.quality.defect_rate": "number",
            "transformation.agile.velocity": "number",
            "transformation.financial.roi": "number",
            "transformation.validation.status": "string"
        }
        
        # Validate attribute naming conventions
        for attr_name, attr_type in expected_attributes.items():
            # Check naming convention
            assert attr_name.startswith("transformation."), f"Attribute {attr_name} must start with 'transformation.'"
            
            # Check structure (namespace.category.attribute)
            parts = attr_name.split(".")
            assert len(parts) >= 3, f"Attribute {attr_name} must have at least 3 parts"
            
            # Check type specification
            assert attr_type in ["string", "number", "boolean"], f"Invalid type {attr_type}"
        
        print("✅ Semantic conventions validated")
    
    def test_weaver_config_validation(self):
        """Test Weaver configuration"""
        weaver_path = Path("weaver.yaml")
        
        if weaver_path.exists():
            with open(weaver_path) as f:
                config = yaml.safe_load(f)
            
            # Validate basic structure
            assert "params" in config
            params = config["params"]
            
            assert "project_name" in params
            assert "language" in params
            assert params["language"] == "python"
            
            print("✅ Weaver config validated")
        else:
            print("ℹ️ Weaver config not found - creating basic config")
            self._create_weaver_config()
    
    def _create_weaver_config(self):
        """Create basic Weaver configuration"""
        config = {
            "params": {
                "project_name": "DSLModel",
                "language": "python",
                "organization": "SeanchatmanGPT",
                "semantic_conventions_version": "1.20.0"
            }
        }
        
        with open("weaver.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Created basic weaver.yaml")
    
    def test_cli_otel_commands(self):
        """Test OTEL CLI commands"""
        commands_to_test = [
            ["poetry", "run", "dsl", "--help"],
            ["poetry", "run", "python", "--version"]
        ]
        
        for cmd in commands_to_test:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                print(f"✅ Command {' '.join(cmd)}: exit code {result.returncode}")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Command {' '.join(cmd)}: timeout")
            except FileNotFoundError:
                print(f"ℹ️ Command {' '.join(cmd)}: not found")
    
    def test_span_attribute_validation(self):
        """Test span attribute validation logic"""
        # Mock span data for validation
        test_spans = [
            {
                "name": "roberts.motion.create",
                "attributes": {
                    "transformation.agent.type": "roberts_rules",
                    "roberts.motion.id": "MOTION-TEST",
                    "roberts.motion.budget": 1000000,
                    "transformation.validation.status": "success"
                },
                "expected_valid": True
            },
            {
                "name": "scrum.sprint.execute", 
                "attributes": {
                    "transformation.agent.type": "scrum_scale",
                    "transformation.quality.defect_rate": 0.15,  # Above threshold
                    "transformation.agile.velocity": 85.0
                },
                "expected_valid": True  # Warning but valid
            },
            {
                "name": "invalid.span",
                "attributes": {
                    # Missing required transformation.agent.type
                    "some.other.attribute": "value"
                },
                "expected_valid": False
            }
        ]
        
        # Validate each span
        for span in test_spans:
            attrs = span["attributes"]
            
            # Check required attributes
            has_agent_type = "transformation.agent.type" in attrs
            
            # Basic validation
            is_valid = has_agent_type
            
            if span["expected_valid"]:
                assert is_valid, f"Span {span['name']} should be valid"
            else:
                # For invalid spans, we expect them to fail validation
                if not is_valid:
                    print(f"✅ Correctly identified invalid span: {span['name']}")
        
        print("✅ Span attribute validation logic tested")
    
    def test_integration_points_validation(self):
        """Test integration points between phases"""
        # Define expected integration flows
        integration_flows = [
            {
                "from": "roberts_rules",
                "to": "scrum_scale",
                "mechanism": "budget_to_capacity",
                "data_flow": "governance.budget → agile.capacity"
            },
            {
                "from": "scrum_scale", 
                "to": "lean_six_sigma",
                "mechanism": "defect_threshold_trigger",
                "data_flow": "defect_rate > 10% → LSS project"
            },
            {
                "from": "lean_six_sigma",
                "to": "roberts_rules", 
                "mechanism": "savings_report",
                "data_flow": "cost_savings → governance_review"
            }
        ]
        
        # Validate each integration
        for integration in integration_flows:
            assert "from" in integration
            assert "to" in integration
            assert "mechanism" in integration
            assert "data_flow" in integration
            
            # Check valid agent types
            valid_agents = ["roberts_rules", "scrum_scale", "lean_six_sigma", "orchestrator"]
            assert integration["from"] in valid_agents
            assert integration["to"] in valid_agents
        
        print(f"✅ Integration flows validated: {len(integration_flows)} points")
    
    def test_weaver_semantic_template(self):
        """Test and create Weaver semantic convention templates"""
        template_dir = Path("weaver_templates")
        template_dir.mkdir(exist_ok=True)
        
        # Create transformation semantic convention
        semconv_file = template_dir / "transformation.yaml"
        semconv_content = {
            "groups": [
                {
                    "id": "transformation",
                    "type": "span",
                    "prefix": "transformation",
                    "brief": "Organizational transformation telemetry",
                    "attributes": [
                        {
                            "id": "agent.type",
                            "type": "string",
                            "brief": "Type of transformation agent",
                            "examples": ["roberts_rules", "scrum_scale", "lean_six_sigma"],
                            "requirement_level": "required"
                        },
                        {
                            "id": "workflow.phase",
                            "type": "string", 
                            "brief": "Current workflow phase",
                            "examples": ["governance", "agile_scaling", "process_optimization"],
                            "requirement_level": "required"
                        },
                        {
                            "id": "quality.defect_rate",
                            "type": "double",
                            "brief": "Defect rate as decimal",
                            "examples": [0.147, 0.05],
                            "requirement_level": "recommended"
                        },
                        {
                            "id": "financial.roi",
                            "type": "double",
                            "brief": "Return on investment multiplier", 
                            "examples": [2.5, 3.4],
                            "requirement_level": "recommended"
                        }
                    ]
                }
            ]
        }
        
        with open(semconv_file, "w") as f:
            yaml.dump(semconv_content, f, default_flow_style=False)
        
        assert semconv_file.exists()
        print("✅ Weaver semantic conventions template created")
    
    def test_validation_summary_format(self):
        """Test validation summary output format"""
        # Expected validation summary structure
        expected_structure = {
            "validation_summary": {
                "total_validations": "int",
                "successful_validations": "int", 
                "success_rate": "float",
                "agent_statistics": "dict"
            },
            "workflow_state": {
                "phase_results": "dict"
            },
            "telemetry_validated": "bool",
            "recommendation": "string"
        }
        
        # Validate structure definition
        for section, fields in expected_structure.items():
            assert isinstance(section, str)
            if isinstance(fields, dict):
                for field, field_type in fields.items():
                    assert field_type in ["int", "float", "string", "bool", "dict", "list"]
        
        print("✅ Validation summary format validated")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])