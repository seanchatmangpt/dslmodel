"""
Core Evolution Framework Components
Autonomous evolution engine for continuous system improvement
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import hashlib
import json
import uuid

from dslmodel import DSLModel
from pydantic import Field, validator

class EvolutionStrategy(str, Enum):
    """Evolution strategies for different improvement approaches"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_HARDENING = "security_hardening"
    CODE_QUALITY_IMPROVEMENT = "code_quality_improvement"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    ARCHITECTURE_REFINEMENT = "architecture_refinement"
    BUG_ELIMINATION = "bug_elimination"
    DEPENDENCY_OPTIMIZATION = "dependency_optimization"
    API_IMPROVEMENT = "api_improvement"
    DOCUMENTATION_ENHANCEMENT = "documentation_enhancement"
    TEST_COVERAGE_EXPANSION = "test_coverage_expansion"

class EvolutionPhase(str, Enum):
    """Phases of the evolution process"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    MUTATION = "mutation"
    CROSSOVER = "crossover"
    SELECTION = "selection"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"

class FitnessMetric(str, Enum):
    """Metrics for evaluating evolutionary fitness"""
    PERFORMANCE_SCORE = "performance_score"
    SECURITY_SCORE = "security_score"
    QUALITY_SCORE = "quality_score"
    MAINTAINABILITY_SCORE = "maintainability_score"
    RELIABILITY_SCORE = "reliability_score"
    SCALABILITY_SCORE = "scalability_score"
    USABILITY_SCORE = "usability_score"
    EFFICIENCY_SCORE = "efficiency_score"
    ROBUSTNESS_SCORE = "robustness_score"
    INNOVATION_SCORE = "innovation_score"

class EvolutionaryFitness(DSLModel):
    """Comprehensive fitness evaluation for evolutionary candidates"""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    strategy: EvolutionStrategy = Field(..., description="Evolution strategy used")
    
    # Core fitness metrics (0.0 - 1.0)
    performance_score: float = Field(..., ge=0.0, le=1.0, description="Performance efficiency")
    security_score: float = Field(..., ge=0.0, le=1.0, description="Security strength")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Code quality")
    maintainability_score: float = Field(..., ge=0.0, le=1.0, description="Maintainability")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="System reliability")
    
    # Advanced metrics
    scalability_score: float = Field(0.5, ge=0.0, le=1.0, description="Scalability potential")
    usability_score: float = Field(0.5, ge=0.0, le=1.0, description="API usability")
    efficiency_score: float = Field(0.5, ge=0.0, le=1.0, description="Resource efficiency")
    robustness_score: float = Field(0.5, ge=0.0, le=1.0, description="Error handling")
    innovation_score: float = Field(0.5, ge=0.0, le=1.0, description="Novel improvements")
    
    # Weighted overall fitness
    overall_fitness: float = Field(0.0, ge=0.0, le=1.0, description="Weighted overall score")
    
    # Meta information
    evaluation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    improvements_detected: List[str] = Field(default_factory=list, description="Specific improvements")
    regressions_detected: List[str] = Field(default_factory=list, description="Potential regressions")
    confidence_level: float = Field(0.8, ge=0.0, le=1.0, description="Confidence in evaluation")
    
    def calculate_overall_fitness(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted overall fitness score"""
        if weights is None:
            # Default weights favoring core metrics
            weights = {
                "performance_score": 0.15,
                "security_score": 0.15,
                "quality_score": 0.15,
                "maintainability_score": 0.15,
                "reliability_score": 0.15,
                "scalability_score": 0.05,
                "usability_score": 0.05,
                "efficiency_score": 0.05,
                "robustness_score": 0.05,
                "innovation_score": 0.05
            }
        
        total_score = sum(
            getattr(self, metric) * weight 
            for metric, weight in weights.items()
            if hasattr(self, metric)
        )
        
        self.overall_fitness = min(total_score, 1.0)
        return self.overall_fitness
    
    def is_viable_candidate(self, threshold: float = 0.6) -> bool:
        """Determine if candidate meets viability threshold"""
        return self.overall_fitness >= threshold and len(self.regressions_detected) == 0

class EvolutionCandidate(DSLModel):
    """Represents a candidate solution in the evolution process"""
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generation: int = Field(..., description="Generation number")
    strategy: EvolutionStrategy = Field(..., description="Evolution strategy")
    parent_ids: List[str] = Field(default_factory=list, description="Parent candidate IDs")
    
    # Changes and modifications
    code_changes: Dict[str, str] = Field(default_factory=dict, description="File path -> new content")
    new_files: Dict[str, str] = Field(default_factory=dict, description="New file path -> content")
    deleted_files: List[str] = Field(default_factory=list, description="Files to delete")
    
    # Metadata
    description: str = Field(..., description="Human-readable description of changes")
    implementation_notes: List[str] = Field(default_factory=list, description="Implementation details")
    estimated_impact: str = Field("medium", description="Expected impact level")
    risk_level: str = Field("low", description="Risk assessment")
    
    # Evolution tracking
    mutation_applied: List[str] = Field(default_factory=list, description="Mutations applied")
    crossover_source: Optional[str] = Field(None, description="Source for crossover")
    fitness: Optional[EvolutionaryFitness] = Field(None, description="Fitness evaluation")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    validated: bool = Field(False, description="Whether candidate passed validation")
    deployed: bool = Field(False, description="Whether candidate was deployed")

class EvolutionResult(DSLModel):
    """Result of an evolution cycle"""
    evolution_id: str = Field(..., description="Unique evolution cycle ID")
    strategy: EvolutionStrategy = Field(..., description="Strategy used")
    
    # Cycle metrics
    generation_count: int = Field(..., description="Number of generations")
    candidate_count: int = Field(..., description="Total candidates evaluated")
    success_count: int = Field(..., description="Successful improvements")
    
    # Best candidate
    best_candidate: Optional[EvolutionCandidate] = Field(None, description="Best evolved candidate")
    fitness_improvement: float = Field(0.0, description="Fitness improvement achieved")
    
    # Evolution statistics
    convergence_generation: Optional[int] = Field(None, description="Generation where convergence occurred")
    diversity_score: float = Field(0.0, ge=0.0, le=1.0, description="Population diversity")
    innovation_rate: float = Field(0.0, ge=0.0, le=1.0, description="Rate of novel solutions")
    
    # Performance metrics
    evolution_duration: timedelta = Field(..., description="Total evolution time")
    analysis_time: float = Field(0.0, description="Time spent on analysis")
    generation_time: float = Field(0.0, description="Time spent generating candidates")
    validation_time: float = Field(0.0, description="Time spent on validation")
    
    # Deployment results
    deployed: bool = Field(False, description="Whether improvement was deployed")
    rollback_required: bool = Field(False, description="Whether rollback was needed")
    production_impact: Optional[str] = Field(None, description="Observed production impact")
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class EvolutionConfig(DSLModel):
    """Configuration for evolution processes"""
    target_path: Path = Field(..., description="Target codebase path")
    strategies: List[EvolutionStrategy] = Field(..., description="Evolution strategies to use")
    
    # Population parameters
    population_size: int = Field(10, ge=1, le=100, description="Number of candidates per generation")
    max_generations: int = Field(20, ge=1, le=1000, description="Maximum generations")
    convergence_threshold: float = Field(0.01, ge=0.001, le=0.1, description="Convergence criteria")
    
    # Selection parameters
    selection_pressure: float = Field(0.7, ge=0.1, le=1.0, description="Selection pressure")
    elitism_rate: float = Field(0.2, ge=0.0, le=0.5, description="Elite preservation rate")
    mutation_rate: float = Field(0.1, ge=0.01, le=0.5, description="Mutation probability")
    crossover_rate: float = Field(0.8, ge=0.1, le=1.0, description="Crossover probability")
    
    # Fitness weights
    fitness_weights: Dict[str, float] = Field(default_factory=dict, description="Custom fitness weights")
    
    # Safety and validation
    enable_safety_checks: bool = Field(True, description="Enable safety validation")
    require_tests_pass: bool = Field(True, description="Require all tests to pass")
    max_risk_level: str = Field("medium", description="Maximum acceptable risk level")
    
    # Performance constraints
    max_evolution_time: timedelta = Field(
        default_factory=lambda: timedelta(hours=2),
        description="Maximum time for evolution cycle"
    )
    parallel_evaluation: bool = Field(True, description="Enable parallel candidate evaluation")
    resource_limits: Dict[str, int] = Field(
        default_factory=lambda: {"cpu_percent": 80, "memory_mb": 2048},
        description="Resource usage limits"
    )

class EvolutionEngine:
    """Main evolution engine coordinating autonomous improvement"""
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.current_generation = 0
        self.population: List[EvolutionCandidate] = []
        self.evolution_history: List[EvolutionResult] = []
        self.best_overall: Optional[EvolutionCandidate] = None
        
        # Initialize components (will be injected)
        self.analyzers: Dict[str, Any] = {}
        self.generators: Dict[str, Any] = {}
        self.operators: Dict[str, Any] = {}
        self.validators: Dict[str, Any] = {}
        
        # Evolution state
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.convergence_detected = False
        
    def register_analyzer(self, name: str, analyzer):
        """Register an analysis component"""
        self.analyzers[name] = analyzer
        
    def register_generator(self, name: str, generator):
        """Register a generation component"""
        self.generators[name] = generator
        
    def register_operator(self, name: str, operator):
        """Register an evolution operator"""
        self.operators[name] = operator
        
    def register_validator(self, name: str, validator):
        """Register a validation component"""
        self.validators[name] = validator
    
    async def evolve(self, strategy: Optional[EvolutionStrategy] = None) -> EvolutionResult:
        """Run complete evolution cycle"""
        evolution_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.is_running = True
        
        try:
            # Select strategy if not provided
            if strategy is None:
                strategy = await self._select_optimal_strategy()
            
            print(f"🧬 Starting evolution cycle: {strategy.value}")
            print(f"🎯 Target: {self.config.target_path}")
            
            # Phase 1: Analysis
            analysis_start = datetime.utcnow()
            baseline_fitness = await self._analyze_current_state()
            analysis_time = (datetime.utcnow() - analysis_start).total_seconds()
            
            # Phase 2: Generation
            generation_start = datetime.utcnow()
            await self._initialize_population(strategy)
            
            # Phase 3: Evolution loop
            for generation in range(self.config.max_generations):
                self.current_generation = generation
                
                print(f"🔄 Generation {generation + 1}/{self.config.max_generations}")
                
                # Evaluate fitness
                await self._evaluate_population()
                
                # Check convergence
                if await self._check_convergence():
                    print(f"✅ Convergence detected at generation {generation + 1}")
                    self.convergence_detected = True
                    break
                
                # Selection
                selected = await self._selection()
                
                # Generate new population
                await self._generate_offspring(selected, strategy)
                
                # Report progress
                best_fitness = max(c.fitness.overall_fitness for c in self.population if c.fitness)
                print(f"   Best fitness: {best_fitness:.3f}")
            
            generation_time = (datetime.utcnow() - generation_start).total_seconds()
            
            # Phase 4: Validation and deployment
            validation_start = datetime.utcnow()
            best_candidate = await self._select_best_candidate()
            
            if best_candidate and await self._validate_candidate(best_candidate):
                deployment_success = await self._deploy_candidate(best_candidate)
            else:
                deployment_success = False
                
            validation_time = (datetime.utcnow() - validation_start).total_seconds()
            
            # Generate result
            result = EvolutionResult(
                evolution_id=evolution_id,
                strategy=strategy,
                generation_count=self.current_generation + 1,
                candidate_count=len(self.population),
                success_count=sum(1 for c in self.population if c.fitness and c.fitness.is_viable_candidate()),
                best_candidate=best_candidate,
                fitness_improvement=best_candidate.fitness.overall_fitness - baseline_fitness.overall_fitness if best_candidate and best_candidate.fitness else 0.0,
                convergence_generation=self.current_generation + 1 if self.convergence_detected else None,
                diversity_score=await self._calculate_diversity(),
                innovation_rate=await self._calculate_innovation_rate(),
                evolution_duration=datetime.utcnow() - self.start_time,
                analysis_time=analysis_time,
                generation_time=generation_time,
                validation_time=validation_time,
                deployed=deployment_success
            )
            
            self.evolution_history.append(result)
            
            if best_candidate and deployment_success:
                self.best_overall = best_candidate
                print(f"🚀 Evolution successful! Fitness improved by {result.fitness_improvement:.3f}")
            else:
                print(f"⚠️  Evolution completed but no viable improvements found")
            
            return result
            
        finally:
            self.is_running = False
    
    async def _select_optimal_strategy(self) -> EvolutionStrategy:
        """Automatically select optimal evolution strategy"""
        # Analyze current state to determine best strategy
        analysis_results = {}
        
        for analyzer_name, analyzer in self.analyzers.items():
            if hasattr(analyzer, 'analyze'):
                analysis_results[analyzer_name] = await analyzer.analyze(self.config.target_path)
        
        # Simple heuristic for strategy selection
        if 'security' in analysis_results and hasattr(analysis_results['security'], 'metrics') and analysis_results['security'].metrics.get('critical_count', 0) > 0:
            return EvolutionStrategy.SECURITY_HARDENING
        elif 'performance' in analysis_results and hasattr(analysis_results['performance'], 'score') and analysis_results['performance'].score < 0.7:
            return EvolutionStrategy.PERFORMANCE_OPTIMIZATION
        elif 'quality' in analysis_results and hasattr(analysis_results['quality'], 'score') and analysis_results['quality'].score < 0.8:
            return EvolutionStrategy.CODE_QUALITY_IMPROVEMENT
        else:
            return EvolutionStrategy.FEATURE_ENHANCEMENT
    
    async def _analyze_current_state(self) -> EvolutionaryFitness:
        """Analyze current codebase state to establish baseline"""
        fitness_scores = {}
        
        # Run all available analyzers
        for analyzer_name, analyzer in self.analyzers.items():
            if hasattr(analyzer, 'evaluate_fitness'):
                score = await analyzer.evaluate_fitness(self.config.target_path)
                fitness_scores[analyzer_name] = score
        
        # If no scores, use defaults
        if not fitness_scores:
            fitness_scores = {
                'performance': 0.7,
                'security': 0.7,
                'quality': 0.5,
                'maintainability': 0.6,
                'reliability': 0.6
            }
        
        # Create baseline fitness
        baseline = EvolutionaryFitness(
            candidate_id="baseline",
            strategy=EvolutionStrategy.PERFORMANCE_OPTIMIZATION,  # Placeholder
            performance_score=fitness_scores.get('performance', 0.5),
            security_score=fitness_scores.get('security', 0.5),
            quality_score=fitness_scores.get('quality', 0.5),
            maintainability_score=fitness_scores.get('maintainability', 0.5),
            reliability_score=fitness_scores.get('reliability', 0.5)
        )
        
        baseline.calculate_overall_fitness(self.config.fitness_weights or None)
        
        print(f"📊 Baseline fitness: {baseline.overall_fitness:.3f}")
        print(f"   Performance: {baseline.performance_score:.3f}")
        print(f"   Security: {baseline.security_score:.3f}")
        print(f"   Quality: {baseline.quality_score:.3f}")
        return baseline
    
    async def _initialize_population(self, strategy: EvolutionStrategy):
        """Initialize population of evolution candidates"""
        self.population = []
        
        # Generate initial candidates using available generators
        for i in range(self.config.population_size):
            candidate = await self._generate_candidate(strategy, generation=0)
            if candidate:
                self.population.append(candidate)
        
        print(f"🌱 Initialized population with {len(self.population)} candidates")
    
    async def _generate_candidate(self, strategy: EvolutionStrategy, generation: int, parents: List[str] = None) -> Optional[EvolutionCandidate]:
        """Generate a single evolution candidate"""
        
        # Select appropriate generator based on strategy
        generator = self._select_generator(strategy)
        if not generator:
            return None
        
        try:
            # Generate candidate
            if hasattr(generator, 'generate'):
                candidate_data = await generator.generate(
                    self.config.target_path, 
                    strategy, 
                    generation
                )
                
                candidate = EvolutionCandidate(
                    generation=generation,
                    strategy=strategy,
                    parent_ids=parents or [],
                    **candidate_data
                )
                
                return candidate
                
        except Exception as e:
            print(f"⚠️  Failed to generate candidate: {e}")
            return None
    
    def _select_generator(self, strategy: EvolutionStrategy):
        """Select appropriate generator for strategy"""
        strategy_mapping = {
            EvolutionStrategy.PERFORMANCE_OPTIMIZATION: "optimization",
            EvolutionStrategy.SECURITY_HARDENING: "security", 
            EvolutionStrategy.CODE_QUALITY_IMPROVEMENT: "refactoring",
            EvolutionStrategy.FEATURE_ENHANCEMENT: "feature",
            EvolutionStrategy.ARCHITECTURE_REFINEMENT: "architecture"
        }
        
        generator_name = strategy_mapping.get(strategy, "code")
        return self.generators.get(generator_name)
    
    async def _evaluate_population(self):
        """Evaluate fitness for all candidates in population"""
        evaluation_tasks = []
        
        for candidate in self.population:
            if not candidate.fitness:
                task = self._evaluate_candidate_fitness(candidate)
                evaluation_tasks.append(task)
        
        if evaluation_tasks:
            if self.config.parallel_evaluation:
                await asyncio.gather(*evaluation_tasks)
            else:
                for task in evaluation_tasks:
                    await task
    
    async def _evaluate_candidate_fitness(self, candidate: EvolutionCandidate):
        """Evaluate fitness for a single candidate"""
        try:
            # Apply candidate changes temporarily for evaluation
            temp_scores = await self._simulate_candidate_impact(candidate)
            
            fitness = EvolutionaryFitness(
                candidate_id=candidate.candidate_id,
                strategy=candidate.strategy,
                performance_score=temp_scores.get('performance', 0.5),
                security_score=temp_scores.get('security', 0.5),
                quality_score=temp_scores.get('quality', 0.5),
                maintainability_score=temp_scores.get('maintainability', 0.5),
                reliability_score=temp_scores.get('reliability', 0.5),
                improvements_detected=temp_scores.get('improvements', []),
                regressions_detected=temp_scores.get('regressions', [])
            )
            
            fitness.calculate_overall_fitness(self.config.fitness_weights)
            candidate.fitness = fitness
            
        except Exception as e:
            print(f"⚠️  Failed to evaluate candidate {candidate.candidate_id}: {e}")
            # Assign default low fitness
            candidate.fitness = EvolutionaryFitness(
                candidate_id=candidate.candidate_id,
                strategy=candidate.strategy,
                performance_score=0.1,
                security_score=0.1,
                quality_score=0.1,
                maintainability_score=0.1,
                reliability_score=0.1
            )
            candidate.fitness.calculate_overall_fitness()
    
    async def _simulate_candidate_impact(self, candidate: EvolutionCandidate) -> Dict[str, Any]:
        """Simulate the impact of applying candidate changes"""
        # This would temporarily apply changes and measure impact
        # For now, return mock scores with some randomness
        import random
        
        base_score = 0.5
        improvement_factor = random.uniform(0.8, 1.5)
        
        # Give higher scores to certain strategies
        strategy_bonus = {
            EvolutionStrategy.FEATURE_ENHANCEMENT: 0.2,
            EvolutionStrategy.CODE_QUALITY_IMPROVEMENT: 0.15,
            EvolutionStrategy.PERFORMANCE_OPTIMIZATION: 0.1,
            EvolutionStrategy.TEST_COVERAGE_EXPANSION: 0.25
        }
        
        bonus = strategy_bonus.get(candidate.strategy, 0.0)
        
        return {
            'performance': min(base_score * improvement_factor + bonus, 1.0),
            'security': min(base_score * improvement_factor + bonus, 1.0),
            'quality': min(base_score * improvement_factor + bonus, 1.0),
            'maintainability': min(base_score * improvement_factor + bonus, 1.0),
            'reliability': min(base_score * improvement_factor + bonus, 1.0),
            'improvements': [f"Improvement from {candidate.strategy.value}"],
            'regressions': []
        }
    
    async def _check_convergence(self) -> bool:
        """Check if population has converged"""
        if len(self.population) < 2:
            return False
        
        # Calculate fitness variance
        fitness_scores = [c.fitness.overall_fitness for c in self.population if c.fitness]
        if not fitness_scores:
            return False
        
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        variance = sum((score - avg_fitness) ** 2 for score in fitness_scores) / len(fitness_scores)
        
        return variance < self.config.convergence_threshold
    
    async def _selection(self) -> List[EvolutionCandidate]:
        """Select candidates for reproduction"""
        # Sort by fitness
        viable_candidates = [c for c in self.population if c.fitness and c.fitness.is_viable_candidate()]
        viable_candidates.sort(key=lambda c: c.fitness.overall_fitness, reverse=True)
        
        # Elite selection
        elite_count = int(len(viable_candidates) * self.config.elitism_rate)
        selected = viable_candidates[:elite_count]
        
        # Tournament selection for remaining slots
        remaining_slots = self.config.population_size - elite_count
        
        for _ in range(remaining_slots):
            tournament_size = max(2, int(len(viable_candidates) * 0.1))
            tournament = random.sample(viable_candidates, min(tournament_size, len(viable_candidates)))
            winner = max(tournament, key=lambda c: c.fitness.overall_fitness)
            selected.append(winner)
        
        return selected
    
    async def _generate_offspring(self, parents: List[EvolutionCandidate], strategy: EvolutionStrategy):
        """Generate new population from selected parents"""
        new_population = []
        
        # Keep elite parents
        elite_count = int(len(parents) * self.config.elitism_rate)
        new_population.extend(parents[:elite_count])
        
        # Generate offspring
        while len(new_population) < self.config.population_size:
            # Crossover
            if random.random() < self.config.crossover_rate and len(parents) >= 2:
                parent1, parent2 = random.sample(parents, 2)
                offspring = await self._crossover(parent1, parent2, strategy)
            else:
                parent = random.choice(parents)
                offspring = await self._mutate(parent, strategy)
            
            if offspring:
                new_population.append(offspring)
        
        self.population = new_population[:self.config.population_size]
    
    async def _crossover(self, parent1: EvolutionCandidate, parent2: EvolutionCandidate, strategy: EvolutionStrategy) -> Optional[EvolutionCandidate]:
        """Create offspring through crossover"""
        crossover_op = self.operators.get('crossover')
        if crossover_op and hasattr(crossover_op, 'crossover'):
            return await crossover_op.crossover(parent1, parent2, strategy, self.current_generation + 1)
        
        # Default simple crossover
        offspring_data = {
            'description': f"Crossover of {parent1.description} and {parent2.description}",
            'code_changes': {**parent1.code_changes, **parent2.code_changes},
            'new_files': {**parent1.new_files, **parent2.new_files},
            'parent_ids': [parent1.candidate_id, parent2.candidate_id],
            'crossover_source': f"{parent1.candidate_id}+{parent2.candidate_id}"
        }
        
        return EvolutionCandidate(
            generation=self.current_generation + 1,
            strategy=strategy,
            **offspring_data
        )
    
    async def _mutate(self, parent: EvolutionCandidate, strategy: EvolutionStrategy) -> Optional[EvolutionCandidate]:
        """Create offspring through mutation"""
        mutation_op = self.operators.get('mutation')
        if mutation_op and hasattr(mutation_op, 'mutate'):
            return await mutation_op.mutate(parent, strategy, self.current_generation + 1)
        
        # Default simple mutation
        mutated_data = {
            'description': f"Mutation of {parent.description}",
            'code_changes': parent.code_changes.copy(),
            'new_files': parent.new_files.copy(),
            'parent_ids': [parent.candidate_id],
            'mutation_applied': [f"random_mutation_{strategy.value}"]
        }
        
        return EvolutionCandidate(
            generation=self.current_generation + 1,
            strategy=strategy,
            **mutated_data
        )
    
    async def _select_best_candidate(self) -> Optional[EvolutionCandidate]:
        """Select the best candidate from final population"""
        viable_candidates = [c for c in self.population if c.fitness and c.fitness.is_viable_candidate()]
        
        if not viable_candidates:
            return None
        
        return max(viable_candidates, key=lambda c: c.fitness.overall_fitness)
    
    async def _validate_candidate(self, candidate: EvolutionCandidate) -> bool:
        """Validate candidate before deployment"""
        if not self.config.enable_safety_checks:
            return True
        
        # Run validation checks
        for validator_name, validator in self.validators.items():
            if hasattr(validator, 'validate'):
                is_valid = await validator.validate(candidate, self.config.target_path)
                if not is_valid:
                    print(f"❌ Validation failed: {validator_name}")
                    return False
        
        candidate.validated = True
        print(f"✅ Candidate {candidate.candidate_id} validated successfully")
        return True
    
    async def _deploy_candidate(self, candidate: EvolutionCandidate) -> bool:
        """Deploy validated candidate"""
        try:
            # Apply changes to target codebase
            for file_path, content in candidate.code_changes.items():
                target_file = self.config.target_path / file_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(content)
            
            for file_path, content in candidate.new_files.items():
                target_file = self.config.target_path / file_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(content)
            
            for file_path in candidate.deleted_files:
                target_file = self.config.target_path / file_path
                if target_file.exists():
                    target_file.unlink()
            
            candidate.deployed = True
            print(f"🚀 Candidate {candidate.candidate_id} deployed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    async def _calculate_diversity(self) -> float:
        """Calculate population diversity score"""
        if len(self.population) < 2:
            return 0.0
        
        # Simple diversity metric based on fitness variance
        fitness_scores = [c.fitness.overall_fitness for c in self.population if c.fitness]
        if not fitness_scores:
            return 0.0
        
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        variance = sum((score - avg_fitness) ** 2 for score in fitness_scores) / len(fitness_scores)
        
        return min(variance * 10, 1.0)  # Normalize to 0-1
    
    async def _calculate_innovation_rate(self) -> float:
        """Calculate rate of innovative solutions"""
        if not self.population:
            return 0.0
        
        # Count candidates with innovation score > 0.7
        innovative_count = sum(
            1 for c in self.population 
            if c.fitness and c.fitness.innovation_score > 0.7
        )
        
        return innovative_count / len(self.population)

import random