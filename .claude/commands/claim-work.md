# Command: claim-work

Claim a new work item in the agent coordination system with the following details: $ARGUMENTS

## Steps:

1. Parse the work description from the arguments to extract:
   - Work type (feature, bug, task, etc.)
   - Brief description
   - Priority (critical, high, medium, low)
   - Team assignment

2. Use the coordination CLI to claim the work:
   ```bash
   python coordination_cli_v2.py claim "<work_type>" "<description>" --priority <priority> --team <team>
   ```

3. If successful, update any relevant tracking:
   - Set CURRENT_WORK_ITEM environment variable
   - Log the claim in the coordination system
   - Show the work item ID for reference

4. Create a todo list for the claimed work if it's a complex task

## Examples:

- `/claim-work: Implement OAuth2 authentication [feature, high priority, security team]`
- `/claim-work: Fix database connection timeout [bug, critical, backend team]`
- `/claim-work: Update API documentation [task, low, docs team]`

## Output Format:

```
✅ Successfully claimed work item: work_<nanosecond_id>
   Type: <work_type>
   Description: <description>
   Priority: <priority>
   Team: <team>
   Agent: <agent_id>
```