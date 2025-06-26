# Command: team-analysis

Analyze team performance and workload distribution: $ARGUMENTS

## Steps:

1. Parse analysis parameters:
   - Specific team name (optional)
   - Time period (default: current sprint)
   - Metrics focus (velocity, quality, balance)

2. Gather team data:
   ```bash
   python coordination_cli_v2.py list-work --team <team>
   python coordination_cli_v2.py dashboard
   ```

3. Calculate team metrics:
   - Velocity (story points completed)
   - Throughput (items completed)
   - Work in progress (WIP)
   - Cycle time
   - Load balance across team members

4. Identify patterns:
   - Consistent over/under performance
   - Bottlenecks or blockers
   - Skill gaps or training needs
   - Collaboration effectiveness

5. Generate recommendations

## Examples:

- `/team-analysis: backend team last 30 days`
- `/team-analysis: all teams velocity comparison`
- `/team-analysis: frontend team workload balance`

## Key Metrics:

### Velocity Metrics
- Average velocity per sprint
- Velocity trend (improving/declining)
- Planned vs actual velocity

### Quality Metrics  
- Success rate (successful completions)
- Rework rate
- Defect density

### Balance Metrics
- Work distribution evenness
- Specialization vs generalization
- Cross-team dependencies

## Output Format:

```
👥 Team Analysis Report

📊 Team: <team_name>
   Period: <time_period>
   Members: <count> active agents

📈 Performance Metrics:
   Velocity: <current> pts/sprint (avg: <average>)
   Throughput: <items>/sprint
   Success Rate: <percentage>%
   Cycle Time: <average> hours

📋 Current Status:
   Active Work: <count> items
   Completed This Sprint: <count> items
   WIP Limit: <current>/<recommended>

🎯 Work Distribution:
   <work_type>: <percentage>% (<count> items)
   <work_type>: <percentage>% (<count> items)

💡 Insights:
   ✅ Strengths:
      - <positive finding>
      - <positive finding>
   
   ⚠️ Areas for Improvement:
      - <improvement area>
      - <improvement area>

🚀 Recommendations:
   1. <specific actionable recommendation>
   2. <specific actionable recommendation>
   3. <specific actionable recommendation>
```