"""
DSLModel Autonomous Evolution Framework
Self-improving, self-optimizing, and self-enhancing system
"""

from .core import (
    EvolutionEngine,
    EvolutionaryFitness,
    EvolutionStrategy,
    EvolutionResult,
    EvolutionConfig,
    EvolutionCandidate,
    EvolutionPhase,
    FitnessMetric
)

from .analyzers import (
    CodeAnalyzer,
    PerformanceAnalyzer,
    SecurityAnalyzer,
    QualityAnalyzer,
    ArchitectureAnalyzer
)

from .generators import (
    CodeGenerator,
    OptimizationGenerator,
    FeatureGenerator,
    RefactoringGenerator,
    TestGenerator
)

from .operators import (
    MutationOperator,
    CrossoverOperator,
    SelectionOperator
)

from .validators import (
    SyntaxValidator,
    SecurityValidator,
    TestValidator,
    PerformanceValidator,
    QualityValidator,
    RegressionValidator,
    CompositeValidator
)

__all__ = [
    # Core framework
    "EvolutionEngine",
    "EvolutionaryFitness",
    "EvolutionStrategy", 
    "EvolutionResult",
    "EvolutionConfig",
    "EvolutionCandidate",
    "EvolutionPhase",
    "FitnessMetric",
    
    # Analysis components
    "CodeAnalyzer",
    "PerformanceAnalyzer",
    "SecurityAnalyzer", 
    "QualityAnalyzer",
    "ArchitectureAnalyzer",
    
    # Generation components
    "CodeGenerator",
    "OptimizationGenerator",
    "FeatureGenerator",
    "RefactoringGenerator",
    "TestGenerator",
    
    # Evolution operators
    "MutationOperator",
    "CrossoverOperator",
    "SelectionOperator",
    
    # Validation components
    "SyntaxValidator",
    "SecurityValidator",
    "TestValidator",
    "PerformanceValidator",
    "QualityValidator",
    "RegressionValidator",
    "CompositeValidator"
]