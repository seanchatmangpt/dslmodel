"""
Worktree-based Evolution Engine
Uses Git worktrees for isolated evolution experiments with OTEL coordination
"""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from ..generated.models.evolution import (
    Evolution,
    EvolutionWorktree,
    EvolutionValidation, 
    EvolutionDeployment
)
from ..agents.worktree_agent import WorktreeAgent, WorktreeCoordinator, FeatureTask
from ..otel.otel_instrumentation_mock import init_otel, SwarmSpanAttributes
from ..utils.llm_init import init_qwen3


class EvolutionStrategy(Enum):
    """Evolution strategies for system improvement."""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    COORDINATION_IMPROVEMENT = "coordination_improvement"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    RELIABILITY_IMPROVEMENT = "reliability_improvement"


@dataclass
class EvolutionCandidate:
    """A candidate for system evolution."""
    candidate_id: str
    strategy: EvolutionStrategy
    description: str
    worktree_path: str
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    fitness_score: float = 0.0
    validation_results: Optional[Dict[str, Any]] = None
    telemetry_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionGeneration:
    """Results from one evolution generation."""
    generation_id: str
    candidates: List[EvolutionCandidate]
    best_candidate: Optional[EvolutionCandidate]
    fitness_improvement: float
    deployed: bool = False


class WorktreeEvolutionEngine:
    """
    Evolution engine that uses Git worktrees for isolated experiments.
    
    Each evolution candidate is tested in its own worktree with full
    OTEL coordination and telemetry validation.
    """
    
    def __init__(
        self,
        base_path: str = "/Users/sac/dev/dslmodel-evolution",
        population_size: int = 5,
        mutation_rate: float = 0.1
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.current_generation = 0
        
        # Initialize OTEL coordination
        self.otel = init_otel(
            service_name="evolution-engine",
            service_version="1.0.0",
            enable_console_export=True
        )
        
        # Initialize AI
        init_qwen3(temperature=0.2)
        
        # Initialize worktree coordinator
        self.worktree_coordinator = WorktreeCoordinator(
            coordinator_id="evolution-coordinator"
        )
        
        # Track evolution history
        self.evolution_history: List[EvolutionGeneration] = []
        self.active_candidates: Set[str] = set()
        
        print(f"🧬 WorktreeEvolutionEngine initialized")
        print(f"   Base path: {self.base_path}")
        print(f"   Population size: {self.population_size}")
        print(f"   Mutation rate: {self.mutation_rate}")
    
    async def evolve_generation(
        self,
        strategy: EvolutionStrategy = EvolutionStrategy.COORDINATION_IMPROVEMENT
    ) -> EvolutionGeneration:
        """Evolve one generation using worktree isolation."""
        
        generation_id = f"gen-{self.current_generation:03d}-{uuid.uuid4().hex[:8]}"
        
        with self.otel.trace_span(
            name="evolution.generation",
            attributes={
                SwarmSpanAttributes.SWARM_FRAMEWORK: "evolution",
                SwarmSpanAttributes.SWARM_PHASE: "generation",
                "evolution.generation.id": generation_id,
                "evolution.strategy": strategy.value,
                "evolution.population_size": self.population_size
            }
        ) as span:
            
            print(f"🧬 Starting evolution generation {self.current_generation}")
            print(f"   Strategy: {strategy.value}")
            print(f"   Population: {self.population_size}")
            
            # Create evolution model for telemetry
            evolution_model = Evolution(
                generation_id=generation_id,
                strategy=strategy.value,
                fitness_score=0.0,
                experiment_id=f"exp-{generation_id}",
                worktree_path=str(self.base_path)
            )
            
            evolution_trace_id = evolution_model.emit_telemetry()
            
            # Generate candidate mutations
            candidates = await self._generate_candidates(strategy, generation_id)
            
            # Test candidates in parallel worktrees
            validated_candidates = await self._test_candidates_in_worktrees(candidates)
            
            # Select best candidate
            best_candidate = self._select_best_candidate(validated_candidates)
            
            # Calculate fitness improvement
            previous_best = 0.0
            if self.evolution_history:
                previous_best = max(
                    gen.best_candidate.fitness_score for gen in self.evolution_history
                    if gen.best_candidate
                )
            
            current_best = best_candidate.fitness_score if best_candidate else 0.0
            fitness_improvement = current_best - previous_best
            
            # Create generation result
            generation = EvolutionGeneration(
                generation_id=generation_id,
                candidates=validated_candidates,
                best_candidate=best_candidate,
                fitness_improvement=fitness_improvement
            )
            
            # Record generation completion
            span.add_event("evolution.generation.complete", {
                "candidates_tested": len(validated_candidates),
                "best_fitness": current_best,
                "fitness_improvement": fitness_improvement,
                "trace_id": evolution_trace_id
            })
            
            self.evolution_history.append(generation)
            self.current_generation += 1
            
            print(f"✅ Generation {self.current_generation - 1} complete")
            print(f"   Best fitness: {current_best:.3f}")
            print(f"   Improvement: {fitness_improvement:.3f}")
            
            return generation
    
    async def _generate_candidates(
        self, 
        strategy: EvolutionStrategy, 
        generation_id: str
    ) -> List[EvolutionCandidate]:
        """Generate evolution candidates for testing."""
        
        candidates = []
        
        for i in range(self.population_size):
            candidate_id = f"{generation_id}-cand-{i:02d}"
            worktree_path = str(self.base_path / f"worktree-{candidate_id}")
            
            # Generate mutations based on strategy
            mutations = await self._generate_mutations(strategy)
            
            candidate = EvolutionCandidate(
                candidate_id=candidate_id,
                strategy=strategy,
                description=f"{strategy.value} optimization candidate {i+1}",
                worktree_path=worktree_path,
                mutations=mutations
            )
            
            candidates.append(candidate)
            self.active_candidates.add(candidate_id)
            
            print(f"   📋 Generated candidate: {candidate_id}")
        
        return candidates
    
    async def _generate_mutations(self, strategy: EvolutionStrategy) -> List[Dict[str, Any]]:
        """Generate mutations based on evolution strategy."""
        
        base_mutations = {
            EvolutionStrategy.COORDINATION_IMPROVEMENT: [
                {
                    "type": "coordination_pattern",
                    "target": "agent_communication",
                    "change": "reduce_coordination_overhead",
                    "value": 0.15
                },
                {
                    "type": "otel_optimization", 
                    "target": "span_collection",
                    "change": "optimize_telemetry_batching",
                    "value": 0.2
                }
            ],
            EvolutionStrategy.PERFORMANCE_OPTIMIZATION: [
                {
                    "type": "algorithm_optimization",
                    "target": "task_assignment",
                    "change": "improve_load_balancing",
                    "value": 0.25
                },
                {
                    "type": "caching_strategy",
                    "target": "validation_cache",
                    "change": "intelligent_cache_warming",
                    "value": 0.3
                }
            ],
            EvolutionStrategy.FEATURE_ENHANCEMENT: [
                {
                    "type": "ai_reasoning",
                    "target": "decision_making",
                    "change": "enhanced_context_analysis",
                    "value": 0.2
                },
                {
                    "type": "automation_expansion",
                    "target": "remediation_workflows", 
                    "change": "predictive_issue_detection",
                    "value": 0.35
                }
            ]
        }
        
        return base_mutations.get(strategy, [])
    
    async def _test_candidates_in_worktrees(
        self, 
        candidates: List[EvolutionCandidate]
    ) -> List[EvolutionCandidate]:
        """Test all candidates in parallel worktrees."""
        
        print(f"🧪 Testing {len(candidates)} candidates in worktrees...")
        
        # Create agents for each candidate
        agents = []
        for candidate in candidates:
            agent = WorktreeAgent(agent_id=f"evo-agent-{candidate.candidate_id}")
            agents.append(agent)
            self.worktree_coordinator.add_agent(agent)
        
        # Create feature tasks for testing
        tasks = []
        for i, candidate in enumerate(candidates):
            task = FeatureTask(
                name=f"evolution-test-{candidate.candidate_id}",
                description=f"Test evolution candidate: {candidate.description}",
                branch_name=f"evolution/{candidate.candidate_id}",
                worktree_path=candidate.worktree_path,
                requirements=[
                    "Apply evolution mutations",
                    "Run performance benchmarks", 
                    "Collect telemetry metrics",
                    "Validate fitness criteria"
                ]
            )
            
            tasks.append(task)
            self.worktree_coordinator.add_task(task)
        
        # Run coordination to assign and execute tasks
        await self.worktree_coordinator.coordinate_development()
        
        # Collect results from each candidate test
        validated_candidates = []
        for candidate, task in zip(candidates, tasks):
            if task.status == "completed":
                # Validate candidate and calculate fitness
                validation_result = await self._validate_candidate(candidate, task)
                candidate.validation_results = validation_result
                candidate.fitness_score = self._calculate_fitness_score(validation_result)
                
                # Create validation telemetry
                validation_model = EvolutionValidation(
                    validation_type="worktree_integration_test",
                    validation_score=candidate.fitness_score,
                    tests_passed=validation_result.get("tests_passed", 0),
                    tests_total=validation_result.get("tests_total", 0),
                    performance_delta=validation_result.get("performance_improvement", 0.0)
                )
                
                validation_model.emit_telemetry()
                
                print(f"   ✅ {candidate.candidate_id}: fitness {candidate.fitness_score:.3f}")
            else:
                candidate.fitness_score = 0.0
                print(f"   ❌ {candidate.candidate_id}: test failed")
            
            validated_candidates.append(candidate)
        
        return validated_candidates
    
    async def _validate_candidate(
        self, 
        candidate: EvolutionCandidate, 
        task: FeatureTask
    ) -> Dict[str, Any]:
        """Validate a candidate based on worktree test results."""
        
        with self.otel.trace_span(
            name="evolution.validation",
            attributes={
                "evolution.candidate.id": candidate.candidate_id,
                "evolution.strategy": candidate.strategy.value,
                "evolution.worktree.path": candidate.worktree_path
            }
        ):
            
            # Simulate validation metrics (in real implementation, would analyze test results)
            import random
            
            validation_results = {
                "tests_passed": random.randint(18, 25),
                "tests_total": 25,
                "performance_improvement": random.uniform(-5.0, 30.0),
                "error_rate_change": random.uniform(-15.0, 5.0),
                "coordination_efficiency": random.uniform(0.7, 0.95),
                "telemetry_quality": random.uniform(0.8, 1.0),
                "stability_score": random.uniform(0.75, 1.0)
            }
            
            # Add strategy-specific validation
            if candidate.strategy == EvolutionStrategy.COORDINATION_IMPROVEMENT:
                validation_results["coordination_latency_reduction"] = random.uniform(10.0, 40.0)
            elif candidate.strategy == EvolutionStrategy.PERFORMANCE_OPTIMIZATION:
                validation_results["throughput_increase"] = random.uniform(15.0, 50.0)
            
            return validation_results
    
    def _calculate_fitness_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate fitness score from validation results."""
        
        weights = {
            "test_success_rate": 0.3,
            "performance_improvement": 0.25,
            "coordination_efficiency": 0.2, 
            "stability_score": 0.15,
            "telemetry_quality": 0.1
        }
        
        fitness = 0.0
        
        # Test success rate
        if validation_results.get("tests_total", 0) > 0:
            success_rate = validation_results["tests_passed"] / validation_results["tests_total"]
            fitness += success_rate * weights["test_success_rate"]
        
        # Performance improvement (normalized)
        perf_improvement = validation_results.get("performance_improvement", 0.0)
        normalized_perf = max(0, min(perf_improvement / 50.0, 1.0))  # 50% is max
        fitness += normalized_perf * weights["performance_improvement"]
        
        # Coordination efficiency
        coord_eff = validation_results.get("coordination_efficiency", 0.0)
        fitness += coord_eff * weights["coordination_efficiency"]
        
        # Stability score
        stability = validation_results.get("stability_score", 0.0)
        fitness += stability * weights["stability_score"]
        
        # Telemetry quality
        telemetry = validation_results.get("telemetry_quality", 0.0)
        fitness += telemetry * weights["telemetry_quality"]
        
        return min(fitness, 1.0)  # Cap at 1.0
    
    def _select_best_candidate(
        self, 
        candidates: List[EvolutionCandidate]
    ) -> Optional[EvolutionCandidate]:
        """Select the best candidate based on fitness scores."""
        
        if not candidates:
            return None
        
        # Sort by fitness score
        sorted_candidates = sorted(candidates, key=lambda c: c.fitness_score, reverse=True)
        
        best = sorted_candidates[0]
        
        # Only return if fitness is above threshold
        if best.fitness_score > 0.7:
            return best
        
        return None
    
    async def deploy_candidate(
        self, 
        candidate: EvolutionCandidate,
        strategy: str = "gradual_rollout"
    ) -> bool:
        """Deploy a successful evolution candidate."""
        
        with self.otel.trace_span(
            name="evolution.deployment",
            attributes={
                "evolution.candidate.id": candidate.candidate_id,
                "evolution.deployment.strategy": strategy,
                "evolution.fitness.score": candidate.fitness_score
            }
        ) as span:
            
            print(f"🚀 Deploying candidate: {candidate.candidate_id}")
            
            # Create deployment telemetry
            deployment_model = EvolutionDeployment(
                deployment_strategy=strategy,
                deployment_success=True,
                rollback_enabled=True,
                fitness_improvement=candidate.fitness_score * 100  # Convert to percentage
            )
            
            deployment_trace_id = deployment_model.emit_telemetry()
            
            # Simulate deployment process
            await asyncio.sleep(2)
            
            # Record successful deployment
            span.add_event("evolution.deployment.complete", {
                "deployment_success": True,
                "trace_id": deployment_trace_id,
                "fitness_score": candidate.fitness_score
            })
            
            print(f"✅ Deployment successful: {candidate.candidate_id}")
            return True
    
    async def run_evolution_cycles(
        self, 
        cycles: int = 3,
        strategy: EvolutionStrategy = EvolutionStrategy.COORDINATION_IMPROVEMENT
    ) -> List[EvolutionGeneration]:
        """Run multiple evolution cycles."""
        
        results = []
        
        for cycle in range(cycles):
            print(f"\n🔄 Evolution Cycle {cycle + 1}/{cycles}")
            print("=" * 40)
            
            generation = await self.evolve_generation(strategy)
            results.append(generation)
            
            # Deploy best candidate if good enough
            if generation.best_candidate and generation.best_candidate.fitness_score > 0.8:
                await self.deploy_candidate(generation.best_candidate)
                generation.deployed = True
            
            # Brief pause between cycles
            await asyncio.sleep(1)
        
        return results
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status."""
        
        total_candidates = sum(len(gen.candidates) for gen in self.evolution_history)
        successful_deployments = sum(1 for gen in self.evolution_history if gen.deployed)
        
        best_fitness = 0.0
        if self.evolution_history:
            best_fitness = max(
                gen.best_candidate.fitness_score for gen in self.evolution_history
                if gen.best_candidate
            )
        
        return {
            "current_generation": self.current_generation,
            "total_generations": len(self.evolution_history),
            "total_candidates_tested": total_candidates,
            "successful_deployments": successful_deployments,
            "best_fitness_score": best_fitness,
            "active_candidates": len(self.active_candidates),
            "population_size": self.population_size,
            "mutation_rate": self.mutation_rate
        }