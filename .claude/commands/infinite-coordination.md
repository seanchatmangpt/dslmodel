# Command: infinite-coordination

Run an infinite loop of coordination tasks, continuously optimizing and managing work: $ARGUMENTS

## Overview

This command implements an infinite agentic loop for the coordination system, continuously:
- Monitoring system health
- Claiming appropriate work
- Updating progress
- Completing tasks
- Optimizing performance
- Generating reports

## Steps:

1. Initialize the infinite loop with parameters:
   - Max iterations (default: infinite)
   - Sleep interval between cycles (default: 60s)
   - Auto-claim threshold (default: when < 3 active items)
   - Auto-optimize threshold (default: every 100 items)

2. Main loop cycle:
   ```python
   while True:
       # Health check
       check_system_health()
       
       # Auto-claim if below threshold
       if active_items < threshold:
           claim_new_work()
       
       # Update progress on active items
       update_active_progress()
       
       # Complete ready items
       complete_finished_work()
       
       # Optimize if needed
       if should_optimize():
           optimize_system()
       
       # Generate periodic reports
       if should_report():
           generate_report()
       
       # Sleep before next cycle
       sleep(interval)
   ```

3. Intelligent work selection:
   - Prioritize critical items
   - Balance across teams
   - Match agent capabilities
   - Avoid overload

4. Progress simulation:
   - Realistic progress increments
   - Random delays and blockers
   - Quality variations

5. Continuous improvement:
   - Learn from completion patterns
   - Adjust estimates
   - Optimize team assignments

## Examples:

- `/infinite-coordination` - Run forever with defaults
- `/infinite-coordination: iterations=10 interval=30` - Run 10 cycles, 30s apart
- `/infinite-coordination: demo mode` - Fast demo with 5s intervals

## Loop Behaviors:

### Work Claiming Logic
- Claim when active < threshold
- Prefer high priority items
- Distribute across teams
- Respect WIP limits

### Progress Updates
- Update every 15-30 minutes
- Realistic increments (10-25%)
- Occasional blockers
- Natural variation

### Completion Criteria
- Complete at 100% progress
- Assign realistic velocity
- Update team metrics
- Clear work item

### Optimization Triggers
- Every 100 completions
- When files > 10MB
- Daily at 3 AM
- On performance degradation

## Output Format:

```
♾️  Infinite Coordination Loop Started
═══════════════════════════════════════

Cycle #<number> | <timestamp>
─────────────────────────────

📊 Current State:
   Active Work: <count> items
   Completed Today: <count> items
   System Health: [🟢|🟡|🔴]
   Performance: <ms> ms

🔄 Actions This Cycle:
   ✓ Claimed: <count> new items
   ✓ Updated: <count> items progress  
   ✓ Completed: <count> items
   ✓ Optimized: <yes/no>

📈 Progress Updates:
   • work_123: 25% → 50% (on track)
   • work_456: 60% → 75% (ahead)
   • work_789: 40% → 40% (blocked)

💡 Intelligence:
   • Recommendation: <insight>
   • Pattern detected: <pattern>
   • Optimization: <suggestion>

⏸️  Sleeping <interval>s until next cycle...

[Press Ctrl+C to stop]
```

## Safeguards:

- Maximum WIP limit per agent
- Automatic error recovery
- Performance monitoring
- Graceful shutdown
- State preservation