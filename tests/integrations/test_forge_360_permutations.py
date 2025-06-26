"""
Tests for Forge 360 Permutation Generator

Validates the generation of 360 semantic convention permutations
across multiple dimensions.
"""

import pytest
from pathlib import Path
import yaml
import shutil
from typing import Dict, List

from dslmodel.integrations.otel.forge_360_permutations import Forge360PermutationGenerator


class TestForge360PermutationGenerator:
    """Test suite for 360 permutation generator."""
    
    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory for tests."""
        output_dir = tmp_path / "test_permutations"
        output_dir.mkdir()
        yield output_dir
        # Cleanup handled by pytest tmp_path
    
    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create generator instance with temp directory."""
        return Forge360PermutationGenerator(temp_output_dir)
    
    def test_generate_exactly_360_permutations(self, generator):
        """Test that exactly 360 permutations are generated."""
        permutations = generator.generate_all_permutations()
        assert len(permutations) == 360
        assert len(generator.permutations) == 360
    
    def test_permutation_structure(self, generator):
        """Test that each permutation has required structure."""
        permutations = generator.generate_all_permutations()
        
        for perm in permutations[:10]:  # Check first 10
            # Check required fields
            assert "id" in perm
            assert "span_type" in perm
            assert "attribute_set" in perm
            assert "metric_type" in perm
            assert "language" in perm
            assert "framework" in perm
            assert "semconv" in perm
            assert "template_config" in perm
            assert "metadata" in perm
            
            # Check metadata structure
            assert "generated_at" in perm["metadata"]
            assert "generator_version" in perm["metadata"]
            assert "permutation_index" in perm["metadata"]
            
            # Check semconv structure
            assert "groups" in perm["semconv"]
            assert len(perm["semconv"]["groups"]) >= 2  # At least span group and metric
    
    def test_unique_permutation_ids(self, generator):
        """Test that all permutation IDs are unique."""
        permutations = generator.generate_all_permutations()
        ids = [p["id"] for p in permutations]
        assert len(ids) == len(set(ids))  # All IDs should be unique
    
    def test_matrix_coverage(self, generator):
        """Test that all matrix dimensions are covered."""
        permutations = generator.generate_all_permutations()
        
        # Check span type coverage
        span_types = set(p["span_type"] for p in permutations)
        assert len(span_types) == len(generator.SPAN_TYPES)
        
        # Check attribute set coverage
        attr_sets = set(p["attribute_set"] for p in permutations)
        assert len(attr_sets) == len(generator.ATTRIBUTE_SETS)
        
        # Check language coverage
        languages = set(p["language"] for p in permutations)
        assert len(languages) == len(generator.TARGET_LANGUAGES)
        
        # Check metric types (limited subset used)
        metric_types = set(p["metric_type"] for p in permutations)
        assert len(metric_types) >= 3  # At least 3 metric types used
    
    def test_attribute_generation_by_set(self, generator):
        """Test that attribute sets generate correct number of attributes."""
        permutations = generator.generate_all_permutations()
        
        # Group by attribute set
        by_attr_set = {}
        for perm in permutations:
            attr_set = perm["attribute_set"]
            if attr_set not in by_attr_set:
                by_attr_set[attr_set] = []
            by_attr_set[attr_set].append(perm)
        
        # Check attribute counts
        for attr_set, perms in by_attr_set.items():
            sample_perm = perms[0]
            groups = sample_perm["semconv"]["groups"]
            span_group = next(g for g in groups if g.get("type") == "span")
            attributes = span_group.get("attributes", [])
            
            if attr_set == "minimal":
                assert len(attributes) >= 2  # At least method and status_code
            elif attr_set == "standard":
                assert len(attributes) >= 4  # Additional recommended attributes
            elif attr_set == "extended":
                assert len(attributes) >= 6  # All attributes
            elif attr_set == "custom":
                assert any("custom" in attr["id"] for attr in attributes)
    
    def test_language_framework_compatibility(self, generator):
        """Test that frameworks match their languages correctly."""
        permutations = generator.generate_all_permutations()
        
        for perm in permutations:
            language = perm["language"]
            framework = perm["framework"]
            assert framework in generator.FRAMEWORKS[language]
    
    def test_write_permutations_to_disk(self, generator):
        """Test writing permutations to disk."""
        permutations = generator.generate_all_permutations()
        generator.write_permutations_to_disk()
        
        # Check directory structure
        output_dir = generator.output_dir
        assert output_dir.exists()
        
        # Check language directories
        for language in generator.TARGET_LANGUAGES:
            lang_dir = output_dir / language
            assert lang_dir.exists()
            assert lang_dir.is_dir()
        
        # Check index file
        index_file = output_dir / "permutations_index.yaml"
        assert index_file.exists()
        
        with open(index_file) as f:
            index_data = yaml.safe_load(f)
        
        assert index_data["total_permutations"] == 360
        assert "matrix_dimensions" in index_data
        assert "permutations_by_language" in index_data
    
    def test_generate_forge_commands(self, generator):
        """Test forge command generation."""
        permutations = generator.generate_all_permutations()
        generator.write_permutations_to_disk()
        commands = generator.generate_forge_commands()
        
        assert len(commands) == 360
        
        # Check command format
        for cmd in commands[:5]:  # Check first 5
            assert cmd.startswith("weaver forge generate")
            assert "--registry" in cmd
            assert "--templates" in cmd
            assert "--output" in cmd
        
        # Check script file
        script_file = generator.output_dir / "run_all_permutations.sh"
        assert script_file.exists()
        assert script_file.stat().st_mode & 0o111  # Check executable
    
    def test_validation_suite_creation(self, generator):
        """Test validation suite generation."""
        permutations = generator.generate_all_permutations()
        generator.write_permutations_to_disk()
        generator.create_validation_suite()
        
        validation_dir = generator.output_dir / "validation"
        assert validation_dir.exists()
        
        # Check validation matrix
        validation_file = validation_dir / "validation_matrix.yaml"
        assert validation_file.exists()
        
        with open(validation_file) as f:
            validation_data = yaml.safe_load(f)
        
        assert len(validation_data["validation_tests"]) == 360
        assert "coverage_matrix" in validation_data
        
        # Check coverage report
        report_file = validation_dir / "coverage_report.md"
        assert report_file.exists()
        
        with open(report_file) as f:
            report_content = f.read()
        
        assert "Total Permutations: 360" in report_content
        assert "Coverage by Dimension" in report_content
    
    def test_semconv_metric_generation(self, generator):
        """Test that metrics are properly generated in semconv."""
        permutations = generator.generate_all_permutations()
        
        for perm in permutations[:10]:  # Check first 10
            groups = perm["semconv"]["groups"]
            
            # Find metric group
            metric_group = next(g for g in groups if g.get("type") == "metric")
            
            assert "metric_name" in metric_group
            assert "instrument" in metric_group
            assert "unit" in metric_group
            assert "attributes" in metric_group
            
            # Check metric type matches
            assert metric_group["instrument"] == perm["metric_type"]
    
    def test_template_config_generation(self, generator):
        """Test template configuration for different languages."""
        permutations = generator.generate_all_permutations()
        
        # Test Python configs
        python_perms = [p for p in permutations if p["language"] == "python"]
        for perm in python_perms[:5]:
            config = perm["template_config"]
            framework = perm["framework"]
            
            if framework == "pydantic":
                assert "base_class" in config
                assert "imports" in config
            elif framework == "dataclass":
                assert "decorator" in config
                assert config["decorator"] == "@dataclass"
        
        # Test Rust configs
        rust_perms = [p for p in permutations if p["language"] == "rust"]
        for perm in rust_perms[:5]:
            config = perm["template_config"]
            if perm["framework"] == "serde":
                assert "derives" in config
                assert "Serialize" in config["derives"]
    
    @pytest.mark.parametrize("span_type,expected_attrs", [
        ("http", ["http.method", "http.status_code"]),
        ("database", ["database.method", "database.status_code"]),
        ("messaging", ["messaging.method", "messaging.status_code"]),
    ])
    def test_span_type_attributes(self, generator, span_type, expected_attrs):
        """Test that span types generate correct base attributes."""
        permutations = generator.generate_all_permutations()
        
        # Find permutation with specific span type
        span_perms = [p for p in permutations if p["span_type"] == span_type]
        assert len(span_perms) > 0
        
        sample_perm = span_perms[0]
        groups = sample_perm["semconv"]["groups"]
        span_group = next(g for g in groups if g.get("type") == "span")
        
        attr_ids = [attr["id"] for attr in span_group["attributes"]]
        
        for expected_attr in expected_attrs:
            assert expected_attr in attr_ids


@pytest.mark.integration
class TestForge360Integration:
    """Integration tests for forge 360 system."""
    
    def test_end_to_end_generation(self, tmp_path):
        """Test complete end-to-end generation flow."""
        generator = Forge360PermutationGenerator(tmp_path / "e2e_test")
        
        # Generate permutations
        permutations = generator.generate_all_permutations()
        assert len(permutations) == 360
        
        # Write to disk
        generator.write_permutations_to_disk()
        
        # Generate commands
        commands = generator.generate_forge_commands()
        assert len(commands) == 360
        
        # Create validation
        generator.create_validation_suite()
        
        # Verify complete output structure
        output_dir = generator.output_dir
        assert (output_dir / "permutations_index.yaml").exists()
        assert (output_dir / "run_all_permutations.sh").exists()
        assert (output_dir / "validation").exists()
        
        # Count generated files
        yaml_files = list(output_dir.rglob("*.yaml"))
        assert len(yaml_files) > 360  # Permutations + index + validation files
    
    def test_coverage_balance(self, tmp_path):
        """Test that coverage is balanced across dimensions."""
        generator = Forge360PermutationGenerator(tmp_path / "coverage_test")
        permutations = generator.generate_all_permutations()
        
        # Calculate coverage percentages
        total = len(permutations)
        
        # Each span type should have roughly equal coverage
        span_coverage = {}
        for span_type in generator.SPAN_TYPES:
            count = len([p for p in permutations if p["span_type"] == span_type])
            span_coverage[span_type] = count / total
        
        # Check that coverage is relatively balanced (within 20% of expected)
        expected_coverage = 1.0 / len(generator.SPAN_TYPES)
        for span_type, coverage in span_coverage.items():
            assert abs(coverage - expected_coverage) < 0.2
    
    def test_permutation_reproducibility(self, tmp_path):
        """Test that generation is reproducible."""
        # Generate twice with same parameters
        gen1 = Forge360PermutationGenerator(tmp_path / "repro1")
        perms1 = gen1.generate_all_permutations()
        
        gen2 = Forge360PermutationGenerator(tmp_path / "repro2")
        perms2 = gen2.generate_all_permutations()
        
        # Should generate identical permutations
        assert len(perms1) == len(perms2)
        
        # Compare first 10 permutation IDs
        ids1 = [p["id"] for p in perms1[:10]]
        ids2 = [p["id"] for p in perms2[:10]]
        assert ids1 == ids2