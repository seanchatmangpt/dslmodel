# Evolution Tracker with FSM

## Overview
The EvolutionTracker uses FSMMixin to manage system evolution through defined states:

```
IDLE → ANALYZING → MUTATING → EVALUATING → SELECTING → APPLYING → VALIDATING → COMPLETED
                                                                         ↓
                                                                   ROLLING_BACK → IDLE
```

## Key Features

1. **State Management**: Uses FSM to ensure evolution follows proper workflow
2. **Mutation Pipeline**: Tracks pending, applied, and rejected mutations
3. **Fitness Metrics**: Monitors system health, performance, and quality
4. **AI-Driven Transitions**: Uses LLM to decide state transitions based on prompts

## Example Usage

```python
from dslmodel.examples.evolution_tracker import EvolutionTracker

# Initialize tracker
tracker = EvolutionTracker(evolution_dir="./evolution")

# Check initial state
print(tracker.state)  # "IDLE"
print(tracker.get_evolution_status())

# Start evolution cycle with AI-driven transitions
tracker.forward("analyze system performance and propose optimizations")
# AI decides: IDLE → ANALYZING

# Continue through the cycle
tracker.forward("generate mutations to improve completion rate")  
# AI decides: ANALYZING → MUTATING

tracker.forward("evaluate mutation fitness scores")
# AI decides: MUTATING → EVALUATING

tracker.forward("select best mutations for application")
# AI decides: EVALUATING → SELECTING

tracker.forward("apply selected mutations")
# AI decides: SELECTING → APPLYING

tracker.forward("validate the changes improved fitness")
# AI decides: APPLYING → VALIDATING

# Based on validation results
if tracker.mutations_improve_fitness():
    tracker.forward("complete the evolution cycle")
    # AI decides: VALIDATING → COMPLETED
else:
    tracker.forward("rollback the failed mutations")
    # AI decides: VALIDATING → ROLLING_BACK
```

## State Transitions

### Available Triggers:
- `start_evolution_cycle`: IDLE → ANALYZING
- `propose_mutations`: ANALYZING → MUTATING  
- `evaluate_mutations`: MUTATING → EVALUATING
- `select_best_mutations`: EVALUATING → SELECTING
- `apply_mutations`: SELECTING → APPLYING
- `validate_changes`: APPLYING → VALIDATING
- `complete_cycle`: VALIDATING → COMPLETED
- `initiate_rollback`: VALIDATING → ROLLING_BACK
- `rollback_complete`: ROLLING_BACK → IDLE
- `reset_for_next_cycle`: COMPLETED → IDLE

## Mutation Types

1. **Latent Mutations**: Fast SPR-based fitness evaluation
2. **Semantic Mutations**: Content/meaning-based changes
3. **File-based Mutations**: Traditional code changes

## Fitness Metrics Tracked

- Health Score (0-100)
- Pattern Recognition Rate 
- Telemetry Quality
- Completion Rate
- Response Time (ms)
- Process Count

## Evolution Results

Each cycle produces an `EvolutionResult` with:
- Mutations proposed/applied/rejected
- Fitness before/after
- Improvement percentage
- Cycle duration

## Directory Structure

```
evolution/
├── mutations/
│   ├── pending/     # Proposed mutations
│   ├── applied/     # Successfully applied
│   └── rejected/    # Failed fitness check
└── cycle_*_result.json  # Evolution results
```

## Integration with Command System

The EvolutionTracker can be integrated with the `/evolution-status` command to provide real-time evolution tracking and mutation management.