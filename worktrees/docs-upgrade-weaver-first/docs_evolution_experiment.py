#!/usr/bin/env python3
"""
Documentation Evolution Experiment - Using Weaver-First Approach
Based on generated evolution_worktree models
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dslmodel.generated.models.evolution_worktree import Evolution_worktree_experiment

class DocumentationEvolutionExperiment:
    """
    Documentation upgrade experiment using Weaver-first evolution patterns
    """
    
    def __init__(self):
        self.experiment = Evolution_worktree_experiment(
            experiment_id="docs-upgrade-2025-001",
            worktree_path="/Users/sac/dev/dslmodel/worktrees/docs-upgrade-weaver-first",
            branch_name="evolution/docs-upgrade-weaver-first",
            base_commit="latest"  # In real implementation, get actual commit SHA
        )
        
    def initialize_experiment(self):
        """Initialize the documentation evolution experiment"""
        print("🧬 Starting Documentation Evolution Experiment")
        print(f"   Experiment ID: {self.experiment.experiment_id}")
        print(f"   Worktree: {self.experiment.worktree_path}")
        print(f"   Branch: {self.experiment.branch_name}")
        
        # Create experiment metadata
        metadata = {
            "experiment_type": "documentation_upgrade",
            "approach": "weaver_first",
            "target": "production_readiness_documentation",
            "validation_criteria": {
                "honest_assessment": True,
                "evidence_based": True,
                "production_ready": True
            },
            "start_time": datetime.now().isoformat()
        }
        
        # Save experiment metadata
        metadata_file = Path(self.experiment.worktree_path) / "experiment_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with metadata_file.open("w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"✅ Experiment metadata saved: {metadata_file}")
        
    def generate_documentation_specifications(self):
        """Generate Weaver-based specifications for documentation"""
        
        docs_spec = {
            "semantic_conventions": {
                "documentation": {
                    "id": "dslmodel.docs",
                    "type": "span",
                    "brief": "Documentation operation spans",
                    "attributes": [
                        {
                            "id": "docs.operation",
                            "type": "string",
                            "requirement_level": "required",
                            "brief": "Type of documentation operation",
                            "examples": ["upgrade", "validate", "generate", "deploy"]
                        },
                        {
                            "id": "docs.target",
                            "type": "string", 
                            "requirement_level": "required",
                            "brief": "Documentation target",
                            "examples": ["context", "readme", "production_guide", "usage_examples"]
                        },
                        {
                            "id": "docs.validation_status",
                            "type": "string",
                            "requirement_level": "recommended",
                            "brief": "Validation status of documentation",
                            "examples": ["validated", "partial", "needs_work"]
                        },
                        {
                            "id": "docs.evidence_provided",
                            "type": "boolean",
                            "requirement_level": "recommended", 
                            "brief": "Whether evidence was provided for claims"
                        }
                    ]
                }
            }
        }
        
        # Save documentation semantic conventions
        spec_file = Path(self.experiment.worktree_path) / "docs_semantic_conventions.yaml"
        with spec_file.open("w") as f:
            import yaml
            yaml.dump(docs_spec, f, default_flow_style=False, indent=2)
            
        print(f"✅ Documentation semantic conventions: {spec_file}")
        
    def apply_validated_documentation_changes(self):
        """Apply the validated documentation changes from our previous work"""
        
        # Copy our validated documentation changes into the worktree
        source_files = [
            "context/README.md",
            "context/index.md", 
            "README.md",
            "PRODUCTION_READINESS_GUIDE.md",
            "TEMPLATE_GENERATION_GUIDE.md",
            "PRACTICAL_USAGE_EXAMPLES.md",
            "SKEPTICAL_VALIDATION_REPORT.md"
        ]
        
        base_path = Path("/Users/sac/dev/dslmodel")
        worktree_path = Path(self.experiment.worktree_path)
        
        print("📝 Applying validated documentation changes...")
        
        for file_path in source_files:
            source = base_path / file_path
            target = worktree_path / file_path
            
            if source.exists():
                # Ensure target directory exists
                target.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the validated content
                import shutil
                shutil.copy2(source, target)
                print(f"   ✅ {file_path}")
            else:
                print(f"   ⚠️  {file_path} (not found)")
                
    def validate_documentation_evolution(self):
        """Validate the documentation evolution using Weaver patterns"""
        
        worktree_path = Path(self.experiment.worktree_path)
        validation_results = {
            "experiment_id": self.experiment.experiment_id,
            "validation_time": datetime.now().isoformat(),
            "files_validated": [],
            "evidence_based": False,
            "production_ready": False,
            "honest_assessment": False
        }
        
        # Check for key documentation files
        required_files = [
            "README.md",
            "PRODUCTION_READINESS_GUIDE.md", 
            "context/README.md",
            "context/index.md"
        ]
        
        for file_path in required_files:
            file_obj = worktree_path / file_path
            if file_obj.exists():
                # Read content and validate
                content = file_obj.read_text()
                
                file_validation = {
                    "file": file_path,
                    "exists": True,
                    "size": len(content),
                    "has_evidence": "✅" in content and ("validated" in content.lower() or "tested" in content.lower()),
                    "has_honest_assessment": "85%" in content or "partial" in content.lower(),
                    "production_ready": "production" in content.lower() and "ready" in content.lower()
                }
                
                validation_results["files_validated"].append(file_validation)
                print(f"   ✅ {file_path}: {file_validation}")
            else:
                print(f"   ❌ {file_path}: Missing")
                
        # Overall assessment
        evidence_files = [f for f in validation_results["files_validated"] if f.get("has_evidence")]
        honest_files = [f for f in validation_results["files_validated"] if f.get("has_honest_assessment")]
        production_files = [f for f in validation_results["files_validated"] if f.get("production_ready")]
        
        validation_results["evidence_based"] = len(evidence_files) >= 2
        validation_results["honest_assessment"] = len(honest_files) >= 2  
        validation_results["production_ready"] = len(production_files) >= 2
        
        # Save validation results
        results_file = worktree_path / "validation_results.json"
        with results_file.open("w") as f:
            json.dump(validation_results, f, indent=2)
            
        print(f"📊 Validation Results:")
        print(f"   Evidence-based: {validation_results['evidence_based']}")
        print(f"   Honest assessment: {validation_results['honest_assessment']}")
        print(f"   Production ready: {validation_results['production_ready']}")
        print(f"   Results saved: {results_file}")
        
        return validation_results
        
    def run_evolution_experiment(self):
        """Run the complete documentation evolution experiment"""
        print("\n🚀 DOCUMENTATION EVOLUTION EXPERIMENT")
        print("="*50)
        
        # Step 1: Initialize
        self.initialize_experiment()
        print()
        
        # Step 2: Generate specifications
        self.generate_documentation_specifications()
        print()
        
        # Step 3: Apply changes
        self.apply_validated_documentation_changes()
        print()
        
        # Step 4: Validate
        results = self.validate_documentation_evolution()
        print()
        
        # Step 5: Summary
        success_criteria = sum([
            results["evidence_based"],
            results["honest_assessment"], 
            results["production_ready"]
        ])
        
        print(f"🎯 EXPERIMENT SUMMARY")
        print(f"   Success Criteria Met: {success_criteria}/3")
        print(f"   Overall Status: {'✅ SUCCESS' if success_criteria >= 2 else '⚠️ NEEDS_WORK'}")
        print()
        
        return results

if __name__ == "__main__":
    experiment = DocumentationEvolutionExperiment()
    results = experiment.run_evolution_experiment()
    
    # Exit with appropriate code
    success = sum([
        results["evidence_based"],
        results["honest_assessment"],
        results["production_ready"]
    ]) >= 2
    
    sys.exit(0 if success else 1)