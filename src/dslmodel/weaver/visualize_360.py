#!/usr/bin/env python3
"""
Visualize DSLModel 360 Permutations
Creates a comprehensive view of all permutation dimensions
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def load_permutations(file_path: Path) -> List[Dict[str, Any]]:
    """Load permutations from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_matrix_view(permutations: List[Dict[str, Any]]):
    """Create a matrix view of permutations"""
    print("\n🎯 DSLModel 360 Permutation Matrix")
    print("="*80)
    
    # Create 3D matrix: model_type x mixin x source
    matrix = defaultdict(lambda: defaultdict(set))
    
    for perm in permutations:
        model_type = perm['model_type']
        mixin = perm['mixin_combination']
        source = perm['generation_source']
        matrix[model_type][mixin].add(source)
    
    # Print matrix
    model_types = sorted(matrix.keys())
    all_mixins = sorted(set(mixin for mt in matrix.values() for mixin in mt.keys()))
    
    print(f"\n{'Model Type':<12}", end='')
    for mixin in all_mixins:
        print(f"{mixin:<15}", end='')
    print()
    print("-" * (12 + 15 * len(all_mixins)))
    
    for model_type in model_types:
        print(f"{model_type:<12}", end='')
        for mixin in all_mixins:
            sources = matrix[model_type].get(mixin, set())
            print(f"{len(sources):<15}", end='')
        print()

def create_dimension_summary(permutations: List[Dict[str, Any]]):
    """Create summary by each dimension"""
    print("\n📊 Dimension Summary")
    print("="*80)
    
    dimensions = ['model_type', 'mixin_combination', 'generation_source', 
                  'output_format', 'template_engine']
    
    for dim in dimensions:
        counts = defaultdict(int)
        for perm in permutations:
            counts[perm.get(dim, 'unknown')] += 1
        
        print(f"\n{dim.replace('_', ' ').title()}:")
        for value, count in sorted(counts.items(), key=lambda x: -x[1]):
            bar = '█' * (count // 5)
            print(f"  {value:<20} {count:>3} {bar}")

def create_coverage_report(permutations: List[Dict[str, Any]]):
    """Create coverage report for all combinations"""
    print("\n✅ Coverage Report")
    print("="*80)
    
    # Expected combinations
    expected_model_types = 6
    expected_mixins = 10
    expected_sources = 6
    expected_core = expected_model_types * expected_mixins * expected_sources
    
    print(f"Expected core permutations: {expected_core}")
    print(f"Actual permutations: {len(permutations)}")
    print(f"Coverage: {len(permutations)/expected_core*100:.1f}%")
    
    # Find missing combinations
    seen = set()
    for perm in permutations:
        key = (perm['model_type'], perm['mixin_combination'], perm['generation_source'])
        seen.add(key)
    
    # All possible combinations
    model_types = ['base', 'fsm', 'workflow', 'agent', 'event', 'template']
    mixins = ['none', 'jinja', 'tool', 'file', 'jinja_tool', 
              'jinja_file', 'tool_file', 'all', 'fsm_jinja', 'fsm_tool']
    sources = ['prompt', 'schema', 'api', 'template', 'weaver', 'manual']
    
    missing = []
    for mt in model_types:
        for mx in mixins:
            for src in sources:
                if (mt, mx, src) not in seen:
                    # Check if it's a valid exclusion
                    if mx in ['fsm_jinja', 'fsm_tool'] and mt != 'fsm':
                        continue  # Expected exclusion
                    missing.append((mt, mx, src))
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} combinations:")
        for mt, mx, src in missing[:5]:
            print(f"  - {mt} + {mx} + {src}")
        if len(missing) > 5:
            print(f"  ... and {len(missing)-5} more")
    else:
        print("\n✅ All valid combinations covered!")

def create_semantic_span_examples(permutations: List[Dict[str, Any]]):
    """Create example OpenTelemetry spans"""
    print("\n🔍 Sample OpenTelemetry Spans")
    print("="*80)
    
    # Take diverse samples
    samples = [
        permutations[0],    # First
        permutations[59],   # End of basic models
        permutations[149],  # Middle of single mixin
        permutations[299],  # Multi mixin
        permutations[359]   # Last
    ]
    
    for i, perm in enumerate(samples):
        print(f"\nSpan {i+1}:")
        print(f"  Name: dslmodel.generate.{perm['model_type']}")
        print(f"  Attributes:")
        print(f"    dslmodel.model.type: {perm['model_type']}")
        print(f"    dslmodel.mixin.combination: {perm['mixin_combination']}")
        print(f"    dslmodel.generation.source: {perm['generation_source']}")
        print(f"    dslmodel.validation.enabled: {perm['validation_enabled']}")
        print(f"    dslmodel.output.format: {perm['output_format']}")

def main():
    """Visualize the 360 permutations"""
    # Load permutations
    perm_file = Path("output/dslmodel_360/dslmodel_360_permutations.json")
    
    if not perm_file.exists():
        print("❌ Permutation file not found. Run dslmodel_permutations.py first.")
        return
    
    permutations = load_permutations(perm_file)
    
    print(f"🎨 Visualizing {len(permutations)} DSLModel Permutations")
    
    # Create different views
    create_matrix_view(permutations)
    create_dimension_summary(permutations)
    create_coverage_report(permutations)
    create_semantic_span_examples(permutations)
    
    # Create Weaver command examples
    print("\n🔧 Weaver Forge Commands")
    print("="*80)
    print("# Generate models from semantic conventions:")
    print("weaver registry generate \\")
    print("  --registry-path semconv_registry \\")
    print("  --templates weaver_templates \\")
    print("  --output output/generated_models \\")
    print("  python")
    
    print("\n# Validate semantic conventions:")
    print("weaver registry check \\")
    print("  --registry-path semconv_registry/dslmodel_360.yaml")
    
    print("\n# Generate specific permutation:")
    print("dsl forge build \\")
    print("  --model-type fsm \\")
    print("  --mixin fsm_jinja \\")
    print("  --source weaver \\")
    print("  --output output/fsm_models")

if __name__ == "__main__":
    main()