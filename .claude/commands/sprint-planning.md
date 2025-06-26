# Command: sprint-planning

Initialize or update sprint planning with work items: $ARGUMENTS

## Steps:

1. Parse sprint planning arguments:
   - Sprint name/number
   - Sprint duration (default: 2 weeks)
   - Team capacity
   - Priority items to include

2. Analyze current backlog:
   ```bash
   python coordination_cli_v2.py list-work --status active
   ```

3. Create sprint plan:
   - Prioritize critical and high priority items
   - Balance work across teams
   - Calculate total story points vs capacity
   - Identify dependencies

4. For each planned item:
   - Verify it's ready (has clear requirements)
   - Estimate if not already estimated
   - Assign to appropriate team
   - Set sprint tag

5. Generate sprint planning summary

## Examples:

- `/sprint-planning: Sprint 2025-01 - 2 weeks - 120 points capacity`
- `/sprint-planning: Emergency hotfix sprint - 3 days - critical items only`
- `/sprint-planning: PI Planning Sprint 1 of 4`

## Sprint Planning Process:

1. **Capacity Planning**
   - Team A: X points
   - Team B: Y points
   - Total: Z points

2. **Priority Stack Ranking**
   - Critical items first
   - High priority business value
   - Technical debt allocation (20%)
   - Innovation time (10%)

3. **Risk Assessment**
   - External dependencies
   - Resource constraints
   - Technical unknowns

## Output Format:

```
🎯 Sprint Planning: <sprint_name>

📅 Sprint Details:
   Duration: <start_date> to <end_date>
   Total Capacity: <points> story points
   Teams: <count> teams participating

📋 Planned Work:
   Critical: <count> items (<points> pts)
   High: <count> items (<points> pts)
   Medium: <count> items (<points> pts)
   
   Total Planned: <points> pts
   Capacity Used: <percentage>%

👥 Team Assignments:
   <team>: <count> items (<points> pts)
   <team>: <count> items (<points> pts)

⚠️ Risks & Dependencies:
   - <risk or dependency>
   - <mitigation plan>

✅ Sprint Goal:
   <clear sprint goal statement>
```