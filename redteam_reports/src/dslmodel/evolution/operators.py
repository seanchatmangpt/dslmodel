"""
Evolution Operators for Genetic Algorithm Components
Mutation and crossover operators for autonomous evolution
"""

import ast
import random
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from dslmodel import DSLModel
from pydantic import Field

from .core import EvolutionStrategy, EvolutionCandidate

class MutationOperator:
    """Handles mutation operations on evolution candidates"""
    
    def __init__(self):
        self.name = "MutationOperator"
        
    async def mutate(self, parent: EvolutionCandidate, strategy: EvolutionStrategy, generation: int) -> Optional[EvolutionCandidate]:
        """Apply mutation to create offspring candidate"""
        
        mutation_types = [
            self._code_optimization_mutation,
            self._structure_mutation,
            self._import_mutation,
            self._parameter_mutation
        ]
        
        # Select random mutation type
        mutation_func = random.choice(mutation_types)
        
        try:
            # Apply mutation
            mutated_changes = {}
            mutated_files = {}
            mutations_applied = []
            
            # Mutate existing code changes
            for file_path, content in parent.code_changes.items():
                mutated_content, mutation_description = await mutation_func(content, strategy)
                mutated_changes[file_path] = mutated_content
                mutations_applied.append(f"{mutation_description} in {file_path}")
            
            # Sometimes add new files through mutation
            if random.random() < 0.3 and strategy in [EvolutionStrategy.FEATURE_ENHANCEMENT, EvolutionStrategy.TEST_COVERAGE_EXPANSION]:
                new_file_content, mutation_description = await self._generate_new_file_mutation(strategy)
                new_file_path = f"evolved_{generation}_{random.randint(1000, 9999)}.py"
                mutated_files[new_file_path] = new_file_content
                mutations_applied.append(f"Generated {new_file_path}: {mutation_description}")
            
            offspring = EvolutionCandidate(
                generation=generation,
                strategy=strategy,
                parent_ids=[parent.candidate_id],
                code_changes=mutated_changes,
                new_files=mutated_files,
                description=f"Mutated {parent.description}",
                implementation_notes=parent.implementation_notes + [f"Applied mutations: {', '.join(mutations_applied)}"],
                mutation_applied=mutations_applied,
                estimated_impact=parent.estimated_impact,
                risk_level=parent.risk_level
            )
            
            return offspring
            
        except Exception as e:
            # Return simple mutation as fallback
            return EvolutionCandidate(
                generation=generation,
                strategy=strategy,
                parent_ids=[parent.candidate_id],
                description=f"Simple mutation of {parent.description}",
                implementation_notes=[f"Mutation failed, applied simple change: {str(e)}"],
                mutation_applied=["simple_mutation"],
                estimated_impact="low",
                risk_level="low"
            )
    
    async def _code_optimization_mutation(self, content: str, strategy: EvolutionStrategy) -> Tuple[str, str]:
        """Apply code optimization mutations"""
        lines = content.splitlines()
        mutated_lines = []
        
        for line in lines:
            mutated_line = line
            
            # Optimize loops
            if "for i in range(len(" in line and random.random() < 0.5:
                mutated_line = line.replace("for i in range(len(", "for i, item in enumerate(")
                mutated_line = mutated_line.replace(")):", "):")
            
            # Optimize string concatenation
            elif "+=" in line and "str" in line.lower() and random.random() < 0.3:
                mutated_line = line + "  # TODO: Consider using join() for better performance"
            
            # Add type hints
            elif "def " in line and ":" in line and "->" not in line and random.random() < 0.2:
                if line.strip().endswith(":"):
                    mutated_line = line.replace(":", " -> Any:")
            
            mutated_lines.append(mutated_line)
        
        return "\n".join(mutated_lines), "code optimization mutations"
    
    async def _structure_mutation(self, content: str, strategy: EvolutionStrategy) -> Tuple[str, str]:
        """Apply structural mutations"""
        lines = content.splitlines()
        
        # Add docstrings where missing
        if random.random() < 0.4:
            mutated_lines = []
            for i, line in enumerate(lines):
                mutated_lines.append(line)
                
                # Add docstring after function definition
                if line.strip().startswith("def ") and ":" in line:
                    # Check if next line is not already a docstring
                    if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                        indent = len(line) - len(line.lstrip())
                        docstring = ' ' * (indent + 4) + '"""Generated docstring for enhanced documentation."""'
                        mutated_lines.append(docstring)
            
            return "\n".join(mutated_lines), "structure improvements"
        
        return content, "no structural changes"
    
    async def _import_mutation(self, content: str, strategy: EvolutionStrategy) -> Tuple[str, str]:
        """Apply import optimization mutations"""
        lines = content.splitlines()
        mutated_lines = []
        
        for line in lines:
            mutated_line = line
            
            # Optimize imports
            if line.strip().startswith("import ") and "," not in line and random.random() < 0.2:
                # Sometimes suggest specific imports
                if "os" in line:
                    mutated_line = line + "\n# Consider: from os.path import join, exists for specific usage"
                elif "json" in line:
                    mutated_line = line + "\n# Consider: from json import loads, dumps for specific usage"
            
            mutated_lines.append(mutated_line)
        
        return "\n".join(mutated_lines), "import optimizations"
    
    async def _parameter_mutation(self, content: str, strategy: EvolutionStrategy) -> Tuple[str, str]:
        """Apply parameter and configuration mutations"""
        # Simple parameter tweaking for numeric values
        mutated_content = content
        
        # Randomly adjust numeric constants
        import re
        numeric_pattern = r'\b(\d+\.?\d*)\b'
        
        def mutate_number(match):
            if random.random() < 0.1:  # 10% chance to mutate
                num = float(match.group(1))
                # Small random adjustment
                adjustment = random.uniform(0.9, 1.1)
                new_num = num * adjustment
                return str(int(new_num) if new_num.is_integer() else round(new_num, 2))
            return match.group(1)
        
        mutated_content = re.sub(numeric_pattern, mutate_number, content)
        
        return mutated_content, "parameter adjustments"
    
    async def _generate_new_file_mutation(self, strategy: EvolutionStrategy) -> Tuple[str, str]:
        """Generate new file through mutation"""
        
        if strategy == EvolutionStrategy.TEST_COVERAGE_EXPANSION:
            content = '''"""
Generated test file for improved coverage.
"""

import unittest
from unittest.mock import Mock, patch

class TestEvolved(unittest.TestCase):
    """Generated test class for enhanced coverage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_object = Mock()
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Generated test case
        self.assertTrue(True)
        self.mock_object.method.return_value = "test"
        result = self.mock_object.method()
        self.assertEqual(result, "test")
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Generated edge case testing
        self.assertIsNotNone(self.mock_object)
        with self.assertRaises(AttributeError):
            self.mock_object.nonexistent_method()

if __name__ == '__main__':
    unittest.main()
'''
            return content, "test coverage expansion"
        
        elif strategy == EvolutionStrategy.FEATURE_ENHANCEMENT:
            content = '''"""
Generated utility module for feature enhancement.
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EvolutionUtility:
    """Generated utility class for enhanced functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize utility with optional configuration."""
        self.config = config or {}
        self.cache = {}
    
    def process_data(self, data: Any) -> Any:
        """Process data with caching for performance."""
        data_hash = hash(str(data))
        
        if data_hash in self.cache:
            logger.debug("Cache hit for data processing")
            return self.cache[data_hash]
        
        # Simple processing logic
        result = self._transform_data(data)
        self.cache[data_hash] = result
        return result
    
    def _transform_data(self, data: Any) -> Any:
        """Transform data according to configuration."""
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [item for item in data if item is not None]
        return data
    
    def clear_cache(self):
        """Clear internal cache."""
        self.cache.clear()
        logger.info("Cache cleared")
'''
            return content, "feature enhancement utility"
        
        else:
            content = '''"""
Generated helper module for code improvement.
"""

import time
from functools import wraps
from typing import Callable, Any

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        if execution_time > 1.0:  # Log slow functions
            print(f"Performance warning: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper

def safe_execute(func: Callable, default: Any = None) -> Any:
    """Safely execute function with fallback."""
    try:
        return func()
    except Exception as e:
        print(f"Error in {func.__name__}: {e}")
        return default
'''
            return content, "helper utilities"

class CrossoverOperator:
    """Handles crossover operations between evolution candidates"""
    
    def __init__(self):
        self.name = "CrossoverOperator"
    
    async def crossover(self, parent1: EvolutionCandidate, parent2: EvolutionCandidate, strategy: EvolutionStrategy, generation: int) -> Optional[EvolutionCandidate]:
        """Apply crossover to create offspring from two parents"""
        
        try:
            # Combine code changes from both parents
            combined_changes = {}
            
            # Strategy 1: Merge non-conflicting files
            all_files = set(parent1.code_changes.keys()) | set(parent2.code_changes.keys())
            
            for file_path in all_files:
                if file_path in parent1.code_changes and file_path in parent2.code_changes:
                    # Both parents modified this file - create hybrid
                    content1 = parent1.code_changes[file_path]
                    content2 = parent2.code_changes[file_path]
                    hybrid_content = await self._merge_file_contents(content1, content2, strategy)
                    combined_changes[file_path] = hybrid_content
                
                elif file_path in parent1.code_changes:
                    # Only parent1 has this change
                    if random.random() < 0.7:  # 70% chance to inherit
                        combined_changes[file_path] = parent1.code_changes[file_path]
                
                elif file_path in parent2.code_changes:
                    # Only parent2 has this change
                    if random.random() < 0.7:  # 70% chance to inherit
                        combined_changes[file_path] = parent2.code_changes[file_path]
            
            # Combine new files
            combined_new_files = {}
            
            # Inherit new files from both parents with some probability
            for file_path, content in parent1.new_files.items():
                if random.random() < 0.5:
                    combined_new_files[file_path] = content
            
            for file_path, content in parent2.new_files.items():
                if file_path not in combined_new_files and random.random() < 0.5:
                    combined_new_files[file_path] = content
            
            # Create crossover description
            description = f"Crossover: {parent1.description} × {parent2.description}"
            
            # Combine implementation notes
            combined_notes = (
                parent1.implementation_notes + 
                parent2.implementation_notes + 
                [f"Crossover between {parent1.candidate_id} and {parent2.candidate_id}"]
            )
            
            offspring = EvolutionCandidate(
                generation=generation,
                strategy=strategy,
                parent_ids=[parent1.candidate_id, parent2.candidate_id],
                code_changes=combined_changes,
                new_files=combined_new_files,
                description=description,
                implementation_notes=combined_notes,
                crossover_source=f"{parent1.candidate_id}+{parent2.candidate_id}",
                estimated_impact=self._combine_impact_levels(parent1.estimated_impact, parent2.estimated_impact),
                risk_level=self._combine_risk_levels(parent1.risk_level, parent2.risk_level)
            )
            
            return offspring
            
        except Exception as e:
            # Fallback simple crossover
            return EvolutionCandidate(
                generation=generation,
                strategy=strategy,
                parent_ids=[parent1.candidate_id, parent2.candidate_id],
                description=f"Simple crossover: {parent1.description} × {parent2.description}",
                implementation_notes=[f"Crossover failed, using simple combination: {str(e)}"],
                crossover_source=f"{parent1.candidate_id}+{parent2.candidate_id}",
                estimated_impact="medium",
                risk_level="medium"
            )
    
    async def _merge_file_contents(self, content1: str, content2: str, strategy: EvolutionStrategy) -> str:
        """Merge contents of two files intelligently"""
        
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        # Simple line-by-line merge strategy
        merged_lines = []
        max_lines = max(len(lines1), len(lines2))
        
        for i in range(max_lines):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""
            
            if line1 == line2:
                # Identical lines - use either
                merged_lines.append(line1)
            elif not line1:
                # Only line2 exists
                merged_lines.append(line2)
            elif not line2:
                # Only line1 exists
                merged_lines.append(line1)
            else:
                # Different lines - choose based on strategy
                if strategy == EvolutionStrategy.SECURITY_HARDENING:
                    # Prefer more defensive code
                    if any(keyword in line1.lower() for keyword in ['validate', 'check', 'security', 'safe']):
                        merged_lines.append(line1)
                    elif any(keyword in line2.lower() for keyword in ['validate', 'check', 'security', 'safe']):
                        merged_lines.append(line2)
                    else:
                        merged_lines.append(line1 if random.random() < 0.5 else line2)
                
                elif strategy == EvolutionStrategy.PERFORMANCE_OPTIMIZATION:
                    # Prefer performance-oriented code
                    if any(keyword in line1.lower() for keyword in ['cache', 'optimize', 'fast', 'efficient']):
                        merged_lines.append(line1)
                    elif any(keyword in line2.lower() for keyword in ['cache', 'optimize', 'fast', 'efficient']):
                        merged_lines.append(line2)
                    else:
                        merged_lines.append(line1 if random.random() < 0.5 else line2)
                
                else:
                    # Random choice for other strategies
                    merged_lines.append(line1 if random.random() < 0.5 else line2)
        
        return "\n".join(merged_lines)
    
    def _combine_impact_levels(self, impact1: str, impact2: str) -> str:
        """Combine impact levels from two parents"""
        impact_order = {"low": 1, "medium": 2, "high": 3}
        
        level1 = impact_order.get(impact1, 2)
        level2 = impact_order.get(impact2, 2)
        
        # Take the higher impact level
        combined_level = max(level1, level2)
        
        for level_name, level_value in impact_order.items():
            if level_value == combined_level:
                return level_name
        
        return "medium"
    
    def _combine_risk_levels(self, risk1: str, risk2: str) -> str:
        """Combine risk levels from two parents"""
        risk_order = {"low": 1, "medium": 2, "high": 3}
        
        level1 = risk_order.get(risk1, 2)
        level2 = risk_order.get(risk2, 2)
        
        # Take the higher risk level (more conservative)
        combined_level = max(level1, level2)
        
        for level_name, level_value in risk_order.items():
            if level_value == combined_level:
                return level_name
        
        return "medium"

class SelectionOperator:
    """Handles selection operations for evolution"""
    
    def __init__(self):
        self.name = "SelectionOperator"
    
    def tournament_selection(self, population: List[EvolutionCandidate], tournament_size: int = 3) -> EvolutionCandidate:
        """Tournament selection of candidates"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        
        # Select best candidate from tournament
        viable_candidates = [c for c in tournament if c.fitness and c.fitness.is_viable_candidate()]
        
        if viable_candidates:
            return max(viable_candidates, key=lambda c: c.fitness.overall_fitness)
        else:
            return random.choice(tournament)
    
    def roulette_wheel_selection(self, population: List[EvolutionCandidate]) -> EvolutionCandidate:
        """Roulette wheel selection based on fitness"""
        viable_candidates = [c for c in population if c.fitness]
        
        if not viable_candidates:
            return random.choice(population)
        
        # Calculate total fitness
        total_fitness = sum(c.fitness.overall_fitness for c in viable_candidates)
        
        if total_fitness == 0:
            return random.choice(viable_candidates)
        
        # Spin the wheel
        spin = random.uniform(0, total_fitness)
        current = 0
        
        for candidate in viable_candidates:
            current += candidate.fitness.overall_fitness
            if current >= spin:
                return candidate
        
        return viable_candidates[-1]  # Fallback
    
    def elite_selection(self, population: List[EvolutionCandidate], elite_size: int) -> List[EvolutionCandidate]:
        """Select elite candidates"""
        viable_candidates = [c for c in population if c.fitness and c.fitness.is_viable_candidate()]
        viable_candidates.sort(key=lambda c: c.fitness.overall_fitness, reverse=True)
        
        return viable_candidates[:elite_size]