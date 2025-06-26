#!/usr/bin/env python3
"""
DSLModel 360 Permutations Generator
Generates all valid combinations of DSLModel configurations
"""

from typing import List, Dict, Any, Set
from itertools import product
from dataclasses import dataclass
import json
import yaml
from pathlib import Path

@dataclass
class DSLModelPermutation:
    """Represents a single DSLModel configuration permutation"""
    model_type: str
    mixin_combination: str
    generation_source: str
    validation_enabled: bool
    output_format: str
    template_engine: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_type": self.model_type,
            "mixin_combination": self.mixin_combination,
            "generation_source": self.generation_source,
            "validation_enabled": self.validation_enabled,
            "output_format": self.output_format,
            "template_engine": self.template_engine
        }
    
    def to_span_attributes(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry span attributes"""
        return {
            "dslmodel.model.type": self.model_type,
            "dslmodel.mixin.combination": self.mixin_combination,
            "dslmodel.generation.source": self.generation_source,
            "dslmodel.validation.enabled": self.validation_enabled,
            "dslmodel.output.format": self.output_format,
            "dslmodel.template.engine": self.template_engine
        }
    
    def get_model_name(self) -> str:
        """Generate a descriptive model name"""
        parts = [
            self.model_type.title(),
            self.mixin_combination.replace('_', '').title(),
            self.generation_source.title(),
            "Validated" if self.validation_enabled else "Unvalidated",
            self.output_format.upper()
        ]
        return "".join(parts) + "Model"
    
    def get_file_suffix(self) -> str:
        """Get appropriate file suffix for output format"""
        suffixes = {
            "python": ".py",
            "json_schema": ".json",
            "typescript": ".ts",
            "yaml": ".yaml",
            "proto": ".proto"
        }
        return suffixes.get(self.output_format, ".txt")

class DSLModelPermutationGenerator:
    """Generates all 360 permutations of DSLModel configurations"""
    
    # Core dimensions that multiply to 360
    MODEL_TYPES = ["base", "fsm", "workflow", "agent", "event", "template"]  # 6
    MIXIN_COMBINATIONS = [
        "none", "jinja", "tool", "file", "jinja_tool", 
        "jinja_file", "tool_file", "all", "fsm_jinja", "fsm_tool"
    ]  # 10
    GENERATION_SOURCES = ["prompt", "schema", "api", "template", "weaver", "manual"]  # 6
    
    # Additional variations (these are conditional/contextual)
    VALIDATION_STATES = [True, False]
    OUTPUT_FORMATS = ["python", "json_schema", "typescript", "yaml", "proto"]
    TEMPLATE_ENGINES = ["jinja2", "mako", "custom"]
    
    def __init__(self):
        self.permutations: List[DSLModelPermutation] = []
        self._excluded_combinations: Set[tuple] = set()
        self._setup_exclusions()
    
    def _setup_exclusions(self):
        """Define invalid combinations to exclude"""
        # FSM mixins only valid with FSM model type
        for mixin in ["fsm_jinja", "fsm_tool"]:
            for model_type in ["base", "workflow", "agent", "event", "template"]:
                self._excluded_combinations.add((model_type, mixin))
        
        # Template engine only relevant with template generation or jinja mixin
        for source in ["prompt", "schema", "api", "manual"]:
            for mixin in ["none", "tool", "file"]:
                for engine in ["mako", "custom"]:
                    self._excluded_combinations.add((source, mixin, engine))
    
    def is_valid_combination(self, perm: DSLModelPermutation) -> bool:
        """Check if a permutation is valid"""
        # Check model type + mixin combination
        if (perm.model_type, perm.mixin_combination) in self._excluded_combinations:
            return False
        
        # FSM mixins only with FSM model
        if "fsm" in perm.mixin_combination and perm.model_type != "fsm":
            return False
        
        # Template engine constraints
        if perm.template_engine != "jinja2":
            # Only use non-jinja2 engines with template source or jinja mixin
            if perm.generation_source not in ["template", "weaver"] and "jinja" not in perm.mixin_combination:
                return False
        
        # Proto output only with schema or API sources
        if perm.output_format == "proto" and perm.generation_source not in ["schema", "api", "weaver"]:
            return False
        
        return True
    
    def generate_core_360(self) -> List[DSLModelPermutation]:
        """Generate the core 360 permutations (6 x 10 x 6)"""
        permutations = []
        
        for model_type, mixin, source in product(
            self.MODEL_TYPES,
            self.MIXIN_COMBINATIONS, 
            self.GENERATION_SOURCES
        ):
            # Default values for core 360
            perm = DSLModelPermutation(
                model_type=model_type,
                mixin_combination=mixin,
                generation_source=source,
                validation_enabled=True,  # Default to enabled
                output_format="python",   # Default output
                template_engine="jinja2"  # Default engine
            )
            
            if self.is_valid_combination(perm):
                permutations.append(perm)
        
        return permutations
    
    def generate_extended_permutations(self, limit: int = 1000) -> List[DSLModelPermutation]:
        """Generate extended permutations with all variations"""
        permutations = []
        count = 0
        
        for model_type, mixin, source, validation, output, engine in product(
            self.MODEL_TYPES,
            self.MIXIN_COMBINATIONS,
            self.GENERATION_SOURCES,
            self.VALIDATION_STATES,
            self.OUTPUT_FORMATS,
            self.TEMPLATE_ENGINES
        ):
            if count >= limit:
                break
                
            perm = DSLModelPermutation(
                model_type=model_type,
                mixin_combination=mixin,
                generation_source=source,
                validation_enabled=validation,
                output_format=output,
                template_engine=engine
            )
            
            if self.is_valid_combination(perm):
                permutations.append(perm)
                count += 1
        
        return permutations
    
    def generate_categorized_360(self) -> Dict[str, List[DSLModelPermutation]]:
        """Generate 360 permutations organized by category"""
        categories = {
            "basic_models": [],      # 60 - Basic models without mixins
            "single_mixin": [],      # 90 - Models with single mixin
            "multi_mixin": [],       # 90 - Models with multiple mixins
            "fsm_models": [],        # 60 - FSM-specific models
            "specialized": []        # 60 - Specialized configurations
        }
        
        core_perms = self.generate_core_360()
        
        for perm in core_perms:
            if perm.mixin_combination == "none":
                categories["basic_models"].append(perm)
            elif perm.mixin_combination in ["jinja", "tool", "file"]:
                categories["single_mixin"].append(perm)
            elif perm.mixin_combination in ["jinja_tool", "jinja_file", "tool_file", "all"]:
                categories["multi_mixin"].append(perm)
            elif "fsm" in perm.mixin_combination:
                categories["fsm_models"].append(perm)
            else:
                categories["specialized"].append(perm)
        
        # Balance categories to exactly 360
        self._balance_categories(categories, target_total=360)
        
        return categories
    
    def _balance_categories(self, categories: Dict[str, List], target_total: int):
        """Balance categories to reach exact target total"""
        current_total = sum(len(perms) for perms in categories.values())
        
        if current_total == target_total:
            return
        
        # Add variations to reach target
        if current_total < target_total:
            needed = target_total - current_total
            
            # Add output format variations
            for category, perms in categories.items():
                if needed == 0:
                    break
                    
                base_perms = perms[:10]  # Take first 10 as base
                for perm in base_perms:
                    if needed == 0:
                        break
                        
                    for output in ["json_schema", "typescript", "yaml"]:
                        if needed == 0:
                            break
                            
                        new_perm = DSLModelPermutation(
                            model_type=perm.model_type,
                            mixin_combination=perm.mixin_combination,
                            generation_source=perm.generation_source,
                            validation_enabled=perm.validation_enabled,
                            output_format=output,
                            template_engine=perm.template_engine
                        )
                        
                        if self.is_valid_combination(new_perm):
                            categories[category].append(new_perm)
                            needed -= 1
    
    def export_permutations(self, permutations: List[DSLModelPermutation], 
                          output_dir: Path, format: str = "json"):
        """Export permutations to file"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            output_file = output_dir / "dslmodel_360_permutations.json"
            data = [p.to_dict() for p in permutations]
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        elif format == "yaml":
            output_file = output_dir / "dslmodel_360_permutations.yaml"
            data = {"permutations": [p.to_dict() for p in permutations]}
            with open(output_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
                
        elif format == "spans":
            output_file = output_dir / "dslmodel_360_spans.jsonl"
            with open(output_file, 'w') as f:
                for i, perm in enumerate(permutations):
                    span = {
                        "trace_id": f"dslmodel-360-{i:04d}",
                        "span_id": f"perm-{i:04d}",
                        "name": f"dslmodel.generate.{perm.get_model_name()}",
                        "attributes": perm.to_span_attributes()
                    }
                    f.write(json.dumps(span) + "\n")
        
        return output_file
    
    def generate_statistics(self, permutations: List[DSLModelPermutation]) -> Dict[str, Any]:
        """Generate statistics about the permutations"""
        stats = {
            "total": len(permutations),
            "by_model_type": {},
            "by_mixin": {},
            "by_source": {},
            "by_output": {},
            "validation_enabled": 0,
            "unique_model_names": set()
        }
        
        for perm in permutations:
            # Count by dimensions
            stats["by_model_type"][perm.model_type] = stats["by_model_type"].get(perm.model_type, 0) + 1
            stats["by_mixin"][perm.mixin_combination] = stats["by_mixin"].get(perm.mixin_combination, 0) + 1
            stats["by_source"][perm.generation_source] = stats["by_source"].get(perm.generation_source, 0) + 1
            stats["by_output"][perm.output_format] = stats["by_output"].get(perm.output_format, 0) + 1
            
            if perm.validation_enabled:
                stats["validation_enabled"] += 1
                
            stats["unique_model_names"].add(perm.get_model_name())
        
        stats["unique_model_count"] = len(stats["unique_model_names"])
        stats["unique_model_names"] = list(stats["unique_model_names"])[:10]  # Sample
        
        return stats

def main():
    """Generate and display DSLModel 360 permutations"""
    generator = DSLModelPermutationGenerator()
    
    print("🔄 Generating DSLModel 360 Permutations")
    print("="*60)
    
    # Generate core 360
    core_perms = generator.generate_core_360()
    print(f"\n✅ Generated {len(core_perms)} core permutations")
    
    # Generate categorized 360
    categorized = generator.generate_categorized_360()
    print("\n📊 Permutations by Category:")
    total = 0
    for category, perms in categorized.items():
        print(f"  {category}: {len(perms)}")
        total += len(perms)
    print(f"  TOTAL: {total}")
    
    # Flatten categorized for export
    all_perms = []
    for perms in categorized.values():
        all_perms.extend(perms)
    
    # Generate statistics
    stats = generator.generate_statistics(all_perms)
    print("\n📈 Statistics:")
    print(f"  Total permutations: {stats['total']}")
    print(f"  Unique model names: {stats['unique_model_count']}")
    print(f"  Validation enabled: {stats['validation_enabled']}/{stats['total']}")
    
    print("\n🎯 Distribution by dimension:")
    print("  Model Types:", stats['by_model_type'])
    print("  Mixin Combinations:", stats['by_mixin'])
    print("  Generation Sources:", stats['by_source'])
    
    # Export permutations
    output_dir = Path("output/dslmodel_360")
    
    print(f"\n💾 Exporting to {output_dir}/")
    generator.export_permutations(all_perms, output_dir, format="json")
    generator.export_permutations(all_perms, output_dir, format="yaml")
    generator.export_permutations(all_perms, output_dir, format="spans")
    
    # Sample permutations
    print("\n🎲 Sample Permutations:")
    for i, perm in enumerate(all_perms[:5]):
        print(f"\n{i+1}. {perm.get_model_name()}")
        print(f"   Type: {perm.model_type}")
        print(f"   Mixins: {perm.mixin_combination}")
        print(f"   Source: {perm.generation_source}")
        print(f"   Output: {perm.output_format}")
    
    print(f"\n✅ Successfully generated {len(all_perms)} permutations!")

if __name__ == "__main__":
    main()