#!/usr/bin/env python3
"""
Generate DSLModel 360 permutations
Creates all combinations of model types, mixins, and generation sources
"""

import itertools
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class DSLModelPermutation:
    """Single DSLModel permutation configuration"""
    model_type: str
    mixin_combo: str
    generation_source: str
    
    @property
    def name(self) -> str:
        """Generate unique name for this permutation"""
        return f"{self.model_type}_{self.mixin_combo}_{self.generation_source}"
    
    @property
    def attributes(self) -> Dict[str, Any]:
        """Generate OpenTelemetry attributes for this permutation"""
        return {
            "dslmodel.model_type": self.model_type,
            "dslmodel.mixin.combination": self.mixin_combo,
            "dslmodel.generation.source": self.generation_source,
            "dslmodel.permutation.id": self.name
        }
    
    def to_semantic_convention(self) -> Dict[str, Any]:
        """Convert to semantic convention format"""
        return {
            "id": f"dslmodel.permutation.{self.name}",
            "type": "span",
            "brief": f"DSLModel permutation: {self.model_type} with {self.mixin_combo} mixins from {self.generation_source}",
            "span_kind": "internal",
            "prefix": "dslmodel.permutation",
            "attributes": [
                {
                    "ref": "dslmodel.model_type",
                    "requirement_level": "required"
                },
                {
                    "ref": "dslmodel.mixin.combination",
                    "requirement_level": "required"
                },
                {
                    "ref": "dslmodel.generation.source",
                    "requirement_level": "required"
                }
            ]
        }

class DSLModel360Generator:
    """Generate all 360 permutations of DSLModel"""
    
    # Define the 6x10x6 matrix
    MODEL_TYPES = ["base", "fsm", "workflow", "agent", "event", "template"]
    
    MIXIN_COMBINATIONS = [
        "none", "jinja", "tool", "file", 
        "jinja_tool", "jinja_file", "tool_file", 
        "all", "fsm_jinja", "fsm_tool"
    ]
    
    GENERATION_SOURCES = ["prompt", "schema", "api", "template", "weaver", "manual"]
    
    def __init__(self):
        self.permutations: List[DSLModelPermutation] = []
        
    def generate_permutations(self) -> List[DSLModelPermutation]:
        """Generate all 360 permutations"""
        for model_type, mixin_combo, gen_source in itertools.product(
            self.MODEL_TYPES, self.MIXIN_COMBINATIONS, self.GENERATION_SOURCES
        ):
            permutation = DSLModelPermutation(
                model_type=model_type,
                mixin_combo=mixin_combo,
                generation_source=gen_source
            )
            self.permutations.append(permutation)
        
        return self.permutations
    
    def generate_semantic_conventions(self) -> Dict[str, Any]:
        """Generate semantic convention YAML structure"""
        groups = []
        
        # Base attributes group
        base_group = {
            "id": "dslmodel.permutation.attributes",
            "prefix": "dslmodel.permutation",
            "type": "attribute_group",
            "brief": "Attributes for DSLModel 360 permutations",
            "attributes": [
                {
                    "id": "id",
                    "type": "string",
                    "requirement_level": "required",
                    "brief": "Unique identifier for the permutation",
                    "examples": ["base_none_prompt", "fsm_jinja_api"]
                }
            ]
        }
        groups.append(base_group)
        
        # Generate span definitions for each permutation
        for perm in self.permutations:
            groups.append(perm.to_semantic_convention())
        
        return {"groups": groups}
    
    def generate_python_models(self) -> str:
        """Generate Python code for all permutations"""
        code = '''"""
DSLModel 360 Permutations
Auto-generated Python models for all DSLModel permutations
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dslmodel.mixins import JinjaMixin, ToolMixin, FileMixin, FSMMixin

# Base model types
'''
        
        # Generate model classes
        for perm in self.permutations:
            code += self._generate_model_class(perm)
        
        # Generate factory function
        code += '''

def create_dslmodel_permutation(
    model_type: str,
    mixin_combo: str, 
    generation_source: str,
    **kwargs
) -> BaseModel:
    """Factory function to create DSLModel permutation instances"""
    class_name = f"{model_type.title()}{mixin_combo.title().replace('_', '')}{generation_source.title()}Model"
    model_class = globals().get(class_name)
    
    if not model_class:
        raise ValueError(f"Unknown permutation: {model_type}_{mixin_combo}_{generation_source}")
    
    return model_class(**kwargs)

# Permutation registry
PERMUTATION_REGISTRY = {
'''
        
        for perm in self.permutations:
            code += f'    "{perm.name}": {self._get_class_name(perm)},\n'
        
        code += '}\n'
        
        return code
    
    def _generate_model_class(self, perm: DSLModelPermutation) -> str:
        """Generate a single model class"""
        class_name = self._get_class_name(perm)
        
        # Determine base class and mixins
        base_class = "BaseModel"
        mixins = []
        
        if perm.model_type == "fsm":
            mixins.append("FSMMixin")
        
        if "jinja" in perm.mixin_combo:
            mixins.append("JinjaMixin")
        if "tool" in perm.mixin_combo:
            mixins.append("ToolMixin")
        if "file" in perm.mixin_combo:
            mixins.append("FileMixin")
        
        # Build inheritance list
        inheritance = ", ".join([base_class] + mixins) if mixins else base_class
        
        return f'''
@dataclass
class {class_name}({inheritance}):
    """
    DSLModel Permutation: {perm.model_type} with {perm.mixin_combo} mixins
    Generated from: {perm.generation_source}
    """
    name: str = Field(default="{perm.name}", description="Permutation name")
    model_type: str = Field(default="{perm.model_type}", description="Model type")
    mixin_combo: str = Field(default="{perm.mixin_combo}", description="Mixin combination")
    generation_source: str = Field(default="{perm.generation_source}", description="Generation source")
    
    class Config:
        extra = "allow"
'''
    
    def _get_class_name(self, perm: DSLModelPermutation) -> str:
        """Generate class name for permutation"""
        model_type = perm.model_type.title()
        mixin = perm.mixin_combo.title().replace("_", "")
        source = perm.generation_source.title()
        return f"{model_type}{mixin}{source}Model"
    
    def generate_telemetry_config(self) -> Dict[str, Any]:
        """Generate OpenTelemetry configuration for all permutations"""
        config = {
            "service_name": "dslmodel_360",
            "spans": {},
            "metrics": {}
        }
        
        for perm in self.permutations:
            span_name = f"dslmodel.permutation.{perm.name}"
            config["spans"][span_name] = {
                "attributes": perm.attributes,
                "description": f"Permutation: {perm.model_type} with {perm.mixin_combo} from {perm.generation_source}"
            }
            
            # Add metric for each permutation
            metric_name = f"dslmodel.permutation.{perm.name}.count"
            config["metrics"][metric_name] = {
                "type": "counter",
                "unit": "1",
                "description": f"Count of {perm.name} permutation usage"
            }
        
        return config

def main():
    """Generate all DSLModel 360 permutations"""
    generator = DSLModel360Generator()
    
    # Generate permutations
    permutations = generator.generate_permutations()
    print(f"Generated {len(permutations)} permutations")
    
    # Create output directory
    output_dir = Path("output/dslmodel_360")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate semantic conventions
    semconv = generator.generate_semantic_conventions()
    with open(output_dir / "semantic_conventions.yaml", "w") as f:
        import yaml
        yaml.dump(semconv, f, default_flow_style=False)
    print(f"✅ Generated semantic conventions: {output_dir}/semantic_conventions.yaml")
    
    # Generate Python models
    python_code = generator.generate_python_models()
    with open(output_dir / "dslmodel_360_models.py", "w") as f:
        f.write(python_code)
    print(f"✅ Generated Python models: {output_dir}/dslmodel_360_models.py")
    
    # Generate telemetry config
    telemetry_config = generator.generate_telemetry_config()
    with open(output_dir / "telemetry_config.json", "w") as f:
        json.dump(telemetry_config, f, indent=2)
    print(f"✅ Generated telemetry config: {output_dir}/telemetry_config.json")
    
    # Generate summary
    summary = {
        "total_permutations": len(permutations),
        "model_types": generator.MODEL_TYPES,
        "mixin_combinations": generator.MIXIN_COMBINATIONS,
        "generation_sources": generator.GENERATION_SOURCES,
        "permutations": [p.name for p in permutations[:10]] + ["..."],
        "matrix": f"{len(generator.MODEL_TYPES)} x {len(generator.MIXIN_COMBINATIONS)} x {len(generator.GENERATION_SOURCES)} = {len(permutations)}"
    }
    
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Generated summary: {output_dir}/summary.json")
    
    print(f"\n🎯 Successfully generated {len(permutations)} DSLModel permutations!")
    print(f"📁 Output directory: {output_dir}")

if __name__ == "__main__":
    main()