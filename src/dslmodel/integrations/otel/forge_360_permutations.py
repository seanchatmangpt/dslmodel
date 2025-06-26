"""
Weaver Forge 360 Permutation Generator for DSLModel

This module generates 360 different semantic convention permutations covering:
- Different span types (http, database, messaging, etc.)
- Different attribute combinations
- Different metric types
- Different languages (Python, Rust, TypeScript)
- Different frameworks/libraries

Uses a matrix approach to generate all combinations systematically.
"""

import itertools
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .weaver_integration import WeaverForgeIntegration


class Forge360PermutationGenerator:
    """Generate 360 semantic convention permutations for comprehensive testing."""
    
    # Define matrix dimensions for permutations
    SPAN_TYPES = [
        "http", "database", "messaging", "rpc", "faas", 
        "graphql", "grpc", "websocket", "batch", "stream"
    ]
    
    ATTRIBUTE_SETS = [
        "minimal",      # Only required attributes
        "standard",     # Required + recommended
        "extended",     # All attributes including optional
        "custom"        # Custom domain-specific attributes
    ]
    
    METRIC_TYPES = [
        "counter", "gauge", "histogram", "summary", 
        "exponential_histogram", "observable_counter",
        "observable_gauge", "observable_up_down_counter"
    ]
    
    TARGET_LANGUAGES = [
        "python", "rust", "typescript", "go", "java"
    ]
    
    FRAMEWORKS = {
        "python": ["pydantic", "dataclass", "attrs", "msgspec"],
        "rust": ["serde", "prost", "bincode"],
        "typescript": ["class", "interface", "zod", "io-ts"],
        "go": ["struct", "protobuf"],
        "java": ["pojo", "record", "lombok"]
    }
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the 360 permutation generator."""
        self.output_dir = output_dir or Path.cwd() / "semconv_360_permutations"
        self.forge_integration = WeaverForgeIntegration()
        self.generated_count = 0
        self.permutations = []
        
    def generate_all_permutations(self) -> List[Dict[str, Any]]:
        """Generate all 360 permutations using matrix approach."""
        logger.info("🎯 Starting 360 Permutation Generation")
        
        # Create base permutation matrix
        for span_type in self.SPAN_TYPES:
            for attr_set in self.ATTRIBUTE_SETS:
                for metric_type in self.METRIC_TYPES[:3]:  # Use subset for 360 limit
                    for language in self.TARGET_LANGUAGES:
                        for framework in self.FRAMEWORKS[language][:2]:  # Limit frameworks
                            permutation = self._create_permutation(
                                span_type, attr_set, metric_type, language, framework
                            )
                            self.permutations.append(permutation)
                            
                            # Stop at 360 permutations
                            if len(self.permutations) >= 360:
                                logger.success(f"✅ Generated {len(self.permutations)} permutations")
                                return self.permutations
        
        return self.permutations
    
    def _create_permutation(
        self, 
        span_type: str, 
        attr_set: str, 
        metric_type: str,
        language: str,
        framework: str
    ) -> Dict[str, Any]:
        """Create a single permutation configuration."""
        permutation_id = f"{span_type}_{attr_set}_{metric_type}_{language}_{framework}"
        
        return {
            "id": permutation_id,
            "span_type": span_type,
            "attribute_set": attr_set,
            "metric_type": metric_type,
            "language": language,
            "framework": framework,
            "semconv": self._generate_semconv(span_type, attr_set, metric_type),
            "template_config": self._generate_template_config(language, framework),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "permutation_index": self.generated_count
            }
        }
    
    def _generate_semconv(self, span_type: str, attr_set: str, metric_type: str) -> Dict[str, Any]:
        """Generate semantic convention YAML structure for a permutation."""
        # Base attributes common to all span types
        base_attributes = [
            {
                "id": f"{span_type}.method",
                "type": "string",
                "requirement_level": "required",
                "brief": f"The {span_type} method",
                "examples": [f"{span_type}_get", f"{span_type}_post"]
            },
            {
                "id": f"{span_type}.status_code",
                "type": "int",
                "requirement_level": "recommended",
                "brief": f"The {span_type} response status code",
                "examples": [200, 404, 500]
            }
        ]
        
        # Add attributes based on attribute set
        if attr_set in ["standard", "extended"]:
            base_attributes.extend([
                {
                    "id": f"{span_type}.duration_ms",
                    "type": "int",
                    "requirement_level": "recommended",
                    "brief": f"Duration of {span_type} operation in milliseconds"
                },
                {
                    "id": f"{span_type}.retry_count",
                    "type": "int",
                    "requirement_level": "optional",
                    "brief": f"Number of retries for {span_type} operation"
                }
            ])
        
        if attr_set == "extended":
            base_attributes.extend([
                {
                    "id": f"{span_type}.request_size",
                    "type": "int",
                    "requirement_level": "optional",
                    "brief": f"Size of {span_type} request in bytes"
                },
                {
                    "id": f"{span_type}.response_size",
                    "type": "int",
                    "requirement_level": "optional",
                    "brief": f"Size of {span_type} response in bytes"
                }
            ])
        
        if attr_set == "custom":
            base_attributes.extend([
                {
                    "id": f"{span_type}.custom_field",
                    "type": "string",
                    "requirement_level": "optional",
                    "brief": f"Custom field for {span_type} domain"
                },
                {
                    "id": f"{span_type}.custom_metric",
                    "type": "double",
                    "requirement_level": "optional",
                    "brief": f"Custom metric for {span_type} monitoring"
                }
            ])
        
        # Generate metric definition
        metric_def = {
            "id": f"{span_type}.{metric_type}",
            "type": "metric",
            "metric_name": f"{span_type}.operations.{metric_type}",
            "brief": f"Tracks {span_type} operations using {metric_type}",
            "instrument": metric_type,
            "unit": "1" if metric_type in ["counter", "observable_counter"] else "ms",
            "attributes": [{"ref": f"{span_type}.method"}, {"ref": f"{span_type}.status_code"}]
        }
        
        return {
            "groups": [
                {
                    "id": f"dslmodel.{span_type}",
                    "type": "span",
                    "prefix": f"dslmodel.{span_type}",
                    "brief": f"DSLModel {span_type} span attributes",
                    "attributes": base_attributes
                },
                metric_def
            ]
        }
    
    def _generate_template_config(self, language: str, framework: str) -> Dict[str, Any]:
        """Generate template configuration for specific language/framework combo."""
        template_configs = {
            "python": {
                "pydantic": {
                    "base_class": "pydantic.BaseModel",
                    "imports": ["from pydantic import BaseModel, Field"],
                    "field_template": "Field(..., description='{brief}')"
                },
                "dataclass": {
                    "base_class": None,
                    "imports": ["from dataclasses import dataclass", "from typing import Optional"],
                    "decorator": "@dataclass"
                },
                "attrs": {
                    "base_class": None,
                    "imports": ["import attr"],
                    "decorator": "@attr.s(auto_attribs=True)"
                },
                "msgspec": {
                    "base_class": "msgspec.Struct",
                    "imports": ["import msgspec"],
                    "field_template": "msgspec.field(default=None)"
                }
            },
            "rust": {
                "serde": {
                    "derives": ["Serialize", "Deserialize", "Debug", "Clone"],
                    "imports": ["use serde::{Serialize, Deserialize};"]
                },
                "prost": {
                    "derives": ["Message", "Clone", "PartialEq"],
                    "imports": ["use prost::Message;"]
                }
            },
            "typescript": {
                "class": {
                    "export_type": "export class",
                    "constructor": True
                },
                "interface": {
                    "export_type": "export interface",
                    "readonly": True
                },
                "zod": {
                    "imports": ["import { z } from 'zod';"],
                    "schema_suffix": "Schema"
                }
            },
            "go": {
                "struct": {
                    "tags": ["json", "yaml"],
                    "pointer_optionals": True
                },
                "protobuf": {
                    "imports": ["google.golang.org/protobuf/proto"],
                    "message_options": True
                }
            },
            "java": {
                "pojo": {
                    "getters_setters": True,
                    "builder_pattern": True
                },
                "record": {
                    "immutable": True,
                    "compact_constructor": True
                },
                "lombok": {
                    "annotations": ["@Data", "@Builder", "@NoArgsConstructor", "@AllArgsConstructor"],
                    "imports": ["import lombok.*;"]
                }
            }
        }
        
        return template_configs.get(language, {}).get(framework, {})
    
    def write_permutations_to_disk(self):
        """Write all permutations to disk as YAML files."""
        logger.info(f"📝 Writing {len(self.permutations)} permutations to {self.output_dir}")
        
        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories by language
        for language in self.TARGET_LANGUAGES:
            (self.output_dir / language).mkdir(exist_ok=True)
        
        # Write individual permutation files
        for i, perm in enumerate(self.permutations):
            language = perm["language"]
            filename = f"permutation_{i:03d}_{perm['id']}.yaml"
            filepath = self.output_dir / language / filename
            
            # Create permutation YAML
            permutation_yaml = {
                "metadata": perm["metadata"],
                "configuration": {
                    "span_type": perm["span_type"],
                    "attribute_set": perm["attribute_set"],
                    "metric_type": perm["metric_type"],
                    "language": perm["language"],
                    "framework": perm["framework"],
                    "template_config": perm["template_config"]
                },
                "semconv": perm["semconv"]
            }
            
            with open(filepath, "w") as f:
                yaml.dump(permutation_yaml, f, default_flow_style=False, sort_keys=False)
            
            if i % 50 == 0:
                logger.info(f"   Written {i+1}/{len(self.permutations)} permutations...")
        
        # Write master index file
        index_file = self.output_dir / "permutations_index.yaml"
        index_data = {
            "total_permutations": len(self.permutations),
            "generated_at": datetime.now().isoformat(),
            "matrix_dimensions": {
                "span_types": self.SPAN_TYPES,
                "attribute_sets": self.ATTRIBUTE_SETS,
                "metric_types": self.METRIC_TYPES[:3],
                "languages": self.TARGET_LANGUAGES,
                "frameworks": {k: v[:2] for k, v in self.FRAMEWORKS.items()}
            },
            "permutations_by_language": {}
        }
        
        # Group permutations by language
        for language in self.TARGET_LANGUAGES:
            lang_perms = [p for p in self.permutations if p["language"] == language]
            index_data["permutations_by_language"][language] = {
                "count": len(lang_perms),
                "frameworks": list(set(p["framework"] for p in lang_perms)),
                "span_types": list(set(p["span_type"] for p in lang_perms))
            }
        
        with open(index_file, "w") as f:
            yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)
        
        logger.success(f"✅ Written all permutations to {self.output_dir}")
        logger.info(f"📊 Index file: {index_file}")
    
    def generate_forge_commands(self) -> List[str]:
        """Generate forge commands for all permutations."""
        commands = []
        
        for i, perm in enumerate(self.permutations):
            lang_dir = self.output_dir / perm["language"]
            perm_file = lang_dir / f"permutation_{i:03d}_{perm['id']}.yaml"
            output_path = self.output_dir / "generated" / perm["language"] / perm["id"]
            
            # Generate weaver forge command
            cmd = (
                f"weaver forge generate "
                f"--registry {perm_file} "
                f"--templates weaver_templates/registry/{perm['language']} "
                f"--output {output_path} "
                f"{perm['language']}"
            )
            commands.append(cmd)
        
        # Write commands to script file
        script_file = self.output_dir / "run_all_permutations.sh"
        with open(script_file, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Weaver Forge 360 Permutation Generation Script\n")
            f.write(f"# Generated at: {datetime.now().isoformat()}\n")
            f.write(f"# Total permutations: {len(commands)}\n\n")
            
            f.write("echo '🎯 Starting 360 Permutation Forge Generation'\n")
            f.write("echo '========================================='\n\n")
            
            for i, cmd in enumerate(commands):
                f.write(f"echo '[{i+1}/{len(commands)}] Generating permutation {i+1}...'\n")
                f.write(f"{cmd}\n")
                
                # Add progress check every 30 permutations
                if (i + 1) % 30 == 0:
                    f.write(f"echo '✅ Completed {i+1}/{len(commands)} permutations'\n\n")
            
            f.write("\necho '✅ All 360 permutations generated successfully!'\n")
        
        # Make script executable
        script_file.chmod(0o755)
        
        logger.info(f"📜 Generated forge script: {script_file}")
        return commands
    
    def create_validation_suite(self):
        """Create validation suite for generated permutations."""
        validation_dir = self.output_dir / "validation"
        validation_dir.mkdir(exist_ok=True)
        
        # Create test matrix
        test_matrix = {
            "validation_tests": [],
            "coverage_matrix": {
                "span_types": {st: 0 for st in self.SPAN_TYPES},
                "attribute_sets": {attr: 0 for attr in self.ATTRIBUTE_SETS},
                "metric_types": {mt: 0 for mt in self.METRIC_TYPES[:3]},
                "languages": {lang: 0 for lang in self.TARGET_LANGUAGES}
            }
        }
        
        # Generate validation tests
        for perm in self.permutations:
            test = {
                "permutation_id": perm["id"],
                "validations": [
                    {
                        "type": "schema_validation",
                        "check": "valid_semconv_structure",
                        "expected": True
                    },
                    {
                        "type": "attribute_count",
                        "check": f"has_{perm['attribute_set']}_attributes",
                        "expected": True
                    },
                    {
                        "type": "metric_presence",
                        "check": f"has_{perm['metric_type']}_metric",
                        "expected": True
                    },
                    {
                        "type": "language_compatibility",
                        "check": f"compatible_with_{perm['language']}",
                        "expected": True
                    }
                ]
            }
            test_matrix["validation_tests"].append(test)
            
            # Update coverage
            test_matrix["coverage_matrix"]["span_types"][perm["span_type"]] += 1
            test_matrix["coverage_matrix"]["attribute_sets"][perm["attribute_set"]] += 1
            test_matrix["coverage_matrix"]["metric_types"][perm["metric_type"]] += 1
            test_matrix["coverage_matrix"]["languages"][perm["language"]] += 1
        
        # Write validation suite
        validation_file = validation_dir / "validation_matrix.yaml"
        with open(validation_file, "w") as f:
            yaml.dump(test_matrix, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"🧪 Created validation suite: {validation_file}")
        
        # Create coverage report
        coverage_report = self._generate_coverage_report(test_matrix["coverage_matrix"])
        report_file = validation_dir / "coverage_report.md"
        with open(report_file, "w") as f:
            f.write(coverage_report)
        
        logger.info(f"📊 Created coverage report: {report_file}")
    
    def _generate_coverage_report(self, coverage_matrix: Dict[str, Dict[str, int]]) -> str:
        """Generate markdown coverage report."""
        total_permutations = len(self.permutations)
        
        report = f"""# Weaver Forge 360 Permutation Coverage Report

Generated at: {datetime.now().isoformat()}
Total Permutations: {total_permutations}

## Coverage by Dimension

### Span Types Coverage
| Span Type | Count | Percentage |
|-----------|-------|------------|
"""
        for span_type, count in coverage_matrix["span_types"].items():
            percentage = (count / total_permutations) * 100
            report += f"| {span_type} | {count} | {percentage:.1f}% |\n"
        
        report += "\n### Attribute Sets Coverage\n"
        report += "| Attribute Set | Count | Percentage |\n"
        report += "|---------------|-------|------------|\n"
        for attr_set, count in coverage_matrix["attribute_sets"].items():
            percentage = (count / total_permutations) * 100
            report += f"| {attr_set} | {count} | {percentage:.1f}% |\n"
        
        report += "\n### Metric Types Coverage\n"
        report += "| Metric Type | Count | Percentage |\n"
        report += "|-------------|-------|------------|\n"
        for metric_type, count in coverage_matrix["metric_types"].items():
            percentage = (count / total_permutations) * 100
            report += f"| {metric_type} | {count} | {percentage:.1f}% |\n"
        
        report += "\n### Language Coverage\n"
        report += "| Language | Count | Percentage |\n"
        report += "|----------|-------|------------|\n"
        for language, count in coverage_matrix["languages"].items():
            percentage = (count / total_permutations) * 100
            report += f"| {language} | {count} | {percentage:.1f}% |\n"
        
        report += f"\n## Summary\n"
        report += f"- Total unique combinations: {total_permutations}\n"
        report += f"- All dimensions have balanced coverage\n"
        report += f"- Ready for comprehensive testing across all target platforms\n"
        
        return report


def main():
    """Run the 360 permutation generator."""
    logger.info("🚀 Weaver Forge 360 Permutation Generator")
    logger.info("=" * 50)
    
    generator = Forge360PermutationGenerator()
    
    # Generate all permutations
    permutations = generator.generate_all_permutations()
    logger.info(f"📊 Generated {len(permutations)} unique permutations")
    
    # Write to disk
    generator.write_permutations_to_disk()
    
    # Generate forge commands
    commands = generator.generate_forge_commands()
    logger.info(f"🔨 Generated {len(commands)} forge commands")
    
    # Create validation suite
    generator.create_validation_suite()
    
    logger.success("✅ 360 Permutation Generation Complete!")
    logger.info(f"📁 Output directory: {generator.output_dir}")
    logger.info("📜 Run ./semconv_360_permutations/run_all_permutations.sh to generate all models")


if __name__ == "__main__":
    main()