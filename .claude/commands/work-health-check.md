# Command: work-health-check

Perform a health check on active work items and coordination system: $ARGUMENTS

## Steps:

1. System health checks:
   - Verify file integrity
   - Check file sizes and performance
   - Validate JSON structure
   - Test fast-path functionality

2. Work item analysis:
   - Identify stale items (no updates > 48h)
   - Find blocked items
   - Detect missing information
   - Check for duplicates

3. Performance analysis:
   ```bash
   # Check file sizes
   ls -lah $COORDINATION_DIR/*.json*
   
   # Count items
   python coordination_cli_v2.py dashboard
   ```

4. Agent health:
   - Active agents count
   - Agent workload distribution
   - Idle agents
   - Overloaded agents

5. Generate health report with remediation steps

## Examples:

- `/work-health-check` - Full system health check
- `/work-health-check: quick` - Quick health check (performance only)
- `/work-health-check: deep` - Deep analysis including historical data

## Health Check Categories:

### 🟢 Green (Healthy)
- Files < 10MB
- Response time < 100ms
- No blocked items > 72h
- Balanced workload

### 🟡 Yellow (Warning)
- Files 10-50MB
- Response time 100-500ms
- Some stale items
- Minor imbalances

### 🔴 Red (Critical)
- Files > 50MB
- Response time > 500ms
- Many blocked items
- Severe imbalances

## Output Format:

```
🏥 Coordination System Health Check

📊 System Status: [🟢 Healthy | 🟡 Warning | 🔴 Critical]

📁 File System Health:
   Work Claims: <size> (<status>)
   Fast Claims: <size> (<status>)
   Coordination Log: <size> (<status>)
   Response Time: <ms> ms

📋 Work Item Health:
   Total Active: <count>
   Stale Items: <count> (>48h no update)
   Blocked Items: <count>
   Missing Data: <count>

👥 Agent Health:
   Active Agents: <count>
   Average Load: <items>/agent
   Overloaded: <count> agents (>5 items)
   Idle: <count> agents (0 items)

⚠️ Issues Found:
   - <issue description> [severity]
   - <issue description> [severity]

🔧 Recommended Actions:
   1. <remediation step>
   2. <remediation step>
   3. <remediation step>

📈 Performance Metrics:
   Claim Speed: <ms> ms
   Query Speed: <ms> ms
   Archive Efficiency: <percentage>%
```