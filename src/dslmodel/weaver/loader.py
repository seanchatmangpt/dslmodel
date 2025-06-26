"""Loader for Python-based semantic convention definitions."""

import importlib
import importlib.util
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from .models import ConventionSet


class PythonConventionLoader:
    """Loads semantic conventions from Python modules."""
    
    def __init__(self, modules: Optional[List[str]] = None):
        """Initialize with list of module names to load."""
        self.modules = modules or []
        
    def load_module(self, module_name: str) -> List[ConventionSet]:
        """Load convention sets from a Python module."""
        try:
            # Try to import as a regular module first
            module = importlib.import_module(module_name)
        except ImportError:
            # If that fails, try to load from file path
            module_path = Path(module_name)
            if module_path.suffix != '.py':
                module_path = module_path.with_suffix('.py')
                
            if not module_path.exists():
                # Check in authoring directory
                module_path = Path('authoring') / module_path
                
            if not module_path.exists():
                raise ImportError(f"Cannot find module {module_name}")
                
            # Load module from file
            spec = importlib.util.spec_from_file_location(
                module_name.replace('.py', ''),
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
        # Get convention sets from module
        if hasattr(module, 'get_convention_sets'):
            convention_sets = module.get_convention_sets()
            logger.info(f"Loaded {len(convention_sets)} convention sets from {module_name}")
            return convention_sets
        else:
            raise AttributeError(f"Module {module_name} does not have get_convention_sets() function")
            
    def load_all(self) -> Dict[str, List[ConventionSet]]:
        """Load all configured modules."""
        results = {}
        for module_name in self.modules:
            try:
                results[module_name] = self.load_module(module_name)
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {e}")
                
        return results
        
    def convert_to_yaml(self, convention_sets: List[ConventionSet], output_path: Path):
        """Convert convention sets to YAML format for Weaver."""
        all_groups = []
        
        for convention_set in convention_sets:
            groups = convention_set.to_yaml_groups()
            all_groups.extend(groups)
            
        yaml_content = {
            "groups": all_groups
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
            
        logger.info(f"Generated YAML convention file at {output_path}")
        
    def generate_yaml_from_modules(self, output_dir: Path):
        """Generate YAML files from all loaded modules."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        all_results = self.load_all()
        
        for module_name, convention_sets in all_results.items():
            # Create output filename from module name
            base_name = Path(module_name).stem
            output_file = output_dir / f"{base_name}.yaml"
            
            self.convert_to_yaml(convention_sets, output_file)