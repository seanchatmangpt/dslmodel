# Command: coordination-dashboard

Show the agent coordination dashboard with optional filters: $ARGUMENTS

## Steps:

1. Parse any filter arguments:
   - Team filter (e.g., "team:frontend")
   - Status filter (e.g., "status:active")
   - Time range (e.g., "last:24h")

2. Generate comprehensive dashboard:
   ```bash
   python coordination_cli_v2.py dashboard
   ```

3. If filters provided, also run:
   ```bash
   python coordination_cli_v2.py list-work --team <team> --status <status>
   ```

4. Calculate and display key metrics:
   - Active work items count
   - Completed items today/this sprint
   - Total velocity points
   - Team distribution
   - Priority breakdown

5. Identify any issues:
   - Overdue items
   - Blocked work
   - Unbalanced workload

## Examples:

- `/coordination-dashboard` - Show full dashboard
- `/coordination-dashboard: team:backend status:active` - Backend team active work
- `/coordination-dashboard: last:7d` - Last 7 days activity

## Output Sections:

### 📊 Summary Metrics
- Total Active Work: X items
- Completed Today: Y items  
- Sprint Velocity: Z points

### 🎯 Priority Breakdown
- Critical: X items
- High: Y items
- Medium: Z items
- Low: W items

### 👥 Team Distribution
- Team A: X active, Y completed
- Team B: X active, Y completed

### ⚡ Performance
- Fast-path items: X
- Regular items: Y
- Archive size: Z MB

### 🚨 Alerts
- Overdue items: X
- Blocked items: Y
- Capacity warnings: [teams]