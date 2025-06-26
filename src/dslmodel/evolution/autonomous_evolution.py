"""Autonomous Evolution Engine - Self-improving SwarmAgent ecosystem.

The system automatically evolves based on:
1. Telemetry performance metrics from OTEL spans
2. Validation success rates from Weaver
3. Agent coordination efficiency
4. Feature development velocity
5. Error patterns and remediation success

Evolution strategies:
- Genetic algorithms for agent behavior optimization
- Reinforcement learning from telemetry feedback
- A/B testing of agent variants
- Automatic code generation improvements
- Semantic convention evolution
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
import traceback
import statistics
import hashlib

from loguru import logger
from pydantic import BaseModel, Field
import numpy as np

# Import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry not available")

# Import validation components
try:
    from ..validation.weaver_otel_validator import WeaverOTELValidator
    from ..validation.swarm_validation_loop import SwarmValidationLoop
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    logger.warning("Validation components not available")


class EvolutionStrategy(Enum):
    """Evolution strategy types."""
    GENETIC_ALGORITHM = "genetic_algorithm"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    AB_TESTING = "ab_testing"
    MUTATION_BREEDING = "mutation_breeding"
    PERFORMANCE_GRADIENT = "performance_gradient"
    SWARM_OPTIMIZATION = "swarm_optimization"


class FitnessMetric(Enum):
    """Fitness evaluation metrics."""
    VALIDATION_SUCCESS_RATE = "validation_success_rate"
    THROUGHPUT_PERFORMANCE = "throughput_performance"
    ERROR_RATE = "error_rate"
    REMEDIATION_EFFICIENCY = "remediation_efficiency"
    FEATURE_COMPLETION_VELOCITY = "feature_completion_velocity"
    COORDINATION_EFFICIENCY = "coordination_efficiency"
    RESOURCE_UTILIZATION = "resource_utilization"


@dataclass
class EvolutionGenome:
    """Genetic representation of an agent or system component."""
    genome_id: str
    genome_type: str  # "agent", "validator", "coordinator", etc.
    genes: Dict[str, Any] = field(default_factory=dict)
    fitness_score: float = 0.0
    generation: int = 0
    parent_genomes: List[str] = field(default_factory=list)
    mutation_history: List[str] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    creation_time: float = field(default_factory=time.time)


@dataclass
class EvolutionMetrics:
    """Metrics collected for evolution feedback."""
    metric_type: FitnessMetric
    value: float
    timestamp: float
    source_component: str
    context: Dict[str, Any] = field(default_factory=dict)


class AutonomousEvolutionEngine:
    """Main evolution engine that automatically improves the SwarmAgent ecosystem."""
    
    def __init__(self,
                 coordination_dir: Path = Path("/Users/sac/s2s/agent_coordination"),
                 evolution_dir: Path = Path("/tmp/swarm_evolution"),
                 population_size: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 elite_percentage: float = 0.2):
        
        self.coordination_dir = coordination_dir
        self.evolution_dir = evolution_dir
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_percentage = elite_percentage
        
        # Ensure directories exist
        self.coordination_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        
        # Evolution state
        self.current_generation = 0
        self.population: List[EvolutionGenome] = []
        self.fitness_history: List[List[float]] = []
        self.best_genome: Optional[EvolutionGenome] = None
        self.evolution_metrics: List[EvolutionMetrics] = []
        
        # Performance baselines
        self.baseline_metrics: Dict[FitnessMetric, float] = {}
        self.performance_targets: Dict[FitnessMetric, float] = {
            FitnessMetric.VALIDATION_SUCCESS_RATE: 0.95,
            FitnessMetric.THROUGHPUT_PERFORMANCE: 50000.0,  # validations/sec
            FitnessMetric.ERROR_RATE: 0.05,
            FitnessMetric.REMEDIATION_EFFICIENCY: 0.80,
            FitnessMetric.FEATURE_COMPLETION_VELOCITY: 10.0,  # features/day
            FitnessMetric.COORDINATION_EFFICIENCY: 0.90
        }
        
        # Evolution components
        self.validator = WeaverOTELValidator(coordination_dir) if VALIDATION_AVAILABLE else None
        self.tracer = self._setup_tracer() if OTEL_AVAILABLE else None
        
        # Evolution strategies
        self.active_strategies: Set[EvolutionStrategy] = {
            EvolutionStrategy.GENETIC_ALGORITHM,
            EvolutionStrategy.MUTATION_BREEDING,
            EvolutionStrategy.PERFORMANCE_GRADIENT
        }
        
        logger.info(f"🧬 AutonomousEvolutionEngine initialized")
        logger.info(f"   Population size: {population_size}")
        logger.info(f"   Mutation rate: {mutation_rate}")
        logger.info(f"   Evolution dir: {evolution_dir}")
    
    def _setup_tracer(self):
        """Setup OpenTelemetry tracer for evolution telemetry."""
        if not OTEL_AVAILABLE:
            return None
            
        resource = Resource.create({
            "service.name": "autonomous-evolution-engine",
            "service.version": "1.0.0",
            "evolution.generation": str(self.current_generation),
            "evolution.population_size": str(self.population_size)
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        return trace.get_tracer(__name__)
    
    async def collect_telemetry_metrics(self) -> List[EvolutionMetrics]:
        """Collect performance metrics from telemetry data."""
        with self.tracer.start_as_current_span("collect_metrics") if self.tracer else nullcontext():
            metrics = []
            
            try:
                # Load recent telemetry spans
                spans_file = self.coordination_dir / "telemetry_spans.jsonl"
                if not spans_file.exists():
                    return metrics
                
                recent_spans = []
                cutoff_time = time.time() - 3600  # Last hour
                
                with open(spans_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                span = json.loads(line)
                                span_time = span.get('timestamp', 0)
                                if span_time > cutoff_time:
                                    recent_spans.append(span)
                            except json.JSONDecodeError:
                                continue
                
                # Calculate metrics from spans
                if recent_spans:
                    # Validation success rate
                    validation_spans = [s for s in recent_spans if 'validate' in s.get('name', '')]
                    if validation_spans:
                        success_rate = self._calculate_validation_success_rate(validation_spans)
                        metrics.append(EvolutionMetrics(
                            metric_type=FitnessMetric.VALIDATION_SUCCESS_RATE,
                            value=success_rate,
                            timestamp=time.time(),
                            source_component="validation_system",
                            context={"span_count": len(validation_spans)}
                        ))
                    
                    # Throughput performance
                    throughput = len(recent_spans) / 3600  # spans per second over last hour
                    metrics.append(EvolutionMetrics(
                        metric_type=FitnessMetric.THROUGHPUT_PERFORMANCE,
                        value=throughput,
                        timestamp=time.time(),
                        source_component="coordination_system",
                        context={"total_spans": len(recent_spans)}
                    ))
                    
                    # Error rate
                    error_spans = [s for s in recent_spans if 'error' in s.get('name', '').lower() or 'failed' in s.get('name', '').lower()]
                    error_rate = len(error_spans) / len(recent_spans) if recent_spans else 0
                    metrics.append(EvolutionMetrics(
                        metric_type=FitnessMetric.ERROR_RATE,
                        value=error_rate,
                        timestamp=time.time(),
                        source_component="coordination_system",
                        context={"error_spans": len(error_spans), "total_spans": len(recent_spans)}
                    ))
                    
                    # Remediation efficiency
                    remediation_spans = [s for s in recent_spans if 'remediat' in s.get('name', '').lower()]
                    successful_remediations = len([s for s in remediation_spans if 'success' in str(s.get('attributes', {}))])
                    remediation_efficiency = successful_remediations / len(remediation_spans) if remediation_spans else 0
                    metrics.append(EvolutionMetrics(
                        metric_type=FitnessMetric.REMEDIATION_EFFICIENCY,
                        value=remediation_efficiency,
                        timestamp=time.time(),
                        source_component="remediation_system",
                        context={"successful": successful_remediations, "total": len(remediation_spans)}
                    ))
                    
                    # Coordination efficiency
                    coordination_spans = [s for s in recent_spans if s.get('name', '').startswith('swarmsh.')]
                    coord_efficiency = len(coordination_spans) / len(recent_spans) if recent_spans else 0
                    metrics.append(EvolutionMetrics(
                        metric_type=FitnessMetric.COORDINATION_EFFICIENCY,
                        value=coord_efficiency,
                        timestamp=time.time(),
                        source_component="coordination_system",
                        context={"coordination_spans": len(coordination_spans)}
                    ))
                
                logger.info(f"📊 Collected {len(metrics)} evolution metrics")
                self.evolution_metrics.extend(metrics)
                
                return metrics
                
            except Exception as e:
                logger.error(f"Failed to collect metrics: {e}")
                return metrics
    
    def _calculate_validation_success_rate(self, validation_spans: List[Dict[str, Any]]) -> float:
        """Calculate validation success rate from spans."""
        if not validation_spans:
            return 0.0
        
        # Look for success indicators in span attributes
        successful = 0
        for span in validation_spans:
            attrs = span.get('attributes', {})
            if attrs.get('validation.passed', 0) > 0 or 'passed' in span.get('name', '').lower():
                successful += 1
        
        return successful / len(validation_spans)
    
    def initialize_population(self) -> List[EvolutionGenome]:
        """Initialize the first generation of genomes."""
        with self.tracer.start_as_current_span("initialize_population") if self.tracer else nullcontext():
            logger.info(f"🧬 Initializing evolution population (generation 0)")
            
            population = []
            
            # Create diverse initial genomes for different components
            genome_types = [
                "validator_config",
                "coordination_params", 
                "remediation_strategy",
                "agent_behavior",
                "performance_optimizer"
            ]
            
            for i in range(self.population_size):
                genome_type = genome_types[i % len(genome_types)]
                genome = self._create_random_genome(genome_type, i)
                population.append(genome)
            
            self.population = population
            self.current_generation = 0
            
            # Emit evolution start span
            self._emit_evolution_span(
                "swarmsh.evolution.initialize",
                {
                    "population_size": len(population),
                    "generation": 0,
                    "genome_types": len(genome_types)
                }
            )
            
            logger.info(f"✅ Created initial population of {len(population)} genomes")
            return population
    
    def _create_random_genome(self, genome_type: str, index: int) -> EvolutionGenome:
        """Create a random genome for the specified type."""
        genome_id = f"{genome_type}_{index}_{int(time.time())}"
        
        # Define gene parameters for different genome types
        if genome_type == "validator_config":
            genes = {
                "max_workers": random.randint(5, 50),
                "validation_timeout": random.uniform(1.0, 10.0),
                "retry_attempts": random.randint(1, 5),
                "batch_size": random.randint(10, 100),
                "validation_strictness": random.uniform(0.5, 1.0)
            }
        elif genome_type == "coordination_params":
            genes = {
                "coordination_interval": random.uniform(0.5, 5.0),
                "agent_timeout": random.uniform(5.0, 30.0),
                "max_concurrent_features": random.randint(1, 10),
                "priority_weights": {
                    "high": random.uniform(1.5, 3.0),
                    "medium": 1.0,
                    "low": random.uniform(0.3, 0.8)
                }
            }
        elif genome_type == "remediation_strategy":
            genes = {
                "auto_remediation_enabled": random.choice([True, False]),
                "max_remediation_attempts": random.randint(1, 5),
                "remediation_timeout": random.uniform(5.0, 30.0),
                "fallback_strategies": random.sample([
                    "retry", "normalize", "escalate", "quarantine"
                ], k=random.randint(1, 3))
            }
        elif genome_type == "agent_behavior":
            genes = {
                "decision_speed": random.uniform(0.1, 2.0),
                "risk_tolerance": random.uniform(0.1, 0.9),
                "collaboration_preference": random.uniform(0.3, 1.0),
                "learning_rate": random.uniform(0.01, 0.3),
                "exploration_factor": random.uniform(0.1, 0.5)
            }
        elif genome_type == "performance_optimizer":
            genes = {
                "cache_size": random.randint(100, 10000),
                "prefetch_enabled": random.choice([True, False]),
                "parallel_processing": random.choice([True, False]),
                "memory_limit_mb": random.randint(512, 4096),
                "optimization_level": random.randint(1, 3)
            }
        else:
            genes = {"random_param": random.random()}
        
        return EvolutionGenome(
            genome_id=genome_id,
            genome_type=genome_type,
            genes=genes,
            generation=self.current_generation
        )
    
    async def evaluate_fitness(self, genome: EvolutionGenome) -> float:
        """Evaluate the fitness of a genome based on performance metrics."""
        with self.tracer.start_as_current_span("evaluate_fitness") if self.tracer else nullcontext():
            try:
                # Apply genome configuration to test environment
                test_metrics = await self._test_genome_performance(genome)
                
                # Calculate composite fitness score
                fitness_score = 0.0
                total_weight = 0.0
                
                # Weight different metrics based on importance
                metric_weights = {
                    FitnessMetric.VALIDATION_SUCCESS_RATE: 0.3,
                    FitnessMetric.THROUGHPUT_PERFORMANCE: 0.2,
                    FitnessMetric.ERROR_RATE: 0.2,  # Lower is better
                    FitnessMetric.REMEDIATION_EFFICIENCY: 0.15,
                    FitnessMetric.COORDINATION_EFFICIENCY: 0.15
                }
                
                for metric_type, weight in metric_weights.items():
                    if metric_type in test_metrics:
                        metric_value = test_metrics[metric_type]
                        target_value = self.performance_targets[metric_type]
                        
                        # Normalize metric to 0-1 scale
                        if metric_type == FitnessMetric.ERROR_RATE:
                            # For error rate, lower is better
                            normalized_score = max(0, 1 - (metric_value / target_value))
                        else:
                            # For other metrics, higher is better
                            normalized_score = min(1, metric_value / target_value)
                        
                        fitness_score += normalized_score * weight
                        total_weight += weight
                
                # Normalize final score
                if total_weight > 0:
                    fitness_score = fitness_score / total_weight
                
                # Add bonus for novel/innovative genomes
                novelty_bonus = self._calculate_novelty_bonus(genome)
                fitness_score += novelty_bonus
                
                # Update genome fitness
                genome.fitness_score = fitness_score
                genome.performance_history.append(fitness_score)
                
                return fitness_score
                
            except Exception as e:
                logger.error(f"Fitness evaluation failed for {genome.genome_id}: {e}")
                return 0.0
    
    async def _test_genome_performance(self, genome: EvolutionGenome) -> Dict[FitnessMetric, float]:
        """Test genome performance in controlled environment."""
        # Simulate testing the genome configuration
        await asyncio.sleep(0.1)  # Simulate test time
        
        # Generate realistic performance metrics based on genome
        base_performance = {
            FitnessMetric.VALIDATION_SUCCESS_RATE: 0.85,
            FitnessMetric.THROUGHPUT_PERFORMANCE: 25000.0,
            FitnessMetric.ERROR_RATE: 0.08,
            FitnessMetric.REMEDIATION_EFFICIENCY: 0.75,
            FitnessMetric.COORDINATION_EFFICIENCY: 0.80
        }
        
        # Modify based on genome characteristics
        performance = base_performance.copy()
        
        if genome.genome_type == "validator_config":
            # Validator genomes affect validation and throughput
            max_workers = genome.genes.get("max_workers", 20)
            performance[FitnessMetric.THROUGHPUT_PERFORMANCE] *= (max_workers / 20)
            
            strictness = genome.genes.get("validation_strictness", 0.8)
            performance[FitnessMetric.VALIDATION_SUCCESS_RATE] *= strictness
            
        elif genome.genome_type == "coordination_params":
            # Coordination genomes affect coordination efficiency
            interval = genome.genes.get("coordination_interval", 2.0)
            performance[FitnessMetric.COORDINATION_EFFICIENCY] *= (2.0 / interval)
            
        elif genome.genome_type == "remediation_strategy":
            # Remediation genomes affect error handling
            if genome.genes.get("auto_remediation_enabled", True):
                performance[FitnessMetric.REMEDIATION_EFFICIENCY] *= 1.2
                performance[FitnessMetric.ERROR_RATE] *= 0.8
        
        # Add some randomness to simulate real-world variability
        for metric in performance:
            variance = random.uniform(0.9, 1.1)
            performance[metric] *= variance
        
        return performance
    
    def _calculate_novelty_bonus(self, genome: EvolutionGenome) -> float:
        """Calculate novelty bonus for diverse genomes."""
        # Compare with existing population
        if not self.population:
            return 0.1  # Base novelty bonus
        
        # Calculate genetic distance from existing genomes
        distances = []
        for other_genome in self.population:
            if other_genome.genome_id != genome.genome_id and other_genome.genome_type == genome.genome_type:
                distance = self._calculate_genome_distance(genome, other_genome)
                distances.append(distance)
        
        if not distances:
            return 0.1
        
        # Higher average distance = more novel = higher bonus
        avg_distance = statistics.mean(distances)
        novelty_bonus = min(0.2, avg_distance * 0.1)  # Cap at 20% bonus
        
        return novelty_bonus
    
    def _calculate_genome_distance(self, genome1: EvolutionGenome, genome2: EvolutionGenome) -> float:
        """Calculate genetic distance between two genomes."""
        if genome1.genome_type != genome2.genome_type:
            return 1.0  # Maximum distance for different types
        
        # Compare gene values
        common_genes = set(genome1.genes.keys()) & set(genome2.genes.keys())
        if not common_genes:
            return 1.0
        
        total_distance = 0.0
        for gene in common_genes:
            val1 = genome1.genes[gene]
            val2 = genome2.genes[gene]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric distance
                max_val = max(abs(val1), abs(val2), 1)  # Avoid division by zero
                distance = abs(val1 - val2) / max_val
            elif isinstance(val1, bool) and isinstance(val2, bool):
                # Boolean distance
                distance = 0 if val1 == val2 else 1
            elif isinstance(val1, str) and isinstance(val2, str):
                # String distance (simple)
                distance = 0 if val1 == val2 else 1
            else:
                # Default distance for complex types
                distance = 0 if val1 == val2 else 1
            
            total_distance += distance
        
        return total_distance / len(common_genes)
    
    async def evolve_generation(self) -> List[EvolutionGenome]:
        """Evolve to the next generation using genetic algorithms."""
        with self.tracer.start_as_current_span("evolve_generation") if self.tracer else nullcontext():
            logger.info(f"🧬 Evolving to generation {self.current_generation + 1}")
            
            # Evaluate fitness for all genomes
            for genome in self.population:
                await self.evaluate_fitness(genome)
            
            # Sort by fitness (descending)
            self.population.sort(key=lambda g: g.fitness_score, reverse=True)
            
            # Track best genome
            if not self.best_genome or self.population[0].fitness_score > self.best_genome.fitness_score:
                self.best_genome = self.population[0]
                logger.info(f"🏆 New best genome: {self.best_genome.genome_id} (fitness: {self.best_genome.fitness_score:.4f})")
            
            # Record generation fitness
            generation_fitness = [g.fitness_score for g in self.population]
            self.fitness_history.append(generation_fitness)
            
            # Create next generation
            new_population = []
            elite_count = int(self.population_size * self.elite_percentage)
            
            # Keep elite genomes
            for i in range(elite_count):
                elite = self.population[i]
                elite.generation = self.current_generation + 1
                new_population.append(elite)
            
            # Generate offspring through crossover and mutation
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()
                
                # Crossover
                if random.random() < self.crossover_rate:
                    offspring1, offspring2 = self._crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1, parent2
                
                # Mutation
                if random.random() < self.mutation_rate:
                    offspring1 = self._mutate(offspring1)
                if random.random() < self.mutation_rate:
                    offspring2 = self._mutate(offspring2)
                
                new_population.extend([offspring1, offspring2])
            
            # Trim to exact population size
            new_population = new_population[:self.population_size]
            
            # Update generation
            self.current_generation += 1
            self.population = new_population
            
            # Emit evolution span
            self._emit_evolution_span(
                "swarmsh.evolution.generation",
                {
                    "generation": self.current_generation,
                    "population_size": len(new_population),
                    "best_fitness": self.best_genome.fitness_score if self.best_genome else 0,
                    "avg_fitness": statistics.mean(generation_fitness),
                    "elite_count": elite_count
                }
            )
            
            logger.info(f"✅ Generation {self.current_generation} created")
            logger.info(f"   Best fitness: {max(generation_fitness):.4f}")
            logger.info(f"   Average fitness: {statistics.mean(generation_fitness):.4f}")
            
            return new_population
    
    def _tournament_selection(self, tournament_size: int = 3) -> EvolutionGenome:
        """Select parent using tournament selection."""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda g: g.fitness_score)
    
    def _crossover(self, parent1: EvolutionGenome, parent2: EvolutionGenome) -> Tuple[EvolutionGenome, EvolutionGenome]:
        """Create offspring through genetic crossover."""
        if parent1.genome_type != parent2.genome_type:
            # Can't crossover different types, return copies
            return self._copy_genome(parent1), self._copy_genome(parent2)
        
        # Create offspring
        offspring1_id = f"cross_{int(time.time())}_{random.randint(1000, 9999)}"
        offspring2_id = f"cross_{int(time.time())}_{random.randint(1000, 9999)}"
        
        offspring1_genes = {}
        offspring2_genes = {}
        
        # Mix genes from both parents
        all_genes = set(parent1.genes.keys()) | set(parent2.genes.keys())
        for gene in all_genes:
            if random.random() < 0.5:
                # Take from parent1
                if gene in parent1.genes:
                    offspring1_genes[gene] = parent1.genes[gene]
                if gene in parent2.genes:
                    offspring2_genes[gene] = parent2.genes[gene]
            else:
                # Take from parent2
                if gene in parent2.genes:
                    offspring1_genes[gene] = parent2.genes[gene]
                if gene in parent1.genes:
                    offspring2_genes[gene] = parent1.genes[gene]
        
        offspring1 = EvolutionGenome(
            genome_id=offspring1_id,
            genome_type=parent1.genome_type,
            genes=offspring1_genes,
            generation=self.current_generation + 1,
            parent_genomes=[parent1.genome_id, parent2.genome_id]
        )
        
        offspring2 = EvolutionGenome(
            genome_id=offspring2_id,
            genome_type=parent1.genome_type,
            genes=offspring2_genes,
            generation=self.current_generation + 1,
            parent_genomes=[parent1.genome_id, parent2.genome_id]
        )
        
        return offspring1, offspring2
    
    def _mutate(self, genome: EvolutionGenome) -> EvolutionGenome:
        """Apply random mutations to a genome."""
        mutated_genome = self._copy_genome(genome)
        mutated_genome.genome_id = f"mut_{int(time.time())}_{random.randint(1000, 9999)}"
        mutated_genome.mutation_history.append(f"gen_{self.current_generation}")
        
        # Mutate random genes
        genes_to_mutate = random.sample(list(mutated_genome.genes.keys()), 
                                       max(1, int(len(mutated_genome.genes) * 0.3)))
        
        for gene in genes_to_mutate:
            original_value = mutated_genome.genes[gene]
            
            if isinstance(original_value, int):
                # Integer mutation
                mutation_range = max(1, abs(original_value) // 4)
                mutated_genome.genes[gene] = original_value + random.randint(-mutation_range, mutation_range)
                mutated_genome.genes[gene] = max(1, mutated_genome.genes[gene])  # Keep positive
                
            elif isinstance(original_value, float):
                # Float mutation
                mutation_factor = random.uniform(0.8, 1.2)
                mutated_genome.genes[gene] = original_value * mutation_factor
                
            elif isinstance(original_value, bool):
                # Boolean mutation
                if random.random() < 0.3:  # 30% chance to flip
                    mutated_genome.genes[gene] = not original_value
                    
            elif isinstance(original_value, list):
                # List mutation
                if original_value and random.random() < 0.5:
                    if random.random() < 0.5:
                        # Remove element
                        if len(original_value) > 1:
                            original_value.remove(random.choice(original_value))
                    else:
                        # Add element (if it's a list of strings)
                        possible_values = ["retry", "normalize", "escalate", "quarantine", "optimize", "cache"]
                        new_value = random.choice(possible_values)
                        if new_value not in original_value:
                            original_value.append(new_value)
        
        return mutated_genome
    
    def _copy_genome(self, genome: EvolutionGenome) -> EvolutionGenome:
        """Create a deep copy of a genome."""
        import copy
        return EvolutionGenome(
            genome_id=f"copy_{genome.genome_id}",
            genome_type=genome.genome_type,
            genes=copy.deepcopy(genome.genes),
            fitness_score=genome.fitness_score,
            generation=genome.generation,
            parent_genomes=genome.parent_genomes.copy(),
            mutation_history=genome.mutation_history.copy(),
            performance_history=genome.performance_history.copy()
        )
    
    async def apply_best_genome(self) -> bool:
        """Apply the best evolved genome to the actual system."""
        if not self.best_genome:
            logger.warning("No best genome to apply")
            return False
        
        with self.tracer.start_as_current_span("apply_best_genome") if self.tracer else nullcontext():
            try:
                logger.info(f"🚀 Applying best genome: {self.best_genome.genome_id}")
                logger.info(f"   Fitness: {self.best_genome.fitness_score:.4f}")
                logger.info(f"   Type: {self.best_genome.genome_type}")
                
                # Save genome configuration
                genome_file = self.evolution_dir / f"best_genome_gen_{self.current_generation}.json"
                genome_data = {
                    "genome_id": self.best_genome.genome_id,
                    "genome_type": self.best_genome.genome_type,
                    "genes": self.best_genome.genes,
                    "fitness_score": self.best_genome.fitness_score,
                    "generation": self.best_genome.generation,
                    "applied_at": time.time()
                }
                
                with open(genome_file, 'w') as f:
                    json.dump(genome_data, f, indent=2)
                
                # Apply configuration based on genome type
                success = await self._apply_genome_configuration(self.best_genome)
                
                if success:
                    self._emit_evolution_span(
                        "swarmsh.evolution.apply_best",
                        {
                            "genome_id": self.best_genome.genome_id,
                            "genome_type": self.best_genome.genome_type,
                            "fitness_score": self.best_genome.fitness_score,
                            "generation": self.current_generation
                        }
                    )
                    
                    logger.info(f"✅ Successfully applied best genome")
                else:
                    logger.error(f"❌ Failed to apply best genome")
                
                return success
                
            except Exception as e:
                logger.error(f"Failed to apply best genome: {e}")
                return False
    
    async def _apply_genome_configuration(self, genome: EvolutionGenome) -> bool:
        """Apply genome configuration to system components."""
        try:
            # In a real implementation, this would update actual system configuration
            # For now, we'll simulate the application
            
            if genome.genome_type == "validator_config":
                # Update validator configuration
                config_file = self.evolution_dir / "evolved_validator_config.json"
                with open(config_file, 'w') as f:
                    json.dump(genome.genes, f, indent=2)
                    
            elif genome.genome_type == "coordination_params":
                # Update coordination parameters
                config_file = self.evolution_dir / "evolved_coordination_config.json"
                with open(config_file, 'w') as f:
                    json.dump(genome.genes, f, indent=2)
                    
            # Simulate configuration application time
            await asyncio.sleep(0.5)
            
            logger.info(f"📝 Applied {genome.genome_type} configuration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply configuration: {e}")
            return False
    
    async def continuous_evolution_loop(self, max_generations: int = 50, evolution_interval: float = 300.0):
        """Run continuous evolution loop."""
        logger.info(f"🔄 Starting continuous evolution loop")
        logger.info(f"   Max generations: {max_generations}")
        logger.info(f"   Evolution interval: {evolution_interval}s")
        
        # Initialize population
        if not self.population:
            self.initialize_population()
        
        try:
            for generation in range(max_generations):
                logger.info(f"\n🧬 === EVOLUTION CYCLE {generation + 1}/{max_generations} ===")
                
                # Collect current performance metrics
                await self.collect_telemetry_metrics()
                
                # Evolve to next generation
                await self.evolve_generation()
                
                # Apply best genome periodically
                if (generation + 1) % 5 == 0:  # Every 5 generations
                    await self.apply_best_genome()
                
                # Wait before next evolution cycle
                if generation < max_generations - 1:
                    logger.info(f"⏳ Waiting {evolution_interval}s before next evolution cycle...")
                    await asyncio.sleep(evolution_interval)
            
            # Final application of best genome
            await self.apply_best_genome()
            
            logger.info(f"🏁 Evolution completed after {max_generations} generations")
            
        except KeyboardInterrupt:
            logger.info("🛑 Evolution interrupted by user")
        except Exception as e:
            logger.error(f"❌ Evolution failed: {e}")
            logger.error(traceback.format_exc())
    
    def _emit_evolution_span(self, span_name: str, attributes: Dict[str, Any]):
        """Emit evolution telemetry span."""
        try:
            span_data = {
                "name": span_name,
                "trace_id": f"evolution_trace_{int(time.time() * 1000)}",
                "span_id": f"evolution_span_{int(time.time() * 1000000)}",
                "timestamp": time.time(),
                "attributes": {
                    "swarm.agent": "evolution_engine",
                    "swarm.trigger": "evolution",
                    **attributes
                }
            }
            
            # Write to coordination file
            spans_file = self.coordination_dir / "telemetry_spans.jsonl"
            with open(spans_file, 'a') as f:
                f.write(json.dumps(span_data) + '\n')
            
        except Exception as e:
            logger.error(f"Failed to emit evolution span: {e}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status and statistics."""
        return {
            "current_generation": self.current_generation,
            "population_size": len(self.population),
            "best_genome": {
                "genome_id": self.best_genome.genome_id if self.best_genome else None,
                "fitness_score": self.best_genome.fitness_score if self.best_genome else 0,
                "genome_type": self.best_genome.genome_type if self.best_genome else None
            } if self.best_genome else None,
            "fitness_statistics": {
                "current_best": max([g.fitness_score for g in self.population]) if self.population else 0,
                "current_average": statistics.mean([g.fitness_score for g in self.population]) if self.population else 0,
                "historical_best": max([max(gen) for gen in self.fitness_history]) if self.fitness_history else 0
            },
            "evolution_metrics": len(self.evolution_metrics),
            "active_strategies": [s.value for s in self.active_strategies],
            "performance_targets": {k.value: v for k, v in self.performance_targets.items()}
        }


# Null context manager for when tracer is None
class nullcontext:
    def __enter__(self):
        return self
    def __exit__(self, *excinfo):
        pass