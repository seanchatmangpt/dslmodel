# Command: complete-work

Complete the current work item or specified work item: $ARGUMENTS

## Steps:

1. Determine which work item to complete:
   - If work ID provided in arguments, use that
   - Otherwise use CURRENT_WORK_ITEM environment variable
   - If neither available, list recent active work items

2. Run any final tests or validation:
   ```bash
   pytest  # or appropriate test command
   ruff check  # or appropriate linting
   ```

3. Complete the work item:
   ```bash
   python coordination_cli_v2.py complete <work_id> --result <success|failure> --velocity <points>
   ```

4. Update tracking:
   - Clear CURRENT_WORK_ITEM if it was the completed item
   - Log completion with velocity points
   - Archive if needed

5. Generate a brief completion report

## Examples:

- `/complete-work: work_1234567890 success 8 points`
- `/complete-work: current item completed successfully, 5 story points`
- `/complete-work: failed due to external dependency, 0 points`

## Velocity Point Guidelines:

- 1-3 points: Simple changes, documentation updates
- 5-8 points: Standard features, bug fixes
- 13 points: Complex features, major refactoring
- 21+ points: Should have been broken down

## Output Format:

```
✅ Work Completed Successfully
   Work ID: <work_id>
   Result: <success|failure>
   Velocity: <points> story points
   Duration: <time_elapsed>
   
📊 Updated Metrics:
   Sprint Velocity: <total> points
   Completion Rate: <percentage>%
```