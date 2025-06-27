import logging
import json
from datetime import datetime
from enum import Enum, auto
from typing import List, Dict, Optional, Any
from pathlib import Path

from dslmodel import DSLModel
from dslmodel.mixins import FSMMixin, trigger

logger = logging.getLogger(__name__)


class EvolutionState(Enum):
    """States for the evolution tracking system"""
    IDLE = auto()
    ANALYZING = auto()
    MUTATING = auto()
    EVALUATING = auto()
    SELECTING = auto()
    APPLYING = auto()
    VALIDATING = auto()
    ROLLING_BACK = auto()
    COMPLETED = auto()


class MutationProposal(DSLModel):
    """Model for a proposed mutation"""
    id: str
    name: str
    description: str
    mutation_type: str  # "latent", "file-based", "semantic"
    fitness_score: Optional[float] = None
    status: str = "pending"  # pending, applied, rejected
    created_at: datetime = datetime.now()


class FitnessMetrics(DSLModel):
    """Model for system fitness metrics"""
    health_score: float
    pattern_recognition_rate: float
    telemetry_quality: float
    completion_rate: float
    response_time_ms: float
    process_count: int
    timestamp: datetime = datetime.now()


class EvolutionResult(DSLModel):
    """Model for evolution cycle results"""
    cycle_id: str
    mutations_proposed: int
    mutations_applied: int
    mutations_rejected: int
    fitness_before: float
    fitness_after: float
    improvement_percentage: float
    duration_seconds: float


class EvolutionTracker(FSMMixin):
    """
    Evolution tracking system using FSM to manage system mutations
    and fitness-based evolution cycles.
    """
    
    def __init__(self, evolution_dir: str = "./evolution"):
        super().__init__()
        self.evolution_dir = Path(evolution_dir)
        self.evolution_dir.mkdir(exist_ok=True)
        
        # Initialize state directories
        self.mutations_dir = self.evolution_dir / "mutations"
        self.mutations_dir.mkdir(exist_ok=True)
        (self.mutations_dir / "pending").mkdir(exist_ok=True)
        (self.mutations_dir / "applied").mkdir(exist_ok=True)
        (self.mutations_dir / "rejected").mkdir(exist_ok=True)
        
        # Initialize tracking data
        self.current_fitness: Optional[FitnessMetrics] = None
        self.pending_mutations: List[MutationProposal] = []
        self.cycle_start_time: Optional[datetime] = None
        self.fitness_history: List[FitnessMetrics] = []
        
        # Setup FSM
        self.setup_fsm(state_enum=EvolutionState, initial=EvolutionState.IDLE)
        
        logger.info(f"Evolution tracker initialized in state: {self.state}")
    
    @trigger(source=EvolutionState.IDLE, dest=EvolutionState.ANALYZING)
    def start_evolution_cycle(self):
        """Begin a new evolution cycle by analyzing current system state"""
        self.cycle_start_time = datetime.now()
        logger.info("Starting evolution cycle - analyzing system fitness")
        
    @trigger(source=EvolutionState.ANALYZING, dest=EvolutionState.MUTATING)
    def propose_mutations(self):
        """Generate mutation proposals based on fitness analysis"""
        logger.info("Proposing mutations based on current fitness metrics")
        
    @trigger(source=EvolutionState.MUTATING, dest=EvolutionState.EVALUATING)
    def evaluate_mutations(self):
        """Evaluate fitness scores for proposed mutations"""
        logger.info(f"Evaluating {len(self.pending_mutations)} proposed mutations")
        
    @trigger(source=EvolutionState.EVALUATING, dest=EvolutionState.SELECTING)
    def select_best_mutations(self):
        """Select mutations with highest fitness potential"""
        logger.info("Selecting best mutations based on fitness scores")
        
    @trigger(source=EvolutionState.SELECTING, dest=EvolutionState.APPLYING)
    def apply_mutations(self):
        """Apply selected mutations to the system"""
        logger.info("Applying selected mutations")
        
    @trigger(source=EvolutionState.APPLYING, dest=EvolutionState.VALIDATING)
    def validate_changes(self):
        """Validate that applied mutations improve system fitness"""
        logger.info("Validating applied mutations")
        
    @trigger(source=EvolutionState.VALIDATING, dest=EvolutionState.COMPLETED)
    def complete_cycle(self):
        """Successfully complete the evolution cycle"""
        logger.info("Evolution cycle completed successfully")
        
    @trigger(source=EvolutionState.VALIDATING, dest=EvolutionState.ROLLING_BACK)
    def initiate_rollback(self):
        """Rollback failed mutations"""
        logger.warning("Validation failed - initiating rollback")
        
    @trigger(source=EvolutionState.ROLLING_BACK, dest=EvolutionState.IDLE)
    def rollback_complete(self):
        """Complete rollback and return to idle state"""
        logger.info("Rollback completed - returning to idle state")
        
    @trigger(source=EvolutionState.COMPLETED, dest=EvolutionState.IDLE)
    def reset_for_next_cycle(self):
        """Reset system for next evolution cycle"""
        logger.info("Resetting for next evolution cycle")
        
    # Condition methods for state transitions
    def has_fitness_data(self) -> bool:
        """Check if we have current fitness metrics"""
        return self.current_fitness is not None
    
    def has_pending_mutations(self) -> bool:
        """Check if there are mutations to evaluate"""
        return len(self.pending_mutations) > 0
    
    def mutations_improve_fitness(self) -> bool:
        """Check if mutations improve overall fitness"""
        if not self.fitness_history or not self.current_fitness:
            return False
        baseline = self.fitness_history[-1].health_score
        return self.current_fitness.health_score > baseline
    
    # Business logic methods
    def analyze_fitness(self) -> FitnessMetrics:
        """Analyze current system fitness metrics"""
        # In a real implementation, this would gather actual metrics
        metrics = FitnessMetrics(
            health_score=85.5,
            pattern_recognition_rate=0.75,
            telemetry_quality=0.92,
            completion_rate=0.39,
            response_time_ms=35.6,
            process_count=4
        )
        self.current_fitness = metrics
        self.fitness_history.append(metrics)
        return metrics
    
    def generate_mutations(self) -> List[MutationProposal]:
        """Generate mutation proposals based on fitness analysis"""
        mutations = []
        
        # Example: Generate mutations based on low-scoring metrics
        if self.current_fitness:
            if self.current_fitness.completion_rate < 0.5:
                mutations.append(MutationProposal(
                    id="mut_001",
                    name="intelligent-completion-optimizer",
                    description="Optimize intelligent completion engine for higher throughput",
                    mutation_type="semantic"
                ))
            
            if self.current_fitness.response_time_ms > 40:
                mutations.append(MutationProposal(
                    id="mut_002", 
                    name="latent-space-caching",
                    description="Implement latent space caching for faster responses",
                    mutation_type="latent"
                ))
        
        self.pending_mutations = mutations
        
        # Save mutations to pending directory
        for mutation in mutations:
            mutation_path = self.mutations_dir / "pending" / f"{mutation.id}.json"
            mutation_path.write_text(mutation.model_dump_json(indent=2))
        
        return mutations
    
    def calculate_mutation_fitness(self, mutation: MutationProposal) -> float:
        """Calculate fitness score for a specific mutation"""
        # In a real implementation, this would use SPR or other fitness functions
        base_score = 0.5
        
        if mutation.mutation_type == "latent":
            base_score += 0.2  # Latent mutations are faster to evaluate
        elif mutation.mutation_type == "semantic":
            base_score += 0.15
        
        # Simulate fitness calculation
        import random
        fitness = base_score + random.uniform(-0.1, 0.3)
        mutation.fitness_score = min(1.0, max(0.0, fitness))
        
        return mutation.fitness_score
    
    def select_mutations(self, threshold: float = 0.7) -> List[MutationProposal]:
        """Select mutations above fitness threshold"""
        selected = [m for m in self.pending_mutations if m.fitness_score and m.fitness_score >= threshold]
        
        for mutation in self.pending_mutations:
            if mutation in selected:
                mutation.status = "applied"
                # Move to applied directory
                src = self.mutations_dir / "pending" / f"{mutation.id}.json"
                dst = self.mutations_dir / "applied" / f"{mutation.id}.json"
                if src.exists():
                    src.rename(dst)
            else:
                mutation.status = "rejected"
                # Move to rejected directory
                src = self.mutations_dir / "pending" / f"{mutation.id}.json"
                dst = self.mutations_dir / "rejected" / f"{mutation.id}.json"
                if src.exists():
                    src.rename(dst)
        
        return selected
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        pending_count = len(list((self.mutations_dir / "pending").glob("*.json")))
        applied_count = len(list((self.mutations_dir / "applied").glob("*.json")))
        rejected_count = len(list((self.mutations_dir / "rejected").glob("*.json")))
        
        status = {
            "current_state": self.state,
            "pending_mutations": pending_count,
            "applied_mutations": applied_count,
            "rejected_mutations": rejected_count,
            "current_fitness": self.current_fitness.model_dump() if self.current_fitness else None,
            "fitness_history_count": len(self.fitness_history),
            "possible_triggers": self.possible_triggers()
        }
        
        return status
    
    def run_evolution_cycle(self, prompt: str) -> EvolutionResult:
        """Run a complete evolution cycle based on the given prompt"""
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        # Record initial fitness
        initial_fitness = self.current_fitness.health_score if self.current_fitness else 0.0
        
        # Use the FSM forward method to progress through states
        self.forward(prompt)
        
        # Calculate results
        duration = (datetime.now() - start_time).total_seconds()
        final_fitness = self.current_fitness.health_score if self.current_fitness else initial_fitness
        
        result = EvolutionResult(
            cycle_id=cycle_id,
            mutations_proposed=len(self.pending_mutations),
            mutations_applied=len([m for m in self.pending_mutations if m.status == "applied"]),
            mutations_rejected=len([m for m in self.pending_mutations if m.status == "rejected"]),
            fitness_before=initial_fitness,
            fitness_after=final_fitness,
            improvement_percentage=((final_fitness - initial_fitness) / initial_fitness * 100) if initial_fitness > 0 else 0,
            duration_seconds=duration
        )
        
        # Save result
        result_path = self.evolution_dir / f"{cycle_id}_result.json"
        result_path.write_text(result.model_dump_json(indent=2))
        
        return result


def main():
    """Example usage of EvolutionTracker"""
    from dslmodel import init_instant
    init_instant()
    
    # Initialize evolution tracker
    tracker = EvolutionTracker()
    
    print(f"Initial state: {tracker.state}")
    print(f"Status: {json.dumps(tracker.get_evolution_status(), indent=2)}")
    
    # Start evolution cycle
    tracker.forward("analyze system performance and propose optimizations")
    print(f"\nState after analysis: {tracker.state}")
    
    # Analyze fitness
    fitness = tracker.analyze_fitness()
    print(f"Current fitness: {fitness.health_score}")
    
    # Continue evolution
    tracker.forward("generate mutations to improve completion rate")
    mutations = tracker.generate_mutations()
    print(f"\nGenerated {len(mutations)} mutations")
    
    # Evaluate mutations
    tracker.forward("evaluate mutation fitness scores")
    for mutation in tracker.pending_mutations:
        score = tracker.calculate_mutation_fitness(mutation)
        print(f"Mutation {mutation.name}: {score:.2f}")
    
    # Select and apply
    tracker.forward("select best mutations for application")
    selected = tracker.select_mutations()
    print(f"\nSelected {len(selected)} mutations for application")
    
    # Complete cycle
    tracker.forward("apply selected mutations")
    tracker.forward("validate the changes improved fitness")
    
    if tracker.mutations_improve_fitness():
        tracker.forward("complete the evolution cycle")
    else:
        tracker.forward("rollback the failed mutations")
    
    print(f"\nFinal state: {tracker.state}")
    print(f"Final status: {json.dumps(tracker.get_evolution_status(), indent=2)}")


if __name__ == '__main__':
    main()