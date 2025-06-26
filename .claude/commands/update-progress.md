# Command: update-progress

Update progress on the current or specified work item: $ARGUMENTS

## Steps:

1. Parse the progress update from arguments:
   - Work ID (optional, defaults to CURRENT_WORK_ITEM)
   - Progress percentage (0-100)
   - Status (optional: active, in_progress, blocked)
   - Notes or blockers

2. Validate the work item exists and is active

3. Update the progress:
   ```bash
   python coordination_cli_v2.py progress <work_id> <percentage> --status <status>
   ```

4. If blocked, document the blocker:
   - Create a note about what's blocking
   - Suggest potential solutions
   - Flag for team attention

5. Show updated status and next steps

## Examples:

- `/update-progress: 50% - Implemented core logic, starting tests`
- `/update-progress: work_123456 75% blocked - Waiting for API access`
- `/update-progress: 90% in_progress - Final review and cleanup`

## Progress Milestones:

- 25% - Initial implementation started
- 50% - Core functionality complete
- 75% - Tests and edge cases handled
- 90% - Code review and polish
- 100% - Ready for completion

## Output Format:

```
📈 Progress Updated
   Work ID: <work_id>
   Progress: <old>% → <new>%
   Status: <status>
   
📋 Work Details:
   Type: <work_type>
   Description: <description>
   Time Elapsed: <duration>
   
💡 Next Steps:
   - <suggested next action>
   - <estimated time to completion>
```